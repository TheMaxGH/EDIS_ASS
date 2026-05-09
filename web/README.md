# EDIS Web Interface

Киберпанк-интерфейс для удаленного управления Dual Qwen Brain.

## 🏗️ Архитектура

```
┌─────────────────────────────────────────┐
│  Сервер (8x H200)                       │
│  ├─ FastAPI Backend (port 8000)         │
│  ├─ Dual Qwen Brain                     │
│  └─ vLLM Servers                        │
└─────────────────────────────────────────┘
              ↕ REST API + WebSockets
┌─────────────────────────────────────────┐
│  Локальный ПК / Любое устройство        │
│  └─ Next.js Frontend (port 3000)        │
└─────────────────────────────────────────┘
```

## 🚀 Быстрый старт

### 1. Запуск Backend (на сервере с H200)

```bash
# Установка зависимостей
pip install -r web/backend/requirements.txt

# Установка API ключа
export EDIS_API_KEY="your-secret-key-here"

# Запуск сервера
cd web/backend
python main.py
```

Backend будет доступен на `http://0.0.0.0:8000`

### 2. Запуск Frontend (на локальном ПК)

**Windows:**
```bash
start_web.bat
```

**Linux/Mac:**
```bash
chmod +x start_web.sh
./start_web.sh
```

Или вручную:
```bash
cd web/frontend
npm install
cp .env.example .env.local
# Отредактируйте .env.local
npm run dev
```

Frontend будет доступен на `http://localhost:3000`

### 3. Настройка подключения

1. Откройте `web/frontend/.env.local`
2. Укажите IP вашего сервера:
   ```
   NEXT_PUBLIC_API_URL=http://YOUR_SERVER_IP:8000
   NEXT_PUBLIC_API_KEY=your-secret-key-here
   ```
3. Перезапустите фронтенд

## 📁 Структура проекта

```
web/
├── backend/
│   ├── main.py              # FastAPI сервер
│   ├── requirements.txt     # Python зависимости
│   └── __init__.py
│
└── frontend/
    ├── components/
    │   ├── AutonomousLog.tsx      # Терминал с логами
    │   ├── TaskInput.tsx          # Ввод задач
    │   └── SystemStats.tsx        # Мониторинг системы
    ├── lib/
    │   └── edis-client.ts         # API клиент
    ├── pages/
    │   ├── index.tsx              # Главная страница
    │   └── _app.tsx               # App wrapper
    ├── styles/
    │   └── globals.css            # Киберпанк стили
    ├── package.json
    ├── tailwind.config.js
    └── next.config.js
```

## 🎨 Особенности интерфейса

### Cyberpunk Dark Theme
- **Цвета:** Deep Black, Neon Purple, Cyan, Hot Pink
- **Эффекты:** Glassmorphism, Neon Glow, Scanline overlay
- **Шрифты:** JetBrains Mono (моноширинный)

### Компоненты

1. **Task Input** - Неоновое поле ввода задач
   - Выбор приоритета (Critical/High/Medium/Low)
   - Режим Task Graph
   - Анимированная кнопка отправки

2. **Autonomous Log** - Живой терминал
   - WebSocket трансляция логов
   - Поддержка Markdown
   - Подсветка синтаксиса кода
   - Автоскролл

3. **System Stats** - Мониторинг ресурсов
   - Количество GPU
   - Использование памяти
   - Активные задачи
   - Uptime сервера

## 🔌 API Endpoints

### REST API

- `GET /` - Проверка работоспособности
- `POST /api/v1/tasks` - Создание задачи
- `GET /api/v1/tasks/{task_id}` - Статус задачи
- `GET /api/v1/tasks` - Список всех задач
- `GET /api/v1/workspace/files` - Список файлов
- `GET /api/v1/workspace/files/{path}` - Скачать файл
- `GET /api/v1/system/stats` - Статистика системы

### WebSocket

- `WS /api/v1/ws/logs` - Трансляция логов в реальном времени

## 🔐 Безопасность

1. **API Key Authentication**
   - Все запросы требуют заголовок `X-API-Key`
   - Установите через переменную окружения `EDIS_API_KEY`

2. **CORS**
   - По умолчанию разрешены все источники
   - В production настройте конкретные домены

## 🛠️ Разработка

### Backend

```bash
cd web/backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd web/frontend
npm install
npm run dev
```

## 📦 Production Build

### Frontend

```bash
cd web/frontend
npm run build
npm start
```

Или используйте Docker:

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 🐛 Troubleshooting

### Backend не запускается
- Проверьте, что установлены все зависимости: `pip install -r requirements.txt`
- Убедитесь, что порт 8000 свободен
- Проверьте логи: `python main.py`

### Frontend не подключается к серверу
- Проверьте `.env.local` - правильный ли IP сервера
- Убедитесь, что backend запущен
- Проверьте firewall на сервере (порт 8000 должен быть открыт)
- Проверьте API ключ

### WebSocket не работает
- Убедитесь, что используется правильный протокол (ws:// или wss://)
- Проверьте, что backend поддерживает WebSocket соединения
- Проверьте логи браузера (F12 → Console)

## 📝 TODO

- [ ] Добавить Task Graph Visualizer (React Flow)
- [ ] Реализовать File Explorer с предпросмотром
- [ ] Добавить историю задач
- [ ] Реализовать темы (Light/Dark/Cyberpunk)
- [ ] Добавить уведомления о завершении задач
- [ ] Мобильная версия интерфейса

## 💜 Made with Love by Alya

*мур~*
