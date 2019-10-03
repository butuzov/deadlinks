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


def read_data() -> Dict[str, str]:
    init = Path(__file__).parent / "deadlinks" / "__init__.py"

    if not Path(init).is_file():
        raise RuntimeError("Can not find source for deadlinks/__init__.py")

    DUNDER_REGEXP = _compile(r'(__(.*?)__ = "(.*?)")\n')

    values = dict() # type: Dict[str, str]

    with open(str(init)) as fh:
        content = "".join(fh.readlines())
        for match in DUNDER_REGEXP.findall(content):
            values[match[1]] = match[2]

    return values


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
data = read_data()

# --
TESTS = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
TESTS_RUNNER = ['pytest-runner'] if TESTS else []

# Setup
setup(
    name=data['app_package'],
    version=data['app_version'],
    description=data['description'],
    keywords=["documentation", "website", "spider", "crawler", "link-checker"],
    author=data['author_name'],
    author_email=data['author_mail'],
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
    url=data['app_website'],
    license=data['app_license'],
    platforms=['MacOS', 'Posix', 'Unix'],
    classifiers=[
        # Env
        "Environment :: Console",

        # Status
        "Development Status :: 2 - Pre-Alpha",

        # Audience
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",

        # Topic
        "Topic :: Utilities",
        "Topic :: Documentation",

        # Audience and Topic
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",

        # Python version
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"

        # License
        "License :: OSI Approved :: {} License".format(data['app_license']),

        # Operation System
        "Operating System :: MacOS",
        "Operating System :: Posix",
        "Operating System :: Unix",

        # Language
        "Natural Language :: English",
    ],
)
