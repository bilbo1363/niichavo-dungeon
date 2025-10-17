# 📦 ИНСТРУКЦИЯ ПО УСТАНОВКЕ

## 🎮 Подземелье НИИЧАВО

---

## 🪟 Windows (Рекомендуемый способ)

### Шаг 1: Установка Python

1. Скачайте Python 3.11 или выше: https://www.python.org/downloads/
2. **ВАЖНО!** При установке отметьте галочку **"Add Python to PATH"**
3. Завершите установку

### Шаг 2: Скачивание игры

**Вариант A: С помощью Git**
```bash
git clone https://github.com/bilbo1363/niichavo-dungeon.git
cd niichavo-dungeon
```

**Вариант B: Скачать ZIP**
1. Откройте https://github.com/bilbo1363/niichavo-dungeon
2. Нажмите зелёную кнопку **"Code"**
3. Выберите **"Download ZIP"**
4. Распакуйте архив в любую папку

### Шаг 3: Автоматическая установка

1. Откройте папку с игрой
2. Запустите **`install.bat`** (двойной клик)
3. Дождитесь завершения установки

### Шаг 4: Запуск игры

Запустите **`start_game_simple.bat`**

**Готово!** 🎉

---

## 🐧 Linux / 🍎 macOS

### Шаг 1: Проверка Python

Откройте терминал и выполните:
```bash
python3 --version
```

Если Python не установлен:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**macOS:**
```bash
brew install python3
```

### Шаг 2: Скачивание игры

```bash
git clone https://github.com/bilbo1363/niichavo-dungeon.git
cd niichavo-dungeon
```

### Шаг 3: Установка зависимостей

```bash
python3 -m pip install -r requirements.txt
```

### Шаг 4: Запуск игры

```bash
python3 main.py
```

---

## 🔧 Ручная установка (все платформы)

Если автоматическая установка не работает:

### 1. Установите зависимости по одной:

```bash
python -m pip install pygame==2.5.2
python -m pip install numpy==1.26.0
python -m pip install pyyaml==6.0.1
python -m pip install pydantic==2.5.0
python -m pip install pillow==10.1.0
```

### 2. Проверьте установку:

```bash
python -c "import pygame; print('Pygame OK')"
python -c "import numpy; print('NumPy OK')"
python -c "import yaml; print('PyYAML OK')"
```

### 3. Запустите игру:

```bash
python main.py
```

---

## ❓ Решение проблем

### Проблема: "Python не найден"

**Windows:**
1. Переустановите Python
2. Обязательно отметьте **"Add Python to PATH"**
3. Перезагрузите компьютер

**Linux/macOS:**
- Используйте `python3` вместо `python`
- Установите Python через менеджер пакетов

### Проблема: "ModuleNotFoundError: No module named 'pygame'"

Установите зависимости:
```bash
python -m pip install -r requirements.txt
```

Или вручную:
```bash
python -m pip install pygame
```

### Проблема: "pip не найден"

Установите pip:
```bash
python -m ensurepip --upgrade
```

Или:
```bash
python -m pip install --upgrade pip
```

### Проблема: "Permission denied" (Linux/macOS)

Используйте `--user`:
```bash
python3 -m pip install --user -r requirements.txt
```

Или используйте виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Проблема: Игра не запускается

1. Проверьте версию Python:
```bash
python --version
```
Должно быть 3.11 или выше

2. Проверьте зависимости:
```bash
python -c "import pygame, numpy, yaml, pydantic, PIL"
```

3. Запустите в режиме отладки:
```bash
python main.py --debug
```

---

## 📋 Список зависимостей

- **pygame** 2.5.2 - Игровой движок
- **numpy** 1.26.0 - Математика и генерация звуков
- **pyyaml** 6.0.1 - Чтение конфигураций
- **pydantic** 2.5.0 - Валидация данных
- **pillow** 10.1.0 - Работа с изображениями

---

## 🎵 Опционально: Генерация звуков

Звуки уже включены в репозиторий, но вы можете перегенерировать их:

```bash
python generate_sounds.py
```

Это создаст:
- `assets/sounds/` - 7 звуковых эффектов
- `assets/music/` - 5 музыкальных тем

---

## 🚀 Режимы запуска

### Оконный режим (по умолчанию)
```bash
python main.py
```
или
```bash
start_game_simple.bat
```

### Полноэкранный режим
```bash
python main.py --fullscreen
```
или
```bash
start_fullscreen.bat
```

---

## 💡 Советы

1. **Первый запуск может быть медленным** - pygame инициализирует аудио
2. **Звуки генерируются автоматически** если файлы отсутствуют
3. **Сохранения хранятся в** `saves/profiles/`
4. **Логи находятся в** консоли при запуске

---

## 📞 Поддержка

Если у вас возникли проблемы:

1. Проверьте этот файл (INSTALL.md)
2. Посмотрите [Issues на GitHub](https://github.com/bilbo1363/niichavo-dungeon/issues)
3. Создайте новый Issue с описанием проблемы

---

**Приятной игры!** 🎮✨
