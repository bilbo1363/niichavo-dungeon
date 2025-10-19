@echo off
chcp 65001 >nul
git add .
git commit -m "Fix input manager bug - prevent key sticking when UI opens/closes"
git push
pause
