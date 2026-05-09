import React, { useState, useEffect } from 'react';

interface FileInfo {
  name: string;
  path: string;
  size: number;
  is_directory: boolean;
  modified: string;
  mime_type?: string;
}

interface DirectoryListing {
  current_path: string;
  parent_path?: string;
  files: FileInfo[];
}

interface FileManagerProps {
  serverUrl: string;
  apiKey: string;
}

export default function FileManager({ serverUrl, apiKey }: FileManagerProps) {
  const [listing, setListing] = useState<DirectoryListing | null>(null);
  const [currentPath, setCurrentPath] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<FileInfo | null>(null);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [newFolderName, setNewFolderName] = useState('');
  const [showNewFolder, setShowNewFolder] = useState(false);

  // Загрузка списка файлов
  const loadFiles = async (path: string = '') => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        `${serverUrl}/api/v1/sandbox/files?path=${encodeURIComponent(path)}`,
        {
          headers: {
            'X-API-Key': apiKey,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Не удалось загрузить файлы');
      }

      const data = await response.json();
      setListing(data);
      setCurrentPath(path);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки');
    } finally {
      setIsLoading(false);
    }
  };

  // Загрузка при монтировании
  useEffect(() => {
    loadFiles();
  }, []);

  // Открыть директорию
  const openDirectory = (file: FileInfo) => {
    if (file.is_directory) {
      loadFiles(file.path);
    }
  };

  // Вернуться назад
  const goBack = () => {
    if (listing?.parent_path !== undefined) {
      loadFiles(listing.parent_path);
    }
  };

  // Загрузка файла
  const handleUpload = async () => {
    if (!uploadFile) return;

    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('path', currentPath);

      const response = await fetch(`${serverUrl}/api/v1/sandbox/upload`, {
        method: 'POST',
        headers: {
          'X-API-Key': apiKey,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Не удалось загрузить файл');
      }

      setUploadFile(null);
      await loadFiles(currentPath);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки');
    } finally {
      setIsLoading(false);
    }
  };

  // Скачать файл
  const handleDownload = async (file: FileInfo) => {
    try {
      const response = await fetch(
        `${serverUrl}/api/v1/sandbox/download/${encodeURIComponent(file.path)}`,
        {
          headers: {
            'X-API-Key': apiKey,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Не удалось скачать файл');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = file.name;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка скачивания');
    }
  };

  // Создать папку
  const handleCreateFolder = async () => {
    if (!newFolderName.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const newPath = currentPath ? `${currentPath}/${newFolderName}` : newFolderName;
      
      const response = await fetch(`${serverUrl}/api/v1/sandbox/directory`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey,
        },
        body: JSON.stringify({ path: newPath }),
      });

      if (!response.ok) {
        throw new Error('Не удалось создать папку');
      }

      setNewFolderName('');
      setShowNewFolder(false);
      await loadFiles(currentPath);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка создания папки');
    } finally {
      setIsLoading(false);
    }
  };

  // Удалить файл/папку
  const handleDelete = async (file: FileInfo) => {
    if (!confirm(`Удалить ${file.is_directory ? 'папку' : 'файл'} "${file.name}"?`)) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${serverUrl}/api/v1/sandbox/delete`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey,
        },
        body: JSON.stringify({ path: file.path }),
      });

      if (!response.ok) {
        throw new Error('Не удалось удалить');
      }

      setSelectedFile(null);
      await loadFiles(currentPath);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка удаления');
    } finally {
      setIsLoading(false);
    }
  };

  // Форматирование размера
  const formatSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
  };

  // Иконка файла
  const getFileIcon = (file: FileInfo): string => {
    if (file.is_directory) return '📁';
    
    const ext = file.name.split('.').pop()?.toLowerCase();
    const iconMap: Record<string, string> = {
      'py': '🐍',
      'js': '📜',
      'ts': '📘',
      'json': '📋',
      'md': '📝',
      'txt': '📄',
      'pdf': '📕',
      'zip': '📦',
      'png': '🖼️',
      'jpg': '🖼️',
      'jpeg': '🖼️',
      'gif': '🖼️',
    };
    
    return iconMap[ext || ''] || '📄';
  };

  return (
    <div className="flex flex-col h-full">
      {/* Заголовок и панель инструментов */}
      <div className="p-4 bg-bg-secondary/50 backdrop-blur-md border-b border-glass-border/30">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-text-primary">📂 Файловый менеджер</h2>
          
          <div className="flex items-center gap-2">
            {/* Кнопка обновить */}
            <button
              onClick={() => loadFiles(currentPath)}
              disabled={isLoading}
              className="
                px-3 py-1.5 rounded-lg text-sm
                bg-bg-secondary/50 hover:bg-accent-primary/20
                border border-glass-border/30 hover:border-accent-primary/50
                text-text-secondary hover:text-accent-primary
                transition-all duration-200
                hover:scale-105 active:scale-95
                disabled:opacity-50
              "
            >
              🔄 Обновить
            </button>

            {/* Кнопка новая папка */}
            <button
              onClick={() => setShowNewFolder(!showNewFolder)}
              disabled={isLoading}
              className="
                px-3 py-1.5 rounded-lg text-sm
                bg-bg-secondary/50 hover:bg-accent-secondary/20
                border border-glass-border/30 hover:border-accent-secondary/50
                text-text-secondary hover:text-accent-secondary
                transition-all duration-200
                hover:scale-105 active:scale-95
                disabled:opacity-50
              "
            >
              📁+ Новая папка
            </button>
          </div>
        </div>

        {/* Хлебные крошки */}
        <div className="flex items-center gap-2 text-sm text-text-secondary">
          <button
            onClick={() => loadFiles('')}
            className="hover:text-accent-primary transition-colors"
          >
            🏠 Корень
          </button>
          {currentPath && (
            <>
              <span>/</span>
              <span className="text-text-primary">{currentPath}</span>
              {listing?.parent_path !== undefined && (
                <button
                  onClick={goBack}
                  className="ml-2 px-2 py-1 rounded bg-bg-secondary/50 hover:bg-accent-primary/20 border border-glass-border/30 hover:border-accent-primary/50 transition-all"
                >
                  ⬅️ Назад
                </button>
              )}
            </>
          )}
        </div>

        {/* Форма новой папки */}
        {showNewFolder && (
          <div className="mt-3 flex items-center gap-2">
            <input
              type="text"
              value={newFolderName}
              onChange={(e) => setNewFolderName(e.target.value)}
              placeholder="Имя папки"
              className="
                flex-1 px-3 py-2 rounded-lg
                bg-bg-secondary/70 border border-glass-border/50
                text-text-primary placeholder-text-secondary/50
                focus:border-accent-primary/50 focus:outline-none
                transition-all
              "
              onKeyDown={(e) => e.key === 'Enter' && handleCreateFolder()}
            />
            <button
              onClick={handleCreateFolder}
              disabled={!newFolderName.trim() || isLoading}
              className="
                px-3 py-2 rounded-lg text-sm
                bg-gradient-to-br from-accent-primary/80 to-accent-secondary/80
                hover:from-accent-primary hover:to-accent-secondary
                border border-accent-primary/30
                transition-all duration-200
                hover:scale-105 active:scale-95
                disabled:opacity-30
              "
            >
              Создать
            </button>
            <button
              onClick={() => {
                setShowNewFolder(false);
                setNewFolderName('');
              }}
              className="
                px-3 py-2 rounded-lg text-sm
                bg-bg-secondary/50 hover:bg-red-500/20
                border border-glass-border/30 hover:border-red-500/50
                text-text-secondary hover:text-red-400
                transition-all duration-200
              "
            >
              Отмена
            </button>
          </div>
        )}

        {/* Загрузка файла */}
        <div className="mt-3 flex items-center gap-2">
          <input
            type="file"
            onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
            className="
              flex-1 text-sm text-text-secondary
              file:mr-4 file:py-2 file:px-4
              file:rounded-lg file:border-0
              file:text-sm file:font-medium
              file:bg-bg-secondary/50 file:text-text-primary
              file:hover:bg-accent-primary/20
              file:transition-all file:cursor-pointer
            "
          />
          <button
            onClick={handleUpload}
            disabled={!uploadFile || isLoading}
            className="
              px-3 py-2 rounded-lg text-sm
              bg-gradient-to-br from-accent-tertiary/80 to-accent-primary/80
              hover:from-accent-tertiary hover:to-accent-primary
              border border-accent-tertiary/30
              transition-all duration-200
              hover:scale-105 active:scale-95
              disabled:opacity-30
            "
          >
            ⬆️ Загрузить
          </button>
        </div>
      </div>

      {/* Ошибка */}
      {error && (
        <div className="px-4 py-2 bg-red-500/10 border-b border-red-500/20 text-red-400 text-sm">
          ⚠️ {error}
        </div>
      )}

      {/* Список файлов */}
      <div className="flex-1 overflow-y-auto p-4 scrollbar-thin scrollbar-thumb-glass-border scrollbar-track-transparent">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-text-secondary">Загрузка...</div>
          </div>
        ) : listing && listing.files.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="text-6xl mb-4">📂</div>
            <p className="text-text-secondary">Папка пуста</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {listing?.files.map((file) => (
              <div
                key={file.path}
                className={`
                  p-3 rounded-xl
                  bg-bg-secondary/70 backdrop-blur-md
                  border transition-all duration-200
                  hover:scale-105 cursor-pointer
                  ${selectedFile?.path === file.path
                    ? 'border-accent-primary/50 shadow-lg shadow-accent-primary/20'
                    : 'border-glass-border/50 hover:border-accent-primary/30'
                  }
                `}
                onClick={() => setSelectedFile(file)}
                onDoubleClick={() => file.is_directory && openDirectory(file)}
              >
                <div className="flex items-start justify-between mb-2">
                  <span className="text-3xl">{getFileIcon(file)}</span>
                  <div className="flex gap-1">
                    {!file.is_directory && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDownload(file);
                        }}
                        className="p-1 rounded hover:bg-accent-primary/20 transition-colors"
                        title="Скачать"
                      >
                        ⬇️
                      </button>
                    )}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(file);
                      }}
                      className="p-1 rounded hover:bg-red-500/20 transition-colors"
                      title="Удалить"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
                <div className="text-sm font-medium text-text-primary truncate" title={file.name}>
                  {file.name}
                </div>
                {!file.is_directory && (
                  <div className="text-xs text-text-secondary mt-1">
                    {formatSize(file.size)}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
