# -- Imports -------------------------------------------------------------------
from threading import Thread

from typing import (Dict, Sequence) #pylint: disable-msg=W0611
from sys import stdout
from time import sleep

import click

from .export import Export
from ..crawler import Crawler

from os import name as os_name

if os_name == 'nt':
    BEFORE_BAR = '\r'
    AFTER_BAR = '\n'
else:
    BEFORE_BAR = '\r\033[?25l'
    AFTER_BAR = '\033[?25h\n'


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
        message = "URL=<{}>; External Cheks={}; Threads={}; Retry={}".format(
            self._crawler.settings.base,
            "On" if self._crawler.settings.external else "Off",
            self._crawler.settings.threads,
            self._crawler.settings.retry,
        )

        return message

    def _progress_handler(self) -> None:
        """ progress handler desides states regarding crawler """

        while not self._crawler.crawled:
            while self._crawler.crawling:
                print(BEFORE_BAR, file=stdout, end="", flush=True)

                # why: because len of the colored progress msg is way larger
                #      decolored one, so its print way more spaces to strout.
                if self.is_colored():
                    self._progress_msg = click.unstyle(self._progress_msg)

                print(' ' * len(self._progress_msg), file=stdout, end="", flush=True)
                print(BEFORE_BAR, file=stdout, end="", flush=True)

                # why: hey, its just regular coloring output (isntead click.echo)
                self._progress_msg = self._get_progress()
                if not self.is_colored():
                    self._progress_msg = click.unstyle(self._progress_msg)

                print(self._progress_msg, file=stdout, end="", flush=True)
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
        if key not in {'failed', 'ok', 'ignored'}:
            return ""

        param = 'succeed' if key == 'ok' else key
        links = self._crawler.__getattribute__(param)
        if not links:
            return ""

        param_color = click.style(param, fg=self.params_colors[param])

        return '\n'.join(map(lambda x: "[ {} ] {}".format(param_color, x), links))

    def report(self) -> None:

        last_line_printed = click.unstyle(self._progress_msg)

        print(BEFORE_BAR, file=stdout, end="", flush=True)
        print(' ' * len(last_line_printed), file=stdout, end="", flush=True)
        print(BEFORE_BAR, file=stdout, end='', flush=True)

        info = self.info() # type: str
        stat = self._get_progress() # type: str

        split_line_len = max(len(click.unstyle(info)), len(click.unstyle(stat)))

        click.echo("=" * split_line_len)
        click.echo(info, color=self.is_colored())
        click.echo("=" * split_line_len)

        click.echo(stat, color=self.is_colored())
        print("-" * split_line_len, file=stdout, end='\033[?25h\n')

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
