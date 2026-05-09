import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, X, Save, Server, Key, CheckCircle } from 'lucide-react';

interface SettingsProps {
  onSettingsChange: (serverUrl: string, apiKey: string) => void;
}

export default function Settings({ onSettingsChange }: SettingsProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [serverUrl, setServerUrl] = useState('http://localhost:8000');
  const [apiKey, setApiKey] = useState('');
  const [isSaved, setIsSaved] = useState(false);
  const [isTestingConnection, setIsTestingConnection] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'success' | 'error'>('idle');

  // Load settings from localStorage on mount
  useEffect(() => {
    const savedUrl = localStorage.getItem('edis_server_url');
    const savedKey = localStorage.getItem('edis_api_key');
    
    if (savedUrl) setServerUrl(savedUrl);
    if (savedKey) setApiKey(savedKey);
    
    // Notify parent if settings exist
    if (savedUrl && savedKey) {
      onSettingsChange(savedUrl, savedKey);
      setIsSaved(true);
    }
  }, [onSettingsChange]);

  const handleSave = () => {
    // Save to localStorage
    localStorage.setItem('edis_server_url', serverUrl);
    localStorage.setItem('edis_api_key', apiKey);
    
    // Notify parent component
    onSettingsChange(serverUrl, apiKey);
    
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2000);
  };

  const handleTest = async () => {
    setIsTestingConnection(true);
    setConnectionStatus('idle');
    
    try {
      const response = await fetch(`${serverUrl}/api/v1/health`, {
        headers: {
          'X-API-Key': apiKey
        }
      });
      
      if (response.ok) {
        setConnectionStatus('success');
        setTimeout(() => setConnectionStatus('idle'), 3000);
      } else {
        setConnectionStatus('error');
        setTimeout(() => setConnectionStatus('idle'), 3000);
      }
    } catch (error) {
      setConnectionStatus('error');
      setTimeout(() => setConnectionStatus('idle'), 3000);
    } finally {
      setIsTestingConnection(false);
    }
  };

  return (
    <>
      {/* Settings Button - Floating */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed top-6 right-6 z-50 p-3 glass-panel hover:scale-105 transition-all duration-300 group"
        title="Settings"
      >
        <SettingsIcon 
          className="w-6 h-6 text-accent-purple group-hover:rotate-90 transition-transform duration-500" 
        />
      </button>

      {/* Settings Modal */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in"
          style={{ background: 'rgba(0, 0, 0, 0.6)', backdropFilter: 'blur(8px)' }}
          onClick={() => setIsOpen(false)}
        >
          <div 
            className="relative w-full max-w-md glass-panel animate-scale-in"
            onClick={(e) => e.stopPropagation()}
          >
            
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-glass-border">
              <div className="flex items-center gap-3">
                <SettingsIcon className="w-6 h-6 text-accent-purple animate-pulse-soft" />
                <h2 className="text-2xl font-bold gradient-text">
                  Connection Settings
                </h2>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 hover:bg-glass-hover rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-accent-purple" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-6">
              
              {/* Server URL */}
              <div className="space-y-2">
                <label className="flex items-center gap-2 text-sm font-medium text-accent-cyan">
                  <Server className="w-4 h-4" />
                  Server URL
                </label>
                <input
                  type="text"
                  value={serverUrl}
                  onChange={(e) => setServerUrl(e.target.value)}
                  placeholder="http://your-server-ip:8000"
                  className="w-full px-4 py-3 glass-input"
                />
                <p className="text-xs text-text-muted">
                  Example: http://192.168.1.100:8000
                </p>
              </div>

              {/* API Key */}
              <div className="space-y-2">
                <label className="flex items-center gap-2 text-sm font-medium text-accent-cyan">
                  <Key className="w-4 h-4" />
                  API Key
                </label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="your-secret-api-key"
                  className="w-full px-4 py-3 glass-input"
                />
                <p className="text-xs text-text-muted">
                  Your secret API key for authentication
                </p>
              </div>

              {/* Connection Status */}
              {connectionStatus !== 'idle' && (
                <div className={`p-3 rounded-lg ${
                  connectionStatus === 'success' 
                    ? 'bg-accent-green bg-opacity-10 border border-accent-green border-opacity-30' 
                    : 'bg-accent-pink bg-opacity-10 border border-accent-pink border-opacity-30'
                }`}>
                  <p className={`text-sm flex items-center gap-2 ${
                    connectionStatus === 'success' ? 'text-accent-green' : 'text-accent-pink'
                  }`}>
                    {connectionStatus === 'success' ? (
                      <>
                        <CheckCircle className="w-4 h-4" />
                        Connection successful!
                      </>
                    ) : (
                      <>
                        <X className="w-4 h-4" />
                        Connection failed. Check your settings.
                      </>
                    )}
                  </p>
                </div>
              )}

              {/* Buttons */}
              <div className="flex gap-3 pt-4">
                <button
                  onClick={handleTest}
                  disabled={!serverUrl || !apiKey || isTestingConnection}
                  className="flex-1 btn-outline"
                >
                  {isTestingConnection ? 'Testing...' : 'Test Connection'}
                </button>
                
                <button
                  onClick={handleSave}
                  disabled={!serverUrl || !apiKey}
                  className="flex-1 btn-gradient flex items-center justify-center gap-2"
                >
                  <Save className="w-4 h-4" />
                  {isSaved ? 'Saved!' : 'Save'}
                </button>
              </div>

              {/* Info */}
              <div className="p-4 glass-card">
                <p className="text-xs text-text-secondary leading-relaxed">
                  💡 <strong>Tip:</strong> Settings are saved in your browser's localStorage. 
                  You can change them anytime by clicking the settings icon.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
