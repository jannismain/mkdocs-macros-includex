from __future__ import annotations  # compatibility with

import os
import pathlib
from warnings import warn

try:
    from pygments.lexers import guess_lexer_for_filename
    from pygments.util import ClassNotFound

    use_pygments = True
except ImportError:  # pragma: no cover
    use_pygments = False

__version__ = "0.0.6"


def define_env(env):  # pragma: no cover
    env.macro(includex)
    env.macro(show_and_tell)


REPLACE_NOTICE_TEMPLATE = (
    "*In the above text, the following substrings have been replaced: %s*{.caption}"
)
ESCAPE_NOTICE_TEMPLATE = (
    "*In the above text, the following characters have been escaped: %s*{.caption}"
)
ERROR_NOTICE_TEMPLATE = '<span class="error" style="color:red">%s</span>'
CAPTION_TEMPLATE = "*%(filepath)s%(line)s*{.caption}"

CODE_EXTENSION_TO_LANGUAGE = {"yml": "yaml", "j2": "jinja"}
"""Map of file extensions to code language.

Used when pygments is not available.
"""


def includex(
    filepath: pathlib.Path,
    start: int = 1,
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
    include_end_match: bool = False,
    silence_errors: bool = False,
    raise_errors: bool = True,
    raw: bool = False,
    escape: list[str] = None,
    replace: list[tuple[str]] = None,
    add_heading_levels: int = 0,
    lang: str = None,
    escape_notice: bool | str = True,
    replace_notice: bool | str = False,
    caption: bool | str = None,
    alt_code_fences: bool | str = False,
    suffix: str = "",
    code: bool | str = False,
) -> str:
    r"""Include parts of a file.

    Note:
        Whitespace (spaces, empty lines) will be stripped from the end of file.
        This prevents all includes of full files to end in a newline.

    Args:
        filepath: file to include
        start: line number to begin include (is overwritten, if start_match matches a line).
        end: line number to end include on (is overwritten, if end_match matches a line).

            Use negative numbers to index from end of file (e.g. -3 to skip last 3 lines of file).
            Must be greater than start, otherwise no content will be returned.

        lines: number of lines to return (takes precedence over end and end_match)
        dedent (bool): dedent by indentation of first line to be returned
        dedent (int): dedent by that many characters
        indent: add this many *indent_char*s to beginning of each line
        indent_char: single character to use for indentation (default: " " → *space*)
        indent_first: whether to also indent the first line

            `indent` might be used to make the content match the indentation of the document
            where the content is included. As the `includex` statement will already be
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

        include_end_match: also include the ending matched line (same as `end_offset=1`)
        silence_errors: if true, do not return exception messages
        raise_errors: if true, raise exceptions instead of returning error string
        raw: will wrap file content in {% raw %} block.

            this prevents further interpretation of the file content by jinja.

        escape: characters in list will be escaped using `\`
        replace: replace arbitrary substrings
        add_heading_levels: If > 0, append as many "#" to any line starting with "#"

            this is meant to be used with Markdown files, that need to fit into an existing header
            structure

        lang: wrap included file in markdown code fences with this language

            this was added to support escaping an included file (using `raw`) but not have
            the raw-tags be part of the code block.

            Deprecated since v0.0.4, use `code` instead.

        escape_notice: include note about escaped characters at the end
        replace_notice: include note about replaced strings at the end
        caption: include caption for code block

            `lang` must be given for this option to have any effect

        alt_code_fences: when `True`, `'''` is used for code fences so they are not rendered
            in Markdown documents.

            When a custom string is provided, it will be used as code fence marker instead.

        suffix: add this after the included content
        code: render included content as code block

            If `True`, the language will be inferred from the file extension.
            If `""`, code block will be rendered without language.
            Otherwise, the given string will be used as code language

            Added in v0.0.4

    Returns:
        content of file at *filepath*, modified by remaining arguments
    """
    # transform one-based indices into file to zero-based indices into arrays
    start_idx = start - 1 if start > 0 else start
    # end doesn't need to be adjusted here, as it is exclusive in Python but should be
    # inclusive (+1) and also is a one-based index (-1)
    end_idx = end
    # use empty list as default argument safely
    escape = [] if escape is None else escape
    replace = [] if replace is None else replace
    prefix_offset, suffix_offset = 0, 0
    has_escaped_characters, has_replaced_characters = False, False

    try:
        filepath = pathlib.Path(filepath)
        content = filepath.open("r").readlines()
        original_content = content.copy()
        if start_match or end_match:
            first_line_found = not start_match
            for i, line in enumerate(content):
                if not first_line_found and start_match in line:
                    start_idx = i + start_offset
                    first_line_found = True
                    if not lines and end_match:
                        continue
                    else:
                        break
                if first_line_found and end_match and end_match in line:
                    end_idx = i + end_offset + (1 if include_end_match else 0)
                    break
            else:
                raise NoMatchError(
                    f"Couldn't find match for {'end_match' if first_line_found else 'start_match'}="
                    f"'{end_match if first_line_found else start_match}' in {filepath}"
                )
        if lines:
            end_idx = start_idx + lines

        content = content[start_idx:end_idx]

        if not content:
            if raise_errors and not silence_errors:
                raise ValueError("no content to include")
            elif silence_errors:
                return ""
            else:
                return ERROR_NOTICE_TEMPLATE % "no content to include"

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

        assert isinstance(dedent, (bool, int))
        if dedent is True and content:
            dedent = len(content[0].rstrip()) - len(content[0].strip())

        if add_heading_levels:
            content = [add_heading_levels * "#" + c if c.startswith("#") else c for c in content]

        if not keep_trailing_whitespace:
            content[-1] = content[-1].rstrip()

        if suffix:
            if not content[-1].endswith("\n"):
                content[-1] += "\n"
            content[-1] += f"{suffix}\n"

        if lang is not None:
            warn(
                "`lang` option is deprecated and will be removed in a future release. "
                "Use `code` instead.",
                DeprecationWarning,
                stacklevel=2,
            )

        if code is True and lang is None:
            lang = _infer_code_language(filepath, "".join(content))
        elif isinstance(code, str):
            lang = code

        if lang is not None:
            code_fence_marker = (
                "```"
                if alt_code_fences is False
                else ("'''" if alt_code_fences is True else alt_code_fences)
            )
            content.insert(0, f"{code_fence_marker}{lang}\n")
            if not content[-1].endswith("\n"):
                content[-1] += "\n"
            content.append(f"{code_fence_marker}")
            prefix_offset += 1
            suffix_offset += 1

        if raw:
            if not content[-1].endswith("\n"):
                content[-1] += "\n"
            content = ["{% raw %}\n", *content, "{% endraw %}"]
            prefix_offset += 1
            suffix_offset += 1

        # only dedent actual content, not prefix and suffix inserted by this macro
        content = "".join(
            [
                ((indent_char * indent) if i > 0 or indent_first else "")
                + line[dedent if prefix_offset <= i < len(content) - suffix_offset else None :]
                for i, line in enumerate(content)
            ]
        )

        if escape_notice and has_escaped_characters:
            if not content.endswith("\n"):
                content += "\n"
            content += (ESCAPE_NOTICE_TEMPLATE if escape_notice is True else escape_notice) % (
                ", ".join(f"` {e} `" for e in escape)
            )
            suffix_offset += 1

        if replace_notice and has_replaced_characters:
            if not content.endswith("\n"):
                content += "\n"
            content += (
                REPLACE_NOTICE_TEMPLATE % ", ".join(f"{orig} --> {repl}" for orig, repl in replace)
                if replace_notice is True
                else replace_notice
            )
            suffix_offset += 1

        if caption and lang is not None:
            if not content.endswith("\n"):
                content += "\n"

            # lines in file start with 1
            start_lineno = start_idx + 1
            end_lineno = end_idx if end_idx is not None else None
            # indices might be negative
            if start_lineno < 0:
                start_lineno = len(original_content) + start_lineno
            if end_lineno is not None and end_lineno < 0:
                end_lineno = len(original_content) + end_lineno

            content += _render_caption(caption, filepath, start_lineno, end_lineno)
            suffix_offset += 1

        return content

    except Exception as e:
        if raise_errors and not silence_errors:
            raise e
        return (
            ""
            if silence_errors
            else ERROR_NOTICE_TEMPLATE % (f"{e.__class__.__name__}" + (f": {e}" if f"{e}" else ""))
        )


def _infer_code_language(filepath: str | pathlib.Path, text: str) -> str:
    if use_pygments:
        lang = _infer_code_language_pygments(filepath, text)
    if not use_pygments or lang is None:  # fallback in case pygments failed to guess lang
        lang = _infer_code_language_file_extension(filepath)
    return lang.lower()


def _infer_code_language_pygments(filepath: str | pathlib.Path, text: str) -> str | None:
    """Infer language using pygments based on filename or content."""
    try:
        return guess_lexer_for_filename(filepath, text).name.lower()
    except ClassNotFound:
        return None


def _infer_code_language_file_extension(filepath: str | pathlib.Path) -> str:
    _, file_extension = os.path.splitext(filepath)
    file_extension = file_extension[1:].lower()
    return CODE_EXTENSION_TO_LANGUAGE.get(file_extension, file_extension)


def _render_caption(caption, filepath: pathlib.Path, start=0, end=0):
    if end is None:  # open end inclusion
        end_line_str = "-"
    elif end > start:  # range inclusion
        end_line_str = f"-{end}"
    else:
        end_line_str = ""

    return (CAPTION_TEMPLATE if caption is True else caption) % dict(
        filepath=filepath,
        filename=filepath.name,
        line=(
            f", line{'s' if (end is None or end>start) else ''} {start}{end_line_str}"
            if start
            else ""
        ),
    )


def show_and_tell(
    command, lang="py", output_lang="txt", render_result=False, alt_code_fences=True
):  # pragma: no cover
    original_command = command
    if alt_code_fences:
        command = f"""{command[:-1]}, alt_code_fences={alt_code_fences})"""
    result = eval(
        command,
        dict(
            includex=includex,
        ),
    )
    rv = (
        f"```{{ .{lang} .show_and_tell_command }}\n{original_command}\n```\n"
        f'\n```{{ .{output_lang} .show_and_tell_result title="Result" }}\n{result}\n```'
    )
    if render_result:
        # if the result shall be rendered, we need proper code fences
        if alt_code_fences:
            result = eval(original_command, dict(includex=includex))
        rv += f"\n\n---\n\n{result}\n\n---\n"
    return rv


class NoMatchError(Exception):
    pass
