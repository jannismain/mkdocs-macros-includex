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
    keep_trailing_whitespace: bool = False,
    start_match: str = "",
    end_match: str = "",
    start_offset: int = 0,
    end_offset: int = 1,
    silence_errors: bool = False,
) -> str:
    """Include parts of a file.

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

            e.g. end_offset=1 will include the matched line in the output (default)

        silence_errors: if true, do not return exception messages

    Returns:
        content of file at *filepath*, restricted by remaining arguments

    """
    try:
        content = pathlib.Path(filepath).open("r").readlines()
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
                    end = i + end_offset
                    break
        if lines:
            end = start + lines

        content = content[start:end]

        if dedent == True and content:
            dedent = len(content[0]) - len(content[0].lstrip())

        content = "".join([indent_char * indent + line[dedent:] for line in content])
        return content.rstrip() if not keep_trailing_whitespace else content
    except Exception as e:
        return (
            f'<span class="error" style="color:red">{e}</span>'
            if not silence_errors
            else ""
        )
