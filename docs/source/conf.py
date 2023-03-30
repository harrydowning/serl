# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
from serl.constants import NAME, VERSION

project = NAME.title()
copyright = '2023, Harry Downing'
author = 'Harry Downing'
release = VERSION

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []
templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# see https://sphinx-rtd-theme.readthedocs.io/en/stable/configuring.html
html_theme_options = {
    'style_external_links': True,
    'sticky_navigation': False,
    'navigation_depth': 2,
}

# -- Options for Latex/PDF output -------------------------------------------------

# latex_documents = [
#   ('index', 'foo.tex', u'foo Documentation',
#    u'bar', 'manual', True),
# ]