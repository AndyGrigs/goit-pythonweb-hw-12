# Configuration file for the Sphinx documentation builder.
import os
import sys
from pathlib import Path

# Add the project root and app to the path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "app"))

print(f"Project root: {project_root}")
print(f"Python path: {sys.path[:3]}")

# Project information
project = 'Contact Management API'
copyright = '2025, Contact Management Team'
author = 'Contact Management Team'
release = '2.0.0'
version = '2.0.0'

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.githubpages',
    'sphinx_rtd_theme',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
language = 'uk'

# Source file suffixes
source_suffix = {
    '.rst': None,
    '.md': 'myst_parser',
}

# Master document
master_doc = 'index'

# HTML output options
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ['custom.css']

# Theme options
html_theme_options = {
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False,
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    'style_nav_header_background': '#2980B9',
}

# HTML context
html_context = {
    'display_github': True,
    'github_user': 'yourusername',
    'github_repo': 'contact-management-api',
    'github_version': 'main',
    'conf_py_path': '/docs/',
}

# Autodoc options
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Mock imports для модулів, які не можуть бути імпортовані
autodoc_mock_imports = [
    # FastAPI та веб-фреймворки
    'fastapi',
    'fastapi.middleware',
    'fastapi.security',
    'fastapi.responses',
    'fastapi_mail',
    'slowapi',
    'uvicorn',
    
    # База даних
    'sqlalchemy',
    'alembic',
    'psycopg2',
    'psycopg2-binary',
    
    # Валідація та серіалізація
    'pydantic',
    'pydantic_settings',
    
    # Аутентифікація та безпека
    'jose',
    'passlib',
    'python-jose',
    
    # Зовнішні сервіси
    'redis',
    'cloudinary',
    
    # Інші
    'python-multipart',
    'python-dotenv',
    'typing_extensions'
]

# Napoleon settings (Google та NumPy docstrings)
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

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'fastapi': ('https://fastapi.tiangolo.com/', None),
    'sqlalchemy': ('https://docs.sqlalchemy.org/', None),
    'pydantic': ('https://docs.pydantic.dev/', None),
}

# Todo extension
todo_include_todos = True

def setup(app):
    """Налаштування Sphinx app."""
    app.add_css_file('custom.css')
