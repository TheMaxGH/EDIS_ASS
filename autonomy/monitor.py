"""
Система автономного мониторинга и самообучения
Режим "Сна" - фоновая работа агента
"""
import asyncio
from typing import List, Dict, Any
from datetime import datetime
import httpx
from loguru import logger

from core.schemas import AutonomyTask, KnowledgeEntry
from core.memory.vector_store import VectorMemory


class AutonomyMonitor:
    """
    Монитор для автономного режима
    Сканирует GitHub Trending, Arxiv, новости и обновляет базу знаний
    """
    
    def __init__(
        self,
        vector_memory: VectorMemory,
        tavily_api_key: str,
        github_token: str,
        check_interval: int = 3600,
        max_articles: int = 10
    ):
        self.memory = vector_memory
        self.tavily_api_key = tavily_api_key
        self.github_token = github_token
        self.check_interval = check_interval
        self.max_articles = max_articles
        self.is_running = False
        
        logger.info("AutonomyMonitor инициализирован")
    
    async def start(self):
        """Запуск автономного режима"""
        self.is_running = True
        logger.info("Автономный режим активирован")
        
        while self.is_running:
            try:
                await self._monitoring_cycle()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Ошибка в цикле мониторинга: {e}")
                await asyncio.sleep(60)  # Короткая пауза перед повтором
    
    def stop(self):
        """Остановка автономного режима"""
        self.is_running = False
        logger.info("Автономный режим деактивирован")
    
    async def _monitoring_cycle(self):
        """Один цикл мониторинга"""
        logger.info("Начало цикла автономного мониторинга")
        
        # Параллельный запуск всех задач мониторинга
        tasks = [
            self._monitor_github_trending(),
            self._monitor_arxiv(),
            self._monitor_tech_news()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Обработка результатов
        total_entries = 0
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Ошибка в задаче мониторинга: {result}")
            elif isinstance(result, list):
                total_entries += len(result)
        
        logger.info(f"Цикл завершен. Добавлено {total_entries} новых записей в память")
    
    async def _monitor_github_trending(self) -> List[KnowledgeEntry]:
        """Мониторинг GitHub Trending"""
        logger.info("Сканирование GitHub Trending...")
        
        entries = []
        
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"token {self.github_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                # Поиск трендовых репозиториев по тегам
                tags = ["AI", "LLM", "machine-learning", "deep-learning"]
                
                for tag in tags:
                    url = f"https://api.github.com/search/repositories"
                    params = {
                        "q": f"topic:{tag} stars:>100",
                        "sort": "updated",
                        "order": "desc",
                        "per_page": 5
                    }
                    
                    response = await client.get(url, headers=headers, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        for repo in data.get("items", [])[:3]:
                            entry = KnowledgeEntry(
                                content=f"Репозиторий: {repo['full_name']}\n"
                                        f"Описание: {repo.get('description', 'N/A')}\n"
                                        f"Звезды: {repo['stargazers_count']}\n"
                                        f"Язык: {repo.get('language', 'N/A')}",
                                source=f"github:{repo['html_url']}",
                                timestamp=datetime.utcnow().isoformat(),
                                metadata={
                                    "type": "github_trending",
                                    "stars": repo['stargazers_count'],
                                    "language": repo.get('language')
                                }
                            )
                            entries.append(entry)
                    
                    await asyncio.sleep(1)  # Rate limiting
            
            # Сохранение в векторную память
            await self.memory.add_entries(entries)
            logger.info(f"GitHub: добавлено {len(entries)} репозиториев")
            
        except Exception as e:
            logger.error(f"Ошибка мониторинга GitHub: {e}")
        
        return entries
    
    async def _monitor_arxiv(self) -> List[KnowledgeEntry]:
        """Мониторинг Arxiv через Tavily"""
        logger.info("Поиск статей на Arxiv...")
        
        entries = []
        
        try:
            async with httpx.AsyncClient() as client:
                url = "https://api.tavily.com/search"
                
                queries = [
                    "large language models arxiv",
                    "AI agents arxiv",
                    "reinforcement learning arxiv"
                ]
                
                for query in queries:
                    payload = {
                        "api_key": self.tavily_api_key,
                        "query": query,
                        "search_depth": "advanced",
                        "max_results": 3,
                        "include_domains": ["arxiv.org"]
                    }
                    
                    response = await client.post(url, json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        for result in data.get("results", []):
                            entry = KnowledgeEntry(
                                content=f"Статья: {result['title']}\n"
                                        f"Контент: {result['content'][:500]}...",
                                source=f"arxiv:{result['url']}",
                                timestamp=datetime.utcnow().isoformat(),
                                metadata={
                                    "type": "arxiv_paper",
                                    "score": result.get("score", 0)
                                }
                            )
                            entries.append(entry)
                    
                    await asyncio.sleep(1)
            
            await self.memory.add_entries(entries)
            logger.info(f"Arxiv: добавлено {len(entries)} статей")
            
        except Exception as e:
            logger.error(f"Ошибка мониторинга Arxiv: {e}")
        
        return entries
    
    async def _monitor_tech_news(self) -> List[KnowledgeEntry]:
        """Мониторинг технологических новостей"""
        logger.info("Поиск технологических новостей...")
        
        entries = []
        
        try:
            async with httpx.AsyncClient() as client:
                url = "https://api.tavily.com/search"
                
                payload = {
                    "api_key": self.tavily_api_key,
                    "query": "AI technology news latest developments",
                    "search_depth": "basic",
                    "max_results": self.max_articles,
                    "include_domains": ["techcrunch.com", "theverge.com", "arstechnica.com"]
                }
                
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for result in data.get("results", []):
                        entry = KnowledgeEntry(
                            content=f"Новость: {result['title']}\n"
                                    f"Контент: {result['content'][:500]}...",
                            source=f"news:{result['url']}",
                            timestamp=datetime.utcnow().isoformat(),
                            metadata={
                                "type": "tech_news",
                                "score": result.get("score", 0)
                            }
                        )
                        entries.append(entry)
            
            await self.memory.add_entries(entries)
            logger.info(f"Новости: добавлено {len(entries)} статей")
            
        except Exception as e:
            logger.error(f"Ошибка мониторинга новостей: {e}")
        
        return entries
