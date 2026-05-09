# 🚀 EDIS Assistant - Быстрый старт

## Автоматический запуск (рекомендуется)

### Windows
```bash
start_edis.bat
```

### Linux/Mac
```bash
chmod +x start_edis.sh
./start_edis.sh
```

### Или напрямую через Python
```bash
python start_edis.py
```

## Что делает автоматический запуск?

1. ✅ **Проверяет системные требования**
   - Python 3.10+
   - Node.js
   - Docker (опционально)
   - Git (опционально)

2. ✅ **Устанавливает зависимости**
   - Python packages (pip install -r requirements.txt)
   - Frontend packages (npm install)

3. ✅ **Настраивает компоненты**
   - Создает .env из .env.example
   - Устанавливает GPT-SoVITS (опционально)

4. ✅ **Запускает сервисы**
   - Qdrant (Docker)
   - Backend API (http://localhost:8000)
   - Frontend UI (http://localhost:3000)

## Ручной запуск

### 1. Установка зависимостей

```bash
# Python
pip install -r requirements.txt

# Frontend
cd web/frontend
npm install
cd ../..
```

### 2. Настройка конфигурации

```bash
# Создайте .env из примера
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Отредактируйте .env и добавьте свои API ключи
```

### 3. Запуск Qdrant (опционально)

```bash
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

### 4. Запуск Backend

```bash
cd web/backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. Запуск Frontend

```bash
cd web/frontend
npm run dev
```

### 6. Запуск основной системы (опционально)

```bash
python run_system.py
```

## Доступные сервисы

После запуска будут доступны:

- 🌐 **Frontend UI**: http://localhost:3000
- 🔌 **Backend API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs
- 🗄️ **Qdrant**: http://localhost:6333 (если запущен)

## Документация

- [`MASTER_README.md`](MASTER_README.md) - Главная инструкция для чайников
- [`QUICKSTART.md`](QUICKSTART.md) - Быстрый старт за 5 минут
- [`WEB_QUICKSTART.md`](WEB_QUICKSTART.md) - Запуск веб-интерфейса
- [`API_KEYS_GUIDE.md`](API_KEYS_GUIDE.md) - Получение API ключей
- [`ARCHITECTURE.md`](ARCHITECTURE.md) - Архитектура системы
- [`docs/AUDIO_ARCHITECTURE.md`](docs/AUDIO_ARCHITECTURE.md) - Аудио подсистема
- [`docs/TTS_API_REFERENCE.md`](docs/TTS_API_REFERENCE.md) - TTS API референс

## Примеры использования

- [`examples/tts_example.py`](examples/tts_example.py) - Python примеры TTS
- [`examples/tts_example.js`](examples/tts_example.js) - JavaScript примеры TTS
- [`examples/usage_examples.py`](examples/usage_examples.py) - Общие примеры

## Тестирование

```bash
# Запуск тестов
pytest tests/test_voice_api.py -v

# С покрытием
pytest tests/test_voice_api.py --cov=web/backend/routers/voice --cov-report=html
```

## Остановка сервисов

При использовании автоматического запуска:
- Нажмите `Ctrl+C` для остановки всех сервисов

При ручном запуске:
- Остановите каждый процесс через `Ctrl+C`
- Остановите Qdrant: `docker stop qdrant`

## Troubleshooting

### Порт уже занят
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Ошибка импорта модулей
```bash
# Переустановите зависимости
pip install -r requirements.txt --force-reinstall
```

### Frontend не запускается
```bash
# Очистите кэш и переустановите
cd web/frontend
rm -rf node_modules package-lock.json
npm install
```

### GPT-SoVITS не работает
```bash
# Установите вручную
python setup_gpt_sovits.py

# Или запустите без TTS
python run_system.py --skip-tts
```

## Поддержка

Если возникли проблемы:
1. Проверьте [`MASTER_README.md`](MASTER_README.md)
2. Проверьте логи в консоли
3. Проверьте `.env` конфигурацию
4. Создайте issue на GitHub

---

**Версия:** 1.0.0  
**Дата:** 2026-05-09  
**Статус:** Production Ready ✅
