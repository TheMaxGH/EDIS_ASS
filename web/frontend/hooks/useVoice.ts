/**
 * Хук для работы с голосовыми функциями (TTS/STT)
 */
import { useState, useRef, useCallback } from 'react';

interface UseVoiceProps {
  serverUrl: string;
  apiKey: string;
  onTranscript?: (text: string) => void;
}

export function useVoice({ serverUrl, apiKey, onTranscript }: UseVoiceProps) {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Синтез речи (TTS)
  const speak = useCallback(async (text: string) => {
    if (!text.trim()) return;
    
    setIsSpeaking(true);
    setError(null);

    try {
      const response = await fetch(`${serverUrl}/api/v1/voice/tts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey,
        },
        body: JSON.stringify({
          text,
          language: 'ru',
          speed: 1.0,
        }),
      });

      if (!response.ok) {
        throw new Error('Ошибка синтеза речи');
      }

      const data = await response.json();
      
      // Воспроизведение аудио
      const audioUrl = `${serverUrl}${data.audio_url}`;
      const audio = new Audio(audioUrl);
      audioRef.current = audio;
      
      audio.onended = () => {
        setIsSpeaking(false);
      };
      
      audio.onerror = () => {
        setError('Ошибка воспроизведения аудио');
        setIsSpeaking(false);
      };
      
      await audio.play();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка TTS');
      setIsSpeaking(false);
    }
  }, [serverUrl, apiKey]);

  // Остановка воспроизведения
  const stopSpeaking = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsSpeaking(false);
    }
  }, []);

  // Начало записи (STT)
  const startListening = useCallback(async () => {
    setError(null);
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        
        // Отправка на распознавание
        try {
          const formData = new FormData();
          formData.append('audio', audioBlob, 'recording.wav');
          formData.append('language', 'ru');

          const response = await fetch(`${serverUrl}/api/v1/voice/stt`, {
            method: 'POST',
            headers: {
              'X-API-Key': apiKey,
            },
            body: formData,
          });

          if (!response.ok) {
            throw new Error('Ошибка распознавания речи');
          }

          const data = await response.json();
          
          if (onTranscript && data.text) {
            onTranscript(data.text);
          }
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Ошибка STT');
        }
        
        // Остановка потока
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsListening(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка доступа к микрофону');
    }
  }, [serverUrl, apiKey, onTranscript]);

  // Остановка записи
  const stopListening = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      setIsListening(false);
    }
  }, []);

  // Переключение записи
  const toggleListening = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, startListening, stopListening]);

  return {
    isListening,
    isSpeaking,
    error,
    speak,
    stopSpeaking,
    startListening,
    stopListening,
    toggleListening,
  };
}
