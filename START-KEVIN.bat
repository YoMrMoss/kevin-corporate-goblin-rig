@echo off
title Kevin Corporate Goblin - Production Rig - Port 8877
cd /d "%~dp0"
where python >nul 2>nul || (echo Python is required from python.org. & pause & exit /b 1)
echo Starting direct Windows keyboard and mouse input capture...
python server.py
pause
