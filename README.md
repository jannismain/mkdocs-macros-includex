# `includex`

[![coverage](https://codecov.io/gh/jannismain/mkdocs-macros-includex/graph/badge.svg?token=852ISA32PH)](https://codecov.io/gh/jannismain/mkdocs-macros-includex)

Use `includex` to **include** *anything* from any file into your markdown documentation.

## Installation

```sh
pip install mkdocs-macros mkdocs-macros-includex
```

## Usage

`includex` can be configured as a **pluglet** for mkdocs-macros in the `mkdocs.yml` configuration file:

```yaml
plugins:
  - search
  - macros:
      modules: ['includex']
```

Then you can use it to dynamically include file content in your documentation

```md
### Versioning

The version number is defined in the `pyproject.toml` file:

{{ includex("pyproject.toml", start_match="[tool.hatch.version]", code=True, lines=2, caption=True) }}
```

which would be rendered as

---

### Versioning

The version number is defined in the `pyproject.toml` file:

```toml
[tool.hatch.version]
path = "includex.py"
```
<div style="text-align: center; font-style: italic;">pyproject.toml, lines 14-15</div>

---

<!-- TODO: Find out which markdown_extensions need to be enabled for which includex features and list them here -->

## Comparison to other tools

### snippets (pymdown-extensions)

**tl;dr**

- use *snippets* if you want to recursively include content
- use *includex* if you want to include content within macros
- use *includex* if you want to include sections without special markers

The main use case this solves over *[snippets][]* is that it includes partial content (i.e. a section or block) from a file as-is (i.e. without the need for special markers).

Snippets partially supports this now since v9.6 added support to include sections by lines.[^snippet-lines]
Further, v9.7 added to support to sections by name, given that they are marked as such using a special marker comment.[^snippet-sections]

What includex does additionally is to match the start and end of blocks and include them without the need for any markers or line numbers.
While this makes the documentation more prone to break, e.g., when the line that is being matched is changed in a way that it no longer matches, it supports some additional use-cases and requires less custom syntax.

*Snippets* is implemented as a preprocessor, while *includex* is implemented as a [mkdocs-macros][] pluglet. This means that snippets are evaluated earlier than *includex* and prohibits *snippets* to work with other macros, like this:

```jinja
{% for file in get_files("docs/") %}
{{ includex(file) }}
{% endfor %}
```

However, sections included using `includex` are not evaluated themselves, so `includex` cannot be nested (yet). If you need nested includes, use `snippets` instead.

<!-- TODO: nesting includes with snippets vs. includex? -->

<!-- ### mkdocs-include-markdown-plugin -->

[mkdocs-macros]: https://mkdocs-macros-plugin.readthedocs.io/
[snippets]: https://facelessuser.github.io/pymdown-extensions/extensions/snippets/
[^snippet-lines]: https://facelessuser.github.io/pymdown-extensions/extensions/snippets/#snippet-lines
[^snippet-sections]: https://facelessuser.github.io/pymdown-extensions/extensions/snippets/#snippet-sections
[jinja include]: https://jinja.palletsprojects.com/en/3.1.x/templates/#include
