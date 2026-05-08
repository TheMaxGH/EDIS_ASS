"""
LangGraph Workflow для Synergy Flow
Циклическое взаимодействие между Творцом и Логиком
"""
from typing import Literal
from langgraph.graph import StateGraph, END
from loguru import logger

from core.schemas import (
    AgentState, Message, MessageRole, ConflictStatus
)
from agents.brain_agents import CreatorAgent, LogicAgent


class SynergyWorkflow:
    """
    Workflow для взаимодействия Творца и Логика
    Реализует циклический граф с конфликт-резолюцией
    """
    
    def __init__(
        self,
        creator_agent: CreatorAgent,
        logic_agent: LogicAgent,
        max_iterations: int = 3,
        conflict_threshold: float = 0.7
    ):
        self.creator = creator_agent
        self.logic = logic_agent
        self.max_iterations = max_iterations
        self.conflict_threshold = conflict_threshold
        
        # Создание графа
        self.workflow = self._build_graph()
        logger.info("SynergyWorkflow инициализирован")
    
    def _build_graph(self):
        """Построение LangGraph workflow"""
        
        # Определяем граф состояний
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
                "continue": "creator",  # Конфликт - возвращаемся к Творцу
                "finalize": "finalize",  # Одобрено - финализируем
                "end": END  # Превышен лимит итераций
            }
        )
        
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    async def _creator_node(self, state: AgentState) -> AgentState:
        """
        Узел Творца - генерация идеи
        """
        logger.info(f"Творец: итерация {state['iteration_count'] + 1}")
        
        # Получаем фидбек от предыдущей итерации (если есть)
        previous_feedback = None
        if state.get('logic_feedback'):
            previous_feedback = state['logic_feedback'].feedback
        
        # Генерируем идею
        creator_output = await self.creator.generate_idea(
            task=state['current_task'],
            context=state['messages'],
            previous_feedback=previous_feedback
        )
        
        # Обновляем состояние
        state['creator_output'] = creator_output
        state['messages'].append(Message(
            role=MessageRole.CREATOR,
            content=f"Идея: {creator_output.idea}\n\nГипотеза: {creator_output.hypothesis}",
            metadata={"creativity_score": creator_output.creativity_score}
        ))
        
        return state
    
    async def _logic_node(self, state: AgentState) -> AgentState:
        """
        Узел Логика - верификация идеи
        """
        logger.info("Логик: анализ идеи Творца")
        
        if not state.get('creator_output'):
            raise ValueError("Нет вывода от Творца для анализа")
        
        # Верифицируем идею
        logic_feedback = await self.logic.verify_idea(
            task=state['current_task'],
            creator_output=state['creator_output'],
            context=state['messages']
        )
        
        # Обновляем состояние
        state['logic_feedback'] = logic_feedback
        state['messages'].append(Message(
            role=MessageRole.LOGIC,
            content=f"Статус: {logic_feedback.status}\n\nФидбек: {logic_feedback.feedback}",
            metadata={"conflict_score": logic_feedback.conflict_score}
        ))
        
        state['iteration_count'] += 1
        
        return state
    
    def _should_continue(self, state: AgentState) -> Literal["continue", "finalize", "end"]:
        """
        Решение о продолжении цикла
        
        Returns:
            "continue" - конфликт, нужна доработка
            "finalize" - идея одобрена
            "end" - превышен лимит итераций
        """
        if not state.get('logic_feedback'):
            return "end"
        
        # Проверяем лимит итераций
        if state['iteration_count'] >= self.max_iterations:
            logger.warning(f"Достигнут лимит итераций ({self.max_iterations})")
            return "end"
        
        # Проверяем статус
        if state['logic_feedback'].status == ConflictStatus.APPROVED:
            logger.info("Идея одобрена Логиком")
            return "finalize"
        
        # Проверяем степень конфликта
        if state['logic_feedback'].conflict_score >= self.conflict_threshold:
            logger.info(
                f"Конфликт обнаружен (score={state['logic_feedback'].conflict_score}), "
                "возвращаемся к Творцу"
            )
            return "continue"
        
        # Если конфликт небольшой, но статус не approved - финализируем с оговорками
        logger.info("Конфликт незначительный, финализируем")
        return "finalize"
    
    async def _finalize_node(self, state: AgentState) -> AgentState:
        """
        Финализация результата
        """
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
        Запуск workflow
        
        Args:
            task: Задача от пользователя
        
        Returns:
            Финальное состояние с результатом
        """
        logger.info(f"Запуск Synergy Flow для задачи: {task[:100]}...")
        
        # Инициализация состояния (TypedDict)
        initial_state: AgentState = {
            "messages": [],
            "current_task": task,
            "creator_output": None,
            "logic_feedback": None,
            "iteration_count": 0,
            "max_iterations": self.max_iterations,
            "final_result": None
        }
        
        # Запуск графа
        final_state = await self.workflow.ainvoke(initial_state)
        
        logger.info(
            f"Synergy Flow завершен за {final_state['iteration_count']} итераций. "
            f"Статус: {final_state['logic_feedback'].status if final_state.get('logic_feedback') else 'N/A'}"
        )
        
        return final_state
