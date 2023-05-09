import json
from typing import Any, Callable, Literal, Optional

import yaml
from mkdocs.config.base import Config
from mkdocs.config.config_options import Type as MkType
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import ConfigurationError
from mkdocs.livereload import LiveReloadServer
from mkdocs.plugins import BasePlugin

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
    )

    def __init__(self) -> None:
        self.original_docs_dir = None

    def on_config(self, config: MkDocsConfig) -> Config | None:
        print("ON_CONFIG")
        if not config.get("nav"):
            return config

        # setting originalDocsDir means that on_config has been run
        self.original_docs_dir = config['docs_dir']

        # Parse the nav and handle all import statements
        resolve_max_depth = 2
        parser = Resolver(resolve_max_depth=config.resolve_max_depth)
        resolved_nav, resolved_paths = parser.resolve(config['nav'])

        config["nav"] = resolved_nav
        print(config["nav"])

        # Generate a new "docs" directory
        # merger = Merger(config=config, merged_docs_dir="/home/emil/devel/public/mkdocs-ultirepo-plugin/temp")
        merger = Merger(config=config)
        merged, temp_docs_dir = merger.merge(resolved_paths=resolved_paths)
        print("Resolver")
        print(yaml.dump(resolved_nav, sort_keys=False, indent=2))
        print(resolved_paths)
        print("")
        print("")
        print("Merger")
        print(json.dumps(merged, sort_keys=False, indent=2))

        # Update the docs_dir with our temporary one!
        config["docs_dir"] = temp_docs_dir

        return config
