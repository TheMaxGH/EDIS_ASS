import React, { useState } from 'react';

export interface Chat {
  id: string;
  title: string;
  timestamp: string;
  preview?: string;
}

interface SidebarProps {
  chats: Chat[];
  currentChatId: string | null;
  onSelectChat: (id: string) => void;
  onNewChat: () => void;
  onDeleteChat: (id: string) => void;
  onRenameChat?: (id: string, newTitle: string) => void;
}

export default function Sidebar({
  chats,
  currentChatId,
  onSelectChat,
  onNewChat,
  onDeleteChat,
  onRenameChat,
}: SidebarProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  // Group chats by date
  const groupChatsByDate = (chats: Chat[]) => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const lastWeek = new Date(today);
    lastWeek.setDate(lastWeek.getDate() - 7);
    const lastMonth = new Date(today);
    lastMonth.setDate(lastMonth.getDate() - 30);

    const groups: { [key: string]: Chat[] } = {
      'Сегодня': [],
      'Вчера': [],
      'Последние 7 дней': [],
      'Последние 30 дней': [],
      'Старые': [],
    };

    chats.forEach(chat => {
      const chatDate = new Date(chat.timestamp);
      if (chatDate >= today) {
        groups['Сегодня'].push(chat);
      } else if (chatDate >= yesterday) {
        groups['Вчера'].push(chat);
      } else if (chatDate >= lastWeek) {
        groups['Последние 7 дней'].push(chat);
      } else if (chatDate >= lastMonth) {
        groups['Последние 30 дней'].push(chat);
      } else {
        groups['Старые'].push(chat);
      }
    });

    return groups;
  };

  // Filter chats by search query
  const filteredChats = chats.filter(chat =>
    chat.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const groupedChats = groupChatsByDate(filteredChats);

  const handleStartEdit = (chat: Chat) => {
    setEditingId(chat.id);
    setEditTitle(chat.title);
  };

  const handleSaveEdit = (id: string) => {
    if (onRenameChat && editTitle.trim()) {
      onRenameChat(id, editTitle.trim());
    }
    setEditingId(null);
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditTitle('');
  };

  return (
    <div className="h-full flex flex-col bg-sidebar-bg">
      {/* Header */}
      <div className="p-3 border-b border-border-subtle flex-shrink-0">
        {/* New Chat Button */}
        <button
          onClick={onNewChat}
          className="w-full btn-primary flex items-center justify-center gap-2 mb-3"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span>Новый чат</span>
        </button>

        {/* Search Input */}
        <div className="relative">
          <input
            type="text"
            placeholder="Поиск чатов..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="
              w-full pl-9 pr-3 py-2 rounded-lg
              bg-message-user border border-border-subtle
              text-text-primary placeholder:text-text-tertiary
              focus:border-accent-primary focus:outline-none
              transition-all duration-200
            "
          />
          <svg
            className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto scrollbar-chat">
        {Object.entries(groupedChats).map(([group, groupChats]) => {
          if (groupChats.length === 0) return null;

          return (
            <div key={group} className="mb-4">
              {/* Group Header */}
              <div className="px-3 py-2 text-xs font-semibold text-text-tertiary uppercase tracking-wider">
                {group}
              </div>

              {/* Group Chats */}
              <div className="space-y-1 px-2">
                {groupChats.map(chat => (
                  <ChatItem
                    key={chat.id}
                    chat={chat}
                    isActive={chat.id === currentChatId}
                    isEditing={editingId === chat.id}
                    editTitle={editTitle}
                    onSelect={() => onSelectChat(chat.id)}
                    onDelete={() => onDeleteChat(chat.id)}
                    onStartEdit={() => handleStartEdit(chat)}
                    onSaveEdit={() => handleSaveEdit(chat.id)}
                    onCancelEdit={handleCancelEdit}
                    onEditTitleChange={setEditTitle}
                  />
                ))}
              </div>
            </div>
          );
        })}

        {filteredChats.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-text-tertiary p-4">
            <svg className="w-12 h-12 mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <p className="text-sm">Нет чатов</p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-border-subtle flex-shrink-0">
        <div className="flex items-center gap-2">
          <button
            onClick={() => window.location.href = '/'}
            className="flex-1 btn-ghost text-sm"
            title="На главную"
          >
            🏠 Главная
          </button>
          <button
            onClick={() => window.location.href = '/files'}
            className="flex-1 btn-ghost text-sm"
            title="Файлы"
          >
            📁 Файлы
          </button>
        </div>
      </div>
    </div>
  );
}

// ChatItem Component
interface ChatItemProps {
  chat: Chat;
  isActive: boolean;
  isEditing: boolean;
  editTitle: string;
  onSelect: () => void;
  onDelete: () => void;
  onStartEdit: () => void;
  onSaveEdit: () => void;
  onCancelEdit: () => void;
  onEditTitleChange: (title: string) => void;
}

function ChatItem({
  chat,
  isActive,
  isEditing,
  editTitle,
  onSelect,
  onDelete,
  onStartEdit,
  onSaveEdit,
  onCancelEdit,
  onEditTitleChange,
}: ChatItemProps) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className={`
        group relative px-3 py-2 rounded-lg cursor-pointer
        transition-all duration-200
        ${isActive
          ? 'bg-accent-primary/20 border border-accent-primary/50'
          : 'hover:bg-message-user border border-transparent'
        }
      `}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={!isEditing ? onSelect : undefined}
    >
      {isEditing ? (
        <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
          <input
            type="text"
            value={editTitle}
            onChange={(e) => onEditTitleChange(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') onSaveEdit();
              if (e.key === 'Escape') onCancelEdit();
            }}
            className="
              flex-1 px-2 py-1 rounded bg-message-user
              text-text-primary text-sm
              border border-accent-primary
              focus:outline-none
            "
            autoFocus
          />
          <button
            onClick={onSaveEdit}
            className="btn-icon p-1"
            title="Сохранить"
          >
            <svg className="w-4 h-4 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </button>
          <button
            onClick={onCancelEdit}
            className="btn-icon p-1"
            title="Отмена"
          >
            <svg className="w-4 h-4 text-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      ) : (
        <div className="flex items-center justify-between gap-2">
          <div className="flex-1 min-w-0">
            <div className="text-sm text-text-primary truncate font-medium">
              {chat.title}
            </div>
            {chat.preview && (
              <div className="text-xs text-text-tertiary truncate mt-0.5">
                {chat.preview}
              </div>
            )}
          </div>

          {/* Action Buttons (show on hover) */}
          {isHovered && !isActive && (
            <div className="flex gap-1 flex-shrink-0" onClick={(e) => e.stopPropagation()}>
              <button
                onClick={onStartEdit}
                className="btn-icon p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                title="Переименовать"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <button
                onClick={onDelete}
                className="btn-icon p-1 opacity-0 group-hover:opacity-100 transition-opacity hover:text-error"
                title="Удалить"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
