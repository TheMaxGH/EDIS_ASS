/**
 * Message Bubble Component
 * Редизайн в стиле OpenWebUI
 * User: справа, фиолетовый градиент
 * Assistant: слева, темно-серый
 */

import React from 'react';
import { User, Bot, Copy, Check, Volume2, VolumeX } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/cjs/styles/prism';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  isStreaming?: boolean;
}

interface MessageBubbleProps {
  message: Message;
  onRegenerate?: (messageId: string) => void;
  onDelete?: (messageId: string) => void;
  onSpeak?: (text: string) => void;
  isSpeaking?: boolean;
  onStopSpeaking?: () => void;
}

export default function MessageBubble({
  message,
  onRegenerate,
  onDelete,
  onSpeak,
  isSpeaking = false,
  onStopSpeaking
}: MessageBubbleProps) {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isUser = message.role === 'user';
  const { content, timestamp, isStreaming = false } = message;

  return (
    <div className={`flex gap-4 mb-6 animate-slide-up ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div className={`
        flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center
        ${isUser 
          ? 'bg-gradient-purple shadow-glow-purple-sm' 
          : 'bg-gray-700 border border-gray-600'
        }
      `}>
        {isUser ? (
          <User className="w-5 h-5 text-white" />
        ) : (
          <Bot className="w-5 h-5 text-gray-300" />
        )}
      </div>

      {/* Message Content */}
      <div className={`flex-1 min-w-0 ${isUser ? 'flex flex-col items-end' : ''}`}>
        {/* Header */}
        <div className={`flex items-center gap-2 mb-2 ${isUser ? 'flex-row-reverse' : ''}`}>
          <span className={`text-sm font-semibold ${
            isUser ? 'text-primary-purple' : 'text-gray-300'
          }`}>
            {isUser ? 'Вы' : 'EDIS AI'}
          </span>
          {timestamp && (
            <span className="text-xs text-text-muted">
              {new Date(timestamp).toLocaleTimeString('ru-RU', { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </span>
          )}
        </div>

        {/* Message Bubble */}
        <div className={`
          relative group max-w-[85%]
          ${isUser 
            ? 'bg-gradient-purple text-white rounded-2xl rounded-tr-sm' 
            : 'bg-gray-800 text-gray-100 rounded-2xl rounded-tl-sm border border-gray-700'
          }
          px-4 py-3 shadow-card
        `}>
          {isUser ? (
            // User message - simple text
            <p className="text-sm whitespace-pre-wrap break-words">
              {content}
            </p>
          ) : (
            // Assistant message - markdown with code highlighting
            <div className="prose prose-invert prose-sm max-w-none">
              <ReactMarkdown
                components={{
                  code({ node, className, children, ...props }: any) {
                    const match = /language-(\w+)/.exec(className || '');
                    const codeString = String(children).replace(/\n$/, '');
                    const inline = !className;
                    
                    return !inline && match ? (
                      <div className="relative group/code my-3">
                        {/* Copy button */}
                        <button
                          onClick={() => handleCopy(codeString)}
                          className="absolute top-2 right-2 p-2 rounded-lg bg-gray-700 hover:bg-gray-600 opacity-0 group-hover/code:opacity-100 transition-opacity z-10"
                          title="Копировать код"
                        >
                          {copied ? (
                            <Check className="w-4 h-4 text-green-400" />
                          ) : (
                            <Copy className="w-4 h-4 text-gray-300" />
                          )}
                        </button>
                        
                        {/* Code block */}
                        <SyntaxHighlighter
                          style={vscDarkPlus}
                          language={match[1]}
                          PreTag="div"
                          className="rounded-lg !bg-gray-900 !mt-0 !mb-0"
                          customStyle={{
                            margin: 0,
                            padding: '1rem',
                            fontSize: '0.875rem',
                            lineHeight: '1.5'
                          }}
                          {...props}
                        >
                          {codeString}
                        </SyntaxHighlighter>
                      </div>
                    ) : (
                      <code 
                        className="px-1.5 py-0.5 rounded bg-gray-700 text-accent-orange font-mono text-xs"
                        {...props}
                      >
                        {children}
                      </code>
                    );
                  },
                  p({ children }) {
                    return <p className="mb-3 last:mb-0 text-sm leading-relaxed">{children}</p>;
                  },
                  ul({ children }) {
                    return <ul className="list-disc list-inside mb-3 space-y-1 text-sm">{children}</ul>;
                  },
                  ol({ children }) {
                    return <ol className="list-decimal list-inside mb-3 space-y-1 text-sm">{children}</ol>;
                  },
                  li({ children }) {
                    return <li className="text-gray-200">{children}</li>;
                  },
                  a({ href, children }) {
                    return (
                      <a 
                        href={href} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-primary-purple hover:text-accent-orange underline transition-colors"
                      >
                        {children}
                      </a>
                    );
                  },
                  blockquote({ children }) {
                    return (
                      <blockquote className="border-l-4 border-primary-purple pl-4 italic text-gray-300 my-3">
                        {children}
                      </blockquote>
                    );
                  },
                  h1({ children }) {
                    return <h1 className="text-xl font-bold mb-3 text-white">{children}</h1>;
                  },
                  h2({ children }) {
                    return <h2 className="text-lg font-bold mb-2 text-white">{children}</h2>;
                  },
                  h3({ children }) {
                    return <h3 className="text-base font-bold mb-2 text-white">{children}</h3>;
                  },
                  table({ children }) {
                    return (
                      <div className="overflow-x-auto my-3">
                        <table className="min-w-full border border-gray-700 rounded-lg">
                          {children}
                        </table>
                      </div>
                    );
                  },
                  thead({ children }) {
                    return <thead className="bg-gray-700">{children}</thead>;
                  },
                  tbody({ children }) {
                    return <tbody className="divide-y divide-gray-700">{children}</tbody>;
                  },
                  tr({ children }) {
                    return <tr>{children}</tr>;
                  },
                  th({ children }) {
                    return (
                      <th className="px-4 py-2 text-left text-xs font-semibold text-gray-200 uppercase tracking-wider">
                        {children}
                      </th>
                    );
                  },
                  td({ children }) {
                    return <td className="px-4 py-2 text-sm text-gray-300">{children}</td>;
                  },
                }}
              >
                {content}
              </ReactMarkdown>
            </div>
          )}

          {/* Streaming indicator */}
          {isStreaming && (
            <div className="flex items-center gap-1 mt-2">
              <div className="w-2 h-2 bg-primary-purple rounded-full animate-pulse" />
              <div className="w-2 h-2 bg-primary-purple rounded-full animate-pulse delay-75" />
              <div className="w-2 h-2 bg-primary-purple rounded-full animate-pulse delay-150" />
            </div>
          )}
        </div>

        {/* Action buttons for assistant messages */}
        {!isUser && !isStreaming && (
          <div className="mt-2 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            {/* Copy button */}
            <button
              onClick={() => handleCopy(content)}
              className="px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 border border-gray-700 text-xs text-gray-300 transition-colors flex items-center gap-2"
              title="Копировать"
            >
              {copied ? (
                <>
                  <Check className="w-3 h-3 text-green-400" />
                  <span>Скопировано</span>
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3" />
                  <span>Копировать</span>
                </>
              )}
            </button>

            {/* Speak button */}
            {onSpeak && (
              <button
                onClick={() => isSpeaking ? onStopSpeaking?.() : onSpeak(content)}
                className={`px-3 py-1.5 rounded-lg border text-xs transition-colors flex items-center gap-2 ${
                  isSpeaking
                    ? 'bg-primary-purple/20 border-primary-purple text-primary-purple hover:bg-primary-purple/30'
                    : 'bg-gray-800 hover:bg-gray-700 border-gray-700 text-gray-300'
                }`}
                title={isSpeaking ? "Остановить озвучку" : "Озвучить"}
              >
                {isSpeaking ? (
                  <>
                    <VolumeX className="w-3 h-3 animate-pulse" />
                    <span>Остановить</span>
                  </>
                ) : (
                  <>
                    <Volume2 className="w-3 h-3" />
                    <span>Озвучить</span>
                  </>
                )}
              </button>
            )}

            {/* Regenerate button */}
            {onRegenerate && (
              <button
                onClick={() => onRegenerate(message.id)}
                className="px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 border border-gray-700 text-xs text-gray-300 transition-colors flex items-center gap-2"
                title="Регенерировать"
              >
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span>Регенерировать</span>
              </button>
            )}

            {/* Delete button */}
            {onDelete && (
              <button
                onClick={() => onDelete(message.id)}
                className="px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-red-900/50 border border-gray-700 hover:border-red-500/50 text-xs text-gray-300 hover:text-red-400 transition-colors flex items-center gap-2"
                title="Удалить"
              >
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                <span>Удалить</span>
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
