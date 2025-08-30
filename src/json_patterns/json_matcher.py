from json_patterns.patterns import compile_template


class JSONMatcher:

    def __init__(self, pattern_handlers: dict):
        self.pattern_handlers = pattern_handlers
        self.values = {}
        self.__reset_values()
    
    def __reset_values(self):
        self.values = {
            key: {}
            for key in self.pattern_handlers
        }

    def match(self, left: dict, right: dict) -> None:
        self.__reset_values()
        self._match(left, right, "$")

    def _match(self, left: dict, right: dict, path: str) -> None:
        if left.keys() != right.keys():
            return False
        for key in left:
            left_value = left[key]
            right_value = right[key]
            if isinstance(left_value, dict) and isinstance(right_value, dict):
                self._match(left_value, right_value, f"{path}.{key}")
            elif isinstance(left_value, list) and isinstance(right_value, list):
                if len(left_value) != len(right_value):
                    raise ValueError(f"Lists at {path}.{key} do not match, they have different lengths")
                for i in range(len(left_value)):
                    self._match(left_value[i], right_value[i], f"{path}.{key}[{i}]")
            elif isinstance(left_value, str) and isinstance(right_value, str) and self.pattern_handlers:
                regex, fields = compile_template(left_value, self.pattern_handlers)
                if not fields:
                    if left_value != right_value:
                        raise ValueError(f"Strings at {path}.{key} do not match")
                    continue
                match = regex.match(right_value)
                if not match:
                    raise ValueError(f"Strings at {path}.{key} = {right_value} do not match the pattern {left_value}")
                for i, (pattern, identifier) in enumerate(fields, start=1):
                    if identifier is None:
                        continue
                    if identifier not in self.values[pattern]:
                        self.values[pattern][identifier] = match.group(i)
                    elif self.values[pattern][identifier] != match.group(i):
                        raise ValueError(f"Values at {path}.{key}.{identifier} do not match")
            elif left_value != right_value:
                raise ValueError(f"Values at {path}.{key} do not match")
