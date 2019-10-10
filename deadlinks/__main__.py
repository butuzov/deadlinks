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
deadlinks.main
~~~~~~~~~~~~~~~~~

main (cli interface)

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

from typing import Dict, Any

import click

from deadlinks.help import CLI
from deadlinks.settings import Settings
from deadlinks.link import Link
from deadlinks.crawler import Crawler
from deadlinks.exceptions import DeadlinksExeption
from deadlinks.reports import Console
from deadlinks.__init__ import __app_version__, __app_package__

# ~ Options ~~~~~

options = dict() # type: Dict[str, Dict[str, Any]]

options['external'] = {
    'keys': ['-e', '--external'],
    'params': {
        'default': False,
        'is_flag': True,
        'multiple': False,
        'show_default': True,
        'help': 'Enables external resources check',
    }
}

options['retry'] = {
    'keys': ['-r', '--retry'],
    'params': {
        'default': 0,
        'type': click.IntRange(0, 10),
        'is_flag': False,
        'multiple': False,
        'show_default': True,
        'help': 'try for error',
    }
}
options['threads'] = {
    'keys': ['-n', '--threads'],
    'params': {
        'default': 1,
        'type': click.IntRange(1, 10),
        'is_flag': False,
        'multiple': False,
        'show_default': True,
        'help': 'cralwer instances to run',
    }
}
options['domains'] = {
    'keys': ['-d', '--domains'],
    'params': {
        'multiple': True,
        'help': 'Domains to ignore',
    },
}
options['pathes'] = {
    'keys': ['-p', '--pathes'],
    'params': {
        'multiple': True,
        'help': 'Pathes to ignore',
    },
}

options['show'] = {
    'keys': ['-s', '--show'],
    'params': {
        'default': ['failed'],
        'multiple': True,
        'type': click.Choice([
            'failed',
            'ok',
            'ignored',
            'all',
            'none',
        ], case_sensitive=False),
        'show_default': True,
        'help': 'Category of URLs to show.',
    },
}

options['export'] = {
    'keys': ['--export'],
    'params': {
        'default': 'default',
        'hidden': True,
        'multiple': False,
        'type': click.Choice([
            'default',
        ], case_sensitive=False),
        'help': 'Export type',
    },
}

options['within_path'] = {
    'keys': ['--full-site-check'],
    'params': {
        'default': False,
        'is_flag': True,
        'help': 'Check links on domain not limiting',
    },
}

options['color'] = {
    'keys': ['--no-colors'],
    'params': {
        'default': False,
        'is_flag': True,
        'help': 'Color output of `default` export',
    },
}

# ~ Actual command decoration ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


@click.command(__app_package__, cls=CLI, context_settings={"ignore_unknown_options": True})
@click.argument('url', nargs=1, required=True, metavar='<URL>')
@click.option(*options['external']['keys'], **options['external']['params'])
@click.option(*options['threads']['keys'], **options['threads']['params'])
@click.option(*options['retry']['keys'], **options['retry']['params'])
@click.option(*options['domains']['keys'], **options['domains']['params'])
@click.option(*options['pathes']['keys'], **options['pathes']['params'])
@click.option(*options['show']['keys'], **options['show']['params'])
@click.option(*options['export']['keys'], **options['export']['params'])
@click.option(*options['within_path']['keys'], **options['within_path']['params'])
@click.option(*options['color']['keys'], **options['color']['params'])
@click.version_option(
    message='%(prog)s: v%(version)s',
    prog_name=__app_package__,
    version=__app_version__,
)
@click.pass_context
def main(ctx: click.Context, url: str, **opts: Dict[str, Any]) -> None:
    """ checking links from web resource for dead/alive status. """

    try:
        settings = Settings(
            normilize_domain(url),
            **{
                'check_external_urls': opts['external'],
                'stay_within_path': not opts['full_site_check'],
                'threads': opts['threads'],
                'retry': opts['retry'],
                'ignore_domains': opts['domains'],
                'ignore_pathes': opts['pathes'],
            },
        )
        crawler = Crawler(settings)
        crawler.start()

        if str(opts['export']) == "default":
            Console(crawler, **opts).report()

    except DeadlinksExeption as e:
        ctx.fail(str(e))


def normilize_domain(url: str) -> str:
    """ 'guessing' scheme for urls without it. """

    u = Link(url)
    if not u.is_valid() and not u.scheme:
        return "http://{}".format(url)

    return url


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
