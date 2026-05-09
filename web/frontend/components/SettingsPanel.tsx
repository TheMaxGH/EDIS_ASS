/**
 * Settings Panel - Панель управления настройками системы
 * Вкладки: Models, Autonomy, Tools, System
 */
import React, { useState, useEffect } from 'react';
import EDISClient, {
  FullSettings,
  ModelSettings,
  AutonomySettings,
  ToolsSettings,
  SystemSettings,
  ConnectionTestResponse
} from '../lib/edis-client';

interface SettingsPanelProps {
  isOpen: boolean;
  onClose: () => void;
  edisClient: EDISClient;
}

type SettingsTab = 'models' | 'autonomy' | 'tools' | 'voice' | 'system';

export default function SettingsPanel({ isOpen, onClose, edisClient }: SettingsPanelProps) {
  const [activeTab, setActiveTab] = useState<SettingsTab>('models');
  const [settings, setSettings] = useState<FullSettings | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [testResults, setTestResults] = useState<Record<string, ConnectionTestResponse>>({});
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Загрузка настроек при открытии
  useEffect(() => {
    if (isOpen) {
      loadSettings();
    }
  }, [isOpen]);

  const loadSettings = async () => {
    setIsLoading(true);
    try {
      const data = await edisClient.getSettings();
      setSettings(data);
    } catch (error) {
      showNotification('error', 'Ошибка загрузки настроек');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!settings) return;

    setIsSaving(true);
    try {
      const response = await edisClient.updateSettings(settings);
      
      if (response.success) {
        showNotification('success', response.message);
        if (response.restart_required) {
          showNotification('success', '⚠️ Требуется перезапуск агента');
        }
      }
    } catch (error: any) {
      showNotification('error', error.response?.data?.detail || 'Ошибка сохранения');
    } finally {
      setIsSaving(false);
    }
  };

  const testConnection = async (type: 'creator' | 'logic' | 'tavily' | 'github') => {
    if (!settings) return;

    try {
      let config: Record<string, any> = {};

      if (type === 'creator') {
        config = {
          base_url: settings.models.creator.base_url,
          api_key: settings.models.creator.api_key,
          model_name: settings.models.creator.model_name
        };
      } else if (type === 'logic') {
        config = {
          base_url: settings.models.logic.base_url,
          api_key: settings.models.logic.api_key,
          model_name: settings.models.logic.model_name
        };
      } else if (type === 'tavily') {
        config = { api_key: settings.autonomy.tavily_api_key };
      } else if (type === 'github') {
        config = { token: settings.autonomy.github_token };
      }

      const result = await edisClient.testConnection({ type, config });
      setTestResults(prev => ({ ...prev, [type]: result }));
      
      if (result.success) {
        showNotification('success', `${type}: ${result.message}`);
      } else {
        showNotification('error', `${type}: ${result.message}`);
      }
    } catch (error) {
      showNotification('error', `Ошибка тестирования ${type}`);
    }
  };

  const showNotification = (type: 'success' | 'error', message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 5000);
  };

  const maskToken = (token: string | null | undefined): string => {
    if (!token || token.startsWith('••••')) return token || '';
    if (token.length < 8) return '••••••••';
    return '••••••••' + token.slice(-4);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-fade-in">
      <div className="bg-bg-secondary border border-border-subtle rounded-2xl shadow-elevated w-full max-w-4xl max-h-[90vh] overflow-hidden animate-scale-in">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border-subtle">
          <h2 className="text-2xl font-bold text-text-primary">⚙️ Настройки системы</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-bg-primary rounded-lg transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 p-4 border-b border-border-subtle bg-bg-primary/30">
          {[
            { id: 'models', label: '🤖 Модели', icon: '🤖' },
            { id: 'autonomy', label: '🔄 Автономность', icon: '🔄' },
            { id: 'tools', label: '🛠️ Инструменты', icon: '🛠️' },
            { id: 'voice', label: '🎤 Голос & TTS', icon: '🎤' },
            { id: 'system', label: '⚙️ Система', icon: '⚙️' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as SettingsTab)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-accent-primary text-white shadow-glow'
                  : 'text-text-secondary hover:bg-bg-secondary hover:text-text-primary'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-primary"></div>
            </div>
          ) : settings ? (
            <>
              {/* Models Tab */}
              {activeTab === 'models' && (
                <div className="space-y-6">
                  {/* Creator Model */}
                  <div className="bg-bg-primary/50 rounded-xl p-6 border border-border-subtle">
                    <h3 className="text-xl font-bold text-text-primary mb-4">Creator Model (Qwen2.5-72B)</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-2">Base URL</label>
                        <input
                          type="text"
                          value={settings.models.creator.base_url}
                          onChange={(e) => setSettings({
                            ...settings,
                            models: {
                              ...settings.models,
                              creator: { ...settings.models.creator, base_url: e.target.value }
                            }
                          })}
                          className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                          placeholder="http://localhost:8001/v1"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-2">API Key</label>
                        <input
                          type="password"
                          value={settings.models.creator.api_key}
                          onChange={(e) => setSettings({
                            ...settings,
                            models: {
                              ...settings.models,
                              creator: { ...settings.models.creator, api_key: e.target.value }
                            }
                          })}
                          className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none font-mono"
                          placeholder="dummy-key"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-2">Model Name</label>
                        <input
                          type="text"
                          value={settings.models.creator.model_name}
                          onChange={(e) => setSettings({
                            ...settings,
                            models: {
                              ...settings.models,
                              creator: { ...settings.models.creator, model_name: e.target.value }
                            }
                          })}
                          className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                        />
                      </div>

                      <div className="grid grid-cols-3 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-text-secondary mb-2">Temperature</label>
                          <input
                            type="number"
                            step="0.1"
                            min="0"
                            max="2"
                            value={settings.models.creator.temperature}
                            onChange={(e) => setSettings({
                              ...settings,
                              models: {
                                ...settings.models,
                                creator: { ...settings.models.creator, temperature: parseFloat(e.target.value) }
                              }
                            })}
                            className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-text-secondary mb-2">Max Tokens</label>
                          <input
                            type="number"
                            value={settings.models.creator.max_tokens}
                            onChange={(e) => setSettings({
                              ...settings,
                              models: {
                                ...settings.models,
                                creator: { ...settings.models.creator, max_tokens: parseInt(e.target.value) }
                              }
                            })}
                            className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-text-secondary mb-2">Top P</label>
                          <input
                            type="number"
                            step="0.05"
                            min="0"
                            max="1"
                            value={settings.models.creator.top_p}
                            onChange={(e) => setSettings({
                              ...settings,
                              models: {
                                ...settings.models,
                                creator: { ...settings.models.creator, top_p: parseFloat(e.target.value) }
                              }
                            })}
                            className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                          />
                        </div>
                      </div>

                      <button
                        onClick={() => testConnection('creator')}
                        className="w-full px-4 py-2 bg-accent-secondary hover:bg-accent-secondary/80 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                      >
                        <span>🔌</span>
                        <span>Test Connection</span>
                      </button>

                      {testResults.creator && (
                        <div className={`p-3 rounded-lg ${testResults.creator.success ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                          {testResults.creator.success ? '✓' : '✗'} {testResults.creator.message}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Logic Model */}
                  <div className="bg-bg-primary/50 rounded-xl p-6 border border-border-subtle">
                    <h3 className="text-xl font-bold text-text-primary mb-4">Logic Model (Qwen3.5-397B)</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-2">Base URL</label>
                        <input
                          type="text"
                          value={settings.models.logic.base_url}
                          onChange={(e) => setSettings({
                            ...settings,
                            models: {
                              ...settings.models,
                              logic: { ...settings.models.logic, base_url: e.target.value }
                            }
                          })}
                          className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                          placeholder="http://localhost:8002/v1"
                        />
                      </div>
    
                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-2">API Key</label>
                        <input
                          type="password"
                          value={settings.models.logic.api_key}
                          onChange={(e) => setSettings({
                            ...settings,
                            models: {
                              ...settings.models,
                              logic: { ...settings.models.logic, api_key: e.target.value }
                            }
                          })}
                          className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none font-mono"
                          placeholder="dummy-key"
                        />
                      </div>
    
                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-2">Model Name</label>
                        <input
                          type="text"
                          value={settings.models.logic.model_name}
                          onChange={(e) => setSettings({
                            ...settings,
                            models: {
                              ...settings.models,
                              logic: { ...settings.models.logic, model_name: e.target.value }
                            }
                          })}
                          className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                        />
                      </div>
    
                      <div className="grid grid-cols-3 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-text-secondary mb-2">Temperature</label>
                          <input
                            type="number"
                            step="0.1"
                            min="0"
                            max="2"
                            value={settings.models.logic.temperature}
                            onChange={(e) => setSettings({
                              ...settings,
                              models: {
                                ...settings.models,
                                logic: { ...settings.models.logic, temperature: parseFloat(e.target.value) }
                              }
                            })}
                            className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                          />
                        </div>
    
                        <div>
                          <label className="block text-sm font-medium text-text-secondary mb-2">Max Tokens</label>
                          <input
                            type="number"
                            value={settings.models.logic.max_tokens}
                            onChange={(e) => setSettings({
                              ...settings,
                              models: {
                                ...settings.models,
                                logic: { ...settings.models.logic, max_tokens: parseInt(e.target.value) }
                              }
                            })}
                            className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                          />
                        </div>
    
                        <div>
                          <label className="block text-sm font-medium text-text-secondary mb-2">Top P</label>
                          <input
                            type="number"
                            step="0.05"
                            min="0"
                            max="1"
                            value={settings.models.logic.top_p}
                            onChange={(e) => setSettings({
                              ...settings,
                              models: {
                                ...settings.models,
                                logic: { ...settings.models.logic, top_p: parseFloat(e.target.value) }
                              }
                            })}
                            className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                          />
                        </div>
                      </div>
    
                      <button
                        onClick={() => testConnection('logic')}
                        className="w-full px-4 py-2 bg-accent-secondary hover:bg-accent-secondary/80 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                      >
                        <span>🔌</span>
                        <span>Test Connection</span>
                      </button>
    
                      {testResults.logic && (
                        <div className={`p-3 rounded-lg ${testResults.logic.success ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                          {testResults.logic.success ? '✓' : '✗'} {testResults.logic.message}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Autonomy Tab */}
              {activeTab === 'autonomy' && (
                <div className="space-y-6">
                  <div className="bg-bg-primary/50 rounded-xl p-6 border border-border-subtle">
                    <h3 className="text-xl font-bold text-text-primary mb-4">Автономный режим</h3>
                    <div className="space-y-4">
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={settings.autonomy.enabled}
                          onChange={(e) => setSettings({
                            ...settings,
                            autonomy: { ...settings.autonomy, enabled: e.target.checked }
                          })}
                          className="w-5 h-5 rounded border-border-subtle bg-bg-secondary checked:bg-accent-primary"
                        />
                        <span className="text-text-primary font-medium">Включить автономный режим</span>
                      </label>

                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-2">Tavily API Key</label>
                        <input
                          type="password"
                          value={settings.autonomy.tavily_api_key || ''}
                          onChange={(e) => setSettings({
                            ...settings,
                            autonomy: { ...settings.autonomy, tavily_api_key: e.target.value }
                          })}
                          className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none font-mono"
                          placeholder="tvly-..."
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-2">GitHub Token</label>
                        <input
                          type="password"
                          value={settings.autonomy.github_token || ''}
                          onChange={(e) => setSettings({
                            ...settings,
                            autonomy: { ...settings.autonomy, github_token: e.target.value }
                          })}
                          className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none font-mono"
                          placeholder="ghp_..."
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-2">
                          Check Interval: {Math.floor(settings.autonomy.check_interval / 3600)} часов
                        </label>
                        <input
                          type="range"
                          min="3600"
                          max="86400"
                          step="3600"
                          value={settings.autonomy.check_interval}
                          onChange={(e) => setSettings({
                            ...settings,
                            autonomy: { ...settings.autonomy, check_interval: parseInt(e.target.value) }
                          })}
                          className="w-full"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-2">Max Articles</label>
                        <input
                          type="number"
                          min="1"
                          max="50"
                          value={settings.autonomy.max_articles}
                          onChange={(e) => setSettings({
                            ...settings,
                            autonomy: { ...settings.autonomy, max_articles: parseInt(e.target.value) }
                          })}
                          className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tools Tab */}
              {activeTab === 'tools' && (
                <div className="space-y-6">
                  {/* Sandbox Settings */}
                  <div className="bg-bg-primary/50 rounded-xl p-6 border border-border-subtle">
                    <h3 className="text-xl font-bold text-text-primary mb-4">🐳 Sandbox (Docker)</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-2">Timeout (секунды)</label>
                        <input
                          type="number"
                          min="1"
                          max="300"
                          value={settings.tools.sandbox_timeout}
                          onChange={(e) => setSettings({
                            ...settings,
                            tools: { ...settings.tools, sandbox_timeout: parseInt(e.target.value) }
                          })}
                          className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-2">Memory Limit</label>
                        <input
                          type="text"
                          value={settings.tools.sandbox_memory}
                          onChange={(e) => setSettings({
                            ...settings,
                            tools: { ...settings.tools, sandbox_memory: e.target.value }
                          })}
                          className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                          placeholder="512m"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Browser Settings */}
                  <div className="bg-bg-primary/50 rounded-xl p-6 border border-border-subtle">
                    <h3 className="text-xl font-bold text-text-primary mb-4">🌐 Browser (Playwright)</h3>
                    <div className="space-y-4">
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={settings.tools.browser_headless}
                          onChange={(e) => setSettings({
                            ...settings,
                            tools: { ...settings.tools, browser_headless: e.target.checked }
                          })}
                          className="w-5 h-5 rounded border-border-subtle bg-bg-secondary checked:bg-accent-primary"
                        />
                        <span className="text-text-primary font-medium">Headless режим</span>
                      </label>

                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-2">Timeout (мс)</label>
                        <input
                          type="number"
                          min="1000"
                          max="120000"
                          step="1000"
                          value={settings.tools.browser_timeout}
                          onChange={(e) => setSettings({
                            ...settings,
                            tools: { ...settings.tools, browser_timeout: parseInt(e.target.value) }
                          })}
                          className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                        />
                      </div>
                    </div>
                  </div>

                  {/* TTS Settings */}
                  <div className="bg-bg-primary/50 rounded-xl p-6 border border-border-subtle">
                    <h3 className="text-xl font-bold text-text-primary mb-4">🎤 TTS (GPT-SoVITS)</h3>
                    <div className="space-y-4">
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={settings.tools.tts_enabled}
                          onChange={(e) => setSettings({
                            ...settings,
                            tools: { ...settings.tools, tts_enabled: e.target.checked }
                          })}
                          className="w-5 h-5 rounded border-border-subtle bg-bg-secondary checked:bg-accent-primary"
                        />
                        <span className="text-text-primary font-medium">Включить TTS</span>
                      </label>

                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-2">API URL</label>
                        <input
                          type="text"
                          value={settings.tools.tts_api_url}
                          onChange={(e) => setSettings({
                            ...settings,
                            tools: { ...settings.tools, tts_api_url: e.target.value }
                          })}
                          className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                          placeholder="http://localhost:9880"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-2">Speaker Name</label>
                        <input
                          type="text"
                          value={settings.tools.tts_speaker_name}
                          onChange={(e) => setSettings({
                            ...settings,
                            tools: { ...settings.tools, tts_speaker_name: e.target.value }
                          })}
                          className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-2">Language</label>
                        <select
                          value={settings.tools.tts_language}
                          onChange={(e) => setSettings({
                            ...settings,
                            tools: { ...settings.tools, tts_language: e.target.value }
                          })}
                          className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                        >
                          <option value="ru">Русский</option>
                          <option value="en">English</option>
                          <option value="zh">中文</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Document Engine */}
                  <div className="bg-bg-primary/50 rounded-xl p-6 border border-border-subtle">
                    <h3 className="text-xl font-bold text-text-primary mb-4">📄 Document Engine</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-2">Output Directory</label>
                        <input
                          type="text"
                          value={settings.tools.output_dir}
                          onChange={(e) => setSettings({
                            ...settings,
                            tools: { ...settings.tools, output_dir: e.target.value }
                          })}
                          className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                          placeholder="outputs"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Voice & TTS Tab */}
              {activeTab === 'voice' && (
                <div className="space-y-6">
                  {/* GPT-SoVITS Info */}
                  <div className="bg-bg-primary/50 rounded-xl p-6 border border-border-subtle">
                    <h3 className="text-xl font-bold text-text-primary mb-4">🎤 GPT-SoVITS TTS</h3>
                    <div className="space-y-4">
                      <div className="bg-accent-primary/10 border border-accent-primary/30 rounded-lg p-4">
                        <p className="text-text-secondary text-sm leading-relaxed">
                          <strong className="text-accent-primary">GPT-SoVITS</strong> - это продвинутая система синтеза речи с поддержкой клонирования голоса.
                          Система автоматически устанавливается при первом запуске и работает на GPU 6 (порт 9880).
                        </p>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div className="bg-bg-secondary/50 rounded-lg p-4 border border-border-subtle">
                          <div className="text-sm font-medium text-text-secondary mb-1">Статус</div>
                          <div className="text-lg font-bold text-green-400">🟢 Активен</div>
                        </div>
                        <div className="bg-bg-secondary/50 rounded-lg p-4 border border-border-subtle">
                          <div className="text-sm font-medium text-text-secondary mb-1">Порт</div>
                          <div className="text-lg font-bold text-text-primary">9880</div>
                        </div>
                        <div className="bg-bg-secondary/50 rounded-lg p-4 border border-border-subtle">
                          <div className="text-sm font-medium text-text-secondary mb-1">GPU</div>
                          <div className="text-lg font-bold text-text-primary">GPU 6</div>
                        </div>
                        <div className="bg-bg-secondary/50 rounded-lg p-4 border border-border-subtle">
                          <div className="text-sm font-medium text-text-secondary mb-1">Модель</div>
                          <div className="text-lg font-bold text-text-primary">s2G488k</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Voice Features */}
                  <div className="bg-bg-primary/50 rounded-xl p-6 border border-border-subtle">
                    <h3 className="text-xl font-bold text-text-primary mb-4">✨ Возможности</h3>
                    <div className="space-y-3">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-lg bg-accent-primary/20 flex items-center justify-center flex-shrink-0">
                          <span className="text-lg">🎯</span>
                        </div>
                        <div>
                          <div className="font-semibold text-text-primary">Озвучка сообщений</div>
                          <div className="text-sm text-text-secondary">Нажмите кнопку "Озвучить" под любым сообщением ассистента</div>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-lg bg-accent-primary/20 flex items-center justify-center flex-shrink-0">
                          <span className="text-lg">🎙️</span>
                        </div>
                        <div>
                          <div className="font-semibold text-text-primary">Голосовой ввод</div>
                          <div className="text-sm text-text-secondary">Используйте микрофон для отправки голосовых сообщений</div>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-lg bg-accent-primary/20 flex items-center justify-center flex-shrink-0">
                          <span className="text-lg">🔊</span>
                        </div>
                        <div>
                          <div className="font-semibold text-text-primary">Клонирование голоса</div>
                          <div className="text-sm text-text-secondary">Обучение на новых голосах через Voice Management (скоро)</div>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-lg bg-accent-primary/20 flex items-center justify-center flex-shrink-0">
                          <span className="text-lg">🌍</span>
                        </div>
                        <div>
                          <div className="font-semibold text-text-primary">Мультиязычность</div>
                          <div className="text-sm text-text-secondary">Поддержка русского, английского, китайского и японского языков</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Quick Actions */}
                  <div className="bg-bg-primary/50 rounded-xl p-6 border border-border-subtle">
                    <h3 className="text-xl font-bold text-text-primary mb-4">⚡ Быстрые действия</h3>
                    <div className="grid grid-cols-2 gap-3">
                      <button
                        className="px-4 py-3 bg-accent-primary/10 hover:bg-accent-primary/20 border border-accent-primary/30 rounded-lg text-text-primary font-medium transition-colors text-left"
                        onClick={() => window.open('http://localhost:9880', '_blank')}
                      >
                        <div className="text-sm text-text-secondary mb-1">🌐 Открыть</div>
                        <div>GPT-SoVITS WebUI</div>
                      </button>
                      <button
                        className="px-4 py-3 bg-bg-secondary hover:bg-bg-secondary/70 border border-border-subtle rounded-lg text-text-primary font-medium transition-colors text-left"
                        onClick={() => alert('Voice Management UI - в разработке')}
                      >
                        <div className="text-sm text-text-secondary mb-1">🎤 Управление</div>
                        <div>Voice Library (скоро)</div>
                      </button>
                    </div>
                  </div>

                  {/* Documentation Link */}
                  <div className="bg-gradient-to-r from-accent-primary/10 to-accent-secondary/10 rounded-xl p-6 border border-accent-primary/20">
                    <div className="flex items-start gap-4">
                      <div className="text-4xl">📚</div>
                      <div className="flex-1">
                        <h4 className="text-lg font-bold text-text-primary mb-2">Документация</h4>
                        <p className="text-sm text-text-secondary mb-3">
                          Подробная информация об установке, настройке и использовании GPT-SoVITS доступна в документации проекта.
                        </p>
                        <button
                          className="px-4 py-2 bg-accent-primary hover:bg-accent-primary/80 text-white rounded-lg font-medium transition-colors text-sm"
                          onClick={() => window.open('https://github.com/RVC-Boss/GPT-SoVITS', '_blank')}
                        >
                          Открыть документацию →
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* System Tab */}
              {activeTab === 'system' && (
                <div className="space-y-6">
                  {/* Qdrant Settings */}
                  <div className="bg-bg-primary/50 rounded-xl p-6 border border-border-subtle">
                    <h3 className="text-xl font-bold text-text-primary mb-4">🗄️ Qdrant (Vector Store)</h3>
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-text-secondary mb-2">Host</label>
                          <input
                            type="text"
                            value={settings.system.qdrant_host}
                            onChange={(e) => setSettings({
                              ...settings,
                              system: { ...settings.system, qdrant_host: e.target.value }
                            })}
                            className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                            placeholder="localhost"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-text-secondary mb-2">Port</label>
                          <input
                            type="number"
                            min="1"
                            max="65535"
                            value={settings.system.qdrant_port}
                            onChange={(e) => setSettings({
                              ...settings,
                              system: { ...settings.system, qdrant_port: parseInt(e.target.value) }
                            })}
                            className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-2">Collection Name</label>
                        <input
                          type="text"
                          value={settings.system.qdrant_collection}
                          onChange={(e) => setSettings({
                            ...settings,
                            system: { ...settings.system, qdrant_collection: e.target.value }
                          })}
                          className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-2">Vector Size</label>
                        <input
                          type="number"
                          min="128"
                          max="4096"
                          step="128"
                          value={settings.system.qdrant_vector_size}
                          onChange={(e) => setSettings({
                            ...settings,
                            system: { ...settings.system, qdrant_vector_size: parseInt(e.target.value) }
                          })}
                          className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Workflow Settings */}
                  <div className="bg-bg-primary/50 rounded-xl p-6 border border-border-subtle">
                    <h3 className="text-xl font-bold text-text-primary mb-4">⚡ Workflow</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-2">Max Conflict Retries</label>
                        <input
                          type="number"
                          min="1"
                          max="10"
                          value={settings.system.max_conflict_retries}
                          onChange={(e) => setSettings({
                            ...settings,
                            system: { ...settings.system, max_conflict_retries: parseInt(e.target.value) }
                          })}
                          className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-2">
                          Conflict Threshold: {settings.system.conflict_threshold.toFixed(2)}
                        </label>
                        <input
                          type="range"
                          min="0"
                          max="1"
                          step="0.05"
                          value={settings.system.conflict_threshold}
                          onChange={(e) => setSettings({
                            ...settings,
                            system: { ...settings.system, conflict_threshold: parseFloat(e.target.value) }
                          })}
                          className="w-full"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Logging Settings */}
                  <div className="bg-bg-primary/50 rounded-xl p-6 border border-border-subtle">
                    <h3 className="text-xl font-bold text-text-primary mb-4">📝 Logging</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-2">Log Level</label>
                        <select
                          value={settings.system.log_level}
                          onChange={(e) => setSettings({
                            ...settings,
                            system: { ...settings.system, log_level: e.target.value }
                          })}
                          className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                        >
                          <option value="DEBUG">DEBUG</option>
                          <option value="INFO">INFO</option>
                          <option value="WARNING">WARNING</option>
                          <option value="ERROR">ERROR</option>
                          <option value="CRITICAL">CRITICAL</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-2">Log File</label>
                        <input
                          type="text"
                          value={settings.system.log_file}
                          onChange={(e) => setSettings({
                            ...settings,
                            system: { ...settings.system, log_file: e.target.value }
                          })}
                          className="w-full px-4 py-2 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary focus:border-accent-primary focus:outline-none"
                          placeholder="logs/dual_qwen_brain.log"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : null}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-border-subtle bg-bg-primary/30">
          <button
            onClick={onClose}
            className="px-6 py-2 text-text-secondary hover:text-text-primary transition-colors"
          >
            Отмена
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="px-6 py-2 bg-accent-primary hover:bg-accent-primary/80 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSaving ? 'Сохранение...' : 'Сохранить'}
          </button>
        </div>

        {/* Notification */}
        {notification && (
          <div className={`fixed bottom-6 right-6 px-6 py-3 rounded-lg shadow-elevated animate-slide-up ${
            notification.type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
          }`}>
            {notification.message}
          </div>
        )}
      </div>
    </div>
  );
}
