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

from typing import (Dict, List, Tuple, Union, Any, Callable, Sequence)
from textwrap import dedent
from collections import OrderedDict

from click import Option, Argument
from click import Command, Context
from click import HelpFormatter as Formatter

from .link import Link
from .__version__ import __app_package__ as app

# -- Typing Decorators -----~---------------------------------------------------
OptionsValues = Union[str, bool, int, List[str], List[Callable]]
Options = Dict[str, OptionsValues]
OptionModifier = Callable
OptionRaw = Tuple[Sequence[str], Dict[str, Any]]
OptionsList = List[OptionRaw]
HelpDefList = List[Tuple[str, str]]

# -- Options Decorators --------------------------------------------------------
#   Its better to make own wrappet than add number of options directly to
#   main function each time.


class OrderedDefaultDict(OrderedDict):
    factory = list

    def __missing__(self, key: str) -> List:
        self[key] = value = self.factory() # type: ignore
        return value


default_attributes = {
    '__click_params_groups__': OrderedDefaultDict,
    '__click_params__': list,
    '__click_params_modify__': OrderedDefaultDict,
}


def modify(f: Any, group: str, options: OptionsList) -> Any:

    for attr, factory in default_attributes.items():
        if not hasattr(f, attr):
            f.__dict__[attr] = factory()

    for option in reversed(options):
        # exported value is variable that we getting in the function.
        # params is a list of options
        # key=>value
        params, attrs = option

        OptionClass = attrs.pop('cls', Option)
        Modifiers = attrs.pop('modifier', [])

        _option = OptionClass(params, **attrs)

        # adding option and group
        f.__click_params__.append(_option)
        f.__click_params_groups__[group].append(_option.name)
        if Modifiers:
            f.__click_params_modify__[_option.name] += Modifiers

    return f


def register_exports(exporters: Dict[str, Any]) -> Callable:

    def decorator(f: Any) -> Any:

        for exporter in exporters.values():
            group, options = exporter.options()
            f = modify(f, group, options)

        return f

    return decorator


def register_options(group: str, options: OptionsList) -> Callable:
    """ Register Multiple Options in one set  """

    def decorator(f: Any) -> Any:
        """ Final decoration for main """

        return modify(f, group, options)

    return decorator


# -- CLI wrapper ---------------------------------------------------------------
#   So we can have nice looking options groups.


class Clicker(Command):
    """ For a better --help function """

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

        if hasattr(kwargs['callback'], '__click_params_groups__'):
            self._groups = kwargs['callback'].__click_params_groups__
            self._groups['Other'] = []

        if hasattr(kwargs['callback'], '__click_params_modify__'):
            self._modify = kwargs['callback'].__click_params_modify__

        super().__init__(*args, **kwargs)

    def format_help(self, ctx: Context, formatter: Formatter) -> None:
        """ Writes the help into the formatter if it exists. """

        # Checking links from web resource for dead/alive status.
        self.format_help_text(ctx, formatter)
        self.format_examples(ctx, formatter)
        self.format_options(ctx, formatter)
        self.format_epilog(ctx, formatter)

    def make_context(self, info_name, args, parent=None, **extra) -> Context: # type: ignore
        """ Hooking into context in oder to make pro_name for unnamed call. """

        extra['help_option_names'] = ['--help', '-h']

        return super().make_context(app, args, parent, **extra)

    def format_options(self, ctx: Context, formatter: Formatter) -> None:
        """ Group options together. """

        if not hasattr(self, '_groups'):
            return super().format_options(ctx, formatter)

        # building reverse look up
        lookup = {}
        for group, items in self._groups.items():
            lookup.update({item: group for item in items})

        groups = {group: [] for group in self._groups} #type: Dict[str, HelpDefList]

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
            formatter.write("\n")
            for line in self.EXAMPLES.split("\n"):
                formatter.write("  {}\n".format(line))

    def modify(self, ctx: Context) -> None:
        """ Modifing params based on context. """
        if not self._modify:
            return

        for key, modifiers in self._modify.items():
            if ctx.params.get(key, None):
                for modify in modifiers:
                    ctx.params = modify(ctx.params)

    def invoke(self, ctx: Context) -> None:
        """ Hooking into invoke in order to modify params. """
        self.modify(ctx)
        super().invoke(ctx)


# -- CLI wrapper ---------------------------------------------------------------
#   So we can have nice looking options groups.

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
