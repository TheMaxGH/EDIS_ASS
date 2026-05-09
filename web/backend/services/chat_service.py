"""
Сервис управления чатами
"""
import asyncio
from typing import Dict, List, Optional, AsyncGenerator
from datetime import datetime
import uuid
from loguru import logger

from models.chat_models import (
    Message, ChatCreate, ChatResponse, MessageCreate,
    ChatHistory, ChatListItem, ChatList
)


class ChatService:
    """Сервис для управления чатами и сообщениями"""
    
    def __init__(self, edis_agent=None):
        """
        Args:
            edis_agent: Экземпляр DualQwenAgent для генерации ответов
        """
        self.edis_agent = edis_agent
        self.chats: Dict[str, ChatHistory] = {}
        logger.info("ChatService инициализирован")
    
    async def create_chat(self, chat_data: ChatCreate) -> ChatResponse:
        """Создание нового чата"""
        chat_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        chat = ChatHistory(
            chat_id=chat_id,
            title=chat_data.title or "Новый диалог",
            messages=[],
            created_at=now,
            updated_at=now,
            message_count=0
        )
        
        # Добавляем системное сообщение если указано
        if chat_data.system_prompt:
            system_msg = Message(
                chat_id=chat_id,
                role="system",
                content=chat_data.system_prompt,
                timestamp=now
            )
            chat.messages.append(system_msg)
            chat.message_count += 1
        
        self.chats[chat_id] = chat
        
        logger.info(f"Создан новый чат: {chat_id}")
        
        return ChatResponse(
            chat_id=chat_id,
            title=chat.title,
            created_at=chat.created_at,
            message_count=chat.message_count
        )
    
    async def get_chat(self, chat_id: str) -> Optional[ChatHistory]:
        """Получение чата по ID"""
        return self.chats.get(chat_id)
    
    async def list_chats(self) -> ChatList:
        """Список всех чатов"""
        chat_items = []
        
        for chat in self.chats.values():
            last_msg = None
            last_msg_time = None
            
            # Находим последнее сообщение (не системное)
            for msg in reversed(chat.messages):
                if msg.role != "system":
                    last_msg = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                    last_msg_time = msg.timestamp
                    break
            
            chat_items.append(ChatListItem(
                chat_id=chat.chat_id,
                title=chat.title,
                last_message=last_msg,
                last_message_time=last_msg_time,
                message_count=chat.message_count,
                created_at=chat.created_at
            ))
        
        # Сортируем по времени последнего сообщения
        chat_items.sort(
            key=lambda x: x.last_message_time or x.created_at,
            reverse=True
        )
        
        return ChatList(chats=chat_items, total=len(chat_items))
    
    async def delete_chat(self, chat_id: str) -> bool:
        """Удаление чата"""
        if chat_id in self.chats:
            del self.chats[chat_id]
            logger.info(f"Чат удален: {chat_id}")
            return True
        return False
    
    async def add_message(
        self,
        chat_id: str,
        message_data: MessageCreate
    ) -> Message:
        """Добавление сообщения пользователя"""
        chat = self.chats.get(chat_id)
        if not chat:
            raise ValueError(f"Чат не найден: {chat_id}")
        
        # Создаем сообщение пользователя
        user_message = Message(
            chat_id=chat_id,
            role="user",
            content=message_data.content,
            timestamp=datetime.now().isoformat()
        )
        
        chat.messages.append(user_message)
        chat.message_count += 1
        chat.updated_at = user_message.timestamp
        
        logger.info(f"Добавлено сообщение в чат {chat_id}")
        
        return user_message
    
    async def generate_response(
        self,
        chat_id: str,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Генерация ответа от EDIS
        
        Yields:
            Части ответа (при stream=True) или полный ответ (при stream=False)
        """
        chat = self.chats.get(chat_id)
        if not chat:
            raise ValueError(f"Чат не найден: {chat_id}")
        
        # Получаем контекст диалога
        context = self._build_context(chat)
        
        # Создаем сообщение ассистента
        assistant_message = Message(
            chat_id=chat_id,
            role="assistant",
            content="",
            timestamp=datetime.now().isoformat(),
            is_streaming=stream
        )
        
        chat.messages.append(assistant_message)
        chat.message_count += 1
        
        try:
            if self.edis_agent:
                # Используем EDIS агента для генерации
                if stream:
                    # Streaming режим
                    async for chunk in self._stream_from_edis(context):
                        assistant_message.content += chunk
                        yield chunk
                else:
                    # Обычный режим
                    response = await self._generate_from_edis(context)
                    assistant_message.content = response
                    yield response
            else:
                # Заглушка если агент не подключен
                response = "EDIS агент не подключен. Это тестовый ответ."
                if stream:
                    # Имитация streaming
                    for char in response:
                        assistant_message.content += char
                        yield char
                        await asyncio.sleep(0.05)
                else:
                    assistant_message.content = response
                    yield response
        
        except Exception as e:
            logger.error(f"Ошибка генерации ответа: {e}")
            error_msg = f"Ошибка: {str(e)}"
            assistant_message.content = error_msg
            yield error_msg
        
        finally:
            assistant_message.is_streaming = False
            chat.updated_at = datetime.now().isoformat()
    
    def _build_context(self, chat: ChatHistory) -> List[Dict[str, str]]:
        """Построение контекста для LLM"""
        context = []
        
        for msg in chat.messages:
            context.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return context
    
    async def _stream_from_edis(self, context: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Streaming генерация от EDIS"""
        if not self.edis_agent:
            # Fallback если агент не инициализирован
            response = "EDIS агент не инициализирован. Пожалуйста, запустите Backend с DualQwenAgent."
            for char in response:
                yield char
                await asyncio.sleep(0.05)
            return
        
        try:
            # Извлекаем последнее сообщение пользователя
            user_message = ""
            for msg in reversed(context):
                if msg["role"] == "user":
                    user_message = msg["content"]
                    break
            
            if not user_message:
                yield "Не найдено сообщение пользователя."
                return
            
            # Используем простой режим (без Task Graph) для чата
            result_data = await self.edis_agent.process(
                task=user_message,
                priority="medium",
                use_task_graph=False
            )
            
            # result_data это dict с ключами "result" и "graph"
            response = result_data.get("result", "Не удалось получить ответ.")
            
            # Streaming по символам
            for char in response:
                yield char
                await asyncio.sleep(0.01)  # Быстрее чем заглушка
                
        except Exception as e:
            logger.error(f"Ошибка генерации от EDIS: {e}")
            error_msg = f"Ошибка при генерации ответа: {str(e)}"
            for char in error_msg:
                yield char
                await asyncio.sleep(0.05)
    
    async def _generate_from_edis(self, context: List[Dict[str, str]]) -> str:
        """Обычная генерация от EDIS"""
        if not self.edis_agent:
            return "EDIS агент не инициализирован. Пожалуйста, запустите Backend с DualQwenAgent."
        
        try:
            # Извлекаем последнее сообщение пользователя
            user_message = ""
            for msg in reversed(context):
                if msg["role"] == "user":
                    user_message = msg["content"]
                    break
            
            if not user_message:
                return "Не найдено сообщение пользователя."
            
            # Используем простой режим (без Task Graph) для чата
            result_data = await self.edis_agent.process(
                task=user_message,
                priority="medium",
                use_task_graph=False
            )
            
            # result_data это dict с ключами "result" и "graph"
            return result_data.get("result", "Не удалось получить ответ.")
            
        except Exception as e:
            logger.error(f"Ошибка генерации от EDIS: {e}")
            return f"Ошибка при генерации ответа: {str(e)}"
    
    async def regenerate_response(
        self,
        chat_id: str,
        message_id: str
    ) -> AsyncGenerator[str, None]:
        """Регенерация ответа ассистента"""
        chat = self.chats.get(chat_id)
        if not chat:
            raise ValueError(f"Чат не найден: {chat_id}")
        
        # Находим сообщение
        message_index = None
        for i, msg in enumerate(chat.messages):
            if msg.id == message_id and msg.role == "assistant":
                message_index = i
                break
        
        if message_index is None:
            raise ValueError(f"Сообщение не найдено: {message_id}")
        
        # Удаляем старый ответ
        chat.messages.pop(message_index)
        chat.message_count -= 1
        
        # Генерируем новый
        async for chunk in self.generate_response(chat_id, stream=True):
            yield chunk
    
    async def delete_message(self, chat_id: str, message_id: str) -> bool:
        """Удаление сообщения"""
        chat = self.chats.get(chat_id)
        if not chat:
            return False
        
        for i, msg in enumerate(chat.messages):
            if msg.id == message_id:
                chat.messages.pop(i)
                chat.message_count -= 1
                chat.updated_at = datetime.now().isoformat()
                logger.info(f"Сообщение удалено: {message_id}")
                return True
        
        return False
    
    async def update_chat_title(self, chat_id: str, title: str) -> bool:
        """Обновление названия чата"""
        chat = self.chats.get(chat_id)
        if not chat:
            return False
        
        chat.title = title
        chat.updated_at = datetime.now().isoformat()
        logger.info(f"Название чата обновлено: {chat_id}")
        return True
