#!/usr/bin/env python3
"""
EDIS Assistant - Универсальный стартовый скрипт
Автоматически проверяет, устанавливает и запускает всю систему
"""
import os
import sys
import subprocess
import platform
import logging
from pathlib import Path
from typing import Optional, List

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EDISStarter:
    """Универсальный стартер для EDIS Assistant"""
    
    def __init__(self):
        self.system = platform.system()
        self.project_root = Path(__file__).parent
        self.python_cmd = sys.executable
        
    def print_banner(self):
        """Красивый баннер"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ███████╗██████╗ ██╗███████╗                               ║
║   ██╔════╝██╔══██╗██║██╔════╝                               ║
║   █████╗  ██║  ██║██║███████╗                               ║
║   ██╔══╝  ██║  ██║██║╚════██║                               ║
║   ███████╗██████╔╝██║███████║                               ║
║   ╚══════╝╚═════╝ ╚═╝╚══════╝                               ║
║                                                              ║
║   Enhanced Dual Intelligence System                          ║
║   Автоматический запуск системы                             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        logger.info(f"Система: {self.system}")
        logger.info(f"Python: {sys.version}")
        logger.info(f"Рабочая директория: {self.project_root}")
        print()
    
    def check_python_version(self) -> bool:
        """Проверка версии Python"""
        logger.info("🔍 Проверка версии Python...")
        version = sys.version_info
        
        if version.major < 3 or (version.major == 3 and version.minor < 10):
            logger.error("❌ Требуется Python 3.10 или выше!")
            logger.error(f"   Текущая версия: {version.major}.{version.minor}.{version.micro}")
            return False
        
        logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    
    def check_git(self) -> bool:
        """Проверка наличия Git"""
        logger.info("🔍 Проверка Git...")
        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"✅ {result.stdout.strip()}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        logger.warning("⚠️  Git не найден (опционально)")
        return False
    
    def check_node(self) -> bool:
        """Проверка наличия Node.js"""
        logger.info("🔍 Проверка Node.js...")
        try:
            result = subprocess.run(
                ['node', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"✅ Node.js {result.stdout.strip()}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        logger.error("❌ Node.js не найден!")
        logger.error("   Установите Node.js: https://nodejs.org/")
        return False
    
    def check_docker(self) -> bool:
        """Проверка наличия Docker"""
        logger.info("🔍 Проверка Docker...")
        try:
            result = subprocess.run(
                ['docker', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"✅ {result.stdout.strip()}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        logger.warning("⚠️  Docker не найден (требуется для Qdrant)")
        return False
    
    def install_python_dependencies(self) -> bool:
        """Установка Python зависимостей"""
        logger.info("📦 Установка Python зависимостей...")
        
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            logger.error("❌ requirements.txt не найден!")
            return False
        
        try:
            subprocess.run(
                [self.python_cmd, '-m', 'pip', 'install', '--upgrade', 'pip'],
                check=True,
                timeout=60
            )
            
            subprocess.run(
                [self.python_cmd, '-m', 'pip', 'install', '-r', str(requirements_file)],
                check=True,
                timeout=300
            )
            
            logger.info("✅ Python зависимости установлены")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Ошибка установки зависимостей: {e}")
            return False
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout при установке зависимостей")
            return False
    
    def install_frontend_dependencies(self) -> bool:
        """Установка frontend зависимостей"""
        logger.info("📦 Установка frontend зависимостей...")
        
        frontend_dir = self.project_root / "web" / "frontend"
        if not frontend_dir.exists():
            logger.warning("⚠️  Frontend директория не найдена")
            return False
        
        package_json = frontend_dir / "package.json"
        if not package_json.exists():
            logger.error("❌ package.json не найден!")
            return False
        
        try:
            subprocess.run(
                ['npm', 'install'],
                cwd=str(frontend_dir),
                check=True,
                timeout=300
            )
            
            logger.info("✅ Frontend зависимости установлены")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Ошибка установки frontend: {e}")
            return False
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout при установке frontend")
            return False
    
    def setup_gpt_sovits(self) -> bool:
        """Установка GPT-SoVITS"""
        logger.info("🎤 Проверка GPT-SoVITS...")
        
        setup_script = self.project_root / "setup_gpt_sovits.py"
        if not setup_script.exists():
            logger.warning("⚠️  setup_gpt_sovits.py не найден")
            return False
        
        try:
            result = subprocess.run(
                [self.python_cmd, str(setup_script)],
                timeout=600,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✅ GPT-SoVITS готов")
                return True
            else:
                logger.warning("⚠️  GPT-SoVITS установка завершилась с предупреждениями")
                return True  # Не критично
                
        except subprocess.TimeoutExpired:
            logger.warning("⚠️  Timeout при установке GPT-SoVITS")
            return True  # Не критично
        except Exception as e:
            logger.warning(f"⚠️  Ошибка установки GPT-SoVITS: {e}")
            return True  # Не критично
    
    def check_env_file(self) -> bool:
        """Проверка .env файла"""
        logger.info("🔑 Проверка конфигурации...")
        
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        if not env_file.exists():
            if env_example.exists():
                logger.warning("⚠️  .env не найден, создаю из .env.example...")
                try:
                    import shutil
                    shutil.copy(env_example, env_file)
                    logger.info("✅ .env создан из примера")
                    logger.warning("⚠️  ВАЖНО: Отредактируйте .env и добавьте свои API ключи!")
                except Exception as e:
                    logger.error(f"❌ Ошибка создания .env: {e}")
                    return False
            else:
                logger.error("❌ .env и .env.example не найдены!")
                return False
        else:
            logger.info("✅ .env найден")
        
        return True
    
    def start_qdrant(self) -> Optional[subprocess.Popen]:
        """Запуск Qdrant в Docker"""
        logger.info("🗄️  Запуск Qdrant...")
        
        try:
            # Проверяем, не запущен ли уже
            check = subprocess.run(
                ['docker', 'ps', '--filter', 'name=qdrant', '--format', '{{.Names}}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if 'qdrant' in check.stdout:
                logger.info("✅ Qdrant уже запущен")
                return None
            
            # Запускаем Qdrant
            subprocess.run(
                [
                    'docker', 'run', '-d',
                    '--name', 'qdrant',
                    '-p', '6333:6333',
                    '-p', '6334:6334',
                    '-v', 'qdrant_storage:/qdrant/storage',
                    'qdrant/qdrant'
                ],
                check=True,
                timeout=30
            )
            
            logger.info("✅ Qdrant запущен")
            return None
            
        except subprocess.CalledProcessError:
            logger.warning("⚠️  Не удалось запустить Qdrant (продолжаем без него)")
            return None
        except Exception as e:
            logger.warning(f"⚠️  Ошибка запуска Qdrant: {e}")
            return None
    
    def start_backend(self) -> Optional[subprocess.Popen]:
        """Запуск backend сервера"""
        logger.info("🚀 Запуск backend сервера...")
        
        backend_dir = self.project_root / "web" / "backend"
        main_file = backend_dir / "main.py"
        
        if not main_file.exists():
            logger.error("❌ Backend main.py не найден!")
            return None
        
        try:
            process = subprocess.Popen(
                [self.python_cmd, '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'],
                cwd=str(backend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            logger.info("✅ Backend запущен на http://localhost:8000")
            return process
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска backend: {e}")
            return None
    
    def start_frontend(self) -> Optional[subprocess.Popen]:
        """Запуск frontend сервера"""
        logger.info("🎨 Запуск frontend сервера...")
        
        frontend_dir = self.project_root / "web" / "frontend"
        
        if not frontend_dir.exists():
            logger.error("❌ Frontend директория не найдена!")
            return None
        
        try:
            process = subprocess.Popen(
                ['npm', 'run', 'dev'],
                cwd=str(frontend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            logger.info("✅ Frontend запущен на http://localhost:3000")
            return process
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска frontend: {e}")
            return None
    
    def start_main_system(self) -> Optional[subprocess.Popen]:
        """Запуск основной системы EDIS"""
        logger.info("🧠 Запуск основной системы EDIS...")
        
        run_system = self.project_root / "run_system.py"
        
        if not run_system.exists():
            logger.error("❌ run_system.py не найден!")
            return None
        
        try:
            process = subprocess.Popen(
                [self.python_cmd, str(run_system)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            logger.info("✅ Основная система EDIS запущена")
            return process
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска системы: {e}")
            return None
    
    def run(self):
        """Главный метод запуска"""
        self.print_banner()
        
        # Фаза 1: Проверка системных требований
        logger.info("=" * 60)
        logger.info("ФАЗА 1: Проверка системных требований")
        logger.info("=" * 60)
        
        if not self.check_python_version():
            sys.exit(1)
        
        self.check_git()
        
        if not self.check_node():
            sys.exit(1)
        
        has_docker = self.check_docker()
        
        # Фаза 2: Установка зависимостей
        logger.info("\n" + "=" * 60)
        logger.info("ФАЗА 2: Установка зависимостей")
        logger.info("=" * 60)
        
        if not self.install_python_dependencies():
            logger.error("❌ Не удалось установить Python зависимости")
            sys.exit(1)
        
        if not self.install_frontend_dependencies():
            logger.error("❌ Не удалось установить frontend зависимости")
            sys.exit(1)
        
        # Фаза 3: Настройка компонентов
        logger.info("\n" + "=" * 60)
        logger.info("ФАЗА 3: Настройка компонентов")
        logger.info("=" * 60)
        
        if not self.check_env_file():
            logger.error("❌ Проблема с конфигурацией")
            sys.exit(1)
        
        self.setup_gpt_sovits()
        
        # Фаза 4: Запуск сервисов
        logger.info("\n" + "=" * 60)
        logger.info("ФАЗА 4: Запуск сервисов")
        logger.info("=" * 60)
        
        processes = []
        
        if has_docker:
            self.start_qdrant()
        
        backend_process = self.start_backend()
        if backend_process:
            processes.append(('Backend', backend_process))
        
        frontend_process = self.start_frontend()
        if frontend_process:
            processes.append(('Frontend', frontend_process))
        
        # Опционально: запуск основной системы
        # main_process = self.start_main_system()
        # if main_process:
        #     processes.append(('Main System', main_process))
        
        # Финал
        logger.info("\n" + "=" * 60)
        logger.info("🎉 СИСТЕМА ЗАПУЩЕНА!")
        logger.info("=" * 60)
        logger.info("")
        logger.info("📍 Доступные сервисы:")
        logger.info("   • Backend API:  http://localhost:8000")
        logger.info("   • Frontend UI:  http://localhost:3000")
        logger.info("   • API Docs:     http://localhost:8000/docs")
        if has_docker:
            logger.info("   • Qdrant:       http://localhost:6333")
        logger.info("")
        logger.info("📖 Документация:")
        logger.info("   • MASTER_README.md - Главная инструкция")
        logger.info("   • QUICKSTART.md - Быстрый старт")
        logger.info("   • WEB_QUICKSTART.md - Веб-интерфейс")
        logger.info("")
        logger.info("⚠️  Нажмите Ctrl+C для остановки всех сервисов")
        logger.info("=" * 60)
        
        # Ожидание завершения
        try:
            for name, process in processes:
                process.wait()
        except KeyboardInterrupt:
            logger.info("\n\n🛑 Остановка сервисов...")
            for name, process in processes:
                logger.info(f"   Остановка {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
            logger.info("✅ Все сервисы остановлены")


def main():
    """Точка входа"""
    try:
        starter = EDISStarter()
        starter.run()
    except KeyboardInterrupt:
        logger.info("\n\n👋 До свидания!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
