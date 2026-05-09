import React from 'react';
import { Cpu, HardDrive, Activity, Clock } from 'lucide-react';

export interface SystemStats {
  gpu_count: number;
  total_memory_gb: number;
  active_tasks: number;
  uptime_hours: number;
  gpu_utilization?: number;
  memory_used_gb?: number;
}

interface SystemStatsProps {
  stats: SystemStats | null;
}

export default function SystemStatsComponent({ stats }: SystemStatsProps) {
  const formatUptime = (hours: number) => {
    const days = Math.floor(hours / 24);
    const remainingHours = Math.floor(hours % 24);
    const minutes = Math.floor((hours % 1) * 60);
    
    if (days > 0) {
      return `${days}d ${remainingHours}h`;
    } else if (remainingHours > 0) {
      return `${remainingHours}h ${minutes}m`;
    } else {
      return `${minutes}m`;
    }
  };

  const getUtilizationColor = (utilization: number) => {
    if (utilization >= 80) return 'text-accent-pink';
    if (utilization >= 50) return 'text-accent-orange';
    return 'text-accent-green';
  };

  const getUtilizationGradient = (utilization: number) => {
    if (utilization >= 80) return 'from-accent-pink to-accent-orange';
    if (utilization >= 50) return 'from-accent-orange to-accent-green';
    return 'from-accent-green to-accent-cyan';
  };

  if (!stats) {
    return (
      <div className="glass-card p-6 animate-slide-up">
        <div className="flex items-center gap-3 mb-4">
          <Activity className="w-5 h-5 text-accent-purple" />
          <h3 className="text-lg font-semibold gradient-text">System Stats</h3>
        </div>
        <div className="text-center py-8 text-text-muted">
          <Activity className="w-12 h-12 mx-auto mb-3 opacity-30 animate-pulse-soft" />
          <p className="text-sm">Loading system statistics...</p>
        </div>
      </div>
    );
  }

  const gpuUtilization = stats.gpu_utilization || 0;
  const memoryUsed = stats.memory_used_gb || 0;
  const memoryUtilization = (memoryUsed / stats.total_memory_gb) * 100;

  return (
    <div className="glass-card p-6 space-y-4 animate-slide-up">
      {/* Header */}
      <div className="flex items-center gap-3 mb-2">
        <Activity className="w-5 h-5 text-accent-purple" />
        <h3 className="text-lg font-semibold gradient-text">System Stats</h3>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4">
        
        {/* GPU Count */}
        <div className="glass-card p-4 rounded-xl hover:bg-glass-hover transition-all duration-300">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-gradient-button rounded-lg">
              <Cpu className="w-4 h-4 text-white" />
            </div>
            <span className="text-xs text-text-muted">GPU Count</span>
          </div>
          <p className="text-2xl font-bold text-text-primary">
            {stats.gpu_count}
          </p>
          <p className="text-xs text-text-secondary mt-1">
            H200 GPUs
          </p>
        </div>

        {/* Memory */}
        <div className="glass-card p-4 rounded-xl hover:bg-glass-hover transition-all duration-300">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-gradient-button rounded-lg">
              <HardDrive className="w-4 h-4 text-white" />
            </div>
            <span className="text-xs text-text-muted">Memory</span>
          </div>
          <p className="text-2xl font-bold text-text-primary">
            {stats.total_memory_gb}GB
          </p>
          <p className="text-xs text-text-secondary mt-1">
            Total VRAM
          </p>
        </div>

        {/* Active Tasks */}
        <div className="glass-card p-4 rounded-xl hover:bg-glass-hover transition-all duration-300">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-gradient-button rounded-lg">
              <Activity className="w-4 h-4 text-white" />
            </div>
            <span className="text-xs text-text-muted">Active Tasks</span>
          </div>
          <p className="text-2xl font-bold text-text-primary">
            {stats.active_tasks}
          </p>
          <p className="text-xs text-text-secondary mt-1">
            In progress
          </p>
        </div>

        {/* Uptime */}
        <div className="glass-card p-4 rounded-xl hover:bg-glass-hover transition-all duration-300">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-gradient-button rounded-lg">
              <Clock className="w-4 h-4 text-white" />
            </div>
            <span className="text-xs text-text-muted">Uptime</span>
          </div>
          <p className="text-2xl font-bold text-text-primary">
            {formatUptime(stats.uptime_hours)}
          </p>
          <p className="text-xs text-text-secondary mt-1">
            System running
          </p>
        </div>
      </div>

      {/* Utilization Bars */}
      {(gpuUtilization > 0 || memoryUsed > 0) && (
        <div className="space-y-3 pt-2">
          
          {/* GPU Utilization */}
          {gpuUtilization > 0 && (
            <div className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-text-secondary">GPU Utilization</span>
                <span className={`font-medium ${getUtilizationColor(gpuUtilization)}`}>
                  {gpuUtilization.toFixed(1)}%
                </span>
              </div>
              <div className="h-2 bg-glass-light rounded-full overflow-hidden">
                <div
                  className={`h-full bg-gradient-to-r ${getUtilizationGradient(gpuUtilization)} transition-all duration-500`}
                  style={{ width: `${gpuUtilization}%` }}
                />
              </div>
            </div>
          )}

          {/* Memory Utilization */}
          {memoryUsed > 0 && (
            <div className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-text-secondary">Memory Usage</span>
                <span className={`font-medium ${getUtilizationColor(memoryUtilization)}`}>
                  {memoryUsed.toFixed(1)}GB / {stats.total_memory_gb}GB
                </span>
              </div>
              <div className="h-2 bg-glass-light rounded-full overflow-hidden">
                <div
                  className={`h-full bg-gradient-to-r ${getUtilizationGradient(memoryUtilization)} transition-all duration-500`}
                  style={{ width: `${memoryUtilization}%` }}
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
