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
deadlinks.report.console
~~~~~~~~~~~~~~~~~~~~~~~~~

Formats some text

TODO
- [ ] info - add output of ignored domains and pathes


:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""
from typing import Dict, Sequence

import click

from deadlinks.crawler import Crawler


class Console:

    params_colors = {
        'succeed': 'green',
        'failed': 'red',
        'ignored': 'yellow',
    }

    def __init__(self, crawler: Crawler, **opts: Dict) -> None:
        self._crawler = crawler
        self._opts = opts

    def is_colored(self) -> bool:
        return not self._opts.get('no_colors', False)

    def info(self) -> str:
        message = "URL=<{}>; External Cheks={}; Threads={}; Retry={}".format(
            self._crawler.settings.base,
            "On" if self._crawler.settings.external else "Off",
            self._crawler.settings.threads,
            self._crawler.settings.retry,
        )

        return message

    def stats(self) -> str:

        message = "Stats: Found {0}; Not Found {1}; Ignored {2}"
        found = click.style(str(len(self._crawler.succeed)), fg='green')
        not_found = click.style(str(len(self._crawler.failed)), fg='red')
        ignored = click.style(str(len(self._crawler.ignored)), fg='yellow')

        return message.format(found, not_found, ignored)

    def _generate(self, key: str) -> str:
        """ generate a report about urls """
        if key not in {'failed', 'ok', 'ignored'}:
            return ""

        param = 'succeed' if key == 'ok' else key
        links = self._crawler.__getattribute__(param)
        if not links:
            return ""

        param_color = click.style(param, fg=self.params_colors[param])

        return '\n'.join(map(lambda x: "[ {} ] {}".format(param_color, x), links))

    def report(self) -> None:
        """ generate report and pass it to the echo callback """

        info = self.info() # type: str
        stat = self.stats() # type: str

        click.echo(info, color=self.is_colored())
        click.echo("=" * len(click.unstyle(info)))
        click.echo(stat, color=self.is_colored())
        click.echo("-" * len(click.unstyle(stat)))

        # show some url report(s)
        show = list(self._opts.get('show', [])) # type: Sequence[str]

        if 'none' in show:
            return

        if 'all' in show:
            show = [
                'ok',
                'failed',
                'ignored',
            ]

        for report in show:
            OUTPUT_REPORT = self._generate(report)

            if len(OUTPUT_REPORT):
                click.echo(OUTPUT_REPORT, color=self.is_colored())
