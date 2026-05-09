#!/bin/bash

echo "========================================"
echo "EDIS Control Center - Startup Script"
echo "========================================"
echo ""

# Проверка Node.js
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js не установлен!"
    echo "Установите с https://nodejs.org/"
    exit 1
fi

echo "[1/4] Переход в директорию фронтенда..."
cd web/frontend

# Проверка наличия node_modules
if [ ! -d "node_modules" ]; then
    echo "[2/4] Установка зависимостей (это может занять время)..."
    npm install
    if [ $? -ne 0 ]; then
        echo "[ERROR] Ошибка установки зависимостей!"
        exit 1
    fi
else
    echo "[2/4] Зависимости уже установлены"
fi

# Проверка .env.local
if [ ! -f ".env.local" ]; then
    echo "[3/4] Создание .env.local из .env.example..."
    cp .env.example .env.local
    echo ""
    echo "[ВАЖНО] Отредактируйте web/frontend/.env.local"
    echo "Укажите IP вашего сервера и API ключ!"
    echo ""
    read -p "Нажмите Enter для продолжения..."
fi

echo "[4/4] Запуск Control Center..."
echo ""
echo "========================================"
echo "EDIS Control Center запущен!"
echo "Откройте браузер: http://localhost:3000"
echo "Для остановки нажмите Ctrl+C"
echo "========================================"
echo ""

npm run dev
