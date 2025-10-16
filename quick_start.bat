@echo off
REM Быстрый запуск без вывода информации
chcp 65001 >nul
call venv\Scripts\activate.bat
python main.py
