#!/bin/bash
# =============================================================================
# 🚀 Автономный скрипт запуска Dual Qwen Brain
# =============================================================================
# Этот скрипт:
# 1. Скачивает модели с HuggingFace
# 2. Запускает DoRA fine-tuning
# 3. Запускает Dual Qwen Brain систему
# =============================================================================

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Логирование
log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# =============================================================================
# Конфигурация
# =============================================================================

# Модели
CREATOR_MODEL="huihui-ai/Qwen2.5-72B-Instruct-abliterated"
LOGIC_MODEL="Qwen/Qwen3.5-397B-A17B-FP8"

# Директории
MODELS_DIR="./models"
CREATOR_DIR="${MODELS_DIR}/creator"
LOGIC_DIR="${MODELS_DIR}/logic"
LOGS_DIR="./logs"
CHECKPOINTS_DIR="./checkpoints"

# HuggingFace настройки
HF_TOKEN="${HF_TOKEN:-}"  # Опционально, для приватных моделей
HF_CACHE_DIR="${HF_HOME:-$HOME/.cache/huggingface}"

# DoRA настройки
SKIP_DORA="${SKIP_DORA:-false}"  # Установи в 'true' чтобы пропустить DoRA
DORA_EPOCHS="${DORA_EPOCHS:-3}"

# Запуск системы
AUTONOMY_ENABLED="${AUTONOMY_ENABLED:-false}"  # Автономный режим
RUN_SYSTEM="${RUN_SYSTEM:-true}"  # Запустить систему после обучения

# =============================================================================
# Проверка окружения
# =============================================================================

log_step "Проверка окружения..."

# Проверка Python
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 не найден. Установи Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
log_info "Python версия: ${PYTHON_VERSION}"

# Проверка vLLM
if ! python3 -c "import vllm" 2>/dev/null; then
    log_error "vLLM не установлен. Установи: pip install vllm"
    exit 1
fi
log_success "vLLM установлен"

# Проверка GPU
if ! command -v nvidia-smi &> /dev/null; then
    log_warning "nvidia-smi не найден. Убедись что CUDA установлена"
else
    GPU_COUNT=$(nvidia-smi --list-gpus | wc -l)
    log_info "Обнаружено GPU: ${GPU_COUNT}"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
fi

# Проверка свободного места
AVAILABLE_SPACE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
REQUIRED_SPACE=500  # GB
if [ "$AVAILABLE_SPACE" -lt "$REQUIRED_SPACE" ]; then
    log_warning "Мало места на диске: ${AVAILABLE_SPACE}GB (рекомендуется ${REQUIRED_SPACE}GB+)"
else
    log_success "Свободно места: ${AVAILABLE_SPACE}GB"
fi

# =============================================================================
# Создание директорий
# =============================================================================

log_step "Создание директорий..."

mkdir -p "${MODELS_DIR}"
mkdir -p "${CREATOR_DIR}"
mkdir -p "${LOGIC_DIR}"
mkdir -p "${LOGS_DIR}"
mkdir -p "${CHECKPOINTS_DIR}"
mkdir -p "${CHECKPOINTS_DIR}/creator"
mkdir -p "${CHECKPOINTS_DIR}/logic"

log_success "Директории созданы"

# =============================================================================
# Установка зависимостей
# =============================================================================

log_step "Установка зависимостей..."

if [ ! -f "requirements.txt" ]; then
    log_error "requirements.txt не найден"
    exit 1
fi

pip install -q --upgrade pip
pip install -q -r requirements.txt

log_success "Зависимости установлены"

# =============================================================================
# Загрузка моделей с HuggingFace
# =============================================================================

download_model() {
    local model_name=$1
    local target_dir=$2
    local model_type=$3
    
    log_step "Загрузка ${model_type}: ${model_name}..."
    
    # Проверка существования модели
    if [ -d "${target_dir}" ] && [ "$(ls -A ${target_dir})" ]; then
        log_warning "Модель уже существует в ${target_dir}"
        read -p "Перезагрузить? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Пропуск загрузки ${model_type}"
            return 0
        fi
        rm -rf "${target_dir}"
        mkdir -p "${target_dir}"
    fi
    
    # Загрузка через huggingface-cli
    log_info "Начинаю загрузку... (это может занять 30-60 минут)"
    
    if [ -n "$HF_TOKEN" ]; then
        huggingface-cli download "${model_name}" \
            --local-dir "${target_dir}" \
            --local-dir-use-symlinks False \
            --token "${HF_TOKEN}" \
            --resume-download
    else
        huggingface-cli download "${model_name}" \
            --local-dir "${target_dir}" \
            --local-dir-use-symlinks False \
            --resume-download
    fi
    
    if [ $? -eq 0 ]; then
        log_success "${model_type} загружен: ${target_dir}"
    else
        log_error "Ошибка загрузки ${model_type}"
        exit 1
    fi
}

# Загрузка Творца
download_model "${CREATOR_MODEL}" "${CREATOR_DIR}" "Творец (Creator)"

# Загрузка Логика
download_model "${LOGIC_MODEL}" "${LOGIC_DIR}" "Логик (Logic)"

# =============================================================================
# Обновление конфигурации
# =============================================================================

log_step "Обновление конфигурации..."

cat > config/config.yaml << EOF
# Конфигурация моделей (обновлено автоматически)
CREATOR_MODEL: "${CREATOR_DIR}"
LOGIC_MODEL: "${LOGIC_DIR}"

# Параметры генерации
CREATOR_TEMPERATURE: 1.2
CREATOR_TOP_P: 0.95
CREATOR_MAX_TOKENS: 2048

LOGIC_TEMPERATURE: 0.1
LOGIC_TOP_P: 0.9
LOGIC_MAX_TOKENS: 4096

# vLLM настройки
VLLM_TENSOR_PARALLEL_SIZE: ${GPU_COUNT:-8}
VLLM_GPU_MEMORY_UTILIZATION: 0.9
VLLM_MAX_MODEL_LEN: 32768

# Qdrant настройки
QDRANT_HOST: "localhost"
QDRANT_PORT: 6333
QDRANT_COLLECTION: "dual_qwen_memory"
QDRANT_VECTOR_SIZE: 1024

# Tavily API (опционально)
TAVILY_API_KEY: "your_tavily_api_key_here"

# GitHub мониторинг (опционально)
GITHUB_TOKEN: "your_github_token_here"
GITHUB_TRENDING_TAGS: ["AI", "LLM", "Rust", "Python"]

# Режим автономности
AUTONOMY_ENABLED: ${AUTONOMY_ENABLED}
AUTONOMY_CHECK_INTERVAL: 3600
AUTONOMY_MAX_ARTICLES: 10

# Конфликт-резолюция
MAX_CONFLICT_RETRIES: 3
CONFLICT_THRESHOLD: 0.7

# Логирование
LOG_LEVEL: "INFO"
LOG_FILE: "logs/dual_qwen.log"
EOF

log_success "Конфигурация обновлена"

# =============================================================================
# DoRA Fine-tuning
# =============================================================================

if [ "$SKIP_DORA" = "false" ]; then
    log_step "Запуск DoRA fine-tuning..."
    
    # Проверка датасетов
    if [ ! -f "data/creator_dataset.jsonl" ] || [ ! -f "data/logic_dataset.jsonl" ]; then
        log_warning "Датасеты не найдены. Создаю примеры..."
        mkdir -p data
        
        # Создание примера датасета для Творца
        cat > data/creator_dataset.jsonl << 'EOFDATA'
{"instruction": "Предложи инновационный подход к кэшированию в распределенной системе", "input": "", "output": "Рассмотрим гибридный подход с многоуровневым кэшированием:\n1. L1: In-memory кэш с LRU\n2. L2: Redis cluster для горячих данных\n3. L3: Distributed cache с consistent hashing\n\nИнновация: предиктивная предзагрузка на основе ML-модели, анализирующей паттерны доступа."}
{"instruction": "Как можно улучшить производительность GraphQL API?", "input": "", "output": "Креативные решения:\n1. DataLoader с батчингом запросов\n2. Персистентные запросы (query whitelisting)\n3. Автоматическая генерация SQL JOIN из GraphQL схемы\n4. Edge caching с CDN\n5. Streaming responses для больших датасетов"}
EOFDATA
        
        # Создание примера датасета для Логика
        cat > data/logic_dataset.jsonl << 'EOFDATA'
{"instruction": "Проверь корректность этого алгоритма сортировки", "input": "def sort(arr):\n    for i in range(len(arr)):\n        for j in range(i+1, len(arr)):\n            if arr[i] > arr[j]:\n                arr[i], arr[j] = arr[j], arr[i]\n    return arr", "output": "Анализ:\n✓ Алгоритм корректен (bubble sort вариация)\n✓ Временная сложность: O(n²)\n✓ Пространственная сложность: O(1)\n⚠ Рекомендация: использовать встроенный sorted() или quicksort для больших массивов\n\nТесты:\nassert sort([3,1,2]) == [1,2,3]\nassert sort([]) == []\nassert sort([1]) == [1]"}
{"instruction": "Найди ошибки в этом SQL запросе", "input": "SELECT * FROM users WHERE id = '123' AND deleted = false ORDER BY created_at", "output": "Обнаруженные проблемы:\n1. ❌ SELECT * - избегай, указывай конкретные поля\n2. ⚠ id = '123' - если id числовой, убери кавычки\n3. ✓ deleted = false - корректно\n4. ⚠ Отсутствует LIMIT - может вернуть много строк\n\nИсправленный запрос:\nSELECT id, name, email, created_at \nFROM users \nWHERE id = 123 AND deleted = false \nORDER BY created_at DESC \nLIMIT 100"}
EOFDATA
        
        log_success "Примеры датасетов созданы"
    fi
    
    # Запуск DoRA обучения
    log_info "Начинаю DoRA fine-tuning (это займет несколько часов)..."
    log_info "Эпохи: ${DORA_EPOCHS}"
    
    python3 training/dora_finetuning.py \
        --creator_model "${CREATOR_DIR}" \
        --logic_model "${LOGIC_DIR}" \
        --creator_dataset "data/creator_dataset.jsonl" \
        --logic_dataset "data/logic_dataset.jsonl" \
        --output_dir "${CHECKPOINTS_DIR}" \
        --epochs "${DORA_EPOCHS}" \
        --batch_size 4 \
        --learning_rate 2e-4 \
        2>&1 | tee "${LOGS_DIR}/dora_training.log"
    
    if [ $? -eq 0 ]; then
        log_success "DoRA fine-tuning завершен"
        
        # Обновление путей к моделям на fine-tuned версии
        CREATOR_DIR="${CHECKPOINTS_DIR}/creator"
        LOGIC_DIR="${CHECKPOINTS_DIR}/logic"
        
        # Обновление конфига
        sed -i "s|CREATOR_MODEL:.*|CREATOR_MODEL: \"${CREATOR_DIR}\"|" config/config.yaml
        sed -i "s|LOGIC_MODEL:.*|LOGIC_MODEL: \"${LOGIC_DIR}\"|" config/config.yaml
        
        log_success "Конфигурация обновлена на fine-tuned модели"
    else
        log_error "Ошибка DoRA fine-tuning"
        log_warning "Продолжаю с базовыми моделями..."
    fi
else
    log_info "DoRA fine-tuning пропущен (SKIP_DORA=true)"
fi

# =============================================================================
# Запуск Qdrant
# =============================================================================

log_step "Проверка Qdrant..."

if ! curl -s http://localhost:6333/health > /dev/null 2>&1; then
    log_warning "Qdrant не запущен. Запускаю через Docker..."
    
    if command -v docker &> /dev/null; then
        docker run -d \
            --name qdrant \
            -p 6333:6333 \
            -p 6334:6334 \
            -v $(pwd)/qdrant_storage:/qdrant/storage \
            qdrant/qdrant:latest
        
        log_info "Ожидание запуска Qdrant..."
        sleep 10
        
        if curl -s http://localhost:6333/health > /dev/null 2>&1; then
            log_success "Qdrant запущен"
        else
            log_error "Не удалось запустить Qdrant"
            exit 1
        fi
    else
        log_error "Docker не найден. Установи Qdrant вручную: https://qdrant.tech/documentation/quick-start/"
        exit 1
    fi
else
    log_success "Qdrant уже запущен"
fi

# =============================================================================
# Запуск Dual Qwen Brain
# =============================================================================

if [ "$RUN_SYSTEM" = "true" ]; then
    log_step "Запуск Dual Qwen Brain системы..."
    
    # Создание скрипта запуска
    cat > run_agent.py << 'EOFPYTHON'
import asyncio
import sys
from dual_qwen_brain import DualQwenAgent

async def main():
    print("🧠 Инициализация Dual Qwen Brain...")
    
    agent = DualQwenAgent(config_path="config/config.yaml")
    
    try:
        await agent.initialize()
        print("✅ Система инициализирована")
        
        # Тестовая задача
        print("\n🚀 Запуск тестовой задачи...")
        result = await agent.process(
            "Создай REST API для управления задачами с использованием FastAPI. "
            "Включи CRUD операции, валидацию данных и документацию."
        )
        
        print("\n" + "="*80)
        print("📊 РЕЗУЛЬТАТ:")
        print("="*80)
        print(result)
        print("="*80)
        
        # Запуск автономного режима (если включен)
        config = agent.config
        if config.get('AUTONOMY_ENABLED', False):
            print("\n🌙 Запуск автономного режима...")
            await agent.start_autonomy()
            print("✅ Автономный режим активен")
            print("💡 Система будет мониторить GitHub, Arxiv и tech новости")
            print("⏰ Интервал проверки: {} секунд".format(
                config.get('AUTONOMY_CHECK_INTERVAL', 3600)
            ))
            
            # Держим систему запущенной
            print("\n⌨️  Нажми Ctrl+C для остановки...")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Остановка системы...")
                agent.stop_autonomy()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    finally:
        await agent.shutdown()
        print("👋 Система остановлена")
    
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
EOFPYTHON
    
    log_success "Скрипт запуска создан"
    
    # Запуск
    log_info "Запускаю агента..."
    python3 run_agent.py 2>&1 | tee "${LOGS_DIR}/agent_run.log"
    
else
    log_info "Автоматический запуск системы пропущен (RUN_SYSTEM=false)"
    log_info "Для запуска вручную: python3 dual_qwen_brain.py"
fi

# =============================================================================
# Завершение
# =============================================================================

log_success "🎉 Установка завершена!"
echo ""
echo "📁 Структура:"
echo "   Модели:      ${MODELS_DIR}/"
echo "   Чекпоинты:   ${CHECKPOINTS_DIR}/"
echo "   Логи:        ${LOGS_DIR}/"
echo "   Конфиг:      config/config.yaml"
echo ""
echo "🚀 Для запуска системы:"
echo "   python3 dual_qwen_brain.py"
echo ""
echo "📚 Документация:"
echo "   README.md           - Общая информация"
echo "   DEPLOYMENT.md       - Руководство по деплою"
echo "   API_KEYS_GUIDE.md   - Настройка API ключей"
echo "   DEBUG_REPORT.md     - Отчет об исправлениях"
echo ""
echo "💡 Полезные команды:"
echo "   # Пропустить DoRA и сразу запустить"
echo "   SKIP_DORA=true ./setup_and_run.sh"
echo ""
echo "   # Включить автономный режим"
echo "   AUTONOMY_ENABLED=true ./setup_and_run.sh"
echo ""
echo "   # Только загрузить модели (без обучения и запуска)"
echo "   SKIP_DORA=true RUN_SYSTEM=false ./setup_and_run.sh"
echo ""
