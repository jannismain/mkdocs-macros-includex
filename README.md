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
