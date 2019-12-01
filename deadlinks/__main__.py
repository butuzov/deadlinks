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
~~~~~~~~~~~~~~

Main (cli interface)

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

import click

from .settings import Settings
from .crawler import Crawler
from .exceptions import DeadlinksException

# CLI implementation related
from .clicker import (register_options, register_exports)
from .clicker import Options
from .clicker import (command, argument)

# Exporters
from .exporters import Export #pylint: disable-msg=W0611
from .exporters import exporters

# Default and Specified Options
from .options import default_options as general_options
from .serving.options import default_options as serving_options

# Version and App.
from .__version__ import __app_version__ as version
from .__version__ import __app_package__ as name

# -- Implementation ------------------------------------------------------------


@click.command(name, **command)
@click.argument('url', **argument)
@click.version_option(version, '-V', '--version', message='%(prog)s: v%(version)s', prog_name=name)
@register_exports(exporters)
@register_options("Server Settings", serving_options)
@register_options("Default Options", general_options)
@click.pass_context
def main(ctx: click.Context, url: str, **opts: Options) -> None:
    """ Check links in your (web) documentation for accessibility. """

    try:
        settings = Settings(url, **opts)
        crawler = Crawler(settings)

        driver = exporters[str(opts['export'])]

        # Instantion of the exported before starting crawling will alow us to
        # have progress report, while we crawling website.
        exporter = driver(crawler, **opts)

        # Starting crawler
        crawler.start()

        # And showing report of crawling, in 90% we not showing anything
        # un till crawling is done, so we can just output (pipe) data
        # to where user desire have results.
        exporter.report()

        if opts['fail_if_fails_found'] and len(crawler.failed) > 0:
            ctx.exit(1)

    except DeadlinksException as e:
        ctx.fail(e.__str__())


if __name__ == "__main__":
    main() # pylint: disable=no-value-for-parameter
