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


@pytest.fixture()
def testfile():
    fp = tempfile.NamedTemporaryFile("w", delete=False, suffix=".md")
    fp.write(content)
    fp.close()
    yield fp.name
    os.unlink(fp.name)


@pytest.fixture(autouse=True)
def add_filepath_to_doctest(doctest_namespace, testfile):
    print("preparing doctests...")
    doctest_namespace["filepath"] = testfile


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
    args = dict(start_match="- third level", end_match="- fifth level", code="yaml")
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
        _render_caption("%(filepath)s%(line)s", **args, start=1, end=None)
        == "foo/bar.txt, lines 1-"
    )


@pytest.mark.parametrize(
    "caption", [False, True, "Included from testfile", "Excerpt from $(filename)s"]
)
def test_caption(testfile, caption):
    args = dict(start_match="print", lines=1, code="py", caption=caption)

    expected = """```py\nprint("Hello, World!")\n```"""
    if caption:
        expected_caption = CAPTION_TEMPLATE if caption is True else caption
        expected_caption = _render_caption(
            expected_caption,
            filepath=pathlib.Path(testfile),
            start=10,
            end=10,
        )
        expected = expected + "\n" + expected_caption

    returned = includex(testfile, **args)

    print_debug(expected, returned)
    assert returned == expected


# The example content above has 32 lines in total (not including the empty line at the end)


@pytest.mark.parametrize(
    "args, expected",
    [
        (dict(start=3, lines=1), "line 3"),  # include only line 3
        (dict(start=3, end=5), "lines 3-5"),  # include lines 3-5
        (dict(start=3, lines=3), "lines 3-5"),  # include 3 lines starting with line 3
        # negative indices
        (dict(start=-3), "lines 30-"),  # include last 3 lines
        (dict(start=-3, end=-1), "lines 30-31"),  # include last 3 lines, but omit the last one
        # start/end match
        (dict(start_match="print", lines=1), "line 10"),  # include first line that contains `print`
        (
            dict(start_match="```py", end_match="```", include_end_match=True),
            "lines 9-11",
        ),  # include code block
        (dict(start_match="## Ref", end_match="## List"), "lines 16-19"),  # include reference block
        (
            dict(start_match="## Ref", start_offset=1, end_match="## List"),
            "lines 17-19",
        ),  # include reference block without the heading
    ],
)
def test_caption_lines(testfile, args, expected):
    args.update(dict(caption=True, code=True))  # ensure caption is generated
    returned = includex(testfile, **args)
    print(returned)
    returned_caption = returned.rstrip().split("\n")[-1]
    assert expected in returned_caption


@pytest.mark.parametrize("alt_code_fences", [False, True, "..."])
def test_alt_code_fences(testfile, alt_code_fences):
    args = dict(start_match="print", lines=1, code="py", alt_code_fences=alt_code_fences)

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


def test_raw_code(testfile):
    args = dict(raw=True, code="foo")
    expected = "{% raw %}\n"
    expected += f"```{args['code']}\n"
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


def test_readme_example():
    # read example from readme and execute it
    command = includex("README.md", start_match="{{ includex(", lines=1)
    command = command.replace("{{", "").replace("}}", "").strip()
    actual = eval(command).strip()

    # read expected output from readme
    expected = includex("README.md", start_match="```toml", end_match="```", include_end_match=True)

    assert actual.startswith(expected), "caption is different but included content should match"


@pytest.mark.parametrize(
    "filetype,kwargs,expected",
    [
        (".md", dict(code=True), "```md\n"),
        (".md", dict(), content[:30]),
    ],
)
def test_code_option(filetype, kwargs, expected, tmp_path):
    with tempfile.NamedTemporaryFile("w", suffix=filetype, dir=tmp_path) as fp:
        fp.write(content)
        fp.seek(0)
        assert includex(tmp_path / fp.name, **kwargs).startswith(expected)


@pytest.mark.parametrize(
    "kwargs,expected",
    [
        (dict(code=True, lang="py"), "```py\n"),  # lang should overwrite code
    ],
)
def test_code_lang_interaction(testfile, kwargs, expected):
    assert includex(testfile, **kwargs).startswith(expected)


@pytest.mark.parametrize(
    "code,lang",
    [
        (True, "md"),  # code block with default language (defaults to file suffix)
        (False, None),  # no code block
        ("py", "py"),  # code block with given language
        ("", ""),  # code block without language
    ],
)
def test_code_lang_sameness(testfile, code, lang):
    assert includex(testfile, code=code) == includex(testfile, lang=lang)


if __name__ == "__main__":
    import sys

    pytest.main(["-vv", "--capture=tee-sys", *sys.argv[1:]])
