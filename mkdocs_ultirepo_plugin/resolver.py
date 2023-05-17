import logging
import sys
from copy import deepcopy
from pathlib import Path, PosixPath
from typing import Dict, List, Optional, Tuple, Union

from mkdocs.utils import warning_filter

from .include_parsers import ParserInterface

log = logging.getLogger(__name__)
log.addFilter(warning_filter)

class Resolver:
    def __init__(self, resolve_depth: int = 0, resolve_max_depth: int = 1) -> None:
        self.resolve_depth = resolve_depth
        self.resolve_max_depth = resolve_max_depth
        self.parsers = None
        self.parent: Path = None
        self.include_parent: Path = None

    def set_parsers(self, parsers):
        self.parsers = parsers
    
    def strip_prefix(self, string: str) -> str:
        result = string.split(" ", 1)
        return result[1]
    
    def _get_prefix(self, path_str: str) -> str:
        path = Path(path_str)
        if path.parent != Path('.'):
            return str(path.parent)
        else:
            return None
    
    def _include_pattern_exists(self, string: str) -> Tuple[bool, ParserInterface]:
        result = False, None

        for pattern, parser in self.parsers:
            if string.startswith(pattern):
                result = True, parser

        return result

    def _nicelify_string(self, key: str) -> str:
        string = key.lower().replace(" ", "-")
        return string

    def _set_parent(self, item):
        if isinstance(item, dict):
            key, = item.keys()
            value, = item.values()

            nice_string = self._nicelify_string(key)
            child = Path(nice_string)
            
            if not self.parent is None:
                path_parent = self.parent.parent
                if not isinstance(value, str):
                    if not nice_string == self.parent.name and not path_parent == path_parent.parent:
                        self.parent = path_parent / child
                elif isinstance(value, str):
                    pass
                else:
                    pass
            else:
                self.parent = Path(nice_string)

    def _resolve_dict(self, item: Dict) -> Tuple[List, List[dict]]:

        key, = item.keys()
        value, = item.values()

        resolved_value, additional_info = self._resolve(value)
        if len(resolved_value) <= 1:
            return [{key: resolved_value[0]}], additional_info
        else:
            return [{key: resolved_value}], additional_info

    def _resolve_list(self, items: List) -> Tuple[List, List[dict]]:

        resolved_items = []
        additional_info = []

        for item in items:
            resolved_item, info = self._resolve(item)
            resolved_items.extend(resolved_item)
            additional_info.extend(info)
        
        return resolved_items, additional_info

    def _resolve_string(self, string: str) -> Tuple[List, List[dict]]:

        pattern_exists, parser = self._include_pattern_exists(string)
        string_path_prefix = self._get_prefix(string)


        if not pattern_exists:
            if not string_path_prefix == str(self.include_parent) and not self.include_parent is None:
                result = str(self.include_parent / Path(string))
            else:
                result = string

            return [result], []
        else:
            resolve_depth = self.resolve_depth + 1
            resolver = Resolver(resolve_depth=resolve_depth, resolve_max_depth=self.resolve_max_depth)
            stripped_string = self.strip_prefix(string)
            try:
                include = parser(resolver, self.parent, stripped_string)
                resolved_nav, additional_info = include.execute(parsers=self.parsers)

                return resolved_nav, additional_info
            except Exception as e:
                raise Exception(e)

    def _resolve(self, value: Union[str, List, Dict]) -> Tuple[Union[str, List, Dict], List[dict]]:
        self._set_parent(value)

        if isinstance(value, dict):
            return self._resolve_dict(value)
        elif isinstance(value, list):
            return self._resolve_list(value)
        elif isinstance(value, str):
            return self._resolve_string(value)
        else:
            return [], []

    def resolve(self, nav, parent: Path = None) -> Tuple[Union[str, List, Dict], List[dict]]:
        resolved_nav = []
        additional_info = []

        self.include_parent = parent
        if self.resolve_depth > self.resolve_max_depth:
            log.info(
                f"Reached maximum depth ({self.resolve_max_depth}). Stopping further processing of include directives."
            )
            return nav, additional_info

        for item in nav:
            resolved_item, a_info = self._resolve(item)
            resolved_nav.extend(resolved_item)
            additional_info.extend(a_info)

        return resolved_nav, additional_info
