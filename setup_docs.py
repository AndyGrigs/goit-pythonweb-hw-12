def build_documentation():
    """Будує документацію."""
    print("🏗️ Побудова документації...")

    os.chdir("docs")

    # Спочатку спробуємо make (для Unix систем)
    success = False
    try:
        success = run_command(
            ["make", "clean"],
            "Очищення попередньої побудови",
            check=False
        )
        success = run_command(
            ["make", "html"],
            "Побудова HTML документації (make)",
            check=False
        )
    except FileNotFoundError:
        print("⚠️ Команда 'make' недоступна, використовуємо sphinx-build...")

    # Якщо make не працює, використовуємо sphinx-build напряму
    if not success:
        run_command(
            ["sphinx-build", "-b", "html", "-E", ".", "_build/html"],
            "Побудова HTML документації (sphinx-build)"
        )

    os.chdir("..")

    if os.path.exists("docs/_build/html/index.html"):
        print("✅ Документація успішно побудована!")
        print("📁 HTML файли знаходяться в: docs/_build/html/")
        print("🌐 Відкрийте docs/_build/html/index.html у браузері")
    else:
        print("❌ Помилка при побудові документації")
        print("🔍 Перевірте файл docs/conf.py та структуру проекту")

    return os.path.exists("docs/_build/html/index.html")


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
            "--port", "8080",
            "--open-browser"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Сервер зупинено")
    except FileNotFoundError:
        print("❌ sphinx-autobuild не знайдено. Встановіть його:")
        print("pip install sphinx-autobuild")
    finally:
        os.chdir("..")


def clean_docs():
    """Очищує існуючу документацію."""
    print("🧹 Очищення документації...")
    
    paths_to_clean = [
        "docs/_build",
        "docs/_static/__pycache__",
    ]
    
    for path in paths_to_clean:
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"✅ Очищено: {path}")
        else:
            print(f"⚠️ Шлях не існує: {path}")
    
    print("✅ Очищення завершено")


def validate_project_structure():
    """Перевіряє структуру проекту для документації."""
    print("🔍 Перевірка структури проекту...")
    
    required_paths = [
        "app",
        "app/main.py",
        "app/models",
        "app/crud",
        "app/services",
        "app/utils",
        "app/api"
    ]
    
    missing_paths = []
    for path in required_paths:
        if not os.path.exists(path):
            missing_paths.append(path)
    
    if missing_paths:
        print("❌ Відсутні необхідні файли/директорії:")
        for path in missing_paths:
            print(f"   - {path}")
        return False
    
    print("✅ Структура проекту корректна")
    return True


def create_env_template():
    """Створює шаблон .env файлу для документації."""
    print("📄 Створення .env.example...")
    
    env_template = '''# Database Configuration
DB_HOST=localhost
DB_PORT=5433
DB_NAME=contacts_db
DB_USER=contacts_user
DB_PASSWORD=contacts_password

# Security Configuration
SECRET_KEY=your-super-secret-jwt-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com

# Cloudinary Configuration
CLOUDINARY_NAME=your-cloudinary-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
CACHE_EXPIRE_MINUTES=15

# Rate Limiting
RATE_LIMIT_ME_ENDPOINT=10

# Application
APP_NAME=Contact Management API
APP_VERSION=2.0.0
DEBUG=true
'''
    
    if not os.path.exists(".env.example"):
        with open(".env.example", "w", encoding="utf-8") as f:
            f.write(env_template)
        print("✅ .env.example створено")
    else:
        print("⚠️ .env.example вже існує")


def show_next_steps():
    """Показує наступні кроки після налаштування."""
    print("\n" + "="*60)
    print("🎉 Налаштування документації завершено!")
    print("="*60)
    
    print("\n📋 Наступні кроки:")
    print("1. cd docs")
    print("2. make html                 # Побудувати документацію")
    print("3. make livehtml            # Запустити live reload сервер")
    print("4. open _build/html/index.html  # Відкрити в браузері")
    
    print("\n🔧 Корисні команди:")
    print("make clean                  # Очистити побудову")
    print("make linkcheck             # Перевірити посилання")
    print("make coverage              # Перевірити покриття документації")
    
    print("\n📝 Рекомендації:")
    print("• Додайте детальні docstring до всіх публічних функцій")
    print("• Використовуйте Google або NumPy стиль docstring")
    print("• Додайте приклади використання в docstring")
    print("• Регулярно оновлюйте документацію при змінах коду")
    
    print("\n🔗 Корисні посилання:")
    print("• Sphinx документація: https://www.sphinx-doc.org/")
    print("• reStructuredText: https://docutils.sourceforge.io/rst.html")
    print("• Napoleon (Google docstrings): https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html")


def main():
    """Головна функція."""
    parser = argparse.ArgumentParser(
        description="Налаштування Sphinx документації для Contact Management API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--clean", action="store_true", 
                       help="Очистити існуючу документацію")
    parser.add_argument("--build", action="store_true",
                       help="Побудувати документацію після налаштування")
    parser.add_argument("--serve", action="store_true",
                       help="Запустити сервер для перегляду")
    parser.add_argument("--validate", action="store_true",
                       help="Тільки перевірити структуру проекту")
    
    args = parser.parse_args()
    
    print("📚 Contact Management API - Налаштування документації")
    print("=" * 60)
    
    try:
        # Перевірка структури проекту
        if not validate_project_structure():
            print("❌ Неправильна структура проекту")
            sys.exit(1)
        
        if args.validate:
            print("✅ Структура проекту корректна")
            sys.exit(0)
        
        # Очищення якщо потрібно
        if args.clean:
            clean_docs()
        
        # Основне налаштування
        if not check_dependencies():
            print("\n🔧 Встановлення відсутніх залежностей...")
            install_docs_dependencies()
        
        create_docs_structure()
        create_sphinx_config()
        create_custom_css()
        create_index_page()
        create_api_documentation()
        create_modules_documentation()
        create_development_documentation()
        create_makefile()
        create_requirements_file()
        add_missing_docstrings()
        create_env_template()
        
        print("\n🎉 Базове налаштування документації завершено!")
        
        # Побудова якщо потрібно
        if args.build:
            success = build_documentation()
            if not success:
                print("❌ Помилка при побудові документації")
                print("🔍 Перевірте помилки вище та виправте їх")
        
        # Запуск сервера якщо потрібно
        if args.serve:
            if not args.build:
                print("🔄 Побудова документації перед запуском сервера...")
                build_documentation()
            serve_documentation()
        
        show_next_steps()
        
    except KeyboardInterrupt:
        print("\n❌ Налаштування перервано користувачем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Неочікувана помилка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Виправлений скрипт для автоматичного налаштування Sphinx документації
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
import textwrap


if __name__ == "__main__":
    main()

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
        ("sphinx", "sphinx"),
        ("sphinx_rtd_theme", "sphinx_rtd_theme"),
        ("myst-parser", "myst_parser"),
        ("sphinx-autobuild", "sphinx_autobuild"),
        ("sphinx-autodoc-typehints", "sphinx_autodoc_typehints")
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            missing_packages.append(package_name)
            print(f"❌ {package_name}")
    
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
        "docs/api",
        "docs/modules",
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
        "sphinx-autodoc-typehints>=1.24.0",
        "sphinx-autoapi>=3.0.0"
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
'''
    
    with open("docs/conf.py", "w", encoding="utf-8") as f:
        f.write(config_content)
    
    print("✅ Конфігурація Sphinx створена")


def create_custom_css():
    """Створює кастомний CSS файл."""
    print("🎨 Створення кастомного CSS...")
    
    css_content = '''/* Custom CSS for Contact Management API Documentation */

/* Загальні стилі */
.wy-nav-content {
    max-width: none;
}

/* Кольорова схема */
.wy-side-nav-search {
    background-color: #2980B9;
}

.wy-side-nav-search input[type=text] {
    border-color: #3498DB;
}

/* Покращення читабельності */
.rst-content .section > h1,
.rst-content .section > h2,
.rst-content .section > h3 {
    margin-bottom: 24px;
}

/* Стилі для code блоків */
.rst-content pre.literal-block,
.rst-content div[class^='highlight'] pre {
    font-size: 14px;
    line-height: 1.4;
}

/* Підсвітка важливих елементів */
.rst-content .admonition.note {
    background: #E8F4FD;
    border: 1px solid #3498DB;
}

.rst-content .admonition.warning {
    background: #FDF2E9;
    border: 1px solid #E67E22;
}

/* Покращення навігації */
.wy-menu-vertical li.current > a {
    background: #3498DB;
}

.wy-menu-vertical li.current a {
    border-right: 1px solid #3498DB;
}

/* API documentation improvements */
.rst-content dl:not(.docutils) dt {
    background: #f8f8f8;
    border-left: 3px solid #2980B9;
    padding: 12px;
    font-weight: bold;
}

/* Method signatures */
.rst-content .method dt,
.rst-content .function dt,
.rst-content .class dt {
    background: #f4f4f4;
    border-left: 4px solid #27AE60;
}

/* Parameters and return values */
.rst-content .field-list {
    margin-bottom: 24px;
}

.rst-content .field-name {
    background: #ECF0F1;
    padding: 4px 8px;
    border-radius: 3px;
    font-weight: bold;
    min-width: 100px;
}
'''
    
    with open("docs/_static/custom.css", "w", encoding="utf-8") as f:
        f.write(css_content)
    
    print("✅ Кастомний CSS створено")


def create_index_page():
    """Створює головну сторінку документації."""
    print("📄 Створення головної сторінки...")
    
    index_content = '''Contact Management API Documentation
=====================================

.. image:: https://img.shields.io/badge/version-2.0.0-blue.svg
   :alt: Version
   :target: #

.. image:: https://img.shields.io/badge/python-3.9+-green.svg
   :alt: Python Version

.. image:: https://img.shields.io/badge/FastAPI-0.104+-red.svg
   :alt: FastAPI Version

Ласкаво просимо до документації **Contact Management API** - повнофункціональної системи для управління контактами з JWT аутентифікацією, email верифікацією та багатьма іншими функціями.

🌟 Особливості
--------------

* **JWT аутентифікація** з автоматичним закінченням терміну дії
* **Email верифікація** користувачів
* **Управління контактами** з CRUD операціями
* **Завантаження аватарів** через Cloudinary
* **Rate limiting** для захисту API
* **Redis кешування** для покращення продуктивності
* **PostgreSQL** база даних з міграціями
* **Docker** контейнеризація
* **Повне тестове покриття** 75%+

📚 Зміст документації
---------------------

.. toctree::
   :maxdepth: 2
   :caption: 🚀 API Документація

   api/index
   api/authentication
   api/users
   api/contacts

.. toctree::
   :maxdepth: 2
   :caption: 📖 Код Документація

   modules/index
   modules/models
   modules/crud
   modules/services
   modules/utils

.. toctree::
   :maxdepth: 2
   :caption: 🛠️ Розробка

   development/index
   development/setup
   development/testing
   development/deployment

🚀 Швидкий старт
----------------

1. **Клонування проекту:**

.. code-block:: bash

   git clone <your-repo-url>
   cd contact-management-api

2. **Встановлення залежностей:**

.. code-block:: bash

   # Створити віртуальне середовище
   python -m venv venv
   
   # Активувати середовище (Windows)
   venv\\Scripts\\activate
   
   # Активувати середовище (Linux/Mac)
   source venv/bin/activate
   
   # Встановити залежності
   pip install -r requirements.txt

3. **Налаштування середовища:**

.. code-block:: bash

   # Скопіювати .env.example в .env
   cp .env.example .env
   
   # Редагувати змінні середовища
   nano .env

4. **Запуск бази даних:**

.. code-block:: bash

   # Запустити PostgreSQL та Redis
   docker-compose up -d

5. **Виконання міграцій:**

.. code-block:: bash

   # Застосувати міграції
   alembic upgrade head

6. **Запуск API:**

.. code-block:: bash

   # Запуск з auto-reload
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

🌐 Доступ до API
----------------

Після запуску API буде доступне за адресами:

* **API Docs (Swagger):** http://localhost:8000/docs
* **Alternative Docs (ReDoc):** http://localhost:8000/redoc  
* **PgAdmin:** http://localhost:8080

📊 Архітектура
--------------

Проект побудований за принципами **Clean Architecture** та використовує:

* **FastAPI** - сучасний веб-фреймворк для Python
* **SQLAlchemy** - ORM для роботи з базою даних
* **Pydantic** - валідація та серіалізація даних
* **Alembic** - міграції бази даних
* **JWT** - аутентифікація та авторизація
* **Redis** - кешування та сесії
* **Cloudinary** - зберігання зображень

🧪 Тестування
-------------

Проект має повне покриття тестами понад 75%:

.. code-block:: bash

   # Запустити всі тести
   make test
   
   # Запустити тільки модульні тести
   make test-unit
   
   # Запустити тільки інтеграційні тести  
   make test-integration
   
   # Згенерувати HTML звіт покриття
   make test-html

📝 Ліцензія
-----------

Цей проект розповсюджується під ліцензією MIT. Дивіться файл LICENSE для деталей.

Індекси та пошук
================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

---

**Автор:** AndyGrigs  
**Версія:** 2.0.0  
**Остання оновлення:** 2025-09-23
'''
    
    with open("docs/index.rst", "w", encoding="utf-8") as f:
        f.write(index_content)
    
    print("✅ Головна сторінка створена")


def create_api_documentation():
    """Створює документацію API."""
    print("📡 Створення API документації...")
    
    # API index
    api_index_content = '''API Документація
=================

Цей розділ містить повну документацію всіх API ендпоінтів Contact Management API.

.. toctree::
   :maxdepth: 2
   
   authentication
   users  
   contacts

Загальна інформація
-------------------

Base URL
~~~~~~~~

В локальному середовищі:

.. code-block:: text

   http://localhost:8000

Версіонування API
~~~~~~~~~~~~~~~~~~

Всі API ендпоінти мають префікс ``/api/v1/``

Аутентифікація
~~~~~~~~~~~~~~

API використовує JWT (JSON Web Tokens) для аутентифікації. Після успішного входу ви отримаєте токен, який потрібно передавати в заголовку ``Authorization``:

.. code-block:: text

   Authorization: Bearer YOUR_JWT_TOKEN

Формат відповідей
~~~~~~~~~~~~~~~~~

Всі відповіді API повертаються в JSON форматі:

.. code-block:: json

   {
     "field1": "value1",
     "field2": "value2"
   }

Обробка помилок
~~~~~~~~~~~~~~~

API повертає стандартні HTTP статус коди:

* ``200`` - Успішний запит
* ``201`` - Ресурс створено
* ``400`` - Некоректний запит
* ``401`` - Не авторизований
* ``403`` - Заборонено
* ``404`` - Не знайдено
* ``422`` - Помилка валідації
* ``429`` - Занадто багато запитів
* ``500`` - Внутрішня помилка сервера

Формат помилок:

.. code-block:: json

   {
     "detail": "Error description"
   }
'''
    
    with open("docs/api/index.rst", "w", encoding="utf-8") as f:
        f.write(api_index_content)
    
    # Authentication API
    auth_content = '''Аутентифікація API
==================

Ендпоінти для реєстрації, входу та управління аутентифікацією користувачів.

Реєстрація користувача
----------------------

Реєстрація нового користувача в системі.

.. http:post:: /api/v1/auth/register

   **Приклад запиту:**

   .. code-block:: json

      {
        "username": "johndoe",
        "email": "john@example.com", 
        "password": "SecurePassword123!"
      }

   **Приклад відповіді:**

   .. code-block:: json

      {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "role": "user", 
        "is_verified": false,
        "created_at": "2025-09-23T10:30:00Z"
      }

   :reqjson string username: Ім'я користувача (3-50 символів)
   :reqjson string email: Email адреса
   :reqjson string password: Пароль (мінімум 6 символів)
   :reqjson string role: Роль користувача (опціонально)
   
   :statuscode 201: Користувач успішно створений
   :statuscode 409: Email або username вже зайняті
   :statuscode 422: Некоректні дані

Реєстрація адміністратора
-------------------------

.. http:post:: /api/v1/auth/register-admin

   Спеціальний ендпоінт для створення користувача з роллю admin.

Вхід користувача
----------------

.. http:post:: /api/v1/auth/login

   **Приклад запиту:**

   .. code-block:: json

      {
        "email": "john@example.com",
        "password": "SecurePassword123!"
      }

   **Приклад відповіді:**

   .. code-block:: json

      {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "token_type": "bearer"
      }

   :reqjson string email: Email адреса
   :reqjson string password: Пароль
   
   :statuscode 200: Успішний вхід
   :statuscode 401: Неправильні credentials

Верифікація Email
-----------------

.. http:get:: /api/v1/auth/verify-email

   Верифікує email адресу користувача за токеном.

   :query token: Токен верифікації з email

Повторна відправка верифікації
------------------------------

.. http:post:: /api/v1/auth/resend-verification

   :query email: Email адреса для повторної відправки

Скидання пароля
---------------

.. http:post:: /api/v1/auth/forgot-password

   Запит на скидання пароля.

.. http:post:: /api/v1/auth/reset-password

   Скидання пароля за токеном.

.. http:get:: /api/v1/auth/verify-reset-token

   Перевірка валідності токена скидання пароля.
'''
    
    with open("docs/api/authentication.rst", "w", encoding="utf-8") as f:
        f.write(auth_content)
    
    # Users API
    users_content = '''Користувачі API
===============

Ендпоінти для управління профілями користувачів.

Отримання поточного користувача
-------------------------------

.. http:get:: /api/v1/users/me

   **Заголовки:**

   .. code-block:: text

      Authorization: Bearer YOUR_JWT_TOKEN

   **Приклад відповіді:**

   .. code-block:: json

      {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "avatar_url": "https://cloudinary.com/avatar.jpg",
        "role": "user",
        "is_verified": true,
        "created_at": "2025-09-23T10:30:00Z"
      }

   :statuscode 200: Успішно
   :statuscode 401: Не авторизований
   :statuscode 400: Email не верифікований

   .. note::
      Цей ендпоінт має rate limiting: максимум 10 запитів на хвилину.

Завантаження аватара
--------------------

.. http:post:: /api/v1/users/me/avatar

   **Тільки для адміністраторів**

   Завантажує аватар користувача в Cloudinary.

   :form file: Файл зображення (максимум 5MB)

   :statuscode 200: Аватар завантажено
   :statuscode 400: Некоректний файл або занадто великий
   :statuscode 403: Потрібні права адміністратора

Зміна ролі користувача
----------------------

.. http:patch:: /api/v1/users/{user_id}/role

   **Тільки для адміністраторів**

   **Приклад запиту:**

   .. code-block:: json

      {
        "role": "admin"
      }

   :param user_id: ID користувача
   :reqjson string role: Нова роль (user/admin)

   :statuscode 200: Роль змінена
   :statuscode 400: Адмін не може понизити себе
   :statuscode 403: Потрібні права адміністратора
   :statuscode 404: Користувач не знайдений
'''
    
    with open("docs/api/users.rst", "w", encoding="utf-8") as f:
        f.write(users_content)
    
    # Contacts API
    contacts_content = '''Контакти API
============

Ендпоінти для управління контактами користувачів.

Створення контакту
------------------

.. http:post:: /api/v1/contacts/

   **Приклад запиту:**

   .. code-block:: json

      {
        "first_name": "Іван",
        "last_name": "Петренко",
        "email": "ivan@example.com", 
        "phone_number": "+380501234567",
        "birth_date": "1990-05-15",
        "additional_data": "Друг з університету"
      }

   **Приклад відповіді:**

   .. code-block:: json

      {
        "id": 1,
        "first_name": "Іван",
        "last_name": "Петренко", 
        "email": "ivan@example.com",
        "phone_number": "+380501234567",
        "birth_date": "1990-05-15",
        "additional_data": "Друг з університету",
        "owner_id": 1
      }

   :reqjson string first_name: Ім'я (обов'язкове)
   :reqjson string last_name: Прізвище (обов'язкове)
   :reqjson string email: Email адреса (унікальна)
   :reqjson string phone_number: Номер телефону
   :reqjson string birth_date: Дата народження (YYYY-MM-DD)
   :reqjson string additional_data: Додаткові дані (опціонально)

   :statuscode 201: Контакт створено
   :statuscode 400: Email вже існує або некоректні дані
   :statuscode 401: Не авторизований

Отримання списку контактів
--------------------------

.. http:get:: /api/v1/contacts/

   :query skip: Кількість записів для пропуску (за замовчуванням 0)
   :query limit: Максимальна кількість записів (за замовчуванням 100)
   :query search: Пошук за іменем, прізвищем або email

   **Приклад з пошуком:**

   .. code-block:: text

      GET /api/v1/contacts/?search=Іван&skip=0&limit=10

Отримання контакту за ID
------------------------

.. http:get:: /api/v1/contacts/{contact_id}

   :param contact_id: ID контакту

   :statuscode 200: Контакт знайдено
   :statuscode 404: Контакт не знайдено

Оновлення контакту
------------------

.. http:put:: /api/v1/contacts/{contact_id}

   **Приклад запиту:**

   .. code-block:: json

      {
        "first_name": "Іван",
        "additional_data": "Оновлені дані"
      }

   :param contact_id: ID контакту

Видалення контакту
------------------

.. http:delete:: /api/v1/contacts/{contact_id}

   :param contact_id: ID контакту

   **Приклад відповіді:**

   .. code-block:: json

      {
        "message": "Contact deleted successfully!"
      }

Дні народження
--------------

.. http:get:: /api/v1/contacts/birthdays/

   Повертає контакти з днями народження на найближчі 7 днів.

   **Приклад відповіді:**

   .. code-block:: json

      [
        {
          "id": 1,
          "first_name": "Марія",
          "last_name": "Коваленко",
          "birth_date": "1985-12-25",
          "email": "maria@example.com"
        }
      ]
'''
    
    with open("docs/api/contacts.rst", "w", encoding="utf-8") as f:
        f.write(contacts_content)
    
    print("✅ API документація створена")


def create_modules_documentation():
    """Створює документацію модулів."""
    print("📦 Створення документації модулів...")
    
    # Modules index
    modules_index_content = '''Документація модулів
====================

Цей розділ містить автоматично згенеровану документацію всіх модулів проекту.

.. toctree::
   :maxdepth: 2
   
   models
   crud
   services
   utils

Структура проекту
-----------------

.. code-block:: text

   app/
   ├── main.py                 # Головний файл додатку
   ├── config.py              # Налаштування
   ├── api/                    # API роутери
   │   ├── deps.py            # Залежності
   │   └── v1/                # API версії 1
   │       ├── api.py         # Головний роутер
   │       └── endpoints/     # Ендпоінти
   ├── models/                # SQLAlchemy моделі
   │   ├── users.py           # Модель користувачів
   │   └── contacts.py        # Модель контактів
   ├── schemas/               # Pydantic схеми
   │   ├── users.py           # Схеми користувачів
   │   └── contacts.py        # Схеми контактів
   ├── crud/                  # CRUD операції
   │   ├── users.py           # CRUD користувачів
   │   └── contacts.py        # CRUD контактів
   ├── services/              # Бізнес логіка
   │   ├── email.py           # Email сервіс
   │   ├── redis.py           # Redis кешування
   │   └── cloudinary.py      # Завантаження файлів
   ├── middleware/            # Middleware
   │   ├── auth.py            # Аутентифікація
   │   └── rate_limiter.py    # Rate limiting
   ├── utils/                 # Утиліти
   │   └── auth.py            # JWT утиліти
   └── database/              # База даних
       ├── base.py            # Базовий клас
       └── connection.py      # З'єднання
'''
    
    with open("docs/modules/index.rst", "w", encoding="utf-8") as f:
        f.write(modules_index_content)
    
    # Models documentation
    models_content = '''Моделі бази даних
==================

SQLAlchemy моделі для роботи з базою даних.

.. automodule:: app.models.users
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: app.models.contacts
   :members:
   :undoc-members:
   :show-inheritance:

Перечислення (Enums)
--------------------

.. autoclass:: app.models.users.UserRole
   :members:
   :undoc-members:

Основні моделі
--------------

Модель користувача
~~~~~~~~~~~~~~~~~~

.. autoclass:: app.models.users.User
   :members:
   :undoc-members:
   :show-inheritance:

Модель контакту
~~~~~~~~~~~~~~~

.. autoclass:: app.models.contacts.Contact
   :members:
   :undoc-members:
   :show-inheritance:
'''
    
    with open("docs/modules/models.rst", "w", encoding="utf-8") as f:
        f.write(models_content)
    
    # CRUD documentation
    crud_content = '''CRUD операції
==============

Модулі для виконання операцій Create, Read, Update, Delete з базою даних.

Користувачі CRUD
----------------

.. automodule:: app.crud.users
   :members:
   :undoc-members:
   :show-inheritance:

Контакти CRUD
-------------

.. automodule:: app.crud.contacts
   :members:
   :undoc-members:
   :show-inheritance:

Основні функції
---------------

Управління користувачами
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: app.crud.users.get_user_by_email
.. autofunction:: app.crud.users.create_user
.. autofunction:: app.crud.users.authenticate_user
.. autofunction:: app.crud.users.verify_user_email

Управління контактами
~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: app.crud.contacts.get_contacts
.. autofunction:: app.crud.contacts.create_contact
.. autofunction:: app.crud.contacts.update_contact
.. autofunction:: app.crud.contacts.delete_contact
.. autofunction:: app.crud.contacts.get_contacts_with_upcoming_birthdays
'''
    
    with open("docs/modules/crud.rst", "w", encoding="utf-8") as f:
        f.write(crud_content)
    
    # Services documentation
    services_content = '''Сервіси
========

Модулі для роботи з зовнішніми сервісами та бізнес-логікою.

Email сервіс
------------

.. automodule:: app.services.email
   :members:
   :undoc-members:
   :show-inheritance:

Redis кешування
----------------

.. automodule:: app.services.redis
   :members:
   :undoc-members:
   :show-inheritance:

Cloudinary сервіс
-----------------

.. automodule:: app.services.cloudinary
   :members:
   :undoc-members:
   :show-inheritance:

Cache утиліти
-------------

.. automodule:: app.services.cache_utils
   :members:
   :undoc-members:

Основні класи та функції
------------------------

RedisService
~~~~~~~~~~~~

.. autoclass:: app.services.redis.RedisService
   :members:
   :undoc-members:

Функції Cloudinary
~~~~~~~~~~~~~~~~~~

.. autofunction:: app.services.cloudinary.upload_avatar
.. autofunction:: app.services.cloudinary.delete_avatar

Email функції
~~~~~~~~~~~~~

.. autofunction:: app.services.email.send_verification_email
.. autofunction:: app.services.email.send_password_reset_email
'''
    
    with open("docs/modules/services.rst", "w", encoding="utf-8") as f:
        f.write(services_content)
    
    # Utils documentation
    utils_content = '''Утиліти
========

Допоміжні модулі та функції.

Аутентифікація утиліти
----------------------

.. automodule:: app.utils.auth
   :members:
   :undoc-members:
   :show-inheritance:

Основні функції
---------------

Робота з паролями
~~~~~~~~~~~~~~~~~

.. autofunction:: app.utils.auth.get_password_hash
.. autofunction:: app.utils.auth.verify_password

JWT токени
~~~~~~~~~~

.. autofunction:: app.utils.auth.create_access_token
.. autofunction:: app.utils.auth.verify_token

Токени верифікації
~~~~~~~~~~~~~~~~~~

.. autofunction:: app.utils.auth.generate_verification_token
.. autofunction:: app.utils.auth.generate_reset_password_token
.. autofunction:: app.utils.auth.create_reset_password_token
.. autofunction:: app.utils.auth.verify_reset_password_token
'''
    
    with open("docs/modules/utils.rst", "w", encoding="utf-8") as f:
        f.write(utils_content)
    
    print("✅ Документація модулів створена")


def create_development_documentation():
    """Створює документацію для розробників."""
    print("🛠️ Створення документації для розробників...")
    
    # Development index
    dev_index_content = '''Документація для розробників
===============================

Цей розділ містить інформацію для розробників про налаштування, тестування та деплой проекту.

.. toctree::
   :maxdepth: 2
   
   setup
   testing
   deployment

Загальна інформація
-------------------

Цей проект використовує сучасний Python стек:

* **FastAPI** - веб-фреймворк
* **SQLAlchemy** - ORM
* **Alembic** - міграції бази даних
* **Pytest** - тестування
* **Docker** - контейнеризація
* **Redis** - кешування
* **PostgreSQL** - база даних

Вимоги до середовища розробки
-----------------------------

* Python 3.9+
* Docker та Docker Compose
* Git
* Текстовий редактор або IDE (рекомендується VS Code або PyCharm)

Рекомендована структура розробки
-------------------------------

1. Створити віртуальне середовище
2. Встановити залежності
3. Налаштувати змінні середовища
4. Запустити базу даних через Docker
5. Виконати міграції
6. Запустити тести
7. Запустити сервер розробки
'''
    
    with open("docs/development/index.rst", "w", encoding="utf-8") as f:
        f.write(dev_index_content)
    
    # Setup documentation
    setup_content = '''Налаштування середовища розробки
===================================

Детальна інструкція по налаштуванню проекту для розробки.

Попередні вимоги
----------------

Перед початком роботи переконайтеся, що у вас встановлені:

* Python 3.9 або вище
* Git
* Docker та Docker Compose
* pip та venv

Крок 1: Клонування репозиторію
-------------------------------

.. code-block:: bash

   git clone <your-repo-url>
   cd contact-management-api

Крок 2: Створення віртуального середовища
------------------------------------------

.. code-block:: bash

   # Створення віртуального середовища
   python -m venv venv

   # Активація (Windows)
   venv\\Scripts\\activate

   # Активація (Linux/Mac)  
   source venv/bin/activate

Крок 3: Встановлення залежностей
---------------------------------

.. code-block:: bash

   # Основні залежності
   pip install -r requirements.txt

   # Залежності для тестування (опціонально)
   pip install -r requirements-test.txt

Крок 4: Налаштування змінних середовища
----------------------------------------

.. code-block:: bash

   # Скопіюйте приклад файлу
   cp .env.example .env

   # Відредагуйте файл .env
   nano .env

Приклад .env файлу:

.. code-block:: text

   # Database
   DB_HOST=localhost
   DB_PORT=5433
   DB_NAME=contacts_db
   DB_USER=contacts_user
   DB_PASSWORD=contacts_password

   # Security
   SECRET_KEY=your-super-secret-jwt-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # Email Configuration
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_FROM=your-email@gmail.com
   MAIL_PORT=587
   MAIL_SERVER=smtp.gmail.com

   # Cloudinary
   CLOUDINARY_NAME=your-cloudinary-name
   CLOUDINARY_API_KEY=your-api-key
   CLOUDINARY_API_SECRET=your-api-secret

   # Redis
   REDIS_HOST=localhost
   REDIS_PORT=6379

Крок 5: Запуск сервісів
------------------------

.. code-block:: bash

   # Запуск PostgreSQL, Redis та PgAdmin
   docker-compose up -d

   # Перевірка статусу
   docker-compose ps

Крок 6: Виконання міграцій
---------------------------

.. code-block:: bash

   # Застосування міграцій
   alembic upgrade head

   # Створення нової міграції (за потреби)
   alembic revision --autogenerate -m "Опис змін"

Крок 7: Запуск сервера розробки
--------------------------------

.. code-block:: bash

   # Запуск з auto-reload
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Корисні команди
---------------

.. code-block:: bash

   # Перевірка здоров'я API
   curl http://localhost:8000/health

   # Доступ до API документації
   open http://localhost:8000/docs

   # Доступ до PgAdmin
   open http://localhost:8080

   # Перегляд логів Docker
   docker-compose logs -f

Налаштування IDE
----------------

VS Code
~~~~~~~

Рекомендовані розширення:

* Python
* Pylance  
* Python Docstring Generator
* REST Client
* Docker

Налаштування .vscode/settings.json:

.. code-block:: json

   {
       "python.defaultInterpreterPath": "./venv/bin/python",
       "python.linting.enabled": true,
       "python.linting.pylintEnabled": true,
       "python.formatting.provider": "black",
       "python.testing.pytestEnabled": true,
       "python.testing.pytestArgs": ["tests/"]
   }

PyCharm
~~~~~~~

1. Налаштуйте Python інтерпретатор на віртуальне середовище
2. Встановіть pytest як test runner
3. Налаштуйте автоматичне форматування з black
'''
    
    with open("docs/development/setup.rst", "w", encoding="utf-8") as f:
        f.write(setup_content)
    
    # Testing documentation (скорочена версія з TESTING.md)
    testing_content = '''Тестування
==========

Інструкції по запуску та підтримці тестів.

Швидкий старт
-------------

.. code-block:: bash

   # Встановити тестові залежності
   make install-test-deps

   # Запустити всі тести
   make test

   # Тільки модульні тести
   make test-unit

   # Тільки інтеграційні тести
   make test-integration

Структура тестів
----------------

.. code-block:: text

   tests/
   ├── conftest.py              # Конфігурація та фікстури
   ├── unit/                    # Модульні тести
   │   ├── test_crud_users.py
   │   ├── test_crud_contacts.py
   │   └── test_utils_auth.py
   └── integration/             # Інтеграційні тести
       ├── test_api_auth.py
       ├── test_api_users.py
       └── test_api_contacts.py

Покриття тестами
----------------

Проект має покриття тестами понад 75%:

.. code-block:: bash

   # Генерація HTML звіту покриття
   make test-html

   # Перегляд звіту
   open htmlcov/index.html

Написання тестів
----------------

Приклад модульного тесту:

.. code-block:: python

   @pytest.mark.unit
   def test_create_user(db_session):
       user_data = UserCreate(
           username="testuser",
           email="test@example.com", 
           password="password123"
       )
       
       user = create_user(db_session, user_data)
       
       assert user.username == "testuser"
       assert user.email == "test@example.com"

Приклад інтеграційного тесту:

.. code-block:: python

   @pytest.mark.integration
   def test_create_contact_api(client, auth_headers):
       contact_data = {
           "first_name": "Іван",
           "last_name": "Петренко",
           "email": "ivan@example.com"
       }
       
       response = client.post(
           "/api/v1/contacts/",
           json=contact_data,
           headers=auth_headers
       )
       
       assert response.status_code == 201
'''
    
    with open("docs/development/testing.rst", "w", encoding="utf-8") as f:
        f.write(testing_content)
    
    # Deployment documentation
    deployment_content = '''Деплой
======

Інструкції по деплою Contact Management API в продакшн.

Docker деплой
-------------

Проект підготовлений для деплою через Docker:

.. code-block:: bash

   # Побудова Docker образу
   docker build -t contact-management-api .

   # Запуск продакшн композиції
   docker-compose -f docker-compose.prod.yaml up -d

Змінні середовища для продакшн
-------------------------------

.. code-block:: text

   DEBUG=false
   SECRET_KEY=super-secure-production-key-256-bit
   ACCESS_TOKEN_EXPIRE_MINUTES=15
   DB_PASSWORD=secure-production-password

Nginx конфігурація
------------------

.. code-block:: nginx

   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }

Моніторинг
----------

Використовуйте ендпоінт для health checks:

.. code-block:: bash

   curl http://your-domain.com/health

SSL/TLS
-------

Рекомендується використовувати Let's Encrypt для безкоштовних SSL сертифікатів.
'''
    
    with open("docs/development/deployment.rst", "w", encoding="utf-8") as f:
        f.write(deployment_content)
    
    print("✅ Документація для розробників створена")


def create_makefile():
    """Створює Makefile для документації."""
    print("🔨 Створення Makefile...")
    
    makefile_content = '''# Makefile for Sphinx documentation

SPHINXOPTS    ?=
SPHINXBUILD  ?= sphinx-build
SOURCEDIR    = .
BUILDDIR     = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile clean html livehtml

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Clean build directory
clean:
	rm -rf $(BUILDDIR)/*

# Build HTML documentation
html:
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS)
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

# Live reload for development
livehtml:
	sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)/html" \
		--host 0.0.0.0 \
		--port 8080 \
		--open-browser \
		$(SPHINXOPTS)

# Clean build and rebuild
cleanhtml: clean html

# Build and open in browser  
open: html
	@python -c "import webbrowser; webbrowser.open('$(BUILDDIR)/html/index.html')"

# Check for broken links
linkcheck:
	@$(SPHINXBUILD) -b linkcheck "$(SOURCEDIR)" "$(BUILDDIR)/linkcheck" $(SPHINXOPTS)
	@echo
	@echo "Link check complete; look for any errors in the above output " \\
	      "or in $(BUILDDIR)/linkcheck/output.txt."

# Build PDF (requires LaTeX)
pdf:
	@$(SPHINXBUILD) -b latex "$(SOURCEDIR)" "$(BUILDDIR)/latex" $(SPHINXOPTS)
	@make -C $(BUILDDIR)/latex all-pdf
	@echo
	@echo "Build finished; the PDF files are in $(BUILDDIR)/latex."

# Check documentation health
doctest:
	@$(SPHINXBUILD) -b doctest "$(SOURCEDIR)" "$(BUILDDIR)/doctest" $(SPHINXOPTS)
	@echo "Testing of doctests in the sources finished, look at the " \\
	      "results in $(BUILDDIR)/doctest/output.txt."

# Coverage check
coverage:
	@$(SPHINXBUILD) -b coverage "$(SOURCEDIR)" "$(BUILDDIR)/coverage" $(SPHINXOPTS)
	@echo "Testing of coverage in the sources finished, look at the " \\
	      "results in $(BUILDDIR)/coverage/python.txt."
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
sphinx-autoapi>=3.0.0
myst-parser>=2.0.0
sphinx-autobuild>=2021.3.14
sphinx-copybutton>=0.5.2
sphinxext-opengraph>=0.9.0
typing-extensions>=4.8.0
'''
    
    with open("docs/requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements_content)
    
    print("✅ requirements.txt створено")


def add_missing_docstrings():
    """Додає відсутні docstring до основних файлів."""
    print("📝 Додання відсутніх docstring...")
    
    # Це функція-заглушка - в реальності потрібно було б модифікувати файли
    # Але це складно зробити в межах цього скрипта
    print("⚠️ Необхідно вручну додати docstring до файлів:")
    print("   - app/main.py (функції root, health_check, тощо)")
    print("   - app/api/v1/endpoints/*.py (функції API endpoints)")
    print("   - app/config.py (клас Settings)")
    
    # Показуємо приклад docstring
    example_docstring = '''
    Приклад docstring для API endpoint:
    
    def create_contact(contact: ContactCreate, current_user: User = Depends(get_current_verified_user)):
        """
        Створює новий контакт для поточного користувача.
        
        Args:
            contact (ContactCreate): Дані для створення контакту
            current_user (User): Поточний авторизований користувач
            
        Returns:
            ContactResponse: Створений контакт з ID та owner_id
            
        Raises:
            HTTPException: 400 якщо email вже існує
            HTTPException: 422 якщо дані невалідні
            
        Example:
            >>> contact_data = ContactCreate(
            ...     first_name="Іван",
            ...     last_name="Петренко",
            ...     email="ivan@example.com"
            ... )
            >>> contact = create_contact(contact_data, current_user)
            >>> contact.id
            1
        """
    '''
    
    print(example_docstring)
    print("✅ Інструкції для docstring створені")