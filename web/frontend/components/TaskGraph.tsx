/**
 * TaskGraph Component
 * Визуализация графа задач с использованием ReactFlow
 */

import React, { useCallback, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  ConnectionMode,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';

interface SubTask {
  id: string;
  title: string;
  description: string;
  type: string;
  status: string;
  priority: string;
  dependencies: string[];
  estimated_time?: number;
  assigned_agent?: string;
}

interface TaskGraphData {
  task_id: string;
  original_task: string;
  subtasks: SubTask[];
  total_subtasks: number;
  estimated_total_time: number;
}

interface TaskGraphProps {
  graphData: TaskGraphData | null;
  onNodeClick?: (nodeId: string) => void;
}

export default function TaskGraph({ graphData, onNodeClick }: TaskGraphProps) {
  // Преобразование данных в формат ReactFlow
  const { nodes: initialNodes, edges: initialEdges } = useMemo(() => {
    if (!graphData || !graphData.subtasks) {
      return { nodes: [], edges: [] };
    }

    const nodes: Node[] = [];
    const edges: Edge[] = [];
    const levelMap = new Map<string, number>();

    // Вычисление уровней для layout
    const calculateLevel = (taskId: string, visited = new Set<string>()): number => {
      if (visited.has(taskId)) return 0;
      visited.add(taskId);

      const task = graphData.subtasks.find(t => t.id === taskId);
      if (!task || task.dependencies.length === 0) return 0;

      const depLevels = task.dependencies.map(depId => calculateLevel(depId, visited));
      return Math.max(...depLevels) + 1;
    };

    // Вычисляем уровни для всех задач
    graphData.subtasks.forEach(task => {
      levelMap.set(task.id, calculateLevel(task.id));
    });

    // Группируем задачи по уровням
    const levelGroups = new Map<number, SubTask[]>();
    graphData.subtasks.forEach(task => {
      const level = levelMap.get(task.id) || 0;
      if (!levelGroups.has(level)) {
        levelGroups.set(level, []);
      }
      levelGroups.get(level)!.push(task);
    });

    // Создаем узлы с позиционированием
    const levelWidth = 350;
    const nodeHeight = 120;
    const verticalSpacing = 150;

    graphData.subtasks.forEach(task => {
      const level = levelMap.get(task.id) || 0;
      const tasksInLevel = levelGroups.get(level) || [];
      const indexInLevel = tasksInLevel.indexOf(task);
      const totalInLevel = tasksInLevel.length;

      // Центрируем узлы в уровне
      const yOffset = (indexInLevel - (totalInLevel - 1) / 2) * verticalSpacing;

      // Цвета в зависимости от статуса
      let bgColor = '#1a1a1a';
      let borderColor = '#374151';
      let textColor = '#9ca3af';

      switch (task.status) {
        case 'completed':
          bgColor = '#065f46';
          borderColor = '#10b981';
          textColor = '#d1fae5';
          break;
        case 'in_progress':
          bgColor = '#7c2d12';
          borderColor = '#f97316';
          textColor = '#fed7aa';
          break;
        case 'failed':
          bgColor = '#7f1d1d';
          borderColor = '#ef4444';
          textColor = '#fecaca';
          break;
        case 'pending':
          bgColor = '#1e1b4b';
          borderColor = '#8b5cf6';
          textColor = '#ddd6fe';
          break;
      }

      // Иконка приоритета
      let priorityIcon = '●';
      switch (task.priority) {
        case 'critical':
          priorityIcon = '🔴';
          break;
        case 'high':
          priorityIcon = '🟠';
          break;
        case 'medium':
          priorityIcon = '🟡';
          break;
        case 'low':
          priorityIcon = '🟢';
          break;
      }

      nodes.push({
        id: task.id,
        type: 'default',
        position: { x: level * levelWidth, y: yOffset },
        data: {
          label: (
            <div className="p-3 min-w-[280px]">
              <div className="flex items-start justify-between gap-2 mb-2">
                <div className="font-semibold text-sm leading-tight flex-1">
                  {task.title}
                </div>
                <span className="text-xs">{priorityIcon}</span>
              </div>
              <div className="text-xs opacity-70 mb-2 line-clamp-2">
                {task.description}
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="px-2 py-0.5 rounded bg-black/30">
                  {task.type}
                </span>
                {task.estimated_time && (
                  <span className="opacity-60">
                    ~{task.estimated_time}м
                  </span>
                )}
              </div>
            </div>
          ),
        },
        style: {
          background: bgColor,
          border: `2px solid ${borderColor}`,
          borderRadius: '12px',
          color: textColor,
          fontSize: '13px',
          padding: 0,
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
        },
      });

      // Создаем рёбра для зависимостей
      task.dependencies.forEach(depId => {
        edges.push({
          id: `${depId}-${task.id}`,
          source: depId,
          target: task.id,
          type: 'smoothstep',
          animated: task.status === 'in_progress',
          style: {
            stroke: task.status === 'in_progress' ? '#f97316' : '#4b5563',
            strokeWidth: 2,
          },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: task.status === 'in_progress' ? '#f97316' : '#4b5563',
          },
        });
      });
    });

    return { nodes, edges };
  }, [graphData]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const handleNodeClick = useCallback(
    (event: React.MouseEvent, node: Node) => {
      if (onNodeClick) {
        onNodeClick(node.id);
      }
    },
    [onNodeClick]
  );

  if (!graphData) {
    return (
      <div className="flex items-center justify-center h-full bg-bg-primary rounded-xl border border-white/5">
        <div className="text-center">
          <div className="text-4xl mb-4">📊</div>
          <div className="text-text-secondary">
            Граф задач появится после декомпозиции
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full bg-bg-primary rounded-xl border border-white/5 overflow-hidden">
      {/* Заголовок */}
      <div className="px-4 py-3 border-b border-white/5 bg-bg-secondary/50">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-white">Граф задач</h3>
            <p className="text-xs text-text-secondary mt-0.5">
              {graphData.total_subtasks} подзадач • ~{graphData.estimated_total_time}м
            </p>
          </div>
          <div className="flex items-center gap-3 text-xs">
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-full bg-purple-500/20 border border-purple-500"></div>
              <span className="text-text-secondary">Ожидает</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-full bg-orange-500/20 border border-orange-500"></div>
              <span className="text-text-secondary">В работе</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-full bg-green-500/20 border border-green-500"></div>
              <span className="text-text-secondary">Завершено</span>
            </div>
          </div>
        </div>
      </div>

      {/* ReactFlow Canvas */}
      <div className="h-[calc(100%-60px)]">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={handleNodeClick}
          connectionMode={ConnectionMode.Strict}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.1}
          maxZoom={1.5}
          defaultEdgeOptions={{
            type: 'smoothstep',
          }}
          proOptions={{ hideAttribution: true }}
        >
          <Background
            color="#374151"
            gap={16}
            size={1}
            style={{ backgroundColor: '#0d0d0d' }}
          />
          <Controls
            style={{
              background: '#1a1a1a',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '8px',
            }}
          />
          <MiniMap
            nodeColor={(node) => {
              const status = graphData.subtasks.find(t => t.id === node.id)?.status;
              switch (status) {
                case 'completed': return '#10b981';
                case 'in_progress': return '#f97316';
                case 'failed': return '#ef4444';
                default: return '#8b5cf6';
              }
            }}
            style={{
              background: '#1a1a1a',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '8px',
            }}
            maskColor="rgba(0, 0, 0, 0.6)"
          />
        </ReactFlow>
      </div>
    </div>
  );
}
