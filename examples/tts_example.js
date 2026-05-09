/**
 * Примеры использования Voice API на JavaScript/TypeScript
 * 
 * Этот файл содержит практические примеры работы с Voice API
 * из браузера или Node.js приложения.
 */

// Конфигурация
const API_URL = 'http://localhost:8000';
const API_KEY = 'your-secret-key-here';

// Базовый класс для работы с Voice API
class VoiceAPIClient {
  constructor(apiUrl = API_URL, apiKey = API_KEY) {
    this.apiUrl = apiUrl;
    this.apiKey = apiKey;
  }

  async request(endpoint, options = {}) {
    const url = `${this.apiUrl}${endpoint}`;
    const headers = {
      'X-API-Key': this.apiKey,
      ...options.headers
    };

    const response = await fetch(url, {
      ...options,
      headers
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }
}

// ============================================
// Пример 1: Простой синтез речи
// ============================================
async function example1_simpleTTS() {
  console.log('=== Пример 1: Простой TTS ===\n');

  const client = new VoiceAPIClient();

  try {
    const result = await client.request('/api/v1/voice/tts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: 'Привет! Это пример синтеза речи.',
        language: 'ru',
        speed: 1.0
      })
    });

    console.log('✅ Аудио создано:', result.audio_url);
    console.log('   Длительность:', result.duration.toFixed(2), 'сек');

    // Воспроизведение в браузере
    if (typeof Audio !== 'undefined') {
      const audio = new Audio(`${API_URL}${result.audio_url}`);
      await audio.play();
    }

    return result;
  } catch (error) {
    console.error('❌ Ошибка:', error.message);
  }
}

// ============================================
// Пример 2: Создание голоса
// ============================================
async function example2_createVoice(audioFile, name, referenceText) {
  console.log('\n=== Пример 2: Создание голоса ===\n');

  const formData = new FormData();
  formData.append('audio', audioFile);
  formData.append('name', name);
  formData.append('reference_text', referenceText);
  formData.append('description', 'Голос созданный из примера');
  formData.append('language', 'ru');

  try {
    const response = await fetch(`${API_URL}/api/v1/voice/voices`, {
      method: 'POST',
      headers: { 'X-API-Key': API_KEY },
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const voice = await response.json();
    console.log('✅ Голос создан!');
    console.log('   ID:', voice.id);
    console.log('   Название:', voice.name);
    console.log('   Язык:', voice.language);

    return voice;
  } catch (error) {
    console.error('❌ Ошибка:', error.message);
  }
}

// ============================================
// Пример 3: Получение списка голосов
// ============================================
async function example3_listVoices() {
  console.log('\n=== Пример 3: Список голосов ===\n');

  const client = new VoiceAPIClient();

  try {
    const data = await client.request('/api/v1/voice/voices');

    console.log(`📚 Всего голосов: ${data.total}\n`);

    data.voices.forEach(voice => {
      const status = voice.is_trained ? '✅ Обучен' : '⏳ Не обучен';
      console.log(`🎤 ${voice.name}`);
      console.log(`   ID: ${voice.id}`);
      console.log(`   Язык: ${voice.language}`);
      console.log(`   Статус: ${status}`);
      console.log(`   Сэмплов: ${voice.sample_count}\n`);
    });

    return data.voices;
  } catch (error) {
    console.error('❌ Ошибка:', error.message);
  }
}

// ============================================
// Пример 4: Добавление обучающего сэмпла
// ============================================
async function example4_addTrainingSample(voiceId, audioFile, text) {
  console.log('\n=== Пример 4: Добавление сэмпла ===\n');

  const formData = new FormData();
  formData.append('audio', audioFile);
  formData.append('text', text);

  try {
    const response = await fetch(
      `${API_URL}/api/v1/voice/voices/${voiceId}/samples`,
      {
        method: 'POST',
        headers: { 'X-API-Key': API_KEY },
        body: formData
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const sample = await response.json();
    console.log('✅ Сэмпл добавлен:', sample.id);
    console.log('   Текст:', text);
    console.log('   Длительность:', sample.duration.toFixed(2), 'сек');

    return sample;
  } catch (error) {
    console.error('❌ Ошибка:', error.message);
  }
}

// ============================================
// Пример 5: Обучение голоса с мониторингом
// ============================================
async function example5_trainVoice(voiceId, options = {}) {
  console.log('\n=== Пример 5: Обучение голоса ===\n');

  const client = new VoiceAPIClient();

  const trainingParams = {
    voice_id: voiceId,
    epochs: options.epochs || 100,
    batch_size: options.batchSize || 4,
    learning_rate: options.learningRate || 0.0001,
    save_interval: options.saveInterval || 10
  };

  try {
    // Запуск обучения
    const status = await client.request(`/api/v1/voice/voices/${voiceId}/train`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(trainingParams)
    });

    console.log('✅ Обучение запущено!');
    console.log('   Статус:', status.status);
    console.log('   Эпох:', status.total_epochs);
    console.log();

    // Мониторинг прогресса
    console.log('📊 Мониторинг прогресса...\n');

    return new Promise((resolve, reject) => {
      const checkProgress = async () => {
        try {
          const currentStatus = await client.request(
            `/api/v1/voice/voices/${voiceId}/training-status`
          );

          if (currentStatus.status === 'completed') {
            console.log('✅ Обучение завершено!');
            resolve(currentStatus);
            return;
          }

          if (currentStatus.status === 'failed') {
            console.error('❌ Обучение провалилось:', currentStatus.error);
            reject(new Error(currentStatus.error));
            return;
          }

          // Вывод прогресса
          const progress = currentStatus.progress.toFixed(1);
          const epoch = currentStatus.current_epoch;
          const total = currentStatus.total_epochs;
          const eta = Math.floor((currentStatus.eta_seconds || 0) / 60);

          console.log(`⏳ Прогресс: ${progress}% | Эпоха: ${epoch}/${total} | ETA: ${eta} мин`);

          // Проверяем снова через 5 секунд
          setTimeout(checkProgress, 5000);
        } catch (error) {
          reject(error);
        }
      };

      checkProgress();
    });
  } catch (error) {
    console.error('❌ Ошибка:', error.message);
    throw error;
  }
}

// ============================================
// Пример 6: Тестирование голоса
// ============================================
async function example6_testVoice(voiceId, testText) {
  console.log('\n=== Пример 6: Тестирование голоса ===\n');

  const client = new VoiceAPIClient();

  try {
    const result = await client.request(`/api/v1/voice/voices/${voiceId}/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        voice_id: voiceId,
        test_text: testText,
        language: 'ru'
      })
    });

    console.log('✅ Тестовое аудио создано:', result.audio_url);
    console.log('   Текст:', testText);
    console.log('   Длительность:', result.duration.toFixed(2), 'сек');

    // Воспроизведение в браузере
    if (typeof Audio !== 'undefined') {
      const audio = new Audio(`${API_URL}${result.audio_url}`);
      await audio.play();
    }

    return result;
  } catch (error) {
    console.error('❌ Ошибка:', error.message);
  }
}

// ============================================
// Пример 7: Speech-to-Text
// ============================================
async function example7_speechToText(audioFile, language = 'ru') {
  console.log('\n=== Пример 7: Speech-to-Text ===\n');

  const formData = new FormData();
  formData.append('audio', audioFile);
  formData.append('language', language);

  try {
    const response = await fetch(`${API_URL}/api/v1/voice/stt`, {
      method: 'POST',
      headers: { 'X-API-Key': API_KEY },
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const result = await response.json();
    console.log('✅ Распознано:');
    console.log('   Текст:', result.text);
    console.log('   Уверенность:', (result.confidence * 100).toFixed(1) + '%');
    console.log('   Язык:', result.language);

    return result;
  } catch (error) {
    console.error('❌ Ошибка:', error.message);
  }
}

// ============================================
// Пример 8: React Hook для TTS
// ============================================
/**
 * Пример React Hook для использования в компонентах
 * 
 * Usage:
 * ```tsx
 * const { speak, isPlaying, error } = useTTS();
 * 
 * <button onClick={() => speak('Привет!')}>
 *   {isPlaying ? 'Играет...' : 'Озвучить'}
 * </button>
 * ```
 */
function useTTS(apiUrl = API_URL, apiKey = API_KEY) {
  const [isPlaying, setIsPlaying] = React.useState(false);
  const [error, setError] = React.useState(null);
  const audioRef = React.useRef(null);

  const speak = React.useCallback(async (text, options = {}) => {
    setError(null);
    setIsPlaying(true);

    try {
      const response = await fetch(`${apiUrl}/api/v1/voice/tts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey
        },
        body: JSON.stringify({
          text,
          language: options.language || 'ru',
          speed: options.speed || 1.0,
          voice_id: options.voiceId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = await response.json();

      // Создаем и воспроизводим аудио
      const audio = new Audio(`${apiUrl}${result.audio_url}`);
      audioRef.current = audio;

      audio.onended = () => setIsPlaying(false);
      audio.onerror = () => {
        setError('Ошибка воспроизведения');
        setIsPlaying(false);
      };

      await audio.play();
    } catch (err) {
      setError(err.message);
      setIsPlaying(false);
    }
  }, [apiUrl, apiKey]);

  const stop = React.useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
      setIsPlaying(false);
    }
  }, []);

  return { speak, stop, isPlaying, error };
}

// ============================================
// Пример 9: Пакетная обработка
// ============================================
async function example9_batchProcessing(texts) {
  console.log('\n=== Пример 9: Пакетная обработка ===\n');

  const client = new VoiceAPIClient();

  try {
    const promises = texts.map(text =>
      client.request('/api/v1/voice/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, language: 'ru', speed: 1.0 })
      })
    );

    const results = await Promise.allSettled(promises);

    let successCount = 0;
    results.forEach((result, index) => {
      if (result.status === 'fulfilled') {
        console.log(`✅ Аудио ${index + 1}:`, result.value.audio_url);
        successCount++;
      } else {
        console.error(`❌ Ошибка ${index + 1}:`, result.reason.message);
      }
    });

    console.log(`\n📊 Успешно: ${successCount}/${texts.length}`);

    return results;
  } catch (error) {
    console.error('❌ Ошибка:', error.message);
  }
}

// ============================================
// Экспорт для использования в модулях
// ============================================
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    VoiceAPIClient,
    example1_simpleTTS,
    example2_createVoice,
    example3_listVoices,
    example4_addTrainingSample,
    example5_trainVoice,
    example6_testVoice,
    example7_speechToText,
    useTTS,
    example9_batchProcessing
  };
}

// ============================================
// Запуск примеров (если файл запущен напрямую)
// ============================================
if (typeof window !== 'undefined') {
  console.log('🎤 Примеры Voice API доступны в консоли');
  console.log('Используйте: example1_simpleTTS(), example3_listVoices() и т.д.');
}
