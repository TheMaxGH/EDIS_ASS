/**
 * Freelance Projects Page
 * Страница управления фриланс-проектами с Kanban-доской
 */

import React, { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { 
  ArrowLeft, 
  Briefcase,
  Plus,
  MoreVertical,
  Clock,
  DollarSign,
  CheckCircle
} from 'lucide-react';
import Settings from '../components/Settings';

interface Project {
  id: string;
  title: string;
  client: string;
  status: 'backlog' | 'in-progress' | 'review' | 'completed';
  budget: number;
  deadline: string;
  description: string;
}

export default function FreelancePage() {
  const [projects, setProjects] = useState<Project[]>([
    {
      id: '1',
      title: 'Разработка веб-приложения',
      client: 'Клиент А',
      status: 'in-progress',
      budget: 50000,
      deadline: '2026-06-01',
      description: 'Создание SaaS платформы для управления проектами'
    },
    {
      id: '2',
      title: 'Дизайн лендинга',
      client: 'Клиент Б',
      status: 'review',
      budget: 15000,
      deadline: '2026-05-20',
      description: 'Современный лендинг для стартапа'
    }
  ]);

  const columns = [
    { id: 'backlog', title: 'Бэклог', color: 'text-text-muted' },
    { id: 'in-progress', title: 'В работе', color: 'text-primary-purple' },
    { id: 'review', title: 'На проверке', color: 'text-accent-orange' },
    { id: 'completed', title: 'Завершено', color: 'text-green-400' }
  ];

  const getProjectsByStatus = (status: string) => {
    return projects.filter(p => p.status === status);
  };

  const totalBudget = projects.reduce((sum, p) => sum + p.budget, 0);
  const completedProjects = projects.filter(p => p.status === 'completed').length;

  return (
    <>
      <Head>
        <title>Фриланс - EDIS</title>
        <meta name="description" content="Управление фриланс-проектами" />
      </Head>

      <Settings onSettingsChange={() => {}} />

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
              <Briefcase className="w-6 h-6 text-accent-orange" />
              <span className="text-xl font-bold gradient-text-combo">
                Фриланс-проекты
              </span>
            </div>
          </div>

          <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-combo text-white font-medium hover:shadow-glow-purple-sm transition-all">
            <Plus className="w-4 h-4" />
            Новый проект
          </button>
        </div>
      </nav>

      <div className="min-h-screen bg-bg-primary p-6">
        <div className="max-w-[1920px] mx-auto">
          
          {/* Статистика */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="p-6 rounded-xl bg-bg-secondary/80 backdrop-blur-md border border-white/5 shadow-card animate-fade-in">
              <div className="flex items-center gap-3 mb-2">
                <Briefcase className="w-5 h-5 text-primary-purple" />
                <span className="text-sm text-text-muted">Всего проектов</span>
              </div>
              <p className="text-3xl font-bold text-text-primary">{projects.length}</p>
            </div>

            <div className="p-6 rounded-xl bg-bg-secondary/80 backdrop-blur-md border border-white/5 shadow-card animate-fade-in">
              <div className="flex items-center gap-3 mb-2">
                <DollarSign className="w-5 h-5 text-accent-orange" />
                <span className="text-sm text-text-muted">Общий бюджет</span>
              </div>
              <p className="text-3xl font-bold text-text-primary">{totalBudget.toLocaleString('ru-RU')} ₽</p>
            </div>

            <div className="p-6 rounded-xl bg-bg-secondary/80 backdrop-blur-md border border-white/5 shadow-card animate-fade-in">
              <div className="flex items-center gap-3 mb-2">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span className="text-sm text-text-muted">Завершено</span>
              </div>
              <p className="text-3xl font-bold text-text-primary">{completedProjects}</p>
            </div>
          </div>

          {/* Kanban доска */}
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
            {columns.map((column) => {
              const columnProjects = getProjectsByStatus(column.id);
              return (
                <div key={column.id} className="flex flex-col">
                  {/* Заголовок колонки */}
                  <div className="mb-4 flex items-center justify-between">
                    <h3 className={`text-lg font-bold ${column.color}`}>
                      {column.title}
                    </h3>
                    <span className="px-2 py-1 rounded-lg bg-white/5 text-xs font-medium text-text-muted">
                      {columnProjects.length}
                    </span>
                  </div>

                  {/* Карточки проектов */}
                  <div className="space-y-3 flex-1">
                    {columnProjects.length === 0 ? (
                      <div className="p-4 rounded-xl border-2 border-dashed border-white/10 text-center">
                        <p className="text-sm text-text-muted">Нет проектов</p>
                      </div>
                    ) : (
                      columnProjects.map((project) => (
                        <div
                          key={project.id}
                          className="p-4 rounded-xl bg-bg-secondary/80 backdrop-blur-md border border-white/5 shadow-card hover:shadow-elevated hover:scale-[1.02] transition-all cursor-pointer group"
                        >
                          {/* Заголовок карточки */}
                          <div className="flex items-start justify-between mb-3">
                            <h4 className="text-sm font-bold text-text-primary group-hover:text-primary-purple transition-colors">
                              {project.title}
                            </h4>
                            <button className="p-1 rounded hover:bg-white/10 transition-colors">
                              <MoreVertical className="w-4 h-4 text-text-muted" />
                            </button>
                          </div>

                          {/* Клиент */}
                          <p className="text-xs text-text-muted mb-3">
                            {project.client}
                          </p>

                          {/* Описание */}
                          <p className="text-xs text-text-secondary mb-4 line-clamp-2">
                            {project.description}
                          </p>

                          {/* Метаданные */}
                          <div className="flex items-center justify-between pt-3 border-t border-white/10">
                            <div className="flex items-center gap-1 text-xs text-text-muted">
                              <Clock className="w-3 h-3" />
                              {new Date(project.deadline).toLocaleDateString('ru-RU')}
                            </div>
                            <div className="flex items-center gap-1 text-xs font-medium text-accent-orange">
                              <DollarSign className="w-3 h-3" />
                              {project.budget.toLocaleString('ru-RU')}
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </>
  );
}
