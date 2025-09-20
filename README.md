# 🚀 Contact Management API з JWT аутентифікацією

REST API для управління контактами з повноцінною системою JWT аутентифікації, email верифікацією та завантаженням аватарів.

## 📁 Структура проекту

```
contacts-api/
├── app/
│   ├── main.py                 # Головний файл додатку
│   ├── config.py              # Налаштування
│   ├── api/
│   │   ├── deps.py            # Залежності
│   │   └── v1/
│   │       ├── api.py         # API роутер v1
│   │       └── endpoints/
│   │           ├── auth.py    # Аутентифікація
│   │           ├── users.py   # Користувачі
│   │           └── contacts.py # Контакти
│   ├── database/
│   │   ├── base.py            # Базовий клас моделей
│   │   └── connection.py      # З'єднання з БД
│   ├── models/
│   │   ├── users.py           # Модель користувачів
│   │   └── contacts.py        # Модель контактів
│   ├── schemas/
│   │   ├── users.py           # Pydantic схеми користувачів
│   │   └── contacts.py        # Pydantic схеми контактів
│   ├── crud/
│   │   ├── users.py           # CRUD користувачів
│   │   └── contacts.py        # CRUD контактів
│   ├── middleware/
│   │   ├── auth.py            # JWT middleware
│   │   └── rate_limiter.py    # Rate limiting
│   ├── services/
│   │   ├── email.py           # Email сервіс
│   │   └── cloudinary.py      # Cloudinary сервіс
│   └── utils/
│       └── auth.py            # JWT утиліти
├── alembic/                   # Database migrations
├── .env                       # Змінні середовища
├── .gitignore                # Git ігнорування
├── docker-compose.yaml       # Docker композиція
├── init.sql                  # Ініціалізація БД
├── requirements.txt          # Python залежності
└── README.md                 # Цей файл
```

## 🚀 Швидкий старт

### Крок 1: Встановлення залежностей

```bash
# Клонуйте репозиторій
git clone <your-repo-url>
cd contacts-api

# Створіть віртуальне середовище
python -m venv venv

# Активуйте середовище
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Встановіть залежності
pip install -r requirements.txt
```

### Крок 2: Налаштування середовища

Скопіюйте `.env.example` в `.env` та налаштуйте змінні:

```env
# Database
DB_HOST=localhost
DB_PORT=5433
DB_NAME=contacts_db
DB_USER=contacts_user
DB_PASSWORD=contacts_password

# Security
SECRET_KEY=your-super-secret-jwt-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration (налаштуйте для відправки email)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com

# Cloudinary (налаштуйте для завантаження аватарів)
CLOUDINARY_NAME=your-cloudinary-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Rate Limiting
RATE_LIMIT_ME_ENDPOINT=10
```

### Крок 3: Запуск бази даних

```bash
# Запустіть PostgreSQL та PgAdmin через Docker
docker-compose up -d

# Перевірте статус контейнерів
docker-compose ps

# Перегляньте логи (за потреби)
docker-compose logs db
```

### Крок 4: Виконання міграцій

```bash
# Створіть міграцію (якщо потрібно)
alembic revision --autogenerate -m "Add users and update contacts"

# Застосуйте міграції
alembic upgrade head
```

### Крок 5: Запуск API

```bash
# З кореня проекту
python -m app.main

# Або через uvicorn з auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 Доступ до додатку

- **API Docs (Swagger):** http://localhost:8000/docs
- **Alternative Docs (ReDoc):** http://localhost:8000/redoc  
- **PgAdmin:** http://localhost:8080 (admin@example.com / admin123)

## 📝 API Ендпоінти

### 🔐 Аутентифікація (`/api/v1/auth/`)
| Метод | URL | Опис | Статус |
|-------|-----|------|--------|
| POST | `/register` | Реєстрація користувача | 201 |
| POST | `/login` | Вхід користувача | 200 |
| GET | `/verify-email` | Верифікація email | 200 |
| POST | `/resend-verification` | Повторна відправка email | 200 |

### 👤 Користувачі (`/api/v1/users/`)
| Метод | URL | Опис | Авторизація |
|-------|-----|------|-------------|
| GET | `/me` | Профіль користувача | Required |
| PATCH | `/me` | Оновлення профілю | Required |
| POST | `/me/avatar` | Завантаження аватара | Required |

### 📞 Контакти (`/api/v1/contacts/`)
| Метод | URL | Опис | Авторизація |
|-------|-----|------|-------------|
| POST | `/` | Створити контакт | Required |
| GET | `/` | Список контактів | Required |
| GET | `/{id}` | Контакт за ID | Required |
| PUT | `/{id}` | Оновити контакт | Required |
| DELETE | `/{id}` | Видалити контакт | Required |
| GET | `/birthdays/` | Дні народження (7 днів) | Required |

## 🔧 Приклади використання

### Реєстрація користувача
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePassword123!"
  }'
```

### Вхід користувача
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePassword123!"
  }'
```

### Створення контакту (з токеном)
```bash
curl -X POST "http://localhost:8000/api/v1/contacts/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "first_name": "Іван",
    "last_name": "Петренко",
    "email": "ivan@example.com",
    "phone_number": "+380501234567",
    "birth_date": "1990-12-25",
    "additional_data": "Друг з університету"
  }'
```

### Завантаження аватара
```bash
curl -X POST "http://localhost:8000/api/v1/users/me/avatar" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@avatar.jpg"
```

## 🔍 Функції пошуку та фільтрації

```bash
# Пошук за іменем, прізвищем або email
GET /api/v1/contacts/?search=Іван

# Пагінація
GET /api/v1/contacts/?skip=0&limit=10

# Комбінований запит
GET /api/v1/contacts/?search=петренко&skip=0&limit=5
```

## 🗄️ Налаштування PgAdmin

1. Відкрийте http://localhost:8080
2. Увійдіть з credentials:
   - **Email:** admin@example.com
   - **Password:** admin123
3. Додайте сервер:
   - **Name:** Contacts DB
   - **Host:** db (назва Docker сервісу!)
   - **Port:** 5432 (внутрішній Docker порт)
   - **Database:** contacts_db
   - **Username:** contacts_user
   - **Password:** contacts_password

## 🎯 Реалізовані функції

### ✅ Безпека та аутентифікація
- **JWT токени** з автоматичним закінченням терміну дії
- **Bcrypt хешування** паролів
- **Email верифікація** з токенами
- **Rate limiting** (10 запитів/хв до /me)
- **CORS** підтримка
- **Middleware** для автоматичної перевірки токенів

### ✅ Управління даними
- **Приватні контакти** - кожен користувач бачить тільки свої
- **CRUD операції** для контактів
- **Пошук та фільтрація**
- **Дні народження** на найближчі 7 днів
- **Валідація** даних з Pydantic

### ✅ Інтеграції
- **Cloudinary** для зберігання аватарів
- **Email сервіс** для верифікації
- **PostgreSQL** з міграціями Alembic
- **Docker** контейнеризація

### ✅ Моніторинг та документація
- **Swagger UI** автоматична документація
- **Health checks** для моніторингу
- **Structured logging**
- **PgAdmin** для управління БД

## 🛠️ Корисні команди

### Docker управління
```bash
# Запуск сервісів
docker-compose up -d

# Зупинка контейнерів
docker-compose down

# Зупинка з видаленням даних
docker-compose down -v

# Перезапуск бази даних
docker-compose restart db

# Перегляд логів
docker-compose logs -f db
```

### Database управління
```bash
# Створення міграції
alembic revision --autogenerate -m "Description"

# Застосування міграцій
alembic upgrade head

# Підключення до PostgreSQL
docker exec -it contacts_db psql -U contacts_user -d contacts_db

# Перегляд таблиць
docker exec -it contacts_db psql -U contacts_user -d contacts_db -c "\dt"
```

### Відладка
```bash
# Перевірка здоров'я API
curl http://localhost:8000/health

# Перевірка статусу контейнерів
docker-compose ps

# Перегляд логів API
python -m app.main
```

## 🐛 Розв'язання проблем

### "Connection refused" до PostgreSQL
```bash
# Перевірте контейнери
docker-compose ps

# Перезапустіть базу
docker-compose restart db

# Перевірте порт в .env (має бути 5433)
```

### "JWT token invalid"
```bash
# Перевірте SECRET_KEY в .env
# Отримайте новий токен через /auth/login
# Використовуйте формат: "Bearer YOUR_TOKEN"
```

### "Email not verified"
```bash
# Перевірте email конфігурацію в .env
# Використайте /auth/resend-verification
# Або примусово верифікуйте в базі даних
```

### "Rate limit exceeded"
```bash
# Зачекайте 1 хвилину
# Або збільште RATE_LIMIT_ME_ENDPOINT в .env
```

## 📊 Тестові дані

Система автоматично створює тестового користувача:
- **Email:** test@example.com
- **Password:** testpassword
- **Username:** testuser
- **Verified:** true

## 🚀 Продакшн деплой

### Змінні для продакшн
```env
DEBUG=false
SECRET_KEY=super-secure-production-key-256-bit
ACCESS_TOKEN_EXPIRE_MINUTES=15
DB_PASSWORD=secure-production-password
```

### Docker Compose для продакшн
```bash
docker-compose -f docker-compose.prod.yaml up -d
```

## 📋 TODO / Майбутні покращення

- [ ] OAuth2 провайдери (Google, GitHub)
- [ ] WebSocket підтримка для real-time
- [ ] API versioning
- [ ] Automated testing suite
- [ ] Kubernetes deployment
- [ ] Redis для сесій
- [ ] Elasticsearch для пошуку
- [ ] Webhook підтримка

---

**Автор:** Ваше ім'я  
**Версія:** 2.0.0 (з JWT аутентифікацією)  
**Tech Stack:** FastAPI, PostgreSQL, JWT, Cloudinary, Docker  
**Python:** 3.11+  
**FastAPI:** 0.104.1