"""
doc.md
~~~~~~
doc.md is a documentation markdown generator for cli tools, easy way to get
markdown page for every single option of your cli tool.
"""

import re

from pathlib import Path
from typing import Tuple, Dict, List
from setuptools import find_packages, setup


def read_version() -> str:
    """Reads version of the package"""

    init = Path(__file__).parent / "deadlinks" / "__init__.py"
    print(init)

    if not Path(init).is_file():
        raise RuntimeError("Cannot source for Version - deadlinks/__init__.py")

    regexp = re.compile(r'^__version__\W*=\W*"([\d.abrc]+)"')

    with open(init) as fh:
        for line in fh:
            print(line)
            match = regexp.match(line)
            if match is not None:
                return match.group(1)

    raise RuntimeError("Cannot find version in deadlinks/__init__.py")


def read_descriptions() -> Tuple[str, str]:
    """Reads the descriptions from README.rst"""

    readme_rst = Path(__file__).parent / "README.rst"
    if not Path(readme_rst).is_file():
        raise RuntimeError("Cannot source for Descriptions - README.rst")

    # raw prefiltered chapters
    raw: Dict[str, List[str]] = dict()

    with open(readme_rst, "rb") as fh:
        prev_title, title, lines = "", "", fh.read().decode("utf-8").split("\n")

        for i in range(0, len(lines)):
            if not lines[i]:
                continue

            if lines[i][0] in ("-", "=") and len(lines[i]) == len(lines[i - 1]):
                title = lines[i - 1]
                continue

            if not lines[i][0] or not title or prev_title == title:
                continue

            c = raw.get(title, [])
            if not c:
                prev = raw.get(prev_title, [])
                raw.update({prev_title: prev[: len(prev)]})

            c.append(lines[i])
            raw.update({title: c})
            prev_title = title

    del raw[""]

    chapters: Dict[str, str] = {k: "\n".join(v) for k, v in raw.items()}

    try:
        return chapters["deadlinks"], chapters["Description"]
    except KeyError:
        raise RuntimeError("Cannot find Descriptions in README.rst")


def requirements() -> List[str]:
    """requirements txt parser"""

    requirements_txt = Path(__file__).parent / "requirements.txt"
    if not Path(requirements_txt).is_file():
        return []

    install_requires: List[str] = []

    with open(requirements_txt, "rb") as fh:
        install_requires = [i.strip() for i in fh.read().decode("utf-8").split("\n")]

    return install_requires


# Classifiers
CLASSIFIERS = ["Natural Language :: English"]

# General Information
NAME = "deadlinks"
DESCRIPTION, LONG_DESCRIPTION = read_descriptions()
VERSION = read_version()
CLASSIFIERS.append("Development Status :: 1 - Planning")

# Author
AUTHOR = "Butuzov Oleg"
AUTHOR_EMAIL = "butuzov@made.ua"
URL = "https://github.com/butuzov/deadlinks"

# Classifiers - Audience and Topic
CLASSIFIERS.append("Intended Audience :: Developers")
CLASSIFIERS.append("Intended Audience :: System Administrators")
CLASSIFIERS.append("Topic :: Utilities")

# Classifiers - Python
CLASSIFIERS.append("Programming Language :: Python")
CLASSIFIERS.append("Programming Language :: Python :: 3.6")
CLASSIFIERS.append("Programming Language :: Python :: 3.7")
# Required Packages

# Licence
LICENSE = "MIT"
CLASSIFIERS.append("License :: OSI Approved :: {} License".format(LICENSE))

# platforms
PLATFORMS = ["MacOS", "Unix"]
for OS in PLATFORMS:
    CLASSIFIERS.append("Operating System :: {}".format(OS))

# Setup
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    keywords="documentation",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=find_packages(exclude=["tests*"]),
    install_requires=requirements(),
    scripts=["bin/deadlinks"],
    zip_safe=False,
    classifiers=CLASSIFIERS,
    url=URL,
    license=LICENSE,
    platforms=PLATFORMS,
)
