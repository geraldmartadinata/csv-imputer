@echo off
title Martadinata CSV Imputer & 3NF Normalizer
cd /d "%~dp0"

set "UV_PATH=C:\Users\steph\AppData\Local\hermes\bin\uv.exe"

if exist "%UV_PATH%" (
    "%UV_PATH%" run imputer.py %*
) else (
    where uv >nul 2>&1
    if %errorlevel% equ 0 (
        uv run imputer.py %*
    ) else (
        python imputer.py %*
    )
)

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Script finished with an error.
)

pause
