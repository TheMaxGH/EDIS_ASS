import React, { useState, useRef, KeyboardEvent, ChangeEvent, useEffect } from 'react';

interface ChatInputProps {
  onSend: (message: string, attachments?: File[]) => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function ChatInput({ 
  onSend, 
  disabled = false,
  placeholder = 'Напишите сообщение...'
}: ChatInputProps) {
  const [message, setMessage] = useState('');
  const [attachments, setAttachments] = useState<File[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Cleanup recording interval on unmount
  useEffect(() => {
    return () => {
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }
    };
  }, []);

  const adjustHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    }
  };

  const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    adjustHeight();
  };

  const handleSend = () => {
    if (message.trim() || attachments.length > 0) {
      onSend(message.trim(), attachments);
      setMessage('');
      setAttachments([]);
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setAttachments(prev => [...prev, ...files]);
    // Reset input для возможности повторного выбора того же файла
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const getFileIcon = (file: File): string => {
    const type = file.type;
    if (type.startsWith('image/')) return '🖼️';
    if (type.startsWith('video/')) return '🎥';
    if (type.startsWith('audio/')) return '🎵';
    if (type.includes('pdf')) return '📄';
    if (type.includes('zip') || type.includes('rar')) return '📦';
    if (type.includes('text')) return '📝';
    return '📎';
  };

  const formatRecordingTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const startRecording = async () => {
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
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        
        // Отправляем аудио на Backend для STT
        try {
          const formData = new FormData();
          formData.append('audio', audioBlob, 'recording.webm');

          const response = await fetch('/api/v1/voice/stt', {
            method: 'POST',
            body: formData,
          });

          if (response.ok) {
            const data = await response.json();
            setMessage(prev => prev + (prev ? ' ' : '') + data.text);
            adjustHeight();
          } else {
            console.error('STT failed:', await response.text());
          }
        } catch (error) {
          console.error('Error sending audio:', error);
        }

        // Cleanup
        stream.getTracks().forEach(track => track.stop());
        setRecordingTime(0);
      };

      mediaRecorder.start();
      setIsRecording(true);

      // Start timer
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Не удалось получить доступ к микрофону. Проверьте разрешения.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
        recordingIntervalRef.current = null;
      }
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <div className="w-full">
      {/* Attachments Preview */}
      {attachments.length > 0 && (
        <div className="mb-3 flex flex-wrap gap-2">
          {attachments.map((file, index) => (
            <div
              key={index}
              className="flex items-center gap-2 bg-message-user/50 backdrop-blur-sm border border-border-subtle rounded-lg px-3 py-2 group hover:bg-message-user/70 transition-colors"
            >
              <span className="text-lg">{getFileIcon(file)}</span>
              <div className="flex flex-col min-w-0">
                <span className="text-text-primary text-sm font-medium truncate max-w-[200px]">
                  {file.name}
                </span>
                <span className="text-text-secondary text-xs">
                  {formatFileSize(file.size)}
                </span>
              </div>
              <button
                onClick={() => removeAttachment(index)}
                className="ml-2 p-1 rounded hover:bg-red-500/20 text-text-secondary hover:text-red-400 transition-colors"
                title="Удалить"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Recording Indicator */}
      {isRecording && (
        <div className="mb-3 flex items-center gap-3 bg-red-500/20 backdrop-blur-sm border border-red-500/50 rounded-lg px-4 py-3 animate-pulse-soft">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-red-400 font-medium">Запись...</span>
          </div>
          <span className="text-text-primary font-mono text-sm">
            {formatRecordingTime(recordingTime)}
          </span>
        </div>
      )}

      {/* Input Container */}
      <div className="relative flex items-end gap-2 bg-message-user/30 backdrop-blur-md border border-border-subtle rounded-2xl p-3 focus-within:border-accent-primary/50 transition-colors">
        {/* Attach Button */}
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled || isRecording}
          className="flex-shrink-0 p-2 rounded-lg hover:bg-message-user/50 text-text-secondary hover:text-accent-primary transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          title="Прикрепить файл"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
          </svg>
        </button>

        {/* Voice Button */}
        <button
          onClick={toggleRecording}
          disabled={disabled}
          className={`flex-shrink-0 p-2 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed ${
            isRecording 
              ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30' 
              : 'hover:bg-message-user/50 text-text-secondary hover:text-accent-primary'
          }`}
          title={isRecording ? 'Остановить запись' : 'Голосовой ввод'}
        >
          {isRecording ? (
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <rect x="6" y="6" width="12" height="12" rx="2" />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          )}
        </button>

        {/* Hidden File Input */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          className="hidden"
          onChange={handleFileSelect}
          disabled={disabled}
        />

        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={message}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          disabled={disabled || isRecording}
          placeholder={isRecording ? 'Идёт запись...' : placeholder}
          rows={1}
          className="flex-1 bg-transparent text-text-primary placeholder-text-secondary resize-none outline-none min-h-[24px] max-h-[200px] py-1 disabled:opacity-50 disabled:cursor-not-allowed"
          style={{ scrollbarWidth: 'thin' }}
        />

        {/* Send Button */}
        <button
          onClick={handleSend}
          disabled={disabled || isRecording || (!message.trim() && attachments.length === 0)}
          className="flex-shrink-0 p-2 rounded-lg bg-accent-primary hover:bg-accent-hover text-white transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-accent-primary"
          title="Отправить (Enter)"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>

      {/* Hint Text */}
      <div className="mt-2 flex items-center justify-between text-xs text-text-secondary px-1">
        <span>
          <kbd className="px-1.5 py-0.5 bg-message-user/30 border border-border-subtle rounded text-xs">Enter</kbd>
          {' '}для отправки, {' '}
          <kbd className="px-1.5 py-0.5 bg-message-user/30 border border-border-subtle rounded text-xs">Shift+Enter</kbd>
          {' '}для новой строки
        </span>
        {message.length > 0 && (
          <span className={message.length > 4000 ? 'text-red-400' : ''}>
            {message.length} / 4000
          </span>
        )}
      </div>
    </div>
  );
}
