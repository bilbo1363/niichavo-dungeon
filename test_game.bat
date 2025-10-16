@echo off
title Gold - Test Mode

echo ========================================
echo    GOLD - TEST MODE
echo ========================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Select test mode:
echo.
echo [1] Run game (normal mode)
echo [2] Run tests (pytest)
echo [3] Check code (black + flake8)
echo [4] Show code statistics
echo [5] Exit
echo.
set /p choice="Your choice (1-5): "

if "%choice%"=="1" goto run_game
if "%choice%"=="2" goto run_tests
if "%choice%"=="3" goto check_code
if "%choice%"=="4" goto show_stats
if "%choice%"=="5" goto end

echo [ERROR] Invalid choice!
pause
exit /b 1

:run_game
echo.
echo [TEST] Starting game...
python main.py
goto end

:run_tests
echo.
echo [TEST] Running pytest...
if not exist "tests" (
    echo [WARNING] tests folder not found!
    echo Create tests in tests/ folder
    pause
    goto end
)
pytest tests/ -v
goto end

:check_code
echo.
echo [TEST] Checking formatting (black)...
black --check src/
echo.
echo [TEST] Checking style (flake8)...
flake8 src/ --max-line-length=120
goto end

:show_stats
echo.
echo [STATS] Counting lines of code...
echo.
echo Python files:
for /f %%i in ('dir /s /b *.py ^| find /c /v ""') do echo   Files: %%i
echo.
echo Markdown files:
for /f %%i in ('dir /s /b Doc\*.md ^| find /c /v ""') do echo   Files: %%i
echo.
pause
goto end

:end
echo.
echo ========================================
echo    TESTING FINISHED
echo ========================================
pause
