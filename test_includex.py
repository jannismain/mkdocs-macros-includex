#!/usr/bin/env python3
import os
import pathlib
import tempfile

import pytest

from includex import (
    CAPTION_TEMPLATE,
    ERROR_NOTICE_TEMPLATE,
    ESCAPE_NOTICE_TEMPLATE,
    REPLACE_NOTICE_TEMPLATE,
    _render_caption,
    includex,
)

content = """# Header

This file explains something very interesting.

## Getting Started

This is how you would get started:

```py
print("Hello, World!")
```

!!! example "Example"
    Indented Example Content

## References

* [Python](python.org)

## List

- first level
  - second level
    - third level
      - fourth level
        - fifth level

          some content
          on the fifth level

Second last line
Last line
"""


def print_debug(expected, returned):
    print(f"\nEXPECTED: {expected!r}")
    print(f"RETURNED: {returned!r}")


@pytest.fixture(autouse=True)
def add_filepath_to_doctest(doctest_namespace, testfile):
    print("preparing doctests...")
    doctest_namespace["filepath"] = testfile


@pytest.fixture()
def testfile():
    fp = tempfile.NamedTemporaryFile("w", delete=False)
    fp.write(content)
    fp.close()
    yield fp.name
    os.unlink(fp.name)


def test_include_full_file(testfile):
    """Include all content from file."""
    expected = content
    returned = includex(testfile)
    print_debug(expected, returned)
    assert returned == returned


def test_include_first_lines(testfile):
    """Include first lines from file."""
    expected = "\n".join(content.split("\n")[:5])
    returned = includex(testfile, lines=5)
    print_debug(expected, returned)
    assert returned == returned


@pytest.mark.parametrize(("start", "end"), [(2, 5)])
def test_include_block_by_line_number(testfile, start, end):
    """Include block from file by line number."""
    expected = "".join(
        pathlib.Path(testfile).open().readlines()[start - 1 : end]
    ).rstrip()  # account for 1-based indexing into files
    returned = includex(testfile, start=start, end=end)
    print_debug(expected, returned)
    assert returned == expected


def test_include_block_by_matching_start_and_end(testfile):
    """Include block from file by matching start and end lines."""
    expected = "\n".join(content.split("\n")[8:11]).rstrip()
    returned = includex(testfile, start_match="```py", end_match="```", include_end_match=True)
    print_debug(expected, returned)
    assert returned == expected


def test_include_block_by_number_of_lines(testfile):
    """Include block from file by matching start line and fixed number of lines."""
    expected = "\n".join(content.split("\n")[8:11]).rstrip()
    returned = includex(testfile, start_match="```py", lines=3)
    print_debug(expected, returned)
    assert returned == expected


def test_wrap_in_raw_tags(testfile):
    """Include content wrapped in jinja raw blocks."""
    expected = "{% raw %}\n" + includex(testfile) + "\n{% endraw %}"
    returned = includex(testfile, raw=True)
    print_debug(expected, returned)
    assert returned == expected

    args = {"keep_trailing_whitespace": True}
    expected = "{% raw %}\n" + includex(testfile, **args) + "{% endraw %}"
    returned = includex(testfile, raw=True, **args)
    print_debug(expected, returned)
    assert returned == expected


def test_escape(testfile):
    args = {"escape": ["`"], "keep_trailing_whitespace": True}
    expected = content.replace("`", "\\`")
    expected += ESCAPE_NOTICE_TEMPLATE % ("` ` `")
    returned = includex(testfile, **args)
    print_debug(expected, returned)
    assert returned == expected


def test_escape_no_notice(testfile):
    args = {"escape": ["`"], "keep_trailing_whitespace": True, "escape_notice": False}
    expected = content.replace("`", "\\`")
    returned = includex(testfile, **args)
    print_debug(expected, returned)
    assert returned == expected


@pytest.mark.parametrize("replace_notice", [True, False], ids=["notice", "no_notice"])
@pytest.mark.parametrize("replace", [[("!!!", "???")]])
def test_replace(testfile, replace, replace_notice):
    args = {"replace": replace, "replace_notice": replace_notice}
    expected = content
    for orig, repl in replace:
        expected = expected.replace(orig, repl)
    if replace_notice:
        expected += REPLACE_NOTICE_TEMPLATE % ", ".join(
            f"{orig} --> {repl}" for orig, repl in replace
        )
    else:
        expected = expected.rstrip()
    returned = includex(testfile, **args)
    print_debug(expected, returned)
    assert returned == expected


def test_first_character_missing_issue(testfile):
    args = {"start_match": "# ", "start_offset": 1, "keep_trailing_whitespace": True}
    expected = "\n".join(content.split("\n")[1:])
    returned = includex(testfile, **args)
    print_debug(expected, returned)
    assert returned == expected


@pytest.mark.parametrize("dedent", [True, False, 4, "foo"])
def test_dedent(testfile, dedent):
    args = dict(start_match="- second level", lines=1, dedent=dedent)
    if dedent is True:
        expected = "- second level"
    elif dedent is False:
        expected = "  - second level"
    elif isinstance(dedent, int):
        expected = "second level"
    else:
        args["raise_errors"] = True
        with pytest.raises(AssertionError):
            includex(testfile, **args)
        return

    returned = includex(testfile, **args)
    print_debug(expected, returned)
    assert returned == expected


def test_automatic_dedent(testfile):
    args = dict(start_match="- third level", end_match="- fifth level")
    expected = """- third level\n  - fourth level"""
    returned = includex(testfile, **args)
    print_debug(expected, returned)
    assert returned == expected


def test_automatic_dedent_code_block(testfile):
    args = dict(start_match="- third level", end_match="- fifth level", lang="yaml")
    expected = """```yaml\n- third level\n  - fourth level\n```"""
    returned = includex(testfile, **args)
    print_debug(expected, returned)
    assert returned == expected


def test_render_caption():
    args = dict(filepath=pathlib.Path("foo/bar.txt"))
    assert _render_caption("%(filepath)s", **args) == "foo/bar.txt"
    assert _render_caption("%(filename)s", **args) == "bar.txt"
    assert _render_caption("%(filepath)s%(line)s", **args, start=1, end=1) == "foo/bar.txt, line 1"
    assert (
        _render_caption("%(filepath)s%(line)s", **args, start=1, end=3) == "foo/bar.txt, lines 1-3"
    )


@pytest.mark.parametrize(
    "caption", [False, True, "Included from testfile", "Excerpt from $(filename)s"]
)
def test_caption(testfile, caption):
    args = dict(start_match="print", lines=1, lang="py", caption=caption)

    expected = """```py\nprint("Hello, World!")\n```"""
    if caption:
        expected_caption = CAPTION_TEMPLATE if caption is True else caption
        expected_caption = _render_caption(
            expected_caption,
            filepath=pathlib.Path(testfile),
            start=10,
            end=11,
        )
        expected = expected + "\n" + expected_caption

    returned = includex(testfile, **args)

    print_debug(expected, returned)
    assert returned == expected


@pytest.mark.parametrize("alt_code_fences", [False, True, "..."])
def test_alt_code_fences(testfile, alt_code_fences):
    args = dict(start_match="print", lines=1, lang="py", alt_code_fences=alt_code_fences)

    expected = 'print("Hello, World!")'
    if alt_code_fences is True:
        code_fence_marker = "'''"
    elif alt_code_fences is False:
        code_fence_marker = "```"
    else:
        code_fence_marker = alt_code_fences
    expected = "\n".join([f"{code_fence_marker}py", expected, code_fence_marker])

    returned = includex(testfile, **args)

    print_debug(expected, returned)
    assert returned == expected


@pytest.mark.parametrize("indent_first", [True, False])
def test_indent_raw(testfile, indent_first):
    args = dict(indent=4, raw=True, indent_first=indent_first)
    expected = ((args["indent"] * " ") if indent_first else "") + "{% raw %}\n"
    expected += "\n".join([args["indent"] * " " + line for line in content.split("\n")[:-1]])
    expected += "\n" + (args["indent"] * " ") + "{% endraw %}"
    returned = includex(testfile, **args)
    print_debug(expected, returned)
    assert returned == expected


def test_raw_lang(testfile):
    args = dict(raw=True, lang="foo")
    expected = "{% raw %}\n"
    expected += f"```{args['lang']}\n"
    expected += content.rstrip()
    expected += "\n" + "```"
    expected += "\n" + "{% endraw %}"
    returned = includex(testfile, **args)
    print_debug(expected, returned)
    assert returned == expected


@pytest.mark.parametrize("args", [dict(dedent="foo")])
def test_exception_to_error_message(testfile, args):
    args = dict(start=0, end=1, raise_errors=False, **args)
    expected = ERROR_NOTICE_TEMPLATE % "AssertionError"
    returned = includex(testfile, **args)
    print_debug(expected, returned)
    assert returned == expected


if __name__ == "__main__":
    import sys

    pytest.main(["-vv", "--capture=tee-sys", *sys.argv[1:]])
