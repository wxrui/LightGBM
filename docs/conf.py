#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# LightGBM documentation build configuration file, created by
# sphinx-quickstart on Thu May  4 14:30:58 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute.
"""Sphinx configuration file."""
import datetime
import os
import sys
import sphinx

from docutils.parsers.rst import Directive
from sphinx.errors import VersionRequirementError
from subprocess import PIPE, Popen

CURR_PATH = os.path.abspath(os.path.dirname(__file__))
LIB_PATH = os.path.join(CURR_PATH, os.path.pardir, 'python-package')
sys.path.insert(0, LIB_PATH)

# -- mock out modules
try:
    from unittest.mock import Mock  # Python 3.x
except ImportError:
    from mock import Mock  # Python 2.x

MOCK_MODULES = ['numpy', 'scipy', 'scipy.sparse',
                'sklearn', 'matplotlib', 'pandas', 'graphviz']
for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = Mock()


class IgnoredDirective(Directive):
    """Stub for unknown directives."""

    has_content = True

    def run(self):
        """Do nothing."""
        return []


# -- General configuration ------------------------------------------------

os.environ['LIGHTGBM_BUILD_DOC'] = '1'
C_API = os.environ.get('C_API', '').lower().strip() != 'no'

# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = '1.3'  # Due to sphinx.ext.napoleon
if needs_sphinx > sphinx.__version__:
    message = 'This project needs at least Sphinx v%s' % needs_sphinx
    raise VersionRequirementError(message)

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
# source_suffix = ['.rst', '.md']

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'LightGBM'
copyright = '%s, Microsoft Corporation' % str(datetime.datetime.now().year)
author = 'Microsoft Corporation'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
with open(os.path.join(CURR_PATH, os.path.pardir, 'VERSION.txt'), 'r') as f:
    # The short X.Y version.
    version = f.read().strip()

    # The full version, including alpha/beta/rc tags.
    release = version

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'default'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# Both the class' and the __init__ method's docstring are concatenated and inserted.
autoclass_content = 'both'

# -- Configuration for C API docs generation ------------------------------

if C_API:
    extensions.extend([
        'breathe',
    ])
    breathe_projects = {
        "LightGBM": os.path.join(CURR_PATH, 'doxyoutput', 'xml')
    }
    breathe_default_project = "LightGBM"
    breathe_domain_by_extension = {
        "h": "c",
    }
    breathe_show_define_initializer = True

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    'includehidden': False,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'LightGBMdoc'


def generate_doxygen_xml(app):
    """Generate XML documentation for C API by Doxygen.

    Parameters
    ----------
    app : object
        The application object representing the Sphinx process.
    """
    doxygen_args = [
        "INPUT={}".format(os.path.join(CURR_PATH, os.path.pardir,
                                       'include', 'LightGBM', 'c_api.h')),
        "OUTPUT_DIRECTORY={}".format(os.path.join(CURR_PATH, 'doxyoutput')),
        "GENERATE_HTML=NO",
        "GENERATE_LATEX=NO",
        "GENERATE_XML=YES",
        "XML_OUTPUT=xml",
        "XML_PROGRAMLISTING=YES",
        r'ALIASES="rst=\verbatim embed:rst:leading-asterisk"',
        r'ALIASES+="endrst=\endverbatim"',
        "ENABLE_PREPROCESSING=YES",
        "MACRO_EXPANSION=YES",
        "EXPAND_ONLY_PREDEF=NO",
        "SKIP_FUNCTION_MACROS=NO",
        "SORT_BRIEF_DOCS=YES",
        "WARN_AS_ERROR=YES",
    ]
    doxygen_input = '\n'.join(doxygen_args)
    is_py3 = sys.version[0] == "3"
    if is_py3:
        doxygen_input = bytes(doxygen_input, "utf-8")
    if not os.path.exists(os.path.join(CURR_PATH, 'doxyoutput')):
        os.makedirs(os.path.join(CURR_PATH, 'doxyoutput'))
    try:
        # Warning! The following code can cause buffer overflows on RTD.
        # Consider suppressing output completely if RTD project silently fails.
        # Refer to https://github.com/svenevs/exhale
        # /blob/fe7644829057af622e467bb529db6c03a830da99/exhale/deploy.py#L99-L111
        process = Popen(["doxygen", "-"],
                        stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate(doxygen_input)
        output = '\n'.join([i.decode('utf-8') if is_py3 else i
                            for i in (stdout, stderr) if i is not None])
        if process.returncode != 0:
            raise RuntimeError(output)
        else:
            print(output)
    except BaseException as e:
        raise Exception("An error has occurred while executing Doxygen\n" + str(e))


def setup(app):
    """Add new elements at Sphinx initialization time.

    Parameters
    ----------
    app : object
        The application object representing the Sphinx process.
    """
    if C_API:
        app.connect("builder-inited", generate_doxygen_xml)
    else:
        app.add_directive('doxygenfile', IgnoredDirective)
    app.add_javascript("js/script.js")
