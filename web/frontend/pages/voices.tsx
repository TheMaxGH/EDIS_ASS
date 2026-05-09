/**
 * Voice Management Page - управление библиотекой голосов
 */
import React, { useState, useEffect, useCallback } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import {
  Mic, Plus, Trash2, Edit2, Play, Pause, Upload,
  Download, Settings, CheckCircle, XCircle, Clock,
  Volume2, AlertCircle, Loader
} from 'lucide-react';
import SettingsPanel from '../components/SettingsPanel';
import EDISClient from '../lib/edis-client';
import { CreateVoiceModal, TrainVoiceModal } from '../components/VoiceModals';

interface Voice {
  id: string;
  name: string;
  description?: string;
  language: string;
  reference_audio: string;
  reference_text: string;
  created_at: string;
  is_trained: boolean;
  training_status?: string;
  sample_count: number;
}

interface TrainingSample {
  id: string;
  voice_id: string;
  audio_path: string;
  text: string;
  duration: number;
  created_at: string;
}

interface TrainingStatus {
  voice_id: string;
  status: string;
  progress: number;
  current_epoch: number;
  total_epochs: number;
  loss?: number;
  eta_seconds?: number;
  started_at?: string;
  completed_at?: string;
  error?: string;
}

export default function VoicesPage() {
  const [serverUrl, setServerUrl] = useState('http://localhost:8000');
  const [apiKey, setApiKey] = useState('your-secret-key-here');
  const [client, setClient] = useState<EDISClient | null>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  
  const [voices, setVoices] = useState<Voice[]>([]);
  const [selectedVoice, setSelectedVoice] = useState<Voice | null>(null);
  const [samples, setSamples] = useState<TrainingSample[]>([]);
  const [trainingStatus, setTrainingStatus] = useState<TrainingStatus | null>(null);
  
  const [isLoading, setIsLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showTrainModal, setShowTrainModal] = useState(false);
  const [showAddSampleModal, setShowAddSampleModal] = useState(false);
  const [testText, setTestText] = useState('Привет! Это тестовое сообщение.');
  const [isPlaying, setIsPlaying] = useState(false);
  const [uploadingSample, setUploadingSample] = useState(false);

  useEffect(() => {
    const savedUrl = localStorage.getItem('edis_server_url');
    const savedKey = localStorage.getItem('edis_api_key');
    if (savedUrl) setServerUrl(savedUrl);
    if (savedKey) setApiKey(savedKey);
    
    const edisClient = new EDISClient(savedUrl || serverUrl, savedKey || apiKey);
    setClient(edisClient);
  }, []);

  const handleSettingsChange = useCallback((newServerUrl: string, newApiKey: string) => {
    setServerUrl(newServerUrl);
    setApiKey(newApiKey);
    setClient(new EDISClient(newServerUrl, newApiKey));
  }, []);

  useEffect(() => {
    if (client) {
      loadVoices();
    }
  }, [client]);

  useEffect(() => {
    if (selectedVoice) {
      loadSamples(selectedVoice.id);
      loadTrainingStatus(selectedVoice.id);
    }
  }, [selectedVoice]);

  const loadVoices = async () => {
    if (!client) return;
    setIsLoading(true);
    try {
      const response = await fetch(`${serverUrl}/api/v1/voice/voices`, {
        headers: { 'X-API-Key': apiKey }
      });
      const data = await response.json();
      setVoices(data.voices || []);
    } catch (error) {
      console.error('Failed to load voices:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadSamples = async (voiceId: string) => {
    try {
      const response = await fetch(`${serverUrl}/api/v1/voice/voices/${voiceId}/samples`, {
        headers: { 'X-API-Key': apiKey }
      });
      const data = await response.json();
      setSamples(data.samples || []);
    } catch (error) {
      console.error('Failed to load samples:', error);
    }
  };

  const loadTrainingStatus = async (voiceId: string) => {
    try {
      const response = await fetch(`${serverUrl}/api/v1/voice/voices/${voiceId}/training-status`, {
        headers: { 'X-API-Key': apiKey }
      });
      const data = await response.json();
      setTrainingStatus(data);
    } catch (error) {
      console.error('Failed to load training status:', error);
    }
  };

  const handleDeleteVoice = async (voiceId: string) => {
    if (!confirm('Удалить этот голос?')) return;
    
    try {
      await fetch(`${serverUrl}/api/v1/voice/voices/${voiceId}`, {
        method: 'DELETE',
        headers: { 'X-API-Key': apiKey }
      });
      await loadVoices();
      if (selectedVoice?.id === voiceId) {
        setSelectedVoice(null);
      }
    } catch (error) {
      console.error('Failed to delete voice:', error);
    }
  };

  const handleTestVoice = async (voiceId: string) => {
    setIsPlaying(true);
    try {
      const response = await fetch(`${serverUrl}/api/v1/voice/voices/${voiceId}/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey
        },
        body: JSON.stringify({
          voice_id: voiceId,
          test_text: testText,
          language: 'ru'
        })
      });
      
      const data = await response.json();
      const audio = new Audio(`${serverUrl}${data.audio_url}`);
      audio.onended = () => setIsPlaying(false);
      audio.onerror = () => setIsPlaying(false);
      await audio.play();
    } catch (error) {
      console.error('Failed to test voice:', error);
      setIsPlaying(false);
    }
  };

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'training':
        return <Loader className="w-4 h-4 text-blue-400 animate-spin" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-400" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-400';
      case 'training':
        return 'text-blue-400';
      case 'failed':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  const handleCreateVoice = async (data: {
    name: string;
    description: string;
    language: string;
    referenceText: string;
    audioFile: File;
  }) => {
    const formData = new FormData();
    formData.append('name', data.name);
    formData.append('reference_text', data.referenceText);
    formData.append('audio', data.audioFile);
    if (data.description) formData.append('description', data.description);
    formData.append('language', data.language);

    const response = await fetch(`${serverUrl}/api/v1/voice/voices`, {
      method: 'POST',
      headers: { 'X-API-Key': apiKey },
      body: formData
    });

    if (!response.ok) {
      throw new Error('Failed to create voice');
    }

    await loadVoices();
  };

  const handleStartTraining = async (data: {
    epochs: number;
    batchSize: number;
    learningRate: number;
  }) => {
    if (!selectedVoice) return;

    const response = await fetch(`${serverUrl}/api/v1/voice/voices/${selectedVoice.id}/train`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': apiKey
      },
      body: JSON.stringify({
        voice_id: selectedVoice.id,
        epochs: data.epochs,
        batch_size: data.batchSize,
        learning_rate: data.learningRate,
        save_interval: 10
      })
    });

    if (!response.ok) {
      throw new Error('Failed to start training');
    }

    await loadTrainingStatus(selectedVoice.id);
  };

  const handleAddSample = async (audioFile: File, text: string) => {
    if (!selectedVoice) return;

    setUploadingSample(true);
    try {
      const formData = new FormData();
      formData.append('audio', audioFile);
      formData.append('text', text);

      const response = await fetch(`${serverUrl}/api/v1/voice/voices/${selectedVoice.id}/samples`, {
        method: 'POST',
        headers: { 'X-API-Key': apiKey },
        body: formData
      });

      if (!response.ok) {
        throw new Error('Failed to add sample');
      }

      await loadSamples(selectedVoice.id);
      await loadVoices(); // Обновить счетчик сэмплов
    } finally {
      setUploadingSample(false);
    }
  };

  const handleDeleteSample = async (sampleId: string) => {
    if (!selectedVoice || !confirm('Удалить этот сэмпл?')) return;

    try {
      await fetch(`${serverUrl}/api/v1/voice/voices/${selectedVoice.id}/samples/${sampleId}`, {
        method: 'DELETE',
        headers: { 'X-API-Key': apiKey }
      });

      await loadSamples(selectedVoice.id);
      await loadVoices();
    } catch (error) {
      console.error('Failed to delete sample:', error);
    }
  };

  return (
    <>
      <Head>
        <title>Управление голосами - EDIS</title>
      </Head>

      <CreateVoiceModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSubmit={handleCreateVoice}
      />

      {selectedVoice && (
        <TrainVoiceModal
          isOpen={showTrainModal}
          onClose={() => setShowTrainModal(false)}
          voiceName={selectedVoice.name}
          sampleCount={samples.length}
          onSubmit={handleStartTraining}
        />
      )}

      <SettingsPanel
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        edisClient={client!}
      />

      <nav className="sticky top-0 z-50 bg-bg-secondary/80 backdrop-blur-xl border-b border-white/5 shadow-elevated">
        <div className="max-w-[1920px] mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="flex items-center gap-3 group">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center group-hover:scale-110 transition-transform">
                <Mic className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-accent-primary to-accent-secondary bg-clip-text text-transparent">
                Voice Library
              </span>
            </Link>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-accent-primary hover:bg-accent-secondary text-white rounded-lg transition-colors flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Новый голос
            </button>
            <button
              onClick={() => setSettingsOpen(true)}
              className="p-2 hover:bg-white/5 rounded-lg transition-colors"
            >
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>
      </nav>

      <div className="flex h-[calc(100vh-4rem)]">
        {/* Список голосов */}
        <div className="w-80 border-r border-white/5 bg-bg-secondary/30 overflow-y-auto">
          <div className="p-4 space-y-2">
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader className="w-6 h-6 animate-spin text-accent-primary" />
              </div>
            ) : voices.length === 0 ? (
              <div className="text-center py-8 text-text-secondary">
                <Mic className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p>Нет голосов</p>
                <p className="text-sm mt-1">Создайте первый голос</p>
              </div>
            ) : (
              voices.map((voice) => (
                <button
                  key={voice.id}
                  onClick={() => setSelectedVoice(voice)}
                  className={`w-full p-4 rounded-xl text-left transition-all ${
                    selectedVoice?.id === voice.id
                      ? 'bg-accent-primary/20 border-accent-primary/50'
                      : 'bg-white/5 hover:bg-white/10 border-transparent'
                  } border`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Volume2 className="w-4 h-4 text-accent-primary" />
                      <span className="font-medium">{voice.name}</span>
                    </div>
                    {getStatusIcon(voice.training_status)}
                  </div>
                  
                  {voice.description && (
                    <p className="text-sm text-text-secondary mb-2 line-clamp-2">
                      {voice.description}
                    </p>
                  )}
                  
                  <div className="flex items-center gap-3 text-xs text-text-secondary">
                    <span className="flex items-center gap-1">
                      <Upload className="w-3 h-3" />
                      {voice.sample_count} сэмплов
                    </span>
                    <span className={getStatusColor(voice.training_status)}>
                      {voice.is_trained ? 'Обучен' : 'Не обучен'}
                    </span>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Детали голоса */}
        <div className="flex-1 overflow-y-auto">
          {selectedVoice ? (
            <div className="p-6 space-y-6">
              {/* Заголовок */}
              <div className="flex items-start justify-between">
                <div>
                  <h1 className="text-3xl font-bold mb-2">{selectedVoice.name}</h1>
                  {selectedVoice.description && (
                    <p className="text-text-secondary">{selectedVoice.description}</p>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleTestVoice(selectedVoice.id)}
                    disabled={isPlaying}
                    className="px-4 py-2 bg-accent-primary hover:bg-accent-secondary disabled:opacity-50 text-white rounded-lg transition-colors flex items-center gap-2"
                  >
                    {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    Тест
                  </button>
                  <button
                    onClick={() => handleDeleteVoice(selectedVoice.id)}
                    className="p-2 hover:bg-red-500/20 text-red-400 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Статус обучения */}
              {trainingStatus && trainingStatus.status === 'training' && (
                <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-3">
                    <span className="font-medium text-blue-400">Обучение в процессе</span>
                    <span className="text-sm text-blue-400">
                      {trainingStatus.progress.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-blue-500/20 rounded-full h-2 mb-3">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all"
                      style={{ width: `${trainingStatus.progress}%` }}
                    />
                  </div>
                  <div className="flex items-center justify-between text-sm text-text-secondary">
                    <span>Эпоха {trainingStatus.current_epoch}/{trainingStatus.total_epochs}</span>
                    {trainingStatus.eta_seconds && (
                      <span>~{Math.ceil(trainingStatus.eta_seconds / 60)} мин</span>
                    )}
                  </div>
                </div>
              )}

              {/* Тестирование */}
              <div className="bg-white/5 rounded-xl p-4">
                <h3 className="font-medium mb-3">Тестовый текст</h3>
                <textarea
                  value={testText}
                  onChange={(e) => setTestText(e.target.value)}
                  className="w-full bg-bg-primary border border-border-subtle rounded-lg p-3 text-text-primary resize-none focus:outline-none focus:border-accent-primary transition-colors"
                  rows={3}
                  placeholder="Введите текст для тестирования голоса..."
                />
              </div>

              {/* Обучающие сэмплы */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold">
                    Обучающие сэмплы ({samples.length})
                  </h3>
                  <div className="flex items-center gap-2">
                    <label className="px-4 py-2 bg-white/5 hover:bg-white/10 text-text-primary rounded-lg transition-colors cursor-pointer flex items-center gap-2">
                      <Upload className="w-4 h-4" />
                      Добавить
                      <input
                        type="file"
                        accept="audio/*"
                        className="hidden"
                        onChange={async (e) => {
                          const file = e.target.files?.[0];
                          if (file) {
                            const text = prompt('Введите текст аудио:');
                            if (text) {
                              await handleAddSample(file, text);
                            }
                          }
                        }}
                      />
                    </label>
                    <button
                      onClick={() => setShowTrainModal(true)}
                      disabled={samples.length < 5}
                      className="px-4 py-2 bg-accent-primary hover:bg-accent-secondary disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center gap-2"
                    >
                      <Play className="w-4 h-4" />
                      Обучить
                    </button>
                  </div>
                </div>

                {samples.length < 5 && (
                  <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4 mb-4 flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-medium text-yellow-400 mb-1">
                        Недостаточно сэмплов
                      </p>
                      <p className="text-sm text-text-secondary">
                        Для обучения голоса требуется минимум 5 аудио сэмплов. 
                        Сейчас: {samples.length}/5
                      </p>
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-1 gap-3">
                  {samples.map((sample) => (
                    <div
                      key={sample.id}
                      className="bg-white/5 rounded-lg p-4 hover:bg-white/10 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <p className="text-sm text-text-primary mb-2">{sample.text}</p>
                          <span className="text-xs text-text-secondary">
                            {sample.duration.toFixed(1)}s
                          </span>
                        </div>
                        <button
                          onClick={() => handleDeleteSample(sample.id)}
                          className="p-1 hover:bg-red-500/20 text-red-400 rounded transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-text-secondary">
              <div className="text-center">
                <Mic className="w-16 h-16 mx-auto mb-4 opacity-30" />
                <p className="text-lg">Выберите голос из списка</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
