@echo off
chcp 65001 >nul
git add .
git commit -m "Add automatic installer and detailed installation instructions"
git push
pause
