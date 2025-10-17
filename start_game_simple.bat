@echo off
chcp 65001 >nul
title Подземелье НИИЧАВО
echo ========================================
echo 🎮 ПОДЗЕМЕЛЬЕ НИИЧАВО
echo ========================================
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo.
    echo Запустите install.bat для установки зависимостей
    pause
    exit /b 1
)

REM Проверка pygame
echo Проверка зависимостей...
python -c "import pygame" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ Зависимости не установлены!
    echo.
    echo Запустите install.bat для установки
    pause
    exit /b 1
)

echo ✅ Всё готово!
echo.
echo Запуск игры...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo ❌ Ошибка запуска игры!
    echo ========================================
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ Игра завершена
echo ========================================
pause
