"""Documentation macros.

See the [`mkdocs-macros-plugin` Documentation](https://mkdocs-macros-plugin.readthedocs.io/) for more information.

"""
import pathlib


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
    escape=[],
    replace=[],
    add_heading_levels: int = 0,
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

        escape (List[str]): characters in list will be escaped using `\`
        replace (List[Tuple(str, str)]): replace arbitrary substrings
        add_heading_levels: If > 0, append as many "#" to any line starting with "#"

            this is meant to be used with Markdown files, that need to fit into an existing header structure

    Returns:
        content of file at *filepath*, restricted by remaining arguments

    !!! seealso "Examples"
        Have a look at [test_macros][] for some examples on how to use [macros.include_partial][]

    """
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

        if dedent == True and content:
            dedent = len(content[0].rstrip()) - len(content[0].strip())

        if add_heading_levels:
            content = [
                add_heading_levels * "#" + c if c.startswith("#") else c
                for c in content
            ]

        if not keep_trailing_whitespace:
            content[-1] = content[-1].rstrip()

        if raw:
            content.insert(0, "{% raw %}\n")
            if keep_trailing_whitespace:
                content.append("{% endraw %}\n")
            else:
                content.append("\n{% endraw %}")

        content = "".join(
            [
                ((indent_char * indent) if i > 0 or indent_first else "")
                + line[dedent:]
                for i, line in enumerate(content)
            ]
        )

        for esc in escape:
            content = content.replace(esc, "\\" + esc)

        for orig, repl in replace:
            content = content.replace(orig, repl)

        return content

    except Exception as e:
        return (
            f'<span class="error" style="color:red">{e}</span>'
            if not silence_errors
            else ""
        )
