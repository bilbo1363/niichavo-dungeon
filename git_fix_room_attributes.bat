@echo off
chcp 65001 >nul
git add .
git commit -m "Fix Room attribute error - use x,y,width,height instead of x1,x2,y1,y2"
git push
pause
