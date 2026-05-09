"""
Базовые типы и схемы для Dual Qwen Brain
"""
from typing import Literal, Optional, List, Dict, Any, TypedDict
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    """Роли сообщений в системе"""
    USER = "user"
    CREATOR = "creator"
    LOGIC = "logic"
    SYSTEM = "system"


class ConflictStatus(str, Enum):
    """Статусы конфликта между Творцом и Логиком"""
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


class Message(BaseModel):
    """Базовое сообщение в системе"""
    role: MessageRole
    content: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CreatorOutput(BaseModel):
    """Выход Творца (Qwen-72B)"""
    idea: str = Field(description="Основная идея или гипотеза")
    hypothesis: str = Field(description="Развернутая гипотеза")
    reasoning: str = Field(description="Цепочка рассуждений")
    alternative_approaches: Optional[List[str]] = Field(
        default=None,
        description="Альтернативные подходы"
    )
    creativity_score: float = Field(
        ge=0.0, le=1.0,
        description="Самооценка креативности"
    )


class LogicFeedback(BaseModel):
    """Фидбек от Логика (Qwen3.5-397B-FP8)"""
    status: ConflictStatus
    feedback: str = Field(description="Детальный фидбек")
    logical_errors: Optional[List[str]] = Field(
        default=None,
        description="Обнаруженные логические ошибки"
    )
    conflict_score: float = Field(
        ge=0.0, le=1.0,
        description="Степень конфликта (0 = полное согласие)"
    )
    execution_plan: Optional[str] = Field(
        default=None,
        description="План исполнения (если одобрено)"
    )


class AgentState(TypedDict, total=False):
    """Состояние агента в LangGraph (TypedDict для совместимости с LangGraph)"""
    messages: List[Message]
    current_task: str
    creator_output: Optional[CreatorOutput]
    logic_feedback: Optional[LogicFeedback]
    iteration_count: int
    max_iterations: int
    final_result: Optional[str]


class AutonomyTask(BaseModel):
    """Задача для автономного режима"""
    task_type: Literal["github_trending", "arxiv_search", "tech_news"]
    query: Optional[str] = None
    tags: Optional[List[str]] = None
    max_results: int = 10


class KnowledgeEntry(BaseModel):
    """Запись в базе знаний (RAG)"""
    content: str
    source: str
    timestamp: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
