#!/usr/bin/env python3
"""
🚀 EDIS System Launcher
Запуск всей системы Enhanced Dual Intelligence System

Последовательность:
1. Проверка зависимостей и окружения
2. Запуск Qdrant (векторная БД)
3. Запуск vLLM серверов (Creator + Logic)
4. Запуск GPT-SoVITS TTS сервера
5. Запуск FastAPI backend (опционально)
6. Инициализация главного агента
"""
import asyncio
import subprocess
import sys
import os
import time
from pathlib import Path
from loguru import logger
import yaml
import signal


class EDISLauncher:
    """Лаунчер для всей системы EDIS"""
    
    def __init__(self, config_path: str = "config/vllm_config.yaml", skip_tts: bool = False):
        self.config_path = config_path
        self.skip_tts = skip_tts
        self.processes = []
        self.config = None
        
        # Настройка логирования
        logger.add(
            "logs/system_launch.log",
            rotation="100 MB",
            level="INFO"
        )
        
        logger.info("EDIS Launcher инициализирован")
    
    def load_config(self):
        """Загрузка конфигурации"""
        logger.info(f"Загрузка конфигурации: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        logger.info("Конфигурация загружена")
    
    def check_dependencies(self) -> bool:
        """Проверка зависимостей"""
        logger.info("Проверка зависимостей...")
        
        required = {
            "docker": "Docker для Sandbox",
            "nvidia-smi": "NVIDIA GPU",
            "python": "Python 3.11+",
        }
        
        missing = []
        
        for cmd, desc in required.items():
            try:
                subprocess.run(
                    [cmd, "--version"],
                    capture_output=True,
                    check=True
                )
                logger.info(f"✓ {desc}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.warning(f"✗ {desc} не найден")
                missing.append(desc)
        
        if missing:
            logger.error(f"Отсутствуют зависимости: {', '.join(missing)}")
            return False
        
        # Проверка GPU
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=count", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                check=True
            )
            gpu_count = int(result.stdout.strip())
            logger.info(f"✓ Обнаружено {gpu_count} GPU")
            
            if gpu_count < 8:
                logger.warning(f"Рекомендуется 8 GPU, обнаружено {gpu_count}")
        except Exception as e:
            logger.error(f"Ошибка проверки GPU: {e}")
            return False
        
        return True
    
    def check_gpt_sovits(self) -> bool:
        """Проверка установки GPT-SoVITS"""
        gpt_sovits_path = Path("GPT-SoVITS")
        
        if not gpt_sovits_path.exists():
            logger.warning("GPT-SoVITS не найден")
            return False
        
        # Проверка основных файлов
        required_files = [
            gpt_sovits_path / "api.py",
            gpt_sovits_path / "GPT_SoVITS" / "inference_webui.py",
        ]
        
        for file in required_files:
            if not file.exists():
                logger.warning(f"Отсутствует файл: {file}")
                return False
        
        # Проверка моделей
        models_path = gpt_sovits_path / "GPT_SoVITS" / "pretrained_models"
        if not models_path.exists():
            logger.warning("Отсутствует директория с моделями")
            return False
        
        logger.info("✓ GPT-SoVITS установлен корректно")
        return True
    
    def install_gpt_sovits(self) -> bool:
        """Автоматическая установка GPT-SoVITS через setup_gpt_sovits.py"""
        logger.info("Запуск автоматической установки GPT-SoVITS...")
        
        setup_script = Path("setup_gpt_sovits.py")
        if not setup_script.exists():
            logger.error("setup_gpt_sovits.py не найден!")
            return False
        
        try:
            # Запуск установщика
            result = subprocess.run(
                [sys.executable, str(setup_script), "--auto"],
                capture_output=True,
                text=True,
                timeout=1800  # 30 минут на установку
            )
            
            if result.returncode == 0:
                logger.info("✓ GPT-SoVITS успешно установлен")
                return True
            else:
                logger.error(f"Ошибка установки GPT-SoVITS:\n{result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Превышено время ожидания установки (30 мин)")
            return False
        except Exception as e:
            logger.error(f"Ошибка при запуске установщика: {e}")
            return False
    
    def start_qdrant(self):
        """Запуск Qdrant в Docker"""
        logger.info("Запуск Qdrant...")
        
        try:
            # Проверяем, не запущен ли уже
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=qdrant", "--format", "{{.Names}}"],
                capture_output=True,
                text=True
            )
            
            if "qdrant" in result.stdout:
                logger.info("Qdrant уже запущен")
                return
            
            # Запускаем Qdrant
            cmd = [
                "docker", "run", "-d",
                "--name", "qdrant",
                "-p", "6333:6333",
                "-p", "6334:6334",
                "-v", "qdrant_storage:/qdrant/storage",
                "qdrant/qdrant:latest"
            ]
            
            subprocess.run(cmd, check=True)
            logger.info("✓ Qdrant запущен на порту 6333")
            
            # Ждем готовности
            time.sleep(5)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка запуска Qdrant: {e}")
            raise
    
    def start_vllm_creator(self):
        """Запуск vLLM для Creator (GPU 0-1)"""
        logger.info("Запуск vLLM Creator (Qwen-72B)...")
        
        creator_config = self.config['creator']
        
        cmd = [
            "python", "-m", "vllm.entrypoints.openai.api_server",
            "--model", creator_config['model_name'],
            "--tensor-parallel-size", str(creator_config['tensor_parallel_size']),
            "--gpu-memory-utilization", str(creator_config['gpu_memory_utilization']),
            "--max-model-len", str(creator_config['max_model_len']),
            "--dtype", creator_config['dtype'],
            "--host", creator_config['host'],
            "--port", str(creator_config['port']),
            "--trust-remote-code"
        ]
        
        if creator_config.get('use_flash_attn'):
            cmd.append("--enable-flash-attn")
        
        # Устанавливаем CUDA_VISIBLE_DEVICES для GPU 0-1
        env = os.environ.copy()
        env['CUDA_VISIBLE_DEVICES'] = '0,1'
        
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        self.processes.append(('vllm_creator', process))
        logger.info(f"✓ vLLM Creator запущен на порту {creator_config['port']}")
        
        # Ждем готовности
        time.sleep(30)
    
    def start_vllm_logic(self):
        """Запуск vLLM для Logic (GPU 2-5)"""
        logger.info("Запуск vLLM Logic (Qwen3.5-397B-FP8)...")
        
        logic_config = self.config['logic']
        
        cmd = [
            "python", "-m", "vllm.entrypoints.openai.api_server",
            "--model", logic_config['model_name'],
            "--tensor-parallel-size", str(logic_config['tensor_parallel_size']),
            "--gpu-memory-utilization", str(logic_config['gpu_memory_utilization']),
            "--max-model-len", str(logic_config['max_model_len']),
            "--dtype", logic_config['dtype'],
            "--host", logic_config['host'],
            "--port", str(logic_config['port']),
            "--trust-remote-code"
        ]
        
        if logic_config.get('use_flash_attn'):
            cmd.append("--enable-flash-attn")
        
        # Устанавливаем CUDA_VISIBLE_DEVICES для GPU 2-5
        env = os.environ.copy()
        env['CUDA_VISIBLE_DEVICES'] = '2,3,4,5'
        
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        self.processes.append(('vllm_logic', process))
        logger.info(f"✓ vLLM Logic запущен на порту {logic_config['port']}")
        
        # Ждем готовности
        time.sleep(30)
    
    def start_gpt_sovits(self):
        """Запуск GPT-SoVITS TTS сервера (GPU 6)"""
        if self.skip_tts:
            logger.info("TTS пропущен (флаг --skip-tts)")
            return
        
        logger.info("Запуск GPT-SoVITS TTS...")
        
        # Проверка установки
        if not self.check_gpt_sovits():
            logger.warning("GPT-SoVITS не установлен")
            
            # Предложение автоустановки
            logger.info("Попытка автоматической установки...")
            if self.install_gpt_sovits():
                logger.info("✓ GPT-SoVITS успешно установлен")
            else:
                logger.error("Не удалось установить GPT-SoVITS, пропускаем TTS")
                return
        
        gpt_sovits_path = Path("GPT-SoVITS")
        
        # Устанавливаем CUDA_VISIBLE_DEVICES для GPU 6
        env = os.environ.copy()
        env['CUDA_VISIBLE_DEVICES'] = '6'
        
        cmd = [
            "python",
            str(gpt_sovits_path / "api.py"),
            "--port", "9880"
        ]
        
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(gpt_sovits_path)
        )
        
        self.processes.append(('gpt_sovits', process))
        logger.info("✓ GPT-SoVITS запущен на порту 9880")
        
        time.sleep(10)
    
    async def start_agent(self):
        """Инициализация главного агента"""
        logger.info("Инициализация DualQwenAgent...")
        
        from dual_qwen_brain import DualQwenAgent
        
        agent = DualQwenAgent()
        await agent.initialize()
        
        logger.info("✓ Агент инициализирован и готов к работе")
        
        return agent
    
    def cleanup(self):
        """Остановка всех процессов"""
        logger.info("Остановка системы...")
        
        for name, process in self.processes:
            logger.info(f"Остановка {name}...")
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
        
        # Останавливаем Qdrant
        try:
            subprocess.run(
                ["docker", "stop", "qdrant"],
                capture_output=True,
                timeout=10
            )
            subprocess.run(
                ["docker", "rm", "qdrant"],
                capture_output=True,
                timeout=10
            )
        except Exception as e:
            logger.warning(f"Ошибка остановки Qdrant: {e}")
        
        logger.info("Система остановлена")
    
    async def run(self):
        """Главный метод запуска"""
        try:
            logger.info("="*60)
            logger.info("🚀 ЗАПУСК EDIS (Enhanced Dual Intelligence System)")
            logger.info("="*60)
            
            # 1. Загрузка конфигурации
            self.load_config()
            
            # 2. Проверка зависимостей
            if not self.check_dependencies():
                logger.error("Проверка зависимостей не пройдена")
                return False
            
            # 3. Запуск компонентов
            self.start_qdrant()
            self.start_vllm_creator()
            self.start_vllm_logic()
            self.start_gpt_sovits()
            
            # 4. Инициализация агента
            agent = await self.start_agent()
            
            logger.info("="*60)
            logger.info("✓ СИСТЕМА ПОЛНОСТЬЮ ЗАПУЩЕНА")
            logger.info("="*60)
            logger.info("Creator API: http://localhost:8001")
            logger.info("Logic API: http://localhost:8002")
            logger.info("TTS API: http://localhost:9880")
            logger.info("Qdrant: http://localhost:6333")
            logger.info("="*60)
            
            # Держим систему запущенной
            logger.info("Система работает. Нажмите Ctrl+C для остановки.")
            
            # Простой интерактивный режим
            while True:
                try:
                    task = input("\n💬 Введите задачу (или 'exit' для выхода): ")
                    
                    if task.lower() in ['exit', 'quit', 'q']:
                        break
                    
                    if not task.strip():
                        continue
                    
                    logger.info(f"Обработка задачи: {task}")
                    result = await agent.process(task, use_task_graph=True)
                    
                    print("\n" + "="*60)
                    print("📊 РЕЗУЛЬТАТ:")
                    print("="*60)
                    print(result)
                    print("="*60)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"Ошибка обработки задачи: {e}")
            
            return True
            
        except KeyboardInterrupt:
            logger.info("Получен сигнал прерывания")
            return True
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            return False
        finally:
            self.cleanup()


def main():
    """Точка входа"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Запуск EDIS (Enhanced Dual Intelligence System)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/vllm_config.yaml",
        help="Путь к конфигурации vLLM"
    )
    parser.add_argument(
        "--skip-vllm",
        action="store_true",
        help="Пропустить запуск vLLM (если уже запущен)"
    )
    parser.add_argument(
        "--skip-tts",
        action="store_true",
        help="Пропустить запуск GPT-SoVITS TTS"
    )
    
    args = parser.parse_args()
    
    launcher = EDISLauncher(config_path=args.config, skip_tts=args.skip_tts)
    
    # Обработка сигналов
    def signal_handler(sig, frame):
        logger.info("Получен сигнал остановки")
        launcher.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Запуск
    success = asyncio.run(launcher.run())
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
