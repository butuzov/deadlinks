"""
deadlinks
~~~~~~~~~
deadlinks checker for your static website. It's better keep house clean, right?
"""

from typing import (Dict, Tuple, Optional, List) #pylint: disable-msg=W0611

from pathlib import Path
from re import match
import os
from setuptools import find_packages, setup
from setuptools.command.build_py import build_py as _build_py

from utils.setup import (read_data, require, readme)
try:
    from utils.brew import build_formula
except BaseException:
    build_formula = lambda a, b: "Brew Build not implemented"

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


class BrewFormulaBuilder(_build_py):
    """ Run external formula builder """

    def run(self) -> None:
        data = read_data()
        requirements = require("install") + require("brew")

        with open("{}.rb".format(data['app_package']), 'w') as f:
            print(build_formula(app=data, requirements=requirements), file=f)


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
        packages=find_packages(exclude=["utils*", "unittests*"]),
        install_requires=require("install"),
        entry_points='''
            [console_scripts]
            deadlinks=deadlinks.__main__:main
        ''',
        zip_safe=False,
        cmdclass={'brew_formula_create': BrewFormulaBuilder},
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
