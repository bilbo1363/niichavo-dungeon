# Requirements.txt - Зависимости проекта

## Основные зависимости

```txt
# requirements.txt

# ===== Игровой движок =====
pygame==2.5.2

# ===== Математика и генерация =====
numpy==1.26.0
noise==1.2.2

# ===== Управление данными =====
pydantic==2.5.0
pyyaml==6.0.1

# ===== Работа с изображениями =====
pillow==10.1.0

# ===== Тестирование =====
pytest==7.4.3
pytest-cov==4.1.0
hypothesis==6.92.0

# ===== Линтеры и форматирование =====
black==23.12.0
flake8==6.1.0
mypy==1.7.1
pylint==3.0.3

# ===== Упаковка =====
pyinstaller==6.3.0
```

## Установка

```bash
# Создание виртуального окружения
python -m venv venv

# Активация (Windows)
venv\Scripts\activate

# Активация (Linux/Mac)
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

## Структура проекта

```
Gold/
├── venv/                      # Виртуальное окружение
├── src/                       # Исходный код
├── assets/                    # Ресурсы
├── tests/                     # Тесты
├── saves/                     # Сохранения
├── requirements.txt           # Зависимости
├── requirements-dev.txt       # Dev зависимости
├── setup.py                   # Установка пакета
├── pyproject.toml            # Конфигурация проекта
└── main.py                   # Точка входа
```
