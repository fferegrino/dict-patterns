import pytest

from json_patterns.exceptions import (
    JSONKeyMismatchError,
    JSONListLengthMismatchError,
    JSONPatternMatchError,
    JSONPatternValueInconsistencyError,
)
from json_patterns.json_matcher import JSONMatcher


def test_json_matcher_no_patterns():
    """Test basic JSON matching without any pattern placeholders."""
    json_matcher = JSONMatcher({})

    template = {
        "id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
        "name": "John Doe",
        "age": 30,
        "email": "john.doe@example.com",
        "address": {
            "street": "123 Main St",
        },
    }

    actual = {
        "id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
        "name": "John Doe",
        "age": 30,
        "email": "john.doe@example.com",
        "address": {
            "street": "123 Main St",
        },
    }

    json_matcher.match(template, actual)


def test_json_matcher_with_simple_patterns():
    """Test JSON matching with basic pattern placeholders."""
    simple_patterns = {
        "name": r"[A-Za-z]+\s[A-Za-z]+",
        "uuid": r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    }
    json_matcher = JSONMatcher(simple_patterns)

    template = {
        "id": "{uuid}",
        "name": "{name}",
        "age": 30,
        "email": "john.doe@example.com",
        "address": {
            "street": "123 Main St",
        },
    }

    actual = {
        "id": "1d408610-f129-47a8-a4c1-1a6e0ca2d16f",
        "name": "John Doe",
        "age": 30,
        "email": "john.doe@example.com",
        "address": {
            "street": "123 Main St",
        },
    }

    json_matcher.match(template, actual)


def test_json_matcher_with_simple_patterns_and_value_repetition():
    """Test JSON matching with pattern placeholders and value consistency across nested structures."""
    simple_patterns = {
        "name": r"[A-Za-z]+\s[A-Za-z]+",
        "uuid": r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    }
    json_matcher = JSONMatcher(simple_patterns)

    template = {
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
        ],
    }

    actual = {
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
        ],
    }

    json_matcher.match(template, actual)

    assert json_matcher.values == {
        "name": {},
        "uuid": {"parent": "1d408610-f129-47a8-a4c1-1a6e0ca2d16f", "child": "1d408610-f129-47a8-a4c1-1a6e0ca2d16a"},
    }


def test_json_matcher_ecommerce_order():
    """Test a realistic e-commerce order scenario with various pattern types."""
    patterns = {
        "order_id": r"ORD-\d{8}-\d{4}",
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "phone": r"\+1-\d{3}-\d{3}-\d{4}",
        "sku": r"[A-Z]{2}\d{4}-[A-Z0-9]{3}",
        "price": r"\$\d+\.\d{2}",
        "timestamp": r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z",
    }

    json_matcher = JSONMatcher(patterns)

    template = {
        "order": {
            "id": "{order_id:order_number}",
            "customer": {"email": "{email:customer_email}", "phone": "{phone:customer_phone}", "name": "Alice Johnson"},
            "items": [
                {"sku": "{sku:product_1}", "price": "{price:price_1}", "quantity": 2},
                {"sku": "{sku:product_2}", "price": "{price:price_2}", "quantity": 1},
            ],
            "total": "{price:total_amount}",
            "created_at": "{timestamp:order_time}",
        }
    }

    actual = {
        "order": {
            "id": "ORD-20241201-1234",
            "customer": {"email": "alice.johnson@example.com", "phone": "+1-555-123-4567", "name": "Alice Johnson"},
            "items": [
                {"sku": "EL1234-ABC", "price": "$29.99", "quantity": 2},
                {"sku": "BK5678-XYZ", "price": "$15.50", "quantity": 1},
            ],
            "total": "$75.48",
            "created_at": "2024-12-01T14:30:00Z",
        }
    }

    json_matcher.match(template, actual)

    expected_values = {
        "order_id": {"order_number": "ORD-20241201-1234"},
        "email": {"customer_email": "alice.johnson@example.com"},
        "phone": {"customer_phone": "+1-555-123-4567"},
        "sku": {"product_1": "EL1234-ABC", "product_2": "BK5678-XYZ"},
        "price": {"price_1": "$29.99", "price_2": "$15.50", "total_amount": "$75.48"},
        "timestamp": {"order_time": "2024-12-01T14:30:00Z"},
    }

    assert json_matcher.values == expected_values


def test_json_matcher_api_response():
    """Test matching API response patterns with nested arrays and objects."""
    patterns = {
        "user_id": r"\d+",
        "username": r"[a-zA-Z0-9_]{3,20}",
        "status": r"(active|inactive|pending)",
        "role": r"(admin|user|moderator)",
        "ip_address": r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
        "session_id": r"[a-f0-9]{32}",
    }

    json_matcher = JSONMatcher(patterns)

    template = {
        "api_version": "v1.0",
        "response": {
            "users": [
                {
                    "id": "{user_id:admin_id}",
                    "username": "{username:admin_user}",
                    "status": "{status:admin_status}",
                    "role": "{role:admin_role}",
                    "last_login": {"ip": "{ip_address:admin_ip}", "session": "{session_id:admin_session}"},
                },
                {
                    "id": "{user_id:regular_id}",
                    "username": "{username:regular_user}",
                    "status": "{status:regular_status}",
                    "role": "{role:regular_role}",
                    "last_login": {"ip": "{ip_address:regular_ip}", "session": "{session_id:regular_session}"},
                },
            ],
            "pagination": {"total": 2, "page": 1},
        },
    }

    actual = {
        "api_version": "v1.0",
        "response": {
            "users": [
                {
                    "id": "1",
                    "username": "admin_user",
                    "status": "active",
                    "role": "admin",
                    "last_login": {"ip": "192.168.1.100", "session": "a1b2c3d4e5f678901234567890123456"},
                },
                {
                    "id": "42",
                    "username": "john_doe",
                    "status": "active",
                    "role": "user",
                    "last_login": {"ip": "10.0.0.15", "session": "f9e8d7c6b5a432109876543210987654"},
                },
            ],
            "pagination": {"total": 2, "page": 1},
        },
    }

    json_matcher.match(template, actual)

    # Verify specific captured values
    assert json_matcher.values["user_id"]["admin_id"] == "1"
    assert json_matcher.values["user_id"]["regular_id"] == "42"
    assert json_matcher.values["username"]["admin_user"] == "admin_user"
    assert json_matcher.values["username"]["regular_user"] == "john_doe"
    assert json_matcher.values["role"]["admin_role"] == "admin"
    assert json_matcher.values["role"]["regular_role"] == "user"


def test_json_matcher_error_mismatched_keys():
    """Test that mismatched keys between template and actual raise ValueError."""
    json_matcher = JSONMatcher({})

    template = {"name": "John", "age": 30}
    actual = {"name": "John", "age": 30, "email": "john@example.com"}

    with pytest.raises(JSONKeyMismatchError, match="Keys at \\$ do not match"):
        json_matcher.match(template, actual)


def test_json_matcher_error_different_list_lengths():
    """Test that different list lengths raise ValueError."""
    json_matcher = JSONMatcher({})

    template = {"items": [{"id": 1}, {"id": 2}]}
    actual = {"items": [{"id": 1}]}

    with pytest.raises(
        JSONListLengthMismatchError, match="Lists at \\$\\.items do not match, they have different lengths"
    ):
        json_matcher.match(template, actual)


def test_json_matcher_error_pattern_mismatch():
    """Test that pattern mismatches raise ValueError."""
    patterns = {"email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"}
    json_matcher = JSONMatcher(patterns)

    template = {"email": "{email:user_email}"}
    actual = {"email": "not-an-email"}

    with pytest.raises(
        JSONPatternMatchError,
        match="Strings at \\$\\.email = not-an-email do not match the pattern \\{email:user_email\\}",
    ):
        json_matcher.match(template, actual)


def test_json_matcher_error_inconsistent_values():
    """Test that inconsistent pattern values across multiple matches raise ValueError."""
    patterns = {"uuid": r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"}
    json_matcher = JSONMatcher(patterns)

    template = {"parent_id": "{uuid:shared_id}", "child": {"parent_id": "{uuid:shared_id}"}}

    actual = {
        "parent_id": "1d408610-f129-47a8-a4c1-1a6e0ca2d16f",
        "child": {
            "parent_id": "caa8b54a-eb5e-4134-8ae2-a3946a428ec7"  # Different UUID
        },
    }

    with pytest.raises(
        JSONPatternValueInconsistencyError, match="Values at \\$\\.child\\.parent_id\\.shared_id do not match"
    ):
        json_matcher.match(template, actual)


def test_json_matcher_mixed_data_types():
    """Test matching with various data types including booleans, numbers, and null values."""
    patterns = {"string": r"[a-zA-Z]+", "number": r"\d+"}
    json_matcher = JSONMatcher(patterns)

    template = {
        "string_field": "{string:test_string}",
        "number_field": "{number:test_number}",
        "boolean_field": True,
        "null_field": None,
        "float_field": 3.14,
        "integer_field": 42,
    }

    actual = {
        "string_field": "hello",
        "number_field": "123",
        "boolean_field": True,
        "null_field": None,
        "float_field": 3.14,
        "integer_field": 42,
    }

    json_matcher.match(template, actual)

    assert json_matcher.values["string"]["test_string"] == "hello"
    assert json_matcher.values["number"]["test_number"] == "123"


def test_json_matcher_deep_nesting():
    """Test matching with deeply nested structures."""
    patterns = {"id": r"\d+", "name": r"[a-zA-Z]+"}
    json_matcher = JSONMatcher(patterns)

    template = {
        "level1": {"level2": {"level3": {"level4": {"level5": {"id": "{id:deep_id}", "name": "{name:deep_name}"}}}}}
    }

    actual = {"level1": {"level2": {"level3": {"level4": {"level5": {"id": "999", "name": "DeepValue"}}}}}}

    json_matcher.match(template, actual)

    assert json_matcher.values["id"]["deep_id"] == "999"
    assert json_matcher.values["name"]["deep_name"] == "DeepValue"


def test_json_matcher_empty_structures():
    """Test matching with empty objects and arrays."""
    json_matcher = JSONMatcher({})

    template = {"empty_object": {}, "empty_array": [], "nested_empty": {"empty": {}}}

    actual = {"empty_object": {}, "empty_array": [], "nested_empty": {"empty": {}}}

    json_matcher.match(template, actual)  # Should not raise any exceptions


def test_json_matcher_patterns_without_identifiers():
    """Test patterns without identifiers (anonymous patterns)."""
    patterns = {"word": r"[a-zA-Z]+", "number": r"\d+"}
    json_matcher = JSONMatcher(patterns)

    template = {
        "text": "{word}",  # No identifier
        "count": "{number}",  # No identifier
    }

    actual = {"text": "hello", "count": "42"}

    json_matcher.match(template, actual)  # Should work without storing values


def test_json_matcher_complex_list_nesting():
    """Test matching with complex nested list structures."""
    patterns = {"id": r"\d+", "type": r"[a-zA-Z]+"}
    json_matcher = JSONMatcher(patterns)

    template = {
        "categories": [
            {
                "id": "{id:cat1_id}",
                "type": "{type:cat1_type}",
                "subcategories": [
                    {"id": "{id:sub1_id}", "type": "{type:sub1_type}"},
                    {"id": "{id:sub2_id}", "type": "{type:sub2_type}"},
                ],
            },
            {"id": "{id:cat2_id}", "type": "{type:cat2_type}", "subcategories": []},
        ]
    }

    actual = {
        "categories": [
            {
                "id": "1",
                "type": "Electronics",
                "subcategories": [{"id": "11", "type": "Phones"}, {"id": "12", "type": "Laptops"}],
            },
            {"id": "2", "type": "Books", "subcategories": []},
        ]
    }

    json_matcher.match(template, actual)

    # Verify all captured values
    assert json_matcher.values["id"]["cat1_id"] == "1"
    assert json_matcher.values["id"]["cat2_id"] == "2"
    assert json_matcher.values["id"]["sub1_id"] == "11"
    assert json_matcher.values["id"]["sub2_id"] == "12"
    assert json_matcher.values["type"]["cat1_type"] == "Electronics"
    assert json_matcher.values["type"]["cat2_type"] == "Books"
    assert json_matcher.values["type"]["sub1_type"] == "Phones"
    assert json_matcher.values["type"]["sub2_type"] == "Laptops"
