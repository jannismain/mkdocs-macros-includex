"""Documentation macros.

See the [`mkdocs-macros-plugin` Documentation](https://mkdocs-macros-plugin.readthedocs.io/) for more information.
"""

import logging
import os
import pathlib

from mkdocs_macros.plugin import MacrosPlugin

root = pathlib.Path(__file__).parent.parent.parent

log = logging.getLogger("mkdocs.mkdocs_macros")


def define_env(env: MacrosPlugin):
    """Define variables, macros and filters for mkdocs-macros."""
    env.macro(get_files)


def get_files(directory: str | pathlib.Path, match: str = "", ignore: str = "") -> list[str]:
    """Return list of files in *directory* that match the provided substring.

    Args:
        directory: path to directory
        match: only files that contain this string will be included
        ignore: files containing this string won't be included

    Returns:
        List of files in *directory*
    """
    rv = []
    directory = pathlib.Path(directory)
    assert directory.is_dir()
    for file in sorted(os.listdir(directory)):
        if match and match not in file:
            continue
        if ignore and ignore in file:
            continue
        rv.append(directory / file)
    return rv
