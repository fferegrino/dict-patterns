import pytest


def test_plugin(dict_matcher):
    assert dict_matcher is not None
    assert dict_matcher.pattern_handlers == {}
    assert dict_matcher.values == {}


class TestWithPatternHandlers:
    @pytest.fixture
    def pattern_handlers(self):
        return {
            "string": r"[a-zA-Z]+",
            "number": r"\d+",
        }

    def test_with_pattern_handlers(self, dict_matcher):
        assert dict_matcher is not None
        assert dict_matcher.pattern_handlers == {
            "string": r"[a-zA-Z]+",
            "number": r"\d+",
        }
        assert dict_matcher.values == {
            "string": {},
            "number": {},
        }

    def test_dict_match(self, dict_match):
        template = {
            "name": "{string:name}",
            "age": "{number:age}",
        }
        actual = {
            "name": "John",
            "age": "25",
        }
        extracted_values = dict_match(template, actual)

        assert extracted_values == {
            "string": {"name": "John"},
            "number": {"age": "25"},
        }
