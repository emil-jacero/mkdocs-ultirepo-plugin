# mkdocs-ultirepo-plugin

## Summary

The ultimate plugin for merging documentation in many ways for mkdocs

## TODO

* [ ] Add ability to set custom `alias` by setting the `alias_name` in the nav.yml file. It should parse it to make it url safe with focus on an appealing output.
* [ ] Make the plugin easier to extend by rewriting IncludeParserBang and use either Composition or Inheritance
  * Add the include types from [mkdocs-monorepo-plugin](https://github.com/backstage/mkdocs-monorepo-plugin) to improve backwards compatibility
  * Split out the IncludeParserBang into another file and instantiate the Parser from within the Parser to prefent loops
* [ ] Add the ability to reuse a cloned repo and update it using pull.
