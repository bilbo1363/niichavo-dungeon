@echo off
title Gold - Roguelike Game

echo ========================================
echo    GOLD - ROGUELIKE GAME
echo ========================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Create it with: python -m venv venv
    echo.
    pause
    exit /b 1
)

echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo [2/3] Checking dependencies...
python -c "import pygame" 2>nul
if errorlevel 1 (
    echo [WARNING] Pygame not installed!
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies!
        pause
        exit /b 1
    )
)

echo [3/3] Starting game...
echo.
echo ========================================
echo    GAME STARTED
echo ========================================
echo.
echo Press ESC in game to exit
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo [ERROR] Game crashed!
    echo ========================================
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo    GAME FINISHED
echo ========================================
echo.
pause
