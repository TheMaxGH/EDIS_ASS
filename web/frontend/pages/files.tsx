import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import FileManager from '../components/FileManager';
import Settings from '../components/Settings';

export default function FilesPage() {
  const [serverUrl, setServerUrl] = useState('http://localhost:8000');
  const [apiKey, setApiKey] = useState('your-secret-key-here');
  const [showSettings, setShowSettings] = useState(false);

  // Загрузка настроек из localStorage
  useEffect(() => {
    const savedServerUrl = localStorage.getItem('edis_server_url');
    const savedApiKey = localStorage.getItem('edis_api_key');
    
    if (savedServerUrl) setServerUrl(savedServerUrl);
    if (savedApiKey) setApiKey(savedApiKey);
  }, []);

  const handleSettingsChange = (newServerUrl: string, newApiKey: string) => {
    setServerUrl(newServerUrl);
    setApiKey(newApiKey);
    setShowSettings(false);
  };
  return (
    <>
      <Head>
        <title>Файловый менеджер - EDIS</title>
        <meta name="description" content="Управление файлами в песочнице Docker" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen p-6 bg-gradient-to-br from-bg-primary via-bg-secondary to-bg-primary">
        {/* Header */}
        <header className="mb-8 animate-fade-in">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <Link 
                href="/"
                className="
                  px-4 py-2 rounded-xl
                  bg-bg-secondary/50 backdrop-blur-md
                  border border-glass-border/50
                  text-text-secondary hover:text-text-primary
                  transition-all duration-300
                  hover:border-accent-primary/50
                  hover:shadow-lg hover:shadow-accent-primary/10
                "
              >
                ← Назад
              </Link>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-accent-primary via-accent-secondary to-accent-cyan bg-clip-text text-transparent">
                Файловый менеджер
              </h1>
            </div>
            
            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="
                  px-4 py-2 rounded-xl
                  bg-bg-secondary/50 backdrop-blur-md
                  border border-glass-border/50
                  text-text-secondary hover:text-text-primary
                  transition-all duration-300
                  hover:border-accent-primary/50
                  hover:shadow-lg hover:shadow-accent-primary/10
                "
              >
                ⚙️ Настройки
              </button>
              <Link
                href="/chat"
                className="
                  px-4 py-2 rounded-xl
                  bg-gradient-to-r from-accent-primary/20 to-accent-secondary/20
                  backdrop-blur-md border border-accent-primary/30
                  text-text-primary font-medium
                  transition-all duration-300
                  hover:from-accent-primary/30 hover:to-accent-secondary/30
                  hover:border-accent-primary/50
                  hover:shadow-lg hover:shadow-accent-primary/20
                "
              >
                💬 Чат
              </Link>
            </div>
          </div>

          <p className="text-text-secondary text-lg">
            Управление файлами в изолированной песочнице Docker
          </p>
        </header>

        {/* Settings Panel */}
        {showSettings && (
          <div className="mb-6 animate-slide-up">
            <Settings onSettingsChange={handleSettingsChange} />
          </div>
        )}

        {/* File Manager */}
        <div className="animate-slide-up">
          <FileManager serverUrl={serverUrl} apiKey={apiKey} />
        </div>

        {/* Footer */}
        <footer className="mt-8 text-center animate-fade-in">
          <p className="text-text-secondary text-sm">
            Все операции выполняются в изолированном контейнере Docker
          </p>
        </footer>
      </div>
    </>
  );
}
