"""
deadlinks
~~~~~~~~~
deadlinks checker for your static website. It's better keep house clean, right?
"""

from typing import (Tuple, Dict, List)

from pathlib import Path
from re import compile as _compile
from collections import defaultdict
import sys

from setuptools import find_packages, setup


def read_version() -> str:
    """Reads version of the package"""

    init = Path(__file__).parent / "deadlinks" / "__init__.py"

    if not Path(init).is_file():
        raise RuntimeError("Cannot source for Version - deadlinks/__init__.py")

    version = _compile(r'^__version__\W*=\W*"([\d.abrc]+)"')
    with open(str(init)) as fh:
        for line in fh:
            match = version.match(line)
            if match is not None:
                return match.group(1)

    raise RuntimeError("Cannot find version in deadlinks/__init__.py")


def read_descriptions() -> Tuple[str, str]:
    """Reads the descriptions from README.rst"""

    readme_rst = Path(__file__).parent / "README.rst"
    if not Path(readme_rst).is_file():
        raise RuntimeError("Cannot source for Descriptions - README.rst")

    # raw prefiltered chapters
    raw = dict() # type: Dict[str, List[str]]

    with open(str(readme_rst), "rb") as fh:
        prev_title, title, lines = "", "", fh.read().decode("utf-8").split("\n")

        for i, line in enumerate(lines):
            if not line:
                continue

            if line[0] in ("-", "=") and len(line) == len(lines[i - 1]):
                title = lines[i - 1]
                continue

            if not line[0] or not title or prev_title == title:
                continue

            c = raw.get(title, [])
            if not c:
                prev = raw.get(prev_title, [])
                raw.update({prev_title: prev[:len(prev)]})

            c.append(line)
            raw.update({title: c})
            prev_title = title

    del raw[""]

    chapters = {k: "\n".join(v) for k, v in raw.items()} # type: Dict[str, str]

    try:
        return chapters["deadlinks"], chapters["Description"]
    except KeyError:
        raise RuntimeError("Cannot find Descriptions in README.rst")


def require(section: str = "install") -> List[str]:
    """requirements txt parser"""

    require_txt = Path(__file__).parent / "requirements.txt"
    if not Path(require_txt).is_file():
        return []

    requires = defaultdict(list) # type: Dict[str, List[str]]

    with open(str(require_txt), "rb") as fh:
        key = "" # type: str
        for line in fh.read().decode("utf-8").split("\n"):

            if not line.strip():
                " empty line "
                continue

            if line[0] == "#":
                " section key "
                key = line[2:]
                continue

            # actual package
            requires[key].append(line.strip())

    return requires[section]


# ------------------------------------------------------------------------------

# Author
AUTHOR = "Butuzov Oleg"
AUTHOR_EMAIL = "butuzov@made.ua"
URL = "https://github.com/butuzov/deadlinks"

# General Information
NAME = "deadlinks"
DESCRIPTION, LONG_DESCRIPTION = read_descriptions()
VERSION = read_version()

# Classifiers
CLASSIFIERS = ["Natural Language :: English"]
CLASSIFIERS.append("Development Status :: 2 - Pre-Alpha")

# Classifiers - Audience and Topic
CLASSIFIERS.append("Intended Audience :: Developers")
CLASSIFIERS.append("Intended Audience :: System Administrators")

# Topic
CLASSIFIERS.append("Topic :: Utilities")

# Environment
CLASSIFIERS.append("Environment :: Console")

# Classifiers - Python
CLASSIFIERS.append("Programming Language :: Python :: 3 :: Only")
CLASSIFIERS.append("Programming Language :: Python :: 3.5")
CLASSIFIERS.append("Programming Language :: Python :: 3.6")
CLASSIFIERS.append("Programming Language :: Python :: 3.7")
# Required Packages

# Licence
LICENSE = "Apache License 2.0"
CLASSIFIERS.append("License :: OSI Approved :: {} License".format(LICENSE))

# PPlatforms
PLATFORMS = ["MacOS", "Unix"]
for OS in PLATFORMS:
    CLASSIFIERS.append("Operating System :: {}".format(OS))

# --
TESTS = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
TESTS_RUNNER = ['pytest-runner'] if TESTS else []

# Setup
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    keywords=["documentation", "website", "spider", "crawler", "link-checker"],
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=find_packages(exclude=["tests*"]),
    install_requires=require("install"),
    tests_require=require("tests"),
    setup_requires=(require("install") + TESTS_RUNNER),
    test_suite="pytest",
    extras_require={
        'test': require("tests"),
        'all': require("install") + require("tests") + require("linters"),
        'lint': require("linters"),
    },
    entry_points='''
        [console_scripts]
        deadlinks=deadlinks.main:cli
    ''',
    zip_safe=False,
    python_requires='>=3.5',
    url=URL,
    license=LICENSE,
    platforms=PLATFORMS,
    classifiers=CLASSIFIERS,
)
