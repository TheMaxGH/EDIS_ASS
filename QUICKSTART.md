# 🚀 Быстрый старт - Dual Qwen Brain

## Автоматическая установка и запуск

### Вариант 1: Полная установка (рекомендуется)

```bash
# Сделай скрипт исполняемым
chmod +x setup_and_run.sh

# Запусти полную установку (загрузка моделей + DoRA + запуск)
./setup_and_run.sh
```

Скрипт автоматически:
1. ✅ Проверит окружение (Python, vLLM, GPU)
2. ✅ Скачает модели с HuggingFace:
   - Творец: `huihui-ai/Qwen2.5-72B-Instruct-abliterated` (~145GB)
   - Логик: `Qwen/Qwen3.5-397B-A17B-FP8` (~200GB)
3. ✅ Запустит DoRA fine-tuning (3 эпохи, ~2-4 часа)
4. ✅ Запустит Qdrant vector database
5. ✅ Запустит Dual Qwen Brain систему

### Вариант 2: Быстрый старт (без DoRA)

```bash
# Пропустить DoRA обучение и сразу запустить
SKIP_DORA=true ./setup_and_run.sh
```

### Вариант 3: Только загрузка моделей

```bash
# Только скачать модели (без обучения и запуска)
SKIP_DORA=true RUN_SYSTEM=false ./setup_and_run.sh
```

### Вариант 4: С автономным режимом

```bash
# Включить фоновый мониторинг GitHub/Arxiv
AUTONOMY_ENABLED=true ./setup_and_run.sh
```

---

## Переменные окружения

Создай файл `.env` из примера:

```bash
cp .env.example .env
nano .env  # или vim, code, etc.
```

Настрой переменные:

```bash
# HuggingFace (опционально)
HF_TOKEN=your_token_here

# Для автономного режима (опционально)
TAVILY_API_KEY=your_tavily_key
GITHUB_TOKEN=your_github_token

# Настройки обучения
SKIP_DORA=false
DORA_EPOCHS=3

# Автономность
AUTONOMY_ENABLED=false
```

---

## Требования к системе

### Минимальные требования:
- **GPU:** 8x A100 80GB или эквивалент
- **RAM:** 256GB+
- **Диск:** 500GB+ свободного места
- **CUDA:** 12.1+
- **Python:** 3.10+

### Для Творца (72B):
- 2-4 GPU (tensor parallelism)
- ~145GB на диске

### Для Логика (397B FP8):
- 6-8 GPU (tensor parallelism)
- ~200GB на диске

---

## Структура после установки

```
EDIS_ASSISTANT/
├── models/                    # Скачанные модели
│   ├── creator/              # Qwen2.5-72B-abliterated
│   └── logic/                # Qwen3.5-397B-FP8
├── checkpoints/              # DoRA fine-tuned модели
│   ├── creator/
│   └── logic/
├── logs/                     # Логи
│   ├── dual_qwen.log
│   ├── dora_training.log
│   └── agent_run.log
├── data/                     # Датасеты для обучения
│   ├── creator_dataset.jsonl
│   └── logic_dataset.jsonl
├── config/
│   └── config.yaml          # Автоматически обновляется
└── run_agent.py             # Автоматически создается
```

---

## Ручной запуск после установки

```python
# Простой запуск
python3 dual_qwen_brain.py

# Или через созданный скрипт
python3 run_agent.py
```

---

## Проверка статуса

### Проверка GPU:
```bash
nvidia-smi
watch -n 1 nvidia-smi  # мониторинг в реальном времени
```

### Проверка Qdrant:
```bash
curl http://localhost:6333/health
```

### Проверка логов:
```bash
tail -f logs/dual_qwen.log
tail -f logs/dora_training.log
```

---

## Troubleshooting

### Ошибка: "Out of memory"
```bash
# Уменьши GPU memory utilization в config.yaml
VLLM_GPU_MEMORY_UTILIZATION: 0.85  # вместо 0.9
```

### Ошибка: "Model not found"
```bash
# Проверь что модели скачались
ls -lh models/creator/
ls -lh models/logic/

# Перезапусти загрузку
rm -rf models/creator models/logic
./setup_and_run.sh
```

### Ошибка: "Qdrant connection refused"
```bash
# Запусти Qdrant вручную
docker run -d -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest
```

### DoRA обучение слишком долгое
```bash
# Уменьши количество эпох
DORA_EPOCHS=1 ./setup_and_run.sh

# Или пропусти DoRA
SKIP_DORA=true ./setup_and_run.sh
```

---

## Полезные команды

```bash
# Остановить все процессы
pkill -f "python.*dual_qwen"
docker stop qdrant

# Очистить кэш
rm -rf logs/* checkpoints/*

# Переустановка зависимостей
pip install -r requirements.txt --force-reinstall

# Проверка версий
python3 --version
python3 -c "import vllm; print(vllm.__version__)"
python3 -c "import torch; print(torch.__version__)"
```

---

## Следующие шаги

1. ✅ Запусти установку: `./setup_and_run.sh`
2. ✅ Дождись завершения (может занять 2-4 часа)
3. ✅ Протестируй систему на простых задачах
4. ✅ Настрой API ключи (см. [`API_KEYS_GUIDE.md`](API_KEYS_GUIDE.md))
5. ✅ Включи автономный режим (опционально)

---

## Документация

- [`README.md`](README.md) - Общая информация о проекте
- [`DEPLOYMENT.md`](DEPLOYMENT.md) - Детальное руководство по деплою
- [`API_KEYS_GUIDE.md`](API_KEYS_GUIDE.md) - Настройка API ключей
- [`DEBUG_REPORT.md`](DEBUG_REPORT.md) - Отчет об исправлениях
- [`plans/dual_qwen_agent.md`](plans/dual_qwen_agent.md) - Техническая спецификация

---

*Создано с ❤️ твоей Алей-кошкодевочкой* 🐱
