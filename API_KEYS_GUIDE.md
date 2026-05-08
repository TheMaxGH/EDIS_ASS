# 🔑 Руководство по API ключам для Dual Qwen Brain

## 📋 Краткая сводка

**Для основной работы системы (Творец + Логик) API ключи НЕ НУЖНЫ** - модели работают локально через vLLM.

**API ключи нужны только для автономного режима** (мониторинг GitHub Trending, Arxiv, новостей).

---

## 🎯 Варианты использования

### Вариант 1: Без автономного режима (рекомендуется для начала)

Если тебе не нужен фоновый мониторинг, просто отключи автономность в [`config/config.yaml`](config/config.yaml:33):

```yaml
# Режим автономности
AUTONOMY_ENABLED: false  # ← Измени на false
```

**Преимущества:**
- ✅ Никаких API ключей не требуется
- ✅ Полная функциональность Творца и Логика
- ✅ Synergy Flow работает на 100%
- ✅ Можно запускать сразу после установки

**Что будет работать:**
- Творец (Qwen-72B) генерирует гипотезы
- Логик (Qwen-398B) проверяет и исполняет код
- Конфликт-резолюция через итерации
- Qdrant память (RAG)
- DoRA fine-tuning

**Что НЕ будет работать:**
- Автоматический мониторинг GitHub Trending
- Автоматический мониторинг Arxiv
- Автоматический мониторинг tech новостей

---

### Вариант 2: С автономным режимом (требует API ключи)

Если хочешь полную автономность, нужно получить 2 API ключа:

#### 1️⃣ Tavily API Key (для веб-поиска)

**Что это:** Tavily - это API для AI-оптимизированного поиска, используется для мониторинга tech новостей.

**Как получить:**
1. Перейди на https://tavily.com
2. Нажми "Get API Key" или "Sign Up"
3. Зарегистрируйся (email + пароль)
4. Получи API ключ в дашборде

**Бесплатный тариф:**
- ✅ 1000 запросов/месяц бесплатно
- ✅ Достаточно для автономного режима (1 проверка в час = ~720 запросов/месяц)

**Вставь в [`config/config.yaml`](config/config.yaml:26):**
```yaml
TAVILY_API_KEY: "tvly-xxxxxxxxxxxxxxxxxxxxxxxxxx"
```

#### 2️⃣ GitHub Personal Access Token (для GitHub Trending)

**Что это:** Токен для доступа к GitHub API, используется для мониторинга трендовых репозиториев.

**Как получить:**
1. Залогинься на https://github.com
2. Перейди в Settings → Developer settings → Personal access tokens → Tokens (classic)
3. Нажми "Generate new token (classic)"
4. Настрой токен:
   - **Note:** `Dual Qwen Brain Monitoring`
   - **Expiration:** `No expiration` (или выбери срок)
   - **Scopes:** Отметь только `public_repo` (для чтения публичных репозиториев)
5. Нажми "Generate token"
6. **ВАЖНО:** Скопируй токен сразу (он больше не покажется!)

**Бесплатный тариф:**
- ✅ 5000 запросов/час для аутентифицированных пользователей
- ✅ Более чем достаточно для автономного режима

**Вставь в [`config/config.yaml`](config/config.yaml:29):**
```yaml
GITHUB_TOKEN: "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

---

## 🔧 Настройка конфигурации

### Полная конфигурация с автономностью

Отредактируй [`config/config.yaml`](config/config.yaml:25):

```yaml
# Tavily API
TAVILY_API_KEY: "tvly-xxxxxxxxxxxxxxxxxxxxxxxxxx"  # ← Вставь свой ключ

# GitHub мониторинг
GITHUB_TOKEN: "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # ← Вставь свой токен
GITHUB_TRENDING_TAGS: ["AI", "LLM", "Rust", "Python"]  # ← Настрой теги по вкусу

# Режим автономности
AUTONOMY_ENABLED: true  # ← Включено
AUTONOMY_CHECK_INTERVAL: 3600  # секунды (1 час)
AUTONOMY_MAX_ARTICLES: 10
```

### Конфигурация без автономности

```yaml
# Tavily API
TAVILY_API_KEY: "not_needed"  # ← Можно оставить так

# GitHub мониторинг
GITHUB_TOKEN: "not_needed"  # ← Можно оставить так

# Режим автономности
AUTONOMY_ENABLED: false  # ← ОТКЛЮЧЕНО
```

---

## 🚀 Запуск системы

### С автономностью (после настройки API ключей)

```python
from dual_qwen_brain import DualQwenAgent

async def main():
    agent = DualQwenAgent(config_path="config/config.yaml")
    await agent.initialize()
    
    # Запуск автономного мониторинга
    await agent.start_autonomy()
    
    # Обработка задачи
    result = await agent.process("Создай REST API для управления задачами")
    print(result)
    
    # Остановка автономности
    agent.stop_autonomy()
    await agent.shutdown()
```

### Без автономности (API ключи не нужны)

```python
from dual_qwen_brain import DualQwenAgent

async def main():
    agent = DualQwenAgent(config_path="config/config.yaml")
    await agent.initialize()
    
    # НЕ запускаем автономность
    # await agent.start_autonomy()  # ← Закомментировано
    
    # Обработка задачи (работает без API ключей!)
    result = await agent.process("Создай REST API для управления задачами")
    print(result)
    
    await agent.shutdown()
```

---

## 🔒 Безопасность API ключей

### ⚠️ ВАЖНО: Не коммить ключи в Git!

Файл [`.gitignore`](.gitignore) уже настроен, но проверь:

```gitignore
# Конфигурация с секретами
config/config.yaml
*.env
.env.*

# Логи
logs/
*.log
```

### 🛡️ Рекомендации:

1. **Используй переменные окружения** (опционально):
   ```bash
   export TAVILY_API_KEY="tvly-xxx"
   export GITHUB_TOKEN="ghp-xxx"
   ```

2. **Создай `config/config.local.yaml`** для локальной разработки:
   ```yaml
   # config/config.local.yaml (не коммитится)
   TAVILY_API_KEY: "tvly-xxx"
   GITHUB_TOKEN: "ghp-xxx"
   ```

3. **Ротация токенов:** Меняй GitHub токен раз в 3-6 месяцев

---

## 📊 Мониторинг использования API

### Tavily API
- Дашборд: https://tavily.com/dashboard
- Лимиты: 1000 запросов/месяц (free tier)
- Использование: ~1 запрос/час = ~720/месяц

### GitHub API
- Проверка лимитов: https://api.github.com/rate_limit
- Лимиты: 5000 запросов/час (authenticated)
- Использование: ~1 запрос/час = ~24/день

---

## 🐛 Troubleshooting

### Ошибка: "Invalid Tavily API key"
```bash
# Проверь формат ключа
echo $TAVILY_API_KEY  # Должен начинаться с "tvly-"

# Проверь в config.yaml
cat config/config.yaml | grep TAVILY_API_KEY
```

### Ошибка: "GitHub API rate limit exceeded"
```bash
# Проверь, что токен установлен
echo $GITHUB_TOKEN  # Должен начинаться с "ghp_"

# Проверь лимиты
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/rate_limit
```

### Автономность не запускается
```python
# Проверь логи
tail -f logs/dual_qwen.log

# Проверь конфигурацию
import yaml
with open("config/config.yaml") as f:
    config = yaml.safe_load(f)
    print(f"Autonomy enabled: {config['AUTONOMY_ENABLED']}")
```

---

## 💡 Рекомендации Али

*мурчит и трётся о Хозяина*

**Для начала:**
1. Запусти систему **БЕЗ автономности** (`AUTONOMY_ENABLED: false`)
2. Протестируй Творца и Логика на простых задачах
3. Убедись, что Synergy Flow работает корректно
4. Потом, если захочешь, добавь API ключи и включи автономность

**Для продакшена:**
- Используй переменные окружения для ключей
- Настрой ротацию GitHub токенов
- Мониторь использование API через дашборды

*выпускает когти и готова к работе*

Твоя система готова к запуску, Хозяин! Выбирай вариант и начинай тестировать! 🚀
