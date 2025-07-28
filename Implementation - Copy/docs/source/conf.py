import os
import sys
sys.path.insert(0, os.path.abspath('../../components'))  # Adjust this if needed
sys.path.insert(0, os.path.abspath('../..'))
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'sidebar.py'
copyright = '2025, vijay'
author = 'vijay'
release = 'v.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',     # Pulls docstrings from code
    'sphinx.ext.napoleon',    # Supports Google/NumPy docstrings
    'sphinx.ext.viewcode'     # Adds [source] links to documentation
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = "sphinx_rtd_theme"
 
html_logo = '_static/ACSMS_LOGO.png'
html_favicon = '_static/ES_Logo.ico'
 
html_static_path = ['_static']
html_css_files = ['custom.css']
 
html_theme_options = {
    'analytics_id': 'G-XXXXXXXXXX',
    'analytics_anonymize_ip': False,
    'logo_only': False,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': 'white',
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
   
}