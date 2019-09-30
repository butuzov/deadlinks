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
deadlinks.help
~~~~~~~~~~~~~~~~~

better help for --help

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""
from textwrap import dedent

from click import Command
from click import Context as Ctx
from click import HelpFormatter as Formatter


class CLI(Command):
    """ Custom CLI class, for henerating better `help`"""

    EXAMPLES = dedent(
        """\

            // crawl http://localhost:8080/ in 10 threads, check external links,
            // but not lay.golang.org or github.com
            deadlinks http://localhost:8080/ -n 10 -e -d play.golang.org -d github.com

        """)

    def format_help(self, ctx: Ctx, formatter: Formatter) -> None:
        """Writes the help into the formatter if it exists."""

        self.format_help_text(ctx, formatter)
        self.format_usage(ctx, formatter)
        self.format_examples(ctx, formatter)
        self.format_options(ctx, formatter)
        self.format_epilog(ctx, formatter)

    def format_help_text(self, ctx: Ctx, formatter: Formatter) -> None:
        """Writes the help text to the formatter if it exists."""

        formatter.write_paragraph()
        formatter.write_text(self.help)

    def format_examples(self, ctx: Ctx, formatter: Formatter) -> None: # pylint: disable-msg=R0201
        """ Writes the examples into the formatter. """

        formatter.write_paragraph()
        with formatter.section('Examples'):
            formatter.write_text(self.EXAMPLES)

    def format_usage(self, ctx: Ctx, formatter: Formatter) -> None:
        """ Writes the usage line into the formatter. """
        pieces = self.collect_usage_pieces(ctx)
        pieces = pieces[::-1]

        formatter.write_paragraph()
        with formatter.section('Usage'):
            formatter.write_text("{} {}".format(
                ctx.command_path,
                ' '.join(pieces).rstrip('\n'),
            ))
