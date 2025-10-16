@echo off
title Gold - Fullscreen Mode

echo ========================================
echo    GOLD - FULLSCREEN MODE
echo ========================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Create it with: python -m venv venv
    echo.
    pause
    exit /b 1
)

echo [1/2] Activating virtual environment...
call venv\Scripts\activate.bat

echo [2/2] Starting game in fullscreen...
echo.
echo ========================================
echo    GAME STARTED (FULLSCREEN)
echo ========================================
echo.
echo Press F11 to toggle fullscreen
echo Press ESC to exit
echo.

python main.py --fullscreen

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
