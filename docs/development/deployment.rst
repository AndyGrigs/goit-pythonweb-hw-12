Деплой
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
