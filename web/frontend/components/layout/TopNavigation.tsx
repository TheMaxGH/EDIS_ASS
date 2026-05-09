/**
 * Верхняя навигация для дашборда
 * Top Navigation with OpenWebUI-inspired design
 */

import React from 'react';
import Link from 'next/link';
import { MessageSquare, CheckSquare, FolderOpen, Mic, Settings, User } from 'lucide-react';

interface TopNavigationProps {
  onSettingsClick?: () => void;
}

export default function TopNavigation({ onSettingsClick }: TopNavigationProps) {
  return (
    <nav className="
      sticky top-0 z-50
      bg-bg-secondary/80 backdrop-blur-xl
      border-b border-white/5
      shadow-elevated
    ">
      <div className="max-w-[1920px] mx-auto px-6 h-16 flex items-center justify-between">
        {/* Левая часть: Логотип */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="
            w-10 h-10 rounded-lg bg-gradient-combo
            flex items-center justify-center
            shadow-glow-purple-sm
            group-hover:shadow-glow-orange-md
            transition-all duration-300
          ">
            <span className="text-xl font-bold text-white">E</span>
          </div>
          <span className="text-xl font-bold gradient-text-combo">
            EDIS Control Center
          </span>
        </Link>

        {/* Центр: Быстрые ссылки */}
        <div className="flex items-center gap-2">
          <NavLink href="/chat" icon={<MessageSquare className="w-5 h-5" />} label="Чат" />
          <NavLink href="/tasks" icon={<CheckSquare className="w-5 h-5" />} label="Задачи" />
          <NavLink href="/voices" icon={<Mic className="w-5 h-5" />} label="Голоса" />
          <NavLink href="/files" icon={<FolderOpen className="w-5 h-5" />} label="Файлы" />
        </div>

        {/* Правая часть: Настройки и профиль */}
        <div className="flex items-center gap-2">
          <button
            onClick={onSettingsClick}
            className="
              p-2 rounded-lg
              bg-white/5 hover:bg-white/10
              border border-white/10 hover:border-primary-purple/50
              transition-all duration-200
              group
            "
            title="Настройки"
          >
            <Settings className="w-5 h-5 text-text-secondary group-hover:text-primary-purple transition-colors" />
          </button>

          <button
            className="
              p-2 rounded-lg
              bg-white/5 hover:bg-white/10
              border border-white/10 hover:border-primary-purple/50
              transition-all duration-200
              group
            "
            title="Профиль"
          >
            <User className="w-5 h-5 text-text-secondary group-hover:text-primary-purple transition-colors" />
          </button>
        </div>
      </div>
    </nav>
  );
}

interface NavLinkProps {
  href: string;
  icon: React.ReactNode;
  label: string;
}

function NavLink({ href, icon, label }: NavLinkProps) {
  return (
    <Link
      href={href}
      className="
        flex items-center gap-2 px-4 py-2 rounded-lg
        bg-white/5 hover:bg-white/10
        border border-white/10 hover:border-primary-purple/50
        transition-all duration-200
        group
      "
    >
      <span className="text-text-secondary group-hover:text-primary-purple transition-colors">
        {icon}
      </span>
      <span className="text-sm font-medium text-text-secondary group-hover:text-text-primary transition-colors">
        {label}
      </span>
    </Link>
  );
}
