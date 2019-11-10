"""
deadlinks
~~~~~~~~~
deadlinks checker for your static website. It's better keep house clean, right?
"""

from typing import (Dict, List) #pylint: disable-msg=W0611

from pathlib import Path
from re import compile as _compile
from collections import defaultdict
import sys, os
from setuptools import find_packages, setup


def read_data() -> Dict[str, str]:
    init = Path(__file__).parent / "deadlinks" / "__version__.py"

    if not Path(init).is_file():
        raise RuntimeError("Can not find source for deadlinks/__version__.py")

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


def readme() -> str:
    """ different version of readme changed for pypi """
    readme = Path(__file__).parent / "README.md"

    contents = ""

    if not Path(readme).is_file():
        return contents

    with open("README.md", encoding="utf8") as f:
        contents = f.read()

    # cutout first header

    contents = contents.replace("# deadlinks", "", 1).lstrip()

    return contents


# ------------------------------------------------------------------------------

# ~~ Version Releases ~~
# next code responsible for creating dev release version number.
# - pypi.org: as we not allowed to have version as X.Y.Z.dev+developer+COMMIT
#        to be published on test.pypi.org versions for pipy.org can be
#        overiden only with VERSION=<number> during `make deploy-test` or
#        `make deploy-prod`
#
#        Example
#        ( e.g VERSION=1 PYPI_TEST_USER=BUTUZOV make deploy-test)
#
# - docker hub: dev - auto builds
#       developermnt branch is going to be builded automatically on push
#       image name             butuzov/deadlinks:dev
#       package (for example)  v0.0.2.dev+docker+1a886c6
#
# - docker hub: production (autobuilds)
#       image name             butuzov/deadlinks:0.0.2
#       package (for example)  v0.0.2
#
branch = os.environ.get('DEADLINKS_BRANCH', None)
commit = os.environ.get('DEADLINKS_COMMIT', None)
version = os.environ.get('DEADLINKS_VERSION', None)

data = read_data()

if branch and branch != "master" and not version:
    dev_version_file = Path(__file__).parent / "deadlinks" / "__develop__.py"
    dev_version_str = ".{}.{}".format(branch, commit).rstrip("+")
    with open(str(dev_version_file), "w") as f:
        print("version = '{}'".format(dev_version_str), file=f)
    data['app_version'] += dev_version_str

if version:
    data['app_version'] += ".{}".format(version)

# -- Version Releases / End ~~

# - Local testing
TESTS = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
TESTS_RUNNER = ['pytest-runner'] if TESTS else []

# - Setup
setup(
    name=data['app_package'],
    version=data['app_version'],
    description=data['description'],
    long_description=readme(),
    long_description_content_type="text/markdown",
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
        deadlinks=deadlinks.__main__:main
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
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        # License
        "License :: OSI Approved :: Apache Software License",

        # Operation System
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: Unix",

        # Language
        "Natural Language :: English",
    ],
)
