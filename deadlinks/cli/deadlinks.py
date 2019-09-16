#!/usr/bin/env python

# import libraries
import sys
import click
import deadlinks

_PYTHON_MIN = sys.version_info[:2] >= (3, 6)

if not _PYTHON_MIN:
    _PYTHON_VER = ".".join(map(str, sys.version_info[:2]))
    raise SystemExit(
        "ERROR: deadlinks requires a minimum of Python3 version 3.6. "
        "Current version: {}".format(_PYTHON_VER)
    )


@click.command()
@click.option("--url", "-u", default=None, help="Website URL")
@click.option(
    "--mirror", "-m", default=None, help="Duplicate check for mirror url"
)
def main(url, mirror):
    deadlinks.main()
    # print("URL", url)
    # print("Name", mirror)
    # pass


if __name__ == "__main__":
    sys.exit(main())
