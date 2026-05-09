"""
Главный класс агента Dual Qwen Brain
Объединяет все компоненты системы
Расширенная версия с Task Graph, Tools и системой приоритетов
"""
import asyncio
import yaml
import os
from typing import Optional, Dict, Any
from loguru import logger

from core.models.qwen_wrapper import CreatorModel, LogicModel
from agents.brain_agents import CreatorAgent, LogicAgent
from core.workflow.synergy_flow import SynergyWorkflow
from core.workflow.enhanced_synergy_flow import EnhancedSynergyWorkflow
from core.workflow.task_architect import TaskPriority
from core.memory.vector_store import VectorMemory
from autonomy.monitor import AutonomyMonitor
from core.schemas import AgentState
from core.tools import CodeSandbox, OmniBrowser, DocumentEngine


class DualQwenAgent:
    """
    Главный класс мультимодального агента
    Координирует работу Творца, Логика, автономного режима и исполнительных инструментов
    """
    
    def __init__(self, config_path: str = "config/config.yaml", use_db_settings: bool = True):
        """
        Инициализация агента
        
        Args:
            config_path: Путь к YAML конфигу (для обратной совместимости)
            use_db_settings: Использовать настройки из базы данных (приоритет над YAML)
        """
        self.config_path = config_path
        self.use_db_settings = use_db_settings
        
        # Загрузка конфигурации
        if use_db_settings and os.path.exists("web/backend/database/settings.db"):
            logger.info("Загрузка настроек из базы данных...")
            self.config = self._load_settings_from_db()
        else:
            logger.info(f"Загрузка настроек из {config_path}...")
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        
        logger.info("Инициализация Dual Qwen Brain...")
        
        # Инициализация компонентов (ленивая загрузка)
        self.creator_model: Optional[CreatorModel] = None
        self.logic_model: Optional[LogicModel] = None
        self.creator_agent: Optional[CreatorAgent] = None
        self.logic_agent: Optional[LogicAgent] = None
        self.workflow: Optional[SynergyWorkflow] = None
        self.enhanced_workflow: Optional[EnhancedSynergyWorkflow] = None
        self.memory: Optional[VectorMemory] = None
        self.autonomy_monitor: Optional[AutonomyMonitor] = None
        
        # Исполнительные инструменты
        self.sandbox: Optional[CodeSandbox] = None
        self.browser: Optional[OmniBrowser] = None
        self.doc_engine: Optional[DocumentEngine] = None
        
        # Система приоритетов
        self.current_task_priority: TaskPriority = TaskPriority.LOW
        self.autonomy_task: Optional[asyncio.Task] = None
        self.autonomy_paused: bool = False
        
        self._initialized = False
        self._settings_db = None  # Ленивая инициализация
        
        logger.info("DualQwenAgent создан (компоненты будут загружены при первом использовании)")
    
    def _load_settings_from_db(self) -> Dict[str, Any]:
        """
        Загрузка настроек из базы данных SQLite
        
        Returns:
            Dict с настройками в формате, совместимом с config.yaml
        """
        try:
            # Импортируем здесь, чтобы избежать циклических зависимостей
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web', 'backend'))
            from database.settings_db import SettingsDatabase
            
            db = SettingsDatabase()
            settings = db.load_settings()
            
            if not settings:
                logger.warning("Настройки не найдены в БД, используем YAML")
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f)
            
            # Преобразуем настройки из БД в формат config.yaml
            config = {
                # Models - Creator
                "CREATOR_BASE_URL": settings.models.creator.base_url,
                "CREATOR_API_KEY": settings.models.creator.api_key,
                "CREATOR_MODEL": settings.models.creator.model_name,
                "CREATOR_TEMPERATURE": settings.models.creator.temperature,
                "CREATOR_MAX_TOKENS": settings.models.creator.max_tokens,
                "CREATOR_TOP_P": settings.models.creator.top_p,
                
                # Models - Logic
                "LOGIC_BASE_URL": settings.models.logic.base_url,
                "LOGIC_API_KEY": settings.models.logic.api_key,
                "LOGIC_MODEL": settings.models.logic.model_name,
                "LOGIC_TEMPERATURE": settings.models.logic.temperature,
                "LOGIC_MAX_TOKENS": settings.models.logic.max_tokens,
                "LOGIC_TOP_P": settings.models.logic.top_p,
                
                # Autonomy
                "AUTONOMY_ENABLED": settings.autonomy.enabled,
                "AUTONOMY_CHECK_INTERVAL": settings.autonomy.check_interval,
                "AUTONOMY_MAX_ARTICLES": settings.autonomy.max_articles,
                "AUTONOMY_AUTO_LEARN": settings.autonomy.auto_learn,
                
                # Tools
                "TAVILY_API_KEY": settings.tools.tavily_api_key or "",
                "GITHUB_TOKEN": settings.tools.github_token or "",
                "SANDBOX_TIMEOUT": settings.tools.sandbox_timeout,
                "SANDBOX_MEMORY": settings.tools.sandbox_memory,
                "BROWSER_HEADLESS": settings.tools.browser_headless,
                "BROWSER_TIMEOUT": settings.tools.browser_timeout,
                
                # System
                "QDRANT_HOST": settings.system.qdrant_host,
                "QDRANT_PORT": settings.system.qdrant_port,
                "QDRANT_COLLECTION": settings.system.qdrant_collection,
                "QDRANT_VECTOR_SIZE": settings.system.qdrant_vector_size,
                "MAX_CONFLICT_RETRIES": settings.system.max_conflict_retries,
                "CONFLICT_THRESHOLD": settings.system.conflict_threshold,
                "OUTPUT_DIR": settings.system.output_dir,
                "LOG_LEVEL": settings.system.log_level,
            }
            
            logger.info("✓ Настройки успешно загружены из базы данных")
            return config
            
        except Exception as e:
            logger.error(f"Ошибка загрузки настроек из БД: {e}")
            logger.info("Откат к загрузке из YAML")
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
    
    async def reload_settings_from_db(self):
        """
        Перезагрузка настроек из базы данных во время работы
        Используется после обновления настроек через UI
        
        Note: Некоторые настройки (например, модели) требуют полного перезапуска агента
        """
        logger.info("Перезагрузка настроек из базы данных...")
        
        new_config = self._load_settings_from_db()
        
        # Проверяем, изменились ли критические настройки (модели)
        models_changed = (
            self.config.get("CREATOR_BASE_URL") != new_config.get("CREATOR_BASE_URL") or
            self.config.get("CREATOR_MODEL") != new_config.get("CREATOR_MODEL") or
            self.config.get("LOGIC_BASE_URL") != new_config.get("LOGIC_BASE_URL") or
            self.config.get("LOGIC_MODEL") != new_config.get("LOGIC_MODEL")
        )
        
        if models_changed and self._initialized:
            logger.warning("⚠️ Изменены настройки моделей - требуется полный перезапуск агента!")
            return {
                "success": False,
                "message": "Настройки моделей изменены. Требуется перезапуск агента.",
                "restart_required": True
            }
        
        # Обновляем конфигурацию
        self.config = new_config
        
        # Обновляем runtime настройки (которые можно изменить без перезапуска)
        if self._initialized:
            # Обновляем настройки автономного режима
            if self.autonomy_monitor:
                self.autonomy_monitor.check_interval = self.config["AUTONOMY_CHECK_INTERVAL"]
                self.autonomy_monitor.max_articles = self.config["AUTONOMY_MAX_ARTICLES"]
            
            # Обновляем настройки инструментов
            if self.sandbox:
                self.sandbox.timeout = self.config.get("SANDBOX_TIMEOUT", 30)
                self.sandbox.memory_limit = self.config.get("SANDBOX_MEMORY", "512m")
            
            if self.browser:
                self.browser.timeout = self.config.get("BROWSER_TIMEOUT", 30000)
        
        logger.info("✓ Настройки успешно перезагружены")
        return {
            "success": True,
            "message": "Настройки обновлены",
            "restart_required": False
        }
    
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
        
        # 4. Workflow (оба варианта)
        logger.info("Создание Synergy Flow...")
        self.workflow = SynergyWorkflow(
            creator_agent=self.creator_agent,
            logic_agent=self.logic_agent,
            max_iterations=self.config["MAX_CONFLICT_RETRIES"],
            conflict_threshold=self.config["CONFLICT_THRESHOLD"]
        )
        
        self.enhanced_workflow = EnhancedSynergyWorkflow(
            creator_agent=self.creator_agent,
            logic_agent=self.logic_agent,
            max_iterations=self.config["MAX_CONFLICT_RETRIES"],
            conflict_threshold=self.config["CONFLICT_THRESHOLD"],
            use_task_graph=True
        )
        
        # 4.5. Исполнительные инструменты
        logger.info("Инициализация исполнительных инструментов...")
        self.sandbox = CodeSandbox(
            timeout=self.config.get("SANDBOX_TIMEOUT", 30),
            memory_limit=self.config.get("SANDBOX_MEMORY", "512m")
        )
        self.browser = OmniBrowser(
            headless=self.config.get("BROWSER_HEADLESS", True),
            timeout=self.config.get("BROWSER_TIMEOUT", 30000)
        )
        self.doc_engine = DocumentEngine(
            output_dir=self.config.get("OUTPUT_DIR", "outputs")
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
    
    async def process(
        self,
        task: str,
        priority: TaskPriority = TaskPriority.HIGH,
        use_task_graph: bool = False
    ) -> dict:
        """
        Обработка задачи через Synergy Flow
        
        Args:
            task: Задача от пользователя
            priority: Приоритет задачи
            use_task_graph: Использовать декомпозицию в граф задач
        
        Returns:
            Dict с результатом и опционально графом задач
        """
        if not self._initialized:
            await self.initialize()
        
        # Управление приоритетами
        await self._handle_priority(priority)
        
        logger.info(f"Обработка задачи (приоритет: {priority.value}): {task[:100]}...")
        
        # Поиск релевантного контекста в памяти
        context_results = await self.memory.search(task, limit=3)
        
        if context_results:
            logger.info(f"Найдено {len(context_results)} релевантных записей в памяти")
            context_str = "\n\n".join([r["content"][:200] for r in context_results])
            task_with_context = f"{task}\n\nКонтекст из памяти:\n{context_str}"
        else:
            task_with_context = task
        
        # Выбираем режим выполнения
        if use_task_graph:
            # Режим с декомпозицией
            tools = {
                "sandbox": self.sandbox,
                "browser": self.browser,
                "doc_engine": self.doc_engine
            }
            
            result_dict = await self.enhanced_workflow.run_with_graph(
                task_with_context,
                tools=tools
            )
            
            result = result_dict.get("visualization", "Граф выполнен")
            logger.info(f"Граф задач выполнен: {result_dict['progress']}")
            
            # Получаем граф из workflow
            task_graph = self.enhanced_workflow.current_graph
            graph_data = None
            if task_graph:
                graph_data = {
                    "task_id": task_graph.task_id,
                    "original_task": task_graph.original_task,
                    "subtasks": [
                        {
                            "id": st.id,
                            "title": st.title,
                            "description": st.description,
                            "type": st.type,
                            "status": st.status,
                            "priority": st.priority,
                            "dependencies": st.dependencies,
                            "estimated_time": st.estimated_time,
                            "assigned_agent": st.assigned_agent
                        }
                        for st in task_graph.subtasks
                    ],
                    "total_subtasks": task_graph.total_subtasks,
                    "estimated_total_time": task_graph.estimated_total_time
                }
            
            # Возобновляем автономный режим если был приостановлен
            await self._resume_autonomy()
            
            return {
                "result": result,
                "graph": graph_data
            }
        else:
            # Простой режим
            final_state: AgentState = await self.workflow.run(task_with_context)
            result = final_state.get('final_result') or "Не удалось получить результат"
            logger.info(f"Задача обработана за {final_state['iteration_count']} итераций")
            
            # Возобновляем автономный режим если был приостановлен
            await self._resume_autonomy()
            
            return {
                "result": result,
                "graph": None
            }
    
    async def _handle_priority(self, priority: TaskPriority):
        """
        Управление приоритетами задач
        Если новая задача критическая - приостанавливаем фоновые процессы
        """
        self.current_task_priority = priority
        
        if priority in [TaskPriority.CRITICAL, TaskPriority.HIGH]:
            if self.autonomy_monitor and not self.autonomy_paused:
                logger.info("Приостановка автономного режима для приоритетной задачи")
                self.autonomy_paused = True
                # Здесь можно добавить логику паузы
    
    async def _resume_autonomy(self):
        """Возобновление автономного режима после выполнения приоритетной задачи"""
        if self.autonomy_paused:
            logger.info("Возобновление автономного режима")
            self.autonomy_paused = False
            self.current_task_priority = TaskPriority.LOW
    
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
        
        # Закрываем инструменты
        if self.browser:
            await self.browser.close()
        if self.sandbox:
            self.sandbox.cleanup()
        
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
