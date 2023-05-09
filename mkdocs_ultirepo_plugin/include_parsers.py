from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Union


class ParserInterface(ABC):
    def __init__(self, resolver, pattern) -> None:
        super().__init__()
        self.resolver = resolver
        self.pattern = pattern

    @abstractmethod
    def execute(self, *args, **kwargs) -> Tuple[Union[str, List, Dict], List[dict]]:
        pass

class IncludeParserBang(ParserInterface):
    def __init__(self, resolver, pattern) -> None:
        super().__init__(resolver, pattern)

    def execute(self, *args, **kwargs):
        """Implements the parser using ! as pattern"""
        print(f"IncludeParserBang executed - {self.resolver} - {self.pattern}")
        return ["IncludeParserBang"], [{"alias": "Derp", "docs_dir": "derpio/derp"}]

class IncludeParserPercent(ParserInterface):
    def __init__(self, resolver, pattern) -> None:
        super().__init__(resolver, pattern)

    def execute(self, *args, **kwargs):
        """Implements the parser using % as pattern"""
        print(f"IncludeParserPercent executed - {self.resolver} - {self.pattern}")
        return ["IncludeParserPercent"], [{"alias": "Derp", "docs_dir": "derpio/derp"}]

class ParserManager:
    def __init__(self):
        self._parsers = {}

    def register_parser(self, name, resolver, pattern, parser):
        if not issubclass(parser, ParserInterface):
            raise TypeError("Parser must implement ParserInterface")
        self._parsers[name] = ( parser, resolver, pattern )
    
    def get_all_patterns(self):
        result = []
        for parser, resolver, pattern in self._parsers.values():
            result.append(pattern)
        return result

    def execute_parser(self, name, *args, **kwargs):
        parser, resolver, pattern = self._parsers.get(name)
        if parser:
            parser_instance = parser(resolver, pattern)
            result = parser_instance.execute(*args, **kwargs)
            return result
        else:
            raise KeyError(f"Parser '{name}' not found")
