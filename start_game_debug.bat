@echo off
title Gold - Debug Mode

echo ========================================
echo    GOLD - DEBUG MODE
echo ========================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo [DEBUG] Starting game in debug mode...
echo [DEBUG] Python version:
python --version
echo.
echo [DEBUG] Installed packages:
pip list | findstr "pygame numpy pydantic"
echo.
echo ========================================
echo.

python -u main.py 2>&1

echo.
echo ========================================
echo [DEBUG] Game finished
echo Exit code: %ERRORLEVEL%
echo ========================================
echo.
pause
