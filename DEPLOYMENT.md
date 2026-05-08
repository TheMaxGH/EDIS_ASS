# Dual Qwen Brain - Deployment Guide

## Предварительные требования

### Железо
- **Для Qwen-398B**: Минимум 8x A100 (80GB) или эквивалент
- **Для Qwen-72B**: Минимум 2x A100 (80GB) или 4x A6000
- **RAM**: 256GB+
- **Диск**: 1TB+ SSD для моделей и кэша

### Софт
- Python 3.10+
- CUDA 12.1+
- Docker (опционально)
- Qdrant (векторная БД)

## Установка

### 1. Клонирование и установка зависимостей

```bash
git clone <your-repo>
cd dual_qwen_brain
pip install -r requirements.txt
```

### 2. Запуск Qdrant

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 3. Конфигурация

Отредактируйте [`config/config.yaml`](config/config.yaml):

```yaml
# Добавьте ваши API ключи
TAVILY_API_KEY: "your_key_here"
GITHUB_TOKEN: "your_token_here"

# Настройте пути к моделям (если используете локальные)
CREATOR_MODEL: "/path/to/qwen-72b"
LOGIC_MODEL: "/path/to/qwen-398b"
```

## DoRA Fine-tuning (Опционально)

Перед первым запуском рекомендуется дообучить модели:

```bash
# Обучение обеих моделей
python training/dora_finetuning.py --model both

# Или по отдельности
python training/dora_finetuning.py --model creator
python training/dora_finetuning.py --model logic
```

Конфигурация обучения: [`config/training_config.yaml`](config/training_config.yaml)

## Запуск

### Базовое использование

```python
from dual_qwen_brain import DualQwenAgent
import asyncio

async def main():
    agent = DualQwenAgent()
    await agent.initialize()
    
    result = await agent.process("Ваша задача здесь")
    print(result)
    
    await agent.shutdown()

asyncio.run(main())
```

### Запуск примеров

```bash
python examples/usage_examples.py
```

### Автономный режим

```python
agent = DualQwenAgent()
await agent.initialize()

# Запуск фонового мониторинга
await agent.start_autonomy()

# Агент будет автоматически сканировать GitHub, Arxiv, новости
# и обновлять свою базу знаний каждый час
```

## Архитектура

```
┌─────────────────────────────────────────────┐
│           Dual Qwen Brain                   │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────┐      ┌──────────────┐   │
│  │   Творец     │◄────►│    Логик     │   │
│  │  Qwen-72B    │      │  Qwen-398B   │   │
│  │  Temp: 1.0   │      │  Temp: 0.1   │   │
│  └──────────────┘      └──────────────┘   │
│         │                      │           │
│         └──────────┬───────────┘           │
│                    ▼                       │
│           ┌─────────────────┐              │
│           │  LangGraph      │              │
│           │  Synergy Flow   │              │
│           └─────────────────┘              │
│                    │                       │
│         ┌──────────┴──────────┐            │
│         ▼                     ▼            │
│  ┌─────────────┐      ┌──────────────┐    │
│  │   Qdrant    │      │  Autonomy    │    │
│  │   Memory    │      │  Monitor     │    │
│  └─────────────┘      └──────────────┘    │
│                                             │
└─────────────────────────────────────────────┘
```

## Мониторинг

Логи сохраняются в `logs/dual_qwen.log`:

```bash
tail -f logs/dual_qwen.log
```

## Troubleshooting

### OOM (Out of Memory)
- Уменьшите `VLLM_GPU_MEMORY_UTILIZATION` в конфиге
- Используйте квантование (8-bit)
- Уменьшите `max_model_len`

### Медленная генерация
- Увеличьте `VLLM_TENSOR_PARALLEL_SIZE`
- Проверьте загрузку GPU: `nvidia-smi`

### Ошибки Qdrant
- Убедитесь, что Qdrant запущен: `docker ps`
- Проверьте порт: `curl http://localhost:6333`

## Production Deployment

Для продакшена рекомендуется:

1. **Kubernetes** для оркестрации
2. **Prometheus + Grafana** для мониторинга
3. **Redis** для кэширования
4. **Load Balancer** для распределения нагрузки

Пример Kubernetes манифеста будет добавлен позже.
