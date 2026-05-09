import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import ChatLayout from '../components/layout/ChatLayout';
import Sidebar, { Chat } from '../components/layout/Sidebar';
import BubbleChat from '../components/BubbleChat';
import Settings from '../components/Settings';
import SettingsPanel from '../components/SettingsPanel';
import TopNavigation from '../components/layout/TopNavigation';
import EDISClient from '../lib/edis-client';

export default function ChatPage() {
  const [serverUrl, setServerUrl] = useState('http://localhost:8000');
  const [apiKey, setApiKey] = useState('your-secret-key-here');
  const [client] = useState<EDISClient>(() => new EDISClient('http://localhost:8000', 'your-secret-key-here'));
  const [showSettings, setShowSettings] = useState(false);
  const [isSettingsPanelOpen, setIsSettingsPanelOpen] = useState(false);
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [chatHistory, setChatHistory] = useState<Chat[]>([]);

  // Load settings from localStorage
  useEffect(() => {
    const savedUrl = localStorage.getItem('edis_server_url');
    const savedKey = localStorage.getItem('edis_api_key');
    
    if (savedUrl) setServerUrl(savedUrl);
    if (savedKey) setApiKey(savedKey);

    // Load chat history
    loadChatHistory();
  }, []);

  const loadChatHistory = async () => {
    try {
      const response = await fetch(`${serverUrl}/api/v1/chat/list/all`, {
        headers: {
          'X-API-Key': apiKey,
        },
      });

      if (response.ok) {
        const data = await response.json();
        const chats: Chat[] = (data.chats || []).map((chat: any) => ({
          id: chat.id,
          title: chat.title || 'Новый чат',
          timestamp: chat.created_at || new Date().toISOString(),
          preview: chat.preview || '',
        }));
        setChatHistory(chats);
      }
    } catch (err) {
      console.error('Failed to load chat history:', err);
    }
  };

  const handleSettingsChange = (newServerUrl: string, newApiKey: string) => {
    setServerUrl(newServerUrl);
    setApiKey(newApiKey);
    
    localStorage.setItem('edis_server_url', newServerUrl);
    localStorage.setItem('edis_api_key', newApiKey);
    
    setShowSettings(false);
    loadChatHistory();
  };

  const handleNewChat = () => {
    setCurrentChatId(null);
  };

  const handleChatCreated = (chatId: string) => {
    setCurrentChatId(chatId);
    loadChatHistory();
  };

  const handleSelectChat = (chatId: string) => {
    setCurrentChatId(chatId);
  };

  const handleDeleteChat = async (chatId: string) => {
    try {
      const response = await fetch(`${serverUrl}/api/v1/chat/${chatId}`, {
        method: 'DELETE',
        headers: {
          'X-API-Key': apiKey,
        },
      });

      if (response.ok) {
        // Remove from local state
        setChatHistory(prev => prev.filter(chat => chat.id !== chatId));
        
        // If deleted chat was current, clear selection
        if (currentChatId === chatId) {
          setCurrentChatId(null);
        }
      }
    } catch (err) {
      console.error('Failed to delete chat:', err);
    }
  };

  const handleRenameChat = async (chatId: string, newTitle: string) => {
    try {
      const response = await fetch(`${serverUrl}/api/v1/chat/${chatId}/title`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey,
        },
        body: JSON.stringify({ title: newTitle }),
      });

      if (response.ok) {
        // Update local state
        setChatHistory(prev =>
          prev.map(chat =>
            chat.id === chatId ? { ...chat, title: newTitle } : chat
          )
        );
      }
    } catch (err) {
      console.error('Failed to rename chat:', err);
    }
  };

  return (
    <>
      <Head>
        <title>EDIS Chat - AI Assistant</title>
        <meta name="description" content="Чат с EDIS AI Assistant" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      {/* Верхняя навигация */}
      <TopNavigation onSettingsClick={() => setShowSettings(!showSettings)} />

      <ChatLayout
        sidebar={
          <Sidebar
            chats={chatHistory}
            currentChatId={currentChatId}
            onSelectChat={handleSelectChat}
            onNewChat={handleNewChat}
            onDeleteChat={handleDeleteChat}
            onRenameChat={handleRenameChat}
          />
        }
        rightPanel={
          showSettings ? (
            <Settings onSettingsChange={handleSettingsChange} />
          ) : null
        }
      >
        {/* Settings Button */}
        <div className="absolute top-4 right-4 z-10">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="btn-icon bg-message-user/50 backdrop-blur-sm hover:bg-message-user"
            title="Настройки"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
          </button>
        </div>

        {/* Chat Area */}
        <div className="h-full">
          <BubbleChat
            serverUrl={serverUrl}
            apiKey={apiKey}
            chatId={currentChatId || undefined}
            onChatCreated={handleChatCreated}
          />
        </div>
      </ChatLayout>
    </>
  );
}
