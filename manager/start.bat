@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo [HWT BLOG Manager] 启动管理后端系统...
uv run main.py
if %errorlevel% neq 0 (
    echo.
    echo [错误] 启动失败，请确认已执行过 uv sync
    pause
)
