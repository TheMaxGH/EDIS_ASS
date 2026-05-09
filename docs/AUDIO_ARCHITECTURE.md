# 🎤 Аудио архитектура EDIS

> Полная документация по голосовым функциям и TTS системе

## 📋 Содержание

1. [Обзор системы](#обзор-системы)
2. [Архитектура компонентов](#архитектура-компонентов)
3. [Поток данных](#поток-данных)
4. [API Reference](#api-reference)
5. [Конфигурация](#конфигурация)
6. [Производительность](#производительность)

---

## 🎯 Обзор системы

EDIS использует **GPT-SoVITS** для синтеза речи (TTS) и распознавания (STT):

### Ключевые возможности:

- ✅ **Text-to-Speech (TTS)** - озвучка текста с естественной интонацией
- ✅ **Speech-to-Text (STT)** - распознавание речи (Whisper + Vosk)
- ✅ **Voice Cloning** - клонирование голоса из референсного аудио
- ✅ **Multilingual** - поддержка русского, английского, китайского, японского
- ✅ **Real-time** - потоковая генерация аудио
- ✅ **GPU Acceleration** - использование GPU 6 для ускорения

### Технологический стек:

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| **TTS Engine** | GPT-SoVITS | Синтез речи |
| **STT Engine** | Whisper + Vosk | Распознавание речи |
| **Audio Processing** | librosa, soundfile | Обработка аудио |
| **Backend API** | FastAPI | REST API для TTS/STT |
| **Frontend Hook** | React useVoice | Клиентская интеграция |
| **GPU** | CUDA 12.1+ | Ускорение генерации |

---

## 🏗️ Архитектура компонентов

### Общая схема:

```
┌─────────────────────────────────────────────────────────────────┐
│                         EDIS Audio System                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Frontend   │─────▶│   Backend    │─────▶│ GPT-SoVITS   │
│  (React/TS)  │◀─────│  (FastAPI)   │◀─────│  (GPU 6)     │
└──────────────┘      └──────────────┘      └──────────────┘
      │                      │                      │
      │                      │                      │
   useVoice              /api/v1/voice          port 9880
   Hook                  REST API               TTS Server
```

### Детальная архитектура:

```
┌─────────────────────────────────────────────────────────────────┐
│                          Frontend Layer                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │  MessageBubble  │    │   ChatInput     │                    │
│  │   Component     │    │   Component     │                    │
│  └────────┬────────┘    └────────┬────────┘                    │
│           │                      │                              │
│           └──────────┬───────────┘                              │
│                      │                                          │
│              ┌───────▼────────┐                                 │
│              │   useVoice     │                                 │
│              │     Hook       │                                 │
│              │                │                                 │
│              │ • speak()      │                                 │
│              │ • stopSpeaking()│                                │
│              │ • startListening()│                              │
│              │ • stopListening()│                               │
│              └───────┬────────┘                                 │
│                      │                                          │
└──────────────────────┼──────────────────────────────────────────┘
                       │ HTTP/WebSocket
┌──────────────────────▼──────────────────────────────────────────┐
│                         Backend Layer                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              FastAPI Router (/api/v1/voice)              │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │                                                            │  │
│  │  POST /tts          - Text to Speech                     │  │
│  │  POST /stt          - Speech to Text                     │  │
│  │  POST /clone        - Voice Cloning                      │  │
│  │  GET  /audio/{file} - Download Audio                     │  │
│  │  DELETE /audio/{file} - Delete Audio                     │  │
│  │                                                            │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
│  ┌────────────────────────▼─────────────────────────────────┐  │
│  │              Voice Models (Pydantic)                     │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │                                                            │  │
│  │  • TTSRequest      - TTS запрос                          │  │
│  │  • TTSResponse     - TTS ответ                           │  │
│  │  • STTRequest      - STT запрос                          │  │
│  │  • STTResponse     - STT ответ                           │  │
│  │  • VoiceCloneRequest - Клонирование                      │  │
│  │                                                            │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
└───────────────────────────┼─────────────────────────────────────┘
                            │ HTTP (localhost:9880)
┌───────────────────────────▼─────────────────────────────────────┐
│                      GPT-SoVITS Layer                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  GPT-SoVITS Server                        │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │                                                            │  │
│  │  GPU: 6 (CUDA_VISIBLE_DEVICES=6)                         │  │
│  │  Port: 9880                                               │  │
│  │  Models:                                                  │  │
│  │    • s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt     │  │
│  │    • s2G488k.pth                                          │  │
│  │                                                            │  │
│  │  Endpoints:                                               │  │
│  │    POST /tts - Generate speech                           │  │
│  │    POST /set_gpt_weights - Load GPT model                │  │
│  │    POST /set_sovits_weights - Load SoVITS model          │  │
│  │                                                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Поток данных

### 1. Text-to-Speech (TTS) Flow

```
User clicks "Озвучить" button
         │
         ▼
┌────────────────────┐
│  MessageBubble.tsx │
│  onSpeak(text)     │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  BubbleChat.tsx    │
│  handleSpeakText() │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  useVoice.ts       │
│  speak(text)       │
└─────────┬──────────┘
          │
          │ HTTP POST
          ▼
┌────────────────────────────────────┐
│  Backend: /api/v1/voice/tts        │
│                                    │
│  1. Validate request (Pydantic)    │
│  2. Prepare payload                │
│  3. Call GPT-SoVITS API            │
│  4. Save audio to cache            │
│  5. Return audio URL               │
└─────────┬──────────────────────────┘
          │
          │ HTTP POST to localhost:9880
          ▼
┌────────────────────────────────────┐
│  GPT-SoVITS: /tts                  │
│                                    │
│  1. Load models (if not loaded)    │
│  2. Tokenize text                  │
│  3. Generate mel-spectrogram       │
│  4. Vocoder synthesis              │
│  5. Return WAV audio               │
└─────────┬──────────────────────────┘
          │
          │ Audio file (WAV)
          ▼
┌────────────────────────────────────┐
│  Backend saves to:                 │
│  audio_cache/tts_{timestamp}.wav   │
└─────────┬──────────────────────────┘
          │
          │ Return URL
          ▼
┌────────────────────────────────────┐
│  Frontend receives:                │
│  {                                 │
│    "audio_url": "/api/.../audio/..." │
│    "duration": 5.2                 │
│  }                                 │
└─────────┬──────────────────────────┘
          │
          ▼
┌────────────────────────────────────┐
│  useVoice creates Audio element    │
│  audio.src = audio_url             │
│  audio.play()                      │
└────────────────────────────────────┘
```

### 2. Speech-to-Text (STT) Flow

```
User clicks microphone button
         │
         ▼
┌────────────────────┐
│  ChatInput.tsx     │
│  startRecording()  │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  useVoice.ts       │
│  startListening()  │
└─────────┬──────────┘
          │
          │ MediaRecorder API
          ▼
┌────────────────────────────────────┐
│  Browser captures audio            │
│  • navigator.mediaDevices          │
│  • getUserMedia()                  │
│  • MediaRecorder                   │
└─────────┬──────────────────────────┘
          │
          │ User stops recording
          ▼
┌────────────────────────────────────┐
│  useVoice.ts                       │
│  stopListening()                   │
│  • Collect audio chunks            │
│  • Create Blob                     │
│  • Convert to FormData             │
└─────────┬──────────────────────────┘
          │
          │ HTTP POST (multipart/form-data)
          ▼
┌────────────────────────────────────┐
│  Backend: /api/v1/voice/stt        │
│                                    │
│  1. Receive audio file             │
│  2. Save to temp location          │
│  3. Detect language                │
│  4. Choose engine (Vosk/Whisper)   │
│  5. Transcribe audio               │
│  6. Return text + confidence       │
└─────────┬──────────────────────────┘
          │
          │ Vosk (fast, offline)
          │ OR
          │ Whisper (accurate, online)
          ▼
┌────────────────────────────────────┐
│  STT Engine processes audio        │
│  • Load model                      │
│  • Extract features                │
│  • Decode speech                   │
│  • Return transcript               │
└─────────┬──────────────────────────┘
          │
          │ Return JSON
          ▼
┌────────────────────────────────────┐
│  Frontend receives:                │
│  {                                 │
│    "text": "Привет, как дела?",   │
│    "confidence": 0.95,             │
│    "language": "ru"                │
│  }                                 │
└─────────┬──────────────────────────┘
          │
          ▼
┌────────────────────────────────────┐
│  useVoice calls onTranscript()     │
│  → BubbleChat.sendMessage(text)    │
└────────────────────────────────────┘
```

### 3. Voice Cloning Flow

```
User uploads reference audio
         │
         ▼
┌────────────────────────────────────┐
│  Voice Management UI (future)      │
│  • Upload audio file               │
│  • Provide transcript              │
│  • Set voice name                  │
└─────────┬──────────────────────────┘
          │
          │ HTTP POST
          ▼
┌────────────────────────────────────┐
│  Backend: /api/v1/voice/clone      │
│                                    │
│  1. Validate audio (3-10 sec)      │
│  2. Save reference audio           │
│  3. Extract voice features         │
│  4. Fine-tune model (optional)     │
│  5. Save voice profile             │
└─────────┬──────────────────────────┘
          │
          │ Call training script
          ▼
┌────────────────────────────────────┐
│  training/voice_clone.py           │
│                                    │
│  • VoiceCloner class               │
│  • prepare_audio()                 │
│  • extract_transcript()            │
│  • fine_tune() or quick_clone()    │
└─────────┬──────────────────────────┘
          │
          │ Save to database
          ▼
┌────────────────────────────────────┐
│  Voice Library                     │
│  • voice_id                        │
│  • name                            │
│  • reference_audio_path            │
│  • model_weights_path              │
│  • created_at                      │
└────────────────────────────────────┘
```

---

## 📡 API Reference

### Backend API Endpoints

#### 1. POST `/api/v1/voice/tts`

**Описание:** Синтез речи из текста

**Request:**
```json
{
  "text": "Привет! Как дела?",
  "language": "ru",
  "speed": 1.0,
  "voice_id": null
}
```

**Response:**
```json
{
  "audio_url": "/api/v1/voice/audio/tts_1234567890.wav",
  "duration": 2.5,
  "sample_rate": 32000
}
```

**Параметры:**
- `text` (string, required) - текст для озвучки (макс 1000 символов)
- `language` (string, optional) - язык ("ru", "en", "zh", "ja"), default: "ru"
- `speed` (float, optional) - скорость речи (0.5-2.0), default: 1.0
- `voice_id` (string, optional) - ID кастомного голоса

**Errors:**
- `400` - Invalid request (text too long, invalid language)
- `500` - TTS generation failed
- `503` - GPT-SoVITS server unavailable

---

#### 2. POST `/api/v1/voice/stt`

**Описание:** Распознавание речи из аудио

**Request:** `multipart/form-data`
```
audio: <audio file> (WAV, MP3, OGG)
language: "ru" (optional)
engine: "vosk" (optional, "vosk" or "whisper")
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

**Параметры:**
- `audio` (file, required) - аудио файл (макс 10MB)
- `language` (string, optional) - язык для распознавания
- `engine` (string, optional) - движок ("vosk" или "whisper")

**Errors:**
- `400` - Invalid audio file
- `413` - File too large (>10MB)
- `500` - STT processing failed

---

#### 3. POST `/api/v1/voice/clone`

**Описание:** Клонирование голоса

**Request:** `multipart/form-data`
```
audio: <reference audio> (WAV, MP3)
transcript: "Текст из аудио"
voice_name: "Мой голос"
mode: "quick" (optional, "quick" or "fine-tune")
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

**Параметры:**
- `audio` (file, required) - референсное аудио (3-10 сек)
- `transcript` (string, required) - текст из аудио
- `voice_name` (string, required) - название голоса
- `mode` (string, optional) - режим ("quick" или "fine-tune")

**Errors:**
- `400` - Invalid audio duration or transcript
- `500` - Voice cloning failed

---

#### 4. GET `/api/v1/voice/audio/{filename}`

**Описание:** Скачать аудио файл

**Response:** Audio file (WAV)

**Errors:**
- `404` - File not found

---

#### 5. DELETE `/api/v1/voice/audio/{filename}`

**Описание:** Удалить аудио файл

**Response:**
```json
{
  "success": true,
  "message": "Audio file deleted"
}
```

---

### Frontend Hook API

#### `useVoice(options)`

**Параметры:**
```typescript
interface UseVoiceProps {
  serverUrl: string;        // Backend URL
  apiKey: string;           // API ключ
  onTranscript?: (text: string) => void;  // Callback для STT
}
```

**Возвращает:**
```typescript
{
  speak: (text: string) => Promise<void>;
  stopSpeaking: () => void;
  startListening: () => Promise<void>;
  stopListening: () => void;
  toggleListening: () => void;
  isSpeaking: boolean;
  isListening: boolean;
  isProcessing: boolean;
}
```

**Пример использования:**
```typescript
const voice = useVoice({
  serverUrl: 'http://localhost:8000',
  apiKey: 'your-api-key',
  onTranscript: (text) => {
    console.log('Recognized:', text);
    sendMessage(text);
  }
});

// TTS
await voice.speak('Привет, мир!');

// STT
await voice.startListening();
// ... user speaks ...
voice.stopListening();
```

---

## ⚙️ Конфигурация

### 1. GPT-SoVITS Config

**Файл:** `config/gpt_sovits_config.yaml`

```yaml
server:
  host: "0.0.0.0"
  port: 9880
  gpu_id: 6

models:
  gpt_model: "GPT_SoVITS/pretrained_models/s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt"
  sovits_model: "GPT_SoVITS/pretrained_models/s2G488k.pth"
  bert_model: "GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large"

generation:
  default_language: "ru"
  supported_languages: ["ru", "en", "zh", "ja"]
  default_speed: 1.0
  default_temperature: 0.6
  top_k: 20
  top_p: 0.6

voice_cloning:
  mode: "zero-shot"  # "zero-shot" or "fine-tune"
  min_audio_duration: 3
  recommended_duration: 10
  max_audio_duration: 30

cache:
  audio_cache_dir: "audio_cache"
  max_cache_size_mb: 1000
  cleanup_interval_hours: 24
```

### 2. Backend Voice Router Config

**Файл:** `web/backend/routers/voice.py`

```python
# Константы
MAX_TEXT_LENGTH = 1000
MAX_AUDIO_SIZE_MB = 10
SUPPORTED_AUDIO_FORMATS = [".wav", ".mp3", ".ogg", ".flac"]
AUDIO_CACHE_DIR = Path("audio_cache")
TTS_CACHE_DIR = AUDIO_CACHE_DIR / "tts"
STT_CACHE_DIR = AUDIO_CACHE_DIR / "stt"
REF_CACHE_DIR = AUDIO_CACHE_DIR / "references"

# GPT-SoVITS URL
GPT_SOVITS_URL = "http://localhost:9880"
```

### 3. Frontend useVoice Config

**Файл:** `web/frontend/hooks/useVoice.ts`

```typescript
// Константы
const AUDIO_MIME_TYPE = 'audio/webm';
const SAMPLE_RATE = 16000;
const CHANNELS = 1;
```

---

## 🚀 Производительность

### Метрики TTS:

| Параметр | Значение |
|----------|----------|
| **Latency** | ~500ms (первый токен) |
| **Throughput** | ~15 символов/сек |
| **GPU Memory** | ~8GB (модели) + ~2GB (генерация) |
| **Audio Quality** | 32kHz, 16-bit WAV |
| **Real-time Factor** | ~0.3x (быстрее реального времени) |

### Метрики STT:

| Engine | Latency | Accuracy | Offline |
|--------|---------|----------|---------|
| **Vosk** | ~100ms | 85-90% | ✅ Yes |
| **Whisper** | ~2-5s | 95-98% | ❌ No |

### Оптимизация:

```python
# 1. Кэширование аудио
# Повторные запросы с одинаковым текстом возвращаются из кэша

# 2. Batch processing
# Несколько TTS запросов обрабатываются батчами

# 3. Async I/O
# Все операции асинхронные (FastAPI + httpx)

# 4. GPU Pinning
# GPT-SoVITS закреплен на GPU 6
os.environ['CUDA_VISIBLE_DEVICES'] = '6'
```

### Мониторинг:

```bash
# GPU использование
nvidia-smi -l 1

# Логи GPT-SoVITS
tail -f logs/gpt_sovits.log

# Метрики FastAPI
curl http://localhost:8000/api/v1/system/stats
```

---

## 🔗 Связанные файлы

### Backend:
- [`web/backend/routers/voice.py`](../web/backend/routers/voice.py) - Voice API router
- [`web/backend/models/voice_models.py`](../web/backend/models/voice_models.py) - Pydantic models
- [`core/multimodal/tts.py`](../core/multimodal/tts.py) - TTS manager class

### Frontend:
- [`web/frontend/hooks/useVoice.ts`](../web/frontend/hooks/useVoice.ts) - Voice hook
- [`web/frontend/components/MessageBubble.tsx`](../web/frontend/components/MessageBubble.tsx) - TTS button
- [`web/frontend/components/ChatInput.tsx`](../web/frontend/components/ChatInput.tsx) - STT button

### Training:
- [`training/voice_clone.py`](../training/voice_clone.py) - Voice cloning script

### Config:
- [`config/gpt_sovits_config.yaml`](../config/gpt_sovits_config.yaml) - GPT-SoVITS config
- [`setup_gpt_sovits.py`](../setup_gpt_sovits.py) - Installation script

---

## 📚 Дополнительные ресурсы

- [GPT-SoVITS GitHub](https://github.com/RVC-Boss/GPT-SoVITS)
- [Whisper Documentation](https://github.com/openai/whisper)
- [Vosk Documentation](https://alphacephei.com/vosk/)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)

---

*Документация обновлена: 2026-05-09*
