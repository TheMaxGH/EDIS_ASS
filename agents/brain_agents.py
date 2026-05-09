"""
Агенты: Творец и Логик
"""
import json
from typing import Optional
from loguru import logger

from core.schemas import (
    Message, MessageRole, CreatorOutput, LogicFeedback, ConflictStatus
)
from core.models.qwen_wrapper import CreatorModel, LogicModel


class CreatorAgent:
    """
    Агент-Творец на базе Qwen-72B
    Генерирует креативные идеи и гипотезы
    """
    
    def __init__(self, model: CreatorModel):
        self.model = model
        logger.info("CreatorAgent инициализирован")
    
    async def generate_idea(
        self,
        task: str,
        context: Optional[list[Message]] = None,
        previous_feedback: Optional[str] = None
    ) -> CreatorOutput:
        """
        Генерация креативной идеи на основе задачи
        
        Args:
            task: Задача от пользователя
            context: Контекст предыдущих сообщений
            previous_feedback: Фидбек от Логика (если есть)
        
        Returns:
            Структурированный вывод с идеей
        """
        messages = context or []
        
        # Формируем промпт
        prompt = f"Задача: {task}\n\n"
        
        if previous_feedback:
            prompt += f"Фидбек от Логика: {previous_feedback}\n\n"
            prompt += "Учти замечания и предложи улучшенную версию.\n\n"
        
        prompt += "Сгенерируй креативное решение в формате JSON."
        
        messages.append(Message(
            role=MessageRole.USER,
            content=prompt
        ))
        
        # Генерация
        response = await self.model.generate(
            messages=messages,
            system_prompt=self.model.system_prompt
        )
        
        # Парсинг JSON
        try:
            # Извлекаем JSON из ответа (может быть обернут в markdown)
            json_str = self._extract_json(response)
            data = json.loads(json_str)
            
            output = CreatorOutput(**data)
            logger.info(f"Творец сгенерировал идею с creativity_score={output.creativity_score}")
            
            return output
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Ошибка парсинга ответа Творца: {e}")
            # Fallback: создаем структуру вручную
            return CreatorOutput(
                idea="Ошибка парсинга",
                hypothesis=response[:500],
                reasoning="Не удалось извлечь структурированный ответ",
                creativity_score=0.5
            )
    
    def _extract_json(self, text: str) -> str:
        """Извлечение JSON из текста (может быть в markdown блоке)"""
        # Ищем JSON между ```json и ```
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            return text[start:end].strip()
        
        # Ищем JSON между { и }
        start = text.find("{")
        end = text.rfind("}") + 1
        
        if start != -1 and end > start:
            return text[start:end]
        
        return text


class LogicAgent:
    """
    Агент-Логик на базе Qwen3.5-397B-A17B-FP8
    Верифицирует идеи Творца и создает планы исполнения
    """
    
    def __init__(self, model: LogicModel):
        self.model = model
        logger.info("LogicAgent инициализирован")
    
    async def verify_idea(
        self,
        task: str,
        creator_output: CreatorOutput,
        context: Optional[list[Message]] = None
    ) -> LogicFeedback:
        """
        Верификация идеи от Творца
        
        Args:
            task: Исходная задача
            creator_output: Вывод Творца
            context: Контекст
        
        Returns:
            Структурированный фидбек
        """
        messages = context or []
        
        # Формируем промпт для анализа
        prompt = f"""Исходная задача: {task}

Идея от Творца:
- Идея: {creator_output.idea}
- Гипотеза: {creator_output.hypothesis}
- Рассуждения: {creator_output.reasoning}

Проанализируй эту идею критически:
1. Есть ли логические ошибки?
2. Реализуема ли она на практике?
3. Соответствует ли исходной задаче?

Предоставь структурированный фидбек в формате JSON."""
        
        messages.append(Message(
            role=MessageRole.USER,
            content=prompt
        ))
        
        # Генерация
        response = await self.model.generate(
            messages=messages,
            system_prompt=self.model.system_prompt
        )
        
        # Парсинг JSON
        try:
            json_str = self._extract_json(response)
            data = json.loads(json_str)
            
            feedback = LogicFeedback(**data)
            logger.info(
                f"Логик вынес вердикт: {feedback.status}, "
                f"conflict_score={feedback.conflict_score}"
            )
            
            return feedback
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Ошибка парсинга ответа Логика: {e}")
            # Fallback
            return LogicFeedback(
                status=ConflictStatus.NEEDS_REVISION,
                feedback=response[:500],
                conflict_score=0.5
            )
    
    def _extract_json(self, text: str) -> str:
        """Извлечение JSON из текста"""
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            return text[start:end].strip()
        
        start = text.find("{")
        end = text.rfind("}") + 1
        
        if start != -1 and end > start:
            return text[start:end]
        
        return text
