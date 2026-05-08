@echo off
REM =============================================================================
REM Автономный скрипт запуска Dual Qwen Brain для Windows
REM =============================================================================
setlocal enabledelayedexpansion

echo.
echo ========================================================================
echo   Dual Qwen Brain - Автоматическая установка и запуск
echo ========================================================================
echo.

REM Цвета для Windows (через PowerShell)
set "INFO=[INFO]"
set "SUCCESS=[SUCCESS]"
set "WARNING=[WARNING]"
set "ERROR=[ERROR]"
set "STEP=[STEP]"

REM =============================================================================
REM Конфигурация
REM =============================================================================

set "CREATOR_MODEL=huihui-ai/Qwen2.5-72B-Instruct-abliterated"
set "LOGIC_MODEL=Qwen/Qwen3.5-397B-A17B-FP8"

set "MODELS_DIR=.\models"
set "CREATOR_DIR=%MODELS_DIR%\creator"
set "LOGIC_DIR=%MODELS_DIR%\logic"
set "LOGS_DIR=.\logs"
set "CHECKPOINTS_DIR=.\checkpoints"

REM Настройки из переменных окружения или значения по умолчанию
if not defined SKIP_DORA set "SKIP_DORA=false"
if not defined DORA_EPOCHS set "DORA_EPOCHS=3"
if not defined AUTONOMY_ENABLED set "AUTONOMY_ENABLED=false"
if not defined RUN_SYSTEM set "RUN_SYSTEM=true"

REM =============================================================================
REM Проверка окружения
REM =============================================================================

echo %STEP% Проверка окружения...
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo %ERROR% Python не найден. Установи Python 3.10+
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %INFO% Python версия: %PYTHON_VERSION%

REM Проверка vLLM
python -c "import vllm" >nul 2>&1
if errorlevel 1 (
    echo %ERROR% vLLM не установлен. Установи: pip install vllm
    exit /b 1
)
echo %SUCCESS% vLLM установлен

REM Проверка GPU
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo %WARNING% nvidia-smi не найден. Убедись что CUDA установлена
) else (
    echo %INFO% Информация о GPU:
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
)

echo.

REM =============================================================================
REM Создание директорий
REM =============================================================================

echo %STEP% Создание директорий...

if not exist "%MODELS_DIR%" mkdir "%MODELS_DIR%"
if not exist "%CREATOR_DIR%" mkdir "%CREATOR_DIR%"
if not exist "%LOGIC_DIR%" mkdir "%LOGIC_DIR%"
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"
if not exist "%CHECKPOINTS_DIR%" mkdir "%CHECKPOINTS_DIR%"
if not exist "%CHECKPOINTS_DIR%\creator" mkdir "%CHECKPOINTS_DIR%\creator"
if not exist "%CHECKPOINTS_DIR%\logic" mkdir "%CHECKPOINTS_DIR%\logic"
if not exist "data" mkdir "data"

echo %SUCCESS% Директории созданы
echo.

REM =============================================================================
REM Установка зависимостей
REM =============================================================================

echo %STEP% Установка зависимостей...

if not exist "requirements.txt" (
    echo %ERROR% requirements.txt не найден
    exit /b 1
)

python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet

echo %SUCCESS% Зависимости установлены
echo.

REM =============================================================================
REM Загрузка моделей
REM =============================================================================

echo %STEP% Загрузка моделей с HuggingFace...
echo.

REM Функция загрузки модели для Творца
echo %INFO% Загрузка Творца: %CREATOR_MODEL%
if exist "%CREATOR_DIR%\config.json" (
    echo %WARNING% Модель Творца уже существует в %CREATOR_DIR%
    set /p "REPLY=Перезагрузить? (y/N): "
    if /i not "!REPLY!"=="y" (
        echo %INFO% Пропуск загрузки Творца
        goto skip_creator
    )
    rmdir /s /q "%CREATOR_DIR%"
    mkdir "%CREATOR_DIR%"
)

echo %INFO% Начинаю загрузку Творца... (это может занять 30-60 минут)
if defined HF_TOKEN (
    huggingface-cli download "%CREATOR_MODEL%" --local-dir "%CREATOR_DIR%" --local-dir-use-symlinks False --token "%HF_TOKEN%" --resume-download
) else (
    huggingface-cli download "%CREATOR_MODEL%" --local-dir "%CREATOR_DIR%" --local-dir-use-symlinks False --resume-download
)

if errorlevel 1 (
    echo %ERROR% Ошибка загрузки Творца
    exit /b 1
)
echo %SUCCESS% Творец загружен: %CREATOR_DIR%
echo.

:skip_creator

REM Функция загрузки модели для Логика
echo %INFO% Загрузка Логика: %LOGIC_MODEL%
if exist "%LOGIC_DIR%\config.json" (
    echo %WARNING% Модель Логика уже существует в %LOGIC_DIR%
    set /p "REPLY=Перезагрузить? (y/N): "
    if /i not "!REPLY!"=="y" (
        echo %INFO% Пропуск загрузки Логика
        goto skip_logic
    )
    rmdir /s /q "%LOGIC_DIR%"
    mkdir "%LOGIC_DIR%"
)

echo %INFO% Начинаю загрузку Логика... (это может занять 30-60 минут)
if defined HF_TOKEN (
    huggingface-cli download "%LOGIC_MODEL%" --local-dir "%LOGIC_DIR%" --local-dir-use-symlinks False --token "%HF_TOKEN%" --resume-download
) else (
    huggingface-cli download "%LOGIC_MODEL%" --local-dir "%LOGIC_DIR%" --local-dir-use-symlinks False --resume-download
)

if errorlevel 1 (
    echo %ERROR% Ошибка загрузки Логика
    exit /b 1
)
echo %SUCCESS% Логик загружен: %LOGIC_DIR%
echo.

:skip_logic

REM =============================================================================
REM Обновление конфигурации
REM =============================================================================

echo %STEP% Обновление конфигурации...

REM Подсчет GPU (упрощенная версия для Windows)
set GPU_COUNT=8

(
echo # Конфигурация моделей ^(обновлено автоматически^)
echo CREATOR_MODEL: "%CREATOR_DIR%"
echo LOGIC_MODEL: "%LOGIC_DIR%"
echo.
echo # Параметры генерации
echo CREATOR_TEMPERATURE: 1.2
echo CREATOR_TOP_P: 0.95
echo CREATOR_MAX_TOKENS: 2048
echo.
echo LOGIC_TEMPERATURE: 0.1
echo LOGIC_TOP_P: 0.9
echo LOGIC_MAX_TOKENS: 4096
echo.
echo # vLLM настройки
echo VLLM_TENSOR_PARALLEL_SIZE: %GPU_COUNT%
echo VLLM_GPU_MEMORY_UTILIZATION: 0.9
echo VLLM_MAX_MODEL_LEN: 32768
echo.
echo # Qdrant настройки
echo QDRANT_HOST: "localhost"
echo QDRANT_PORT: 6333
echo QDRANT_COLLECTION: "dual_qwen_memory"
echo QDRANT_VECTOR_SIZE: 1024
echo.
echo # Tavily API ^(опционально^)
echo TAVILY_API_KEY: "your_tavily_api_key_here"
echo.
echo # GitHub мониторинг ^(опционально^)
echo GITHUB_TOKEN: "your_github_token_here"
echo GITHUB_TRENDING_TAGS: ["AI", "LLM", "Rust", "Python"]
echo.
echo # Режим автономности
echo AUTONOMY_ENABLED: %AUTONOMY_ENABLED%
echo AUTONOMY_CHECK_INTERVAL: 3600
echo AUTONOMY_MAX_ARTICLES: 10
echo.
echo # Конфликт-резолюция
echo MAX_CONFLICT_RETRIES: 3
echo CONFLICT_THRESHOLD: 0.7
echo.
echo # Логирование
echo LOG_LEVEL: "INFO"
echo LOG_FILE: "logs/dual_qwen.log"
) > config\config.yaml

echo %SUCCESS% Конфигурация обновлена
echo.

REM =============================================================================
REM Создание примеров датасетов
REM =============================================================================

if not exist "data\creator_dataset.jsonl" (
    echo %INFO% Создание примеров датасетов...
    
    (
    echo {"instruction": "Предложи инновационный подход к кэшированию в распределенной системе", "input": "", "output": "Рассмотрим гибридный подход с многоуровневым кэшированием:\n1. L1: In-memory кэш с LRU\n2. L2: Redis cluster для горячих данных\n3. L3: Distributed cache с consistent hashing\n\nИнновация: предиктивная предзагрузка на основе ML-модели, анализирующей паттерны доступа."}
    echo {"instruction": "Как можно улучшить производительность GraphQL API?", "input": "", "output": "Креативные решения:\n1. DataLoader с батчингом запросов\n2. Персистентные запросы ^(query whitelisting^)\n3. Автоматическая генерация SQL JOIN из GraphQL схемы\n4. Edge caching с CDN\n5. Streaming responses для больших датасетов"}
    ) > data\creator_dataset.jsonl
    
    (
    echo {"instruction": "Проверь корректность этого алгоритма сортировки", "input": "def sort^(arr^):\n    for i in range^(len^(arr^)^):\n        for j in range^(i+1, len^(arr^)^):\n            if arr[i] ^> arr[j]:\n                arr[i], arr[j] = arr[j], arr[i]\n    return arr", "output": "Анализ:\n✓ Алгоритм корректен ^(bubble sort вариация^)\n✓ Временная сложность: O^(n²^)\n✓ Пространственная сложность: O^(1^)\n⚠ Рекомендация: использовать встроенный sorted^(^) или quicksort для больших массивов"}
    echo {"instruction": "Найди ошибки в этом SQL запросе", "input": "SELECT * FROM users WHERE id = '123' AND deleted = false ORDER BY created_at", "output": "Обнаруженные проблемы:\n1. ❌ SELECT * - избегай, указывай конкретные поля\n2. ⚠ id = '123' - если id числовой, убери кавычки\n3. ✓ deleted = false - корректно\n4. ⚠ Отсутствует LIMIT - может вернуть много строк"}
    ) > data\logic_dataset.jsonl
    
    echo %SUCCESS% Примеры датасетов созданы
)

REM =============================================================================
REM DoRA Fine-tuning
REM =============================================================================

if "%SKIP_DORA%"=="false" (
    echo %STEP% Запуск DoRA fine-tuning...
    echo %INFO% Эпохи: %DORA_EPOCHS%
    echo %INFO% Это займет несколько часов...
    echo.
    
    python training\dora_finetuning.py --creator_model "%CREATOR_DIR%" --logic_model "%LOGIC_DIR%" --creator_dataset "data\creator_dataset.jsonl" --logic_dataset "data\logic_dataset.jsonl" --output_dir "%CHECKPOINTS_DIR%" --epochs %DORA_EPOCHS% --batch_size 4 --learning_rate 2e-4 > "%LOGS_DIR%\dora_training.log" 2>&1
    
    if errorlevel 1 (
        echo %ERROR% Ошибка DoRA fine-tuning
        echo %WARNING% Продолжаю с базовыми моделями...
    ) else (
        echo %SUCCESS% DoRA fine-tuning завершен
        
        REM Обновление путей на fine-tuned модели
        set "CREATOR_DIR=%CHECKPOINTS_DIR%\creator"
        set "LOGIC_DIR=%CHECKPOINTS_DIR%\logic"
        
        echo %SUCCESS% Используются fine-tuned модели
    )
    echo.
) else (
    echo %INFO% DoRA fine-tuning пропущен ^(SKIP_DORA=true^)
    echo.
)

REM =============================================================================
REM Запуск Qdrant
REM =============================================================================

echo %STEP% Проверка Qdrant...

curl -s http://localhost:6333/health >nul 2>&1
if errorlevel 1 (
    echo %WARNING% Qdrant не запущен. Попытка запуска через Docker...
    
    docker --version >nul 2>&1
    if errorlevel 1 (
        echo %ERROR% Docker не найден. Установи Qdrant вручную: https://qdrant.tech/documentation/quick-start/
        exit /b 1
    )
    
    docker run -d --name qdrant -p 6333:6333 -p 6334:6334 -v "%cd%\qdrant_storage:/qdrant/storage" qdrant/qdrant:latest
    
    echo %INFO% Ожидание запуска Qdrant...
    timeout /t 10 /nobreak >nul
    
    curl -s http://localhost:6333/health >nul 2>&1
    if errorlevel 1 (
        echo %ERROR% Не удалось запустить Qdrant
        exit /b 1
    )
    echo %SUCCESS% Qdrant запущен
) else (
    echo %SUCCESS% Qdrant уже запущен
)
echo.

REM =============================================================================
REM Создание скрипта запуска
REM =============================================================================

echo %STEP% Создание скрипта запуска...

(
echo import asyncio
echo import sys
echo from dual_qwen_brain import DualQwenAgent
echo.
echo async def main^(^):
echo     print^("🧠 Инициализация Dual Qwen Brain..."^)
echo.    
echo     agent = DualQwenAgent^(config_path="config/config.yaml"^)
echo.    
echo     try:
echo         await agent.initialize^(^)
echo         print^("✅ Система инициализирована"^)
echo.        
echo         # Тестовая задача
echo         print^("\n🚀 Запуск тестовой задачи..."^)
echo         result = await agent.process^(
echo             "Создай REST API для управления задачами с использованием FastAPI. "
echo             "Включи CRUD операции, валидацию данных и документацию."
echo         ^)
echo.        
echo         print^("\n" + "="*80^)
echo         print^("📊 РЕЗУЛЬТАТ:"^)
echo         print^("="*80^)
echo         print^(result^)
echo         print^("="*80^)
echo.        
echo         # Запуск автономного режима ^(если включен^)
echo         config = agent.config
echo         if config.get^('AUTONOMY_ENABLED', False^):
echo             print^("\n🌙 Запуск автономного режима..."^)
echo             await agent.start_autonomy^(^)
echo             print^("✅ Автономный режим активен"^)
echo             print^("💡 Система будет мониторить GitHub, Arxiv и tech новости"^)
echo.            
echo             # Держим систему запущенной
echo             print^("\n⌨️  Нажми Ctrl+C для остановки..."^)
echo             try:
echo                 while True:
echo                     await asyncio.sleep^(1^)
echo             except KeyboardInterrupt:
echo                 print^("\n🛑 Остановка системы..."^)
echo                 agent.stop_autonomy^(^)
echo.        
echo     except Exception as e:
echo         print^(f"❌ Ошибка: {e}", file=sys.stderr^)
echo         import traceback
echo         traceback.print_exc^(^)
echo         return 1
echo     finally:
echo         await agent.shutdown^(^)
echo         print^("👋 Система остановлена"^)
echo.    
echo     return 0
echo.
echo if __name__ == "__main__":
echo     sys.exit^(asyncio.run^(main^(^)^)^)
) > run_agent.py

echo %SUCCESS% Скрипт запуска создан
echo.

REM =============================================================================
REM Запуск системы
REM =============================================================================

if "%RUN_SYSTEM%"=="true" (
    echo %STEP% Запуск Dual Qwen Brain системы...
    echo.
    
    python run_agent.py 2>&1 | tee "%LOGS_DIR%\agent_run.log"
) else (
    echo %INFO% Автоматический запуск системы пропущен ^(RUN_SYSTEM=false^)
    echo %INFO% Для запуска вручную: python dual_qwen_brain.py
)

REM =============================================================================
REM Завершение
REM =============================================================================

echo.
echo ========================================================================
echo   🎉 Установка завершена!
echo ========================================================================
echo.
echo 📁 Структура:
echo    Модели:      %MODELS_DIR%\
echo    Чекпоинты:   %CHECKPOINTS_DIR%\
echo    Логи:        %LOGS_DIR%\
echo    Конфиг:      config\config.yaml
echo.
echo 🚀 Для запуска системы:
echo    python dual_qwen_brain.py
echo.
echo 📚 Документация:
echo    README.md           - Общая информация
echo    DEPLOYMENT.md       - Руководство по деплою
echo    API_KEYS_GUIDE.md   - Настройка API ключей
echo    QUICKSTART.md       - Быстрый старт
echo.
echo 💡 Полезные команды:
echo    REM Пропустить DoRA и сразу запустить
echo    set SKIP_DORA=true ^&^& setup_and_run.bat
echo.
echo    REM Включить автономный режим
echo    set AUTONOMY_ENABLED=true ^&^& setup_and_run.bat
echo.
echo    REM Только загрузить модели
echo    set SKIP_DORA=true ^&^& set RUN_SYSTEM=false ^&^& setup_and_run.bat
echo.

pause
