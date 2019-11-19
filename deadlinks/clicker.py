# Copyright 2019 Oleg Butuzov. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
deadlinks.clicker
~~~~~~~~~~~~~~~~~

Functions related to click package and cli implementation.

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------
from typing import (Dict, List, Tuple, Any, Callable)
from textwrap import dedent
from collections import OrderedDict

from click import Option, Argument
from click import Command
from click import Context
from click import HelpFormatter as Formatter

from .link import Link


def register_exports(exporters: Dict[str, Any]) -> Callable:

    def decorator(f: Any) -> Any:

        if not hasattr(f, '__click_params_groups__'):
            f.__click_params_groups__ = OrderedDict()

        if not hasattr(f, '__click_params__'):
            f.__click_params__ = []

        for exporter in exporters.values():
            group, options = exporter.options()

            for option in reversed(options):
                param, attr = option
                option_attr = attr.copy()
                OptionClass = option_attr.pop('cls', Option)

                _option = OptionClass(param, **attr)
                f.__click_params__.append(_option)

                if group not in f.__click_params_groups__:
                    f.__click_params_groups__[group] = []

                f.__click_params_groups__[group].append(_option.name)

        return f

    return decorator


def register_options(group: str, options: List[Tuple[Any, Dict[str, Any]]]) -> Callable:
    """ Register Multiple Options in one set  """

    def decorator(f: Any) -> Any:
        """ Final decoration for main """

        if not hasattr(f, '__click_params_groups__'):
            f.__click_params_groups__ = OrderedDict()

        if not hasattr(f, '__click_params__'):
            f.__click_params__ = []

        # Issue 926, just in case we also need to worry about custom cls.
        for option in reversed(options):
            param, attr = option
            option_attr = attr.copy()
            OptionClass = option_attr.pop('cls', Option)

            _option = OptionClass(param, **attr)
            f.__click_params__.append(_option)

            # groups

            if group not in f.__click_params_groups__:
                f.__click_params_groups__[group] = []

            f.__click_params_groups__[group].append(_option.name)

        return f

    return decorator


class Clicker(Command):
    """ Custom CLI class, for henerating better `help`"""

    EXAMPLES = dedent(
        """\
            // Check links (including external) at http://gobyexample.com/ in 10 threads,
            // but not ones that leading to domains play.golang.org or github.com
            deadlinks gobyexample.com -n 10 -e -d play.golang.org -d github.com

            // Limiting check only to links found within /docs path.
            deadlinks http://localhost:1313/docs

            // Running checks for all local links that belong to a domain.
            deadlinks http://localhost:1313/docs/ -n 10 --full-site-check
        """)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """ Getting Options groups """

        # print(type(args))
        # print(type(kwargs))

        self._groups = kwargs['callback'].__click_params_groups__
        self._groups['Other'] = []

        super().__init__(*args, **kwargs)

    def format_help(self, ctx: Context, formatter: Formatter) -> None:
        """Writes the help into the formatter if it exists."""

        # shuld print
        # checking links from web resource for dead/alive status.
        self.format_help_text(ctx, formatter)
        self.format_examples(ctx, formatter)
        self.format_options(ctx, formatter)
        self.format_epilog(ctx, formatter)

    def format_options(self, ctx: Context, formatter: Formatter) -> None:
        """ group options """

        # building reverse look up
        lookup = {}
        for group, items in self._groups.items():
            lookup.update({item: group for item in items})

        groups = {group: [] for group in self._groups} #type: Dict[str, List[Tuple[str, str]]]

        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is None:
                continue

            current_group = lookup.get(param.name, "Other")
            groups[current_group].append(rv)

        for group_name, options in groups.items():
            if not options:
                continue

            with formatter.section(group_name):
                formatter.write_dl(options)

    def format_help_text(self, ctx: Context, formatter: Formatter) -> None:
        """ Writes the help text to the formatter if it exists. """

        formatter.write_paragraph()
        formatter.write_text(self.help)

    def format_examples(
            self, ctx: Context, formatter: Formatter) -> None: # pylint: disable-msg=R0201
        """ Writes the examples into the formatter. """

        with formatter.section('Usage Examples'):
            for line in self.EXAMPLES.split("\n"):
                formatter.write("  {}\n".format(line))


command = dict({
    "cls": Clicker,
    "context_settings": {
        "ignore_unknown_options": False
    },
}) # type: Dict[str, Any]


def validate_url(ctx: Context, param: Argument, value: str) -> str:
    """ if received url with no scheme will try to fix it """

    url = Link(value)
    if not url.is_valid() and not url.scheme:
        return "http://{}".format(url)

    return value


argument = dict({
    'nargs': 1,
    'required': True,
    'callback': validate_url,
    'metavar': '<URL>',
}) # type: Dict[str, Any]
