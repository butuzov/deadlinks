# -*- coding: utf-8 -*-

import sys
from os import getenv, path

from recommonmark.parser import CommonMarkParser

sys.path.append(path.dirname(getenv('PWD')))
# sys.path.insert(0, path.dirname(path.dirname(__file__)))

# Add any paths that contain templates here, relative to this directory.
# templates_path = ['_templates']

# The suffix(es) of source filenames.
source_suffix = {
    '.md': 'markdown',
}

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'deadlinks'
copyright = u'Oleg Butuzov' #pylint: disable-msg=W0622
author = u'Oleg Butuzov'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The full version, including alpha/beta/rc tags.

# from deadlinks.__version__ import __version__
# version = release = __version__

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = [
    '_build',
    'Thumbs.db',
    '.DS_Store',
    "readme.md",
    "*/readme.md",
]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
# modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
# keep_warnings = False

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_context = {}

# Output file base name for HTML help builder.
htmlhelp_basename = 'deadlinks'

html_show_sourcelink = False

html_context = {
    "display_github": True, # Add 'Edit on Github' link instead of 'View page source'
    "github_user": "butuzov",
    "github_repo": "deadlinks",
    "github_version": "develop",
    "conf_py_path": "/docs/",
    "source_suffix": ".md",
}
# -- Options for Texinfo output -------------------------------------------

enable_auto_toc_tree = True

extensions = [
    'sphinx_markdown_tables',
]

language = "en"

class MyCommonMarkParser(CommonMarkParser):
    # remove this hack once upsteam RecommonMark supports inline code
    def visit_code(self, mdnode):
        from docutils import nodes
        n = nodes.literal(mdnode.literal, mdnode.literal)
        self.current_node.append(n)

    def visit_document(self, node):
        pass

def setup(app):
    from recommonmark.transform import AutoStructify
    app.add_source_suffix('.md', 'markdown')
    app.add_source_parser(MyCommonMarkParser)

    app.add_config_value(
        'recommonmark_config',
        {
            'enable_auto_toc_tree': True,
            'enable_auto_doc_ref': False, # broken in Sphinx 1.6+
            'enable_eval_rst': True,
            'url_resolver': lambda url: '/' + url
        },
        True)
    app.add_transform(AutoStructify)
