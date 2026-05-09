"""
Task Architect - система декомпозиции задач в граф подзадач
Реализует OpenClaw-подобную логику для автоматического планирования
"""
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from loguru import logger
import json
from enum import Enum
import uuid


class TaskType(str, Enum):
    """Типы задач"""
    RESEARCH = "research"  # Исследование, поиск информации (Творец)
    CODE = "code"  # Написание кода (Логик)
    ANALYSIS = "analysis"  # Анализ данных (Логик)
    CREATIVE = "creative"  # Креативная генерация (Творец)
    EXECUTION = "execution"  # Выполнение кода/команд (Логик)
    SYNTHESIS = "synthesis"  # Синтез результатов (оба)


class TaskStatus(str, Enum):
    """Статусы задач"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskPriority(str, Enum):
    """Приоритеты задач"""
    CRITICAL = "critical"  # Пользовательский запрос
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"  # Фоновые задачи


class SubTask(BaseModel):
    """Подзадача в графе"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(description="Краткое описание задачи")
    description: str = Field(description="Детальное описание")
    task_type: TaskType = Field(description="Тип задачи")
    assigned_to: Literal["creator", "logic", "both"] = Field(
        description="Кому назначена задача"
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="ID задач, которые должны быть выполнены до этой"
    )
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    result: Optional[str] = Field(default=None, description="Результат выполнения")
    error: Optional[str] = Field(default=None, description="Ошибка если есть")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskGraph(BaseModel):
    """Граф задач"""
    root_task: str = Field(description="Исходная задача пользователя")
    subtasks: List[SubTask] = Field(description="Список подзадач")
    created_at: str
    priority: TaskPriority = Field(default=TaskPriority.HIGH)
    
    def get_ready_tasks(self) -> List[SubTask]:
        """
        Получить задачи, готовые к выполнению
        (все зависимости выполнены, статус PENDING)
        """
        ready = []
        
        for task in self.subtasks:
            if task.status != TaskStatus.PENDING:
                continue
            
            # Проверяем зависимости
            dependencies_met = True
            for dep_id in task.dependencies:
                dep_task = self.get_task_by_id(dep_id)
                if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                    dependencies_met = False
                    break
            
            if dependencies_met:
                ready.append(task)
        
        # Сортируем по приоритету
        ready.sort(key=lambda t: list(TaskPriority).index(t.priority))
        return ready
    
    def get_task_by_id(self, task_id: str) -> Optional[SubTask]:
        """Получить задачу по ID"""
        for task in self.subtasks:
            if task.id == task_id:
                return task
        return None
    
    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        result: Optional[str] = None,
        error: Optional[str] = None
    ):
        """Обновить статус задачи"""
        task = self.get_task_by_id(task_id)
        if task:
            task.status = status
            if result:
                task.result = result
            if error:
                task.error = error
    
    def is_completed(self) -> bool:
        """Проверка, все ли задачи выполнены"""
        return all(
            task.status == TaskStatus.COMPLETED
            for task in self.subtasks
        )
    
    def get_progress(self) -> Dict[str, Any]:
        """Прогресс выполнения"""
        total = len(self.subtasks)
        completed = sum(1 for t in self.subtasks if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.subtasks if t.status == TaskStatus.FAILED)
        in_progress = sum(1 for t in self.subtasks if t.status == TaskStatus.IN_PROGRESS)
        
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "pending": total - completed - failed - in_progress,
            "percentage": (completed / total * 100) if total > 0 else 0
        }


class TaskArchitect:
    """
    Архитектор задач - декомпозирует сложные задачи в граф подзадач
    Использует Логика (Qwen3.5-397B-FP8) для планирования
    """
    
    def __init__(self, logic_agent):
        """
        Args:
            logic_agent: Экземпляр LogicAgent для планирования
        """
        self.logic_agent = logic_agent
        logger.info("TaskArchitect инициализирован")
    
    async def decompose_task(
        self,
        task: str,
        priority: TaskPriority = TaskPriority.HIGH
    ) -> TaskGraph:
        """
        Декомпозиция задачи в граф подзадач
        
        Args:
            task: Исходная задача от пользователя
            priority: Приоритет задачи
        
        Returns:
            TaskGraph с подзадачами
        """
        logger.info(f"Декомпозиция задачи: {task[:100]}...")
        
        # Промпт для Логика
        decomposition_prompt = f"""
Задача: {task}

Проанализируй эту задачу и разбей её на граф подзадач.

Для каждой подзадачи определи:
1. Краткое название (title)
2. Детальное описание (description)
3. Тип задачи (task_type): research, code, analysis, creative, execution, synthesis
4. Кому назначить (assigned_to): creator (для креатива/исследований), logic (для кода/анализа), both (для синтеза)
5. Зависимости (dependencies): ID задач, которые должны быть выполнены до этой

Верни результат в формате JSON:
{{
    "subtasks": [
        {{
            "title": "Название задачи",
            "description": "Детальное описание",
            "task_type": "research|code|analysis|creative|execution|synthesis",
            "assigned_to": "creator|logic|both",
            "dependencies": [],
            "priority": "high|medium|low"
        }}
    ]
}}

Важно:
- Задачи должны быть атомарными и выполнимыми
- Учитывай зависимости между задачами
- Первые задачи не должны иметь зависимостей
- Последняя задача обычно - synthesis (синтез результатов)
"""
        
        # Генерируем план через Логика
        from core.schemas import Message, MessageRole
        
        messages = [Message(
            role=MessageRole.USER,
            content=decomposition_prompt
        )]
        
        response = await self.logic_agent.model.generate(
            messages=messages,
            system_prompt="Ты - архитектор задач. Разбивай сложные задачи на подзадачи."
        )
        
        # Парсим JSON
        try:
            json_str = self._extract_json(response)
            data = json.loads(json_str)
            
            # Создаем подзадачи
            subtasks = []
            for i, task_data in enumerate(data.get("subtasks", [])):
                subtask = SubTask(
                    title=task_data.get("title", f"Задача {i+1}"),
                    description=task_data.get("description", ""),
                    task_type=TaskType(task_data.get("task_type", "analysis")),
                    assigned_to=task_data.get("assigned_to", "logic"),
                    dependencies=task_data.get("dependencies", []),
                    priority=TaskPriority(task_data.get("priority", "medium"))
                )
                subtasks.append(subtask)
            
            # Создаем граф
            from datetime import datetime
            task_graph = TaskGraph(
                root_task=task,
                subtasks=subtasks,
                created_at=datetime.now().isoformat(),
                priority=priority
            )
            
            logger.info(f"Создан граф из {len(subtasks)} подзадач")
            return task_graph
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Ошибка парсинга плана: {e}")
            
            # Fallback: создаем простой граф
            fallback_task = SubTask(
                title="Выполнить задачу",
                description=task,
                task_type=TaskType.ANALYSIS,
                assigned_to="logic",
                dependencies=[],
                priority=priority
            )
            
            from datetime import datetime
            return TaskGraph(
                root_task=task,
                subtasks=[fallback_task],
                created_at=datetime.now().isoformat(),
                priority=priority
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
    
    def visualize_graph(self, task_graph: TaskGraph) -> str:
        """
        Визуализация графа задач в текстовом формате
        
        Args:
            task_graph: Граф задач
        
        Returns:
            Текстовое представление графа
        """
        output = []
        output.append(f"📋 Задача: {task_graph.root_task}")
        output.append(f"🎯 Приоритет: {task_graph.priority.value}")
        output.append(f"📊 Прогресс: {task_graph.get_progress()}")
        output.append("\n" + "="*60 + "\n")
        
        # Группируем по уровням (задачи без зависимостей - уровень 0, и т.д.)
        levels = self._calculate_levels(task_graph)
        
        for level in sorted(levels.keys()):
            output.append(f"Уровень {level}:")
            for task in levels[level]:
                status_emoji = {
                    TaskStatus.PENDING: "⏳",
                    TaskStatus.IN_PROGRESS: "🔄",
                    TaskStatus.COMPLETED: "✅",
                    TaskStatus.FAILED: "❌",
                    TaskStatus.BLOCKED: "🚫"
                }
                
                emoji = status_emoji.get(task.status, "❓")
                output.append(f"  {emoji} [{task.assigned_to}] {task.title}")
                
                if task.dependencies:
                    deps = ", ".join(task.dependencies[:3])
                    output.append(f"      └─ Зависит от: {deps}")
            
            output.append("")
        
        return "\n".join(output)
    
    def _calculate_levels(self, task_graph: TaskGraph) -> Dict[int, List[SubTask]]:
        """Вычисление уровней задач для визуализации"""
        levels = {}
        
        def get_level(task: SubTask, visited: set) -> int:
            if task.id in visited:
                return 0
            visited.add(task.id)
            
            if not task.dependencies:
                return 0
            
            max_dep_level = 0
            for dep_id in task.dependencies:
                dep_task = task_graph.get_task_by_id(dep_id)
                if dep_task:
                    dep_level = get_level(dep_task, visited.copy())
                    max_dep_level = max(max_dep_level, dep_level)
            
            return max_dep_level + 1
        
        for task in task_graph.subtasks:
            level = get_level(task, set())
            if level not in levels:
                levels[level] = []
            levels[level].append(task)
        
        return levels
    
    def export_graph_json(self, task_graph: TaskGraph) -> str:
        """Экспорт графа в JSON для веб-интерфейса"""
        return task_graph.model_dump_json(indent=2)
