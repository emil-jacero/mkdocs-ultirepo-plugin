import json

import yaml

from mkdocs_ultirepo_plugin.include_parsers import (
    IncludeParserBang,
    IncludeParserPercent,
)
from mkdocs_ultirepo_plugin.resolver import Resolver

# from mkdocs_ultirepo_plugin.merger import Merger

with open("mkdocs.yml", "r") as mkdocs_file:
    mkdocs_config = yaml.safe_load(mkdocs_file)

# Process includes in the nav section
parsers = [("!include", IncludeParserBang), ("%include", IncludeParserPercent)]
resolve_max_depth = 1
resolver = Resolver(resolve_max_depth=resolve_max_depth)
resolver.set_parsers(parsers)
resolved_nav, additional_info = resolver.resolve(mkdocs_config['nav'])

# Update the nav section in mkdocs.yml with the resolved navigation
mkdocs_config["nav"] = resolved_nav

print("## Resolver:")
print(yaml.dump(mkdocs_config, sort_keys=False, indent=2))
print(additional_info)
# print("")
# print("")
# print("")
# print("## Merger:")
# mkdocs_config["docs_dir"] = "/home/emil/devel/public/mkdocs-ultirepo-plugin/docs"
# merger = Merger(config=mkdocs_config, merged_docs_dir="/home/emil/devel/public/mkdocs-ultirepo-plugin/temp")
# merger = Merger(config=mkdocs_config)
# merged = merger.merge(resolved_paths=resolved_paths)
# print(json.dumps(merged, sort_keys=False, indent=2))
