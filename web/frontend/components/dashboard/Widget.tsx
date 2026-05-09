/**
 * Базовый компонент виджета для модульного дашборда
 * Widget component with OpenWebUI-inspired design
 */

import React, { ReactNode } from 'react';
import { ArrowUpRight } from 'lucide-react';

interface WidgetProps {
  title: string;
  icon: ReactNode;
  children: ReactNode;
  onExpand?: () => void;
  actions?: ReactNode;
  className?: string;
  gradient?: 'purple' | 'orange' | 'combo';
}

export default function Widget({
  title,
  icon,
  children,
  onExpand,
  actions,
  className = '',
  gradient = 'purple'
}: WidgetProps) {
  
  const gradientClasses = {
    purple: 'from-primary-purple/20 to-primary-purple/5',
    orange: 'from-accent-orange/20 to-accent-orange/5',
    combo: 'from-primary-purple/20 via-accent-orange/15 to-accent-gold/10'
  };

  const iconGradients = {
    purple: 'bg-gradient-purple',
    orange: 'bg-gradient-orange',
    combo: 'bg-gradient-combo'
  };

  return (
    <div 
      className={`
        relative group
        bg-bg-secondary/80 backdrop-blur-md
        rounded-xl border border-white/5
        shadow-card hover:shadow-elevated
        transition-all duration-300
        hover:scale-[1.02] hover:border-white/10
        animate-fade-in
        ${className}
      `}
    >
      {/* Градиентный фон */}
      <div className={`absolute inset-0 bg-gradient-to-br ${gradientClasses[gradient]} rounded-xl opacity-50`} />
      
      {/* Контент */}
      <div className="relative p-6">
        {/* Заголовок */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            {/* Иконка с градиентом */}
            <div className={`
              w-10 h-10 rounded-lg ${iconGradients[gradient]}
              flex items-center justify-center
              shadow-glow-purple-sm
              text-white
            `}>
              {icon}
            </div>
            
            {/* Заголовок */}
            <h3 className="text-lg font-semibold text-text-primary">
              {title}
            </h3>
          </div>

          {/* Действия */}
          <div className="flex items-center gap-2">
            {actions}
            
            {/* Кнопка развернуть */}
            {onExpand && (
              <button
                onClick={onExpand}
                className="
                  p-2 rounded-lg
                  bg-white/5 hover:bg-white/10
                  border border-white/10 hover:border-white/20
                  transition-all duration-200
                  group/btn
                "
                title="Развернуть"
              >
                <ArrowUpRight className="w-4 h-4 text-text-secondary group-hover/btn:text-primary-purple transition-colors" />
              </button>
            )}
          </div>
        </div>

        {/* Контент виджета */}
        <div className="text-text-secondary">
          {children}
        </div>
      </div>

      {/* Свечение при hover */}
      <div className={`
        absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100
        transition-opacity duration-300 pointer-events-none
        ${gradient === 'purple' ? 'shadow-glow-purple-sm' : ''}
        ${gradient === 'orange' ? 'shadow-glow-orange-md' : ''}
        ${gradient === 'combo' ? 'shadow-glow-purple-sm' : ''}
      `} />
    </div>
  );
}
