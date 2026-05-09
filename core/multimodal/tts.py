"""
TTS Module - интеграция с GPT-SoVITS для клонирования голоса
Агент может озвучивать свои выводы голосом Хозяина
"""
import asyncio
import os
from typing import Optional, Literal
from pathlib import Path
from loguru import logger
import requests
import json


class GPTSoVITSTTS:
    """
    Интеграция с GPT-SoVITS для генерации речи
    Поддерживает клонирование голоса из короткого образца
    """
    
    def __init__(
        self,
        api_url: str = "http://localhost:9880",
        reference_audio: Optional[str] = None,
        reference_text: Optional[str] = None,
        language: Literal["ru", "en", "zh", "ja"] = "ru"
    ):
        """
        Args:
            api_url: URL API GPT-SoVITS сервера
            reference_audio: Путь к референсному аудио (для клонирования)
            reference_text: Текст референсного аудио
            language: Язык генерации
        """
        self.api_url = api_url.rstrip('/')
        self.reference_audio = reference_audio
        self.reference_text = reference_text
        self.language = language
        
        # Проверяем доступность сервера
        self._check_server()
        
        logger.info(f"GPTSoVITSTTS инициализирован (API: {self.api_url})")
    
    def _check_server(self):
        """Проверка доступности GPT-SoVITS сервера"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("GPT-SoVITS сервер доступен")
            else:
                logger.warning(f"GPT-SoVITS сервер вернул статус {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"GPT-SoVITS сервер недоступен: {e}")
            logger.info("Запустите сервер командой: python GPT_SoVITS/api.py")
    
    async def synthesize(
        self,
        text: str,
        output_path: str,
        reference_audio: Optional[str] = None,
        reference_text: Optional[str] = None,
        speed: float = 1.0,
        temperature: float = 0.6
    ) -> str:
        """
        Синтез речи из текста
        
        Args:
            text: Текст для озвучки
            output_path: Путь для сохранения аудио
            reference_audio: Референсное аудио (если не задано при инициализации)
            reference_text: Текст референса
            speed: Скорость речи (0.5-2.0)
            temperature: Температура генерации (креативность)
        
        Returns:
            Путь к созданному аудио файлу
        """
        # Используем переданные или дефолтные референсы
        ref_audio = reference_audio or self.reference_audio
        ref_text = reference_text or self.reference_text
        
        if not ref_audio or not ref_text:
            raise ValueError("Необходимо указать reference_audio и reference_text")
        
        logger.info(f"Синтез речи: {text[:50]}...")
        
        # Подготовка данных для API
        payload = {
            "text": text,
            "text_language": self.language,
            "ref_audio_path": ref_audio,
            "prompt_text": ref_text,
            "prompt_language": self.language,
            "speed": speed,
            "temperature": temperature
        }
        
        try:
            # Отправляем запрос к API
            response = await asyncio.to_thread(
                requests.post,
                f"{self.api_url}/tts",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                # Сохраняем аудио
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Аудио сохранено: {output_path}")
                return str(output_path)
            else:
                error_msg = f"Ошибка TTS API: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к TTS API: {e}")
            raise
    
    async def synthesize_batch(
        self,
        texts: list[str],
        output_dir: str,
        prefix: str = "speech"
    ) -> list[str]:
        """
        Пакетный синтез нескольких текстов
        
        Args:
            texts: Список текстов
            output_dir: Директория для сохранения
            prefix: Префикс имен файлов
        
        Returns:
            Список путей к созданным файлам
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        paths = []
        for i, text in enumerate(texts):
            output_path = output_dir / f"{prefix}_{i+1:03d}.wav"
            path = await self.synthesize(text, str(output_path))
            paths.append(path)
        
        logger.info(f"Создано {len(paths)} аудио файлов")
        return paths
    
    def set_reference(self, audio_path: str, text: str):
        """
        Установка нового референсного аудио
        
        Args:
            audio_path: Путь к аудио файлу
            text: Текст, произнесенный в аудио
        """
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Аудио файл не найден: {audio_path}")
        
        self.reference_audio = audio_path
        self.reference_text = text
        
        logger.info(f"Установлен новый референс: {audio_path}")
    
    async def clone_voice(
        self,
        sample_audio: str,
        sample_text: str,
        test_text: str = "Привет, Хозяин! Это твоя Аля.",
        output_path: str = "outputs/voice_test.wav"
    ) -> str:
        """
        Клонирование голоса из образца
        
        Args:
            sample_audio: Путь к образцу голоса (1+ минута)
            sample_text: Текст образца
            test_text: Тестовый текст для проверки
            output_path: Путь для сохранения теста
        
        Returns:
            Путь к тестовому аудио
        """
        logger.info("Клонирование голоса из образца...")
        
        # Устанавливаем референс
        self.set_reference(sample_audio, sample_text)
        
        # Генерируем тестовое аудио
        result = await self.synthesize(test_text, output_path)
        
        logger.info(f"Голос клонирован! Тестовое аудио: {result}")
        return result


class TTSManager:
    """
    Менеджер TTS для интеграции в агента
    Управляет озвучкой ключевых выводов
    """
    
    def __init__(
        self,
        tts_engine: GPTSoVITSTTS,
        output_dir: str = "outputs/speech",
        auto_speak: bool = False
    ):
        """
        Args:
            tts_engine: Экземпляр TTS движка
            output_dir: Директория для аудио файлов
            auto_speak: Автоматически озвучивать результаты
        """
        self.tts = tts_engine
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.auto_speak = auto_speak
        
        self.speech_counter = 0
        
        logger.info("TTSManager инициализирован")
    
    async def speak_result(
        self,
        text: str,
        importance: Literal["low", "medium", "high"] = "medium"
    ) -> Optional[str]:
        """
        Озвучка результата
        
        Args:
            text: Текст для озвучки
            importance: Важность (влияет на то, озвучивать ли)
        
        Returns:
            Путь к аудио файлу или None
        """
        # Проверяем, нужно ли озвучивать
        if not self.auto_speak and importance != "high":
            return None
        
        # Ограничиваем длину текста
        max_length = 500
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        # Генерируем имя файла
        self.speech_counter += 1
        output_path = self.output_dir / f"result_{self.speech_counter:04d}.wav"
        
        try:
            path = await self.tts.synthesize(text, str(output_path))
            logger.info(f"Результат озвучен: {path}")
            return path
        except Exception as e:
            logger.error(f"Ошибка озвучки: {e}")
            return None
    
    async def speak_summary(
        self,
        task: str,
        result: str,
        execution_time: Optional[float] = None
    ) -> Optional[str]:
        """
        Озвучка краткого резюме выполнения задачи
        
        Args:
            task: Исходная задача
            result: Результат
            execution_time: Время выполнения в секундах
        
        Returns:
            Путь к аудио
        """
        # Формируем краткое резюме
        summary = f"Задача выполнена. {result[:200]}"
        
        if execution_time:
            summary += f" Время выполнения: {execution_time:.1f} секунд."
        
        return await self.speak_result(summary, importance="high")
    
    def enable_auto_speak(self):
        """Включить автоматическую озвучку"""
        self.auto_speak = True
        logger.info("Автоматическая озвучка включена")
    
    def disable_auto_speak(self):
        """Выключить автоматическую озвучку"""
        self.auto_speak = False
        logger.info("Автоматическая озвучка выключена")
