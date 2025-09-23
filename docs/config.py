# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import django

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../app'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Contact Management API'
copyright = '2025, Contact Management Team'
author = 'Contact Management Team'
release = '2.0.0'
version = '2.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',           # Автоматична документація з docstrings
    'sphinx.ext.viewcode',          # Посилання на вихідний код
    'sphinx.ext.napoleon',          # Підтримка Google/NumPy style docstrings
    'sphinx.ext.intersphinx',       # Посилання на інші проекти Sphinx
    'sphinx.ext.todo',              # Підтримка TODO блоків
    'sphinx.ext.coverage',          # Звіт про покриття документації
    'sphinx.ext.ifconfig',          # Умовна документація
    'sphinx.ext.githubpages',       # Підтримка GitHub Pages
    'sphinx_rtd_theme',             # Read The Docs тема
    'myst_parser',                  # Підтримка Markdown файлів
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Мова документації
language = 'uk'  # Українська мова

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Додаткові опції для теми
html_theme_options = {
    'analytics_id': '',
    'analytics_anonymize_ip': False,
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#2980B9',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Логотип та фавікон
html_logo = "_static/logo.png"
html_favicon = "_static/favicon.ico"

# Кастомний CSS
html_css_files = [
    'custom.css',
]

# Заголовок HTML сторінок
html_title = f"{project} v{version} Documentation"

# Додаткові HTML контексти
html_context = {
    "display_github": True,
    "github_user": "your-username",
    "github_repo": "contact-management-api",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

# -- Extension configuration -------------------------------------------------

# -- Options for autodoc extension -------------------------------------------

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Автоматично документувати модулі
autodoc_mock_imports = [
    'fastapi',
    'sqlalchemy',
    'pydantic',
    'jose',
    'passlib',
    'redis',
    'cloudinary',
    'fastapi_mail',
]

# -- Options for napoleon extension ------------------------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Options for intersphinx extension ---------------------------------------

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'fastapi': ('https://fastapi.tiangolo.com/', None),
    'sqlalchemy': ('https://docs.sqlalchemy.org/en/20/', None),
    'pydantic': ('https://docs.pydantic.dev/latest/', None),
}

# -- Options for todo extension ----------------------------------------------

todo_include_todos = True

# -- Options for coverage extension ------------------------------------------

coverage_show_missing_items = True

# -- Custom configuration ----------------------------------------------------

# Додавання кастомних ролей
rst_prolog = """
.. |project| replace:: Contact Management API
.. |version| replace:: 2.0.0
"""

# Налаштування автодокументації
autoclass_content = "both"  # Включити і класс, і __init__ docstrings

# Порядок членів класу
autodoc_member_order = 'bysource'

# Показувати повні імена модулів
add_module_names = True

# Показувати типи параметрів
autodoc_typehints = "description"

# Налаштування для MyST (Markdown)
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]

# Suppress warnings
suppress_warnings = ['epub.unknown_project_files']

# -- Custom directives and roles ---------------------------------------------

def setup(app):
    """
    Кастомні налаштування для Sphinx.
    
    Args:
        app: Sphinx application instance
    """
    app.add_css_file('custom.css')
    
    # Додавання кастомних директив або ролей можна додати тут
    pass