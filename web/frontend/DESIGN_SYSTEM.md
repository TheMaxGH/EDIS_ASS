# 🎨 EDIS Design System Documentation

**Версия:** 2.0  
**Дата:** 2026-05-09  
**Стиль:** OpenWebUI-inspired с фиолетово-оранжевой палитрой

---

## 📋 Содержание

1. [Цветовая палитра](#цветовая-палитра)
2. [Типографика](#типографика)
3. [Компоненты](#компоненты)
4. [Анимации](#анимации)
5. [Иконография](#иконография)
6. [Spacing & Layout](#spacing--layout)

---

## 🎨 Цветовая палитра

### Основные цвета

```css
/* Акцентные цвета */
--accent-primary: #8B5CF6      /* Фиолетовый - основной акцент */
--accent-secondary: #F97316    /* Оранжевый - вторичный акцент */
--accent-hover: #7C3AED        /* Фиолетовый при hover */

/* Фоновые цвета */
--bg-primary: #0F0F1A          /* Основной фон */
--bg-secondary: #1A1A2E        /* Вторичный фон */
--bg-tertiary: #16213E         /* Третичный фон */

/* Текстовые цвета */
--text-primary: #E5E7EB        /* Основной текст */
--text-secondary: #9CA3AF      /* Вторичный текст */
--text-muted: #6B7280          /* Приглушенный текст */

/* Границы */
--border-subtle: rgba(255, 255, 255, 0.1)
--border-medium: rgba(255, 255, 255, 0.2)
```

### Семантические цвета

```css
/* Статусы */
--success: #10B981    /* Зеленый - успех */
--error: #EF4444      /* Красный - ошибка */
--warning: #F59E0B    /* Желтый - предупреждение */
--info: #3B82F6       /* Синий - информация */
```

### Градиенты

```css
/* Фиолетовый градиент */
.gradient-purple {
  background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
}

/* Оранжевый градиент */
.gradient-orange {
  background: linear-gradient(135deg, #F97316 0%, #EA580C 100%);
}

/* Комбинированный градиент */
.gradient-combined {
  background: linear-gradient(135deg, #8B5CF6 0%, #F97316 100%);
}
```

---

## ✍️ Типографика

### Шрифты

```css
/* UI шрифт */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;

/* Моноширинный шрифт (код) */
font-family: 'JetBrains Mono', 'Fira Code', monospace;
```

### Размеры

| Класс | Размер | Использование |
|-------|--------|---------------|
| `text-xs` | 0.75rem (12px) | Метки, timestamps |
| `text-sm` | 0.875rem (14px) | Основной текст |
| `text-base` | 1rem (16px) | Заголовки карточек |
| `text-lg` | 1.125rem (18px) | Подзаголовки |
| `text-xl` | 1.25rem (20px) | Заголовки секций |
| `text-2xl` | 1.5rem (24px) | Главные заголовки |

### Веса

- **Regular (400)**: Основной текст
- **Semibold (600)**: Подзаголовки, кнопки
- **Bold (700)**: Заголовки, акценты

---

## 🧩 Компоненты

### 1. Кнопки

#### Primary Button
```tsx
<button className="px-4 py-2 bg-accent-primary hover:bg-accent-hover text-white rounded-lg transition-colors shadow-glow">
  Primary Action
</button>
```

#### Secondary Button
```tsx
<button className="px-4 py-2 bg-bg-secondary hover:bg-bg-tertiary text-text-primary border border-border-subtle rounded-lg transition-colors">
  Secondary Action
</button>
```

#### Ghost Button
```tsx
<button className="px-4 py-2 hover:bg-message-user/30 text-text-secondary hover:text-text-primary rounded-lg transition-colors">
  Ghost Action
</button>
```

### 2. Карточки

#### Glass Card
```tsx
<div className="glass-card p-6 rounded-2xl backdrop-blur-xl border border-border-subtle shadow-elevated">
  {/* Content */}
</div>
```

#### Message Bubble (User)
```tsx
<div className="bg-gradient-purple text-white rounded-2xl rounded-tr-sm px-4 py-3 shadow-glow-purple">
  {/* User message */}
</div>
```

#### Message Bubble (Assistant)
```tsx
<div className="bg-message-assistant backdrop-blur-sm border border-border-subtle rounded-2xl rounded-tl-sm px-4 py-3">
  {/* Assistant message */}
</div>
```

### 3. Inputs

#### Text Input
```tsx
<input 
  type="text"
  className="w-full bg-bg-secondary border border-border-subtle rounded-lg px-4 py-2 text-text-primary placeholder-text-secondary focus:border-accent-primary focus:ring-2 focus:ring-accent-primary/20 transition-all"
  placeholder="Enter text..."
/>
```

#### Textarea
```tsx
<textarea
  className="w-full bg-transparent text-text-primary placeholder-text-secondary resize-none outline-none"
  placeholder="Write a message..."
/>
```

### 4. Badges

#### Status Badge
```tsx
<span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs font-medium rounded-full border border-green-500/30">
  Active
</span>
```

### 5. Навигация

#### Top Navigation
```tsx
<nav className="sticky top-0 z-50 bg-bg-secondary/80 backdrop-blur-xl border-b border-border-subtle shadow-elevated">
  {/* Nav content */}
</nav>
```

#### Sidebar
```tsx
<aside className="w-64 bg-bg-secondary border-r border-border-subtle">
  {/* Sidebar content */}
</aside>
```

### 6. Модальные окна

```tsx
<div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
  <div className="bg-bg-secondary border border-border-subtle rounded-2xl p-6 max-w-lg w-full shadow-elevated">
    {/* Modal content */}
  </div>
</div>
```

---

## 🎬 Анимации

### Fade In
```css
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}
```

### Slide Up
```css
@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-slide-up {
  animation: slide-up 0.4s ease-out;
}
```

### Pulse Soft
```css
@keyframes pulse-soft {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.animate-pulse-soft {
  animation: pulse-soft 2s ease-in-out infinite;
}
```

### Scale In
```css
@keyframes scale-in {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-scale-in {
  animation: scale-in 0.2s ease-out;
}
```

---

## 🎯 Иконография

### Библиотека
Используется **Lucide React** для всех иконок.

```tsx
import { User, Bot, Send, Mic, Paperclip } from 'lucide-react';
```

### Размеры
- **Small**: `w-4 h-4` (16px) - для inline элементов
- **Medium**: `w-5 h-5` (20px) - стандартный размер
- **Large**: `w-6 h-6` (24px) - для заголовков
- **XL**: `w-8 h-8` (32px) - для аватаров

### Цвета
```tsx
{/* Primary accent */}
<Icon className="w-5 h-5 text-accent-primary" />

{/* Secondary text */}
<Icon className="w-5 h-5 text-text-secondary" />

{/* Success */}
<Icon className="w-5 h-5 text-green-400" />
```

---

## 📐 Spacing & Layout

### Spacing Scale
```css
/* Tailwind spacing */
0.5 = 2px
1 = 4px
2 = 8px
3 = 12px
4 = 16px
5 = 20px
6 = 24px
8 = 32px
10 = 40px
12 = 48px
16 = 64px
```

### Border Radius
```css
rounded-sm = 2px      /* Мелкие элементы */
rounded = 4px         /* Кнопки, badges */
rounded-lg = 8px      /* Inputs, cards */
rounded-xl = 12px     /* Модальные окна */
rounded-2xl = 16px    /* Большие карточки */
rounded-full = 9999px /* Круглые элементы */
```

### Shadows
```css
/* Elevated - для карточек */
shadow-elevated: 0 4px 6px -1px rgba(0, 0, 0, 0.3)

/* Glow - для акцентов */
shadow-glow: 0 0 20px rgba(139, 92, 246, 0.3)

/* Glow Purple - для фиолетовых элементов */
shadow-glow-purple: 0 0 20px rgba(139, 92, 246, 0.4)
```

---

## 🎨 Примеры использования

### Dashboard Widget
```tsx
<div className="glass-card p-6 rounded-2xl backdrop-blur-xl border border-border-subtle shadow-elevated hover:scale-[1.02] transition-transform">
  <div className="flex items-center gap-3 mb-4">
    <div className="p-3 rounded-xl bg-accent-primary/20">
      <Icon className="w-6 h-6 text-accent-primary" />
    </div>
    <div>
      <h3 className="text-lg font-semibold text-text-primary">Widget Title</h3>
      <p className="text-sm text-text-secondary">Subtitle</p>
    </div>
  </div>
  {/* Widget content */}
</div>
```

### Chat Message
```tsx
<div className="flex gap-3 animate-slide-up">
  {/* Avatar */}
  <div className="w-10 h-10 rounded-lg bg-gradient-purple flex items-center justify-center shadow-glow-purple">
    <User className="w-5 h-5 text-white" />
  </div>
  
  {/* Message */}
  <div className="flex-1">
    <div className="flex items-center gap-2 mb-1">
      <span className="text-sm font-semibold text-accent-primary">You</span>
      <span className="text-xs text-text-muted">12:34</span>
    </div>
    <div className="bg-gradient-purple text-white rounded-2xl rounded-tr-sm px-4 py-3 shadow-glow-purple">
      <p className="text-sm">Message content</p>
    </div>
  </div>
</div>
```

### Timeline Event
```tsx
<div className="relative pl-14">
  {/* Timeline dot */}
  <div className="absolute left-0 top-2 p-2.5 rounded-full bg-green-500/10 border-2 border-green-500/30">
    <CheckCircle className="w-5 h-5 text-green-400" />
  </div>
  
  {/* Event card */}
  <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-4">
    <div className="flex items-center justify-between mb-2">
      <span className="text-xs font-mono text-text-secondary">12:34:56</span>
      <span className="text-xs font-semibold text-green-400">SUCCESS</span>
    </div>
    <p className="text-sm text-text-primary">Event description</p>
  </div>
</div>
```

---

## 📱 Responsive Design

### Breakpoints
```css
sm: 640px   /* Mobile landscape */
md: 768px   /* Tablet */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
2xl: 1536px /* Extra large */
```

### Mobile-First Approach
```tsx
<div className="
  grid 
  grid-cols-1 
  md:grid-cols-2 
  xl:grid-cols-3 
  gap-6
">
  {/* Responsive grid */}
</div>
```

---

## ♿ Accessibility

### Контрастность
- Все текстовые элементы соответствуют WCAG AA (минимум 4.5:1)
- Акцентные цвета имеют достаточный контраст с фоном

### Keyboard Navigation
- Все интерактивные элементы доступны через Tab
- Focus states четко видны с `ring-2 ring-accent-primary`

### Screen Readers
```tsx
<button aria-label="Send message">
  <Send className="w-5 h-5" />
</button>
```

---

## 🔧 Утилиты

### Glass Effect
```css
.glass-card {
  background: rgba(26, 26, 46, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

### Gradient Text
```css
.gradient-text {
  background: linear-gradient(135deg, #8B5CF6 0%, #F97316 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

### Scrollbar Styling
```css
.scrollbar-thin {
  scrollbar-width: thin;
  scrollbar-color: rgba(139, 92, 246, 0.3) transparent;
}

.scrollbar-thin::-webkit-scrollbar {
  width: 6px;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.3);
  border-radius: 3px;
}
```

---

## 📦 Компонентная библиотека

### Созданные компоненты

1. **Layout**
   - [`ChatLayout`](web/frontend/components/layout/ChatLayout.tsx) - Основной layout для чата
   - [`Sidebar`](web/frontend/components/layout/Sidebar.tsx) - Боковая панель с историей
   - [`TopNavigation`](web/frontend/components/layout/TopNavigation.tsx) - Верхняя навигация

2. **Chat**
   - [`BubbleChat`](web/frontend/components/BubbleChat.tsx) - Основной чат компонент
   - [`MessageBubble`](web/frontend/components/MessageBubble.tsx) - Пузырь сообщения
   - [`ChatInput`](web/frontend/components/ChatInput.tsx) - Поле ввода с файлами и голосом

3. **Dashboard**
   - [`Widget`](web/frontend/components/dashboard/Widget.tsx) - Универсальный виджет
   - [`SystemStats`](web/frontend/components/SystemStats.tsx) - Статистика системы

4. **Tasks**
   - [`TaskGraph`](web/frontend/components/TaskGraph.tsx) - Визуализация графа задач
   - [`TaskInput`](web/frontend/components/TaskInput.tsx) - Создание задачи

5. **Monitoring**
   - [`AutonomousLog`](web/frontend/components/AutonomousLog.tsx) - Лента событий
   - [`PreviewPanel`](web/frontend/components/PreviewPanel.tsx) - Предпросмотр кода

6. **Utilities**
   - [`Settings`](web/frontend/components/Settings.tsx) - Настройки подключения
   - [`EdisLogo`](web/frontend/components/EdisLogo.tsx) - Логотип
   - [`FileManager`](web/frontend/components/FileManager.tsx) - Управление файлами

---

## 🎓 Best Practices

### 1. Консистентность
- Используйте единую цветовую палитру
- Придерживайтесь spacing scale
- Применяйте одинаковые border-radius для похожих элементов

### 2. Производительность
- Используйте `backdrop-blur` умеренно
- Оптимизируйте анимации с `will-change`
- Lazy load для тяжелых компонентов

### 3. Доступность
- Всегда добавляйте `aria-label` для иконок-кнопок
- Обеспечьте keyboard navigation
- Тестируйте с screen readers

### 4. Responsive
- Начинайте с mobile-first
- Тестируйте на разных разрешениях
- Используйте относительные единицы (rem, %)

---

## 📚 Ресурсы

- **Tailwind CSS**: https://tailwindcss.com/docs
- **Lucide Icons**: https://lucide.dev/
- **React Flow**: https://reactflow.dev/
- **Next.js**: https://nextjs.org/docs

---

**Создано с ❤️ для EDIS Project**  
*Дизайн-система v2.0 - OpenWebUI-inspired*
