"""Documentation macros.

See the [`mkdocs-macros-plugin` Documentation](https://mkdocs-macros-plugin.readthedocs.io/) for more information.

"""
import pathlib


def define_env(env):
    """Define variables, macros and filters for mkdocs-macros."""

    env.macro(include_partial)


def include_partial(
    filepath,
    start=0,
    end=None,
    lines=0,
    dedent=0,
    keep_trailing_whitespace=False,
    start_match="",
    end_match="",
    start_offset=0,
    end_offset=1,
) -> str:
    """Include parts of a file.

    Note:
        Whitespace (spaces, empty lines) will be stripped from the end of file.
        This prevents all includes of full files to end in a newline.

    Args:
        filepath: file to include
        start: line number to begin include (is overwritten, if start_match matches a line)
        end: line number to end include (is overwritten, if end_match matches a line)
             Use negative numbers to index from end of file (e.g. -3 to skip last 3 lines of file)
             Must be greater than start, otherwise no content will be returned.
        lines: number of lines to return (takes precedence over end and end_match)
        dedent: if True, dedent by indentation of first line to be returned
        start_match: find start by providing text that shall match the first line
        end_match: find end by providing text that shall match the last line
                   cannot be used together with *lines*
        start_offset: number of lines to offset line found by *start_match*
                      provide positive integer to exclude that many lines after matched line
                      provide negative integer to include additional lines before matched line
        end_offset: number of lines to offset line found by *end_match*
                    provide positive integer to include additional lines after matched line
                    provide negative integer to exclude lines before matched line
                    e.g. end_offset=1 will include the matched line in the output (default)

    Returns:
        content of file at *filepath* that matches remaining arguments

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

        content = "".join([line[dedent:] for line in content])
        return content.rstrip() if not keep_trailing_whitespace else content
    except Exception as e:
        return str(e)
