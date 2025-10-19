@echo off
chcp 65001 >nul
git add .
git commit -m "Integrate NIICHAVO elements into gameplay - notes popup and biome names in HUD"
git push
pause
