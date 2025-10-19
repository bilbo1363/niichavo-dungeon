@echo off
chcp 65001 >nul
git add .
git commit -m "Adjust movement speed - balance between smoothness and comfortable pace"
git push
pause
