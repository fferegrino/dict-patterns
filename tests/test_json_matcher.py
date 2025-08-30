from json_patterns.json_matcher import JSONMatcher


def test_json_matcher_no_patterns():
    json_matcher = JSONMatcher({})

    left = {
        "id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
        "name": "John Doe",
        "age": 30,
        "email": "john.doe@example.com",
        "address": {
            "street": "123 Main St",
        }
    }

    right = {
        "id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
        "name": "John Doe",
        "age": 30,
        "email": "john.doe@example.com",
        "address": {
            "street": "123 Main St",
        }
    }

    json_matcher.match(left, right)

def test_json_matcher_with_simple_patterns():
    simple_patterns = {
        "name": r"[A-Za-z]+\s[A-Za-z]+",
        "uuid": r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    }
    json_matcher = JSONMatcher(simple_patterns)

    left = {
        "id": "{uuid}",
        "name": "{name}",
        "age": 30,
        "email": "john.doe@example.com",
        "address": {
            "street": "123 Main St",
        }
    }

    right = {
        "id": "1d408610-f129-47a8-a4c1-1a6e0ca2d16f",
        "name": "John Doe",
        "age": 30,
        "email": "john.doe@example.com",
        "address": {
            "street": "123 Main St",
        }
    }

    json_matcher.match(left, right)



def test_json_matcher_with_simple_patterns_and_value_repetition():
    simple_patterns = {
        "name": r"[A-Za-z]+\s[A-Za-z]+",
        "uuid": r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    }
    json_matcher = JSONMatcher(simple_patterns)

    left = {
        "id": "{uuid:parent}",
        "name": "{name}",
        "age": 30,
        "email": "john.doe@example.com",
        "address": {
            "street": "123 Main St",
        },
        "children": [
            {
                "id": "{uuid:child}",
                "parent": "{uuid:parent}",
                "name": "{name}",
                "age": 2,
            }
        ]
    }

    right = {
        "id": "1d408610-f129-47a8-a4c1-1a6e0ca2d16f",
        "name": "John Doe",
        "age": 30,
        "email": "john.doe@example.com",
        "address": {
            "street": "123 Main St",
        },
        "children": [
            {
                "id": "1d408610-f129-47a8-a4c1-1a6e0ca2d16a",
                "parent": "1d408610-f129-47a8-a4c1-1a6e0ca2d16f",
                "name": "Junior Doe",
                "age": 2,
            }
        ]
    }

    json_matcher.match(left, right)

    assert json_matcher.values == {
        "name": {},
        "uuid": {
            "parent": "1d408610-f129-47a8-a4c1-1a6e0ca2d16f", 
            "child": "1d408610-f129-47a8-a4c1-1a6e0ca2d16a"
        }
    }