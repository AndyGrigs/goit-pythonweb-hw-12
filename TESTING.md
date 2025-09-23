# 🧪 Тестування Contact Management API

Цей документ описує як запускати та підтримувати тести для Contact Management API. Проект має повне покриття тестами понад 75% та включає модульні та інтеграційні тести.

## 📋 Зміст

- [Швидкий старт](#швидкий-старт)
- [Структура тестів](#структура-тестів)
- [Типи тестів](#типи-тестів)
- [Способи запуску](#способи-запуску)
- [Покриття тестами](#покриття-тестами)
- [Налаштування CI/CD](#налаштування-cicd)
- [Розробка тестів](#розробка-тестів)
- [Troubleshooting](#troubleshooting)

## 🚀 Швидкий старт

### 1. Встановлення залежностей

```bash
# Встановити основні залежності
pip install -r requirements.txt

# Встановити тестові залежності
pip install -r requirements-test.txt

# Або використати make
make install-test-deps
```

### 2. Запуск всіх тестів

```bash
# Простий запуск
make test

# Або безпосередньо через pytest
python -m pytest tests/ --cov=app --cov-report=html --cov-fail-under=75 -v
```

### 3. Перегляд результатів

Після запуску тестів відкрийте `htmlcov/index.html` у браузері для перегляду звіту покриття.

## 📁 Структура тестів

```
tests/
├── conftest.py                 # Конфігурація pytest та фікстури
├── unit/                       # Модульні тести
│   ├── test_crud_users.py      # Тести CRUD користувачів
│   ├── test_crud_contacts.py   # Тести CRUD контактів
│   ├── test_utils_auth.py      # Тести утиліт аутентифікації
│   ├── test_middleware_auth.py # Тести middleware
│   └── test_services.py        # Тести сервісів
├── integration/                # Інтеграційні тести
│   ├── test_api_auth.py        # Тести API аутентифікації
│   ├── test_api_users.py       # Тести API користувачів
│   └── test_api_contacts.py    # Тести API контактів
└── test_init.sql              # SQL для тестової бази
```

## 🔬 Типи тестів

### Модульні тести (`@pytest.mark.unit`)
- Тестують окремі функції та методи
- Не потребують зовнішніх залежностей
- Швидкі та ізольовані
- Покривають: CRUD операції, утиліти, сервіси

### Інтеграційні тести (`@pytest.mark.integration`)
- Тестують взаємодію між компонентами
- Використовують тестову базу даних
- Покривають: API ендпоінти, повний flow

### Специфічні маркери
- `@pytest.mark.auth` - Тести аутентифікації
- `@pytest.mark.crud` - Тести CRUD операцій
- `@pytest.mark.api` - Тести API ендпоінтів

## ⚡ Способи запуску

### Make команди (рекомендовано)

```bash
make test              # Всі тести з покриттям
make test-unit         # Тільки модульні тести
make test-integration  # Тільки інтеграційні тести
make test-coverage     # Детальний звіт покриття
make test-html         # HTML звіт покриття
make test-fast         # Швидкий запуск без покриття
make test-parallel     # Паралельний запуск
```

### Pytest команди

```bash
# Всі тести
pytest tests/ --cov=app --cov-report=html -v

# Тільки модульні
pytest tests/ -m unit --cov=app -v

# Тільки інтеграційні
pytest tests/ -m integration --cov=app -v

# Конкретний файл
pytest tests/unit/test_crud_users.py -v

# Конкретний тест
pytest tests/unit/test_crud_users.py::TestUserCRUD::test_create_user_success -v

# З детальним виводом помилок
pytest tests/ -v -s --tb=long

# Паралельно (потребує pytest-xdist)
pytest tests/ -n auto --cov=app -v
```

### Python скрипт

```bash
# Використання кастомного скрипта
python run_tests.py --coverage --html --verbose
python run_tests.py --unit
python run_tests.py --integration --parallel
```

### Docker запуск

```bash
# Запуск у Docker контейнері
docker-compose -f docker-compose.test.yaml up test-runner

# Тільки тестові сервіси
docker-compose -f docker-compose.test.yaml up -d test-db test-redis
```

## 📊 Покриття тестами

### Поточне покриття

Проект має **понад 75%** покриття тестами:

- **app.crud/**: 95%+ (CRUD операції)
- **app.utils/**: 90%+ (Утиліти)
- **app.api/**: 85%+ (API ендпоінти)  
- **app.middleware/**: 80%+ (Middleware)
- **app.services/**: 85%+ (Сервіси)

### Перевірка покриття

```bash
# Генерація звіту
make test-coverage

# Тільки звіт без тестів
python -m coverage report --show-missing

# HTML звіт
python -m coverage html
```

### Вимоги до покриття

- Мінімум **75%** для всього проекту
- Нові файли: **90%+**
- Критичні модулі (auth, crud): **95%+**

## 🤖 Налаштування CI/CD

### GitHub Actions

Файл `.github/workflows/tests.yml` автоматично:

1. **Запускає тести** на Python 3.9, 3.10, 3.11
2. **Перевіряє покриття** (мінімум 75%)
3. **Linting та форматування** коду
4. **Security scan** залежностей
5. **Генерує звіти** та артефакти

### Локальна перевірка перед commit

```bash
# Повна перевірка
make all

# Швидка перевірка
make pre-commit
```

## 🛠️ Розробка тестів

### Структура тесту

```python
import pytest
from app.models.users import User


@pytest.mark.unit
@pytest.mark.auth
class TestUserAuthentication:
    """Тести аутентифікації користувачів"""
    
    def test_valid_login(self, client, create_test_user, mock_all_external_services):
        """Тест валідного входу користувача"""
        # Arrange
        login_data = {"email": "test@example.com", "password": "password123"}
        
        # Act
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Assert
        assert response.status_code == 200
        assert "access_token" in response.json()
```

### Фікстури

Доступні фікстури в `conftest.py`:

```python
# Базові
def test_something(client, db_session):
    pass

# Користувачі
def test_something(create_test_user, create_test_admin):
    pass

# Контакти
def test_something(create_test_contact, test_contact_data):
    pass

# Авторизація
def test_something(auth_headers, admin_headers):
    pass

# Мокування
def test_something(mock_all_external_services):
    pass
```

### Мокування зовнішніх сервісів

```python
@patch('app.services.cloudinary.upload_avatar')
def test_avatar_upload(mock_upload, client, admin_headers):
    mock_upload.return_value = "https://test.com/avatar.jpg"
    # Тест...
```

### Тестування API ендпоінтів

```python
def test_create_contact_success(self, client, auth_headers, test_contact_data):
    response = client.post("/api/v1/contacts/", json=test_contact_data, headers=auth_headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == test_contact_data["first_name"]
```

## 🐛 Troubleshooting

### Проблема: Тести не запускаються

```bash
# Перевірте залежності
pip install -r requirements-test.txt

# Перевірте Python версію
python --version  # Має бути 3.9+

# Очистіть кеш
make clean
```

### Проблема: Database connection error

```bash
# Запустіть тестову базу
docker-compose -f docker-compose.test.yaml up -d test-db

# Перевірте підключення
docker exec -it contacts_test_db psql -U test_user -d test_contacts_db -c "SELECT 1;"
```

### Проблема: Redis connection error

```bash
# Запустіть тестовий Redis
docker-compose -f docker-compose.test.yaml up -d test-redis

# Перевірте підключення
docker exec -it contacts_test_redis redis-cli ping
```

### Проблема: Низьке покриття

```bash
# Знайдіть непокриті файли
python -m coverage report --show-missing

# HTML звіт для детального аналізу
python -m coverage html
open htmlcov/index.html
```

### Проблема: Повільні тести

```bash
# Запустіть паралельно
pytest tests/ -n auto

# Профілювання
pytest tests/ --durations=10

# Тільки швидкі тести
pytest tests/ -m "not slow"
```

### Проблема: Flaky тести

```bash
# Запустіть кілька разів
pytest tests/test_problematic.py --count=5

# З рандомізацією
pytest tests/ --random-order
```

## 📈 Метрики якості

### Code Coverage
- **Ціль**: 75%+
- **Поточний**: 85%+
- **Тренд**: ↗️ Зростає

### Test Performance
- **Unit tests**: <5s
- **Integration tests**: <30s
- **Full suite**: <60s

### Test Quality
- **Success rate**: 99%+
- **Flaky tests**: <1%
- **Maintenance**: Щотижневий огляд

## 🔧 Налаштування IDE

### VS Code

```json
// .vscode/settings.json
{
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "python.testing.cwd": "${workspaceFolder}",
    "python.testing.autoTestDiscoverOnSaveEnabled": true
}
```

### PyCharm

1. Settings → Tools → Python Integrated Tools
2. Default test runner: pytest
3. Additional arguments: `--cov=app -v`

## 📚 Додаткові ресурси

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Testing Best Practices](https://pytest-best-practices.readthedocs.io/)

---

**Автори**: AndyGrigs, розробк Contact Management API  
**Остання оновлення**: 2025-09-21  
**Версія документації**: 2.0.0