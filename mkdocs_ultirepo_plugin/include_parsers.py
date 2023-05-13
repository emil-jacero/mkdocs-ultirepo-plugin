import logging
import os
import re
import sys
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import parse_qs, urlparse

import yaml

from .exceptions import InvalidNavPathError
from .git_clone import GitClone

log = logging.getLogger(__name__)
log.addFilter(warning_filter)

class ParserInterface(ABC):
    def __init__(self, resolver, parent, string) -> None:
        super().__init__()
        self.resolver = resolver
        self.parent = parent
        self.string = string

    @abstractmethod
    def execute(self, *args, **kwargs) -> Tuple[List, List[dict]]:
        pass

class IncludeParserBang(ParserInterface):
    def __init__(self, resolver, parent, string) -> None:
        super().__init__(resolver, parent, string)
        self.clone_dir = None
        self.nav_files = ["nav.yml", "nav.yaml"]

    def _get_docs_sub_dir(self, path: str, docs_dir: str) -> str:
        docs_sub_dir = ""
        for suffix in self.nav_files:
            s = f"/{suffix}"
            if path.endswith(s):
                docs_sub_dir = path.rsplit(s, 1)[0]
                docs_sub_dir = docs_sub_dir.replace(f"{docs_dir}/", "", 1)
        return docs_sub_dir

    def _get_docs_dir(self, nav_config: Dict, abs_path: str, nav_path: str) -> Tuple[str, str]:
        orig_docs_dir = None
        orig_docs_sub_dir = None
        if nav_config.get("docs_dir"):
            docs_dir = nav_config.get("docs_dir")
        elif isinstance(self, IncludeParserBang):
            docs_dir = nav_path.split("/", 1)[0]
        else:
            docs_dir = "docs"
        orig_docs_dir = os.path.join(abs_path, docs_dir)
        orig_docs_sub_dir = self._get_docs_sub_dir(nav_path, docs_dir)
        return orig_docs_dir, orig_docs_sub_dir

    def _clone_git_repo(self, git_url: str, git_ref: str) -> str:
        """
        Clone a git repository and return the path to the cloned repo.

        :param git_url: The URL of the git repository to clone.
        :param git_ref: The git reference to checkout after cloning.
        :return: The path to the cloned git repository.
        """
        git_clone = GitClone(target_dir=self.clone_dir)
        git_repo_path = git_clone.clone(git_url, git_ref)
        return git_repo_path

    def _validate_git_url(self, value: str) -> bool:
        """
        Validate if a given value is a correct git URL.

        :param value: The URL string to validate.
        :return: True if the URL is valid, False otherwise.
        """
        git_url_pattern = r"^(?P<git_url>((git|ssh|http(s)?)|(git@[\w\.]+))(:(//)?)([\w\.@\:/\-~]+)(\.git)(/)?).*$"

        match = re.match(git_url_pattern, value)

        if match:
            return True
        else:
            log.error(f"Not a valid git URL: {value}", file=sys.stderr)
            return False

    def _parse_query_params(self, string: str) -> Tuple[str, str, str]:
        """
        Parse query parameters from a URL string.

        :param url: The URL string containing the query parameters.
        :return: git_url, git_ref, and nav_path extracted from the URL string.
        """
        git_url = None
        git_ref = None
        nav_path = None
        url = urlparse(string)
        query_params = parse_qs(url.query)

        if "ref" not in query_params:
            log.error("Missing 'ref' key in query parameters.")
            raise ValueError("Missing 'ref' key in query parameters.")
        git_ref = query_params["ref"][0]

        if "nav_path" not in query_params:
            log.error("Missing 'nav_path' key in query parameters.")
            raise ValueError(f"Missing 'nav_path' key in query parameters.")
        nav_path = query_params["nav_path"][0]

        # TODO: Verify if this handles SSH based git url
        git_url = url.scheme + "://" + url.netloc + url.path

        return git_url, git_ref, nav_path

    def _get_nav_file_path(self, abs_path, nav_path: str):
        nav_file_path = None

        # Check if nav_path starts with '/'
        if nav_path.startswith("/"):
            raise InvalidNavPathError("nav_path should not begin with '/'.")

        # Check if nav_path already contains 'nav.yml' or 'nav.yaml'
        nav_basename = os.path.basename(nav_path)
        if not nav_basename in self.nav_files:
            # Attempt to find the nav files
            for file_name in self.nav_files:
                temp_nav_file_path = os.path.join(abs_path, nav_path, file_name)
                if os.path.exists(temp_nav_file_path):
                    nav_file_path = temp_nav_file_path
                    break
            else:
                raise InvalidNavPathError(
                    "Neither 'nav.yml' nor 'nav.yaml' found in the specified path"
                )
        else:
            nav_file_path = os.path.join(abs_path, nav_path)

        return nav_file_path

    def _load_nav_file(self, nav_file_path: str) -> Tuple[Dict[str, Union[str, List, Dict]], str]:
        nav_config = None

        try:
            with open(nav_file_path, "r") as nav_file:
                nav_config = yaml.safe_load(nav_file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Nav file not found: {nav_file_path}")
        except PermissionError:
            raise PermissionError(f"Insufficient permissions to open nav file: {nav_file_path}")
        except IsADirectoryError:
            raise IsADirectoryError(f"Expected a file, but got a directory: {nav_file_path}")
        except IOError as e:
            raise IOError(f"I/O error occurred while opening nav file {nav_file_path}: {e}")
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(f"Unable to decode nav file {nav_file_path}: {e}")

        return nav_config

    def _resolve_nav_file(self, nav_config: Dict, parsers: ParserInterface) -> Tuple[List, List[dict]]:
        self.resolver.set_parsers(parsers)
        resolved_nav, additional_info = self.resolver.resolve(nav=nav_config["nav"], parent=self.parent)
        return resolved_nav, additional_info

    def execute(self, *args, **kwargs) -> Tuple[List, List[dict]]:
        super().execute()

        # Set clone dir
        self.clone_dir = kwargs.get("clone_dir", os.path.join(os.getcwd(), "git_clones"))

        # Validate URL
        if not self._validate_git_url(self.string):
            raise ValueError(f"Not a valid Git URL: {self.string}")

        # Parse URL
        git_url, git_ref, nav_path = self._parse_query_params(self.string)

        # Clone Git repo
        git_repo_path = self._clone_git_repo(git_url, git_ref)

        # Get nav path
        nav_file_path = self._get_nav_file_path(git_repo_path, nav_path)

        # Load nav file
        nav_config = self._load_nav_file(nav_file_path)

        # Resolve nav
        resolved_nav, additional_info = self._resolve_nav_file(nav_config, kwargs.get("parsers", None))

        # Get original document directory and sub-directory where the nav file is located
        orig_docs_dir, orig_docs_sub_dir = self._get_docs_dir(nav_config, git_repo_path, nav_path)

        # Add additional info
        additional_info.append({"orig_docs_dir": orig_docs_dir, "orig_docs_sub_dir": orig_docs_sub_dir})

        return resolved_nav, additional_info

class IncludeParserPercent(ParserInterface):
    def __init__(self, resolver, string) -> None:
        super().__init__(resolver, string)

    def execute(self, *args, **kwargs) -> Tuple[List, List[dict]]:
        """Implements the parser using % as pattern"""
        print(f"IncludeParserPercent executed - {self.resolver} - {self.pattern}")
        return ["IncludeParserPercent"], [{"alias": "Derp", "docs_dir": "derpio/derp"}]
