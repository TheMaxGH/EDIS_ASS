/**
 * Main Dashboard Page
 * Модульный дашборд с виджетами в стиле OpenWebUI
 */

import React, { useEffect, useState, useCallback } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import {
  Wifi,
  WifiOff,
  MessageSquare,
  FolderOpen,
  Activity,
  CheckSquare,
  Zap,
  BarChart3,
  Briefcase,
  Clock,
  Settings as SettingsIcon
} from 'lucide-react';
import EDISClient, { LogMessage, SystemStats } from '../lib/edis-client';
import Settings from '../components/Settings';
import SettingsPanel from '../components/SettingsPanel';
import Widget from '../components/dashboard/Widget';

export default function Home() {
  const router = useRouter();
  const [serverUrl, setServerUrl] = useState('http://localhost:8000');
  const [apiKey, setApiKey] = useState('your-api-key-here');
  const [client, setClient] = useState<EDISClient>(() => new EDISClient('http://localhost:8000', 'your-api-key-here'));
  const [isConnected, setIsConnected] = useState(false);
  const [logs, setLogs] = useState<LogMessage[]>([]);
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [tasks, setTasks] = useState<any[]>([]);
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
          setLogs(prev => [...prev.slice(-99), log]);
        });
        loadStats(client);
        loadTasks(client);
      }
    }).catch(() => {
      setIsConnected(false);
    });

    return () => {
      client.disconnectFromLogs();
    };
  }, [client, serverUrl, apiKey]);

  useEffect(() => {
    if (!client || !isConnected) return;
    const interval = setInterval(() => {
      loadStats(client);
      loadTasks(client);
    }, 5000);
    return () => clearInterval(interval);
  }, [client, isConnected]);

  const loadStats = async (edisClient: EDISClient) => {
    try {
      const systemStats = await edisClient.getSystemStats();
      setStats(systemStats);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const loadTasks = async (edisClient: EDISClient) => {
    try {
      const taskList = await edisClient.listTasks();
      setTasks(taskList);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    }
  };

  const recentLogs = logs.slice(-5);
  const activeTasks = tasks.filter(t => t.status === 'running' || t.status === 'pending');

  return (
    <>
      <Head>
        <title>EDIS Control Center</title>
        <meta name="description" content="Enhanced Dual Intelligence System" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <Settings onSettingsChange={handleSettingsChange} />

      {/* Settings Panel */}
      <SettingsPanel
        isOpen={isSettingsPanelOpen}
        onClose={() => setIsSettingsPanelOpen(false)}
        edisClient={client}
      />

      {/* Верхняя навигация */}
      <nav className="sticky top-0 z-50 bg-bg-secondary/80 backdrop-blur-xl border-b border-white/5 shadow-elevated">
        <div className="max-w-[1920px] mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-combo flex items-center justify-center shadow-glow-purple-sm">
              <span className="text-xl font-bold text-white">E</span>
            </div>
            <span className="text-xl font-bold gradient-text-combo">
              EDIS Control Center
            </span>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-bg-secondary border border-white/10">
              {isConnected ? (
                <>
                  <Wifi className="w-4 h-4 text-green-400" />
                  <span className="text-sm font-medium text-green-400">Подключено</span>
                </>
              ) : (
                <>
                  <WifiOff className="w-4 h-4 text-accent-orange" />
                  <span className="text-sm font-medium text-accent-orange">Отключено</span>
                </>
              )}
            </div>

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
        {!isConnected && (
          <div className="mb-6 p-4 rounded-xl bg-accent-orange/10 border border-accent-orange/30 animate-slide-up max-w-[1920px] mx-auto">
            <div className="flex items-center gap-3">
              <WifiOff className="w-6 h-6 text-accent-orange flex-shrink-0" />
              <div>
                <h3 className="text-accent-orange font-bold mb-1">Нет подключения</h3>
                <p className="text-sm text-text-secondary">
                  Нажмите на иконку настроек (⚙️) в правом нижнем углу, чтобы настроить подключение к серверу.
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="max-w-[1920px] mx-auto">
          {/* Заголовок */}
          <header className="mb-8 animate-fade-in">
            <h1 className="text-4xl font-bold gradient-text-combo mb-2">
              Панель управления
            </h1>
            <p className="text-text-secondary">
              Enhanced Dual Intelligence System v1.0
            </p>
          </header>

          {/* Сетка виджетов */}
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            
            {/* Виджет Чата */}
            <Widget
              title="Чат"
              icon={<MessageSquare className="w-5 h-5" />}
              gradient="purple"
              onExpand={() => router.push('/chat')}
            >
              <div className="space-y-3">
                <p className="text-sm text-text-muted mb-4">
                  Общайтесь с EDIS AI через интеллектуальный интерфейс
                </p>
                <button
                  onClick={() => router.push('/chat')}
                  className="w-full px-4 py-3 rounded-lg bg-gradient-purple text-white font-medium hover:shadow-glow-purple-sm transition-all"
                >
                  Открыть чат
                </button>
              </div>
            </Widget>

            {/* Виджет Задач */}
            <Widget
              title="Задачи"
              icon={<CheckSquare className="w-5 h-5" />}
              gradient="orange"
              onExpand={() => router.push('/tasks')}
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-text-muted">Активных задач:</span>
                  <span className="text-2xl font-bold text-accent-orange">
                    {activeTasks.length}
                  </span>
                </div>
                <div className="space-y-2">
                  {activeTasks.slice(0, 3).map((task, idx) => (
                    <div key={idx} className="p-2 rounded-lg bg-white/5 border border-white/10">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-accent-orange animate-pulse" />
                        <span className="text-xs text-text-secondary truncate">
                          {task.task_id?.slice(0, 8) || 'Task'}
                        </span>
                      </div>
                    </div>
                  ))}
                  {activeTasks.length === 0 && (
                    <p className="text-xs text-text-muted italic">Нет активных задач</p>
                  )}
                </div>
                <button
                  onClick={() => router.push('/tasks')}
                  className="w-full px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-accent-orange/50 text-sm font-medium transition-all"
                >
                  Управление задачами
                </button>
              </div>
            </Widget>

            {/* Виджет Автономного Лога */}
            <Widget
              title="Автономный лог"
              icon={<Zap className="w-5 h-5" />}
              gradient="combo"
              onExpand={() => router.push('/autonomous')}
            >
              <div className="space-y-3">
                <div className="space-y-2 max-h-[200px] overflow-y-auto custom-scrollbar">
                  {recentLogs.map((log, idx) => (
                    <div key={idx} className="p-2 rounded-lg bg-white/5 border border-white/10">
                      <div className="flex items-start gap-2">
                        <div className={`
                          w-2 h-2 rounded-full mt-1 flex-shrink-0
                          ${log.level === 'error' ? 'bg-red-400' : ''}
                          ${log.level === 'warning' ? 'bg-yellow-400' : ''}
                          ${log.level === 'success' ? 'bg-green-400' : ''}
                          ${log.level === 'info' ? 'bg-blue-400' : ''}
                          ${log.level === 'debug' ? 'bg-gray-400' : ''}
                        `} />
                        <div className="flex-1 min-w-0">
                          <p className="text-xs text-text-secondary truncate">
                            {log.message}
                          </p>
                          <p className="text-[10px] text-text-muted">
                            {new Date(log.timestamp).toLocaleTimeString('ru-RU')}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                  {recentLogs.length === 0 && (
                    <p className="text-xs text-text-muted italic">Нет событий</p>
                  )}
                </div>
                <button
                  onClick={() => router.push('/autonomous')}
                  className="w-full px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-primary-purple/50 text-sm font-medium transition-all"
                >
                  Полный лог
                </button>
              </div>
            </Widget>

            {/* Виджет Системной Статистики */}
            <Widget
              title="Система"
              icon={<Activity className="w-5 h-5" />}
              gradient="purple"
            >
              <div className="space-y-4">
                {stats ? (
                  <>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                        <p className="text-xs text-text-muted mb-1">GPU</p>
                        <p className="text-lg font-bold text-primary-purple">
                          {stats.gpu_count}x
                        </p>
                      </div>
                      <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                        <p className="text-xs text-text-muted mb-1">Память</p>
                        <p className="text-lg font-bold text-primary-purple">
                          {stats.total_memory_gb}GB
                        </p>
                      </div>
                    </div>
                    
                    {stats.gpu_utilization !== undefined && (
                      <div>
                        <div className="flex justify-between text-xs text-text-muted mb-2">
                          <span>Загрузка GPU</span>
                          <span>{stats.gpu_utilization}%</span>
                        </div>
                        <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-purple transition-all duration-500"
                            style={{ width: `${stats.gpu_utilization}%` }}
                          />
                        </div>
                      </div>
                    )}

                    {stats.memory_used_gb !== undefined && stats.total_memory_gb && (
                      <div>
                        <div className="flex justify-between text-xs text-text-muted mb-2">
                          <span>Использование памяти</span>
                          <span>{Math.round((stats.memory_used_gb / stats.total_memory_gb) * 100)}%</span>
                        </div>
                        <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-orange transition-all duration-500"
                            style={{ width: `${(stats.memory_used_gb / stats.total_memory_gb) * 100}%` }}
                          />
                        </div>
                      </div>
                    )}

                    <div className="flex items-center justify-between pt-2 border-t border-white/10">
                      <span className="text-xs text-text-muted">Uptime</span>
                      <span className="text-sm font-medium text-text-secondary">
                        {stats.uptime_hours.toFixed(1)}h
                      </span>
                    </div>
                  </>
                ) : (
                  <p className="text-sm text-text-muted italic">Загрузка статистики...</p>
                )}
              </div>
            </Widget>

            {/* Виджет Файлов */}
            <Widget
              title="Файлы"
              icon={<FolderOpen className="w-5 h-5" />}
              gradient="orange"
              onExpand={() => router.push('/files')}
            >
              <div className="space-y-3">
                <p className="text-sm text-text-muted mb-4">
                  Управление файлами workspace
                </p>
                <button
                  onClick={() => router.push('/files')}
                  className="w-full px-4 py-3 rounded-lg bg-gradient-orange text-white font-medium hover:shadow-glow-orange-md transition-all"
                >
                  Открыть файлы
                </button>
              </div>
            </Widget>

            {/* Виджет Фриланса */}
            <Widget
              title="Фриланс"
              icon={<Briefcase className="w-5 h-5" />}
              gradient="combo"
              onExpand={() => router.push('/freelance')}
            >
              <div className="space-y-3">
                <p className="text-sm text-text-muted mb-4">
                  Kanban-доска и мониторинг проектов
                </p>
                <div className="grid grid-cols-2 gap-2">
                  <div className="p-2 rounded-lg bg-white/5 border border-white/10 text-center">
                    <p className="text-xs text-text-muted">Активных</p>
                    <p className="text-lg font-bold text-primary-purple">0</p>
                  </div>
                  <div className="p-2 rounded-lg bg-white/5 border border-white/10 text-center">
                    <p className="text-xs text-text-muted">Завершено</p>
                    <p className="text-lg font-bold text-accent-orange">0</p>
                  </div>
                </div>
                <button
                  onClick={() => router.push('/freelance')}
                  className="w-full px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-primary-purple/50 text-sm font-medium transition-all"
                >
                  Открыть доску
                </button>
              </div>
            </Widget>

          </div>

          {/* Футер */}
          <footer className="mt-12 text-center animate-fade-in">
            <div className="inline-block px-6 py-3 rounded-full bg-bg-secondary/80 border border-white/10">
              <p className="text-xs text-text-muted">
                EDIS © 2026 | Powered by Dual Qwen Brain | 
                <span className="gradient-text-combo font-medium ml-1">Made with 💜🧡 by Alya</span>
              </p>
            </div>
          </footer>
        </div>
      </div>

      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 2px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(139, 92, 246, 0.5);
          border-radius: 2px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(139, 92, 246, 0.7);
        }
      `}</style>
    </>
  );
}
