#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для автоматичного налаштування Sphinx документації
для Contact Management API проекту.

Використання:
    python setup_docs.py [--clean] [--build] [--serve]

Опції:
    --clean     Очистити існуючу документацію
    --build     Побудувати документацію після налаштування
    --serve     Запустити сервер для перегляду документації
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())


def run_command(command, description="", check=True):
    """Запускає команду та виводить результат."""
    print(f"🔄 {description}")
    print(f"Команда: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        print(f"✅ {description} - Успішно")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Помилка: {e}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False


def check_dependencies():
    """Перевіряє наявність необхідних залежностей."""
    print("🔍 Перевірка залежностей...")
    
    required_packages = [
        "sphinx",
        "sphinx-rtd-theme",
        "myst-parser"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️ Відсутні пакети: {', '.join(missing_packages)}")
        print("Встановіть їх командою:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ Всі залежності встановлені")
    return True


def create_docs_structure():
    """Створює структуру директорій для документації."""
    print("📁 Створення структури директорій...")
    
    dirs_to_create = [
        "docs",
        "docs/_static",
        "docs/_templates", 
        "docs/modules",
        "docs/api",
        "docs/development",
        "docs/images"
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Створено: {dir_path}")
    
    print("✅ Структура директорій створена")


def install_docs_dependencies():
    """Встановлює залежності для документації."""
    print("📦 Встановлення залежностей документації...")
    
    docs_requirements = [
        "sphinx>=7.1.0",
        "sphinx-rtd-theme>=1.3.0", 
        "myst-parser>=2.0.0",
        "sphinx-autobuild>=2021.3.14",
        "sphinx-autodoc-typehints>=1.24.0"
    ]
    
    for package in docs_requirements:
        success = run_command(
            ["pip", "install", package],
            f"Встановлення {package.split('>=')[0]}",
            check=False
        )
        if not success:
            print(f"⚠️ Не вдалося встановити {package}")
    
    print("✅ Залежності встановлені")


def create_sphinx_config():
    """Створює конфігураційний файл Sphinx."""
    print("⚙️ Створення конфігурації Sphinx...")
    
    config_content = '''# Configuration file for the Sphinx documentation builder.
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
'''
    
    with open("docs/conf.py", "w", encoding="utf-8") as f:
        f.write(config_content)
    
    print("✅ Конфігурація Sphinx створена")


def create_index_page():
    """Створює головну сторінку документації."""
    print("📄 Створення головної сторінки...")
    
    index_content = '''Contact Management API Documentation
=====================================

.. image:: https://img.shields.io/badge/version-2.0.0-blue.svg
   :alt: Version

.. image:: https://img.shields.io/badge/python-3.9+-green.svg
   :alt: Python Version

Ласкаво просимо до документації **Contact Management API** - системи для управління контактами з JWT аутентифікацією.

🌟 Особливості
--------------

* JWT аутентифікація
* Email верифікація
* Управління контактами
* Завантаження аватарів
* Rate limiting
* Redis кешування

📚 Зміст
--------

.. toctree::
   :maxdepth: 2
   :caption: API Документація

   api/authentication
   api/users
   api/contacts

.. toctree::
   :maxdepth: 2
   :caption: Код документація

   modules/models
   modules/crud
   modules/services

🚀 Швидкий старт
----------------

1. Клонування проекту:

.. code-block:: bash

   git clone <repo-url>
   cd contact-management-api

2. Встановлення залежностей:

.. code-block:: bash

   pip install -r requirements.txt

3. Запуск API:

.. code-block:: bash

   uvicorn app.main:app --reload

Індекси
=======

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
'''
    
    with open("docs/index.rst", "w", encoding="utf-8") as f:
        f.write(index_content)
    
    print("✅ Головна сторінка створена")


def create_makefile():
    """Створює Makefile для документації."""
    print("🔨 Створення Makefile...")
    
    makefile_content = '''# Makefile for Sphinx documentation

SPHINXOPTS    ?=
SPHINXBUILD  ?= sphinx-build
SOURCEDIR    = .
BUILDDIR     = _build

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Live reload for development
livehtml:
	sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)/html" --host 0.0.0.0 --port 8080

# Clean build
clean-build: clean html

# Build and open in browser
html-open: html
	@python -c "import webbrowser; webbrowser.open('_build/html/index.html')"
'''
    
    with open("docs/Makefile", "w", encoding="utf-8") as f:
        f.write(makefile_content)
    
    print("✅ Makefile створено")


def create_requirements_file():
    """Створює файл requirements для документації."""
    print("📋 Створення requirements.txt для документації...")
    
    requirements_content = '''sphinx>=7.1.0
sphinx-rtd-theme>=1.3.0
sphinx-autodoc-typehints>=1.24.0
myst-parser>=2.0.0
sphinx-autoapi>=3.0.0
sphinx-autobuild>=2021.3.14
typing-extensions>=4.8.0
'''
    
    with open("docs/requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements_content)
    
    print("✅ requirements.txt створено")


def generate_module_docs():
    """Генерує документацію для модулів автоматично."""
    print("🔄 Генерація документації модулів...")
    
    # Створюємо RST файли для основних модулів
    modules_info = {
        "models": {
            "title": "Моделі бази даних",
            "description": "SQLAlchemy моделі для користувачів та контактів"
        },
        "crud": {
            "title": "CRUD операції",
            "description": "Функції для роботи з базою даних"
        },
        "utils": {
            "title": "Утиліти",
            "description": "Допоміжні функції та утиліти"
        },
        "services": {
            "title": "Сервіси",
            "description": "Зовнішні сервіси (Redis, Cloudinary, Email)"
        },
        "middleware": {
            "title": "Middleware",
            "description": "Middleware для аутентифікації та rate limiting"
        }
    }
    
    for module_name, info in modules_info.items():
        rst_content = f'''{info["title"]}
{'=' * len(info["title"])}

{info["description"]}

.. automodule:: app.{module_name}
   :members:
   :undoc-members:
   :show-inheritance:
'''
        
        with open(f"docs/modules/{module_name}.rst", "w", encoding="utf-8") as f:
            f.write(rst_content)
        
        print(f"✅ Створено docs/modules/{module_name}.rst")


def build_documentation():
    """Будує документацію."""
    print("🏗️ Побудова документації...")

    os.chdir("docs")

    # Спочатку спробуємо make (для Unix систем)
    success = False
    try:
        success = run_command(
            ["make", "html"],
            "Побудова HTML документації (make)",
            check=False
        )
    except FileNotFoundError:
        print("⚠️ Команда 'make' недоступна, використовуємо sphinx-build...")

    # Якщо make не працює, використовуємо sphinx-build напряму
    if not success:
        success = run_command(
            ["sphinx-build", "-b", "html", ".", "_build/html"],
            "Побудова HTML документації (sphinx-build)"
        )

    os.chdir("..")

    if success:
        print("✅ Документація успішно побудована!")
        print("📁 HTML файли знаходяться в: docs/_build/html/")
        print("🌐 Відкрийте docs/_build/html/index.html у браузері")
    else:
        print("❌ Помилка при побудові документації")

    return success


def serve_documentation():
    """Запускає сервер для перегляду документації."""
    print("🚀 Запуск сервера документації...")
    
    os.chdir("docs")
    
    try:
        print("📡 Сервер запущено на http://localhost:8080")
        print("Натисніть Ctrl+C для зупинки")
        
        subprocess.run([
            "sphinx-autobuild", 
            ".", 
            "_build/html",
            "--host", "0.0.0.0",
            "--port", "8080"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Сервер зупинено")
    finally:
        os.chdir("..")


def clean_docs():
    """Очищує існуючу документацію."""
    print("🧹 Очищення документації...")
    
    paths_to_clean = [
        "docs/_build",
        "docs/modules",
    ]
    
    for path in paths_to_clean:
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"✅ Очищено: {path}")
        else:
            print(f"⚠️ Шлях не існує: {path}")
    
    print("✅ Очищення завершено")


def main():
    """Головна функція."""
    parser = argparse.ArgumentParser(
        description="Налаштування Sphinx документації для Contact Management API"
    )
    parser.add_argument("--clean", action="store_true", 
                       help="Очистити існуючу документацію")
    parser.add_argument("--build", action="store_true",
                       help="Побудувати документацію після налаштування")
    parser.add_argument("--serve", action="store_true",
                       help="Запустити сервер для перегляду")
    
    args = parser.parse_args()
    
    print("📚 Contact Management API - Налаштування документації")
    print("=" * 60)
    
    try:
        # Очищення якщо потрібно
        if args.clean:
            clean_docs()
        
        # Основне налаштування
        if not check_dependencies():
            print("❌ Встановіть відсутні залежності та спробуйте знову")
            sys.exit(1)
        
        create_docs_structure()
        install_docs_dependencies()
        create_sphinx_config()
        create_index_page()
        create_makefile()
        create_requirements_file()
        generate_module_docs()
        
        print("\n🎉 Налаштування документації завершено!")
        
        # Побудова якщо потрібно
        if args.build:
            build_documentation()
        
        # Запуск сервера якщо потрібно
        if args.serve:
            serve_documentation()
        
        # Підсумок
        print("\n📋 Наступні кроки:")
        print("1. cd docs")
        print("2. make html                 # Побудувати документацію")
        print("3. make livehtml            # Запустити live reload сервер")
        print("4. firefox _build/html/index.html  # Відкрити в браузері")
        
    except KeyboardInterrupt:
        print("\n❌ Налаштування перервано користувачем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Неочікувана помилка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()