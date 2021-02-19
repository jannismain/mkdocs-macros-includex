"""Documentation macros.

See the [`mkdocs-macros-plugin` Documentation](https://mkdocs-macros-plugin.readthedocs.io/) for more information.

"""
import pathlib


def define_env(env):
    """Define variables, macros and filters for mkdocs-macros."""

    @env.macro
    def include_partial(
        filepath,
        start=0,
        end=-1,
        lines=0,
        dedent=0,
        start_match="",
        end_match="",
    ) -> str:
        """Include parts of a file.

        Args:
            filepath: file to include
            start: line number to begin include (is overwritten, if start_match matches a line)
            end: line number to end include (is overwritten, if end_match matches a line)
                 Use negative numbers to index from end of file (e.g. -3 to skip last 3 lines of file)
                 Must be greater than start, otherwise no content will be returned.
            lines: number of lines to return (takes precedence over end and end_match)
            dedent: if True, dedent by indentation of first line to be returned
            start_match: [description]
            end_match: [description]

        Returns:
            file content

        """
        # print(f"Including '{filepath}'...")
        try:
            content = pathlib.Path(filepath).open("r").readlines()
            # print(f"found '{filepath}'...")
            if start_match:
                # print(f"- start_match={start_match!r}")
                for i, line in enumerate(content):
                    if start_match in line:
                        start = i
                        # print(f"Found '{start_match}' in line {i}: {line.strip()}")
                        if end_match:
                            continue
                        else:
                            break
                    if end_match and end_match in line:
                        end = i
                        break
            if lines:
                end = start + lines

            content = content[start:end]

            if dedent == True and content:
                dedent = len(content[0]) - len(content[0].lstrip())

            return "".join([line[dedent:] for line in content])[:-1]  # omit last \n
        except Exception as e:
            return str(e)
