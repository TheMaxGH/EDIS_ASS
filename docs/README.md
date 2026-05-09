# 📚 EDIS Documentation

Полная документация проекта EDIS (Enhanced Dual Intelligence System).

## 📖 Основные документы

### Для начинающих

- **[MASTER_README.md](../MASTER_README.md)** - 🚀 Полное руководство для новичков
  - Системные требования
  - Пошаговая установка
  - Первый запуск
  - Решение проблем

### Архитектура

- **[ARCHITECTURE.md](../ARCHITECTURE.md)** - 🏗️ Архитектура системы
  - Dual-Agent система (Creator + Logic)
  - Компоненты и модули
  - Workflow и граф задач

- **[AUDIO_ARCHITECTURE.md](AUDIO_ARCHITECTURE.md)** - 🎤 Аудио архитектура
  - GPT-SoVITS интеграция
  - TTS/STT потоки данных
  - Компоненты и API

### API Reference

- **[TTS_API_REFERENCE.md](TTS_API_REFERENCE.md)** - 📡 Voice API справка
  - Endpoints документация
  - Примеры кода (Python, JS/TS)
  - Best practices

### Быстрые гайды

- **[QUICKSTART.md](../QUICKSTART.md)** - ⚡ Быстрый старт
- **[WEB_QUICKSTART.md](../WEB_QUICKSTART.md)** - 🌐 Запуск веб-интерфейса
- **[GETTING_STARTED.md](../GETTING_STARTED.md)** - 🎯 Начало работы

### Настройка

- **[API_KEYS_GUIDE.md](../API_KEYS_GUIDE.md)** - 🔑 Получение API ключей
- **[UI_SETTINGS_GUIDE.md](../UI_SETTINGS_GUIDE.md)** - ⚙️ Настройка через UI
- **[GITHUB_SETUP.md](../GITHUB_SETUP.md)** - 🐙 Настройка GitHub

### Деплой и оптимизация

- **[DEPLOYMENT.md](../DEPLOYMENT.md)** - 🚀 Деплой в продакшн
- **[H200_OPTIMIZATIONS.md](../H200_OPTIMIZATIONS.md)** - ⚡ Оптимизации для H200

## 🗂️ Планы развития

Директория [`plans/`](../plans/) содержит детальные планы:

- **[gpt_sovits_integration_plan.md](../plans/gpt_sovits_integration_plan.md)** - План интеграции TTS
- **[INTEGRATION_SUMMARY.md](../plans/INTEGRATION_SUMMARY.md)** - Сводка по интеграции
- **[web_interface_plan.md](../plans/web_interface_plan.md)** - План веб-интерфейса
- **[dual_qwen_agent.md](../plans/dual_qwen_agent.md)** - Dual-Agent архитектура

## 🎓 Примеры использования

```python
# Примеры в examples/usage_examples.py
from dual_qwen_brain import DualQwenAgent

agent = DualQwenAgent()
await agent.initialize()

# Простая задача
result = await agent.process("Создай REST API для управления пользователями")

# С графом выполнения
result = await agent.process(
    "Разработай микросервис для обработки платежей",
    use_graph=True,
    priority="high"
)
```

## 🔗 Внешние ресурсы

### Модели

- [Qwen2.5-72B](https://huggingface.co/Qwen/Qwen2.5-72B-Instruct) - Creator модель
- [Qwen3.5-397B-FP8](https://huggingface.co/Qwen/Qwen3.5-397B-A17B-FP8) - Logic модель
- [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) - TTS система

### Инструменты

- [vLLM](https://docs.vllm.ai/) - Inference engine
- [Qdrant](https://qdrant.tech/documentation/) - Vector database
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [Next.js](https://nextjs.org/docs) - Frontend framework

## 📊 Структура проекта

```
EDIS_ASSISTANT/
├── docs/                    # 📚 Документация
│   ├── AUDIO_ARCHITECTURE.md
│   └── TTS_API_REFERENCE.md
├── plans/                   # 📋 Планы развития
├── config/                  # ⚙️ Конфигурации
│   ├── vllm_config.yaml
│   └── gpt_sovits_config.yaml
├── core/                    # 🧠 Ядро системы
│   ├── models/             # Обертки моделей
│   ├── workflow/           # Workflow engine
│   ├── multimodal/         # TTS/STT
│   ├── memory/             # Vector store
│   └── tools/              # Инструменты
├── agents/                  # 🤖 Агенты
│   └── brain_agents.py     # Creator + Logic
├── web/                     # 🌐 Веб-интерфейс
│   ├── backend/            # FastAPI
│   └── frontend/           # Next.js + React
├── training/                # 🎓 Обучение
│   ├── voice_clone.py      # Клонирование голоса
│   └── dora_finetuning.py  # Fine-tuning
├── scripts/                 # 🔧 Скрипты
└── examples/                # 💡 Примеры
```

## 🆘 Поддержка

### Проблемы с установкой?

1. Проверьте [MASTER_README.md](../MASTER_README.md) → Раздел "Решение проблем"
2. Проверьте логи: `logs/system_launch.log`
3. Создайте Issue в репозитории

### Вопросы по API?

1. См. [TTS_API_REFERENCE.md](TTS_API_REFERENCE.md)
2. См. [AUDIO_ARCHITECTURE.md](AUDIO_ARCHITECTURE.md)
3. Примеры кода в документации

### Проблемы с производительностью?

1. См. [H200_OPTIMIZATIONS.md](../H200_OPTIMIZATIONS.md)
2. Проверьте `nvidia-smi`
3. Уменьшите `max_model_len` в конфиге

## 📝 Вклад в документацию

Нашли ошибку или хотите улучшить документацию?

1. Fork репозитория
2. Создайте ветку: `git checkout -b docs/improve-readme`
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License - см. [LICENSE](../LICENSE)

---

**Документация обновлена:** 2026-05-09

*Создано с ❤️ командой EDIS*
