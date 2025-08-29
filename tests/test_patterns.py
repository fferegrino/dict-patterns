from json_patterns.patterns import compile_template


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
