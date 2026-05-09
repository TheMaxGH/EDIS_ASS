"""
Скрипт для DoRA (Weight-Decomposed Low-Rank Adaptation) fine-tuning
Дообучение моделей Qwen перед запуском основной системы
Оптимизировано для 8xH200 с DeepSpeed ZeRO-3 и Flash Attention 2
"""
import os
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer
)
from peft import (
    LoraConfig,
    get_peft_model,
    TaskType,
    prepare_model_for_kbit_training
)
from datasets import load_dataset, Dataset
from loguru import logger
import yaml
import deepspeed


class DoRATrainer:
    """
    Тренер для DoRA fine-tuning моделей Qwen
    """
    
    def __init__(self, config_path: str = "config/training_config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        logger.info("DoRATrainer инициализирован")
    
    def prepare_creator_dataset(self) -> Dataset:
        """
        Подготовка датасета для Творца (72B) из папки data/
        Загружает все JSONL файлы с префиксом 'left_' или 'creator_'
        """
        logger.info("Подготовка датасета для Творца из data/...")
        
        import glob
        import json
        
        combined_data = []
        data_dir = "data"
        
        # Ищем файлы для левого полушария (Творец)
        pattern_files = glob.glob(os.path.join(data_dir, "left_*.jsonl")) + \
                       glob.glob(os.path.join(data_dir, "creator_*.jsonl"))
        
        if not pattern_files:
            logger.warning(f"Не найдено файлов датасетов в {data_dir}/ с префиксом 'left_' или 'creator_'")
            logger.info("Создайте файлы датасетов в формате JSONL в папке data/")
            return Dataset.from_list([])
        
        for filepath in pattern_files:
            logger.info(f"Загрузка {filepath}...")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            combined_data.append(data)
            except Exception as e:
                logger.error(f"Ошибка загрузки {filepath}: {e}")
        
        logger.info(f"Подготовлено {len(combined_data)} примеров для Творца из {len(pattern_files)} файлов")
        return Dataset.from_list(combined_data)
    
    def prepare_logic_dataset(self) -> Dataset:
        """
        Подготовка датасета для Логика (Qwen3.5-397B-FP8) из папки data/
        Загружает все JSONL файлы с префиксом 'right_' или 'logic_'
        """
        logger.info("Подготовка датасета для Логика из data/...")
        
        import glob
        import json
        
        combined_data = []
        data_dir = "data"
        
        # Ищем файлы для правого полушария (Логик)
        pattern_files = glob.glob(os.path.join(data_dir, "right_*.jsonl")) + \
                       glob.glob(os.path.join(data_dir, "logic_*.jsonl"))
        
        if not pattern_files:
            logger.warning(f"Не найдено файлов датасетов в {data_dir}/ с префиксом 'right_' или 'logic_'")
            logger.info("Создайте файлы датасетов в формате JSONL в папке data/")
            return Dataset.from_list([])
        
        for filepath in pattern_files:
            logger.info(f"Загрузка {filepath}...")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            combined_data.append(data)
            except Exception as e:
                logger.error(f"Ошибка загрузки {filepath}: {e}")
        
        logger.info(f"Подготовлено {len(combined_data)} примеров для Логика из {len(pattern_files)} файлов")
        return Dataset.from_list(combined_data)
    
    def _extract_text(self, item: dict) -> str:
        """Извлечение текста из элемента датасета"""
        # Пробуем различные ключи
        for key in ["text", "content", "code", "question", "answer"]:
            if key in item and item[key]:
                return str(item[key])
        return ""
    
    def train_model(
        self,
        model_name: str,
        dataset: Dataset,
        output_dir: str,
        is_creator: bool = False
    ):
        """
        Обучение модели с DoRA
        
        Args:
            model_name: Имя базовой модели
            dataset: Датасет для обучения
            output_dir: Директория для сохранения
            is_creator: True для Творца, False для Логика
        """
        logger.info(f"Начало обучения модели {model_name}")
        
        # Загрузка модели и токенизатора
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True,
            load_in_8bit=True  # Квантование для экономии памяти
        )
        
        # Подготовка модели для обучения
        model = prepare_model_for_kbit_training(model)
        
        # Конфигурация DoRA
        lora_config = LoraConfig(
            r=self.config.get("lora_r", 16),
            lora_alpha=self.config.get("lora_alpha", 32),
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
            lora_dropout=0.05,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
            use_dora=True  # Активация DoRA!
        )
        
        # Применяем PEFT
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()
        
        # Токенизация датасета
        def tokenize_function(examples):
            return tokenizer(
                examples["text"],
                truncation=True,
                max_length=2048,
                padding="max_length"
            )
        
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names
        )
        
        # Параметры обучения с DeepSpeed ZeRO-3 для 8xH200
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=self.config.get("num_epochs", 3),
            per_device_train_batch_size=self.config.get("batch_size", 4),
            gradient_accumulation_steps=self.config.get("gradient_accumulation", 4),
            learning_rate=self.config.get("learning_rate", 2e-4),
            fp16=False,
            bf16=True,  # BF16 для H200
            logging_steps=10,
            save_steps=500,
            save_total_limit=3,
            warmup_steps=100,
            optim="adamw_torch",
            report_to="tensorboard",
            logging_dir="./logs/tensorboard",
            # DeepSpeed ZeRO-3 конфигурация
            deepspeed="config/deepspeed_config.json",
            # Оптимизации для H200
            dataloader_num_workers=4,
            dataloader_pin_memory=True,
            gradient_checkpointing=True,  # Экономия памяти
            # Distributed training на 8 GPU
            local_rank=-1,
            ddp_backend="nccl",  # NCCL оптимизирован для NVLink
            ddp_find_unused_parameters=False
        )
        
        # Тренер
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_dataset,
            tokenizer=tokenizer
        )
        
        # Обучение
        logger.info("Запуск обучения...")
        trainer.train()
        
        # Сохранение
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        
        logger.info(f"Модель сохранена в {output_dir}")
    
    def run_full_training(self):
        """
        Полный цикл обучения обеих моделей
        """
        logger.info("=" * 50)
        logger.info("НАЧАЛО ПОЛНОГО ЦИКЛА DORA FINE-TUNING")
        logger.info("=" * 50)
        
        # 1. Обучение Творца (72B)
        logger.info("\n[1/2] Обучение Творца (Qwen-72B)...")
        creator_dataset = self.prepare_creator_dataset()
        
        self.train_model(
            model_name=self.config["creator_model"],
            dataset=creator_dataset,
            output_dir="models/creator_finetuned",
            is_creator=True
        )
        
        # 2. Обучение Логика (Qwen3.5-397B-FP8)
        logger.info("\n[2/2] Обучение Логика (Qwen3.5-397B-FP8)...")
        logic_dataset = self.prepare_logic_dataset()
        
        self.train_model(
            model_name=self.config["logic_model"],
            dataset=logic_dataset,
            output_dir="models/logic_finetuned",
            is_creator=False
        )
        
        logger.info("\n" + "=" * 50)
        logger.info("ОБУЧЕНИЕ ЗАВЕРШЕНО!")
        logger.info("=" * 50)


def main():
    """Точка входа для скрипта обучения"""
    import argparse
    
    parser = argparse.ArgumentParser(description="DoRA Fine-tuning для Dual Qwen Brain")
    parser.add_argument(
        "--config",
        type=str,
        default="config/training_config.yaml",
        help="Путь к конфигурационному файлу"
    )
    parser.add_argument(
        "--model",
        type=str,
        choices=["creator", "logic", "both"],
        default="both",
        help="Какую модель обучать"
    )
    
    args = parser.parse_args()
    
    trainer = DoRATrainer(config_path=args.config)
    
    if args.model == "both":
        trainer.run_full_training()
    elif args.model == "creator":
        dataset = trainer.prepare_creator_dataset()
        trainer.train_model(
            model_name=trainer.config["creator_model"],
            dataset=dataset,
            output_dir="models/creator_finetuned",
            is_creator=True
        )
    else:  # logic
        dataset = trainer.prepare_logic_dataset()
        trainer.train_model(
            model_name=trainer.config["logic_model"],
            dataset=dataset,
            output_dir="models/logic_finetuned",
            is_creator=False
        )


if __name__ == "__main__":
    main()
