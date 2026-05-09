"""
Роутер для голосовых функций (TTS/STT)
"""
import os
import uuid
import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Header, Depends
from fastapi.responses import FileResponse
import httpx
import asyncio

from models.voice_models import (
    TTSRequest, TTSResponse,
    STTRequest, STTResponse,
    VoiceCloneRequest, VoiceCloneResponse,
    VoiceInfo, VoiceListResponse,
    VoiceCreateRequest, VoiceUpdateRequest,
    TrainingSampleListResponse,
    VoiceTrainingRequest, VoiceTrainingStatus,
    VoiceTestRequest, VoiceTestResponse
)
from services.voice_service import get_voice_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/voice", tags=["voice"])

# Директории для хранения аудио
AUDIO_DIR = Path("audio_cache")
AUDIO_DIR.mkdir(exist_ok=True)

# Конфигурация GPT-SoVITS
GPT_SOVITS_URL = os.getenv("GPT_SOVITS_URL", "http://localhost:9880")
GPT_SOVITS_ENABLED = os.getenv("GPT_SOVITS_ENABLED", "false").lower() == "true"

# Конфигурация Vosk/Whisper для STT
STT_ENABLED = os.getenv("STT_ENABLED", "false").lower() == "true"
STT_MODEL = os.getenv("STT_MODEL", "vosk")  # vosk или whisper


async def verify_api_key(x_api_key: str = Header(...)):
    """Проверка API ключа"""
    expected_key = os.getenv("API_KEY", "your-secret-key-here")
    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


@router.post("/tts", response_model=TTSResponse)
async def text_to_speech(
    request: TTSRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Синтез речи из текста
    
    Использует GPT-SoVITS для генерации естественной речи.
    Поддерживает клонирование голоса через референсное аудио.
    """
    if not GPT_SOVITS_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="TTS service is not enabled. Set GPT_SOVITS_ENABLED=true"
        )
    
    try:
        # Подготовка запроса к GPT-SoVITS
        payload = {
            "text": request.text,
            "text_lang": request.language,
            "speed": request.speed
        }
        
        # Добавление референсного аудио для клонирования голоса
        if request.reference_audio and request.reference_text:
            payload["ref_audio_path"] = request.reference_audio
            payload["prompt_text"] = request.reference_text
            payload["prompt_lang"] = request.language
        
        # Запрос к GPT-SoVITS API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{GPT_SOVITS_URL}/tts",
                json=payload
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"TTS service error: {response.text}"
                )
            
            # Сохранение аудио
            audio_id = str(uuid.uuid4())
            audio_path = AUDIO_DIR / f"{audio_id}.wav"
            
            with open(audio_path, "wb") as f:
                f.write(response.content)
            
            # Получение длительности аудио (примерная оценка)
            duration = len(request.text) / 15.0  # ~15 символов в секунду
            
            return TTSResponse(
                audio_url=f"/api/v1/voice/audio/{audio_id}.wav",
                duration=duration,
                text=request.text
            )
    
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="TTS service timeout"
        )
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"TTS error: {str(e)}"
        )


@router.post("/stt", response_model=STTResponse)
async def speech_to_text(
    audio: UploadFile = File(...),
    language: str = "ru",
    api_key: str = Depends(verify_api_key)
):
    """
    Распознавание речи из аудио
    
    Использует Vosk или Whisper для распознавания речи.
    Поддерживает русский и английский языки.
    """
    if not STT_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="STT service is not enabled. Set STT_ENABLED=true"
        )
    
    try:
        # Сохранение загруженного аудио
        audio_id = str(uuid.uuid4())
        audio_path = AUDIO_DIR / f"{audio_id}_input.wav"
        
        with open(audio_path, "wb") as f:
            content = await audio.read()
            f.write(content)
        
        # Распознавание речи
        if STT_MODEL == "vosk":
            text, confidence = await _recognize_with_vosk(audio_path, language)
        else:
            text, confidence = await _recognize_with_whisper(audio_path, language)
        
        # Удаление временного файла
        audio_path.unlink()
        
        return STTResponse(
            text=text,
            confidence=confidence,
            language=language
        )
    
    except Exception as e:
        logger.error(f"STT error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"STT error: {str(e)}"
        )


@router.post("/clone", response_model=VoiceCloneResponse)
async def clone_voice(
    audio: UploadFile = File(...),
    request: VoiceCloneRequest = Depends(),
    api_key: str = Depends(verify_api_key)
):
    """
    Клонирование голоса из референсного аудио
    
    Сохраняет референсное аудио для использования в TTS.
    """
    if not GPT_SOVITS_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Voice cloning is not enabled. Set GPT_SOVITS_ENABLED=true"
        )
    
    try:
        # Сохранение референсного аудио
        voice_id = str(uuid.uuid4())
        audio_path = AUDIO_DIR / f"ref_{voice_id}.wav"
        
        with open(audio_path, "wb") as f:
            content = await audio.read()
            f.write(content)
        
        logger.info(f"Voice cloned: {voice_id}")
        
        return VoiceCloneResponse(
            voice_id=voice_id,
            message=f"Voice cloned successfully. Use reference_audio='audio_cache/ref_{voice_id}.wav' in TTS requests"
        )
    
    except Exception as e:
        logger.error(f"Voice cloning error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Voice cloning error: {str(e)}"
        )


@router.get("/audio/{filename}")
async def get_audio(
    filename: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Получение аудио файла
    """
    audio_path = AUDIO_DIR / filename
    
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        audio_path,
        media_type="audio/wav",
        filename=filename
    )


@router.delete("/audio/{filename}")
async def delete_audio(
    filename: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Удаление аудио файла
    """
    audio_path = AUDIO_DIR / filename
    
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    audio_path.unlink()
    
    return {"message": "Audio file deleted"}


# Вспомогательные функции для STT

async def _recognize_with_vosk(audio_path: Path, language: str) -> tuple[str, float]:
    """Распознавание с помощью Vosk"""
    try:
        import vosk
        import wave
        import json
        
        # Загрузка модели Vosk
        model_path = f"models/vosk-model-small-{language}"
        if not Path(model_path).exists():
            raise HTTPException(
                status_code=503,
                detail=f"Vosk model not found: {model_path}"
            )
        
        model = vosk.Model(model_path)
        
        # Открытие аудио файла
        wf = wave.open(str(audio_path), "rb")
        
        # Проверка формата
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in [8000, 16000, 32000, 44100, 48000]:
            raise HTTPException(
                status_code=400,
                detail="Audio must be WAV format mono PCM"
            )
        
        # Распознавание
        rec = vosk.KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)
        
        results = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if "text" in result:
                    results.append(result["text"])
        
        # Финальный результат
        final_result = json.loads(rec.FinalResult())
        if "text" in final_result:
            results.append(final_result["text"])
        
        text = " ".join(results).strip()
        confidence = 0.85  # Vosk не предоставляет точную уверенность
        
        return text, confidence
    
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="Vosk is not installed. Install with: pip install vosk"
        )
    except Exception as e:
        logger.error(f"Vosk recognition error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Vosk recognition error: {str(e)}"
        )


async def _recognize_with_whisper(audio_path: Path, language: str) -> tuple[str, float]:
    """Распознавание с помощью Whisper"""
    try:
        import whisper
        
        # Загрузка модели Whisper
        model = whisper.load_model("base")
        
        # Распознавание
        result = model.transcribe(
            str(audio_path),
            language=language,
            fp16=False
        )
        
        text = result["text"].strip()
        
        # Whisper предоставляет уверенность для каждого сегмента
        segments = result.get("segments", [])
        if segments:
            avg_confidence = sum(s.get("no_speech_prob", 0.0) for s in segments) / len(segments)
            confidence = 1.0 - avg_confidence
        else:
            confidence = 0.9
        
        return text, confidence
    
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="Whisper is not installed. Install with: pip install openai-whisper"
        )
    except Exception as e:
        logger.error(f"Whisper recognition error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Whisper recognition error: {str(e)}"
        )


# === Voice Management Endpoints ===

@router.get("/voices", response_model=VoiceListResponse)
async def list_voices(api_key: str = Depends(verify_api_key)):
    """
    Получить список всех голосов в библиотеке
    """
    service = get_voice_service()
    return await service.list_voices()


@router.get("/voices/{voice_id}", response_model=VoiceInfo)
async def get_voice(
    voice_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Получить информацию о конкретном голосе
    """
    service = get_voice_service()
    voice = await service.get_voice(voice_id)
    
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    return voice


@router.post("/voices", response_model=VoiceInfo)
async def create_voice(
    name: str,
    reference_text: str,
    audio: UploadFile = File(...),
    description: Optional[str] = None,
    language: str = "ru",
    api_key: str = Depends(verify_api_key)
):
    """
    Создать новый голос из референсного аудио
    """
    service = get_voice_service()
    
    # Сохраняем временный файл
    temp_path = AUDIO_DIR / f"temp_{uuid.uuid4()}.wav"
    try:
        with open(temp_path, "wb") as f:
            content = await audio.read()
            f.write(content)
        
        request = VoiceCreateRequest(
            name=name,
            description=description,
            language=language,
            reference_text=reference_text
        )
        
        voice = await service.create_voice(request, temp_path)
        return voice
    
    finally:
        if temp_path.exists():
            temp_path.unlink()


@router.put("/voices/{voice_id}", response_model=VoiceInfo)
async def update_voice(
    voice_id: str,
    request: VoiceUpdateRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Обновить информацию о голосе
    """
    service = get_voice_service()
    voice = await service.update_voice(voice_id, request)
    
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    return voice


@router.delete("/voices/{voice_id}")
async def delete_voice(
    voice_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Удалить голос из библиотеки
    """
    service = get_voice_service()
    success = await service.delete_voice(voice_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    return {"message": "Voice deleted successfully"}


@router.post("/voices/{voice_id}/samples")
async def add_training_sample(
    voice_id: str,
    text: str,
    audio: UploadFile = File(...),
    api_key: str = Depends(verify_api_key)
):
    """
    Добавить обучающий сэмпл для голоса
    """
    service = get_voice_service()
    
    # Сохраняем временный файл
    temp_path = AUDIO_DIR / f"temp_{uuid.uuid4()}.wav"
    try:
        with open(temp_path, "wb") as f:
            content = await audio.read()
            f.write(content)
        
        # Примерная длительность
        duration = temp_path.stat().st_size / (16000 * 2)
        
        sample = await service.add_training_sample(voice_id, temp_path, text, duration)
        
        if not sample:
            raise HTTPException(status_code=404, detail="Voice not found")
        
        return sample
    
    finally:
        if temp_path.exists():
            temp_path.unlink()


@router.get("/voices/{voice_id}/samples", response_model=TrainingSampleListResponse)
async def list_training_samples(
    voice_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Получить список обучающих сэмплов
    """
    service = get_voice_service()
    samples = await service.list_training_samples(voice_id)
    
    if samples is None:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    return samples


@router.delete("/voices/{voice_id}/samples/{sample_id}")
async def delete_training_sample(
    voice_id: str,
    sample_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Удалить обучающий сэмпл
    """
    service = get_voice_service()
    success = await service.delete_training_sample(voice_id, sample_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Sample not found")
    
    return {"message": "Sample deleted successfully"}


@router.post("/voices/{voice_id}/train", response_model=VoiceTrainingStatus)
async def start_training(
    voice_id: str,
    request: VoiceTrainingRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Запустить обучение голоса
    """
    service = get_voice_service()
    
    try:
        status = await service.start_training(request)
        return status
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/voices/{voice_id}/training-status", response_model=VoiceTrainingStatus)
async def get_training_status(
    voice_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Получить статус обучения голоса
    """
    service = get_voice_service()
    status = await service.get_training_status(voice_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    return status


@router.post("/voices/{voice_id}/cancel-training")
async def cancel_training(
    voice_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Отменить обучение голоса
    """
    service = get_voice_service()
    success = await service.cancel_training(voice_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Training not found or already completed")
    
    return {"message": "Training cancelled"}


@router.post("/voices/{voice_id}/test", response_model=VoiceTestResponse)
async def test_voice(
    voice_id: str,
    request: VoiceTestRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Протестировать голос с заданным текстом
    """
    service = get_voice_service()
    voice = await service.get_voice(voice_id)
    
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    # Используем существующий TTS endpoint с референсным аудио
    tts_request = TTSRequest(
        text=request.test_text,
        language=request.language,
        voice_id=voice_id
    )
    
    # Вызываем TTS с референсным аудио голоса
    if not GPT_SOVITS_ENABLED:
        raise HTTPException(status_code=503, detail="TTS service is not enabled")
    
    try:
        payload = {
            "text": request.test_text,
            "text_lang": request.language,
            "ref_audio_path": voice.reference_audio,
            "prompt_text": voice.reference_text,
            "prompt_lang": voice.language
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{GPT_SOVITS_URL}/tts",
                json=payload
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"TTS service error: {response.text}"
                )
            
            # Сохранение тестового аудио
            audio_id = str(uuid.uuid4())
            audio_path = AUDIO_DIR / f"test_{audio_id}.wav"
            
            with open(audio_path, "wb") as f:
                f.write(response.content)
            
            duration = len(request.test_text) / 15.0
            
            return VoiceTestResponse(
                audio_url=f"/api/v1/voice/audio/test_{audio_id}.wav",
                duration=duration,
                voice_id=voice_id
            )
    
    except Exception as e:
        logger.error(f"Voice test error: {e}")
        raise HTTPException(status_code=500, detail=f"Voice test error: {str(e)}")
