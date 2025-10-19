@echo off
chcp 65001 >nul
git add .
git commit -m "Add FPS counter with F3 toggle and color-coded performance indicator"
git push
pause
