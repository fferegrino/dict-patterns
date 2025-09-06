import pytest

from dict_patterns.exceptions import DictPatternTypeError
from dict_patterns.patterns import compile_template


def test_compile_template():
    template = "{uuid:1}/user/{int:user_id}/{slug:article}"
    pattern_handlers = {
        "uuid": r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        "int": r"\d+",
        "slug": r"[a-z0-9-]+",
    }

    regex, fields = compile_template(template, pattern_handlers)

    assert fields == [("uuid", "1"), ("int", "user_id"), ("slug", "article")]
    match = regex.match("1d408610-f129-47a8-a4c1-1a6e0ca2d16f/user/42/hello-world")
    assert match is not None
    assert match.group(1) == "1d408610-f129-47a8-a4c1-1a6e0ca2d16f"
    assert match.group(2) == "42"
    assert match.group(3) == "hello-world"


def test_unknown_pattern_raises_error():
    """Test that unknown pattern types raise ValueError."""
    template = "{unknown:test}"
    pattern_handlers = {"uuid": r"[0-9a-f]+"}

    with pytest.raises(DictPatternTypeError, match="Unknown pattern type: unknown"):
        compile_template(template, pattern_handlers)


def test_empty_template():
    """Test compilation of empty template."""
    pattern_handlers = {"uuid": r"[0-9a-f]+"}
    regex, fields = compile_template("", pattern_handlers)

    assert fields == []
    assert regex.match("") is not None
    assert regex.match("anything") is None


def test_template_without_placeholders():
    """Test template containing only literal text."""
    pattern_handlers = {"uuid": r"[0-9a-f]+"}
    regex, fields = compile_template("hello/world", pattern_handlers)

    assert fields == []
    assert regex.match("hello/world") is not None
    assert regex.match("hello") is None
    assert regex.match("world") is None


def test_placeholders_without_identifiers():
    """Test placeholders without identifiers."""
    template = "{uuid}/{int}/{slug}"
    pattern_handlers = {
        "uuid": r"[0-9a-f]+",
        "int": r"\d+",
        "slug": r"[a-z-]+",
    }

    regex, fields = compile_template(template, pattern_handlers)

    assert fields == [("uuid", None), ("int", None), ("slug", None)]
    match = regex.match("abc123/42/hello-world")
    assert match is not None
    assert match.group(1) == "abc123"
    assert match.group(2) == "42"
    assert match.group(3) == "hello-world"


def test_mixed_placeholders():
    """Test template with both identified and unidentified placeholders."""
    template = "{uuid:user_id}/{int}/{slug:article}"
    pattern_handlers = {
        "uuid": r"[0-9a-f]+",
        "int": r"\d+",
        "slug": r"[a-z-]+",
    }

    regex, fields = compile_template(template, pattern_handlers)

    assert fields == [("uuid", "user_id"), ("int", None), ("slug", "article")]
    match = regex.match("abc123/42/hello-world")
    assert match is not None


def test_consecutive_placeholders():
    """Test template with consecutive placeholders."""
    template = "{uuid}{int}{slug}"
    pattern_handlers = {
        "uuid": r"[0-9a-f]+",
        "int": r"\d\d",
        "slug": r"[a-z-]+",
    }

    regex, fields = compile_template(template, pattern_handlers)

    assert fields == [("uuid", None), ("int", None), ("slug", None)]
    match = regex.match("abc12342hello-world")
    assert match is not None
    assert match.group(1) == "abc123"
    assert match.group(2) == "42"
    assert match.group(3) == "hello-world"


def test_special_characters_in_literal_text():
    """Test template with special regex characters in literal text."""
    template = "user/{int}/path/to/file.txt"
    pattern_handlers = {"int": r"\d+"}

    regex, fields = compile_template(template, pattern_handlers)

    assert fields == [("int", None)]
    match = regex.match("user/42/path/to/file.txt")
    assert match is not None
    assert match.group(1) == "42"


def test_empty_pattern_handlers():
    """Test with empty pattern handlers dict."""
    template = "hello/world"
    pattern_handlers = {}

    regex, fields = compile_template(template, pattern_handlers)

    assert fields == []
    assert regex.match("hello/world") is not None


def test_field_ordering():
    """Test that fields are returned in correct order."""
    template = "{first}/middle/{second}/end/{third}"
    pattern_handlers = {
        "first": r"[a-z]+",
        "second": r"\d+",
        "third": r"[a-z]+",
    }

    regex, fields = compile_template(template, pattern_handlers)

    expected_fields = [("first", None), ("second", None), ("third", None)]
    assert fields == expected_fields

    match = regex.match("hello/middle/42/end/world")
    assert match is not None
    assert match.group(1) == "hello"  # first
    assert match.group(2) == "42"  # second
    assert match.group(3) == "world"  # third


def test_different_same_pattern_types():
    """Test that different same pattern types are handled correctly."""
    template = "{uuid:1}/{uuid:2}"
    pattern_handlers = {"uuid": r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"}

    regex, fields = compile_template(template, pattern_handlers)

    assert fields == [("uuid", "1"), ("uuid", "2")]
    match = regex.match("1d408610-f129-47a8-a4c1-1a6e0ca2d16f/1d408610-f129-47a8-a4c1-1a6e0ca2d16f")
    assert match is not None


@pytest.mark.parametrize("pattern_name", ["uuid4", "uuid", "UUID", "uuid_4"])
def test_different_pattern_names(pattern_name):
    template = f"{{{pattern_name}:video_id}}/chunk_000001_000009.mp4"
    pattern_handlers = {pattern_name: r"[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12}"}

    regex, fields = compile_template(template, pattern_handlers)

    assert fields == [(pattern_name, "video_id")]
    match = regex.match("1d408610-f129-47a8-a4c1-1a6e0ca2d16f/chunk_000001_000009.mp4")
    assert match is not None
