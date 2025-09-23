Contact Management API Documentation
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
