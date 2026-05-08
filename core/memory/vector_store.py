"""
Векторная память на базе Qdrant
Хранение и поиск знаний для RAG
"""
from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
)
from sentence_transformers import SentenceTransformer
from loguru import logger
import uuid

from core.schemas import KnowledgeEntry


class VectorMemory:
    """
    Векторная память для хранения знаний агента
    Использует Qdrant для векторного поиска
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "dual_qwen_memory",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        vector_size: int = 384
    ):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.vector_size = vector_size
        
        # Модель для эмбеддингов
        self.encoder = SentenceTransformer(embedding_model)
        
        # Инициализация коллекции
        self._init_collection()
        
        logger.info(f"VectorMemory инициализирована: {collection_name}")
    
    def _init_collection(self):
        """Инициализация коллекции в Qdrant"""
        try:
            # Проверяем существование коллекции
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                # Создаем коллекцию
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Коллекция {self.collection_name} создана")
            else:
                logger.info(f"Коллекция {self.collection_name} уже существует")
                
        except Exception as e:
            logger.error(f"Ошибка инициализации коллекции: {e}")
            raise
    
    def _embed_text(self, text: str) -> List[float]:
        """Создание эмбеддинга для текста"""
        embedding = self.encoder.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    async def add_entry(self, entry: KnowledgeEntry) -> str:
        """
        Добавление одной записи в память
        
        Args:
            entry: Запись знаний
        
        Returns:
            ID добавленной записи
        """
        # Генерируем эмбеддинг
        if entry.embedding is None:
            entry.embedding = self._embed_text(entry.content)
        
        # Генерируем уникальный ID
        point_id = str(uuid.uuid4())
        
        # Создаем точку для Qdrant
        point = PointStruct(
            id=point_id,
            vector=entry.embedding,
            payload={
                "content": entry.content,
                "source": entry.source,
                "timestamp": entry.timestamp,
                "metadata": entry.metadata
            }
        )
        
        # Добавляем в Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )
        
        logger.debug(f"Добавлена запись {point_id} из источника {entry.source}")
        return point_id
    
    async def add_entries(self, entries: List[KnowledgeEntry]) -> List[str]:
        """
        Добавление нескольких записей
        
        Args:
            entries: Список записей
        
        Returns:
            Список ID добавленных записей
        """
        if not entries:
            return []
        
        points = []
        ids = []
        
        for entry in entries:
            # Генерируем эмбеддинг
            if entry.embedding is None:
                entry.embedding = self._embed_text(entry.content)
            
            point_id = str(uuid.uuid4())
            ids.append(point_id)
            
            points.append(PointStruct(
                id=point_id,
                vector=entry.embedding,
                payload={
                    "content": entry.content,
                    "source": entry.source,
                    "timestamp": entry.timestamp,
                    "metadata": entry.metadata
                }
            ))
        
        # Batch upsert
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        logger.info(f"Добавлено {len(entries)} записей в память")
        return ids
    
    async def search(
        self,
        query: str,
        limit: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Поиск релевантных записей
        
        Args:
            query: Поисковый запрос
            limit: Максимальное количество результатов
            filter_metadata: Фильтр по метаданным
        
        Returns:
            Список найденных записей с оценками релевантности
        """
        # Создаем эмбеддинг запроса
        query_vector = self._embed_text(query)
        
        # Формируем фильтр (если нужен)
        search_filter = None
        if filter_metadata:
            conditions = []
            for key, value in filter_metadata.items():
                conditions.append(
                    FieldCondition(
                        key=f"metadata.{key}",
                        match=MatchValue(value=value)
                    )
                )
            if conditions:
                search_filter = Filter(must=conditions)
        
        # Поиск
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=search_filter
        )
        
        # Форматирование результатов
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result.id,
                "score": result.score,
                "content": result.payload.get("content"),
                "source": result.payload.get("source"),
                "timestamp": result.payload.get("timestamp"),
                "metadata": result.payload.get("metadata", {})
            })
        
        logger.debug(f"Найдено {len(formatted_results)} результатов для запроса: {query[:50]}...")
        return formatted_results
    
    async def get_recent(
        self,
        limit: int = 10,
        entry_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Получение последних записей
        
        Args:
            limit: Количество записей
            entry_type: Тип записей (github_trending, arxiv_paper, tech_news)
        
        Returns:
            Список последних записей
        """
        search_filter = None
        if entry_type:
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="metadata.type",
                        match=MatchValue(value=entry_type)
                    )
                ]
            )
        
        # Scroll для получения записей
        results, _ = self.client.scroll(
            collection_name=self.collection_name,
            limit=limit,
            scroll_filter=search_filter
        )
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result.id,
                "content": result.payload.get("content"),
                "source": result.payload.get("source"),
                "timestamp": result.payload.get("timestamp"),
                "metadata": result.payload.get("metadata", {})
            })
        
        return formatted_results
