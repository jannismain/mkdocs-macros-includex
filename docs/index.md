# User Guide

<!-- include README without first heading -->
{{ includex("README.md", start=2) }}

## Examples

### Include complete file

{{ show_and_tell("includex('mkdocs.yml')") }}

### Include based on lines

{{ show_and_tell("includex('mkdocs.yml', start=2, end=3)") }}

{{ show_and_tell("includex('mkdocs.yml', start=2, lines=2)") }}

### Include based on content

Include a content block by matching the start line and specifying the number of lines to include:

{{ show_and_tell("includex('mkdocs.yml', start_match='plugins:', lines=2)") }}

Inlude a content block by matching the beginning of the next block:

{{ show_and_tell("includex('mkdocs.yml', start_match='features:', end_match='plugins:')") }}

Inlude a content block by matching the line that starts the block:

{{ show_and_tell("includex('mkdocs.yml', start_match='features:', start_offset=1, end_match='plugins:')") }}

Inlude a content block by matching the end of the block:

{{ show_and_tell("includex('mkdocs.yml', start_match='site_name:', end_match='repo_name:', include_end_match=True)") }}

### Modifying indentation

The included file content is dedented by default. However, you can also include content with its original indentation:

{{ show_and_tell("includex('mkdocs.yml', start_match='features:', end_match='plugins:', dedent=False)") }}

or set your own level of indentation:

{{ show_and_tell("includex('mkdocs.yml', start_match='features:', end_match='plugins:', indent=8, indent_first=True)") }}

You can also choose a custom character to be used for this indentation:

{{ show_and_tell("includex('mkdocs.yml', start_match='features:', end_match='plugins:', indent=8, indent_first=True, indent_char='.')") }}

### Escape characters

{{ show_and_tell("includex('mkdocs.yml', start_match='features:', end_match='plugins:', start_offset=1, escape=['-'])") }}

The escape notice at the bottom can be disabled:

{{ show_and_tell("includex('mkdocs.yml', start_match='features:', end_match='plugins:', start_offset=1, escape=['-'], escape_notice=False)") }}

### Replace characters

{{ show_and_tell("includex('mkdocs.yml', start_match='features:', end_match='plugins:', start_offset=1, replace=[('-', '~')])") }}

For replaced chraracters, a replace notice can be added:

{{ show_and_tell("includex('mkdocs.yml', start_match='features:', end_match='plugins:', start_offset=1, replace=[('-', '~')], replace_notice=True)") }}

### Wrap in `raw` tags

You can wrap included content in `{\% raw \%}` tags to prevent any further macro syntax from being executed:

```py
includex('mkdocs.yml', lines=3, raw=True)
```

``` title="Result"
{{ includex('mkdocs.yml', lines=3, raw=True) }}
```

### Error Handling

By default, an exception raised by `includex` will be inserted as an error message into the document. This way, the remaining document is unaffected by the error in any single macro.

{{ show_and_tell("includex('foo.txt')", render_result=True) }}

However, you can either choose to silence errors (`silence_errors=True`) or raise errors (`raise_errors=True`).

If errors are silenced, no content is being included at all.

{{ show_and_tell("includex('foo.txt', silence_errors=True)") }}

If errors are raised, the default error handling is triggered, which means the whole page will be replaced by an error message and the corresponding traceback. You can enable this behavior like this:

```py
includex('foo.txt', raise_errors=True)
```

## Reference

### ::: includex
    options:
        show_root_heading: false
        show_root_toc_entry: false
        docstring_section_style: list
