/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // === EDIS OpenWebUI Style - Комбинированная палитра ===
        
        // === Основные фоны (Pitch Black) ===
        'bg-primary': '#0d0d0d',        // Основной фон приложения
        'bg-secondary': '#171717',      // Sidebar, панели
        'bg-tertiary': '#1a1a1a',       // Карточки, сообщения
        'bg-elevated': '#2a2a2a',       // Поднятые элементы (input, модалки)
        'bg-hover': '#2f2f2f',          // Hover состояние
        
        // Алиасы для совместимости
        'chat-bg': '#0d0d0d',
        'sidebar-bg': '#171717',
        'message-user': '#2f2f2f',
        'message-assistant': '#1a1a1a',
        'input-bg': '#2a2a2a',
        
        // === Фиолетовый спектр (Основные акценты) ===
        'primary-purple': '#8b5cf6',    // Основной акцент (кнопки, ссылки)
        'primary-purple-hover': '#a78bfa', // Hover состояние
        'primary-purple-active': '#7c3aed', // Active/pressed состояние
        'primary-purple-light': '#c4b5fd', // Светлый вариант
        'primary-purple-dark': '#6d28d9',  // Темный вариант
        'secondary-indigo': '#6366f1',  // Вторичный акцент (индиго)
        'secondary-indigo-hover': '#818cf8',
        
        // Алиасы для совместимости
        'accent-primary': '#8b5cf6',
        'accent-hover': '#a78bfa',
        'accent-active': '#7c3aed',
        'accent-secondary': '#6366f1',
        
        // === Оранжевый спектр (Важные акценты) ===
        'accent-orange': '#f97316',     // Важные элементы (уведомления, алерты)
        'accent-orange-hover': '#fb923c',
        'accent-orange-light': '#fdba74',
        'accent-gold': '#f59e0b',       // Премиум элементы (статусы, достижения)
        'accent-gold-hover': '#fbbf24',
        'accent-amber': '#fbbf24',      // Подсветка активности
        'accent-amber-light': '#fcd34d',
        
        // === Границы и разделители ===
        'border-subtle': '#2a2a2a',     // Тонкие границы
        'border-medium': '#3f3f3f',     // Средние границы
        'border-strong': '#525252',     // Сильные границы
        'border-accent': '#8b5cf6',     // Акцентные границы (фиолетовый)
        'border-accent-orange': '#f97316', // Акцентные границы (оранжевый)
        
        // === Текстовые цвета ===
        'text-primary': '#ececec',      // Основной текст (почти белый)
        'text-secondary': '#a1a1a1',    // Вторичный текст (серый)
        'text-tertiary': '#737373',     // Tertiary текст (темно-серый)
        'text-muted': '#525252',        // Приглушенный текст
        'text-accent': '#8b5cf6',       // Акцентный текст (фиолетовый)
        'text-accent-orange': '#f97316', // Акцентный текст (оранжевый)
        
        // === Статусные цвета ===
        'success': '#10b981',           // Зеленый (успех)
        'success-light': '#34d399',
        'warning': '#f59e0b',           // Оранжевый (предупреждение)
        'warning-light': '#fbbf24',
        'error': '#ef4444',             // Красный (ошибка)
        'error-light': '#f87171',
        'info': '#3b82f6',              // Синий (информация)
        'info-light': '#60a5fa',
        
        // === Legacy Colors (preserved for compatibility) ===
        
        // Glass colors
        glass: {
          light: 'rgba(255, 255, 255, 0.05)',
          medium: 'rgba(255, 255, 255, 0.08)',
          border: 'rgba(255, 255, 255, 0.1)',
          hover: 'rgba(255, 255, 255, 0.12)',
        },
        // Accent colors (soft, not neon)
        accent: {
          blue: '#4A90E2',
          purple: '#9B59B6',
          cyan: '#3498DB',
          pink: '#E74C3C',
          green: '#2ECC71',
          orange: '#F39C12',
        },
        // Background colors
        bg: {
          primary: '#0f0f23',
          secondary: '#1a1a2e',
          tertiary: '#16213e',
        },
        // Text colors
        text: {
          primary: '#E8E8E8',
          secondary: '#A0A0A0',
          muted: '#6B6B6B',
        }
      },
      backgroundImage: {
        // === EDIS Комбинированные градиенты ===
        
        // Фоновые градиенты
        'gradient-primary': 'linear-gradient(180deg, #0d0d0d 0%, #171717 100%)',
        'gradient-secondary': 'linear-gradient(180deg, #171717 0%, #1a1a1a 100%)',
        'gradient-elevated': 'linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%)',
        
        // Фиолетовые градиенты (основные акценты)
        'gradient-purple': 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)',
        'gradient-purple-hover': 'linear-gradient(135deg, #a78bfa 0%, #818cf8 100%)',
        'gradient-purple-vertical': 'linear-gradient(180deg, #8b5cf6 0%, #7c3aed 100%)',
        'gradient-purple-radial': 'radial-gradient(circle at top right, #8b5cf6 0%, #6366f1 100%)',
        
        // Оранжевые градиенты (важные акценты)
        'gradient-orange': 'linear-gradient(135deg, #f97316 0%, #f59e0b 100%)',
        'gradient-orange-hover': 'linear-gradient(135deg, #fb923c 0%, #fbbf24 100%)',
        'gradient-gold': 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)',
        'gradient-amber': 'linear-gradient(135deg, #fbbf24 0%, #fcd34d 100%)',
        
        // Комбинированные градиенты (фиолетовый + оранжевый)
        'gradient-combo': 'linear-gradient(135deg, #8b5cf6 0%, #f97316 100%)',
        'gradient-combo-reverse': 'linear-gradient(135deg, #f97316 0%, #8b5cf6 100%)',
        'gradient-premium': 'linear-gradient(135deg, #8b5cf6 0%, #f59e0b 50%, #f97316 100%)',
        
        // Специальные градиенты для компонентов
        'gradient-chat': 'linear-gradient(180deg, #0d0d0d 0%, #1a1a1a 100%)',
        'gradient-sidebar': 'linear-gradient(180deg, #171717 0%, #0d0d0d 100%)',
        'gradient-message': 'linear-gradient(135deg, #2f2f2f 0%, #1a1a1a 100%)',
        'gradient-card': 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(249, 115, 22, 0.1) 100%)',
        
        // Градиенты для кнопок
        'gradient-button-primary': 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)',
        'gradient-button-primary-hover': 'linear-gradient(135deg, #a78bfa 0%, #818cf8 100%)',
        'gradient-button-accent': 'linear-gradient(135deg, #f97316 0%, #f59e0b 100%)',
        'gradient-button-accent-hover': 'linear-gradient(135deg, #fb923c 0%, #fbbf24 100%)',
        
        // Градиент для лого EDIS
        'gradient-logo': 'linear-gradient(135deg, #8b5cf6 0%, #f97316 50%, #fbbf24 100%)',
      },
      backdropBlur: {
        xs: '2px',
        sm: '4px',
        md: '10px',
        lg: '20px',
        xl: '40px',
      },
      borderRadius: {
        'xl': '16px',
        '2xl': '20px',
        '3xl': '24px',
      },
      boxShadow: {
        // Тени для карточек и панелей
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.3)',
        'card-hover': '0 4px 12px 0 rgba(0, 0, 0, 0.4)',
        'panel': '0 2px 8px 0 rgba(0, 0, 0, 0.35)',
        'elevated': '0 8px 24px 0 rgba(0, 0, 0, 0.45)',
        'modal': '0 20px 60px 0 rgba(0, 0, 0, 0.6)',
        'dropdown': '0 4px 16px 0 rgba(0, 0, 0, 0.5)',
        
        // Glassmorphism
        'glass': '0 8px 32px rgba(0, 0, 0, 0.2)',
        'glass-lg': '0 12px 48px rgba(0, 0, 0, 0.3)',
        
        // Фиолетовое свечение
        'glow-purple-sm': '0 0 10px rgba(139, 92, 246, 0.3)',
        'glow-purple-md': '0 0 20px rgba(139, 92, 246, 0.4)',
        'glow-purple-lg': '0 0 30px rgba(139, 92, 246, 0.5)',
        
        // Оранжевое свечение
        'glow-orange-sm': '0 0 10px rgba(249, 115, 22, 0.3)',
        'glow-orange-md': '0 0 20px rgba(249, 115, 22, 0.4)',
        'glow-orange-lg': '0 0 30px rgba(249, 115, 22, 0.5)',
        
        // Legacy
        'glow-sm': '0 0 10px rgba(139, 92, 246, 0.3)',
        'glow-md': '0 0 20px rgba(139, 92, 246, 0.4)',
        'glow-lg': '0 0 30px rgba(139, 92, 246, 0.5)',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'Monaco', 'monospace'],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'fade-out': 'fadeOut 0.3s ease-in-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'slide-down': 'slideDown 0.4s ease-out',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'slide-in-left': 'slideInLeft 0.3s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'spin-slow': 'spin 3s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeOut: {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideInRight: {
          '0%': { transform: 'translateX(100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideInLeft: {
          '0%': { transform: 'translateX(-100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(139, 92, 246, 0.3)' },
          '50%': { boxShadow: '0 0 40px rgba(139, 92, 246, 0.6)' },
        },
      },
    },
  },
  plugins: [],
}
