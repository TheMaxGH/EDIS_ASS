"""
Тесты для Voice API endpoints
"""
import pytest
import asyncio
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import io

# Импортируем приложение
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from web.backend.main import app
from web.backend.services.voice_service import VoiceService


@pytest.fixture
def client():
    """Тестовый клиент FastAPI"""
    return TestClient(app)


@pytest.fixture
def api_key():
    """API ключ для тестов"""
    return "your-secret-key-here"


@pytest.fixture
def headers(api_key):
    """Заголовки с API ключом"""
    return {"X-API-Key": api_key}


@pytest.fixture
def mock_audio_file():
    """Мок аудио файла"""
    audio_data = b"RIFF" + b"\x00" * 100  # Простой WAV заголовок
    return ("test.wav", io.BytesIO(audio_data), "audio/wav")


@pytest.fixture
def voice_service():
    """Мок сервиса голосов"""
    return VoiceService(voices_dir="test_data/voices")


class TestTTSEndpoint:
    """Тесты для TTS endpoint"""
    
    def test_tts_success(self, client, headers):
        """Тест успешного синтеза речи"""
        with patch('web.backend.routers.voice.GPT_SOVITS_ENABLED', True):
            with patch('httpx.AsyncClient') as mock_client:
                # Мокаем ответ от GPT-SoVITS
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.content = b"fake_audio_data"
                
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                    return_value=mock_response
                )
                
                response = client.post(
                    "/api/v1/voice/tts",
                    json={
                        "text": "Привет, мир!",
                        "language": "ru",
                        "speed": 1.0
                    },
                    headers=headers
                )
                
                assert response.status_code == 200
                data = response.json()
                assert "audio_url" in data
                assert "duration" in data
                assert data["text"] == "Привет, мир!"
    
    def test_tts_service_disabled(self, client, headers):
        """Тест когда TTS сервис отключен"""
        with patch('web.backend.routers.voice.GPT_SOVITS_ENABLED', False):
            response = client.post(
                "/api/v1/voice/tts",
                json={"text": "Test", "language": "ru"},
                headers=headers
            )
            
            assert response.status_code == 503
            assert "not enabled" in response.json()["detail"]
    
    def test_tts_invalid_api_key(self, client):
        """Тест с неверным API ключом"""
        response = client.post(
            "/api/v1/voice/tts",
            json={"text": "Test", "language": "ru"},
            headers={"X-API-Key": "wrong-key"}
        )
        
        assert response.status_code == 401


class TestSTTEndpoint:
    """Тесты для STT endpoint"""
    
    def test_stt_success_whisper(self, client, headers, mock_audio_file):
        """Тест успешного распознавания с Whisper"""
        with patch('web.backend.routers.voice.STT_ENABLED', True):
            with patch('web.backend.routers.voice.STT_MODEL', 'whisper'):
                with patch('web.backend.routers.voice._recognize_with_whisper') as mock_recognize:
                    mock_recognize.return_value = ("Распознанный текст", 0.95)
                    
                    response = client.post(
                        "/api/v1/voice/stt",
                        files={"audio": mock_audio_file},
                        data={"language": "ru"},
                        headers=headers
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["text"] == "Распознанный текст"
                    assert data["confidence"] == 0.95
    
    def test_stt_service_disabled(self, client, headers, mock_audio_file):
        """Тест когда STT сервис отключен"""
        with patch('web.backend.routers.voice.STT_ENABLED', False):
            response = client.post(
                "/api/v1/voice/stt",
                files={"audio": mock_audio_file},
                headers=headers
            )
            
            assert response.status_code == 503


class TestVoiceManagementEndpoints:
    """Тесты для Voice Management endpoints"""
    
    @pytest.mark.asyncio
    async def test_list_voices_empty(self, client, headers):
        """Тест получения пустого списка голосов"""
        with patch('web.backend.routers.voice.get_voice_service') as mock_service:
            mock_service.return_value.list_voices = AsyncMock(
                return_value={"voices": [], "total": 0}
            )
            
            response = client.get("/api/v1/voice/voices", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 0
            assert len(data["voices"]) == 0
    
    def test_create_voice_success(self, client, headers, mock_audio_file):
        """Тест создания нового голоса"""
        with patch('web.backend.routers.voice.get_voice_service') as mock_service:
            from datetime import datetime
            mock_voice = {
                "id": "test-voice-id",
                "name": "Test Voice",
                "description": "Test description",
                "language": "ru",
                "reference_audio": "/path/to/audio.wav",
                "reference_text": "Test text",
                "created_at": datetime.now().isoformat(),
                "is_trained": False,
                "training_status": "idle",
                "sample_count": 0
            }
            
            mock_service.return_value.create_voice = AsyncMock(return_value=mock_voice)
            
            response = client.post(
                "/api/v1/voice/voices",
                files={"audio": mock_audio_file},
                data={
                    "name": "Test Voice",
                    "reference_text": "Test text",
                    "description": "Test description",
                    "language": "ru"
                },
                headers=headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Test Voice"
            assert data["id"] == "test-voice-id"
    
    def test_get_voice_not_found(self, client, headers):
        """Тест получения несуществующего голоса"""
        with patch('web.backend.routers.voice.get_voice_service') as mock_service:
            mock_service.return_value.get_voice = AsyncMock(return_value=None)
            
            response = client.get(
                "/api/v1/voice/voices/nonexistent-id",
                headers=headers
            )
            
            assert response.status_code == 404
    
    def test_delete_voice_success(self, client, headers):
        """Тест удаления голоса"""
        with patch('web.backend.routers.voice.get_voice_service') as mock_service:
            mock_service.return_value.delete_voice = AsyncMock(return_value=True)
            
            response = client.delete(
                "/api/v1/voice/voices/test-voice-id",
                headers=headers
            )
            
            assert response.status_code == 200
            assert "deleted" in response.json()["message"]
    
    def test_add_training_sample(self, client, headers, mock_audio_file):
        """Тест добавления обучающего сэмпла"""
        with patch('web.backend.routers.voice.get_voice_service') as mock_service:
            from datetime import datetime
            mock_sample = {
                "id": "sample-id",
                "voice_id": "voice-id",
                "audio_path": "/path/to/sample.wav",
                "text": "Sample text",
                "duration": 2.5,
                "created_at": datetime.now().isoformat()
            }
            
            mock_service.return_value.add_training_sample = AsyncMock(
                return_value=mock_sample
            )
            
            response = client.post(
                "/api/v1/voice/voices/voice-id/samples",
                files={"audio": mock_audio_file},
                data={"text": "Sample text"},
                headers=headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["text"] == "Sample text"
    
    def test_start_training_insufficient_samples(self, client, headers):
        """Тест запуска обучения с недостаточным количеством сэмплов"""
        with patch('web.backend.routers.voice.get_voice_service') as mock_service:
            mock_service.return_value.start_training = AsyncMock(
                side_effect=ValueError("Недостаточно обучающих сэмплов")
            )
            
            response = client.post(
                "/api/v1/voice/voices/voice-id/train",
                json={
                    "voice_id": "voice-id",
                    "epochs": 100,
                    "batch_size": 4,
                    "learning_rate": 0.0001,
                    "save_interval": 10
                },
                headers=headers
            )
            
            assert response.status_code == 400
            assert "Недостаточно" in response.json()["detail"]
    
    def test_get_training_status(self, client, headers):
        """Тест получения статуса обучения"""
        with patch('web.backend.routers.voice.get_voice_service') as mock_service:
            mock_status = {
                "voice_id": "voice-id",
                "status": "training",
                "progress": 45.5,
                "current_epoch": 45,
                "total_epochs": 100,
                "loss": 0.123,
                "eta_seconds": 300
            }
            
            mock_service.return_value.get_training_status = AsyncMock(
                return_value=mock_status
            )
            
            response = client.get(
                "/api/v1/voice/voices/voice-id/training-status",
                headers=headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "training"
            assert data["progress"] == 45.5
    
    def test_cancel_training(self, client, headers):
        """Тест отмены обучения"""
        with patch('web.backend.routers.voice.get_voice_service') as mock_service:
            mock_service.return_value.cancel_training = AsyncMock(return_value=True)
            
            response = client.post(
                "/api/v1/voice/voices/voice-id/cancel-training",
                headers=headers
            )
            
            assert response.status_code == 200
            assert "cancelled" in response.json()["message"]
    
    def test_test_voice(self, client, headers):
        """Тест тестирования голоса"""
        with patch('web.backend.routers.voice.get_voice_service') as mock_service:
            with patch('web.backend.routers.voice.GPT_SOVITS_ENABLED', True):
                with patch('httpx.AsyncClient') as mock_client:
                    # Мокаем голос
                    from datetime import datetime
                    mock_voice = {
                        "id": "voice-id",
                        "name": "Test Voice",
                        "reference_audio": "/path/to/ref.wav",
                        "reference_text": "Reference text",
                        "language": "ru",
                        "created_at": datetime.now().isoformat(),
                        "is_trained": True,
                        "training_status": "completed",
                        "sample_count": 10
                    }
                    
                    mock_service.return_value.get_voice = AsyncMock(
                        return_value=mock_voice
                    )
                    
                    # Мокаем TTS ответ
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_response.content = b"test_audio"
                    
                    mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                        return_value=mock_response
                    )
                    
                    response = client.post(
                        "/api/v1/voice/voices/voice-id/test",
                        json={
                            "voice_id": "voice-id",
                            "test_text": "Test text",
                            "language": "ru"
                        },
                        headers=headers
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert "audio_url" in data
                    assert data["voice_id"] == "voice-id"


class TestVoiceService:
    """Тесты для VoiceService"""
    
    @pytest.mark.asyncio
    async def test_create_voice(self, voice_service, tmp_path):
        """Тест создания голоса в сервисе"""
        from web.backend.models.voice_models import VoiceCreateRequest
        
        # Создаем временный аудио файл
        audio_file = tmp_path / "test.wav"
        audio_file.write_bytes(b"fake_audio")
        
        request = VoiceCreateRequest(
            name="Test Voice",
            description="Test",
            language="ru",
            reference_text="Test text"
        )
        
        voice = await voice_service.create_voice(request, audio_file)
        
        assert voice.name == "Test Voice"
        assert voice.language == "ru"
        assert voice.is_trained == False
    
    @pytest.mark.asyncio
    async def test_list_voices(self, voice_service):
        """Тест получения списка голосов"""
        result = await voice_service.list_voices()
        
        assert isinstance(result.voices, list)
        assert result.total == len(result.voices)
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_voice(self, voice_service):
        """Тест удаления несуществующего голоса"""
        result = await voice_service.delete_voice("nonexistent-id")
        
        assert result == False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
