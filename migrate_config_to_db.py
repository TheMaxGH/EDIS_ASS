"""
Скрипт миграции настроек из config.yaml в SQLite базу данных
Использование: python migrate_config_to_db.py
"""
import yaml
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent))

from web.backend.database.settings_db import SettingsDatabase
from web.backend.models.settings_models import (
    ModelConfig,
    ModelSettings,
    AutonomySettings,
    ToolsSettings,
    SystemSettings,
    FullSettings
)


def load_config_yaml(config_path: str = "config/config.yaml") -> dict:
    """Загрузка config.yaml"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        print(f"✓ Загружен config.yaml из {config_path}")
        return config
    except FileNotFoundError:
        print(f"✗ Файл {config_path} не найден")
        return None
    except Exception as e:
        print(f"✗ Ошибка чтения config.yaml: {e}")
        return None


def migrate_to_database(config: dict) -> bool:
    """Миграция настроек в базу данных"""
    try:
        # Создаём экземпляр базы данных
        db = SettingsDatabase()
        
        # Извлекаем настройки из config.yaml
        models_config = config.get('models', {})
        autonomy_config = config.get('autonomy', {})
        tools_config = config.get('tools', {})
        system_config = config.get('system', {})
        
        # Создаём объекты настроек
        creator_model = ModelConfig(
            base_url=models_config.get('creator', {}).get('base_url', 'http://localhost:8001/v1'),
            api_key=models_config.get('creator', {}).get('api_key', 'dummy-key'),
            model_name=models_config.get('creator', {}).get('model_name', 'Qwen/Qwen2.5-72B-Instruct'),
            temperature=models_config.get('creator', {}).get('temperature', 0.8),
            max_tokens=models_config.get('creator', {}).get('max_tokens', 4096),
            top_p=models_config.get('creator', {}).get('top_p', 0.95)
        )
        
        logic_model = ModelConfig(
            base_url=models_config.get('logic', {}).get('base_url', 'http://localhost:8002/v1'),
            api_key=models_config.get('logic', {}).get('api_key', 'dummy-key'),
            model_name=models_config.get('logic', {}).get('model_name', 'Qwen/Qwen3.5-397B-A17B-FP8'),
            temperature=models_config.get('logic', {}).get('temperature', 0.3),
            max_tokens=models_config.get('logic', {}).get('max_tokens', 8192),
            top_p=models_config.get('logic', {}).get('top_p', 0.9)
        )
        
        model_settings = ModelSettings(
            creator=creator_model,
            logic=logic_model
        )
        
        autonomy_settings = AutonomySettings(
            enabled=autonomy_config.get('enabled', False),
            tavily_api_key=autonomy_config.get('tavily_api_key'),
            github_token=autonomy_config.get('github_token'),
            check_interval=autonomy_config.get('check_interval', 3600),
            max_articles=autonomy_config.get('max_articles', 5)
        )
        
        tools_settings = ToolsSettings(
            sandbox_timeout=tools_config.get('sandbox', {}).get('timeout', 30),
            sandbox_memory=tools_config.get('sandbox', {}).get('memory', '512m'),
            browser_headless=tools_config.get('browser', {}).get('headless', True),
            browser_timeout=tools_config.get('browser', {}).get('timeout', 30000),
            tts_enabled=tools_config.get('tts', {}).get('enabled', False),
            tts_api_url=tools_config.get('tts', {}).get('api_url', 'http://localhost:9880'),
            tts_speaker_name=tools_config.get('tts', {}).get('speaker_name', 'default'),
            tts_language=tools_config.get('tts', {}).get('language', 'ru'),
            output_dir=tools_config.get('doc_engine', {}).get('output_dir', 'outputs')
        )
        
        system_settings = SystemSettings(
            qdrant_host=system_config.get('qdrant', {}).get('host', 'localhost'),
            qdrant_port=system_config.get('qdrant', {}).get('port', 6333),
            qdrant_collection=system_config.get('qdrant', {}).get('collection', 'dual_qwen_memory'),
            qdrant_vector_size=system_config.get('qdrant', {}).get('vector_size', 1024),
            max_conflict_retries=system_config.get('workflow', {}).get('max_conflict_retries', 3),
            conflict_threshold=system_config.get('workflow', {}).get('conflict_threshold', 0.7),
            log_level=system_config.get('logging', {}).get('level', 'INFO'),
            log_file=system_config.get('logging', {}).get('file', 'logs/dual_qwen_brain.log')
        )
        
        full_settings = FullSettings(
            models=model_settings,
            autonomy=autonomy_settings,
            tools=tools_settings,
            system=system_settings
        )
        
        # Сохраняем в базу данных
        db.save_settings(full_settings)
        
        print("\n✓ Настройки успешно мигрированы в базу данных!")
        print(f"  - База данных: {db.db_path}")
        print(f"  - Ключ шифрования сохранён в .env")
        
        # Показываем замаскированные токены
        print("\n📊 Мигрированные настройки:")
        print(f"  Models:")
        print(f"    - Creator: {creator_model.base_url}")
        print(f"    - Logic: {logic_model.base_url}")
        print(f"  Autonomy:")
        print(f"    - Enabled: {autonomy_settings.enabled}")
        if autonomy_settings.tavily_api_key:
            print(f"    - Tavily API Key: {db.mask_token(autonomy_settings.tavily_api_key)}")
        if autonomy_settings.github_token:
            print(f"    - GitHub Token: {db.mask_token(autonomy_settings.github_token)}")
        print(f"  Tools:")
        print(f"    - Sandbox timeout: {tools_settings.sandbox_timeout}s")
        print(f"    - Browser headless: {tools_settings.browser_headless}")
        print(f"    - TTS enabled: {tools_settings.tts_enabled}")
        print(f"  System:")
        print(f"    - Qdrant: {system_settings.qdrant_host}:{system_settings.qdrant_port}")
        print(f"    - Log level: {system_settings.log_level}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Ошибка миграции: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Главная функция"""
    print("=" * 60)
    print("🔄 Миграция настроек из config.yaml в SQLite")
    print("=" * 60)
    print()
    
    # Загружаем config.yaml
    config = load_config_yaml()
    if not config:
        print("\n⚠️  Не удалось загрузить config.yaml")
        print("Будут использованы настройки по умолчанию")
        config = {}
    
    # Мигрируем в базу данных
    success = migrate_to_database(config)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Миграция завершена успешно!")
        print("=" * 60)
        print("\n💡 Теперь вы можете:")
        print("  1. Запустить веб-интерфейс: cd web/frontend && npm run dev")
        print("  2. Открыть настройки через кнопку ⚙️ в UI")
        print("  3. Изменить настройки через UI вместо config.yaml")
        print("\n⚠️  Рекомендация: создайте резервную копию config.yaml")
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ Миграция завершилась с ошибками")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
