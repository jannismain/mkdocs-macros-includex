"""Documentation macros.

See the [`mkdocs-macros-plugin` Documentation](https://mkdocs-macros-plugin.readthedocs.io/) for more information.

"""
import pathlib
from typing import List, Tuple, Union


def define_env(env):
    """Define variables, macros and filters for mkdocs-macros."""
    env.macro(include_partial)


def include_partial(
    filepath: pathlib.Path,
    start: int = 0,
    end: int = None,
    lines: int = 0,
    dedent=True,
    indent: int = 0,
    indent_char: str = " ",
    indent_first: bool = False,
    keep_trailing_whitespace: bool = False,
    start_match: str = "",
    end_match: str = "",
    start_offset: int = 0,
    end_offset: int = 0,
    include_last: bool = False,
    silence_errors: bool = False,
    raw: bool = False,
    escape: List[str] = None,
    replace: List[Tuple[str]] = None,
    add_heading_levels: int = 0,
    lang: str = None,
    escape_notice: Union[bool, str] = True,
    replace_notice: Union[bool, str] = False,
) -> str:
    r"""Include parts of a file.

    Note:
        Whitespace (spaces, empty lines) will be stripped from the end of file.
        This prevents all includes of full files to end in a newline.

    Args:
        filepath: file to include
        start: line number to begin include (is overwritten, if start_match matches a line).
        end: line number to end include (is overwritten, if end_match matches a line).

            Use negative numbers to index from end of file (e.g. -3 to skip last 3 lines of file).
            Must be greater than start, otherwise no content will be returned.

        lines: number of lines to return (takes precedence over end and end_match)
        dedent (bool): dedent by indentation of first line to be returned
        dedent (int): dedent by that many characters
        indent: add this many *indent_char*s to beginning of each line
        indent_char: single character to use for indentation (default: " " → *space*)
        indent_first: whether to also indent the first line

            `indent` might be used to make the content match the indentation of the document
            where the content is included. As the `include_partial` statement will already be
            indented, the first line doesn't need to be indented in most cases where an indent
            would be used.

        start_match: find start by providing text that shall match the first line
        end_match: find end by providing text that shall match the last line.

            !!! warning
                Cannot be used together with *lines*

        start_offset: number of lines to offset line found by *start_match*
            provide positive integer to exclude that many lines after matched line
            provide negative integer to include additional lines before matched line
        end_offset: number of lines to offset line found by *end_match*

            - provide positive integer to include additional lines after matched line
            - provide negative integer to exclude lines before matched line

        include_last: also include the last line (same as `end_offset=1`)
        silence_errors: if true, do not return exception messages
        raw: will wrap file content in {% raw %} block.

            this prevents further interpretation of the file content by jinja.

        escape (Tuple[str]): characters in list will be escaped using `\`
        replace (Tuple[Tuple(str, str)]): replace arbitrary substrings
        add_heading_levels: If > 0, append as many "#" to any line starting with "#"

            this is meant to be used with Markdown files, that need to fit into an existing header structure

        lang: wrap included file in markdown code fences with this language

            this was added to support escaping an included file (using `raw`) but not have
            the raw-tags part of the code block.

        escape_notice: include note about escaped characters at the end
        replace_notice: include note about replaced strings at the end

    Returns:
        content of file at *filepath*, restricted by remaining arguments

    !!! seealso "Examples"
        Have a look at [test_macros][] for some examples on how to use [macros.include_partial][]

    """
    # use empty list as default argument safely
    escape = [] if escape is None else escape
    replace = [] if replace is None else replace
    prefix, suffix = 0, 0
    has_escaped_characters, has_replaced_characters = False, False

    try:
        filepath = pathlib.Path(filepath)
        content = filepath.open("r").readlines()
        if start_match or end_match:
            first_line_found = not start_match
            for i, line in enumerate(content):
                if not first_line_found and start_match in line:
                    start = i + start_offset
                    first_line_found = True
                    if not lines and end_match:
                        continue
                    else:
                        break
                if first_line_found and end_match and end_match in line:
                    end = i + end_offset + (1 if include_last else 0)
                    break
        if lines:
            end = start + lines

        content = content[start:end]

        for esc in escape:
            for i, line in enumerate(content):
                if esc in line:
                    content[i] = line.replace(esc, "\\" + esc)
                    has_escaped_characters = True

        for orig, repl in replace:
            for idx, line in enumerate(content):
                if orig in line:
                    content[idx] = line.replace(orig, repl)
                    has_replaced_characters = True

        if dedent == True and content:
            dedent = len(content[0].rstrip()) - len(content[0].strip())

        if add_heading_levels:
            content = [
                add_heading_levels * "#" + c if c.startswith("#") else c
                for c in content
            ]

        if not keep_trailing_whitespace:
            content[-1] = content[-1].rstrip()

        if lang is not None:
            content.insert(0, f"```{lang}\n")
            if not content[-1].endswith("\n"):
                content[-1] += "\n"
            content.append("```")
            prefix += 1
            suffix += 1

        if raw:
            content.insert(0, "{% raw %}\n")
            if not content[-1].endswith("\n"):
                content[-1] += "\n"
            content.append("{% endraw %}")
            prefix += 1
            suffix += 1

        if escape_notice and has_escaped_characters:
            if not content[-1].endswith("\n"):
                content[-1] += "\n"
            content.append(
                "*"
                + (
                    "In the above text, the following characters have been escaped: "
                    if escape_notice == True
                    else escape_notice
                )
                + ", ".join(f"` {e} `" for e in escape)
                + "*"
                + "{.caption}"
            )
            suffix += 1

        if replace_notice and has_replaced_characters:
            if not content[-1].endswith("\n"):
                content[-1] += "\n"
            content.append(
                "*"
                + (
                    "In the above text, the following substrings have been replaced: "
                    if replace_notice == True
                    else replace_notice
                )
                + ", ".join(f"{orig} --> {repl}" for orig, repl in replace)
                + "*"
                + "{.caption}"
            )
            suffix += 1

        content = "".join(
            [
                ((indent_char * indent) if i > 0 or indent_first else "")
                + line[dedent:]
                for i, line in enumerate(content)
            ]
        )

        return content

    except Exception as e:
        return (
            f'<span class="error" style="color:red">{e}</span>'
            if not silence_errors
            else ""
        )
