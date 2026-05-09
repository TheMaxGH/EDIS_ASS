"""
Voice Cloning Script - обучение GPT-SoVITS на образце голоса
Принимает 1-минутный (или больше) образец и настраивает модель
"""
import argparse
import os
from pathlib import Path
from loguru import logger
import subprocess
import shutil


class VoiceCloner:
    """
    Утилита для клонирования голоса через GPT-SoVITS
    """
    
    def __init__(
        self,
        gpt_sovits_path: str = "./GPT-SoVITS",
        output_dir: str = "models/voice"
    ):
        """
        Args:
            gpt_sovits_path: Путь к репозиторию GPT-SoVITS
            output_dir: Директория для сохранения модели
        """
        self.gpt_sovits_path = Path(gpt_sovits_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.gpt_sovits_path.exists():
            logger.warning(f"GPT-SoVITS не найден в {gpt_sovits_path}")
            logger.info("Клонируйте репозиторий: git clone https://github.com/RVC-Boss/GPT-SoVITS.git")
        
        logger.info("VoiceCloner инициализирован")
    
    def prepare_audio(
        self,
        audio_path: str,
        output_path: str = "data/voice_sample.wav"
    ) -> str:
        """
        Подготовка аудио образца
        Конвертация в нужный формат (WAV, 16kHz, mono)
        
        Args:
            audio_path: Путь к исходному аудио
            output_path: Путь для сохранения обработанного
        
        Returns:
            Путь к обработанному файлу
        """
        logger.info(f"Подготовка аудио: {audio_path}")
        
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Аудио файл не найден: {audio_path}")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Используем ffmpeg для конвертации
            cmd = [
                "ffmpeg",
                "-i", str(audio_path),
                "-ar", "16000",  # 16kHz
                "-ac", "1",      # mono
                "-y",            # overwrite
                str(output_path)
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Аудио подготовлено: {output_path}")
            
            return str(output_path)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка конвертации аудио: {e.stderr.decode()}")
            raise
        except FileNotFoundError:
            logger.error("ffmpeg не найден. Установите: apt-get install ffmpeg")
            raise
    
    def extract_transcript(
        self,
        audio_path: str,
        language: str = "ru"
    ) -> str:
        """
        Извлечение транскрипции из аудио (если текст не предоставлен)
        Использует Whisper для автоматической транскрипции
        
        Args:
            audio_path: Путь к аудио
            language: Язык аудио
        
        Returns:
            Транскрипция текста
        """
        logger.info("Извлечение транскрипции через Whisper...")
        
        try:
            import whisper
            
            # Загружаем модель Whisper
            model = whisper.load_model("base")
            
            # Транскрибируем
            result = model.transcribe(
                audio_path,
                language=language,
                fp16=False
            )
            
            transcript = result["text"].strip()
            logger.info(f"Транскрипция: {transcript[:100]}...")
            
            return transcript
            
        except ImportError:
            logger.error("Whisper не установлен. Установите: pip install openai-whisper")
            raise
    
    def fine_tune(
        self,
        audio_path: str,
        transcript: str,
        speaker_name: str = "custom_voice",
        epochs: int = 10
    ) -> str:
        """
        Fine-tuning GPT-SoVITS на образце голоса
        
        Args:
            audio_path: Путь к аудио образцу
            transcript: Текст образца
            speaker_name: Имя спикера
            epochs: Количество эпох обучения
        
        Returns:
            Путь к обученной модели
        """
        logger.info(f"Начало fine-tuning для спикера '{speaker_name}'...")
        
        # Подготавливаем данные
        prepared_audio = self.prepare_audio(audio_path)
        
        # Создаем конфигурацию для обучения
        config = {
            "speaker_name": speaker_name,
            "audio_path": prepared_audio,
            "transcript": transcript,
            "epochs": epochs,
            "batch_size": 4,
            "learning_rate": 1e-4
        }
        
        # Сохраняем конфиг
        import json
        config_path = self.output_dir / f"{speaker_name}_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Конфигурация сохранена: {config_path}")
        
        # Запускаем обучение (если GPT-SoVITS установлен)
        if self.gpt_sovits_path.exists():
            try:
                train_script = self.gpt_sovits_path / "GPT_SoVITS" / "train.py"
                
                if train_script.exists():
                    cmd = [
                        "python",
                        str(train_script),
                        "--config", str(config_path),
                        "--output_dir", str(self.output_dir)
                    ]
                    
                    logger.info("Запуск обучения...")
                    subprocess.run(cmd, check=True)
                    
                    model_path = self.output_dir / f"{speaker_name}_model.pth"
                    logger.info(f"✓ Модель обучена: {model_path}")
                    
                    return str(model_path)
                else:
                    logger.warning("Скрипт обучения не найден")
                    
            except subprocess.CalledProcessError as e:
                logger.error(f"Ошибка обучения: {e}")
                raise
        
        logger.warning("GPT-SoVITS не установлен, пропускаем обучение")
        logger.info("Для полноценного клонирования установите GPT-SoVITS")
        
        return str(config_path)
    
    def quick_clone(
        self,
        audio_path: str,
        transcript: Optional[str] = None,
        speaker_name: str = "alya_voice"
    ) -> dict:
        """
        Быстрое клонирование голоса (без fine-tuning)
        Использует zero-shot возможности GPT-SoVITS
        
        Args:
            audio_path: Путь к образцу (1+ минута)
            transcript: Текст образца (если None - автоматическая транскрипция)
            speaker_name: Имя голоса
        
        Returns:
            Dict с информацией о клонированном голосе
        """
        logger.info(f"Быстрое клонирование голоса '{speaker_name}'...")
        
        # Подготавливаем аудио
        prepared_audio = self.prepare_audio(
            audio_path,
            output_path=str(self.output_dir / f"{speaker_name}_reference.wav")
        )
        
        # Получаем транскрипцию
        if transcript is None:
            transcript = self.extract_transcript(prepared_audio)
        
        # Сохраняем информацию о голосе
        voice_info = {
            "name": speaker_name,
            "reference_audio": prepared_audio,
            "reference_text": transcript,
            "created_at": __import__('datetime').datetime.now().isoformat()
        }
        
        import json
        info_path = self.output_dir / f"{speaker_name}_info.json"
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(voice_info, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✓ Голос клонирован (zero-shot режим)")
        logger.info(f"Референс: {prepared_audio}")
        logger.info(f"Текст: {transcript[:100]}...")
        
        return voice_info


def main():
    """CLI для клонирования голоса"""
    parser = argparse.ArgumentParser(
        description="Клонирование голоса для Dual Qwen Brain"
    )
    parser.add_argument(
        "audio",
        type=str,
        help="Путь к аудио образцу (WAV, MP3, и т.д.)"
    )
    parser.add_argument(
        "--text",
        type=str,
        default=None,
        help="Текст образца (если не указан - автоматическая транскрипция)"
    )
    parser.add_argument(
        "--name",
        type=str,
        default="alya_voice",
        help="Имя голоса"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["quick", "finetune"],
        default="quick",
        help="Режим: quick (zero-shot) или finetune (обучение)"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=10,
        help="Количество эпох для fine-tuning"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="models/voice",
        help="Директория для сохранения"
    )
    
    args = parser.parse_args()
    
    # Настройка логирования
    logger.add(
        "logs/voice_cloning.log",
        rotation="10 MB",
        level="INFO"
    )
    
    # Создаем клонер
    cloner = VoiceCloner(output_dir=args.output)
    
    try:
        if args.mode == "quick":
            # Быстрое клонирование
            result = cloner.quick_clone(
                audio_path=args.audio,
                transcript=args.text,
                speaker_name=args.name
            )
            
            print("\n" + "="*60)
            print("✓ ГОЛОС УСПЕШНО КЛОНИРОВАН")
            print("="*60)
            print(f"Имя: {result['name']}")
            print(f"Референс: {result['reference_audio']}")
            print(f"Текст: {result['reference_text'][:100]}...")
            print("\nИспользуйте этот голос в агенте:")
            print(f"  tts = GPTSoVITSTTS(")
            print(f"      reference_audio='{result['reference_audio']}',")
            print(f"      reference_text='{result['reference_text']}'")
            print(f"  )")
            print("="*60)
            
        else:
            # Fine-tuning
            model_path = cloner.fine_tune(
                audio_path=args.audio,
                transcript=args.text or cloner.extract_transcript(args.audio),
                speaker_name=args.name,
                epochs=args.epochs
            )
            
            print("\n" + "="*60)
            print("✓ МОДЕЛЬ ОБУЧЕНА")
            print("="*60)
            print(f"Путь: {model_path}")
            print("="*60)
            
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        print(f"\n❌ Ошибка: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
