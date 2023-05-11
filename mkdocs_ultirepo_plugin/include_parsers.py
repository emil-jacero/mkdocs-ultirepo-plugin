import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Union

log = logging.getLogger(__name__)
# log.addFilter(warning_filter)

class ParserInterface(ABC):
    def __init__(self, resolver, parent_dir, string) -> None:
        super().__init__()
        self.resolver = resolver
        self.parent_dir = parent_dir
        self.string = string

    @abstractmethod
    def execute(self, *args, **kwargs) -> Tuple[Union[str, List, Dict], List[dict]]:
        pass

class IncludeParserBang(ParserInterface):
    def __init__(self, resolver, parent_dir, string) -> None:
        super().__init__(resolver, parent_dir, string)

    def execute(self, *args, **kwargs) -> Tuple[Union[str, List, Dict], List[dict]]:
        return ["IncludeParserBang"], [{"alias": self.string, "docs_dir": "derpio/derp"}]
        return [], []

class IncludeParserPercent(ParserInterface):
    def __init__(self, resolver, string) -> None:
        super().__init__(resolver, string)

    def execute(self, *args, **kwargs) -> Tuple[Union[str, List, Dict], List[dict]]:
        """Implements the parser using % as pattern"""
        print(f"IncludeParserPercent executed - {self.resolver} - {self.pattern}")
        return ["IncludeParserPercent"], [{"alias": "Derp", "docs_dir": "derpio/derp"}]
