#!/usr/bin/env python3
"""
Скрипт для запуску тестів Contact Management API з повним покриттям

Використання:
    python run_tests.py [опції]

Опції:
    --unit         Запустити тільки модульні тести
    --integration  Запустити тільки інтеграційні тести
    --coverage     Генерувати звіт покриття (за замовчуванням True)
    --html         Генерувати HTML звіт покриття
    --verbose      Детальний вивід
    --parallel     Запустити тести паралельно
    --fail-under   Мінімальний відсоток покриття (за замовчуванням 75)
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description=""):
    """Запускає команду та виводить результат"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    print(f"Команда: {' '.join(command)}")
    print()
    
    try:
        result = subprocess.run(command, check=True, capture_output=False)
        print(f"\n✅ {description} - Успішно завершено")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} - Помилка (код: {e.returncode})")
        return False


def check_dependencies():
    """Перевіряє наявність необхідних залежностей"""
    print("🔍 Перевірка залежностей...")
    
    required_packages = [
        "pytest",
        "pytest-cov", 
        "pytest-asyncio",
        "httpx",
        "faker"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Відсутні пакети: {', '.join(missing_packages)}")
        print("Встановіть їх командою:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ Всі залежності встановлені")
    return True


def setup_test_environment():
    """Налаштовує тестове середовище"""
    print("🔧 Налаштування тестового середовища...")
    
    # Встановлюємо змінні середовища для тестів
    test_env = {
        "TESTING": "true",
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "test_contacts_db",
        "DB_USER": "test_user",
        "DB_PASSWORD": "test_password",
        "SECRET_KEY": "test-secret-key-for-testing-only",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "MAIL_USERNAME": "test@example.com",
        "MAIL_PASSWORD": "test_password",
        "CLOUDINARY_NAME": "test_cloud",
        "CLOUDINARY_API_KEY": "test_key",
        "CLOUDINARY_API_SECRET": "test_secret"
    }
    
    for key, value in test_env.items():
        os.environ[key] = value
    
    print("✅ Тестове середовище налаштовано")


def create_test_directories():
    """Створює необхідні директорії для тестів"""
    directories = [
        "tests",
        "tests/unit", 
        "tests/integration",
        "htmlcov"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def run_tests(args):
    """Запускає тести з заданими параметрами"""
    
    # Базова команда pytest
    command = ["python", "-m", "pytest"]
    
    # Додаємо опції покриття
    if args.coverage:
        command.extend([
            "--cov=app",
            "--cov-report=term-missing",
            f"--cov-fail-under={args.fail_under}"
        ])
        
        if args.html:
            command.append("--cov-report=html:htmlcov")
    
    # Вибір типу тестів
    if args.unit:
        command.extend(["-m", "unit"])
    elif args.integration:
        command.extend(["-m", "integration"])
    else:
        # Запускаємо всі тести
        command.append("tests/")
    
    # Додаткові опції
    if args.verbose:
        command.append("-v")
    
    if args.parallel:
        command.extend(["-n", "auto"])
    
    # Додаємо кольоровий вивід
    command.append("--color=yes")
    
    return run_command(command, "Запуск тестів")


def generate_coverage_report():
    """Генерує детальний звіт покриття"""
    print("\n📊 Генерація звіту покриття...")
    
    # Текстовий звіт
    run_command(
        ["python", "-m", "coverage", "report", "--show-missing"],
        "Генерація текстового звіту покриття"
    )
    
    # HTML звіт
    run_command(
        ["python", "-m", "coverage", "html"],
        "Генерація HTML звіту покриття"
    )
    
    print("\n📁 HTML звіт збережено в директорії 'htmlcov/'")
    print("   Відкрийте htmlcov/index.html у браузері для перегляду")


def run_specific_test_suites():
    """Запускає специфічні набори тестів"""
    test_suites = [
        {
            "name": "Модульні тести CRUD",
            "command": ["python", "-m", "pytest", "-m", "crud", "-v"],
            "description": "Тестування CRUD операцій"
        },
        {
            "name": "Тести аутентифікації", 
            "command": ["python", "-m", "pytest", "-m", "auth", "-v"],
            "description": "Тестування системи аутентифікації"
        },
        {
            "name": "API тести",
            "command": ["python", "-m", "pytest", "-m", "api", "-v"],
            "description": "Тестування API ендпоінтів"
        }
    ]
    
    for suite in test_suites:
        success = run_command(suite["command"], suite["description"])
        if not success:
            print(f"❌ Помилка в наборі тестів: {suite['name']}")
            return False
    
    return True


def cleanup():
    """Очищає тимчасові файли після тестування"""
    print("\n🧹 Очищення тимчасових файлів...")
    
    temp_files = [
        "test.db",
        ".coverage",
        ".pytest_cache"
    ]
    
    for file_path in temp_files:
        if os.path.exists(file_path):
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                import shutil
                shutil.rmtree(file_path)
    
    print("✅ Очищення завершено")


def main():
    """Головна функція"""
    parser = argparse.ArgumentParser(
        description="Запуск тестів Contact Management API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--unit", 
        action="store_true",
        help="Запустити тільки модульні тести"
    )
    
    parser.add_argument(
        "--integration", 
        action="store_true",
        help="Запустити тільки інтеграційні тести"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        default=True,
        help="Генерувати звіт покриття (за замовчуванням)"
    )
    
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Не генерувати звіт покриття"
    )
    
    parser.add_argument(
        "--html",
        action="store_true",
        help="Генерувати HTML звіт покриття"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Детальний вивід"
    )
    
    parser.add_argument(
        "--parallel", "-n",
        action="store_true",
        help="Запустити тести паралельно"
    )
    
    parser.add_argument(
        "--fail-under",
        type=int,
        default=75,
        help="Мінімальний відсоток покриття (за замовчуванням 75%%)"
    )
    
    parser.add_argument(
        "--suites",
        action="store_true",
        help="Запустити специфічні набори тестів"
    )
    
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Очистити тимчасові файли після тестування"
    )
    
    args = parser.parse_args()
    
    # Обробка конфліктних опцій
    if args.no_coverage:
        args.coverage = False
    
    if args.unit and args.integration:
        print("❌ Помилка: Не можна одночасно вказувати --unit та --integration")
        sys.exit(1)
    
    print("🧪 Contact Management API - Запуск тестів")
    print("=" * 60)
    
    # Перевірка залежностей
    if not check_dependencies():
        sys.exit(1)
    
    # Налаштування середовища
    setup_test_environment()
    create_test_directories()
    
    success = True
    
    try:
        if args.suites:
            # Запуск специфічних наборів тестів
            success = run_specific_test_suites()
        else:
            # Звичайний запуск тестів
            success = run_tests(args)
        
        if success and args.coverage and args.html:
            generate_coverage_report()
    
    except KeyboardInterrupt:
        print("\n❌ Тестування перервано користувачем")
        success = False
    
    except Exception as e:
        print(f"\n❌ Неочікувана помилка: {e}")
        success = False
    
    finally:
        if args.cleanup:
            cleanup()
    
    # Підсумок
    print("\n" + "=" * 60)
    if success:
        print("✅ Всі тести успішно завершені!")
        if args.coverage:
            print(f"📊 Покриття тестами: мінімум {args.fail_under}%")
        if args.html:
            print("📁 HTML звіт доступний в htmlcov/index.html")
    else:
        print("❌ Деякі тести не пройшли або виникли помилки")
        sys.exit(1)


if __name__ == "__main__":
    main()