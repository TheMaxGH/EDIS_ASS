"""
Расширенный Synergy Flow с поддержкой Task Graph
Циклическое взаимодействие между Творцом и Логиком + выполнение графа задач
"""
from typing import Literal, Optional
from langgraph.graph import StateGraph, END
from loguru import logger

from core.schemas import (
    AgentState, Message, MessageRole, ConflictStatus
)
from agents.brain_agents import CreatorAgent, LogicAgent
from core.workflow.task_architect import TaskArchitect, TaskGraph, TaskStatus, SubTask


class EnhancedSynergyWorkflow:
    """
    Расширенный Workflow с поддержкой графа задач
    Может работать в двух режимах:
    1. Простой режим (как раньше) - один цикл Творец-Логик
    2. Режим графа - декомпозиция и выполнение подзадач
    """
    
    def __init__(
        self,
        creator_agent: CreatorAgent,
        logic_agent: LogicAgent,
        max_iterations: int = 3,
        conflict_threshold: float = 0.7,
        use_task_graph: bool = True
    ):
        self.creator = creator_agent
        self.logic = logic_agent
        self.max_iterations = max_iterations
        self.conflict_threshold = conflict_threshold
        self.use_task_graph = use_task_graph
        
        # Task Architect для декомпозиции
        self.task_architect = TaskArchitect(logic_agent)
        
        # Текущий граф задач
        self.current_graph: Optional[TaskGraph] = None
        
        # Создание графа
        self.workflow = self._build_graph()
        logger.info("EnhancedSynergyWorkflow инициализирован")
    
    def _build_graph(self):
        """Построение LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Добавляем узлы
        workflow.add_node("creator", self._creator_node)
        workflow.add_node("logic", self._logic_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Устанавливаем точку входа
        workflow.set_entry_point("creator")
        
        # Добавляем ребра
        workflow.add_edge("creator", "logic")
        
        # Условное ребро от logic
        workflow.add_conditional_edges(
            "logic",
            self._should_continue,
            {
                "continue": "creator",
                "finalize": "finalize",
                "end": END
            }
        )
        
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    async def _creator_node(self, state: AgentState) -> AgentState:
        """Узел Творца - генерация идеи"""
        logger.info(f"Творец: итерация {state['iteration_count'] + 1}")
        
        previous_feedback = None
        if state.get('logic_feedback'):
            previous_feedback = state['logic_feedback'].feedback
        
        creator_output = await self.creator.generate_idea(
            task=state['current_task'],
            context=state['messages'],
            previous_feedback=previous_feedback
        )
        
        state['creator_output'] = creator_output
        state['messages'].append(Message(
            role=MessageRole.CREATOR,
            content=f"Идея: {creator_output.idea}\n\nГипотеза: {creator_output.hypothesis}",
            metadata={"creativity_score": creator_output.creativity_score}
        ))
        
        return state
    
    async def _logic_node(self, state: AgentState) -> AgentState:
        """Узел Логика - верификация идеи"""
        logger.info("Логик: анализ идеи Творца")
        
        if not state.get('creator_output'):
            raise ValueError("Нет вывода от Творца для анализа")
        
        logic_feedback = await self.logic.verify_idea(
            task=state['current_task'],
            creator_output=state['creator_output'],
            context=state['messages']
        )
        
        state['logic_feedback'] = logic_feedback
        state['messages'].append(Message(
            role=MessageRole.LOGIC,
            content=f"Статус: {logic_feedback.status}\n\nФидбек: {logic_feedback.feedback}",
            metadata={"conflict_score": logic_feedback.conflict_score}
        ))
        
        state['iteration_count'] += 1
        
        return state
    
    def _should_continue(self, state: AgentState) -> Literal["continue", "finalize", "end"]:
        """Решение о продолжении цикла"""
        if not state.get('logic_feedback'):
            return "end"
        
        if state['iteration_count'] >= self.max_iterations:
            logger.warning(f"Достигнут лимит итераций ({self.max_iterations})")
            return "end"
        
        if state['logic_feedback'].status == ConflictStatus.APPROVED:
            logger.info("Идея одобрена Логиком")
            return "finalize"
        
        if state['logic_feedback'].conflict_score >= self.conflict_threshold:
            logger.info(
                f"Конфликт обнаружен (score={state['logic_feedback'].conflict_score}), "
                "возвращаемся к Творцу"
            )
            return "continue"
        
        logger.info("Конфликт незначительный, финализируем")
        return "finalize"
    
    async def _finalize_node(self, state: AgentState) -> AgentState:
        """Финализация результата"""
        logger.info("Финализация результата")
        
        if state.get('logic_feedback') and state['logic_feedback'].execution_plan:
            state['final_result'] = state['logic_feedback'].execution_plan
        elif state.get('creator_output'):
            state['final_result'] = state['creator_output'].hypothesis
        else:
            state['final_result'] = "Не удалось сформировать финальный результат"
        
        return state
    
    async def run(self, task: str) -> AgentState:
        """
        Запуск workflow (простой режим без графа)
        
        Args:
            task: Задача от пользователя
        
        Returns:
            Финальное состояние с результатом
        """
        logger.info(f"Запуск Synergy Flow для задачи: {task[:100]}...")
        
        from core.schemas import AgentState as AgentStateType
        
        initial_state: AgentStateType = {
            "messages": [],
            "current_task": task,
            "creator_output": None,
            "logic_feedback": None,
            "iteration_count": 0,
            "max_iterations": self.max_iterations,
            "final_result": None
        }
        
        final_state = await self.workflow.ainvoke(initial_state)
        
        logger.info(
            f"Synergy Flow завершен за {final_state['iteration_count']} итераций. "
            f"Статус: {final_state['logic_feedback'].status if final_state.get('logic_feedback') else 'N/A'}"
        )
        
        return final_state
    
    async def run_with_graph(
        self,
        task: str,
        tools: Optional[dict] = None
    ) -> dict:
        """
        Запуск с декомпозицией задачи в граф
        
        Args:
            task: Задача от пользователя
            tools: Словарь доступных инструментов (sandbox, browser, doc_engine)
        
        Returns:
            Dict с результатами выполнения всех подзадач
        """
        logger.info(f"Запуск с Task Graph для задачи: {task[:100]}...")
        
        # 1. Декомпозиция задачи
        from core.workflow.task_architect import TaskPriority
        self.current_graph = await self.task_architect.decompose_task(
            task,
            priority=TaskPriority.HIGH
        )
        
        logger.info(f"Создан граф из {len(self.current_graph.subtasks)} подзадач")
        logger.info("\n" + self.task_architect.visualize_graph(self.current_graph))
        
        # 2. Выполнение подзадач
        results = {}
        max_parallel = 3  # Максимум параллельных задач
        
        while not self.current_graph.is_completed():
            # Получаем готовые к выполнению задачи
            ready_tasks = self.current_graph.get_ready_tasks()
            
            if not ready_tasks:
                logger.warning("Нет готовых задач, но граф не завершен. Возможна циклическая зависимость")
                break
            
            # Выполняем задачи (пока последовательно, можно распараллелить)
            for subtask in ready_tasks[:max_parallel]:
                logger.info(f"Выполнение подзадачи: {subtask.title}")
                
                # Обновляем статус
                self.current_graph.update_task_status(
                    subtask.id,
                    TaskStatus.IN_PROGRESS
                )
                
                try:
                    # Выполняем подзадачу
                    result = await self._execute_subtask(subtask, tools)
                    
                    # Сохраняем результат
                    self.current_graph.update_task_status(
                        subtask.id,
                        TaskStatus.COMPLETED,
                        result=result
                    )
                    results[subtask.id] = {
                        "title": subtask.title,
                        "result": result,
                        "status": "completed"
                    }
                    
                    logger.info(f"✓ Подзадача завершена: {subtask.title}")
                    
                except Exception as e:
                    logger.error(f"✗ Ошибка выполнения подзадачи {subtask.title}: {e}")
                    self.current_graph.update_task_status(
                        subtask.id,
                        TaskStatus.FAILED,
                        error=str(e)
                    )
                    results[subtask.id] = {
                        "title": subtask.title,
                        "error": str(e),
                        "status": "failed"
                    }
        
        # 3. Формируем финальный результат
        progress = self.current_graph.get_progress()
        logger.info(f"Граф выполнен: {progress}")
        
        return {
            "task": task,
            "graph": self.current_graph.model_dump(),
            "results": results,
            "progress": progress,
            "visualization": self.task_architect.visualize_graph(self.current_graph)
        }
    
    async def _execute_subtask(
        self,
        subtask: SubTask,
        tools: Optional[dict] = None
    ) -> str:
        """
        Выполнение одной подзадачи
        
        Args:
            subtask: Подзадача для выполнения
            tools: Доступные инструменты
        
        Returns:
            Результат выполнения
        """
        # Формируем контекст из зависимостей
        context = []
        for dep_id in subtask.dependencies:
            dep_task = self.current_graph.get_task_by_id(dep_id)
            if dep_task and dep_task.result:
                context.append(f"Результат '{dep_task.title}': {dep_task.result[:200]}")
        
        context_str = "\n".join(context) if context else "Нет предыдущих результатов"
        
        # Формируем промпт
        task_prompt = f"""
Подзадача: {subtask.title}
Описание: {subtask.description}
Тип: {subtask.task_type.value}

Контекст из предыдущих задач:
{context_str}

Выполни эту подзадачу и предоставь результат.
"""
        
        # Выбираем агента
        if subtask.assigned_to == "creator":
            # Творец генерирует идеи
            output = await self.creator.generate_idea(
                task=task_prompt,
                context=[],
                previous_feedback=None
            )
            return output.hypothesis
            
        elif subtask.assigned_to == "logic":
            # Логик выполняет анализ/код
            from core.schemas import Message, MessageRole, CreatorOutput
            
            # Создаем фейковый вывод Творца для Логика
            fake_creator_output = CreatorOutput(
                idea=subtask.title,
                hypothesis=subtask.description,
                reasoning="Подзадача из графа",
                creativity_score=0.5
            )
            
            feedback = await self.logic.verify_idea(
                task=task_prompt,
                creator_output=fake_creator_output,
                context=[]
            )
            
            return feedback.execution_plan or feedback.feedback
            
        else:  # both
            # Запускаем полный цикл
            state = await self.run(task_prompt)
            return state.get('final_result', "Нет результата")
