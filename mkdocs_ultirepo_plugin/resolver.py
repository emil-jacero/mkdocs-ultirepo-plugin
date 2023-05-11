import logging
import sys
from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from mkdocs.utils import warning_filter

from .include_parsers import ParserInterface

log = logging.getLogger(__name__)
log.addFilter(warning_filter)

class Resolver:
    def __init__(self, resolve_depth: int = 0, resolve_max_depth: int = 1, parsers: List[Tuple] = None) -> None:
        self.resolve_depth = resolve_depth
        self.resolve_max_depth = resolve_max_depth
        self.parsers = parsers
        self.parent_dir: Path = None
        self.include_parent_dir: Path = None
    
    def strip_prefix(self, string: str) -> str:
        result = string.split(" ", 1)
        return result[1]
    
    def _include_pattern_exists(self, string: str) -> Tuple[bool, ParserInterface]:
        result = False, ""

        for pattern, parser in self.parsers:
            if string.startswith(pattern):
                result = True, parser

        return result

    def _get_parent_dir(self, string: str) -> Path:
        transformed_string = string.lower().replace(" ", "-")

        # Handle nested parent dirs. For example when resolving nested includes
        if self.parent_dir:
            parent = deepcopy(self.parent_dir)
            child = Path(transformed_string)
            result = parent / child
        else:
            result = Path(transformed_string)

        return result

    def _resolve_dict(self, item: Dict) -> Tuple[List, List[dict]]:
        key, value = list(item.items())[0]

        # Parent dir is used later to place the files in the correct parent directory when merging
        self.parent_dir = self._get_parent_dir(key)

        resolved_value, paths = self._resolve(value)
        if len(resolved_value) <= 1:
            return [{key: resolved_value[0]}], paths
        else:
            return [{key: resolved_value}], paths

    def _resolve_list(self, items: List) -> Tuple[List, List[dict]]:
        resolved_items = []
        resolved_paths = []

        for item in items:
            resolved_item, paths = self._resolve(item)
            resolved_items.extend(resolved_item)
            resolved_paths.extend(paths)

    def _resolve_string(self, string: str) -> Tuple[List, List[dict]]:

        pattern_exists, parser = self._include_pattern_exists(string)

        if not pattern_exists:
            if not self.include_parent_dir is None:  # Handle the infinite resolver. For example nested !includes
                result = str(self.include_parent_dir / Path(string))
            else:
                result = string

            return [result], []
        else:
            resolve_depth = self.resolve_depth + 1
            resolver = Resolver(resolve_depth=resolve_depth, resolve_max_depth=self.resolve_max_depth)
            stripped_string = self.strip_prefix(string)
            include = parser(resolver, self.parent_dir, stripped_string)
            resolved_nav, resolved_paths = include.execute()

            return resolved_nav, resolved_paths

    def _resolve(self, value: Union[str, List, Dict]) -> Tuple[Union[str, List, Dict], List[dict]]:

        if isinstance(value, dict):
            return self._resolve_dict(value)
        elif isinstance(value, list):
            return self._resolve_list(value)
        elif isinstance(value, str):
            return self._resolve_string(value)
        else:
            return [], []

    def resolve(self, nav, include_parent_dir: Path = None) -> Tuple[Union[str, List, Dict], List[dict]]:
        self.include_parent_dir = include_parent_dir
        if self.resolve_depth > self.resolve_max_depth:
            log.info(
                f"Reached maximum depth ({self.resolve_max_depth}). Stopping further processing of include directives."
            )
            return nav

        resolved_nav = []
        resolved_paths = []

        for item in nav:
            resolved_item, resolved_path = self._resolve(item)
            resolved_nav.extend(resolved_item)
            resolved_paths.extend(resolved_path)

        return resolved_nav, resolved_paths
