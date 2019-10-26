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
deadlinks.options
~~~~~~~~~~~~~~~~~

default options to be consumed by click

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

from click import IntRange, Choice

default_options = [

    # Index External URLs ------------------------------------------------------
    (
        ('-e', '--external'),
        {
            'default': False,
            'is_flag': True,
            'multiple': False,
            'show_default': False,
            'help': 'Enables external resources check',
        },
    ),

    # Retries ------------------------------------------------------------------
    (
        ('-r', '--retry'),
        {
            'default': 0,
            'type': IntRange(0, 10),
            'is_flag': False,
            'multiple': False,
            'show_default': True,
            'help': 'Number of retries (in case of error)',
        },
    ),

    # Retries ------------------------------------------------------------------
    (
        ('-n', '--threads'),
        {
            'default': 1,
            'type': IntRange(1, 10),
            'is_flag': False,
            'multiple': False,
            'show_default': True,
            'help': 'Concurrent crawlers',
        },
    ),

    # Ignored Domains  ---------------------------------------------------------
    (
        ('-d', '--domains'),
        {
            'multiple': True,
            'help': 'Domains to ignore',
        },
    ),
    # Ignored Paths  -----------------------------------------------------------
    (
        ('-p', '--pathes'),
        {
            'multiple': True,
            'help': 'Pathes to ignore',
        },
    ),

    # Disable path limiting for a local to the domain links.
    (
        ('--full-site-check', ),
        {
            'default': False,
            'is_flag': True,
            'help': 'Check links on domain not limiting',
        },
    ),

    # Default export
    (
        ('-s', '--show'),
        {
            'default': ['failed'],
            'multiple': True,
            'type': Choice(['failed', 'ok', 'ignored', 'all', 'none'], case_sensitive=False),
            'show_default': True,
            'help': 'Category of URLs to show.',
        },
    ),
    (
        ('--fiff', ),
        {
            'default': False,
            'is_flag': True,
            'help': 'Fail if failed URLs are found',
        },
    ),
]
