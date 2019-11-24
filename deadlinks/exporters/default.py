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
deadlinks.exporters.__init__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Export module init file.

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

from typing import (Dict, Tuple, List, Sequence, Any) #pylint: disable-msg=W0611

from threading import Thread
from os import name as os_name
from time import sleep

import click

from .export import Export
from ..crawler import Crawler
from ..clicker import OptionRaw

# -- Implementation ------------------------------------------------------------

BEFORE_BAR = '\r' if os_name == 'nt' else '\r\033[?25l'
AFTER_BAR = '\n' if os_name == 'nt' else '\033[?25h\n'


class Default(Export):

    PROGRESS = "Ready: {0:>3.0%} ({1}/{2});"
    FIN_DONE = "Links Total: {};"
    DETAILED = "Found: {0}; Not Found: {1}; Ignored: {2}; Redirects: {3}"

    params_colors = {
        'succeed': 'green',
        'failed': 'red',
        'ignored': 'yellow',
    }

    def __init__(self, crawler: Crawler, **opts: Dict) -> None:
        self._crawler = crawler
        self._opts = opts

        self._progress_msg = ""
        self._progress_trd = Thread(target=self._progress_handler, daemon=True)
        self._progress_trd.start()

    def is_colored(self) -> bool:
        """ provides check about colored output """
        return not self._opts.get('no_colors', False)

    def info(self) -> str:

        base = self._crawler.settings.base
        baseurl = base if not self._crawler.settings.masked else \
                    base.url().replace(base.domain, 'internal')

        message = "URL=<{}>; External Checks={}; Threads={}; Retry={}".format(
            baseurl,
            "On" if self._crawler.settings.external else "Off",
            self._crawler.settings.threads,
            self._crawler.settings.retry,
        )

        return message

    @staticmethod
    def options() -> Tuple[str, List[OptionRaw]]:

        options = [] # type: List[OptionRaw]

        # Default export
        options.append((
            ('--export', ),
            {
                'default': 'default',
                'hidden': True,
                'multiple': False,
                'type': click.Choice(['default'], case_sensitive=False),
                'help': 'Export type',
            },
        ))

        options.append((
            ('--no-colors', ),
            {
                'default': False,
                'is_flag': True,
                'help': 'Color output of `default` export',
            },
        ))

        options.append((
            ('--no-progress', ),
            {
                'default': False,
                'is_flag': True,
                'help': 'Disable Proogresion output',
            },
        ))

        return ("Exporter (default)", options)

    def _progress_handler(self) -> None:
        """ progress handler desides states regarding crawler """

        # user disables progression reports.
        if self._opts['no_progress']:
            return

        while not (self._crawler.crawled or self._crawler.terminated):
            if self._crawler.crawling:
                click.echo(BEFORE_BAR, nl=False)

                unstyled_text_len = len(click.unstyle(self._progress_msg))
                click.echo(' ' * unstyled_text_len, nl=False)
                click.echo(BEFORE_BAR, nl=False)

                self._progress_msg = self._get_progress()
                click.echo(self._progress_msg, color=self.is_colored(), nl=False)
                sleep(0.1)

    def _get_progress(self) -> str:
        """ get progress report from crawler"""

        # ready / total
        stats = dict() # type: Dict[str, str]
        total = 0 # type: int
        for k, v in self._crawler.stats.items():
            total += v
            stats[str(k)] = str(v)

        total_links = len(self._crawler.index)

        progress = self.PROGRESS.format(total / total_links, total, total_links)

        if self._crawler.crawled:
            progress = self.FIN_DONE.format(total_links)

        detailed = self.DETAILED.format(
            click.style(stats['Status.FOUND'], fg='green'),
            click.style(stats['Status.NOT_FOUND'], fg='red'),
            click.style(stats['Status.IGNORED'], fg='yellow'),
            click.style(stats['Status.REDIRECTION'], fg='blue'),
        )

        return progress + ' ' + detailed

    def _generate(self, key: str) -> str:
        """ generate a report about urls """

        param = 'succeed' if key == 'ok' else key

        links = self._crawler.__getattribute__(param)
        if not links:
            return ""

        param_color = click.style(param, fg=self.params_colors[param])

        return '\n'.join(map(lambda x: "[ {} ] {}".format(param_color, x), links))

    def report(self) -> None:

        # progress wasn't disabled, so we need to cleanup a bit.
        clear_line_width = len(click.unstyle(self._progress_msg))

        if self._crawler.terminated:
            # we adding additional 10 spaces to clear ^C we got on the
            # terminal if ^C pressed.
            clear_line_width += 10

        if not self._opts['no_progress']:
            click.echo(BEFORE_BAR, nl=False)
            click.echo(' ' * clear_line_width, nl=False)
            click.echo(BEFORE_BAR, nl=False)

        info = self.info() # type: str
        stat = self._get_progress() # type: str

        split_line_len = max(len(click.unstyle(info)), len(click.unstyle(stat)))

        if self._crawler.terminated:
            term_msg = "Results can be inconsistent, as execution was terminated."
            pref_len = (split_line_len - len(term_msg)) // 2
            click.echo((" " * split_line_len))
            click.echo((" "*pref_len) + term_msg)
            click.echo((" "*pref_len) + ("^" * len(term_msg)))

        click.echo("=" * split_line_len)
        click.echo(info, color=self.is_colored())
        click.echo("=" * split_line_len)

        click.echo(stat, color=self.is_colored())
        click.echo(("-"*split_line_len) + "\033[?25h")

        # show some url report(s)
        show = list(self._opts.get('show', [])) # type: Sequence[str]

        if 'none' in show:
            return

        if 'all' in show:
            show = ['ok', 'failed', 'ignored']

        for report in show:
            OUTPUT_REPORT = self._generate(report)

            if len(OUTPUT_REPORT):
                click.echo(OUTPUT_REPORT, color=self.is_colored())
