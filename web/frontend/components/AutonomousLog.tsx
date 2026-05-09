/**
 * Enhanced Autonomous Log Component
 * Стиль временной ленты событий (Timeline)
 */

import React, { useEffect, useRef } from 'react';
import { Terminal, AlertCircle, CheckCircle, Info, AlertTriangle, Zap } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export interface LogMessage {
  timestamp: string;
  level: 'info' | 'success' | 'warning' | 'error' | 'debug';
  message: string;
  source?: string;
}

interface AutonomousLogProps {
  logs: LogMessage[];
  maxLogs?: number;
  enableStreaming?: boolean;
}

export default function AutonomousLog({ 
  logs, 
  maxLogs = 100,
  enableStreaming = true 
}: AutonomousLogProps) {
  const logContainerRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = React.useState(true);
  const [filter, setFilter] = React.useState<string>('all');

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  // Handle scroll to detect if user scrolled up
  const handleScroll = () => {
    if (logContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = logContainerRef.current;
      const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
      setAutoScroll(isAtBottom);
    }
  };

  const getLogIcon = (level: string) => {
    switch (level) {
      case 'success':
        return <CheckCircle className="w-5 h-5" />;
      case 'error':
        return <AlertCircle className="w-5 h-5" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5" />;
      case 'debug':
        return <Terminal className="w-5 h-5" />;
      default:
        return <Info className="w-5 h-5" />;
    }
  };

  const getLogColors = (level: string) => {
    switch (level) {
      case 'success':
        return {
          bg: 'bg-green-500/10',
          border: 'border-green-500/30',
          icon: 'text-green-400',
          glow: 'shadow-glow-green'
        };
      case 'error':
        return {
          bg: 'bg-red-500/10',
          border: 'border-red-500/30',
          icon: 'text-red-400',
          glow: 'shadow-glow-red'
        };
      case 'warning':
        return {
          bg: 'bg-yellow-500/10',
          border: 'border-yellow-500/30',
          icon: 'text-yellow-400',
          glow: 'shadow-glow-yellow'
        };
      case 'debug':
        return {
          bg: 'bg-purple-500/10',
          border: 'border-purple-500/30',
          icon: 'text-purple-400',
          glow: 'shadow-glow-purple'
        };
      default:
        return {
          bg: 'bg-blue-500/10',
          border: 'border-blue-500/30',
          icon: 'text-blue-400',
          glow: 'shadow-glow'
        };
    }
  };

  const filteredLogs = filter === 'all' 
    ? logs 
    : logs.filter(log => log.level === filter);
  
  const displayLogs = filteredLogs.slice(-maxLogs);

  return (
    <div className="h-full flex flex-col bg-bg-primary rounded-2xl border border-border-subtle overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-border-subtle bg-bg-secondary/50 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-accent-primary/20">
            <Zap className="w-5 h-5 text-accent-primary" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-text-primary">Autonomous Activity</h3>
            <p className="text-xs text-text-secondary">
              {displayLogs.length} {displayLogs.length === 1 ? 'event' : 'events'}
              {enableStreaming && <span className="ml-2 text-accent-primary">● Live</span>}
            </p>
          </div>
        </div>

        {/* Filter Buttons */}
        <div className="flex items-center gap-2">
          {['all', 'info', 'success', 'warning', 'error', 'debug'].map((level) => (
            <button
              key={level}
              onClick={() => setFilter(level)}
              className={`px-3 py-1.5 text-xs rounded-lg transition-all ${
                filter === level
                  ? 'bg-accent-primary text-white shadow-glow'
                  : 'bg-bg-primary text-text-secondary hover:bg-message-user/30 hover:text-text-primary'
              }`}
            >
              {level.charAt(0).toUpperCase() + level.slice(1)}
            </button>
          ))}
        </div>

        {!autoScroll && (
          <button
            onClick={() => {
              setAutoScroll(true);
              if (logContainerRef.current) {
                logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
              }
            }}
            className="ml-4 px-3 py-1.5 text-xs bg-accent-primary hover:bg-accent-hover text-white rounded-lg transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
            Jump to Latest
          </button>
        )}
      </div>

      {/* Timeline Container */}
      <div
        ref={logContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto px-6 py-4 scrollbar-thin scrollbar-thumb-glass-border scrollbar-track-transparent"
      >
        {displayLogs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-text-secondary">
            <div className="p-6 rounded-full bg-bg-secondary/50 mb-4">
              <Terminal className="w-12 h-12 opacity-50" />
            </div>
            <p className="text-sm font-medium mb-1">No Activity Yet</p>
            <p className="text-xs text-text-muted">Waiting for autonomous events...</p>
          </div>
        ) : (
          <div className="relative">
            {/* Timeline Line */}
            <div className="absolute left-[22px] top-0 bottom-0 w-0.5 bg-gradient-to-b from-accent-primary via-accent-secondary to-transparent opacity-30" />

            {/* Log Entries */}
            <div className="space-y-4">
              {displayLogs.map((log, index) => {
                const colors = getLogColors(log.level);
                return (
                  <div
                    key={index}
                    className="relative pl-14 animate-fade-in"
                    style={{ animationDelay: `${index * 0.05}s` }}
                  >
                    {/* Timeline Dot */}
                    <div className={`absolute left-0 top-2 p-2.5 rounded-full ${colors.bg} ${colors.border} border-2 ${colors.glow}`}>
                      <div className={colors.icon}>
                        {getLogIcon(log.level)}
                      </div>
                    </div>

                    {/* Log Card */}
                    <div className={`
                      ${colors.bg} ${colors.border} border backdrop-blur-sm rounded-xl p-4
                      hover:scale-[1.01] transition-all duration-200 group
                    `}>
                      {/* Header */}
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-mono text-text-secondary">
                            {new Date(log.timestamp).toLocaleTimeString('ru-RU', {
                              hour: '2-digit',
                              minute: '2-digit',
                              second: '2-digit'
                            })}
                          </span>
                          {log.source && (
                            <>
                              <span className="text-xs text-text-muted">•</span>
                              <span className={`text-xs font-medium ${colors.icon}`}>
                                {log.source}
                              </span>
                            </>
                          )}
                        </div>
                        <span className={`text-xs font-semibold uppercase tracking-wider ${colors.icon}`}>
                          {log.level}
                        </span>
                      </div>

                      {/* Message */}
                      <div className="text-sm text-text-primary leading-relaxed prose prose-invert prose-sm max-w-none">
                        <ReactMarkdown
                          components={{
                            code: ({ node, className, children, ...props }: any) => {
                              const isInline = !className;
                              return isInline ? (
                                <code className="px-1.5 py-0.5 bg-message-user/30 rounded text-accent-primary font-mono text-xs" {...props}>
                                  {children}
                                </code>
                              ) : (
                                <pre className="bg-bg-primary/50 rounded-lg p-3 overflow-x-auto my-2">
                                  <code className="text-xs font-mono" {...props}>
                                    {children}
                                  </code>
                                </pre>
                              );
                            },
                            p: ({ children }) => <p className="mb-0">{children}</p>,
                            a: ({ href, children }) => (
                              <a 
                                href={href} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="text-accent-primary hover:text-accent-hover underline"
                              >
                                {children}
                              </a>
                            ),
                          }}
                        >
                          {log.message}
                        </ReactMarkdown>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Footer Stats */}
      <div className="px-6 py-3 border-t border-border-subtle bg-bg-secondary/30 backdrop-blur-sm">
        <div className="flex items-center justify-between text-xs text-text-secondary">
          <div className="flex items-center gap-4">
            <span>Total: {logs.length}</span>
            <span className="text-green-400">✓ {logs.filter(l => l.level === 'success').length}</span>
            <span className="text-red-400">✗ {logs.filter(l => l.level === 'error').length}</span>
            <span className="text-yellow-400">⚠ {logs.filter(l => l.level === 'warning').length}</span>
          </div>
          <div className="flex items-center gap-2">
            {enableStreaming && (
              <span className="flex items-center gap-1.5 text-accent-primary">
                <span className="w-2 h-2 bg-accent-primary rounded-full animate-pulse"></span>
                Streaming
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
