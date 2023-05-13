import json
from typing import Any, Callable, Literal, Optional

import yaml
from mkdocs.config.base import Config
from mkdocs.config.config_options import Type as MkType
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import ConfigurationError
from mkdocs.livereload import LiveReloadServer
from mkdocs.plugins import BasePlugin

from .include_parsers import IncludeParserBang, IncludeParserPercent
from .merger import Merger
from .resolver import Resolver


class UltirepoPlugin(BasePlugin):

    """An `mkdocs` plugin.

    This plugin defines the following event hooks:

    - `on_config`
    - `on_post_build`
    - `on_serve`

    Check the [Developing Plugins](https://www.mkdocs.org/user-guide/plugins/#developing-plugins) page of `mkdocs`
    for more information about its plugin system.
    """

    config_scheme: tuple[tuple[str, MkType]] = (
        ("resolve_max_depth", MkType(int, default=1)),
        ("docs_destination_dir", MkType(str, default="/home/emil/devel/public/mkdocs-ultirepo-plugin/temp"))
    )

    def __init__(self) -> None:
        self.original_docs_dir = None

    def on_config(self, config: MkDocsConfig) -> Config | None:
        print("ON_CONFIG")
        resolve_max_depth = 1
        docs_destination_dir = "/home/emil/devel/public/mkdocs-ultirepo-plugin/temp"
        if not config.get("nav"):
            return config

        # setting originalDocsDir means that on_config has been run
        self.original_docs_dir = config['docs_dir']

        # Parse the nav and handle all import statements
        parsers = [("!include", IncludeParserBang)]
        resolver = Resolver(resolve_max_depth=resolve_max_depth)
        resolver.set_parsers(parsers)
        resolved_nav, additional_info = resolver.resolve(config['nav'])

        config["nav"] = resolved_nav
        print(config["nav"])

        # Generate a new "docs" directory
        merger = Merger(config=config,merged_docs_dir=docs_destination_dir)
        merged, temp_docs_dir  = merger.merge(additional_info=additional_info)

        print("### Resolver")
        print(yaml.dump(resolved_nav, sort_keys=False, indent=2))
        print(additional_info)
        print("")
        print("")
        print("### Merger")
        print(json.dumps(merged, sort_keys=False, indent=2))

        # Update the docs_dir with our temporary one
        config["docs_dir"] = temp_docs_dir

        return config
