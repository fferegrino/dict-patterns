# JSON Patterns

A template engine for JSON data – useful for tests!

## Overview

JSON Patterns is a Python library that allows you to match JSON objects using pattern-based templates. It's particularly useful for testing scenarios where you need to verify that JSON responses match expected patterns while allowing for dynamic values.

## Features

- **Pattern-based matching**: Use placeholders like `{string:name}` to match dynamic values
- **Value consistency**: Ensure the same pattern identifier has consistent values across matches
- **Nested structure support**: Handle complex nested JSON objects and arrays
- **Custom exceptions**: Rich error handling with specific exception types
- **Flexible patterns**: Define your own regex patterns for different data types

## Installation

```bash
pip install json-patterns
```

## Quick Start

```python
from json_patterns import JSONMatcher

# Define your patterns
patterns = {
    'string': r'[a-zA-Z]+',
    'number': r'\d+',
    'uuid': r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
}

# Create a matcher
matcher = JSONMatcher(patterns)

# Define your template with placeholders
template = {
    'user': {
        'name': '{string:user_name}',
        'age': '{number:user_age}',
        'id': '{uuid:user_id}'
    }
}

# Your actual data
actual = {
    'user': {
        'name': 'John',
        'age': '25',
        'id': '1d408610-f129-47a8-a4c1-1a6e0ca2d16f'
    }
}

# Match them
matcher.match(template, actual)

# Access matched values
print(matcher.values['string']['user_name'])  # 'John'
print(matcher.values['number']['user_age'])   # '25'
print(matcher.values['uuid']['user_id'])      # '1d408610-f129-47a8-a4c1-1a6e0ca2d16f'
```

## Pattern Syntax

Patterns use the format `{pattern_name:identifier}` where:
- `pattern_name` is the type of pattern to match (must be defined in your patterns dict)
- `identifier` is an optional name for the captured value (used for consistency checking)

### Examples

```python
# Simple patterns
'{string:name}'           # Matches alphabetic strings
'{number:age}'            # Matches numeric strings
'{uuid:user_id}'          # Matches UUID format

# Patterns without identifiers (no consistency checking)
'{string}'                # Matches any string, no identifier
'{number}'                # Matches any number, no identifier
```

## Error Handling

The library provides custom exceptions for better error handling and debugging:

### Exception Hierarchy

```
JSONPatternError (base)
├── JSONStructureError
│   ├── JSONKeyMismatchError
│   └── JSONListLengthMismatchError
├── JSONValueMismatchError
├── JSONPatternMatchError
├── JSONPatternValueInconsistencyError
└── JSONPatternTypeError
```

### Example Error Handling

```python
from json_patterns import (
    JSONMatcher,
    JSONPatternError,
    JSONStructureError,
    JSONKeyMismatchError,
    JSONPatternMatchError
)

try:
    matcher = JSONMatcher({'email': r'[^@]+@[^@]+\.[^@]+'})
    template = {'email': '{email:user_email}'}
    actual = {'email': 'invalid-email'}
    matcher.match(template, actual)
except JSONPatternMatchError as e:
    print(f"Pattern match failed at {e.path}")
    print(f"Expected pattern: {e.template}")
    print(f"Actual value: {e.actual}")
except JSONStructureError as e:
    print(f"Structure mismatch: {e}")
except JSONPatternError as e:
    print(f"Any JSON pattern error: {e}")
```

### Exception Types

- **`JSONKeyMismatchError`**: Dictionary keys don't match between template and actual
- **`JSONListLengthMismatchError`**: Lists have different lengths
- **`JSONValueMismatchError`**: Simple values don't match (with optional template/actual values)
- **`JSONPatternMatchError`**: String doesn't match the pattern template
- **`JSONPatternValueInconsistencyError`**: Same pattern identifier has different values
- **`JSONPatternTypeError`**: Unknown pattern type encountered

## Advanced Usage

### Value Consistency

The library ensures that the same pattern identifier has consistent values across matches:

```python
template = {
    'parent_id': '{uuid:shared_id}',
    'child': {'parent_id': '{uuid:shared_id}'}  # Same identifier
}

actual = {
    'parent_id': '1d408610-f129-47a8-a4c1-1a6e0ca2d16f',
    'child': {'parent_id': '1d408610-f129-47a8-a4c1-1a6e0ca2d16f'}  # Same value
}

# This will work
matcher.match(template, actual)

# This will raise JSONPatternValueInconsistencyError
actual['child']['parent_id'] = 'different-uuid'
matcher.match(template, actual)
```

### Complex Nested Structures

```python
template = {
    'users': [
        {'name': '{string:user_name}', 'age': '{number:user_age}'},
        {'name': '{string:user_name}', 'age': '{number:user_age}'}
    ],
    'metadata': {
        'total': '{number:total_count}',
        'created_at': '{timestamp:creation_time}'
    }
}
```

### Custom Patterns

```python
# Define your own patterns
patterns = {
    'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    'phone': r'\+?1?\d{9,15}',
    'timestamp': r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',
    'slug': r'[a-z0-9]+(?:-[a-z0-9]+)*'
}
```

## API Reference

### JSONMatcher

The main class for matching JSON objects.

#### Constructor

```python
JSONMatcher(pattern_handlers: dict)
```

- `pattern_handlers`: Dictionary mapping pattern names to regex patterns

#### Methods

- `match(template: dict, actual: dict)`: Match template against actual JSON
- `values`: Property containing matched values organized by pattern type

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
