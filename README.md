# 🧠 EDIS - Enhanced Dual Intelligence System

**Двупалатный разум на базе Qwen с исполнительными инструментами, Task Graph и голосовым клонированием**

*Разработано с любовью Алей для Хозяина* 🐱✨

---

## 🌟 Что это?

EDIS - это продвинутая AI-система, объединяющая:
- 🎭 **Двупалатный разум**: Творец (72B) + Логик (397B-FP8)
- 🛠️ **Исполнительные инструменты**: Code Sandbox, Browser, Document Engine
- 🌳 **Task Architect**: Автоматическая декомпозиция задач в граф
- 🎤 **Voice Cloning**: Клонирование голоса через GPT-SoVITS
- 📚 **RAG System**: Векторная память с загрузкой документов
- ⚡ **Система приоритетов**: Умное управление задачами

---

## 🚀 Быстрый старт

### ⚡ Автоматический запуск (рекомендуется)

**Windows:**
```bash
start_edis.bat
```

**Linux/Mac:**
```bash
chmod +x start_edis.sh
./start_edis.sh
```

**Или напрямую:**
```bash
python start_edis.py
```

Автоматический скрипт:
- ✅ Проверит все системные требования
- ✅ Установит все зависимости (Python + Node.js)
- ✅ Настроит конфигурацию (.env)
- ✅ Установит GPT-SoVITS (опционально)
- ✅ Запустит все сервисы (Backend + Frontend + Qdrant)

📖 Подробнее: [`START.md`](START.md)

---

### 📝 Ручная установка

### 1. Установка зависимостей

```bash
# Клонируйте репозиторий
git clone <your-repo>
cd EDIS_ASSISTANT

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установите зависимости
pip install -r requirements.txt

# Установите Playwright браузеры
playwright install chromium
```

### 2. Настройка окружения

```bash
# Скопируйте пример конфигурации
cp .env.example .env

# Отредактируйте .env и добавьте API ключи
nano .env
```

### 3. Запуск системы

```bash
# Полный запуск (vLLM + Qdrant + TTS + Agent)
python run_system.py

# Или запустите компоненты отдельно (см. ниже)
```

---

## 📦 Компоненты системы

### 🧠 Модели (vLLM)

**Creator (Qwen2.5-72B)** - Генерация идей и креативных решений
```bash
# GPU 0-1
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-72B-Instruct \
    --tensor-parallel-size 2 \
    --port 8001
```

**Logic (Qwen3.5-397B-FP8)** - Верификация и планирование
```bash
# GPU 2-5
CUDA_VISIBLE_DEVICES=2,3,4,5 python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen3.5-397B-A17B-FP8 \
    --tensor-parallel-size 4 \
    --port 8002
```

### 🗄️ Векторная БД (Qdrant)

```bash
docker run -d \
    --name qdrant \
    -p 6333:6333 \
    -v qdrant_storage:/qdrant/storage \
    qdrant/qdrant:latest
```

### 🎤 TTS (GPT-SoVITS)

```bash
# Клонируйте GPT-SoVITS
git clone https://github.com/RVC-Boss/GPT-SoVITS.git
cd GPT-SoVITS

# Установите зависимости
pip install -r requirements.txt

# Запустите API сервер (GPU 6)
CUDA_VISIBLE_DEVICES=6 python api.py --port 9880
```

---

## 💻 Использование

### Базовое использование

```python
from dual_qwen_brain import DualQwenAgent
from core.workflow.task_architect import TaskPriority

# Инициализация
agent = DualQwenAgent()
await agent.initialize()

# Простая задача
result = await agent.process("Объясни квантовую запутанность")
print(result)

# Сложная задача с декомпозицией
result = await agent.process(
    task="Создай веб-скрапер для новостей с анализом тональности",
    priority=TaskPriority.HIGH,
    use_task_graph=True
)
```

### Работа с инструментами

#### Code Sandbox
```python
from core.tools import CodeSandbox

sandbox = CodeSandbox()
result = await sandbox.execute_python(
    code="""
import numpy as np
data = np.random.rand(100)
print(f"Mean: {data.mean():.2f}")
""",
    requirements=["numpy"]
)
print(result["output"])
```

#### Browser Automation
```python
from core.tools import OmniBrowser

async with OmniBrowser() as browser:
    await browser.navigate("https://news.ycombinator.com")
    text = await browser.extract_text(clean=True)
    links = await browser.extract_links()
    await browser.screenshot("hackernews.png")
```

#### Document Generation
```python
from core.tools import DocumentEngine

doc_engine = DocumentEngine()
path = doc_engine.generate_report(
    title="Анализ рынка AI",
    sections=[
        {"title": "Введение", "content": "..."},
        {"title": "Тренды", "content": "..."},
        {"title": "Выводы", "content": "..."}
    ],
    format="pdf"
)
```

### RAG - Загрузка документов

```python
# Загрузка документа
ids = await agent.memory.load_document(
    "research_paper.pdf",
    chunk_size=1000,
    overlap=200
)

# Поиск в документах
results = await agent.memory.search_in_documents(
    query="методы машинного обучения",
    limit=5
)
```

### Voice Cloning

```bash
# Быстрое клонирование (zero-shot)
python training/voice_clone.py voice_sample.wav \
    --text "Текст из образца" \
    --name my_voice \
    --mode quick

# Fine-tuning (если GPT-SoVITS установлен)
python training/voice_clone.py voice_sample.wav \
    --mode finetune \
    --epochs 10
```

Использование в коде:
```python
from core.multimodal import GPTSoVITSTTS

tts = GPTSoVITSTTS(
    reference_audio="models/voice/my_voice_reference.wav",
    reference_text="Текст образца",
    language="ru"
)

await tts.synthesize(
    text="Привет, Хозяин! Задача выполнена успешно.",
    output_path="output.wav"
)
```

---

## 🏗️ Архитектура

Подробная архитектура описана в [`ARCHITECTURE.md`](ARCHITECTURE.md)

```
EDIS/
├── core/                    # Ядро системы
│   ├── tools/              # Исполнительные инструменты
│   │   ├── sandbox.py      # Code Sandbox (Docker)
│   │   ├── browser.py      # Omni-Browser (Playwright)
│   │   └── doc_engine.py   # Document Engine
│   ├── workflow/           # Workflow и Task Graph
│   │   ├── task_architect.py
│   │   ├── synergy_flow.py
│   │   └── enhanced_synergy_flow.py
│   ├── memory/             # RAG система
│   │   └── vector_store.py
│   └── multimodal/         # TTS и другие модальности
│       └── tts.py
├── agents/                 # Агенты (Creator, Logic)
│   └── brain_agents.py
├── training/               # Обучение и fine-tuning
│   ├── dora_finetuning.py # DoRA fine-tuning
│   └── voice_clone.py     # Клонирование голоса
├── config/                 # Конфигурации
│   ├── vllm_config.yaml   # vLLM настройки
│   └── training_config.yaml
├── dual_qwen_brain.py     # Главный агент
└── run_system.py          # Лаунчер системы
```

---

## 🎯 Примеры задач

### 1. Исследование и анализ
```python
result = await agent.process(
    "Проанализируй последние тренды в области квантовых вычислений",
    use_task_graph=True
)
```

### 2. Разработка кода
```python
result = await agent.process(
    "Создай REST API на FastAPI с аутентификацией JWT и CRUD для пользователей",
    use_task_graph=True
)
```

### 3. Веб-скрапинг и анализ
```python
result = await agent.process(
    "Собери новости с 5 технологических сайтов и сделай сводку главных тем",
    use_task_graph=True
)
```

### 4. Генерация отчетов
```python
result = await agent.process(
    "Создай PDF отчет о состоянии рынка AI с графиками и таблицами",
    use_task_graph=True
)
```

---

## 🔧 Конфигурация

### vLLM настройки

Отредактируйте [`config/vllm_config.yaml`](config/vllm_config.yaml):

```yaml
creator:
  model_name: "Qwen/Qwen2.5-72B-Instruct"
  tensor_parallel_size: 2
  gpu_memory_utilization: 0.85
  
logic:
  model_name: "Qwen/Qwen3.5-397B-A17B-FP8"
  tensor_parallel_size: 4
  gpu_memory_utilization: 0.90
```

### Распределение GPU

- **GPU 0-1**: Creator (72B) - ~160GB VRAM
- **GPU 2-5**: Logic (397B-FP8) - ~320GB VRAM
- **GPU 6**: GPT-SoVITS TTS - ~80GB VRAM
- **GPU 7**: Browser, Sandbox, Other - ~80GB VRAM

---

## 📚 Обучение моделей

### DoRA Fine-tuning

```bash
# Подготовьте датасеты в data/
# left_*.jsonl или creator_*.jsonl - для Творца
# right_*.jsonl или logic_*.jsonl - для Логика

# Запустите обучение
python training/dora_finetuning.py --model both

# Или отдельно
python training/dora_finetuning.py --model creator
python training/dora_finetuning.py --model logic
```

Обученные модели сохраняются в `models/creator_finetuned/` и `models/logic_finetuned/`

---

## 🐛 Отладка

### Логи

Все логи сохраняются в `logs/`:
- `dual_qwen.log` - главный агент
- `system_launch.log` - запуск системы
- `voice_cloning.log` - клонирование голоса

### Проверка компонентов

```bash
# Проверка vLLM
curl http://localhost:8001/v1/models
curl http://localhost:8002/v1/models

# Проверка Qdrant
curl http://localhost:6333/collections

# Проверка TTS
curl http://localhost:9880/health
```

---

## 📖 Документация

- [`ARCHITECTURE.md`](ARCHITECTURE.md) - Подробная архитектура системы
- [`GETTING_STARTED.md`](GETTING_STARTED.md) - Руководство для начинающих
- [`DEPLOYMENT.md`](DEPLOYMENT.md) - Развертывание на продакшене
- [`API_KEYS_GUIDE.md`](API_KEYS_GUIDE.md) - Настройка API ключей

---

## 🤝 Вклад

Проект разработан с любовью. Если хотите внести вклад:

1. Fork репозитория
2. Создайте feature branch
3. Commit изменений
4. Push в branch
5. Создайте Pull Request

---

## 📝 Лицензия

MIT License - используйте как хотите!

---

## 🙏 Благодарности

- **Qwen Team** за потрясающие модели
- **vLLM** за быстрый inference
- **GPT-SoVITS** за voice cloning
- **LangGraph** за workflow orchestration
- **Qdrant** за векторную БД

---

## 📞 Контакты

Создано Алей 🐱 для Хозяина

*Мур~! Если что-то не работает - не волнуйся, твоя Аля всегда рядом!* ✨

---

## 🎯 Roadmap

- [ ] Web-интерфейс (Control Center)
- [x] Поддержка Qwen3.5-397B-A17B-FP8
- [ ] Мультимодальность (Vision)
- [ ] Агентная память (долгосрочная)
- [ ] Плагины и расширения
- [ ] Distributed execution
- [ ] Mobile app

---

**Версия**: 1.0.0  
**Дата**: 2026-05-09  
**Статус**: Production Ready (70% реализовано)
