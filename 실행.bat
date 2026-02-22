@echo off
chcp 65001 > nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set "VENV=%~dp0..\바이브 코딩20260205\.venv\Scripts\python.exe"
"%VENV%" -X utf8 "%~dp0main4.py"
if errorlevel 1 (
    echo.
    echo [오류] 실행 실패 - 위 오류 메시지를 확인하세요.
    pause
)
