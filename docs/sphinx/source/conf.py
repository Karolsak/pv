#
# PVLIB_Python documentation build configuration file, created by
# sphinx-quickstart on Fri Nov  7 15:56:33 2014.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import sys
import os

# for warning suppression
import warnings

# for generating GH links with linenumbers
import inspect

# import distutils before calling pd.show_versions()
# https://github.com/pypa/setuptools/issues/3044
import distutils  # noqa: F401
import pandas as pd

pd.show_versions()

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath('../sphinxext'))
sys.path.insert(0, os.path.abspath('../../../'))

# -- General configuration ------------------------------------------------

# use napoleon in lieu of numpydoc 2019-04-23

# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.extlinks',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',
    'IPython.sphinxext.ipython_directive',
    'IPython.sphinxext.ipython_console_highlighting',
    'sphinx_gallery.gen_gallery',
    'sphinx_toggleprompt',
    'sphinx_favicon',
]

mathjax3_config = {'chtml': {'displayAlign': 'left',
                             'displayIndent': '2em'}}

napoleon_use_rtype = False  # group rtype on same line together with return

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'pvlib python'
copyright = \
    '2013-2021, Sandia National Laboratories and pvlib python Development Team'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.

import pvlib  # noqa: E402

# The short X.Y version.
version = '%s' % (pvlib.__version__)
# The full version, including alpha/beta/rc tags.
release = version

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['whatsnew/*', '**.ipynb_checkpoints']

# The reST default role (used for this markup: `text`) to use for all
# documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
#keep_warnings = False

autosummary_generate = True

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "pydata_sphinx_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
# https://pydata-sphinx-theme.rtfd.io/en/latest/user_guide/configuring.html
html_theme_options = {
    "github_url": "https://github.com/pvlib/pvlib-python",
    "icon_links": [
        {
            "name": "StackOverflow",
            "url": "https://stackoverflow.com/questions/tagged/pvlib",
            "icon": "fab fa-stack-overflow",
        },
        {
            "name": "Google Group",
            "url": "https://groups.google.com/g/pvlib-python",
            "icon": "fab fa-google",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/pvlib/",
            "icon": "fab fa-python",
        },
    ],
    "use_edit_page_button": True,
    "show_toc_level": 1,
    # "footer_start": [],  # "copyright", "sphinx-version"
    # "footer_center": [],
    "footer_end": [],
    "primary_sidebar_end": [],
    # https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/layout.html#hide-the-previous-and-next-buttons
    "show_prev_next": False,  # disable next/previous links
}  # noqa: E501

# Add favicons from extension sphinx_favicon
favicons = [
    {"rel": "icon", "sizes": "16x16", "href": "favicon-16x16.png"},
    {"rel": "icon", "sizes": "32x32", "href": "favicon-32x32.png"},
]


# Add any paths that contain custom themes here, relative to this directory.
# html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
#html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = '_images/pvlib_logo_horiz.png'

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
#html_extra_path = []

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {
#     "**": ["sidebar-nav-bs"]
# }

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
# html_domain_indices = True

# If false, no index is generated.
# html_use_index = True

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
# html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
# html_show_copyright = False

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = 'pvlib_pythondoc'


# custom CSS workarounds
def setup(app):
    # A workaround for the responsive tables always having annoying scrollbars.
    app.add_css_file("no_scrollbars.css")
    # Override footnote callout CSS to be normal text instead of superscript
    # In-line links to references as numbers in brackets.
    app.add_css_file("reference_format.css")
    # Add a warning banner at the top of the page if viewing the "latest" docs
    app.add_js_file("version-alert.js")

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
#'papersize': 'letterpaper',

# The font size ('10pt', '11pt' or '12pt').
#'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
#'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    ('index', 'pvlib_python.tex', 'pvlib\\_python Documentation',
     'Sandia National Laboratoraties and pvlib python Development Team',
     'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True

# extlinks alias
extlinks = {
    "issue": ("https://github.com/pvlib/pvlib-python/issues/%s", "GH%s"),
    "pull": ("https://github.com/pvlib/pvlib-python/pull/%s", "GH%s"),
    "wiki": ("https://github.com/pvlib/pvlib-python/wiki/%s", "wiki %s"),
    "doi": ("http://dx.doi.org/%s", "DOI: %s"),
    "ghuser": ("https://github.com/%s", "@%s"),
    "discuss": (
        "https://github.com/pvlib/pvlib-python/discussions/%s",
        "GH%s",
    ),
}

# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'pvlib_python', 'pvlib_python Documentation',
     ['Sandia National Laboratoraties and pvlib python Development Team'], 1)
]

# If true, show URL addresses after external links.
#man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    ('index', 'pvlib python', 'pvlib python Documentation',
     'Sandia National Laboratoraties and pvlib python Development Team',
     'pvlib python', 'One line description of project.',
     'Miscellaneous'),
]

# Documents to append as an appendix to all manuals.
#texinfo_appendices = []

# If false, no module index is generated.
#texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
#texinfo_no_detailmenu = False

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/reference/', None),
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable', None),
    'matplotlib': ('https://matplotlib.org/stable', None),
}

ipython_warning_is_error = False

# suppress "WARNING: Footnote [1] is not referenced." messages
# https://github.com/pvlib/pvlib-python/issues/837
suppress_warnings = ['ref.footnote']

# settings for sphinx-gallery
sphinx_gallery_conf = {
    'examples_dirs': ['../../examples'],  # location of gallery scripts
    'gallery_dirs': ['gallery'],  # location of generated output
    # execute all scripts except for ones in the "system-models" directory:
    'filename_pattern': '^((?!system-models).)*$',

    # directory where function/class granular galleries are stored
    'backreferences_dir': 'reference/generated/gallery_backreferences',

    # Modules for which function/class level galleries are created. In
    # this case only pvlib, could include others though. Must be tuple of str
    'doc_module': ('pvlib',),

    # https://sphinx-gallery.github.io/dev/configuration.html#removing-config-comments  # noqa: E501
    'remove_config_comments': True,
}
# supress warnings in gallery output
# https://sphinx-gallery.github.io/stable/configuration.html
warnings.filterwarnings("ignore", category=UserWarning,
                        message='Matplotlib is currently using agg, which is a'
                                ' non-GUI backend, so cannot show the figure.')

# %% helper functions for intelligent "View on Github" linking
# based on
# https://gist.github.com/flying-sheep/b65875c0ce965fbdd1d9e5d0b9851ef1


def get_obj_module(qualname):
    """
    Get a module/class/attribute and its original module by qualname.
    Useful for looking up the original location when a function is imported
    into an __init__.py

    Examples
    --------
    >>> func, mod = get_obj_module("pvlib.iotools.read_midc")
    >>> mod.__name__
    'pvlib.iotools.midc'
    """
    modname = qualname
    classname = None
    attrname = None
    while modname not in sys.modules:
        attrname = classname
        modname, classname = modname.rsplit('.', 1)

    # retrieve object and find original module name
    if classname:
        cls = getattr(sys.modules[modname], classname)
        modname = cls.__module__
        obj = getattr(cls, attrname) if attrname else cls
    else:
        obj = None

    return obj, sys.modules[modname]


def get_linenos(obj):
    """Get an object’s line numbers in its source code file"""
    try:
        lines, start = inspect.getsourcelines(obj)
    except TypeError:  # obj is an attribute or None
        return None, None
    except OSError:  # obj listing cannot be found
        # This happens for methods that are not explicitly defined
        # such as the __init__ method for a dataclass
        return None, None
    else:
        return start, start + len(lines) - 1


def make_github_url(file_name):
    """
    Generate the appropriate GH link for a given docs page.  This function
    is intended for use in sphinx template files.

    The target URL is built differently based on the type of page.  The pydata
    sphinx theme has a built-in `file_name` variable that looks like
    "/docs/sphinx/source/api.rst" or "generated/pvlib.atmosphere.alt2pres.rst"
    """

    URL_BASE = "https://github.com/pvlib/pvlib-python/blob/main/"

    # is it a gallery page?
    if any(d in file_name for d in sphinx_gallery_conf['gallery_dirs']):
        example_folder = file_name.split("/")[-2]
        if file_name.split("/")[-1] == "index.rst":
            example_file = "README.rst"
        else:
            example_file = file_name.split("/")[-1].replace('.rst', '.py')

        if example_folder == 'gallery':
            target_url = URL_BASE + "docs/examples/" + example_file  # noqa: E501
        else:
            target_url = URL_BASE + "docs/examples/" + example_folder + "/" + example_file  # noqa: E501

    # is it an API autogen page?
    elif "generated" in file_name:
        # pagename looks like "generated/pvlib.atmosphere.alt2pres.rst"
        qualname = file_name.split("/")[-1].replace('.rst', '')
        obj, module = get_obj_module(qualname)
        path = module.__name__.replace(".", "/") + ".py"
        target_url = URL_BASE + path
        # add line numbers if possible:
        start, end = get_linenos(obj)
        if start and end:
            target_url += f'#L{start}-L{end}'

    # Just a normal source RST page
    else:
        target_url = URL_BASE + "docs/sphinx/source/" + file_name

    return target_url


# variables to pass into the HTML templating engine; these are accessible from
# _templates/breadcrumbs.html
html_context = {
    'make_github_url': make_github_url,
    'edit_page_url_template': '{{ make_github_url(file_name) }}',
}
