"""
Database layer для хранения настроек с шифрованием
"""
import sqlite3
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from loguru import logger

from models.settings_models import (
    FullSettings, ModelSettings, AutonomySettings, 
    ToolsSettings, SystemSettings, ModelConfig
)


class SettingsDatabase:
    """Управление базой данных настроек"""
    
    def __init__(self, db_path: str = "web/backend/data/settings.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Инициализация шифрования
        self.cipher = self._init_encryption()
        
        # Создание таблиц
        self.create_tables()
        
        logger.info(f"SettingsDatabase инициализирована: {self.db_path}")
    
    def _init_encryption(self) -> Fernet:
        """Инициализация шифрования"""
        env_path = Path(".env")
        encryption_key = None
        
        # Попытка загрузить ключ из .env
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith("ENCRYPTION_KEY="):
                        encryption_key = line.split("=", 1)[1].strip()
                        break
        
        # Генерация нового ключа если не найден
        if not encryption_key:
            encryption_key = Fernet.generate_key().decode()
            logger.warning("Генерация нового ключа шифрования")
            
            # Сохранение в .env
            with open(env_path, 'a') as f:
                f.write(f"\n# Ключ шифрования для настроек (НЕ УДАЛЯТЬ!)\n")
                f.write(f"ENCRYPTION_KEY={encryption_key}\n")
            
            logger.info("Ключ шифрования сохранен в .env")
        
        return Fernet(encryption_key.encode())
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Шифрование чувствительных данных"""
        if not data:
            return ""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Дешифрование чувствительных данных"""
        if not encrypted_data:
            return ""
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            logger.error(f"Ошибка дешифрования: {e}")
            return ""
    
    def mask_token(self, token: str) -> str:
        """Маскирование токена для отображения"""
        if not token or len(token) < 8:
            return "••••••••"
        return "••••••••" + token[-4:]
    
    def create_tables(self):
        """Создание таблиц БД"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица настроек моделей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                creator_base_url TEXT NOT NULL,
                creator_api_key TEXT NOT NULL,
                creator_model_name TEXT NOT NULL,
                creator_temperature REAL DEFAULT 0.8,
                creator_max_tokens INTEGER DEFAULT 4096,
                creator_top_p REAL DEFAULT 0.95,
                
                logic_base_url TEXT NOT NULL,
                logic_api_key TEXT NOT NULL,
                logic_model_name TEXT NOT NULL,
                logic_temperature REAL DEFAULT 0.3,
                logic_max_tokens INTEGER DEFAULT 8192,
                logic_top_p REAL DEFAULT 0.9,
                
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица настроек автономности
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS autonomy_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                enabled BOOLEAN DEFAULT 0,
                tavily_api_key TEXT,
                github_token TEXT,
                check_interval INTEGER DEFAULT 3600,
                max_articles INTEGER DEFAULT 5,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица настроек инструментов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tools_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                sandbox_timeout INTEGER DEFAULT 30,
                sandbox_memory TEXT DEFAULT '512m',
                browser_headless BOOLEAN DEFAULT 1,
                browser_timeout INTEGER DEFAULT 30000,
                tts_enabled BOOLEAN DEFAULT 0,
                tts_api_url TEXT DEFAULT 'http://localhost:9880',
                tts_speaker_name TEXT DEFAULT 'default',
                tts_language TEXT DEFAULT 'ru',
                output_dir TEXT DEFAULT 'outputs',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица системных настроек
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                qdrant_host TEXT DEFAULT 'localhost',
                qdrant_port INTEGER DEFAULT 6333,
                qdrant_collection TEXT DEFAULT 'dual_qwen_memory',
                qdrant_vector_size INTEGER DEFAULT 1024,
                max_conflict_retries INTEGER DEFAULT 3,
                conflict_threshold REAL DEFAULT 0.7,
                log_level TEXT DEFAULT 'INFO',
                log_file TEXT DEFAULT 'logs/dual_qwen_brain.log',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        logger.info("Таблицы БД созданы/проверены")
    
    def save_settings(self, settings: FullSettings) -> bool:
        """Сохранение настроек в БД"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Сохранение настроек моделей
            cursor.execute("""
                INSERT OR REPLACE INTO model_settings (
                    id, creator_base_url, creator_api_key, creator_model_name,
                    creator_temperature, creator_max_tokens, creator_top_p,
                    logic_base_url, logic_api_key, logic_model_name,
                    logic_temperature, logic_max_tokens, logic_top_p,
                    updated_at
                ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                settings.models.creator.base_url,
                self.encrypt_sensitive_data(settings.models.creator.api_key),
                settings.models.creator.model_name,
                settings.models.creator.temperature,
                settings.models.creator.max_tokens,
                settings.models.creator.top_p,
                settings.models.logic.base_url,
                self.encrypt_sensitive_data(settings.models.logic.api_key),
                settings.models.logic.model_name,
                settings.models.logic.temperature,
                settings.models.logic.max_tokens,
                settings.models.logic.top_p
            ))
            
            # Сохранение настроек автономности
            cursor.execute("""
                INSERT OR REPLACE INTO autonomy_settings (
                    id, enabled, tavily_api_key, github_token,
                    check_interval, max_articles, updated_at
                ) VALUES (1, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                1 if settings.autonomy.enabled else 0,
                self.encrypt_sensitive_data(settings.autonomy.tavily_api_key or ""),
                self.encrypt_sensitive_data(settings.autonomy.github_token or ""),
                settings.autonomy.check_interval,
                settings.autonomy.max_articles
            ))
            
            # Сохранение настроек инструментов
            cursor.execute("""
                INSERT OR REPLACE INTO tools_settings (
                    id, sandbox_timeout, sandbox_memory, browser_headless,
                    browser_timeout, tts_enabled, tts_api_url, tts_speaker_name,
                    tts_language, output_dir, updated_at
                ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                settings.tools.sandbox_timeout,
                settings.tools.sandbox_memory,
                1 if settings.tools.browser_headless else 0,
                settings.tools.browser_timeout,
                1 if settings.tools.tts_enabled else 0,
                settings.tools.tts_api_url,
                settings.tools.tts_speaker_name,
                settings.tools.tts_language,
                settings.tools.output_dir
            ))
            
            # Сохранение системных настроек
            cursor.execute("""
                INSERT OR REPLACE INTO system_settings (
                    id, qdrant_host, qdrant_port, qdrant_collection,
                    qdrant_vector_size, max_conflict_retries, conflict_threshold,
                    log_level, log_file, updated_at
                ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                settings.system.qdrant_host,
                settings.system.qdrant_port,
                settings.system.qdrant_collection,
                settings.system.qdrant_vector_size,
                settings.system.max_conflict_retries,
                settings.system.conflict_threshold,
                settings.system.log_level,
                settings.system.log_file
            ))
            
            conn.commit()
            conn.close()
            
            logger.info("Настройки успешно сохранены в БД")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения настроек: {e}")
            return False
    
    def load_settings(self, mask_tokens: bool = False) -> FullSettings:
        """Загрузка настроек из БД"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Загрузка настроек моделей
        cursor.execute("SELECT * FROM model_settings WHERE id = 1")
        model_row = cursor.fetchone()
        
        if model_row:
            creator_api_key = self.decrypt_sensitive_data(model_row['creator_api_key'])
            logic_api_key = self.decrypt_sensitive_data(model_row['logic_api_key'])
            
            if mask_tokens:
                creator_api_key = self.mask_token(creator_api_key)
                logic_api_key = self.mask_token(logic_api_key)
            
            models = ModelSettings(
                creator=ModelConfig(
                    base_url=model_row['creator_base_url'],
                    api_key=creator_api_key,
                    model_name=model_row['creator_model_name'],
                    temperature=model_row['creator_temperature'],
                    max_tokens=model_row['creator_max_tokens'],
                    top_p=model_row['creator_top_p']
                ),
                logic=ModelConfig(
                    base_url=model_row['logic_base_url'],
                    api_key=logic_api_key,
                    model_name=model_row['logic_model_name'],
                    temperature=model_row['logic_temperature'],
                    max_tokens=model_row['logic_max_tokens'],
                    top_p=model_row['logic_top_p']
                )
            )
        else:
            models = ModelSettings()
        
        # Загрузка настроек автономности
        cursor.execute("SELECT * FROM autonomy_settings WHERE id = 1")
        autonomy_row = cursor.fetchone()
        
        if autonomy_row:
            tavily_key = self.decrypt_sensitive_data(autonomy_row['tavily_api_key'] or "")
            github_token = self.decrypt_sensitive_data(autonomy_row['github_token'] or "")
            
            if mask_tokens:
                tavily_key = self.mask_token(tavily_key) if tavily_key else None
                github_token = self.mask_token(github_token) if github_token else None
            
            autonomy = AutonomySettings(
                enabled=bool(autonomy_row['enabled']),
                tavily_api_key=tavily_key,
                github_token=github_token,
                check_interval=autonomy_row['check_interval'],
                max_articles=autonomy_row['max_articles']
            )
        else:
            autonomy = AutonomySettings()
        
        # Загрузка настроек инструментов
        cursor.execute("SELECT * FROM tools_settings WHERE id = 1")
        tools_row = cursor.fetchone()
        
        if tools_row:
            tools = ToolsSettings(
                sandbox_timeout=tools_row['sandbox_timeout'],
                sandbox_memory=tools_row['sandbox_memory'],
                browser_headless=bool(tools_row['browser_headless']),
                browser_timeout=tools_row['browser_timeout'],
                tts_enabled=bool(tools_row['tts_enabled']),
                tts_api_url=tools_row['tts_api_url'],
                tts_speaker_name=tools_row['tts_speaker_name'],
                tts_language=tools_row['tts_language'],
                output_dir=tools_row['output_dir']
            )
        else:
            tools = ToolsSettings()
        
        # Загрузка системных настроек
        cursor.execute("SELECT * FROM system_settings WHERE id = 1")
        system_row = cursor.fetchone()
        
        if system_row:
            system = SystemSettings(
                qdrant_host=system_row['qdrant_host'],
                qdrant_port=system_row['qdrant_port'],
                qdrant_collection=system_row['qdrant_collection'],
                qdrant_vector_size=system_row['qdrant_vector_size'],
                max_conflict_retries=system_row['max_conflict_retries'],
                conflict_threshold=system_row['conflict_threshold'],
                log_level=system_row['log_level'],
                log_file=system_row['log_file']
            )
        else:
            system = SystemSettings()
        
        conn.close()
        
        return FullSettings(
            models=models,
            autonomy=autonomy,
            tools=tools,
            system=system
        )
    
    def settings_exist(self) -> bool:
        """Проверка наличия настроек в БД"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM model_settings WHERE id = 1")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count > 0


# Глобальный экземпляр
_db_instance: Optional[SettingsDatabase] = None


def get_settings_db() -> SettingsDatabase:
    """Получение глобального экземпляра БД"""
    global _db_instance
    if _db_instance is None:
        _db_instance = SettingsDatabase()
    return _db_instance
