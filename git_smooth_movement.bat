@echo off
chcp 65001 >nul
git add .
git commit -m "Fix stuttering movement - reduce move delay for smooth 60 FPS animation"
git push
pause
