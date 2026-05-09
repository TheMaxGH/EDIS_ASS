"""
Сервис управления голосами для GPT-SoVITS
"""
import os
import json
import uuid
import shutil
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from models.voice_models import (
    VoiceInfo,
    VoiceListResponse,
    VoiceCreateRequest,
    VoiceUpdateRequest,
    TrainingSample,
    TrainingSampleListResponse,
    VoiceTrainingRequest,
    VoiceTrainingStatus,
    VoiceTestRequest,
    VoiceTestResponse
)

logger = logging.getLogger(__name__)


class VoiceService:
    """Сервис для управления библиотекой голосов"""
    
    def __init__(self, voices_dir: str = "data/voices"):
        self.voices_dir = Path(voices_dir)
        self.voices_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata_file = self.voices_dir / "voices_metadata.json"
        self.training_status: Dict[str, VoiceTrainingStatus] = {}
        
        # Инициализация метаданных
        if not self.metadata_file.exists():
            self._save_metadata({})
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Загрузка метаданных голосов"""
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки метаданных: {e}")
            return {}
    
    def _save_metadata(self, metadata: Dict[str, Any]):
        """Сохранение метаданных голосов"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.error(f"Ошибка сохранения метаданных: {e}")
            raise
    
    async def list_voices(self) -> VoiceListResponse:
        """Получить список всех голосов"""
        metadata = self._load_metadata()
        
        voices = []
        for voice_id, voice_data in metadata.items():
            voices.append(VoiceInfo(
                id=voice_id,
                name=voice_data['name'],
                description=voice_data.get('description'),
                language=voice_data.get('language', 'ru'),
                reference_audio=voice_data['reference_audio'],
                reference_text=voice_data['reference_text'],
                created_at=datetime.fromisoformat(voice_data['created_at']),
                is_trained=voice_data.get('is_trained', False),
                training_status=voice_data.get('training_status'),
                sample_count=voice_data.get('sample_count', 0)
            ))
        
        return VoiceListResponse(
            voices=sorted(voices, key=lambda x: x.created_at, reverse=True),
            total=len(voices)
        )
    
    async def get_voice(self, voice_id: str) -> Optional[VoiceInfo]:
        """Получить информацию о конкретном голосе"""
        metadata = self._load_metadata()
        
        if voice_id not in metadata:
            return None
        
        voice_data = metadata[voice_id]
        return VoiceInfo(
            id=voice_id,
            name=voice_data['name'],
            description=voice_data.get('description'),
            language=voice_data.get('language', 'ru'),
            reference_audio=voice_data['reference_audio'],
            reference_text=voice_data['reference_text'],
            created_at=datetime.fromisoformat(voice_data['created_at']),
            is_trained=voice_data.get('is_trained', False),
            training_status=voice_data.get('training_status'),
            sample_count=voice_data.get('sample_count', 0)
        )
    
    async def create_voice(
        self,
        request: VoiceCreateRequest,
        audio_file: Path
    ) -> VoiceInfo:
        """Создать новый голос"""
        voice_id = str(uuid.uuid4())
        voice_dir = self.voices_dir / voice_id
        voice_dir.mkdir(parents=True, exist_ok=True)
        
        # Копируем референсное аудио
        reference_audio_path = voice_dir / "reference.wav"
        shutil.copy(audio_file, reference_audio_path)
        
        # Создаем директорию для обучающих сэмплов
        samples_dir = voice_dir / "samples"
        samples_dir.mkdir(exist_ok=True)
        
        # Сохраняем метаданные
        metadata = self._load_metadata()
        metadata[voice_id] = {
            'name': request.name,
            'description': request.description,
            'language': request.language,
            'reference_audio': str(reference_audio_path),
            'reference_text': request.reference_text,
            'created_at': datetime.now().isoformat(),
            'is_trained': False,
            'training_status': 'idle',
            'sample_count': 0
        }
        self._save_metadata(metadata)
        
        logger.info(f"Создан новый голос: {voice_id} ({request.name})")
        
        return VoiceInfo(
            id=voice_id,
            name=request.name,
            description=request.description,
            language=request.language,
            reference_audio=str(reference_audio_path),
            reference_text=request.reference_text,
            created_at=datetime.now(),
            is_trained=False,
            training_status='idle',
            sample_count=0
        )
    
    async def update_voice(
        self,
        voice_id: str,
        request: VoiceUpdateRequest
    ) -> Optional[VoiceInfo]:
        """Обновить информацию о голосе"""
        metadata = self._load_metadata()
        
        if voice_id not in metadata:
            return None
        
        voice_data = metadata[voice_id]
        
        if request.name is not None:
            voice_data['name'] = request.name
        if request.description is not None:
            voice_data['description'] = request.description
        if request.language is not None:
            voice_data['language'] = request.language
        
        self._save_metadata(metadata)
        
        return await self.get_voice(voice_id)
    
    async def delete_voice(self, voice_id: str) -> bool:
        """Удалить голос"""
        metadata = self._load_metadata()
        
        if voice_id not in metadata:
            return False
        
        # Удаляем директорию с файлами
        voice_dir = self.voices_dir / voice_id
        if voice_dir.exists():
            shutil.rmtree(voice_dir)
        
        # Удаляем из метаданных
        del metadata[voice_id]
        self._save_metadata(metadata)
        
        logger.info(f"Удален голос: {voice_id}")
        return True
    
    async def add_training_sample(
        self,
        voice_id: str,
        audio_file: Path,
        text: str,
        duration: float
    ) -> Optional[TrainingSample]:
        """Добавить обучающий сэмпл"""
        metadata = self._load_metadata()
        
        if voice_id not in metadata:
            return None
        
        sample_id = str(uuid.uuid4())
        voice_dir = self.voices_dir / voice_id
        samples_dir = voice_dir / "samples"
        samples_dir.mkdir(exist_ok=True)
        
        # Копируем аудио файл
        sample_path = samples_dir / f"{sample_id}.wav"
        shutil.copy(audio_file, sample_path)
        
        # Сохраняем транскрипцию
        transcript_path = samples_dir / f"{sample_id}.txt"
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # Обновляем счетчик сэмплов
        metadata[voice_id]['sample_count'] = metadata[voice_id].get('sample_count', 0) + 1
        self._save_metadata(metadata)
        
        logger.info(f"Добавлен сэмпл {sample_id} для голоса {voice_id}")
        
        return TrainingSample(
            id=sample_id,
            voice_id=voice_id,
            audio_path=str(sample_path),
            text=text,
            duration=duration,
            created_at=datetime.now()
        )
    
    async def list_training_samples(self, voice_id: str) -> Optional[TrainingSampleListResponse]:
        """Получить список обучающих сэмплов"""
        metadata = self._load_metadata()
        
        if voice_id not in metadata:
            return None
        
        voice_dir = self.voices_dir / voice_id
        samples_dir = voice_dir / "samples"
        
        if not samples_dir.exists():
            return TrainingSampleListResponse(samples=[], total=0)
        
        samples = []
        for audio_file in samples_dir.glob("*.wav"):
            sample_id = audio_file.stem
            transcript_file = samples_dir / f"{sample_id}.txt"
            
            if transcript_file.exists():
                with open(transcript_file, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                # Получаем длительность (упрощенно)
                duration = audio_file.stat().st_size / (16000 * 2)  # Примерная оценка
                
                samples.append(TrainingSample(
                    id=sample_id,
                    voice_id=voice_id,
                    audio_path=str(audio_file),
                    text=text,
                    duration=duration,
                    created_at=datetime.fromtimestamp(audio_file.stat().st_ctime)
                ))
        
        return TrainingSampleListResponse(
            samples=sorted(samples, key=lambda x: x.created_at, reverse=True),
            total=len(samples)
        )
    
    async def delete_training_sample(self, voice_id: str, sample_id: str) -> bool:
        """Удалить обучающий сэмпл"""
        metadata = self._load_metadata()
        
        if voice_id not in metadata:
            return False
        
        voice_dir = self.voices_dir / voice_id
        samples_dir = voice_dir / "samples"
        
        audio_file = samples_dir / f"{sample_id}.wav"
        transcript_file = samples_dir / f"{sample_id}.txt"
        
        deleted = False
        if audio_file.exists():
            audio_file.unlink()
            deleted = True
        if transcript_file.exists():
            transcript_file.unlink()
        
        if deleted:
            metadata[voice_id]['sample_count'] = max(0, metadata[voice_id].get('sample_count', 1) - 1)
            self._save_metadata(metadata)
            logger.info(f"Удален сэмпл {sample_id} голоса {voice_id}")
        
        return deleted
    
    async def start_training(
        self,
        request: VoiceTrainingRequest
    ) -> VoiceTrainingStatus:
        """Запустить обучение голоса"""
        voice_id = request.voice_id
        
        # Проверяем существование голоса
        voice = await self.get_voice(voice_id)
        if not voice:
            raise ValueError(f"Голос {voice_id} не найден")
        
        # Проверяем наличие сэмплов
        samples = await self.list_training_samples(voice_id)
        if not samples or samples.total < 5:
            raise ValueError(f"Недостаточно обучающих сэмплов (минимум 5, есть {samples.total if samples else 0})")
        
        # Создаем статус обучения
        status = VoiceTrainingStatus(
            voice_id=voice_id,
            status='training',
            progress=0.0,
            current_epoch=0,
            total_epochs=request.epochs,
            started_at=datetime.now()
        )
        
        self.training_status[voice_id] = status
        
        # Обновляем метаданные
        metadata = self._load_metadata()
        metadata[voice_id]['training_status'] = 'training'
        self._save_metadata(metadata)
        
        # Запускаем обучение в фоне
        asyncio.create_task(self._train_voice_background(request, status))
        
        logger.info(f"Запущено обучение голоса {voice_id}")
        return status
    
    async def _train_voice_background(
        self,
        request: VoiceTrainingRequest,
        status: VoiceTrainingStatus
    ):
        """Фоновое обучение голоса"""
        voice_id = request.voice_id
        
        try:
            # TODO: Интеграция с GPT-SoVITS fine-tuning
            # Здесь будет вызов training/voice_clone.py
            
            # Симуляция обучения для демонстрации
            for epoch in range(1, request.epochs + 1):
                await asyncio.sleep(0.1)  # Симуляция работы
                
                status.current_epoch = epoch
                status.progress = (epoch / request.epochs) * 100
                status.loss = 1.0 / (epoch + 1)  # Симуляция уменьшения loss
                status.eta_seconds = int((request.epochs - epoch) * 0.1)
                
                self.training_status[voice_id] = status
            
            # Завершение обучения
            status.status = 'completed'
            status.progress = 100.0
            status.completed_at = datetime.now()
            
            # Обновляем метаданные
            metadata = self._load_metadata()
            metadata[voice_id]['is_trained'] = True
            metadata[voice_id]['training_status'] = 'completed'
            self._save_metadata(metadata)
            
            logger.info(f"Обучение голоса {voice_id} завершено")
            
        except Exception as e:
            logger.error(f"Ошибка обучения голоса {voice_id}: {e}")
            status.status = 'failed'
            status.error = str(e)
            
            metadata = self._load_metadata()
            metadata[voice_id]['training_status'] = 'failed'
            self._save_metadata(metadata)
    
    async def get_training_status(self, voice_id: str) -> Optional[VoiceTrainingStatus]:
        """Получить статус обучения"""
        if voice_id in self.training_status:
            return self.training_status[voice_id]
        
        # Проверяем метаданные
        voice = await self.get_voice(voice_id)
        if not voice:
            return None
        
        return VoiceTrainingStatus(
            voice_id=voice_id,
            status=voice.training_status or 'idle',
            progress=100.0 if voice.is_trained else 0.0,
            current_epoch=0,
            total_epochs=0
        )
    
    async def cancel_training(self, voice_id: str) -> bool:
        """Отменить обучение"""
        if voice_id not in self.training_status:
            return False
        
        status = self.training_status[voice_id]
        status.status = 'cancelled'
        
        metadata = self._load_metadata()
        if voice_id in metadata:
            metadata[voice_id]['training_status'] = 'cancelled'
            self._save_metadata(metadata)
        
        logger.info(f"Обучение голоса {voice_id} отменено")
        return True


# Singleton instance
_voice_service: Optional[VoiceService] = None


def get_voice_service() -> VoiceService:
    """Получить singleton instance сервиса"""
    global _voice_service
    if _voice_service is None:
        _voice_service = VoiceService()
    return _voice_service
