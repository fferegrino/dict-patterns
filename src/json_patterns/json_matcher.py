from json_patterns.patterns import compile_template


class JSONMatcher:
    """
    A class for matching JSON objects using pattern-based templates.
    
    The JSONMatcher allows you to compare two JSON objects where one can contain
    pattern placeholders (e.g., {string:name}) that will be matched against
    corresponding values in the other object. Matched values are stored and can
    be reused for consistency across multiple matches.
    
    Parameters
    ----------
    pattern_handlers : dict
        A dictionary mapping pattern names to their corresponding regex patterns.
        For example: {'string': r'[a-zA-Z]+', 'number': r'\\d+'}
    
    Attributes
    ----------
    pattern_handlers : dict
        The pattern handlers dictionary passed during initialization.
    values : dict
        A dictionary storing matched values for each pattern type, organized by
        pattern name and identifier.
    
    Examples
    --------
    >>> pattern_handlers = {
    ...     'string': r'[a-zA-Z]+',
    ...     'number': r'\\d+'
    ... }
    >>> matcher = JSONMatcher(pattern_handlers)
    >>> 
    >>> left = {'name': '{string:user_name}', 'age': '{number:user_age}'}
    >>> right = {'name': 'John', 'age': '25'}
    >>> matcher.match(left, right)
    >>> print(matcher.values)
    {'string': {'user_name': 'John'}, 'number': {'user_age': '25'}}

    """

    def __init__(self, pattern_handlers: dict):
        """
        Initialize the JSONMatcher with pattern handlers.
        
        Parameters
        ----------
        pattern_handlers : dict
            Dictionary mapping pattern names to regex patterns.

        """
        self.pattern_handlers = pattern_handlers
        self.values = {}
        self.__reset_values()
    
    def __reset_values(self):
        """
        Reset the values dictionary to empty state for each pattern type.
        
        This method is called internally to clear previous match results
        before performing a new match operation.
        """
        self.values = {
            key: {}
            for key in self.pattern_handlers
        }

    def match(self, template: dict, actual: dict) -> None:
        """
        Match two JSON objects using pattern templates.
        
        This method compares the template object (which may contain pattern placeholders)
        against the actual object (which contains actual values). Pattern matches
        are stored in the `values` attribute for later use.
        
        Parameters
        ----------
        template : dict
            The template object that may contain pattern placeholders.
            Keys must match exactly with the right object.
        actual : dict
            The actual object to match against. This object should contain
            concrete values that match the patterns in the left object.
        
        Raises
        ------
        ValueError
            If the objects don't match according to the pattern rules, or if
            lists have different lengths, or if pattern values are inconsistent
            across multiple matches.
        
        Examples
        --------
        >>> matcher = JSONMatcher({'string': r'[a-zA-Z]+'})
        >>> template = {'user': '{string:name}'}
        >>> actual = {'user': 'Alice'}
        >>> matcher.match(template, actual)  # No exception raised
        >>> matcher.values['string']['name']
        'Alice'

        """
        self.__reset_values()
        self._match(template, actual, "$")

    def _match(self, template: dict, actual: dict, path: str) -> None:
        """
        Recursively match nested JSON objects.
        
        This is an internal method that handles the recursive matching of
        nested dictionaries, lists, and pattern-based string matching.
        
        Parameters
        ----------
        template : dict
            The template object (left side of comparison).
        actual : dict
            The actual object (right side of comparison).
        path : str
            The current path in the JSON structure for error reporting.
            Uses dot notation (e.g., "$.user.profile.name").
        
        Raises
        ------
        ValueError
            If objects don't match at any level, with detailed path information.

        """
        if template.keys() != actual.keys():
            raise ValueError(f"Keys at {path} do not match")
        for key in template:
            template_value = template[key]
            actual_value = actual[key]
            if isinstance(template_value, dict) and isinstance(actual_value, dict):
                self._match(template_value, actual_value, f"{path}.{key}")
            elif isinstance(template_value, list) and isinstance(actual_value, list):
                if len(template_value) != len(actual_value):
                    raise ValueError(f"Lists at {path}.{key} do not match, they have different lengths")
                for i in range(len(template_value)):
                    self._match(template_value[i], actual_value[i], f"{path}.{key}[{i}]")
            elif isinstance(template_value, str) and isinstance(actual_value, str) and self.pattern_handlers:
                regex, fields = compile_template(template_value, self.pattern_handlers)
                if not fields:
                    if template_value != actual_value:
                        raise ValueError(f"Strings at {path}.{key} do not match")
                    continue
                match = regex.match(actual_value)
                if not match:
                    raise ValueError(f"Strings at {path}.{key} = {actual_value} do not match the pattern {template_value}")
                for i, (pattern, identifier) in enumerate(fields, start=1):
                    if identifier is None:
                        continue
                    if identifier not in self.values[pattern]:
                        self.values[pattern][identifier] = match.group(i)
                    elif self.values[pattern][identifier] != match.group(i):
                        raise ValueError(f"Values at {path}.{key}.{identifier} do not match")
            elif template_value != actual_value:
                raise ValueError(f"Values at {path}.{key} do not match")
