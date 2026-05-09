#!/bin/bash
# EDIS Assistant - Универсальный стартовый скрипт для Linux/Mac
# Автоматически проверяет, устанавливает и запускает всю систему

set -e

echo ""
echo "================================================================"
echo "                    EDIS ASSISTANT"
echo "         Enhanced Dual Intelligence System"
echo "              Автоматический запуск"
echo "================================================================"
echo ""

# Проверка Python
echo "[1/4] Проверка Python..."
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 не найден! Установите Python 3.10+"
    exit 1
fi
echo "[OK] Python найден: $(python3 --version)"

# Проверка Node.js
echo "[2/4] Проверка Node.js..."
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js не найден! Установите Node.js"
    echo "        https://nodejs.org/"
    exit 1
fi
echo "[OK] Node.js найден: $(node --version)"

# Проверка Docker (опционально)
echo "[3/4] Проверка Docker..."
if ! command -v docker &> /dev/null; then
    echo "[WARNING] Docker не найден (опционально для Qdrant)"
else
    echo "[OK] Docker найден: $(docker --version)"
fi

# Запуск Python стартера
echo "[4/4] Запуск системы..."
echo ""
python3 start_edis.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Ошибка запуска системы"
    exit 1
fi
