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

# -- Imports -------------------------------------------------------------------

from typing import Dict, Any

import click

from deadlinks.settings import Settings
from deadlinks.crawler import Crawler
from deadlinks.exceptions import DeadlinksExeption

from .exporters import Export #pylint: disable-msg=W0611
from .exporters import exporters

from .__version__ import __app_version__ as version
from .__version__ import __app_package__ as name

from .options import default_options
from .clicker import register_options
from .clicker import register_exports
from .clicker import command
from .clicker import argument


@click.command(name, **command)
@click.argument('url', **argument)
@click.version_option(message='%(prog)s: v%(version)s', prog_name=name, version=version)
@register_exports(exporters)
@register_options("Default Options", default_options)
@click.pass_context
def main(ctx: click.Context, url: str, **opts: Dict[str, Any]) -> None:
    """ Check links in your (web) documentation for accessibility.  """

    try:
        settings = Settings(
            url, **{
                'check_external_urls': opts['external'],
                'stay_within_path': not opts['full_site_check'],
                'threads': opts['threads'],
                'retry': opts['retry'],
                'ignore_domains': opts['domains'],
                'ignore_pathes': opts['pathes'],
            })
        crawler = Crawler(settings)

        driver = exporters[str(opts['export'])]

        # Instantion of the exported before starting crawling will alow us to
        # have prgress report, while we crawling website.
        exporter = driver(crawler, **opts)

        # Starting crawler
        crawler.start()

        # And showing report of crawling, in 90% we not shoing anything
        # untill crawling is done, so we can just output (pipe) data
        # to where user desire have results.
        exporter.report()

        if opts['fiff'] and len(crawler.failed) > 0:
            ctx.exit(1)

    except DeadlinksExeption as e:
        ctx.fail(e.__str__())


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
