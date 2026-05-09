/**
 * Autonomous Log Page
 * Страница полного автономного лога
 */

import React, { useEffect, useState, useCallback } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import {
  ArrowLeft,
  Zap,
  AlertCircle,
  Info,
  CheckCircle,
  XCircle,
  Bug,
  Filter,
  Trash2,
  Settings as SettingsIcon
} from 'lucide-react';
import EDISClient, { LogMessage } from '../lib/edis-client';
import Settings from '../components/Settings';
import SettingsPanel from '../components/SettingsPanel';

export default function AutonomousPage() {
  const [serverUrl, setServerUrl] = useState('http://localhost:8000');
  const [apiKey, setApiKey] = useState('your-api-key-here');
  const [client, setClient] = useState<EDISClient>(() => new EDISClient('http://localhost:8000', 'your-api-key-here'));
  const [isConnected, setIsConnected] = useState(false);
  const [logs, setLogs] = useState<LogMessage[]>([]);
  const [filter, setFilter] = useState<'all' | 'info' | 'success' | 'warning' | 'error' | 'debug'>('all');
  const [isSettingsPanelOpen, setIsSettingsPanelOpen] = useState(false);

  const handleSettingsChange = useCallback((newServerUrl: string, newApiKey: string) => {
    setServerUrl(newServerUrl);
    setApiKey(newApiKey);
    const newClient = new EDISClient(newServerUrl, newApiKey);
    setClient(newClient);
  }, []);

  useEffect(() => {
    if (!serverUrl || !apiKey) {
      setIsConnected(false);
      return;
    }

    client.ping().then(connected => {
      setIsConnected(connected);
      if (connected) {
        client.connectToLogs((log) => {
          setLogs(prev => [...prev, log]);
        });
      }
    }).catch(() => {
      setIsConnected(false);
    });

    return () => {
      client.disconnectFromLogs();
    };
  }, [client, serverUrl, apiKey]);

  const filteredLogs = filter === 'all' 
    ? logs 
    : logs.filter(log => log.level === filter);

  const getLogIcon = (level: string) => {
    switch (level) {
      case 'error':
        return <XCircle className="w-5 h-5 text-red-400" />;
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-400" />;
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'info':
        return <Info className="w-5 h-5 text-blue-400" />;
      case 'debug':
        return <Bug className="w-5 h-5 text-gray-400" />;
      default:
        return <Info className="w-5 h-5 text-text-muted" />;
    }
  };

  const getLogColor = (level: string) => {
    switch (level) {
      case 'error':
        return 'border-red-400/30 bg-red-400/10';
      case 'warning':
        return 'border-yellow-400/30 bg-yellow-400/10';
      case 'success':
        return 'border-green-400/30 bg-green-400/10';
      case 'info':
        return 'border-blue-400/30 bg-blue-400/10';
      case 'debug':
        return 'border-gray-400/30 bg-gray-400/10';
      default:
        return 'border-white/10 bg-white/5';
    }
  };

  const clearLogs = () => {
    setLogs([]);
  };

  return (
    <>
      <Head>
        <title>Автономный лог - EDIS</title>
        <meta name="description" content="Полный автономный лог EDIS" />
      </Head>

      <Settings onSettingsChange={handleSettingsChange} />

      {/* Settings Panel */}
      <SettingsPanel
        isOpen={isSettingsPanelOpen}
        onClose={() => setIsSettingsPanelOpen(false)}
        edisClient={client}
      />

      {/* Навигация */}
      <nav className="sticky top-0 z-50 bg-bg-secondary/80 backdrop-blur-xl border-b border-white/5 shadow-elevated">
        <div className="max-w-[1920px] mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              href="/"
              className="p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-primary-purple/50 transition-all"
            >
              <ArrowLeft className="w-5 h-5 text-text-secondary" />
            </Link>
            <div className="flex items-center gap-3">
              <Zap className="w-6 h-6 text-primary-purple" />
              <span className="text-xl font-bold gradient-text-combo">
                Автономный лог
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={clearLogs}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-red-400/50 transition-all text-sm"
            >
              <Trash2 className="w-4 h-4 text-red-400" />
              <span className="text-text-secondary">Очистить</span>
            </button>

            {/* Settings Button */}
            <button
              onClick={() => setIsSettingsPanelOpen(true)}
              className="
                p-2 rounded-lg
                bg-white/5 hover:bg-white/10
                border border-white/10 hover:border-accent-primary/50
                transition-all duration-200
                group
              "
              title="Настройки системы"
            >
              <SettingsIcon className="w-5 h-5 text-text-secondary group-hover:text-accent-primary transition-colors" />
            </button>
          </div>
        </div>
      </nav>

      <div className="min-h-screen bg-bg-primary p-6">
        <div className="max-w-[1920px] mx-auto">
          
          {/* Фильтры */}
          <div className="mb-6 p-4 rounded-xl bg-bg-secondary/80 backdrop-blur-md border border-white/5 shadow-card animate-fade-in">
            <div className="flex items-center gap-3 flex-wrap">
              <Filter className="w-5 h-5 text-text-muted" />
              <span className="text-sm text-text-secondary">Фильтр:</span>
              
              {(['all', 'info', 'success', 'warning', 'error', 'debug'] as const).map((level) => (
                <button
                  key={level}
                  onClick={() => setFilter(level)}
                  className={`
                    px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                    ${filter === level 
                      ? 'bg-primary-purple text-white shadow-glow-purple-sm' 
                      : 'bg-white/5 text-text-secondary hover:bg-white/10 border border-white/10'
                    }
                  `}
                >
                  {level === 'all' ? 'Все' : level}
                </button>
              ))}

              <div className="ml-auto text-sm text-text-muted">
                Всего событий: <span className="font-bold text-text-secondary">{filteredLogs.length}</span>
              </div>
            </div>
          </div>

          {/* Лог-лента */}
          <div className="space-y-3">
            {filteredLogs.length === 0 ? (
              <div className="p-12 rounded-xl bg-bg-secondary/80 border border-white/5 text-center">
                <Zap className="w-16 h-16 text-text-muted mx-auto mb-4 opacity-50" />
                <p className="text-text-muted text-lg">
                  {filter === 'all' ? 'Нет событий в логе' : `Нет событий уровня "${filter}"`}
                </p>
                {!isConnected && (
                  <p className="text-sm text-accent-orange mt-2">
                    Подключитесь к серверу для получения логов
                  </p>
                )}
              </div>
            ) : (
              <div className="space-y-2 max-h-[calc(100vh-250px)] overflow-y-auto custom-scrollbar">
                {filteredLogs.slice().reverse().map((log, idx) => (
                  <div
                    key={idx}
                    className={`
                      p-4 rounded-xl border transition-all animate-slide-up
                      ${getLogColor(log.level)}
                      hover:scale-[1.01]
                    `}
                  >
                    <div className="flex items-start gap-3">
                      {getLogIcon(log.level)}
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-1">
                          <span className="text-xs font-mono text-text-muted">
                            {new Date(log.timestamp).toLocaleString('ru-RU')}
                          </span>
                          {log.source && (
                            <span className="px-2 py-0.5 rounded text-xs font-medium bg-white/10 text-text-secondary">
                              {log.source}
                            </span>
                          )}
                          <span className={`
                            px-2 py-0.5 rounded text-xs font-bold uppercase
                            ${log.level === 'error' ? 'bg-red-400/20 text-red-400' : ''}
                            ${log.level === 'warning' ? 'bg-yellow-400/20 text-yellow-400' : ''}
                            ${log.level === 'success' ? 'bg-green-400/20 text-green-400' : ''}
                            ${log.level === 'info' ? 'bg-blue-400/20 text-blue-400' : ''}
                            ${log.level === 'debug' ? 'bg-gray-400/20 text-gray-400' : ''}
                          `}>
                            {log.level}
                          </span>
                        </div>
                        
                        <p className="text-sm text-text-primary whitespace-pre-wrap break-words">
                          {log.message}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Статистика */}
          {logs.length > 0 && (
            <div className="mt-6 p-4 rounded-xl bg-bg-secondary/80 border border-white/5 animate-fade-in">
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {(['info', 'success', 'warning', 'error', 'debug'] as const).map((level) => {
                  const count = logs.filter(log => log.level === level).length;
                  return (
                    <div key={level} className="text-center">
                      <p className="text-2xl font-bold text-text-primary">{count}</p>
                      <p className="text-xs text-text-muted uppercase">{level}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(139, 92, 246, 0.5);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(139, 92, 246, 0.7);
        }
      `}</style>
    </>
  );
}
