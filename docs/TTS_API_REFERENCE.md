# 🎤 TTS API Quick Reference

> Быстрая справка по Voice API для разработчиков

## 📡 Endpoints

### Base URL
```
http://localhost:8000/api/v1/voice
```

### Authentication
```http
X-API-Key: your-api-key-here
```

---

## 🔊 Text-to-Speech

### POST `/tts`

Синтез речи из текста.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/voice/tts \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{
    "text": "Привет, мир!",
    "language": "ru",
    "speed": 1.0
  }'
```

**Response:**
```json
{
  "audio_url": "/api/v1/voice/audio/tts_1234567890.wav",
  "duration": 2.5,
  "sample_rate": 32000
}
```

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `text` | string | ✅ | - | Текст для озвучки (макс 1000 символов) |
| `language` | string | ❌ | "ru" | Язык: "ru", "en", "zh", "ja" |
| `speed` | float | ❌ | 1.0 | Скорость речи (0.5-2.0) |
| `voice_id` | string | ❌ | null | ID кастомного голоса |

---

## 🎙️ Speech-to-Text

### POST `/stt`

Распознавание речи из аудио.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/voice/stt \
  -H "X-API-Key: your-key" \
  -F "audio=@recording.wav" \
  -F "language=ru" \
  -F "engine=vosk"
```

**Response:**
```json
{
  "text": "Привет, как дела?",
  "confidence": 0.95,
  "language": "ru",
  "duration": 3.2
}
```

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `audio` | file | ✅ | - | Аудио файл (WAV, MP3, OGG, макс 10MB) |
| `language` | string | ❌ | "ru" | Язык для распознавания |
| `engine` | string | ❌ | "vosk" | Движок: "vosk" (быстрый) или "whisper" (точный) |

---

## 🎭 Voice Cloning

### POST `/clone`

Клонирование голоса из референсного аудио.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/voice/clone \
  -H "X-API-Key: your-key" \
  -F "audio=@reference.wav" \
  -F "transcript=Это текст из аудио" \
  -F "voice_name=Мой голос" \
  -F "mode=quick"
```

**Response:**
```json
{
  "voice_id": "voice_abc123",
  "name": "Мой голос",
  "status": "ready",
  "reference_audio": "/api/v1/voice/audio/ref_abc123.wav"
}
```

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `audio` | file | ✅ | - | Референсное аудио (3-10 сек, WAV/MP3) |
| `transcript` | string | ✅ | - | Точный текст из аудио |
| `voice_name` | string | ✅ | - | Название голоса |
| `mode` | string | ❌ | "quick" | Режим: "quick" (быстро) или "fine-tune" (качественно) |

---

## 📥 Download Audio

### GET `/audio/{filename}`

Скачать сгенерированный аудио файл.

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/voice/audio/tts_1234567890.wav \
  -H "X-API-Key: your-key" \
  -o output.wav
```

**Response:** Binary audio file (WAV)

---

## 🗑️ Delete Audio

### DELETE `/audio/{filename}`

Удалить аудио файл из кэша.

**Request:**
```bash
curl -X DELETE http://localhost:8000/api/v1/voice/audio/tts_1234567890.wav \
  -H "X-API-Key: your-key"
```

**Response:**
```json
{
  "success": true,
  "message": "Audio file deleted"
}
```

---

## 🐍 Python Examples

### TTS Example

```python
import requests

url = "http://localhost:8000/api/v1/voice/tts"
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "your-api-key"
}
data = {
    "text": "Привет, мир!",
    "language": "ru",
    "speed": 1.0
}

response = requests.post(url, json=data, headers=headers)
result = response.json()

# Download audio
audio_url = f"http://localhost:8000{result['audio_url']}"
audio_response = requests.get(audio_url, headers=headers)

with open("output.wav", "wb") as f:
    f.write(audio_response.content)

print(f"Audio saved! Duration: {result['duration']}s")
```

### STT Example

```python
import requests

url = "http://localhost:8000/api/v1/voice/stt"
headers = {"X-API-Key": "your-api-key"}

with open("recording.wav", "rb") as audio_file:
    files = {"audio": audio_file}
    data = {
        "language": "ru",
        "engine": "vosk"
    }
    
    response = requests.post(url, files=files, data=data, headers=headers)
    result = response.json()
    
    print(f"Recognized: {result['text']}")
    print(f"Confidence: {result['confidence']}")
```

### Voice Cloning Example

```python
import requests

url = "http://localhost:8000/api/v1/voice/clone"
headers = {"X-API-Key": "your-api-key"}

with open("reference.wav", "rb") as audio_file:
    files = {"audio": audio_file}
    data = {
        "transcript": "Это текст из аудио",
        "voice_name": "Мой голос",
        "mode": "quick"
    }
    
    response = requests.post(url, files=files, data=data, headers=headers)
    result = response.json()
    
    print(f"Voice cloned! ID: {result['voice_id']}")
    
    # Use cloned voice for TTS
    tts_data = {
        "text": "Тест клонированного голоса",
        "voice_id": result['voice_id']
    }
    tts_response = requests.post(
        "http://localhost:8000/api/v1/voice/tts",
        json=tts_data,
        headers=headers
    )
```

---

## 🌐 JavaScript/TypeScript Examples

### TTS Example

```typescript
const tts = async (text: string) => {
  const response = await fetch('http://localhost:8000/api/v1/voice/tts', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'your-api-key'
    },
    body: JSON.stringify({
      text,
      language: 'ru',
      speed: 1.0
    })
  });
  
  const result = await response.json();
  
  // Play audio
  const audio = new Audio(`http://localhost:8000${result.audio_url}`);
  await audio.play();
  
  console.log(`Playing audio (${result.duration}s)`);
};

await tts('Привет, мир!');
```

### STT Example

```typescript
const stt = async (audioBlob: Blob) => {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.wav');
  formData.append('language', 'ru');
  formData.append('engine', 'vosk');
  
  const response = await fetch('http://localhost:8000/api/v1/voice/stt', {
    method: 'POST',
    headers: {
      'X-API-Key': 'your-api-key'
    },
    body: formData
  });
  
  const result = await response.json();
  console.log(`Recognized: ${result.text}`);
  console.log(`Confidence: ${result.confidence}`);
  
  return result.text;
};

// Record audio
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
const mediaRecorder = new MediaRecorder(stream);
const chunks: Blob[] = [];

mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
mediaRecorder.onstop = async () => {
  const audioBlob = new Blob(chunks, { type: 'audio/webm' });
  const text = await stt(audioBlob);
  console.log('Transcribed:', text);
};

mediaRecorder.start();
// ... user speaks ...
mediaRecorder.stop();
```

---

## ⚠️ Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `400` | Bad Request | Check request parameters |
| `401` | Unauthorized | Verify API key |
| `413` | Payload Too Large | Reduce audio file size (<10MB) |
| `422` | Validation Error | Check Pydantic model requirements |
| `500` | Internal Server Error | Check backend logs |
| `503` | Service Unavailable | GPT-SoVITS server not running |

---

## 🔧 Configuration

### Environment Variables

```bash
# .env
OPENAI_API_KEY=your-key-here  # For API compatibility
GPT_SOVITS_URL=http://localhost:9880
AUDIO_CACHE_DIR=audio_cache
MAX_AUDIO_SIZE_MB=10
```

### GPT-SoVITS Server

```bash
# Start GPT-SoVITS manually
cd GPT-SoVITS
CUDA_VISIBLE_DEVICES=6 python api.py --port 9880

# Or use system launcher
python run_system.py  # Auto-starts GPT-SoVITS
```

---

## 📊 Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/tts` | 100 requests | 1 minute |
| `/stt` | 50 requests | 1 minute |
| `/clone` | 10 requests | 1 hour |

---

## 🎯 Best Practices

### 1. TTS Optimization

```python
# ✅ Good: Short, natural sentences
text = "Привет! Как дела?"

# ❌ Bad: Very long text
text = "Очень длинный текст..." * 100  # Will be truncated
```

### 2. STT Quality

```python
# ✅ Good: Clean audio, 16kHz+, mono
# ❌ Bad: Noisy audio, low sample rate, stereo

# Preprocess audio
import librosa
audio, sr = librosa.load("input.wav", sr=16000, mono=True)
```

### 3. Voice Cloning

```python
# ✅ Good: 5-10 seconds, clear speech, no background noise
# ❌ Bad: <3 seconds, music, multiple speakers

# Recommended format
# - Sample rate: 32kHz+
# - Bit depth: 16-bit
# - Channels: Mono
# - Duration: 5-10 seconds
```

### 4. Caching

```python
# TTS responses are cached by text hash
# Repeated requests return cached audio instantly

# Clear cache manually
import shutil
shutil.rmtree("audio_cache/tts")
```

---

## 🔗 Related Documentation

- [AUDIO_ARCHITECTURE.md](AUDIO_ARCHITECTURE.md) - Full architecture
- [MASTER_README.md](../MASTER_README.md) - Getting started
- [GPT-SoVITS Docs](https://github.com/RVC-Boss/GPT-SoVITS)

---

*Last updated: 2026-05-09*
