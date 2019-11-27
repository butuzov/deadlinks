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

Default options to be consumed by click

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

from typing import List

from click import IntRange, Choice

from .clicker import OptionRaw

# -- Options -------------------------------------------------------------------

default_options = [] # type: List[OptionRaw]

# Index External URLs ------------------------------------------------------
default_options.append((
    ("check_external_urls", '-e', '--external'),
    {
        'default': False,
        'is_flag': True,
        'show_default': False,
        'help': 'Enables external resources check',
    },
))

# Retries ------------------------------------------------------------------
default_options.append((
    ('-r', '--retry'),
    {
        'default': 0,
        'type': IntRange(0, 10),
        'is_flag': False,
        'show_default': True,
        'metavar': '',
        'help': 'Number of Retries [0...10]',
    },
))

# Concurrent Crawlers ------------------------------------------------------
default_options.append((
    ('-n', '--threads'),
    {
        'default': 1,
        'type': IntRange(1, 10),
        'is_flag': False,
        'show_default': True,
        'metavar': '',
        'help': 'Concurrent crawlers [1...10]',
    },
))

# Ignored Domains  ---------------------------------------------------------
default_options.append((
    ('ignore_domains', '-d', '--domain'),
    {
        'multiple': True,
        'metavar': '',
        'help': 'Domain to ignore (multiple options allowed)',
    },
))

# Ignored Paths  -----------------------------------------------------------
default_options.append((
    ('ignore_pathes', '-p', '--path'),
    {
        'multiple': True,
        'metavar': '',
        'help': 'Path to ignore (multiple options allowe)',
    },
))

# Disable path limiting for a local to the domain links.
default_options.append((
    ('stay_within_path', '--full-site-check'),
    {
        'default': True,
        'is_flag': True,
        'help': 'Check full site',
    },
))

# Show selectors.
default_options.append((
    ('show', '-s', '--show'),
    {
        'default': ['failed'],
        'multiple': True,
        'type': Choice(
            ['failed', 'ok', 'ignored', 'all', 'none'],
            case_sensitive=False,
        ),
        'show_default': False,
        'metavar': '',
        'help': 'Show results [failed (default), ok, ignored, all or none]',
    },
))

default_options.append((
    ('fail_if_fails_found', '--fiff'),
    {
        'default': False,
        'is_flag': True,
        'help': 'Fail if failed URLs are found',
    },
))
