# User Guide

<!-- include README without first heading -->
{{ includex("README.md", start=2) }}

## Examples

### Include complete file

{{ show_and_tell("includex('LICENSE')") }}

### Include based on lines

{{ show_and_tell("includex('LICENSE', end=3)") }}

{{ show_and_tell("includex('LICENSE', start=1, lines=3)") }}

### Include based on content

Include a content block by matching the start line and specifying the number of lines to include:

{{ show_and_tell("includex('mkdocs.yml', start_match='plugins:', lines=2)") }}

Inlude a content block by matching the beginning of the next block:

{{ show_and_tell("includex('mkdocs.yml', start_match='features:', end_match='nav:')") }}

Inlude a content block by matching the line that starts the block:

{{ show_and_tell("includex('mkdocs.yml', start_match='features:', start_offset=1, end_match='nav:')") }}

Inlude a content block by matching the end of the block:

{{ show_and_tell("includex('mkdocs.yml', start_match='site_name:', end_match='repo_name:', include_end_match=True)") }}

### Modifying indentation

The included file content is dedented by default. However, you can also include content with its original indentation:

{{ show_and_tell("includex('mkdocs.yml', start_match='features:', end_match='nav:', dedent=False)") }}

or set your own level of indentation:

{{ show_and_tell("includex('mkdocs.yml', start_match='features:', end_match='nav:', indent=8, indent_first=True)") }}

You can also choose a custom character to be used for this indentation:

{{ show_and_tell("includex('mkdocs.yml', start_match='features:', end_match='nav:', indent=8, indent_first=True, indent_char='.')") }}

### Escape characters

{{ show_and_tell("includex('mkdocs.yml', start_match='features:', end_match='nav:', start_offset=1, escape=['-'])") }}

The escape notice at the bottom can be disabled:

{{ show_and_tell("includex('mkdocs.yml', start_match='features:', end_match='nav:', start_offset=1, escape=['-'], escape_notice=False)") }}

### Replace characters

{{ show_and_tell("includex('mkdocs.yml', start_match='features:', end_match='nav:', start_offset=1, replace=[('-', '~')])") }}

For replaced chraracters, a replace notice can be added:

{{ show_and_tell("includex('mkdocs.yml', start_match='features:', end_match='nav:', start_offset=1, replace=[('-', '~')], replace_notice=True)") }}

### Wrap in code block

{{ show_and_tell("includex('mkdocs.yml', lines=3, lang='yaml')", render_result=True) }}

### Include a caption

{{ show_and_tell("includex('mkdocs.yml', lines=3, lang='yaml', caption=True)", render_result=True) }}

#### Custom caption

{{ show_and_tell("includex('mkdocs.yml', lines=3, lang='yaml', caption='Excerpt from MkDocs configuration file')", render_result=True) }}

{{ show_and_tell("includex('mkdocs.yml', lines=3, lang='yaml', caption='Excerpt from %(filepath)s')", render_result=True) }}

### Wrap in `raw` tags

You can wrap included content in `{\% raw \%}` tags to prevent any further macro syntax from being executed:

```py
includex('mkdocs.yml', lines=3, raw=True)
```

``` title="Result"
{{ includex('mkdocs.yml', lines=3, raw=True) }}
```

### Error Handling

By default, an exception raised by `includex` will be raised, which invokes the default macros error handling. This means the whole page will be replaced by an error message and the corresponding traceback:

```
includex("foo.txt")
```

??? quote "Example of rendered error output"

    *File: `index.md`*

    *FileNotFoundError:* [Errno 2] No such file or directory: 'foo.txt'

    ```
    Traceback (most recent call last):
    ...
    File "/Users/mkj/Developer/mkdocs-macros-includex/includex.py", line XXX, in includex
        raise e
    ...
    FileNotFoundError: [Errno 2] No such file or directory: 'foo.txt'
    ```

If you'd rather have the error message inserted into the document, so that the remainder of the document is  unaffected by the error in any single macro, you can set `raise_errors=False`.

{{ show_and_tell("includex('foo.txt', raise_errors=False)", render_result=True) }}

You can also choose to silence errors (`silence_errors=True`) completely. If errors are silenced, no content is being included at all.

{{ show_and_tell("includex('foo.txt', silence_errors=True)") }}
