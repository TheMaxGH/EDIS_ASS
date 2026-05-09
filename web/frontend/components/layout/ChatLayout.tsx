import React, { ReactNode, useState, useEffect } from 'react';

interface ChatLayoutProps {
  sidebar: ReactNode;
  children: ReactNode;
  rightPanel?: ReactNode;
}

export default function ChatLayout({ sidebar, children, rightPanel }: ChatLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [rightPanelOpen, setRightPanelOpen] = useState(false);

  // Load sidebar state from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('edis_sidebar_open');
    if (saved !== null) {
      setSidebarOpen(saved === 'true');
    }
  }, []);

  // Save sidebar state to localStorage
  useEffect(() => {
    localStorage.setItem('edis_sidebar_open', String(sidebarOpen));
  }, [sidebarOpen]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+B or Cmd+B to toggle sidebar
      if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        setSidebarOpen(prev => !prev);
      }
      
      // Ctrl+Shift+S or Cmd+Shift+S to toggle right panel
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 's') {
        e.preventDefault();
        setRightPanelOpen(prev => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="flex h-screen bg-chat-bg overflow-hidden">
      {/* Sidebar */}
      <aside
        className={`
          ${sidebarOpen ? 'w-64' : 'w-0'}
          transition-all duration-300 ease-in-out
          bg-sidebar-bg border-r border-border-subtle
          flex-shrink-0 overflow-hidden
        `}
      >
        <div className="h-full overflow-hidden">
          {sidebar}
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 relative">
        {/* Toggle Sidebar Button */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="
            absolute top-4 left-4 z-10
            btn-icon
            bg-message-user/50 backdrop-blur-sm
            hover:bg-message-user
          "
          title={sidebarOpen ? 'Скрыть sidebar (Ctrl+B)' : 'Показать sidebar (Ctrl+B)'}
        >
          {sidebarOpen ? (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          )}
        </button>

        {/* Main Chat Area */}
        <div className="flex-1 overflow-hidden">
          {children}
        </div>
      </main>

      {/* Right Panel (Optional) */}
      {rightPanel && rightPanelOpen && (
        <aside
          className="
            w-80 bg-sidebar-bg border-l border-border-subtle
            flex-shrink-0 overflow-hidden
            animate-slide-in-right
          "
        >
          <div className="h-full overflow-y-auto scrollbar-chat">
            <div className="p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-text-primary">Настройки</h3>
                <button
                  onClick={() => setRightPanelOpen(false)}
                  className="btn-icon"
                  title="Закрыть панель"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              {rightPanel}
            </div>
          </div>
        </aside>
      )}
    </div>
  );
}
