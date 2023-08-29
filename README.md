# `includex`

This is a **pluglet** for mkdocs-macros.
It allows to include arbitrary files in mkdocs (similar to [snippets][] or [jinja include][]) with added convenience.

[snippets]: https://facelessuser.github.io/pymdown-extensions/extensions/snippets/
[jinja include]: https://jinja.palletsprojects.com/en/3.1.x/templates/#include

## Installation

`pip install mkdocs-macros-includex`

## Usage

In the config (`mkdocs.yml`) file:

```yaml
plugins:
  - search
  - macros:
      modules: ['includex']
```
<!-- TODO: Find out which markdown_extensions need to be enabled for which includex features and list them here -->

## Comparison to other tools

### snippets (pymdown-extensions)

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
