#!/usr/bin/env python3
"""
GPT-SoVITS Setup Script
Автоматическая установка и настройка GPT-SoVITS для EDIS

Usage:
    python setup_gpt_sovits.py --install        # Установка GPT-SoVITS
    python setup_gpt_sovits.py --test           # Тестирование установки
    python setup_gpt_sovits.py --download-models # Загрузка моделей
    python setup_gpt_sovits.py --all            # Всё вместе
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
import shutil
import platform
from loguru import logger

# Настройка логирования
logger.add(
    "logs/gpt_sovits_setup.log",
    rotation="10 MB",
    level="INFO"
)


class GPTSoVITSSetup:
    """Установщик GPT-SoVITS"""
    
    def __init__(self):
        self.root_dir = Path.cwd()
        self.gpt_sovits_dir = self.root_dir / "GPT-SoVITS"
        self.models_dir = self.gpt_sovits_dir / "pretrained_models"
        self.is_windows = platform.system() == "Windows"
        
        logger.info("GPT-SoVITS Setup инициализирован")
    
    def check_system_requirements(self) -> bool:
        """Проверка системных требований"""
        logger.info("Проверка системных требований...")
        
        requirements = {
            "Python": self._check_python(),
            "Git": self._check_git(),
            "FFmpeg": self._check_ffmpeg(),
            "CUDA": self._check_cuda(),
            "Disk Space": self._check_disk_space()
        }
        
        all_ok = True
        for name, status in requirements.items():
            if status:
                logger.info(f"✓ {name}: OK")
            else:
                logger.error(f"✗ {name}: FAILED")
                all_ok = False
        
        return all_ok
    
    def _check_python(self) -> bool:
        """Проверка Python версии"""
        try:
            version = sys.version_info
            if version.major == 3 and version.minor >= 10:
                logger.info(f"Python {version.major}.{version.minor}.{version.micro}")
                return True
            else:
                logger.error(f"Python {version.major}.{version.minor} < 3.10")
                return False
        except Exception as e:
            logger.error(f"Ошибка проверки Python: {e}")
            return False
    
    def _check_git(self) -> bool:
        """Проверка Git"""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(result.stdout.strip())
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Git не установлен")
            return False
    
    def _check_ffmpeg(self) -> bool:
        """Проверка FFmpeg"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                check=True
            )
            version_line = result.stdout.split('\n')[0]
            logger.info(version_line)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("FFmpeg не установлен (рекомендуется)")
            return False
    
    def _check_cuda(self) -> bool:
        """Проверка CUDA"""
        try:
            import torch
            if torch.cuda.is_available():
                logger.info(f"CUDA {torch.version.cuda}, GPU count: {torch.cuda.device_count()}")
                if torch.cuda.device_count() > 6:
                    gpu_name = torch.cuda.get_device_name(6)
                    logger.info(f"GPU 6: {gpu_name}")
                return True
            else:
                logger.warning("CUDA недоступна (TTS будет работать на CPU)")
                return False
        except ImportError:
            logger.warning("PyTorch не установлен")
            return False
    
    def _check_disk_space(self) -> bool:
        """Проверка свободного места на диске"""
        try:
            stat = shutil.disk_usage(self.root_dir)
            free_gb = stat.free / (1024**3)
            logger.info(f"Свободно: {free_gb:.1f} GB")
            
            if free_gb < 15:
                logger.error("Недостаточно места (требуется минимум 15 GB)")
                return False
            return True
        except Exception as e:
            logger.error(f"Ошибка проверки диска: {e}")
            return False
    
    def install_gpt_sovits(self) -> bool:
        """Установка GPT-SoVITS"""
        logger.info("Начало установки GPT-SoVITS...")
        
        # Проверка существующей установки
        if self.gpt_sovits_dir.exists():
            logger.warning("GPT-SoVITS уже установлен")
            response = input("Переустановить? (y/N): ")
            if response.lower() != 'y':
                logger.info("Установка отменена")
                return True
            
            logger.info("Удаление старой установки...")
            shutil.rmtree(self.gpt_sovits_dir)
        
        # Клонирование репозитория
        logger.info("Клонирование репозитория...")
        try:
            subprocess.run(
                ["git", "clone", "https://github.com/RVC-Boss/GPT-SoVITS.git"],
                cwd=self.root_dir,
                check=True
            )
            logger.info("✓ Репозиторий склонирован")
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка клонирования: {e}")
            return False
        
        # Установка зависимостей
        logger.info("Установка зависимостей...")
        requirements_file = self.gpt_sovits_dir / "requirements.txt"
        
        if not requirements_file.exists():
            logger.error("requirements.txt не найден")
            return False
        
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                check=True
            )
            logger.info("✓ Зависимости установлены")
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка установки зависимостей: {e}")
            return False
        
        # Создание директорий
        logger.info("Создание директорий...")
        (self.root_dir / "audio_cache" / "references").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "models" / "voice").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "logs").mkdir(parents=True, exist_ok=True)
        logger.info("✓ Директории созданы")
        
        logger.info("✓ Установка GPT-SoVITS завершена")
        return True
    
    def download_models(self) -> bool:
        """Загрузка предобученных моделей"""
        logger.info("Загрузка предобученных моделей...")
        
        if not self.gpt_sovits_dir.exists():
            logger.error("GPT-SoVITS не установлен. Запустите --install сначала")
            return False
        
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        models = {
            "GPT Model": {
                "url": "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/s1bert25hz-2kh-longer-epoch%3D68e-step%3D50232.ckpt",
                "path": self.models_dir / "s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt"
            },
            "SoVITS Model": {
                "url": "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/s2G488k.pth",
                "path": self.models_dir / "s2G488k.pth"
            }
        }
        
        for name, info in models.items():
            if info["path"].exists():
                logger.info(f"✓ {name} уже загружен")
                continue
            
            logger.info(f"Загрузка {name}...")
            try:
                # Используем wget или curl в зависимости от системы
                if self.is_windows:
                    # Windows: используем Python requests
                    import requests
                    response = requests.get(info["url"], stream=True)
                    response.raise_for_status()
                    
                    with open(info["path"], 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                else:
                    # Linux/Mac: используем wget
                    subprocess.run(
                        ["wget", "-O", str(info["path"]), info["url"]],
                        check=True
                    )
                
                logger.info(f"✓ {name} загружен")
            except Exception as e:
                logger.error(f"Ошибка загрузки {name}: {e}")
                return False
        
        logger.info("✓ Все модели загружены")
        return True
    
    def test_installation(self) -> bool:
        """Тестирование установки"""
        logger.info("Тестирование установки...")
        
        if not self.gpt_sovits_dir.exists():
            logger.error("GPT-SoVITS не установлен")
            return False
        
        # Проверка Python модулей
        logger.info("Проверка Python модулей...")
        required_modules = [
            "torch",
            "transformers",
            "librosa",
            "soundfile"
        ]
        
        all_ok = True
        for module in required_modules:
            try:
                __import__(module)
                logger.info(f"✓ {module}")
            except ImportError:
                logger.error(f"✗ {module} не установлен")
                all_ok = False
        
        if not all_ok:
            return False
        
        # Проверка моделей
        logger.info("Проверка моделей...")
        required_models = [
            self.models_dir / "s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt",
            self.models_dir / "s2G488k.pth"
        ]
        
        for model_path in required_models:
            if model_path.exists():
                size_mb = model_path.stat().st_size / (1024**2)
                logger.info(f"✓ {model_path.name} ({size_mb:.1f} MB)")
            else:
                logger.error(f"✗ {model_path.name} не найден")
                all_ok = False
        
        if all_ok:
            logger.info("✓ Все тесты пройдены")
        else:
            logger.error("✗ Некоторые тесты не пройдены")
        
        return all_ok
    
    def create_startup_script(self):
        """Создание скрипта запуска"""
        logger.info("Создание скрипта запуска...")
        
        if self.is_windows:
            script_path = self.root_dir / "start_gpt_sovits.bat"
            content = """@echo off
REM Start GPT-SoVITS TTS Server

set CUDA_VISIBLE_DEVICES=6

cd GPT-SoVITS
python api.py --port 9880
"""
        else:
            script_path = self.root_dir / "start_gpt_sovits.sh"
            content = """#!/bin/bash
# Start GPT-SoVITS TTS Server

export CUDA_VISIBLE_DEVICES=6

cd GPT-SoVITS
python api.py --port 9880
"""
        
        with open(script_path, 'w') as f:
            f.write(content)
        
        if not self.is_windows:
            os.chmod(script_path, 0o755)
        
        logger.info(f"✓ Скрипт создан: {script_path}")


def main():
    """Точка входа"""
    parser = argparse.ArgumentParser(
        description="GPT-SoVITS Setup для EDIS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python setup_gpt_sovits.py --all              # Полная установка
  python setup_gpt_sovits.py --install          # Только установка
  python setup_gpt_sovits.py --download-models  # Только загрузка моделей
  python setup_gpt_sovits.py --test             # Тестирование
        """
    )
    
    parser.add_argument(
        "--install",
        action="store_true",
        help="Установить GPT-SoVITS"
    )
    parser.add_argument(
        "--download-models",
        action="store_true",
        help="Загрузить предобученные модели"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Протестировать установку"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Выполнить все шаги (установка + модели + тест)"
    )
    parser.add_argument(
        "--skip-requirements-check",
        action="store_true",
        help="Пропустить проверку системных требований"
    )
    
    args = parser.parse_args()
    
    # Если не указаны флаги, показываем help
    if not any([args.install, args.download_models, args.test, args.all]):
        parser.print_help()
        return 0
    
    setup = GPTSoVITSSetup()
    
    print("="*60)
    print("GPT-SoVITS Setup для EDIS")
    print("="*60)
    print()
    
    # Проверка системных требований
    if not args.skip_requirements_check:
        if not setup.check_system_requirements():
            logger.error("Системные требования не выполнены")
            response = input("\nПродолжить установку? (y/N): ")
            if response.lower() != 'y':
                return 1
    
    success = True
    
    # Установка
    if args.all or args.install:
        if not setup.install_gpt_sovits():
            logger.error("Ошибка установки")
            success = False
    
    # Загрузка моделей
    if success and (args.all or args.download_models):
        if not setup.download_models():
            logger.error("Ошибка загрузки моделей")
            success = False
    
    # Тестирование
    if success and (args.all or args.test):
        if not setup.test_installation():
            logger.error("Тестирование не пройдено")
            success = False
    
    # Создание скрипта запуска
    if success and (args.all or args.install):
        setup.create_startup_script()
    
    print()
    print("="*60)
    if success:
        logger.info("✓ Установка завершена успешно!")
        print()
        print("Для запуска TTS сервера:")
        if setup.is_windows:
            print("  start_gpt_sovits.bat")
        else:
            print("  ./start_gpt_sovits.sh")
        print()
        print("Или используйте полный системный лаунчер:")
        print("  python run_system.py")
        print()
        print("API будет доступен по адресу: http://localhost:9880")
    else:
        logger.error("✗ Установка завершена с ошибками")
        return 1
    print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
