# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

[*see all changes*](https://github.com/jannismain/mkdocs-macros-includex/compare/v0.0.6...HEAD)

## [0.0.6] - 2023-11-08
[0.0.6]: https://github.com/jannismain/mkdocs-macros-includex/releases/tag/v0.0.6


### Added

- support older Python versions up to 3.7

### Changed

- an error is now raised when `start_match` or `end_match` are provided but don't match any line in the included content. Previously, the content was included in full if no match was found.
- **code**: only infer code block language based on extension of included file.
    - pygments' `guess_lexer` fails to work on the most obvious snippets while producing false-positives for others.

[*see all changes*](https://github.com/jannismain/mkdocs-macros-includex/compare/v0.0.5...v0.0.6)

## [0.0.5] - 2023-09-12
[0.0.5]: https://github.com/jannismain/mkdocs-macros-includex/releases/tag/v0.0.5

### Changed

- **code**: Infer code language using `pygments`, if available (added as optional dependency)
    - if `pygments` is not available, map some file extensions to pygments language (e.g. `yml` -> `yaml`)

[*see all changes*](https://github.com/jannismain/mkdocs-macros-includex/compare/v0.0.4...v0.0.5)

## [0.0.4] - 2023-09-12
[0.0.4]: https://github.com/jannismain/mkdocs-macros-includex/releases/tag/v0.0.4

### Added

- **code**: Render included content as code block

### Changed

- `lang` is deprecated and will be removed in favor of `code`

[*see all changes*](https://github.com/jannismain/mkdocs-macros-includex/compare/v0.0.3...v0.0.4)

## [0.0.3] - 2023-09-08
[0.0.3]: https://github.com/jannismain/mkdocs-macros-includex/releases/tag/v0.0.3

### Fixed

- **caption**: line numbers are no longer off

[*see all changes*](https://github.com/jannismain/mkdocs-macros-includex/compare/v0.0.2...v0.0.3)

## [0.0.2] - 2023-08-29
[0.0.2]: https://github.com/jannismain/mkdocs-macros-includex/releases/tag/v0.0.2

### Added

- **caption**: add default or custom caption to included content in code blocks
- **suffix**: add content after included content (but before any markup)

### Changed

- `includex` errors are raised by default
- treat as error when no content is found to include

[*see all changes*](https://github.com/jannismain/mkdocs-macros-includex/compare/v0.0.1...v0.0.2)

## [0.0.1] - 2023-07-21
[0.0.1]: https://github.com/jannismain/mkdocs-macros-includex/releases/tag/v0.0.1

Initial release

[*see all changes*](https://github.com/jannismain/mkdocs-macros-includex/compare/f0c8a335f...v0.0.1)
