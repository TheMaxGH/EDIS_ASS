# 🚀 E.D.I.S. - Гайд для чайников

Полное руководство по развертыванию системы E.D.I.S. на сервере с 8xH200.

---

## 📋 Что вам понадобится

1. **Сервер с 8xH200** (арендованный у Саши)
2. **SSH-доступ** к серверу (IP, порт, пароль/ключ)
3. **Git** (уже должен быть на сервере)
4. **Ваш компьютер** с SSH-клиентом

---

## 🔐 Шаг 1: Подключение к серверу через SSH

### Windows (PowerShell или CMD)

```powershell
# Подключение к серверу
ssh username@your-server-ip

# Если используется нестандартный порт (например, 2222)
ssh -p 2222 username@your-server-ip

# Если используется SSH-ключ
ssh -i C:\path\to\your\private_key.pem username@your-server-ip
```

### Linux / macOS

```bash
# Подключение к серверу
ssh username@your-server-ip

# С нестандартным портом
ssh -p 2222 username@your-server-ip

# С SSH-ключом
ssh -i ~/.ssh/your_private_key username@your-server-ip
```

**Пример:**
```bash
ssh fred@192.168.1.100
# Введите пароль когда попросит
```

---

## 📥 Шаг 2: Клонирование репозитория

После успешного подключения к серверу выполните:

```bash
# Переход в домашнюю директорию
cd ~

# Клонирование репозитория E.D.I.S.
git clone https://github.com/TheMaxGH/EDIS_ASS.git

# Переход в папку проекта
cd EDIS_ASS

# Проверка содержимого
ls -la
```

**Ожидаемый результат:**
```
agents/
autonomy/
config/
core/
data/
examples/
plans/
training/
dual_qwen_brain.py
requirements.txt
setup_and_run.sh
...
```

---

## 📤 Шаг 3: Загрузка датасетов на сервер

### Вариант A: Через SCP (с вашего компьютера)

**Windows (PowerShell):**
```powershell
# Загрузка одного файла
scp C:\path\to\left_creator_dataset.jsonl username@server-ip:~/EDIS_ASS/data/

# Загрузка всей папки data
scp -r C:\path\to\data\* username@server-ip:~/EDIS_ASS/data/
```

**Linux / macOS:**
```bash
# Загрузка одного файла
scp /path/to/left_creator_dataset.jsonl username@server-ip:~/EDIS_ASS/data/

# Загрузка всей папки
scp -r /path/to/data/* username@server-ip:~/EDIS_ASS/data/
```

**Пример:**
```bash
scp ~/Downloads/left_creator_dataset.jsonl fred@192.168.1.100:~/EDIS_ASS/data/
scp ~/Downloads/right_logic_dataset.jsonl fred@192.168.1.100:~/EDIS_ASS/data/
```

### Вариант B: Через SFTP (интерактивный режим)

```bash
# Подключение через SFTP
sftp username@server-ip

# Внутри SFTP-сессии:
cd EDIS_ASS/data
put /local/path/to/left_creator_dataset.jsonl
put /local/path/to/right_logic_dataset.jsonl
bye
```

### Вариант C: Создание файлов напрямую на сервере

```bash
# На сервере
cd ~/EDIS_ASS/data

# Создание файла через nano
nano left_creator_dataset.jsonl
# Вставьте содержимое, нажмите Ctrl+X, затем Y, затем Enter

# Или через vim
vim right_logic_dataset.jsonl
# Нажмите i, вставьте содержимое, нажмите Esc, затем :wq
```

---

## 🔧 Шаг 4: Установка зависимостей

```bash
# Убедитесь, что вы в папке проекта
cd ~/EDIS_ASS

# Создание виртуального окружения Python (рекомендуется)
python3 -m venv venv

# Активация виртуального окружения
source venv/bin/activate

# Установка всех зависимостей
pip install -r requirements.txt

# Это займет 10-20 минут, так как устанавливаются torch, transformers, vllm и т.д.
```

**Если возникает ошибка с pip:**
```bash
# Обновление pip
pip install --upgrade pip

# Повторная попытка
pip install -r requirements.txt
```

---

## ⚙️ Шаг 5: Настройка конфигурации

```bash
# Копирование примера .env
cp .env.example .env

# Редактирование конфигурации
nano .env

# Укажите пути к моделям и другие параметры
# Сохраните: Ctrl+X, затем Y, затем Enter
```

**Минимальная конфигурация `.env`:**
```bash
# Модели (будут скачаны автоматически)
CREATOR_MODEL=huihui-ai/Qwen2.5-72B-Instruct-abliterated
LOGIC_MODEL=Qwen/Qwen3.5-397B-A17B-FP8

# GPU настройки
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
VLLM_TENSOR_PARALLEL_SIZE=8

# API ключи (опционально, только для автономного режима)
# TAVILY_API_KEY=your_key_here
# SERPER_API_KEY=your_key_here
```

---

## 🚀 Шаг 6: Запуск системы

### Автоматический запуск (рекомендуется)

```bash
# Делаем скрипт исполняемым
chmod +x setup_and_run.sh

# Запуск всей системы (скачивание моделей + обучение + запуск)
./setup_and_run.sh
```

**Что происходит:**
1. Скачиваются модели Qwen-72B и Qwen-397B (~200GB)
2. Запускается DoRA fine-tuning на ваших датасетах из `data/`
3. Запускаются обе модели через vLLM
4. Инициализируется система E.D.I.S.

**Время выполнения:**
- Скачивание моделей: 30-60 минут (зависит от интернета)
- DoRA fine-tuning: 2-6 часов (зависит от размера датасетов)
- Запуск системы: 5-10 минут

### Ручной запуск (пошагово)

```bash
# 1. Скачивание моделей
python -c "from huggingface_hub import snapshot_download; snapshot_download('huihui-ai/Qwen2.5-72B-Instruct-abliterated', local_dir='./models/creator')"
python -c "from huggingface_hub import snapshot_download; snapshot_download('Qwen/Qwen3.5-397B-A17B-FP8', local_dir='./models/logic')"

# 2. DoRA fine-tuning
python training/dora_finetuning.py

# 3. Запуск системы
python dual_qwen_brain.py
```

---

## 📊 Шаг 7: Проверка работы

### Проверка GPU

```bash
# Проверка доступности GPU
nvidia-smi

# Должны увидеть 8xH200 с загрузкой памяти
```

### Проверка логов

```bash
# Просмотр логов в реальном времени
tail -f logs/edis.log

# Или если логи выводятся в консоль
# Просто смотрите на вывод после запуска
```

### Тестовый запрос

```bash
# В новом терминале (новое SSH-подключение)
cd ~/EDIS_ASS
source venv/bin/activate

# Запуск примера
python examples/usage_examples.py
```

---

## 🔄 Шаг 8: Обновление кода

```bash
# Переход в папку проекта
cd ~/EDIS_ASS

# Получение последних изменений
git pull origin main

# Переустановка зависимостей (если обновились)
pip install -r requirements.txt --upgrade

# Перезапуск системы
./setup_and_run.sh
```

---

## 🛑 Остановка системы

```bash
# Найти процесс Python
ps aux | grep python

# Остановить по PID
kill -9 <PID>

# Или если запущено в screen/tmux
screen -r edis
# Нажмите Ctrl+C для остановки
```

---

## 📁 Структура датасетов

Ваши датасеты должны быть в формате JSONL в папке `data/`:

**Для Творца (левое полушарие):**
- `data/left_creator_dataset.jsonl`
- `data/left_singularity.jsonl`
- `data/creator_*.jsonl` (любые файлы с префиксом creator_)

**Для Логика (правое полушарие):**
- `data/right_logic_dataset.jsonl`
- `data/right_tactical.jsonl`
- `data/logic_*.jsonl` (любые файлы с префиксом logic_)

**Формат JSONL (каждая строка - отдельный JSON):**
```json
{"messages": [{"role": "system", "content": "Системный промпт E.D.I.S."}, {"role": "user", "content": "Вопрос Капитана"}, {"role": "assistant", "content": "Ответ E.D.I.S."}]}
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

---

## 🐛 Решение проблем

### Проблема: "Permission denied" при запуске скрипта

```bash
chmod +x setup_and_run.sh
```

### Проблема: "CUDA out of memory"

```bash
# Уменьшите batch size в config/training_config.yaml
nano config/training_config.yaml
# Измените per_device_train_batch_size с 4 на 2
```

### Проблема: "ModuleNotFoundError"

```bash
# Переустановите зависимости
pip install -r requirements.txt --force-reinstall
```

### Проблема: Модели не скачиваются

```bash
# Проверьте интернет-соединение
ping huggingface.co

# Установите git-lfs (если не установлен)
sudo apt-get install git-lfs
git lfs install
```

### Проблема: SSH-соединение обрывается

```bash
# Используйте screen или tmux для долгих процессов
screen -S edis
./setup_and_run.sh
# Нажмите Ctrl+A, затем D для отсоединения

# Для возврата к сессии
screen -r edis
```

---

## 📞 Поддержка

Если что-то не работает:

1. Проверьте логи: `tail -f logs/edis.log`
2. Проверьте GPU: `nvidia-smi`
3. Проверьте датасеты: `ls -la data/`
4. Проверьте конфигурацию: `cat .env`

---

## 🎯 Быстрый старт (все команды подряд)

```bash
# 1. Подключение к серверу
ssh username@server-ip

# 2. Клонирование репозитория
cd ~
git clone https://github.com/TheMaxGH/EDIS_ASS.git
cd EDIS_ASS

# 3. Загрузка датасетов (с вашего компьютера в новом терминале)
scp /path/to/left_*.jsonl username@server-ip:~/EDIS_ASS/data/
scp /path/to/right_*.jsonl username@server-ip:~/EDIS_ASS/data/

# 4. Установка зависимостей (обратно на сервере)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Настройка
cp .env.example .env
nano .env  # Настройте при необходимости

# 6. Запуск
chmod +x setup_and_run.sh
screen -S edis
./setup_and_run.sh

# 7. Отсоединение от screen (система продолжит работать)
# Нажмите Ctrl+A, затем D

# 8. Выход из SSH (система продолжит работать)
exit
```

---

**Готово!** Система E.D.I.S. запущена и работает на вашем сервере с 8xH200. 🚀
