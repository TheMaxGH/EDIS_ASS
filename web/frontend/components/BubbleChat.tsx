import React, { useState, useEffect, useRef } from 'react';
import MessageBubble, { Message } from './MessageBubble';
import ChatInput from './ChatInput';
import { useVoice } from '../hooks/useVoice';

interface BubbleChatProps {
  serverUrl: string;
  apiKey: string;
  chatId?: string;
  onChatCreated?: (chatId: string) => void;
}

export default function BubbleChat({ 
  serverUrl, 
  apiKey,
  chatId: initialChatId,
  onChatCreated 
}: BubbleChatProps) {
  const [chatId, setChatId] = useState<string | null>(initialChatId || null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [speakingMessageId, setSpeakingMessageId] = useState<string | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Голосовые функции
  const voice = useVoice({
    serverUrl,
    apiKey,
    onTranscript: (text) => {
      // Автоматически отправляем распознанный текст
      sendMessage(text);
    },
  });

  // Автоскролл к последнему сообщению
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Создание нового чата
  const createChat = async () => {
    try {
      const response = await fetch(`${serverUrl}/api/v1/chat/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey,
        },
        body: JSON.stringify({
          title: 'Новый диалог',
          system_prompt: 'Ты - EDIS, продвинутый AI-ассистент. Отвечай на русском языке, будь полезным и дружелюбным.'
        }),
      });

      if (!response.ok) {
        throw new Error('Не удалось создать чат');
      }

      const data = await response.json();
      setChatId(data.chat_id);
      
      if (onChatCreated) {
        onChatCreated(data.chat_id);
      }

      return data.chat_id;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка создания чата');
      return null;
    }
  };

  // Загрузка истории чата
  const loadChatHistory = async (id: string) => {
    try {
      const response = await fetch(`${serverUrl}/api/v1/chat/${id}`, {
        headers: {
          'X-API-Key': apiKey,
        },
      });

      if (!response.ok) {
        throw new Error('Не удалось загрузить историю');
      }

      const data = await response.json();
      setMessages(data.messages || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки истории');
    }
  };

  // Инициализация чата
  useEffect(() => {
    if (initialChatId) {
      loadChatHistory(initialChatId);
    }
  }, [initialChatId]);

  // Отправка сообщения с streaming
  const sendMessage = async (content: string, attachments?: File[]) => {
    if (!content.trim() && (!attachments || attachments.length === 0)) return;

    // Создаём чат, если его нет
    let currentChatId = chatId;
    if (!currentChatId) {
      currentChatId = await createChat();
      if (!currentChatId) return;
    }

    // Добавляем сообщение пользователя
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: content.trim(),
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    // Создаём временное сообщение ассистента для streaming
    const assistantMessageId = `assistant-${Date.now()}`;
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      isStreaming: true,
    };
    setMessages(prev => [...prev, assistantMessage]);

    try {
      const response = await fetch(
        `${serverUrl}/api/v1/chat/${currentChatId}/message`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': apiKey,
          },
          body: JSON.stringify({
            content: content.trim(),
            stream: true,
          }),
        }
      );

      if (!response.ok) {
        throw new Error('Ошибка отправки сообщения');
      }

      // Обработка SSE streaming
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let accumulatedContent = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') {
                // Завершение streaming
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === assistantMessageId
                      ? { ...msg, isStreaming: false }
                      : msg
                  )
                );
                break;
              }

              try {
                const parsed = JSON.parse(data);
                if (parsed.content) {
                  accumulatedContent += parsed.content;
                  
                  // Обновляем сообщение
                  setMessages(prev =>
                    prev.map(msg =>
                      msg.id === assistantMessageId
                        ? { ...msg, content: accumulatedContent }
                        : msg
                    )
                  );
                }
              } catch (e) {
                // Игнорируем ошибки парсинга
              }
            }
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка отправки');
      // Удаляем временное сообщение при ошибке
      setMessages(prev => prev.filter(msg => msg.id !== assistantMessageId));
    } finally {
      setIsLoading(false);
    }
  };

  // Регенерация ответа
  const handleRegenerate = async (messageId: string) => {
    if (!chatId) return;

    setIsLoading(true);
    try {
      const response = await fetch(
        `${serverUrl}/api/v1/chat/${chatId}/regenerate`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': apiKey,
          },
          body: JSON.stringify({ message_id: messageId }),
        }
      );

      if (!response.ok) {
        throw new Error('Ошибка регенерации');
      }

      // Перезагружаем историю
      await loadChatHistory(chatId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка регенерации');
    } finally {
      setIsLoading(false);
    }
  };

  // Удаление сообщения
  const handleDelete = async (messageId: string) => {
    if (!chatId) return;

    try {
      const response = await fetch(
        `${serverUrl}/api/v1/chat/${chatId}/message`,
        {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': apiKey,
          },
          body: JSON.stringify({ message_id: messageId }),
        }
      );

      if (!response.ok) {
        throw new Error('Ошибка удаления');
      }

      // Удаляем локально
      setMessages(prev => prev.filter(msg => msg.id !== messageId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка удаления');
    }
  };

  // Обработчик озвучивания текста
  const handleSpeakText = (text: string, messageId: string) => {
    setSpeakingMessageId(messageId);
    voice.speak(text);
    
    // Сброс состояния после завершения (примерная длительность)
    const estimatedDuration = (text.length / 15) * 1000; // ~15 символов в секунду
    setTimeout(() => {
      setSpeakingMessageId(null);
    }, estimatedDuration);
  };

  const handleStopSpeaking = () => {
    voice.stopSpeaking();
    setSpeakingMessageId(null);
  };

  return (
    <div className="flex flex-col h-full">

      {/* Область сообщений */}
      <div 
        ref={chatContainerRef}
        className="
          flex-1 overflow-y-auto p-4 space-y-4
          scrollbar-thin scrollbar-thumb-glass-border scrollbar-track-transparent
        "
      >
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="text-6xl mb-4">💬</div>
            <h3 className="text-xl font-semibold text-text-primary mb-2">
              Начните диалог с EDIS
            </h3>
            <p className="text-text-secondary max-w-md">
              Задайте любой вопрос или попросите помощи. Я здесь, чтобы помочь вам!
            </p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                onRegenerate={
                  message.role === 'assistant' && !message.isStreaming
                    ? handleRegenerate
                    : undefined
                }
                onDelete={handleDelete}
                onSpeak={
                  message.role === 'assistant' && !message.isStreaming
                    ? (text) => handleSpeakText(text, message.id)
                    : undefined
                }
                isSpeaking={speakingMessageId === message.id}
                onStopSpeaking={handleStopSpeaking}
              />
            ))}
            
            {/* Typing Indicator */}
            {isLoading && messages.length > 0 && messages[messages.length - 1].role === 'user' && (
              <div className="flex items-start gap-3 animate-fade-in">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center text-white font-bold shadow-glow">
                  E
                </div>
                <div className="flex-1 bg-message-assistant/50 backdrop-blur-sm border border-border-subtle rounded-2xl px-4 py-3 shadow-elevated">
                  <div className="flex items-center gap-2">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-accent-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-accent-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-accent-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                    <span className="text-text-secondary text-sm ml-2">EDIS печатает...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Ошибка */}
      {error && (
        <div className="px-4 py-2 bg-red-500/10 border-t border-red-500/20 text-red-400 text-sm backdrop-blur-md">
          ⚠️ {error}
        </div>
      )}

      {/* Поле ввода */}
      <div className="p-4 bg-bg-secondary/30 backdrop-blur-md border-t border-glass-border/30">
        <ChatInput
          onSend={sendMessage}
          disabled={isLoading}
          placeholder={isLoading ? "EDIS печатает..." : "Напишите сообщение..."}
        />
      </div>
    </div>
  );
}
