@echo off
title Wax and Warmth Backend Keep-Alive
cd /d "%~dp0"
echo Starting Backend Keep-Alive Monitor...
python scripts\keep_alive.py
pause
