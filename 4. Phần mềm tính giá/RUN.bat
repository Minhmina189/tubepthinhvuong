@echo off
chcp 65001 > nul
echo ============================================
echo   PHAN MEM BAO GIA NAM AN
echo   Dang khoi dong...
echo ============================================
cd /d "%~dp0"
python app.py
pause
