"""
Примеры использования TTS API

Этот файл содержит практические примеры работы с Voice API EDIS.
"""
import asyncio
import httpx
from pathlib import Path


# Конфигурация
API_URL = "http://localhost:8000"
API_KEY = "your-secret-key-here"


async def example_1_simple_tts():
    """
    Пример 1: Простой синтез речи
    
    Самый базовый пример - преобразование текста в речь.
    """
    print("=== Пример 1: Простой TTS ===\n")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/api/v1/voice/tts",
            json={
                "text": "Привет! Это пример синтеза речи.",
                "language": "ru",
                "speed": 1.0
            },
            headers={"X-API-Key": API_KEY}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Аудио создано: {data['audio_url']}")
            print(f"   Длительность: {data['duration']:.2f} сек")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"   {response.text}")


async def example_2_create_voice():
    """
    Пример 2: Создание нового голоса
    
    Создание голоса из референсного аудио файла.
    """
    print("\n=== Пример 2: Создание голоса ===\n")
    
    # Путь к вашему аудио файлу
    audio_path = Path("path/to/your/voice_sample.wav")
    
    if not audio_path.exists():
        print("⚠️  Создайте аудио файл для примера")
        return
    
    async with httpx.AsyncClient() as client:
        with open(audio_path, "rb") as audio_file:
            response = await client.post(
                f"{API_URL}/api/v1/voice/voices",
                files={"audio": audio_file},
                data={
                    "name": "Мой голос",
                    "reference_text": "Это референсный текст для моего голоса",
                    "description": "Голос созданный из примера",
                    "language": "ru"
                },
                headers={"X-API-Key": API_KEY}
            )
        
        if response.status_code == 200:
            voice = response.json()
            print(f"✅ Голос создан!")
            print(f"   ID: {voice['id']}")
            print(f"   Название: {voice['name']}")
            print(f"   Язык: {voice['language']}")
            return voice['id']
        else:
            print(f"❌ Ошибка: {response.status_code}")


async def example_3_list_voices():
    """
    Пример 3: Получение списка голосов
    
    Просмотр всех доступных голосов в библиотеке.
    """
    print("\n=== Пример 3: Список голосов ===\n")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_URL}/api/v1/voice/voices",
            headers={"X-API-Key": API_KEY}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"📚 Всего голосов: {data['total']}\n")
            
            for voice in data['voices']:
                status = "✅ Обучен" if voice['is_trained'] else "⏳ Не обучен"
                print(f"🎤 {voice['name']}")
                print(f"   ID: {voice['id']}")
                print(f"   Язык: {voice['language']}")
                print(f"   Статус: {status}")
                print(f"   Сэмплов: {voice['sample_count']}")
                print()
        else:
            print(f"❌ Ошибка: {response.status_code}")


async def example_4_add_training_samples():
    """
    Пример 4: Добавление обучающих сэмплов
    
    Добавление нескольких аудио сэмплов для обучения голоса.
    """
    print("\n=== Пример 4: Добавление сэмплов ===\n")
    
    voice_id = "your-voice-id-here"  # Замените на реальный ID
    
    # Список сэмплов для добавления
    samples = [
        ("sample1.wav", "Первый обучающий сэмпл"),
        ("sample2.wav", "Второй обучающий сэмпл"),
        ("sample3.wav", "Третий обучающий сэмпл"),
    ]
    
    async with httpx.AsyncClient() as client:
        for audio_file, text in samples:
            audio_path = Path(f"samples/{audio_file}")
            
            if not audio_path.exists():
                print(f"⚠️  Файл {audio_file} не найден, пропускаем")
                continue
            
            with open(audio_path, "rb") as f:
                response = await client.post(
                    f"{API_URL}/api/v1/voice/voices/{voice_id}/samples",
                    files={"audio": f},
                    data={"text": text},
                    headers={"X-API-Key": API_KEY}
                )
            
            if response.status_code == 200:
                sample = response.json()
                print(f"✅ Сэмпл добавлен: {sample['id']}")
                print(f"   Текст: {text}")
                print(f"   Длительность: {sample['duration']:.2f} сек\n")
            else:
                print(f"❌ Ошибка добавления {audio_file}: {response.status_code}\n")


async def example_5_train_voice():
    """
    Пример 5: Обучение голоса
    
    Запуск обучения голоса с настройкой параметров.
    """
    print("\n=== Пример 5: Обучение голоса ===\n")
    
    voice_id = "your-voice-id-here"  # Замените на реальный ID
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Запуск обучения
        response = await client.post(
            f"{API_URL}/api/v1/voice/voices/{voice_id}/train",
            json={
                "voice_id": voice_id,
                "epochs": 100,
                "batch_size": 4,
                "learning_rate": 0.0001,
                "save_interval": 10
            },
            headers={"X-API-Key": API_KEY}
        )
        
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Обучение запущено!")
            print(f"   Статус: {status['status']}")
            print(f"   Эпох: {status['total_epochs']}")
            print()
            
            # Мониторинг прогресса
            print("📊 Мониторинг прогресса...\n")
            while True:
                await asyncio.sleep(5)  # Проверяем каждые 5 секунд
                
                status_response = await client.get(
                    f"{API_URL}/api/v1/voice/voices/{voice_id}/training-status",
                    headers={"X-API-Key": API_KEY}
                )
                
                if status_response.status_code == 200:
                    status = status_response.json()
                    
                    if status['status'] == 'completed':
                        print(f"✅ Обучение завершено!")
                        break
                    elif status['status'] == 'failed':
                        print(f"❌ Обучение провалилось: {status.get('error')}")
                        break
                    else:
                        progress = status['progress']
                        epoch = status['current_epoch']
                        total = status['total_epochs']
                        eta = status.get('eta_seconds', 0)
                        
                        print(f"⏳ Прогресс: {progress:.1f}% | Эпоха: {epoch}/{total} | ETA: {eta//60} мин")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"   {response.text}")


async def example_6_test_voice():
    """
    Пример 6: Тестирование голоса
    
    Генерация тестового аудио с обученным голосом.
    """
    print("\n=== Пример 6: Тестирование голоса ===\n")
    
    voice_id = "your-voice-id-here"  # Замените на реальный ID
    
    test_texts = [
        "Привет! Это тестовое сообщение.",
        "Как дела? Надеюсь, всё хорошо!",
        "Это пример синтеза речи с обученным голосом."
    ]
    
    async with httpx.AsyncClient() as client:
        for i, text in enumerate(test_texts, 1):
            response = await client.post(
                f"{API_URL}/api/v1/voice/voices/{voice_id}/test",
                json={
                    "voice_id": voice_id,
                    "test_text": text,
                    "language": "ru"
                },
                headers={"X-API-Key": API_KEY}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Тест {i}: {data['audio_url']}")
                print(f"   Текст: {text}")
                print(f"   Длительность: {data['duration']:.2f} сек\n")
            else:
                print(f"❌ Ошибка теста {i}: {response.status_code}\n")


async def example_7_speech_to_text():
    """
    Пример 7: Распознавание речи (STT)
    
    Преобразование аудио в текст.
    """
    print("\n=== Пример 7: Speech-to-Text ===\n")
    
    audio_path = Path("path/to/audio_to_recognize.wav")
    
    if not audio_path.exists():
        print("⚠️  Создайте аудио файл для распознавания")
        return
    
    async with httpx.AsyncClient() as client:
        with open(audio_path, "rb") as audio_file:
            response = await client.post(
                f"{API_URL}/api/v1/voice/stt",
                files={"audio": audio_file},
                data={"language": "ru"},
                headers={"X-API-Key": API_KEY}
            )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Распознано:")
            print(f"   Текст: {data['text']}")
            print(f"   Уверенность: {data['confidence']:.2%}")
            print(f"   Язык: {data['language']}")
        else:
            print(f"❌ Ошибка: {response.status_code}")


async def example_8_batch_synthesis():
    """
    Пример 8: Пакетный синтез речи
    
    Генерация нескольких аудио файлов одновременно.
    """
    print("\n=== Пример 8: Пакетный синтез ===\n")
    
    texts = [
        "Первое сообщение для синтеза.",
        "Второе сообщение для синтеза.",
        "Третье сообщение для синтеза.",
        "Четвертое сообщение для синтеза.",
        "Пятое сообщение для синтеза."
    ]
    
    async with httpx.AsyncClient() as client:
        tasks = []
        for text in texts:
            task = client.post(
                f"{API_URL}/api/v1/voice/tts",
                json={"text": text, "language": "ru", "speed": 1.0},
                headers={"X-API-Key": API_KEY}
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = 0
        for i, response in enumerate(responses, 1):
            if isinstance(response, Exception):
                print(f"❌ Ошибка {i}: {response}")
            elif response.status_code == 200:
                data = response.json()
                print(f"✅ Аудио {i}: {data['audio_url']}")
                success_count += 1
            else:
                print(f"❌ Ошибка {i}: {response.status_code}")
        
        print(f"\n📊 Успешно: {success_count}/{len(texts)}")


async def main():
    """Запуск всех примеров"""
    print("🎤 Примеры использования Voice API EDIS\n")
    print("=" * 50)
    
    try:
        # Запускаем примеры по очереди
        await example_1_simple_tts()
        await example_3_list_voices()
        
        # Раскомментируйте нужные примеры:
        # await example_2_create_voice()
        # await example_4_add_training_samples()
        # await example_5_train_voice()
        # await example_6_test_voice()
        # await example_7_speech_to_text()
        # await example_8_batch_synthesis()
        
        print("\n" + "=" * 50)
        print("✅ Примеры завершены!")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())
