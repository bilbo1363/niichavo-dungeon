@echo off
chcp 65001 >nul
echo ========================================
echo 🎮 ПОДЗЕМЕЛЬЕ НИИЧАВО - УСТАНОВКА
echo ========================================
echo.

REM Проверка Python
echo [1/4] Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo.
    echo Пожалуйста, установите Python 3.11 или выше:
    echo https://www.python.org/downloads/
    echo.
    echo ВАЖНО: При установке отметьте "Add Python to PATH"
    pause
    exit /b 1
)

python --version
echo ✅ Python установлен
echo.

REM Проверка pip
echo [2/4] Проверка pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip не найден!
    echo Устанавливаю pip...
    python -m ensurepip --upgrade
)
echo ✅ pip готов
echo.

REM Обновление pip
echo [3/4] Обновление pip...
python -m pip install --upgrade pip
echo.

REM Установка зависимостей
echo [4/4] Установка зависимостей игры...
echo.
echo Устанавливаю пакеты из requirements.txt...
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ❌ Ошибка установки зависимостей!
    echo.
    echo Попробуйте установить вручную:
    echo python -m pip install pygame numpy pyyaml pydantic pillow
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ УСТАНОВКА ЗАВЕРШЕНА!
echo ========================================
echo.
echo Теперь вы можете запустить игру:
echo   • start_game.bat - Оконный режим
echo   • start_fullscreen.bat - Полноэкранный режим
echo.
echo Для генерации звуков (опционально):
echo   • python generate_sounds.py
echo.
pause
