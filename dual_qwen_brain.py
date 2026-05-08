"""
Главный класс агента Dual Qwen Brain
Объединяет все компоненты системы
"""
import asyncio
import yaml
from typing import Optional
from loguru import logger

from core.models.qwen_wrapper import CreatorModel, LogicModel
from agents.brain_agents import CreatorAgent, LogicAgent
from core.workflow.synergy_flow import SynergyWorkflow
from core.memory.vector_store import VectorMemory
from autonomy.monitor import AutonomyMonitor
from core.schemas import AgentState


class DualQwenAgent:
    """
    Главный класс мультимодального агента
    Координирует работу Творца, Логика и автономного режима
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        # Загрузка конфигурации
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        logger.info("Инициализация Dual Qwen Brain...")
        
        # Инициализация компонентов (ленивая загрузка)
        self.creator_model: Optional[CreatorModel] = None
        self.logic_model: Optional[LogicModel] = None
        self.creator_agent: Optional[CreatorAgent] = None
        self.logic_agent: Optional[LogicAgent] = None
        self.workflow: Optional[SynergyWorkflow] = None
        self.memory: Optional[VectorMemory] = None
        self.autonomy_monitor: Optional[AutonomyMonitor] = None
        
        self._initialized = False
        
        logger.info("DualQwenAgent создан (компоненты будут загружены при первом использовании)")
    
    async def initialize(self):
        """Асинхронная инициализация всех компонентов"""
        if self._initialized:
            logger.info("Агент уже инициализирован")
            return
        
        logger.info("Загрузка компонентов...")
        
        # 1. Векторная память
        logger.info("Инициализация векторной памяти...")
        self.memory = VectorMemory(
            host=self.config["QDRANT_HOST"],
            port=self.config["QDRANT_PORT"],
            collection_name=self.config["QDRANT_COLLECTION"],
            vector_size=self.config["QDRANT_VECTOR_SIZE"]
        )
        
        # 2. Модели
        logger.info("Загрузка моделей Qwen (это может занять время)...")
        self.creator_model = CreatorModel(self.config)
        self.logic_model = LogicModel(self.config)
        
        await self.creator_model.initialize()
        await self.logic_model.initialize()
        
        # 3. Агенты
        logger.info("Инициализация агентов...")
        self.creator_agent = CreatorAgent(self.creator_model)
        self.logic_agent = LogicAgent(self.logic_model)
        
        # 4. Workflow
        logger.info("Создание Synergy Flow...")
        self.workflow = SynergyWorkflow(
            creator_agent=self.creator_agent,
            logic_agent=self.logic_agent,
            max_iterations=self.config["MAX_CONFLICT_RETRIES"],
            conflict_threshold=self.config["CONFLICT_THRESHOLD"]
        )
        
        # 5. Автономный монитор (опционально)
        if self.config.get("AUTONOMY_ENABLED", False):
            logger.info("Инициализация автономного режима...")
            self.autonomy_monitor = AutonomyMonitor(
                vector_memory=self.memory,
                tavily_api_key=self.config["TAVILY_API_KEY"],
                github_token=self.config["GITHUB_TOKEN"],
                check_interval=self.config["AUTONOMY_CHECK_INTERVAL"],
                max_articles=self.config["AUTONOMY_MAX_ARTICLES"]
            )
        
        self._initialized = True
        logger.info("✓ Dual Qwen Brain полностью инициализирован!")
    
    async def process(self, task: str) -> str:
        """
        Обработка задачи через Synergy Flow
        
        Args:
            task: Задача от пользователя
        
        Returns:
            Финальный результат
        """
        if not self._initialized:
            await self.initialize()
        
        logger.info(f"Обработка задачи: {task[:100]}...")
        
        # Поиск релевантного контекста в памяти
        context_results = await self.memory.search(task, limit=3)
        
        if context_results:
            logger.info(f"Найдено {len(context_results)} релевантных записей в памяти")
            # Можно добавить контекст в задачу
            context_str = "\n\n".join([r["content"][:200] for r in context_results])
            task_with_context = f"{task}\n\nКонтекст из памяти:\n{context_str}"
        else:
            task_with_context = task
        
        # Запуск workflow
        final_state: AgentState = await self.workflow.run(task_with_context)
        
        # Возврат результата (TypedDict доступ)
        result = final_state.get('final_result') or "Не удалось получить результат"
        
        logger.info(f"Задача обработана за {final_state['iteration_count']} итераций")
        return result
    
    async def start_autonomy(self):
        """Запуск автономного режима (фоновый мониторинг)"""
        if not self._initialized:
            await self.initialize()
        
        if not self.autonomy_monitor:
            logger.warning("Автономный режим отключен в конфигурации")
            return
        
        logger.info("Запуск автономного режима...")
        # Запускаем в фоновой задаче
        asyncio.create_task(self.autonomy_monitor.start())
    
    def stop_autonomy(self):
        """Остановка автономного режима"""
        if self.autonomy_monitor:
            self.autonomy_monitor.stop()
            logger.info("Автономный режим остановлен")
    
    async def shutdown(self):
        """Корректное завершение работы агента"""
        logger.info("Завершение работы Dual Qwen Brain...")
        
        # Останавливаем автономный режим
        self.stop_autonomy()
        
        # Останавливаем модели
        if self.creator_model:
            await self.creator_model.shutdown()
        if self.logic_model:
            await self.logic_model.shutdown()
        
        logger.info("Dual Qwen Brain остановлен")


async def main():
    """Пример использования агента"""
    # Настройка логирования
    logger.add(
        "logs/dual_qwen.log",
        rotation="100 MB",
        retention="7 days",
        level="INFO"
    )
    
    # Создание агента
    agent = DualQwenAgent()
    
    try:
        # Инициализация
        await agent.initialize()
        
        # Запуск автономного режима (опционально)
        # await agent.start_autonomy()
        
        # Обработка задачи
        task = """
        Спроектируй архитектуру распределенной системы для обработки 
        миллионов запросов в секунду с гарантией консистентности данных.
        """
        
        result = await agent.process(task)
        
        print("\n" + "=" * 50)
        print("РЕЗУЛЬТАТ:")
        print("=" * 50)
        print(result)
        print("=" * 50)
        
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания")
    finally:
        await agent.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
