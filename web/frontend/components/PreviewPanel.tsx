/**
 * Preview Panel Component
 * Панель предварительного просмотра для кода и артефактов
 * Показывается справа от чата в ChatLayout
 */

import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/cjs/styles/prism';

export interface PreviewContent {
  type: 'code' | 'html' | 'markdown' | 'image' | 'file';
  language?: string;
  content: string;
  filename?: string;
  title?: string;
}

interface PreviewPanelProps {
  content: PreviewContent | null;
  onClose?: () => void;
}

export default function PreviewPanel({ content, onClose }: PreviewPanelProps) {
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');

  if (!content) {
    return (
      <div className="h-full flex items-center justify-center bg-bg-primary border-l border-border-subtle">
        <div className="text-center text-text-secondary p-8">
          <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-sm">Нет контента для предварительного просмотра</p>
        </div>
      </div>
    );
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(content.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([content.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = content.filename || 'download.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const renderPreview = () => {
    switch (content.type) {
      case 'code':
        return (
          <SyntaxHighlighter
            language={content.language || 'text'}
            style={vscDarkPlus}
            customStyle={{
              margin: 0,
              padding: '1.5rem',
              fontSize: '0.875rem',
              lineHeight: '1.6',
              height: '100%',
              background: 'transparent'
            }}
            showLineNumbers
          >
            {content.content}
          </SyntaxHighlighter>
        );

      case 'html':
        return (
          <div className="h-full overflow-auto">
            {activeTab === 'preview' ? (
              <iframe
                srcDoc={content.content}
                className="w-full h-full border-0 bg-white"
                sandbox="allow-scripts"
                title="HTML Preview"
              />
            ) : (
              <SyntaxHighlighter
                language="html"
                style={vscDarkPlus}
                customStyle={{
                  margin: 0,
                  padding: '1.5rem',
                  fontSize: '0.875rem',
                  lineHeight: '1.6',
                  height: '100%',
                  background: 'transparent'
                }}
                showLineNumbers
              >
                {content.content}
              </SyntaxHighlighter>
            )}
          </div>
        );

      case 'markdown':
        return (
          <div className="prose prose-invert max-w-none p-6 overflow-auto h-full">
            <pre className="whitespace-pre-wrap text-sm">{content.content}</pre>
          </div>
        );

      case 'image':
        return (
          <div className="h-full flex items-center justify-center p-6 bg-bg-secondary">
            <img 
              src={content.content} 
              alt={content.title || 'Preview'} 
              className="max-w-full max-h-full object-contain rounded-lg shadow-elevated"
            />
          </div>
        );

      case 'file':
        return (
          <div className="h-full flex items-center justify-center p-6">
            <div className="text-center">
              <svg className="w-20 h-20 mx-auto mb-4 text-accent-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              <p className="text-text-primary font-medium mb-2">{content.filename}</p>
              <p className="text-text-secondary text-sm mb-4">Файл готов к скачиванию</p>
              <button
                onClick={handleDownload}
                className="px-4 py-2 bg-accent-primary hover:bg-accent-hover text-white rounded-lg transition-colors"
              >
                Скачать файл
              </button>
            </div>
          </div>
        );

      default:
        return (
          <pre className="p-6 text-sm text-text-primary whitespace-pre-wrap overflow-auto h-full">
            {content.content}
          </pre>
        );
    }
  };

  return (
    <div className="h-full flex flex-col bg-bg-primary border-l border-border-subtle">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border-subtle bg-bg-secondary/50 backdrop-blur-sm">
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <div className="flex-shrink-0">
            {content.type === 'code' && (
              <svg className="w-5 h-5 text-accent-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
              </svg>
            )}
            {content.type === 'html' && (
              <svg className="w-5 h-5 text-accent-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
              </svg>
            )}
            {content.type === 'image' && (
              <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            )}
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-semibold text-text-primary truncate">
              {content.title || content.filename || 'Предварительный просмотр'}
            </h3>
            {content.language && (
              <p className="text-xs text-text-secondary">{content.language}</p>
            )}
          </div>
        </div>

        {/* Tabs for HTML */}
        {content.type === 'html' && (
          <div className="flex items-center gap-1 mx-4 bg-bg-primary rounded-lg p-1">
            <button
              onClick={() => setActiveTab('preview')}
              className={`px-3 py-1 text-xs rounded transition-colors ${
                activeTab === 'preview'
                  ? 'bg-accent-primary text-white'
                  : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              Просмотр
            </button>
            <button
              onClick={() => setActiveTab('code')}
              className={`px-3 py-1 text-xs rounded transition-colors ${
                activeTab === 'code'
                  ? 'bg-accent-primary text-white'
                  : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              Код
            </button>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="p-2 rounded-lg hover:bg-message-user/30 text-text-secondary hover:text-accent-primary transition-colors"
            title="Копировать"
          >
            {copied ? (
              <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            )}
          </button>

          <button
            onClick={handleDownload}
            className="p-2 rounded-lg hover:bg-message-user/30 text-text-secondary hover:text-accent-primary transition-colors"
            title="Скачать"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </button>

          {onClose && (
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-red-500/20 text-text-secondary hover:text-red-400 transition-colors"
              title="Закрыть"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden bg-bg-secondary/30">
        {renderPreview()}
      </div>
    </div>
  );
}
