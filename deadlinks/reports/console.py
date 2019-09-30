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
from typing import Dict, Sequence, Any

from click import style, unstyle, echo, wrap_text

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

    def info(self) -> str:
        message = "URL=<{}>; External Cheks={}; Threads={}; Retry={}".format(
            self._crawler.settings.base,
            "On" if self._crawler.settings.external else "Off",
            self._crawler.settings.threads,
            self._crawler.settings.retry,
        )

        return message

    def stats(self) -> str:

        stats = []
        stats.append(('Found {}', style(str(len(self._crawler.succeed)), fg='green')))
        stats.append(('Not Found {}', style(str(len(self._crawler.failed)), fg='red')))

        if self._crawler.ignores():
            stats.append(('Ignored {}', style(str(len(self._crawler.ignored)), fg='yellow')))

        places = [v[0] for v in stats]
        values = [v[1] for v in stats]

        return ("Stats: {}".format("; ".join(places))).format(*values)

    def _generate(self, key: str) -> str:
        """ generate a report about urls """
        if key not in {'failed', 'ok', 'ignored'}:
            return ""

        param = 'succeed' if key == 'ok' else key
        links = self._crawler.__getattribute__(param)
        if not links:
            return ""

        param_color = style(param, fg=self.params_colors[param])

        return '\n'.join(map(lambda x: "[ {} ] {}".format(param_color, x), links))

    def report(self) -> None:
        """ generate report and pass it to the echo callback """

        # stats and info
        OUTPUT = "{}\n{}".format(self.info(), self.stats()) # type: str
        if self._opts.get('no_colors', False):
            OUTPUT = unstyle(OUTPUT)
        echo(wrap_text(OUTPUT))

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

            if self._opts.get('no_colors', False):
                OUTPUT_REPORT = unstyle(OUTPUT_REPORT)

            echo(OUTPUT_REPORT)
