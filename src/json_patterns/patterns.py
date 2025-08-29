import re

MASTER_PATTERN_REGEX = re.compile(
    r'\{(?P<pattern>[a-z_]+)(?::(?P<identifier>[a-zA-Z0-9_]+))?\}'
)

def compile_template(template: str, available_patterns: dict) -> tuple[re.Pattern, list[tuple[str, str]]]:
    """Convert a template with placeholders into a regex and metadata."""
    regex_parts = []
    last_end = 0
    fields = []  # to keep track of (pattern, identifier)

    for match in MASTER_PATTERN_REGEX.finditer(template):
        pattern = match.group("pattern")
        identifier = match.group("identifier")

        # Add literal text before this placeholder
        regex_parts.append(re.escape(template[last_end:match.start()]))

        if pattern not in available_patterns:
            raise ValueError(f"Unknown pattern type: {pattern}")

        # Add the capturing group for this placeholder
        regex_parts.append(f"({available_patterns[pattern]})")

        # Remember mapping of this group
        fields.append((pattern, identifier))

        last_end = match.end()

    # Add any remaining text, as literal, after last placeholder
    regex_parts.append(re.escape(template[last_end:]))

    # Compile regex
    full_regex = "".join(regex_parts)
    return re.compile(f"^{full_regex}$"), fields
