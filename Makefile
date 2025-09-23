# Makefile для Contact Management API

.PHONY: help test test-unit test-integration test-coverage test-html install-test-deps clean setup-test-db

# Кольори для виводу
GREEN=\033[0;32m
YELLOW=\033[0;33m
RED=\033[0;31m
NC=\033[0m # No Color

# За замовчуванням показуємо довідку
help:
	@echo "$(GREEN)Contact Management API - Команди для тестування$(NC)"
	@echo ""
	@echo "$(YELLOW)Основні команди:$(NC)"
	@echo "  make test              - Запустити всі тести з покриттям"
	@echo "  make test-unit         - Запустити тільки модульні тести"
	@echo "  make test-integration  - Запустити тільки інтеграційні тести"
	@echo "  make test-coverage     - Запустити тести з детальним покриттям"
	@echo "  make test-html         - Запустити тести з HTML звітом"
	@echo "  make test-fast         - Швидкий запуск тестів без покриття"
	@echo ""
	@echo "$(YELLOW)Допоміжні команди:$(NC)"
	@echo "  make install-test-deps - Встановити тестові залежності"
	@echo "  make setup-test-db     - Налаштувати тестову базу даних"
	@echo "  make clean             - Очистити тимчасові файли"
	@echo "  make lint              - Перевірити код лінтером"
	@echo "  make format            - Форматувати код"
	@echo ""
	@echo "$(YELLOW)Специфічні тести:$(NC)"
	@echo "  make test-auth         - Тести аутентифікації"
	@echo "  make test-crud         - Тести CRUD операцій"
	@echo "  make test-api          - Тести API ендпоінтів"

# Встановлення тестових залежностей
install-test-deps:
	@echo "$(GREEN)📦 Встановлення тестових залежностей...$(NC)"
	pip install -r requirements-test.txt
	@echo "$(GREEN)✅ Залежності встановлені$(NC)"

# Запуск всіх тестів з покриттям
test:
	@echo "$(GREEN)🧪 Запуск всіх тестів з покриттям...$(NC)"
	python -m pytest tests/ \
		--cov=app \
		--cov-report=term-missing \
		--cov-report=html:htmlcov \
		--cov-fail-under=75 \
		-v \
		--color=yes
	@echo "$(GREEN)✅ Тести завершені. HTML звіт доступний в htmlcov/index.html$(NC)"

# Тільки модульні тести
test-unit:
	@echo "$(GREEN)🔬 Запуск модульних тестів...$(NC)"
	python -m pytest tests/ \
		-m unit \
		--cov=app \
		--cov-report=term-missing \
		--cov-fail-under=75 \
		-v \
		--color=yes

# Тільки інтеграційні тести
test-integration:
	@echo "$(GREEN)🔗 Запуск інтеграційних тестів...$(NC)"
	python -m pytest tests/ \
		-m integration \
		--cov=app \
		--cov-report=term-missing \
		--cov-fail-under=75 \
		-v \
		--color=yes

# Детальний звіт покриття
test-coverage:
	@echo "$(GREEN)📊 Запуск тестів з детальним звітом покриття...$(NC)"
	python -m pytest tests/ \
		--cov=app \
		--cov-report=term-missing \
		--cov-report=html:htmlcov \
		--cov-report=xml:coverage.xml \
		--cov-fail-under=75 \
		-v \
		--color=yes
	python -m coverage report --show-missing
	@echo "$(GREEN)✅ Звіти згенеровані:$(NC)"
	@echo "  - HTML: htmlcov/index.html"
	@echo "  - XML: coverage.xml"

# HTML звіт покриття
test-html:
	@echo "$(GREEN)📄 Генерація HTML звіту покриття...$(NC)"
	python -m pytest tests/ \
		--cov=app \
		--cov-report=html:htmlcov \
		--cov-fail-under=75 \
		--color=yes
	@echo "$(GREEN)✅ HTML звіт згенеровано: htmlcov/index.html$(NC)"

# Швидкий запуск без покриття
test-fast:
	@echo "$(GREEN)⚡ Швидкий запуск тестів...$(NC)"
	python -m pytest tests/ -v --color=yes

# Специфічні тести аутентифікації
test-auth:
	@echo "$(GREEN)🔐 Запуск тестів аутентифікації...$(NC)"
	python -m pytest tests/ \
		-m auth \
		--cov=app.api.v1.endpoints.auth \
		--cov=app.middleware.auth \
		--cov=app.utils.auth \
		--cov-report=term-missing \
		-v \
		--color=yes

# Специфічні тести CRUD
test-crud:
	@echo "$(GREEN)💾 Запуск тестів CRUD операцій...$(NC)"
	python -m pytest tests/ \
		-m crud \
		--cov=app.crud \
		--cov-report=term-missing \
		-v \
		--color=yes

# Специфічні тести API
test-api:
	@echo "$(GREEN)🌐 Запуск тестів API...$(NC)"
	python -m pytest tests/ \
		-m api \
		--cov=app.api \
		--cov-report=term-missing \
		-v \
		--color=yes

# Налаштування тестової бази даних
setup-test-db:
	@echo "$(GREEN)🗄️ Налаштування тестової бази даних...$(NC)"
	docker-compose -f docker-compose.test.yaml up -d db
	sleep 5
	@echo "$(GREEN)✅ Тестова база даних запущена$(NC)"

# Очищення тимчасових файлів
clean:
	@echo "$(GREEN)🧹 Очищення тимчасових файлів...$(NC)"
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf test.db
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)✅ Очищення завершено$(NC)"

# Лінтування коду
lint:
	@echo "$(GREEN)🔍 Перевірка коду лінтером...$(NC)"
	python -m flake8 app/ tests/ --max-line-length=100 --ignore=E203,W503
	python -m pylint app/ --disable=missing-docstring,too-few-public-methods
	@echo "$(GREEN)✅ Лінтування завершено$(NC)"

# Форматування коду
format:
	@echo "$(GREEN)✨ Форматування коду...$(NC)"
	python -m black app/ tests/ --line-length=100
	python -m isort app/ tests/ --profile black
	@echo "$(GREEN)✅ Форматування завершено$(NC)"

# Паралельний запуск тестів
test-parallel:
	@echo "$(GREEN)⚡ Паралельний запуск тестів...$(NC)"
	python -m pytest tests/ \
		--cov=app \
		--cov-report=term-missing \
		--cov-fail-under=75 \
		-n auto \
		-v \
		--color=yes

# Тести з детальним виводом помилок
test-debug:
	@echo "$(GREEN)🐛 Запуск тестів в режимі відладки...$(NC)"
	python -m pytest tests/ \
		--cov=app \
		--cov-report=term-missing \
		-v \
		-s \
		--tb=long \
		--color=yes

# Continuous Integration тести
test-ci:
	@echo "$(GREEN)🤖 Запуск тестів для CI...$(NC)"
	python -m pytest tests/ \
		--cov=app \
		--cov-report=xml:coverage.xml \
		--cov-fail-under=75 \
		--junitxml=test-results.xml \
		--color=yes

# Перевірка покриття конкретного модуля
test-module:
ifndef MODULE
	@echo "$(RED)❌ Помилка: Вкажіть MODULE. Приклад: make test-module MODULE=app.crud.users$(NC)"
else
	@echo "$(GREEN)🔍 Тестування модуля $(MODULE)...$(NC)"
	python -m pytest tests/ \
		--cov=$(MODULE) \
		--cov-report=term-missing \
		-k $(MODULE) \
		-v \
		--color=yes
endif

# Генерація тестових даних
generate-test-data:
	@echo "$(GREEN)📊 Генерація тестових даних...$(NC)"
	python -c "
import sys
sys.path.append('.')
from tests.conftest import TestDataFactory
factory = TestDataFactory()
print('Тестові дані згенеровані:', factory.create_user_data())
"

# Перевірка якості тестів
test-quality:
	@echo "$(GREEN)🎯 Перевірка якості тестів...$(NC)"
	python -m pytest tests/ \
		--cov=app \
		--cov-report=term-missing \
		--cov-fail-under=75 \
		--strict-markers \
		--disable-warnings \
		-v

# Benchmark тести (якщо додано)
test-benchmark:
	@echo "$(GREEN)⏱️ Запуск benchmark тестів...$(NC)"
	python -m pytest tests/ \
		-m benchmark \
		--benchmark-only \
		--benchmark-sort=mean \
		-v

# Профілювання тестів
test-profile:
	@echo "$(GREEN)📈 Профілювання тестів...$(NC)"
	python -m pytest tests/ \
		--profile \
		--profile-svg \
		-v

# Все разом: форматування, лінтування, тести
all: format lint test
	@echo "$(GREEN)🎉 Всі перевірки пройдені успішно!$(NC)"

# Швидка перевірка перед commit
pre-commit: format lint test-fast
	@echo "$(GREEN)✅ Готово до commit!$(NC)"