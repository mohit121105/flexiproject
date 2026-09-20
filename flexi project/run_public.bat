@echo off
title AI Defect Reporting System - Public Share
cd /d "%~dp0"
echo ========================================================
echo   Starting AI Defect Reporting System (Public Web Link)
echo ========================================================
echo.
echo Launching Gradio with a public shareable URL...
echo Look for the "Running on public URL: https://xxxx.gradio.live" line below.
echo.
python app/main.py --share
pause
