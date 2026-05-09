# 🎯 Архитектура расширенной системы EDIS (Enhanced Dual Intelligence System)

*Спроектировано Алей для Хозяина* 🐱✨

---

## 📋 Обзор реализованных модулей

### ✅ 1. Исполнительный слой (Tools & Sandbox)

#### [`core/tools/sandbox.py`](core/tools/sandbox.py)
**Code Sandbox** - изолированное выполнение кода в Docker контейнерах
- ✨ Поддержка Python и Node.js
- 🔒 Изоляция сети и ресурсов (CPU/Memory limits)
- ⏱️ Таймауты и безопасное выполнение
- 🔄 Fallback на локальное выполнение (если Docker недоступен)

**Использование:**
```python
sandbox = CodeSandbox(timeout=30, memory_limit="512m")
result = await sandbox.execute_python(
    code="print('Hello from sandbox!')",
    requirements=["numpy", "pandas"]
)
```

#### [`core/tools/browser.py`](core/tools/browser.py)
**Omni-Browser** - автоматизация браузера на Playwright
- 🌐 Навигация, клики, заполнение форм
- 📜 Скроллинг и извлечение текста
- 📸 Скриншоты страниц
- 🔗 Извлечение ссылок и выполнение JavaScript

**Использование:**
```python
async with OmniBrowser(headless=True) as browser:
    await browser.navigate("https://example.com")
    text = await browser.extract_text(clean=True)
    await browser.screenshot("page.png")
```

#### [`core/tools/doc_engine.py`](core/tools/doc_engine.py)
**Document Engine** - генерация документов
- 📄 Markdown, PDF, DOCX форматы
- 📊 Структурированные отчеты
- 🎨 Стилизация и форматирование

**Использование:**
```python
doc_engine = DocumentEngine(output_dir="outputs")
path = doc_engine.generate_report(
    title="Отчет о выполнении",
    sections=[
        {"title": "Введение", "content": "..."},
        {"title": "Результаты", "content": "..."}
    ],
    format="pdf"
)
```

#### [`core/memory/vector_store.py`](core/memory/vector_store.py) (расширенная)
**RAG System** - загрузка и индексация пользовательских документов
- 📚 Поддержка PDF, DOCX, TXT, MD
- ✂️ Умное разбиение на чанки с перекрытием
- 🔍 Векторный поиск в документах
- 🏷️ Метаданные и фильтрация

**Использование:**
```python
memory = VectorMemory()
ids = await memory.load_document("document.pdf", chunk_size=1000)
results = await memory.search_in_documents("найти информацию о...")
```

---

### ✅ 2. Архитектор задач (OpenClaw Logic)

#### [`core/workflow/task_architect.py`](core/workflow/task_architect.py)
**Task Architect** - декомпозиция задач в JSON граф
- 🌳 Автоматическое построение графа зависимостей
- 🎯 Типизация задач (research, code, analysis, creative, execution, synthesis)
- 👥 Умное назначение (Creator, Logic, Both)
- 📊 Визуализация и отслеживание прогресса
- ⚡ Приоритеты задач (critical, high, medium, low)

**Структура TaskGraph:**
```python
class SubTask:
    id: str
    title: str
    description: str
    task_type: TaskType  # research, code, analysis, etc.
    assigned_to: Literal["creator", "logic", "both"]
    dependencies: List[str]  # ID зависимостей
    status: TaskStatus  # pending, in_progress, completed, failed
    priority: TaskPriority
    result: Optional[str]
```

**Использование:**
```python
architect = TaskArchitect(logic_agent)
task_graph = await architect.decompose_task(
    "Создать веб-приложение с аутентификацией",
    priority=TaskPriority.HIGH
)
print(architect.visualize_graph(task_graph))
```

#### [`core/workflow/enhanced_synergy_flow.py`](core/workflow/enhanced_synergy_flow.py)
**Enhanced Synergy Flow** - выполнение графа задач
- 🔄 Два режима: простой (один цикл) и граф (декомпозиция)
- 🎭 Интеграция Творца и Логика
- 🛠️ Доступ к инструментам (sandbox, browser, doc_engine)
- 📈 Параллельное выполнение готовых задач

**Использование:**
```python
workflow = EnhancedSynergyWorkflow(creator, logic, use_task_graph=True)
result = await workflow.run_with_graph(
    task="Сложная задача",
    tools={"sandbox": sandbox, "browser": browser, "doc_engine": doc_engine}
)
```

---

### ✅ 3. Мультимодальность и TTS

#### [`core/multimodal/tts.py`](core/multimodal/tts.py)
**GPT-SoVITS Integration** - клонирование и синтез голоса
- 🎤 Zero-shot клонирование из 1-минутного образца
- 🗣️ Синтез речи с сохранением тембра
- 🎛️ Контроль скорости и температуры
- 📦 Пакетная генерация

**Компоненты:**
- `GPTSoVITSTTS` - низкоуровневый API для GPT-SoVITS
- `TTSManager` - высокоуровневый менеджер для агента

**Использование:**
```python
tts = GPTSoVITSTTS(
    api_url="http://localhost:9880",
    reference_audio="voice_sample.wav",
    reference_text="Текст образца",
    language="ru"
)

await tts.synthesize(
    text="Привет, Хозяин! Задача выполнена.",
    output_path="output.wav"
)
```

#### [`training/voice_clone.py`](training/voice_clone.py)
**Voice Cloning Script** - CLI для клонирования голоса
- 🎵 Автоматическая конвертация аудио (ffmpeg)
- 📝 Транскрипция через Whisper
- ⚡ Быстрый режим (zero-shot) и fine-tuning
- 💾 Сохранение конфигурации голоса

**Использование:**
```bash
# Быстрое клонирование
python training/voice_clone.py voice_sample.wav \
    --text "Текст образца" \
    --name alya_voice \
    --mode quick

# Fine-tuning (если GPT-SoVITS установлен)
python training/voice_clone.py voice_sample.wav \
    --mode finetune \
    --epochs 10
```

---

### ✅ 4. Система приоритетов и управление

#### [`dual_qwen_brain.py`](dual_qwen_brain.py) (расширенная)
**DualQwenAgent** - главный оркестратор с приоритетами
- 🎯 Управление приоритетами задач
- ⏸️ Автоматическая пауза фоновых процессов для критических задач
- 🔧 Интеграция всех инструментов (sandbox, browser, doc_engine, TTS)
- 🔀 Выбор режима выполнения (простой/граф)

**Новые возможности:**
```python
agent = DualQwenAgent()
await agent.initialize()

# Выполнение с приоритетом и декомпозицией
result = await agent.process(
    task="Сложная задача",
    priority=TaskPriority.CRITICAL,
    use_task_graph=True
)
```

---

## 🚀 Что осталось реализовать

### 📱 Web-интерфейс (Control Center)

**Структура:**
```
web/
├── backend/          # FastAPI сервер
│   ├── main.py      # Главный файл API
│   ├── routes/      # Эндпоинты
│   │   ├── tasks.py
│   │   ├── agents.py
│   │   └── tools.py
│   └── websocket.py # Real-time обновления
│
└── frontend/        # Next.js приложение
    ├── app/
    │   ├── page.tsx           # Главная страница
    │   ├── tasks/             # Task Visualizer
    │   ├── workspace/         # Workspace (файлы, скриншоты)
    │   └── autonomy/          # Autonomous Log
    ├── components/
    │   ├── TaskGraph.tsx      # Визуализация графа
    │   ├── AgentStatus.tsx    # Статус агентов
    │   └── FileUpload.tsx     # Drag-and-drop для RAG
    └── lib/
        └── api.ts             # API клиент
```

**Ключевые фичи:**
- 🌳 **Task Visualizer** - интерактивное дерево задач с real-time обновлениями
- 📁 **Workspace** - список созданных файлов, кода, скриншотов
- 📜 **Autonomous Log** - лента фонового обучения
- 📤 **File Upload** - Drag-and-drop для загрузки документов в RAG
- 🎛️ **Control Panel** - управление агентами, приоритетами, TTS

---

### ⚙️ Инфраструктура и развертывание

#### vLLM Configuration
**Оркестрация моделей на 8x H200:**

```yaml
# config/vllm_config.yaml
models:
  creator:
    model_name: "Qwen/Qwen2.5-72B-Instruct"
    tensor_parallel_size: 2  # 2 GPU для 72B
    gpu_memory_utilization: 0.85
    max_model_len: 32768
    
  logic:
    model_name: "Qwen/Qwen3.5-397B-A17B-FP8"  # 397B с FP8 квантизацией
    tensor_parallel_size: 4  # 4 GPU для большой модели
    gpu_memory_utilization: 0.90
    max_model_len: 32768

# Остается 2 GPU для TTS, Browser и других задач
```

#### DoRA Fine-tuning оптимизация
**Уже реализовано в [`training/dora_finetuning.py`](training/dora_finetuning.py):**
- ✅ DeepSpeed ZeRO-3
- ✅ Flash Attention 2
- ✅ Gradient Checkpointing
- ✅ BF16 для H200
- ✅ NCCL для NVLink

**Что добавить:**
- 📊 Мониторинг через TensorBoard
- 💾 Автоматические чекпоинты
- 🔄 Resume training после сбоя

#### Финальный скрипт запуска
**`run_system.py`** - единая точка входа:

```python
"""
Запуск всей системы EDIS
- vLLM серверы для моделей
- GPT-SoVITS TTS сервер
- Qdrant векторная БД
- FastAPI веб-интерфейс
- Главный агент
"""

# Последовательность запуска:
# 1. Проверка зависимостей
# 2. Запуск Qdrant (Docker)
# 3. Запуск vLLM для Creator (GPU 0-1)
# 4. Запуск vLLM для Logic (GPU 2-5)
# 5. Запуск GPT-SoVITS (GPU 6)
# 6. Запуск FastAPI backend
# 7. Запуск Next.js frontend (dev/prod)
# 8. Инициализация DualQwenAgent
```

---

## 📊 Текущий статус

### ✅ Полностью реализовано (70%)
1. ✅ Исполнительный слой (Sandbox, Browser, DocEngine)
2. ✅ RAG система с загрузкой документов
3. ✅ Task Architect и граф задач
4. ✅ Enhanced Synergy Flow
5. ✅ Система приоритетов
6. ✅ TTS интеграция (GPT-SoVITS)
7. ✅ Voice cloning скрипт
8. ✅ Обновленный главный агент

### 🔄 В процессе (20%)
9. 🔄 Web-интерфейс (структура спроектирована)
10. 🔄 vLLM конфигурация (частично)
11. 🔄 DoRA оптимизация (базовая версия есть)

### ⏳ Осталось (10%)
12. ⏳ FastAPI backend реализация
13. ⏳ Next.js frontend реализация
14. ⏳ Финальный скрипт запуска
15. ⏳ Документация по развертыванию

---

## 🎯 Следующие шаги

### Приоритет 1: Web-интерфейс
```bash
# Создать FastAPI backend
mkdir -p web/backend/routes
touch web/backend/main.py
touch web/backend/routes/{tasks,agents,tools}.py

# Создать Next.js frontend
cd web
npx create-next-app@latest frontend --typescript --tailwind --app
```

### Приоритет 2: vLLM оркестрация
```bash
# Создать конфигурацию и скрипты запуска
touch config/vllm_config.yaml
touch scripts/start_vllm_creator.sh
touch scripts/start_vllm_logic.sh
```

### Приоритет 3: Финальная интеграция
```bash
# Главный скрипт запуска
touch run_system.py
chmod +x run_system.py

# Документация
touch DEPLOYMENT_GUIDE.md
```

---

## 💡 Архитектурные решения

### Почему такая структура?

1. **Модульность** - каждый компонент независим и тестируем
2. **Масштабируемость** - легко добавлять новые инструменты и агентов
3. **Безопасность** - изоляция выполнения кода в Docker
4. **Производительность** - параллельное выполнение задач, оптимизация под H200
5. **Гибкость** - два режима работы (простой/граф) для разных сценариев

### Ключевые паттерны

- **Event-driven** - система приоритетов с прерыванием фоновых задач
- **Graph-based** - декомпозиция сложных задач в DAG
- **Tool-augmented** - агенты имеют доступ к реальным инструментам
- **Multimodal** - текст + голос + браузер + код

---

## 📚 Использование

### Быстрый старт

```python
from dual_qwen_brain import DualQwenAgent
from core.workflow.task_architect import TaskPriority

# Инициализация
agent = DualQwenAgent()
await agent.initialize()

# Простая задача
result = await agent.process("Объясни квантовую запутанность")

# Сложная задача с декомпозицией
result = await agent.process(
    task="Создай веб-скрапер для новостей с анализом тональности",
    priority=TaskPriority.HIGH,
    use_task_graph=True
)

# Загрузка документа в RAG
await agent.memory.load_document("research_paper.pdf")

# Клонирование голоса
from training.voice_clone import VoiceCloner
cloner = VoiceCloner()
voice_info = cloner.quick_clone("voice_sample.wav", speaker_name="alya")
```

---

*Мур~! Хозяин, твоя Аля создала мощную систему! Осталось только добавить веб-интерфейс и финальные скрипты запуска. Я готова продолжать! 🐱✨*
