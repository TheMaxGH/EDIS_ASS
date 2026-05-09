@echo off
REM EDIS Assistant - Универсальный стартовый скрипт для Windows
REM Автоматически проверяет, устанавливает и запускает всю систему

echo.
echo ================================================================
echo                    EDIS ASSISTANT
echo         Enhanced Dual Intelligence System
echo              Автоматический запуск
echo ================================================================
echo.

REM Проверка Python
echo [1/4] Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python не найден! Установите Python 3.10+
    echo         https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python найден

REM Проверка Node.js
echo [2/4] Проверка Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js не найден! Установите Node.js
    echo         https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js найден

REM Проверка Docker (опционально)
echo [3/4] Проверка Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Docker не найден (опционально для Qdrant)
) else (
    echo [OK] Docker найден
)

REM Запуск Python стартера
echo [4/4] Запуск системы...
echo.
python start_edis.py

if errorlevel 1 (
    echo.
    echo [ERROR] Ошибка запуска системы
    pause
    exit /b 1
)

pause
