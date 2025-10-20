@echo off
chcp 65001 >nul
git add .
git commit -m "Fix skeletons visibility and remove old notes - use text chars instead of emoji, increase skeleton spawn rate, disable old note system"
git push
pause
