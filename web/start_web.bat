@echo off
echo ========================================
echo EDIS Control Center - Startup Script
echo ========================================
echo.

REM Проверка Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js не установлен!
    echo Скачайте с https://nodejs.org/
    pause
    exit /b 1
)

echo [1/4] Переход в директорию фронтенда...
cd frontend

REM Проверка наличия node_modules
if not exist "node_modules\" (
    echo [2/4] Установка зависимостей (это может занять время)...
    call npm install
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Ошибка установки зависимостей!
        pause
        exit /b 1
    )
) else (
    echo [2/4] Зависимости уже установлены
)

REM Проверка .env.local
if not exist ".env.local" (
    echo [3/4] Создание .env.local из .env.example...
    copy .env.example .env.local
    echo.
    echo [ВАЖНО] Отредактируйте frontend\.env.local
    echo Укажите IP вашего сервера и API ключ!
    echo.
    pause
)

echo [4/4] Запуск Control Center...
echo.
echo ========================================
echo EDIS Control Center запущен!
echo Откройте браузер: http://localhost:3000
echo Для остановки нажмите Ctrl+C
echo ========================================
echo.

call npm run dev

pause
