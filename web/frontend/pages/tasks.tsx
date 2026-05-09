/**
 * Tasks Management Page
 * Страница управления задачами с поддержкой Task Graph
 */

import React, { useEffect, useState, useCallback } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import {
  ArrowLeft,
  CheckSquare,
  Clock,
  AlertCircle,
  CheckCircle,
  XCircle,
  Loader,
  Plus,
  Trash2,
  Network,
  Settings as SettingsIcon
} from 'lucide-react';
import EDISClient, { TaskStatus } from '../lib/edis-client';
import Settings from '../components/Settings';
import SettingsPanel from '../components/SettingsPanel';
import TaskGraph from '../components/TaskGraph';

interface Task {
  task_id: string;
  status: string;
  result?: string;
  error?: string;
  created_at?: string;
  graph?: any;
}

interface TaskDetails extends Task {
  graph?: {
    task_id: string;
    original_task: string;
    subtasks: Array<{
      id: string;
      title: string;
      description: string;
      type: string;
      status: string;
      priority: string;
      dependencies: string[];
      estimated_time?: number;
      assigned_agent?: string;
    }>;
    total_subtasks: number;
    estimated_total_time: number;
  };
}

export default function TasksPage() {
  const [serverUrl, setServerUrl] = useState('http://localhost:8000');
  const [apiKey, setApiKey] = useState('your-api-key-here');
  const [client, setClient] = useState<EDISClient>(() => new EDISClient('http://localhost:8000', 'your-api-key-here'));
  const [isConnected, setIsConnected] = useState(false);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedTask, setSelectedTask] = useState<TaskDetails | null>(null);
  const [newTask, setNewTask] = useState('');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high' | 'critical'>('medium');
  const [useGraph, setUseGraph] = useState(false);
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
        loadTasks(client);
      }
    }).catch(() => {
      setIsConnected(false);
    });
  }, [client, serverUrl, apiKey]);

  useEffect(() => {
    if (!isConnected) return;
    const interval = setInterval(() => {
      loadTasks(client);
      // Обновляем детали выбранной задачи
      if (selectedTask) {
        loadTaskDetails(client, selectedTask.task_id);
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [client, isConnected, selectedTask]);

  const loadTasks = async (edisClient: EDISClient) => {
    try {
      const taskList = await edisClient.listTasks();
      setTasks(taskList);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    }
  };

  const loadTaskDetails = async (edisClient: EDISClient, taskId: string) => {
    try {
      const details = await edisClient.getTaskStatus(taskId);
      setSelectedTask(details as TaskDetails);
    } catch (error) {
      console.error('Failed to load task details:', error);
    }
  };

  const handleCreateTask = async () => {
    if (!client || !newTask.trim()) return;

    try {
      await client.createTask({
        task: newTask,
        priority,
        use_task_graph: useGraph
      });
      setNewTask('');
      loadTasks(client);
    } catch (error) {
      console.error('Failed to create task:', error);
    }
  };

  const handleSelectTask = async (task: Task) => {
    if (!client) return;
    await loadTaskDetails(client, task.task_id);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-400" />;
      case 'running':
        return <Loader className="w-5 h-5 text-primary-purple animate-spin" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-accent-orange" />;
      default:
        return <AlertCircle className="w-5 h-5 text-text-muted" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'border-green-400/30 bg-green-400/10';
      case 'failed':
        return 'border-red-400/30 bg-red-400/10';
      case 'running':
        return 'border-primary-purple/30 bg-primary-purple/10';
      case 'pending':
        return 'border-accent-orange/30 bg-accent-orange/10';
      default:
        return 'border-white/10 bg-white/5';
    }
  };

  return (
    <>
      <Head>
        <title>Задачи - EDIS</title>
        <meta name="description" content="Управление задачами EDIS" />
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
              <CheckSquare className="w-6 h-6 text-accent-orange" />
              <span className="text-xl font-bold gradient-text-combo">
                Управление задачами
              </span>
            </div>
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
      </nav>

      <div className="min-h-screen bg-bg-primary p-6">
        <div className="max-w-[1920px] mx-auto">
          
          {/* Создание новой задачи */}
          <div className="mb-6 p-6 rounded-xl bg-bg-secondary/80 backdrop-blur-md border border-white/5 shadow-card animate-fade-in">
            <h2 className="text-lg font-bold text-text-primary mb-4 flex items-center gap-2">
              <Plus className="w-5 h-5 text-primary-purple" />
              Создать новую задачу
            </h2>
            
            <div className="space-y-4">
              <textarea
                value={newTask}
                onChange={(e) => setNewTask(e.target.value)}
                placeholder="Опишите задачу..."
                className="w-full px-4 py-3 rounded-lg bg-bg-primary border border-white/10 focus:border-primary-purple/50 text-text-primary placeholder-text-muted resize-none focus:outline-none transition-colors"
                rows={3}
                disabled={!isConnected}
              />
              
              <div className="flex items-center gap-4 flex-wrap">
                <div className="flex items-center gap-2">
                  <label className="text-sm text-text-secondary">Приоритет:</label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value as any)}
                    className="px-3 py-2 rounded-lg bg-bg-primary border border-white/10 text-text-primary text-sm focus:outline-none focus:border-primary-purple/50"
                    disabled={!isConnected}
                  >
                    <option value="low">Низкий</option>
                    <option value="medium">Средний</option>
                    <option value="high">Высокий</option>
                    <option value="critical">Критический</option>
                  </select>
                </div>

                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={useGraph}
                    onChange={(e) => setUseGraph(e.target.checked)}
                    className="w-4 h-4 rounded border-white/10 bg-bg-primary text-primary-purple focus:ring-primary-purple"
                    disabled={!isConnected}
                  />
                  <span className="text-sm text-text-secondary flex items-center gap-1.5">
                    <Network className="w-4 h-4" />
                    Использовать Task Graph
                  </span>
                </label>

                <button
                  onClick={handleCreateTask}
                  disabled={!isConnected || !newTask.trim()}
                  className="ml-auto px-6 py-2 rounded-lg bg-gradient-combo text-white font-medium hover:shadow-glow-purple-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Создать задачу
                </button>
              </div>
            </div>
          </div>

          {/* Список задач и детали */}
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
            {/* Левая колонка - список задач */}
            <div className="xl:col-span-1 space-y-4">
              <h2 className="text-lg font-bold text-text-primary mb-4">
                Все задачи ({tasks.length})
              </h2>
              
              {tasks.length === 0 ? (
                <div className="p-8 rounded-xl bg-bg-secondary/80 border border-white/5 text-center">
                  <CheckSquare className="w-12 h-12 text-text-muted mx-auto mb-3 opacity-50" />
                  <p className="text-text-muted">Нет задач</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-[calc(100vh-300px)] overflow-y-auto custom-scrollbar">
                  {tasks.map((task) => (
                    <div
                      key={task.task_id}
                      onClick={() => handleSelectTask(task)}
                      className={`
                        p-4 rounded-xl border cursor-pointer transition-all
                        ${getStatusColor(task.status)}
                        ${selectedTask?.task_id === task.task_id ? 'ring-2 ring-primary-purple' : ''}
                        hover:scale-[1.02]
                      `}
                    >
                      <div className="flex items-start gap-3">
                        {getStatusIcon(task.status)}
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-mono text-text-secondary truncate">
                            {task.task_id}
                          </p>
                          <p className="text-xs text-text-muted mt-1">
                            Статус: <span className="font-medium">{task.status}</span>
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Правая колонка - детали и граф */}
            <div className="xl:col-span-2 space-y-6">
              {selectedTask ? (
                <>
                  {/* Детали задачи */}
                  <div className="p-6 rounded-xl bg-bg-secondary/80 backdrop-blur-md border border-white/5 shadow-card animate-fade-in">
                    <div className="flex items-center justify-between mb-4">
                      <h2 className="text-lg font-bold text-text-primary">Детали задачи</h2>
                      {getStatusIcon(selectedTask.status)}
                    </div>

                    <div className="space-y-4">
                      <div>
                        <label className="text-xs text-text-muted uppercase tracking-wide">Task ID</label>
                        <p className="text-sm font-mono text-text-secondary mt-1 p-2 rounded bg-bg-primary border border-white/10">
                          {selectedTask.task_id}
                        </p>
                      </div>

                      <div>
                        <label className="text-xs text-text-muted uppercase tracking-wide">Статус</label>
                        <p className={`text-sm font-medium mt-1 p-2 rounded border ${getStatusColor(selectedTask.status)}`}>
                          {selectedTask.status}
                        </p>
                      </div>

                      {selectedTask.result && (
                        <div>
                          <label className="text-xs text-text-muted uppercase tracking-wide">Результат</label>
                          <div className="mt-1 p-3 rounded-lg bg-bg-primary border border-white/10 max-h-[200px] overflow-y-auto custom-scrollbar">
                            <pre className="text-xs text-text-secondary whitespace-pre-wrap font-mono">
                              {selectedTask.result}
                            </pre>
                          </div>
                        </div>
                      )}

                      {selectedTask.error && (
                        <div>
                          <label className="text-xs text-text-muted uppercase tracking-wide">Ошибка</label>
                          <div className="mt-1 p-3 rounded-lg bg-red-400/10 border border-red-400/30">
                            <pre className="text-xs text-red-400 whitespace-pre-wrap font-mono">
                              {selectedTask.error}
                            </pre>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Task Graph */}
                  {selectedTask.graph && (
                    <div className="h-[600px] animate-fade-in">
                      <TaskGraph 
                        graphData={selectedTask.graph}
                        onNodeClick={(nodeId) => {
                          console.log('Clicked node:', nodeId);
                        }}
                      />
                    </div>
                  )}
                </>
              ) : (
                <div className="p-8 rounded-xl bg-bg-secondary/80 border border-white/5 text-center">
                  <AlertCircle className="w-12 h-12 text-text-muted mx-auto mb-3 opacity-50" />
                  <p className="text-text-muted">Выберите задачу для просмотра деталей</p>
                </div>
              )}
            </div>
          </div>
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
