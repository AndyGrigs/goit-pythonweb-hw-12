#!/bin/bash

# Setup Tests Script для Contact Management API
# Автоматичне налаштування та запуск тестів

set -e  # Зупинити при помилці

echo "🧪 Contact Management API - Налаштування тестування"
echo "=================================================="

# Перевірка Python
echo "🐍 Перевірка Python..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Знайдено Python $python_version"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не знайдено. Встановіть Python 3.9+ та спробуйте знову."
    exit 1
fi

# Створення віртуального середовища
echo "📦 Створення віртуального середовища..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Віртуальне середовище створено"
else
    echo "✅ Віртуальне середовище вже існує"
fi

# Активація віртуального середовища
echo "🔌 Активація віртуального середовища..."
source venv/bin/activate || source venv/Scripts/activate 2>/dev/null || {
    echo "❌ Не вдалося активувати віртуальне середовище"
    exit 1
}

# Оновлення pip
echo "⬆️ Оновлення pip..."
python -m pip install --upgrade pip

# Встановлення залежностей
echo "📚 Встановлення основних залежностей..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Основні залежності встановлені"
else
    echo "❌ Файл requirements.txt не знайдено"
    exit 1
fi

echo "🧪 Встановлення тестових залежностей..."
if [ -f "requirements-test.txt" ]; then
    pip install -r requirements-test.txt
    echo "✅ Тестові залежності встановлені"
else
    echo "❌ Файл requirements-test.txt не знайдено"
    exit 1
fi

# Створення необхідних директорій
echo "📁 Створення директорій..."
mkdir -p tests/unit tests/integration htmlcov
echo "✅ Директорії створені"

# Перевірка Docker (опціонально)
echo "🐳 Перевірка Docker..."
if command -v docker &> /dev/null; then
    echo "✅ Docker знайдено"
    
    echo "🗄️ Запуск тестової бази даних..."
    docker-compose -f docker-compose.test.yaml up -d test-db test-redis
    
    echo "⏳ Очікування готовності сервісів..."
    sleep 10
    
    echo "✅ Тестові сервіси запущені"
else
    echo "⚠️ Docker не знайдено. Тести будуть використовувати SQLite."
fi

# Налаштування змінних середовища
echo "🔧 Налаштування змінних середовища..."
cat > .env.test << EOF
# Тестові змінні середовища
TESTING=true
DB_HOST=localhost
DB_PORT=5434
DB_NAME=test_contacts_db
DB_USER=test_user
DB_PASSWORD=test_password
SECRET_KEY=test-secret-key-change-in-production
REDIS_HOST=localhost
REDIS_PORT=6380
MAIL_USERNAME=test@example.com
MAIL_PASSWORD=test_password
CLOUDINARY_NAME=test_cloud
CLOUDINARY_API_KEY=test_key
CLOUDINARY_API_SECRET=test_secret
EOF
echo "✅ Файл .env.test створений"

# Перший запуск тестів
echo "🚀 Перший запуск тестів..."
echo "=========================="

# Спочатку швидкі unit тести
echo "🔬 Запуск модульних тестів..."
python -m pytest tests/ -m unit -v --tb=short || {
    echo "❌ Модульні тести не пройшли"
    echo "💡 Перевірте помилки вище та виправте код"
}

# Потім інтеграційні тести
echo "🔗 Запуск інтеграційних тестів..."
python -m pytest tests/ -m integration -v --tb=short || {
    echo "❌ Інтеграційні тести не пройшли"
    echo "💡 Перевірте підключення до тестової БД"
}

# Повний запуск з покриттям
echo "📊 Запуск всіх тестів з покриттям..."
python -m pytest tests/ \
    --cov=app \
    --cov-report=html:htmlcov \
    --cov-report=term-missing \
    --cov-fail-under=75 \
    -v

# Результати
echo ""
echo "🎉 Налаштування завершено!"
echo "========================="
echo ""
echo "📝 Наступні кроки:"
echo "  1. Перегляньте звіт покриття: open htmlcov/index.html"
echo "  2. Запустіть тести: make test"
echo "  3. Читайте документацію: cat TESTING.md"
echo ""
echo "🛠️ Корисні команди:"
echo "  make test              # Всі тести з покриттям"
echo "  make test-unit         # Тільки модульні тести"
echo "  make test-integration  # Тільки інтеграційні тести"
echo "  make test-coverage     # Детальний звіт покриття"
echo "  make clean             # Очистити тимчасові файли"
echo ""
echo "📚 Документація:"
echo "  TESTING.md             # Повна документація по тестуванню"
echo "  README.md              # Загальна документація проекту"
echo ""

# Перевірка покриття
coverage_percent=$(python -m coverage report | tail -1 | awk '{print $4}' | sed 's/%//')
if [ "$coverage_percent" -ge 75 ]; then
    echo "✅ Покриття тестами: $coverage_percent% (≥75% ✓)"
else
    echo "❌ Покриття тестами: $coverage_percent% (<75% ✗)"
    echo "💡 Додайте більше тестів для досягнення 75%+"
fi

echo ""
echo "🎯 Статус: Тестування готове до використання!"