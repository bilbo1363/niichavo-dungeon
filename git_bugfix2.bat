@echo off
chcp 65001 >nul
git add .
git commit -m "Fix player movement when UI is open - prevent movement during inventory navigation"
git push
pause
