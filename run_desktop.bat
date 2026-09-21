@echo off
title MarkItDown Studio
echo Starting MarkItDown Studio (Desktop & Web)...
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" desktop\run_studio.py %*
) else (
    python desktop\run_studio.py %*
)
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with code %ERRORLEVEL%.
    pause
)
