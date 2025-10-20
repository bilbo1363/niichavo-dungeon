@echo off
chcp 65001 >nul
git add .
git commit -m "Fix music bug on floor return and add attic theme - music now changes correctly when going up/down"
git push
pause
