import React, { useState } from 'react';
import { Send, Zap, AlertCircle } from 'lucide-react';

interface TaskInputProps {
  onSubmit: (task: string, priority: string, useGraph: boolean) => void;
  disabled?: boolean;
}

export default function TaskInput({ onSubmit, disabled = false }: TaskInputProps) {
  const [task, setTask] = useState('');
  const [priority, setPriority] = useState('normal');
  const [useGraph, setUseGraph] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!task.trim() || disabled || isSubmitting) return;
    
    setIsSubmitting(true);
    
    try {
      await onSubmit(task, priority, useGraph);
      setTask(''); // Clear input after successful submission
    } catch (error) {
      console.error('Failed to submit task:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const priorityOptions = [
    { value: 'low', label: 'Low', color: 'text-accent-cyan' },
    { value: 'normal', label: 'Normal', color: 'text-accent-blue' },
    { value: 'high', label: 'High', color: 'text-accent-orange' },
    { value: 'critical', label: 'Critical', color: 'text-accent-pink' },
  ];

  return (
    <div className="glass-card p-6 space-y-4 animate-slide-up">
      {/* Header */}
      <div className="flex items-center gap-3 mb-2">
        <Zap className="w-5 h-5 text-accent-purple" />
        <h3 className="text-lg font-semibold gradient-text">New Task</h3>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        
        {/* Task Input */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-text-secondary">
            Task Description
          </label>
          <textarea
            value={task}
            onChange={(e) => setTask(e.target.value)}
            placeholder="Describe your task here..."
            rows={4}
            disabled={disabled || isSubmitting}
            className="w-full px-4 py-3 glass-input resize-none"
          />
        </div>

        {/* Priority Selector */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-text-secondary">
            Priority Level
          </label>
          <div className="grid grid-cols-4 gap-2">
            {priorityOptions.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => setPriority(option.value)}
                disabled={disabled || isSubmitting}
                className={`
                  px-3 py-2 rounded-lg text-sm font-medium transition-all duration-300
                  ${priority === option.value
                    ? 'bg-gradient-button text-white shadow-glow-sm'
                    : 'glass-card hover:bg-glass-hover'
                  }
                  ${option.color}
                  disabled:opacity-50 disabled:cursor-not-allowed
                `}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {/* Task Graph Toggle */}
        <div className="flex items-center justify-between p-3 glass-card rounded-lg">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-accent-cyan" />
            <span className="text-sm text-text-secondary">
              Use Task Graph Decomposition
            </span>
          </div>
          <button
            type="button"
            onClick={() => setUseGraph(!useGraph)}
            disabled={disabled || isSubmitting}
            className={`
              relative w-12 h-6 rounded-full transition-all duration-300
              ${useGraph ? 'bg-gradient-button' : 'bg-glass-light'}
              disabled:opacity-50 disabled:cursor-not-allowed
            `}
          >
            <div
              className={`
                absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform duration-300
                ${useGraph ? 'transform translate-x-6' : ''}
              `}
            />
          </button>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!task.trim() || disabled || isSubmitting}
          className="w-full btn-gradient flex items-center justify-center gap-2 py-3"
        >
          {isSubmitting ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Submitting...
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              Submit Task
            </>
          )}
        </button>
      </form>

      {/* Info */}
      {disabled && (
        <div className="p-3 glass-card border border-accent-pink border-opacity-30">
          <p className="text-xs text-accent-pink flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            Not connected to server. Configure settings first.
          </p>
        </div>
      )}
    </div>
  );
}
