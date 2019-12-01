"""
deadlinks
~~~~~~~~~
deadlinks checker for your static website. It's better keep house clean, right?
"""

from typing import (Dict, Tuple, Optional, List) #pylint: disable-msg=W0611

from collections import defaultdict
from pathlib import Path
from re import match
from re import compile as _compile

import os

from setuptools import find_packages, setup

# -- Common Functions ----------------------------------------------------------

DUNDER_REGEXP = _compile(r'(__(.*?)__ = "(.*?)")\n')


def read_data() -> Dict[str, str]:
    """ Read data from __versions__ py """

    init = Path(".").parent / "deadlinks" / "__version__.py"

    if not Path(init).is_file():
        raise RuntimeError("Can not find source for deadlinks/__version__.py")

    values = dict() # type: Dict[str, str]
    with open(str(init)) as fh:
        content = "".join(fh.readlines())
        for match in DUNDER_REGEXP.findall(content):
            values[match[1]] = match[2]

    return values


def require(section: str = "install") -> List[str]:
    """ Requirements txt parser. """

    require_txt = Path(".").parent / "requirements.txt"
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
    readme = Path(".").parent / "README.md"

    if not Path(readme).is_file():
        return ""

    contents = " "
    with open("README.md", encoding="utf8") as f:
        contents = f.read()

    # cutout first header
    return contents.replace("# deadlinks", "", 1).lstrip()


# ------------------------------------------------------------------------------

# ~~ Version Releases / Start ~~

# PyPi: only releases (x.y.z)
#
#
data = read_data()

branch = os.environ.get('DEADLINKS_BRANCH', None)
commit = os.environ.get('DEADLINKS_COMMIT', None)
tagged = os.environ.get('DEADLINKS_TAGGED', None)

VERSION = r'^\d{1,}.\d{1,}.\d{1,}$' # type: str

if tagged and not match(VERSION, tagged) and branch and commit:
    dev_version_file = Path(__file__).parent / "deadlinks" / "__develop__.py"
    dev_version_str = ".{}.{}".format(branch, commit).rstrip("+")
    with open(str(dev_version_file), "w") as f:
        print("version = '{}'".format(dev_version_str), file=f)
    data['app_version'] += dev_version_str

# -- Version Releases / End ~~

# -- Setup ---------------------------------------------------------------------

if __name__ == "__main__":
    setup(
        name=data['app_package'],
        version=data['app_version'],
        description=data['description'],
        long_description=readme(),
        long_description_content_type="text/markdown",
        keywords=["documentation", "website", "spider", "crawler", "link-checker"],
        author=data['author_name'],
        author_email=data['author_mail'],
        project_urls={
            "GitHub: repo": "https://github.com/butuzov/deadlinks",
            "Bugtracker": "https://github.com/butuzov/deadlinks/issues",
            "Documentation": "http://deadlinks.readthedocs.io/",
            "Documentation (latest)": "https://deadlinks.readthedocs.io/en/latest/",
            "Dockerized": "https://hub.docker.com/repository/docker/butuzov/deadlinks/",
        },
        packages=find_packages(exclude=["unittests*"]),
        install_requires=require("install"),
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
