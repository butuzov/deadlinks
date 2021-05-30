"""
brew.py
~~~~~~~
brew py is brew formula generator for the deadlinks package

"""
from typing import (Dict, Tuple, Optional, List) #pylint: disable-msg=W0611

from collections import defaultdict
from pathlib import Path
from textwrap import dedent
from re import compile as _compile
import json

import requests
from jinja2 import Template

try:
    from packaging.version import parse
except ImportError:
    from pip._vendor.packaging.version import parse

# -- Code ----------------------------------------------------------------------

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


template = Template(
    dedent(
        """\
        class {{class}} < Formula
          include Language::Python::Virtualenv

          desc "{{description}}"
          homepage "{{homepage}}"
          url "{{url}}"
          sha256 "{{digest}}"

          depends_on "python"
        {% for package in packages %}
          resource "{{ package[0] }}" do
            url "{{ package[2] }}"
            sha256 "{{ package[1] }}"
          end
        {% endfor %}
          def install
            virtualenv_install_with_resources
          end

          test do
            # version assertion
            assert_match /#{version}/, shell_output("#{bin}/deadlinks --version")

            # deaddomain expected result
            (testpath/"localhost.localdomain.log").write <<~EOS
              ===========================================================================
              URL=<http://localhost.localdomain>; External Checks=Off; Threads=1; Retry=0
              ===========================================================================
              Links Total: 1; Found: 0; Not Found: 1; Ignored: 0; Redirects: 0
              ---------------------------------------------------------------------------\e[?25h
              [ failed ] http://localhost.localdomain
            EOS

            # deaddomain assertion
            output = shell_output("deadlinks localhost.localdomain --no-progress --no-colors")
            assert_equal (testpath/"localhost.localdomain.log").read, output
          end
        end"""))


def build_formula(app, requirements, build_dev=False) -> str:

    data = {
        'class': app['app_package'][0].upper() + app['app_package'][1:],
        'description': app['description'][:-1],
        'homepage': app['app_website'],
        'packages': [],
    }

    if build_dev:
        data['url'], data['digest'] = get_local_pacage()
    else:
        data['url'], data['digest'] = info(app['app_package'], "", "")

    for _package in requirements:
        pkg, cmp, version = clean_version(_package)
        url, digest = info(pkg, cmp, version)
        data['packages'].append((pkg, digest, url))

    return template.render(**data)


def get_local_pacage():
    import hashlib, glob

    sha256 = hashlib.sha256()

    files = glob.glob("dist/deadlinks-*.tar.gz")
    with open(files[0], "rb") as f:
        data = f.read()
    return "http://localhost:8878/%s" % files[0], hashlib.sha256(data).hexdigest()


def clean_version(package) -> Tuple[str, str, str]:
    """ Splits the module from requirments to the tuple: (pkg, cmp_op, ver) """

    separators = ["==", ">=", "<=", "!="]
    for s in separators:
        if s in package:
            return package.partition(s)

    return (package, "", "")


def info(pkg, cmp: Optional[str], version: Optional[str]) -> Tuple[str, str]:
    """ Return version of package on pypi.python.org using json. """

    package_info = 'https://pypi.python.org/pypi/{}/json'.format(pkg)
    req = requests.get(package_info)

    if req.status_code != requests.codes.ok:
        raise RuntimeError("Can't request PiPy")

    j = json.loads(req.text)
    releases = j.get('releases', {})
    versions = releases.keys()
    version = release(versions, cmp, version)

    source = lambda x: x.get("python_version") == "source"
    version = list(filter(source, releases[str(version)]))[0]

    return version['url'], version["digests"]['sha256']


def release(releases, pkg_cmp, pkg_ver):
    """ filter available release to pick one included in formula """

    not_prerelease = lambda x: not x.is_prerelease

    cmps = {
        '!=': lambda x: x != parse(pkg_ver),
        '==': lambda x: x == parse(pkg_ver),
        '>=': lambda x: x >= parse(pkg_ver),
        '<=': lambda x: x <= parse(pkg_ver),
    }

    _versions = list(releases)
    _versions = map(parse, releases)
    _versions = filter(not_prerelease, _versions)

    if pkg_cmp and pkg_ver:
        _versions = filter(cmps[pkg_cmp], _versions)

    versions = sorted(_versions, reverse=True)
    if not versions:
        raise RuntimeError("No matching version found")

    return versions[0]


if __name__ == "__main__":

    import sys

    data = read_data()
    options = {
        'app': data,
        'requirements': require("install") + require("brew"),
    }

    options['requirements'] = list(
        filter(lambda x: "python_full_version" not in x, options['requirements']))

    if '--dev' in sys.argv[1:]:
        options['build_dev'] = True

    with open("{}.rb".format(data['app_package']), 'w') as f:
        print(build_formula(**options), file=f)
