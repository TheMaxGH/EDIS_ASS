"""
Исполнительные инструменты для Dual Qwen Brain
Sandbox, Browser, Document Engine
"""
from .sandbox import CodeSandbox
from .browser import OmniBrowser
from .doc_engine import DocumentEngine

__all__ = [
    "CodeSandbox",
    "OmniBrowser", 
    "DocumentEngine"
]
