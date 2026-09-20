@echo off
title AI-Based Defect Reporting System
cd /d "%~dp0"
echo ========================================================
echo   Starting AI-Based Defect Reporting System
echo ========================================================
echo.
echo Starting Gradio Web Application...
echo Press Ctrl+C in this window to stop the server.
echo.
python app/main.py
pause
