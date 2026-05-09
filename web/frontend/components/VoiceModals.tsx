/**
 * Модальные окна для Voice Management
 */
import React, { useState, useRef } from 'react';
import { X, Upload, Loader, AlertCircle } from 'lucide-react';

interface CreateVoiceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: {
    name: string;
    description: string;
    language: string;
    referenceText: string;
    audioFile: File;
  }) => Promise<void>;
}

export function CreateVoiceModal({ isOpen, onClose, onSubmit }: CreateVoiceModalProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [language, setLanguage] = useState('ru');
  const [referenceText, setReferenceText] = useState('');
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!name || !referenceText || !audioFile) {
      setError('Заполните все обязательные поля');
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit({
        name,
        description,
        language,
        referenceText,
        audioFile
      });
      onClose();
      // Reset form
      setName('');
      setDescription('');
      setLanguage('ru');
      setReferenceText('');
      setAudioFile(null);
    } catch (err: any) {
      setError(err.message || 'Ошибка создания голоса');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.type.startsWith('audio/')) {
        setError('Выберите аудио файл');
        return;
      }
      setAudioFile(file);
      setError('');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-bg-secondary border border-white/10 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto m-4">
        <div className="sticky top-0 bg-bg-secondary border-b border-white/10 p-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold">Создать новый голос</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-red-400">{error}</p>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-2">
              Название голоса <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-bg-primary border border-border-subtle rounded-lg px-4 py-3 text-text-primary focus:outline-none focus:border-accent-primary transition-colors"
              placeholder="Например: Мой голос"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Описание
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-bg-primary border border-border-subtle rounded-lg px-4 py-3 text-text-primary focus:outline-none focus:border-accent-primary transition-colors resize-none"
              rows={3}
              placeholder="Краткое описание голоса..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Язык
            </label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full bg-bg-primary border border-border-subtle rounded-lg px-4 py-3 text-text-primary focus:outline-none focus:border-accent-primary transition-colors"
            >
              <option value="ru">Русский</option>
              <option value="en">English</option>
              <option value="zh">中文</option>
              <option value="ja">日本語</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Референсное аудио <span className="text-red-400">*</span>
            </label>
            <div
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-border-subtle rounded-lg p-8 text-center cursor-pointer hover:border-accent-primary transition-colors"
            >
              <Upload className="w-8 h-8 mx-auto mb-3 text-text-secondary" />
              {audioFile ? (
                <div>
                  <p className="text-text-primary font-medium">{audioFile.name}</p>
                  <p className="text-sm text-text-secondary mt-1">
                    {(audioFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              ) : (
                <div>
                  <p className="text-text-primary mb-1">Загрузите аудио файл</p>
                  <p className="text-sm text-text-secondary">
                    WAV, MP3 или другой аудио формат
                  </p>
                </div>
              )}
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept="audio/*"
              onChange={handleFileChange}
              className="hidden"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Текст референсного аудио <span className="text-red-400">*</span>
            </label>
            <textarea
              value={referenceText}
              onChange={(e) => setReferenceText(e.target.value)}
              className="w-full bg-bg-primary border border-border-subtle rounded-lg px-4 py-3 text-text-primary focus:outline-none focus:border-accent-primary transition-colors resize-none"
              rows={4}
              placeholder="Введите текст, который произносится в аудио..."
              required
            />
            <p className="text-sm text-text-secondary mt-2">
              Точная транскрипция аудио для лучшего качества клонирования
            </p>
          </div>

          <div className="flex items-center gap-3 pt-4">
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 px-6 py-3 bg-accent-primary hover:bg-accent-secondary disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors font-medium flex items-center justify-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Создание...
                </>
              ) : (
                'Создать голос'
              )}
            </button>
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-6 py-3 bg-white/5 hover:bg-white/10 disabled:opacity-50 text-text-primary rounded-lg transition-colors font-medium"
            >
              Отмена
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

interface TrainVoiceModalProps {
  isOpen: boolean;
  onClose: () => void;
  voiceName: string;
  sampleCount: number;
  onSubmit: (data: {
    epochs: number;
    batchSize: number;
    learningRate: number;
  }) => Promise<void>;
}

export function TrainVoiceModal({ 
  isOpen, 
  onClose, 
  voiceName, 
  sampleCount,
  onSubmit 
}: TrainVoiceModalProps) {
  const [epochs, setEpochs] = useState(100);
  const [batchSize, setBatchSize] = useState(4);
  const [learningRate, setLearningRate] = useState(0.0001);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const estimatedTime = Math.ceil((epochs * sampleCount) / (batchSize * 60)); // примерная оценка в минутах

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (sampleCount < 5) {
      setError('Недостаточно обучающих сэмплов (минимум 5)');
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit({
        epochs,
        batchSize,
        learningRate
      });
      onClose();
    } catch (err: any) {
      setError(err.message || 'Ошибка запуска обучения');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-bg-secondary border border-white/10 rounded-2xl shadow-2xl w-full max-w-xl m-4">
        <div className="bg-bg-secondary border-b border-white/10 p-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold">Обучить голос</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-red-400">{error}</p>
            </div>
          )}

          <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
            <p className="text-blue-400 font-medium mb-2">Голос: {voiceName}</p>
            <p className="text-sm text-text-secondary">
              Обучающих сэмплов: {sampleCount}
            </p>
            <p className="text-sm text-text-secondary">
              Примерное время: ~{estimatedTime} мин
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Количество эпох: {epochs}
            </label>
            <input
              type="range"
              min="10"
              max="500"
              step="10"
              value={epochs}
              onChange={(e) => setEpochs(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-text-secondary mt-1">
              <span>10</span>
              <span>500</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Размер батча: {batchSize}
            </label>
            <input
              type="range"
              min="1"
              max="16"
              step="1"
              value={batchSize}
              onChange={(e) => setBatchSize(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-text-secondary mt-1">
              <span>1</span>
              <span>16</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Learning Rate: {learningRate.toExponential(2)}
            </label>
            <input
              type="range"
              min="-6"
              max="-2"
              step="0.1"
              value={Math.log10(learningRate)}
              onChange={(e) => setLearningRate(Math.pow(10, parseFloat(e.target.value)))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-text-secondary mt-1">
              <span>1e-6</span>
              <span>1e-2</span>
            </div>
          </div>

          <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
            <p className="text-sm text-yellow-400">
              ⚠️ Обучение займет некоторое время. Не закрывайте страницу во время обучения.
            </p>
          </div>

          <div className="flex items-center gap-3 pt-4">
            <button
              type="submit"
              disabled={isSubmitting || sampleCount < 5}
              className="flex-1 px-6 py-3 bg-accent-primary hover:bg-accent-secondary disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors font-medium flex items-center justify-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Запуск...
                </>
              ) : (
                'Начать обучение'
              )}
            </button>
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-6 py-3 bg-white/5 hover:bg-white/10 disabled:opacity-50 text-text-primary rounded-lg transition-colors font-medium"
            >
              Отмена
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
