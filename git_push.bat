@echo off
chcp 65001 >nul
git add .
git commit -m "Add splash screen, file-based audio system, and documentation"
git push
pause
