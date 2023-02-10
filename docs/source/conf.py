# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Tool'
copyright = '2023, Harry Downing'
author = 'Harry Downing'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']

html_theme_options = {
    "logo": {
        "text": "Tool documentation",
    },
    "github_url": "https://github.com/harrydowning/comp3200-project",
    "icon_links": [
        {
            "name": "PyPI",
            "url": "https://pypi.org/",
            "icon": "fa-solid fa-box",
        },
    ],
    "collapse_navigation": True,
    # Add light/dark mode and documentation version switcher:
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
}

html_sidebars = {
    "**": ["search-field.html"]
}