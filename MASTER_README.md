# 🚀 EDIS - Enhanced Dual Intelligence System

> **Полное руководство для начинающих** - от установки до первого запуска

## 📋 Содержание

1. [Что такое EDIS?](#что-такое-edis)
2. [Системные требования](#системные-требования)
3. [Быстрый старт](#быстрый-старт)
4. [Подробная установка](#подробная-установка)
5. [Первый запуск](#первый-запуск)
6. [Использование веб-интерфейса](#использование-веб-интерфейса)
7. [Голосовые функции (TTS)](#голосовые-функции-tts)
8. [Решение проблем](#решение-проблем)
9. [Дополнительные ресурсы](#дополнительные-ресурсы)

---

## 🤔 Что такое EDIS?

**EDIS** - это продвинутая AI-система с двумя специализированными моделями:

- **🎨 Creator (Qwen-72B)** - креативное мышление, генерация идей
- **🧠 Logic (Qwen3.5-397B-FP8)** - логический анализ, проверка решений
- **🎤 GPT-SoVITS** - синтез речи и клонирование голоса

### Ключевые возможности:

✅ Автономная работа с мониторингом GitHub, ArXiv, новостей  
✅ Веб-интерфейс в стиле OpenWebUI  
✅ Голосовой ввод и озвучка ответов  
✅ Работа с файлами и документами  
✅ Sandbox для безопасного выполнения кода  
✅ Векторная база знаний (Qdrant)  

---

## 💻 Системные требования

### Минимальные требования:

| Компонент | Требование |
|-----------|------------|
| **GPU** | 8x NVIDIA H200 (или 7x для работы без TTS) |
| **VRAM** | 560GB+ (Creator: 280GB, Logic: 240GB, TTS: 40GB) |
| **RAM** | 128GB+ |
| **Диск** | 500GB+ свободного места (модели ~300GB) |
| **ОС** | Ubuntu 22.04+ / Windows 11 с WSL2 |
| **Python** | 3.10 - 3.11 |
| **CUDA** | 12.1+ |

### Программное обеспечение:

```bash
# Обязательно
- Python 3.10+
- Git
- Docker (для Qdrant)
- NVIDIA Driver 535+
- CUDA Toolkit 12.1+

# Для TTS (опционально)
- FFmpeg
```

---

## ⚡ Быстрый старт

### Для опытных пользователей:

```bash
# 1. Клонировать репозиторий
git clone <your-repo-url>
cd EDIS_ASSISTANT

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Настроить API ключи
cp .env.example .env
nano .env  # Добавить ваши ключи

# 4. Запустить систему
python run_system.py

# 5. Открыть веб-интерфейс
# http://localhost:3000
```

**Готово!** GPT-SoVITS установится автоматически при первом запуске.

---

## 📦 Подробная установка

### Шаг 1: Подготовка системы

#### Ubuntu/Linux:

```bash
# Обновить систему
sudo apt update && sudo apt upgrade -y

# Установить зависимости
sudo apt install -y python3.10 python3-pip git docker.io ffmpeg

# Проверить NVIDIA драйвер
nvidia-smi

# Установить CUDA (если нужно)
wget https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda_12.1.0_530.30.02_linux.run
sudo sh cuda_12.1.0_530.30.02_linux.run
```

#### Windows (WSL2):

```powershell
# Установить WSL2
wsl --install -d Ubuntu-22.04

# В WSL выполнить команды для Ubuntu выше
```

### Шаг 2: Клонирование репозитория

```bash
# Клонировать проект
git clone <your-repo-url>
cd EDIS_ASSISTANT

# Проверить структуру
ls -la
```

### Шаг 3: Установка Python зависимостей

```bash
# Создать виртуальное окружение (рекомендуется)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установить зависимости
pip install --upgrade pip
pip install -r requirements.txt

# Проверить установку
python -c "import torch; print(torch.cuda.is_available())"
# Должно вывести: True
```

### Шаг 4: Настройка конфигурации

#### 4.1 Создать .env файл:

```bash
cp .env.example .env
nano .env
```

#### 4.2 Заполнить API ключи:

```env
# Tavily API (для поиска)
TAVILY_API_KEY=tvly-ваш-ключ-здесь

# GitHub Token (для мониторинга)
GITHUB_TOKEN=ghp_ваш-токен-здесь

# OpenAI API (опционально, для совместимости)
OPENAI_API_KEY=sk-ваш-ключ-здесь
```

**Где получить ключи:**
- Tavily: https://tavily.com/ (бесплатно 1000 запросов/месяц)
- GitHub: Settings → Developer settings → Personal access tokens
- OpenAI: https://platform.openai.com/api-keys

#### 4.3 Проверить конфигурацию vLLM:

```bash
cat config/vllm_config.yaml
```

Убедитесь, что пути к моделям корректны:

```yaml
creator:
  model_name: "Qwen/Qwen2.5-72B-Instruct"
  port: 8001
  gpu_ids: [0, 1]  # GPU 0-1

logic:
  model_name: "Qwen/Qwen3.5-397B-A17B-FP8"
  port: 8002
  gpu_ids: [2, 3, 4, 5]  # GPU 2-5
```

### Шаг 5: Загрузка моделей (опционально)

Модели загрузятся автоматически при первом запуске, но можно предзагрузить:

```bash
# Через Hugging Face CLI
pip install huggingface-hub

# Войти в аккаунт
huggingface-cli login

# Загрузить модели
huggingface-cli download Qwen/Qwen2.5-72B-Instruct
huggingface-cli download Qwen/Qwen3.5-397B-A17B-FP8
```

---

## 🎬 Первый запуск

### Вариант 1: Полный запуск (с TTS)

```bash
# Запустить все компоненты
python run_system.py

# Логи будут в logs/system_launch.log
```

**Что происходит:**
1. ✅ Проверка зависимостей (Docker, NVIDIA, Python)
2. ✅ Запуск Qdrant (векторная БД)
3. ✅ Запуск vLLM Creator (GPU 0-1, порт 8001)
4. ✅ Запуск vLLM Logic (GPU 2-5, порт 8002)
5. ✅ Проверка GPT-SoVITS → автоустановка если нужно
6. ✅ Запуск GPT-SoVITS (GPU 6, порт 9880)
7. ✅ Инициализация DualQwenAgent

**Время запуска:** 5-10 минут (первый раз дольше из-за загрузки моделей)

### Вариант 2: Без TTS (экономия GPU)

```bash
# Пропустить GPT-SoVITS
python run_system.py --skip-tts
```

Используйте этот вариант если:
- У вас только 7 GPU
- TTS не нужен
- Хотите сэкономить VRAM

### Вариант 3: Только веб-интерфейс

```bash
# Если vLLM уже запущен отдельно
cd web
./start_web.sh

# Или на Windows
start_web.bat
```

### Проверка запуска:

```bash
# Проверить процессы
ps aux | grep python

# Проверить GPU
nvidia-smi

# Проверить порты
netstat -tulpn | grep -E '8001|8002|9880|8000|3000'
```

**Ожидаемые порты:**
- `8001` - vLLM Creator
- `8002` - vLLM Logic  
- `9880` - GPT-SoVITS
- `8000` - FastAPI Backend
- `3000` - Next.js Frontend

---

## 🌐 Использование веб-интерфейса

### Открыть интерфейс:

```
http://localhost:3000
```

### Первый вход:

1. **Настройки** (⚙️ в правом верхнем углу)
2. Вкладка **"🤖 Модели"**
3. Проверить подключение:
   - Creator: `http://localhost:8001`
   - Logic: `http://localhost:8002`
4. Нажать **"Тест подключения"** для каждой модели
5. **Сохранить**

### Основные разделы:

#### 1. 💬 Чат (Chat)
- Диалог с EDIS
- Поддержка Markdown
- Подсветка кода
- История сообщений

**Пример использования:**
```
Вы: Напиши функцию для сортировки массива на Python

EDIS: [Генерирует код с объяснением]
```

#### 2. 📋 Задачи (Tasks)
- Создание задач с приоритетом
- Граф выполнения
- Отслеживание статуса

**Пример:**
```
Задача: Создать REST API для управления пользователями
Приоритет: High
Использовать граф: ✅
```

#### 3. 🔄 Автономность (Autonomous)
- Мониторинг GitHub Trending
- Отслеживание ArXiv
- Технологические новости
- Логи в реальном времени

#### 4. 📁 Файлы (Files)
- Просмотр workspace
- Загрузка файлов
- Предпросмотр кода

---

## 🎤 Голосовые функции (TTS)

### Настройка GPT-SoVITS:

GPT-SoVITS устанавливается автоматически, но можно настроить вручную:

```bash
# Запустить установщик
python setup_gpt_sovits.py

# Или автоматически
python setup_gpt_sovits.py --auto
```

### Использование в чате:

1. **Озвучка ответов:**
   - Наведите на сообщение ассистента
   - Нажмите кнопку **"🔊 Озвучить"**
   - Для остановки: **"🔇 Остановить"**

2. **Голосовой ввод:**
   - Нажмите кнопку микрофона 🎙️ в поле ввода
   - Говорите (запись начнется автоматически)
   - Нажмите еще раз для остановки
   - Текст распознается и отправится автоматически

### Настройки TTS:

**Настройки → 🎤 Голос & TTS:**
- Статус GPT-SoVITS
- Информация о модели
- Быстрый доступ к WebUI
- Документация

### Открыть GPT-SoVITS WebUI:

```
http://localhost:9880
```

Здесь можно:
- Тестировать синтез речи
- Загружать референсные аудио
- Обучать на новых голосах
- Настраивать параметры генерации

---

## 🔧 Решение проблем

### Проблема: "CUDA out of memory"

**Решение:**
```bash
# Уменьшить max_model_len в config/vllm_config.yaml
creator:
  max_model_len: 16384  # Было 32768

logic:
  max_model_len: 16384  # Было 32768
```

### Проблема: "Port already in use"

**Решение:**
```bash
# Найти процесс
lsof -i :8001

# Убить процесс
kill -9 <PID>

# Или изменить порт в config/vllm_config.yaml
```

### Проблема: "GPT-SoVITS не запускается"

**Решение:**
```bash
# Проверить установку
ls -la GPT-SoVITS/

# Переустановить
rm -rf GPT-SoVITS/
python setup_gpt_sovits.py --auto

# Или пропустить TTS
python run_system.py --skip-tts
```

### Проблема: "Модели не загружаются"

**Решение:**
```bash
# Проверить интернет
ping huggingface.co

# Проверить место на диске
df -h

# Загрузить вручную
huggingface-cli download Qwen/Qwen2.5-72B-Instruct
```

### Проблема: "Frontend не открывается"

**Решение:**
```bash
# Проверить Node.js
node --version  # Должно быть 18+

# Переустановить зависимости
cd web/frontend
rm -rf node_modules .next
npm install
npm run dev
```

### Проблема: "Backend ошибки 500"

**Решение:**
```bash
# Проверить логи
tail -f logs/dual_qwen_brain.log

# Проверить БД
ls -la web/backend/data/

# Пересоздать БД
rm web/backend/data/settings.db
python migrate_config_to_db.py
```

---

## 📚 Дополнительные ресурсы

### Документация:

- [ARCHITECTURE.md](ARCHITECTURE.md) - Архитектура системы
- [API_KEYS_GUIDE.md](API_KEYS_GUIDE.md) - Получение API ключей
- [DEPLOYMENT.md](DEPLOYMENT.md) - Деплой в продакшн
- [H200_OPTIMIZATIONS.md](H200_OPTIMIZATIONS.md) - Оптимизации для H200

### Быстрые гайды:

- [QUICKSTART.md](QUICKSTART.md) - Быстрый старт
- [WEB_QUICKSTART.md](WEB_QUICKSTART.md) - Запуск веб-интерфейса
- [GETTING_STARTED.md](GETTING_STARTED.md) - Начало работы

### Планы развития:

- [plans/gpt_sovits_integration_plan.md](plans/gpt_sovits_integration_plan.md) - План интеграции TTS
- [plans/web_interface_plan.md](plans/web_interface_plan.md) - План веб-интерфейса

### Внешние ресурсы:

- [Qwen2.5 Documentation](https://github.com/QwenLM/Qwen2.5)
- [Qwen3.5-397B-FP8](https://huggingface.co/Qwen/Qwen3.5-397B-A17B-FP8)
- [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)
- [vLLM Documentation](https://docs.vllm.ai/)

---

## 🎯 Следующие шаги

После успешного запуска:

1. ✅ **Изучите примеры** в `examples/usage_examples.py`
2. ✅ **Настройте автономность** в веб-интерфейсе
3. ✅ **Попробуйте голосовые функции** в чате
4. ✅ **Создайте первую задачу** с графом выполнения
5. ✅ **Обучите свой голос** через GPT-SoVITS WebUI

---

## 💡 Советы для начинающих

### Оптимизация производительности:

```yaml
# config/vllm_config.yaml
creator:
  gpu_memory_utilization: 0.85  # Уменьшить если OOM
  max_model_len: 16384  # Уменьшить для экономии VRAM

logic:
  gpu_memory_utilization: 0.85
  max_model_len: 16384
```

### Мониторинг ресурсов:

```bash
# Постоянный мониторинг GPU
watch -n 1 nvidia-smi

# Мониторинг логов
tail -f logs/system_launch.log

# Мониторинг Docker
docker stats qdrant
```

### Резервное копирование:

```bash
# Бэкап настроек
cp web/backend/data/settings.db settings.db.backup

# Бэкап чатов
cp -r web/backend/data/chats/ chats_backup/

# Бэкап конфигов
tar -czf configs_backup.tar.gz config/ .env
```

---

## 🆘 Поддержка

Если возникли проблемы:

1. **Проверьте логи:** `logs/system_launch.log`
2. **Проверьте GPU:** `nvidia-smi`
3. **Проверьте порты:** `netstat -tulpn`
4. **Создайте Issue** в репозитории с:
   - Описанием проблемы
   - Логами
   - Выводом `nvidia-smi`
   - Версией Python/CUDA

---

## 📝 Лицензия

MIT License - см. [LICENSE](LICENSE)

---

**Готово к работе!** 🚀

*Создано с ❤️ для сообщества AI разработчиков*
