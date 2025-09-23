# Configuration file for the Sphinx documentation builder.
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../app'))

# Project information
project = 'Contact Management API'
copyright = '2025, Contact Management Team'
author = 'Contact Management Team'
release = '2.0.0'

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx_rtd_theme',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
language = 'uk'

# HTML output options
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ['custom.css']

# Theme options
html_theme_options = {
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'style_nav_header_background': '#2980B9',
}

# Autodoc options
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

autodoc_mock_imports = [
    'fastapi', 'sqlalchemy', 'pydantic', 'jose', 'passlib',
    'redis', 'cloudinary', 'fastapi_mail', 'alembic'
]

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_special_with_doc = True

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'fastapi': ('https://fastapi.tiangolo.com/', None),
}

def setup(app):
    app.add_css_file('custom.css')
