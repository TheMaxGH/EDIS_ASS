"""
API роутер для чата
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import StreamingResponse
from typing import Optional
import json
import os
from loguru import logger

from models.chat_models import (
    ChatCreate, ChatResponse, MessageCreate, MessageResponse,
    ChatHistory, ChatList, RegenerateRequest, DeleteMessageRequest
)
from services.chat_service import ChatService


router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

# Глобальный экземпляр сервиса (будет инициализирован в main.py)
chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """Dependency для получения сервиса чата"""
    if chat_service is None:
        raise HTTPException(status_code=500, detail="Chat service not initialized")
    return chat_service


async def verify_api_key(x_api_key: str = Header(...)):
    """Проверка API ключа"""
    expected_key = os.getenv("EDIS_API_KEY", "your-secret-key-here")
    if x_api_key != expected_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key


@router.post("/create", response_model=ChatResponse)
async def create_chat(
    chat_data: ChatCreate,
    service: ChatService = Depends(get_chat_service),
    api_key: str = Depends(verify_api_key)
):
    """
    Создание нового чата
    
    - **title**: Название чата (опционально)
    - **system_prompt**: Системный промпт (опционально)
    """
    try:
        response = await service.create_chat(chat_data)
        return response
    except Exception as e:
        logger.error(f"Ошибка создания чата: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{chat_id}", response_model=ChatHistory)
async def get_chat(
    chat_id: str,
    service: ChatService = Depends(get_chat_service),
    api_key: str = Depends(verify_api_key)
):
    """
    Получение истории чата
    
    - **chat_id**: ID чата
    """
    chat = await service.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
    return chat


@router.get("/list/all", response_model=ChatList)
async def list_chats(
    service: ChatService = Depends(get_chat_service),
    api_key: str = Depends(verify_api_key)
):
    """
    Список всех чатов
    """
    try:
        chats = await service.list_chats()
        return chats
    except Exception as e:
        logger.error(f"Ошибка получения списка чатов: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: str,
    service: ChatService = Depends(get_chat_service),
    api_key: str = Depends(verify_api_key)
):
    """
    Удаление чата
    
    - **chat_id**: ID чата
    """
    success = await service.delete_chat(chat_id)
    if not success:
        raise HTTPException(status_code=404, detail="Чат не найден")
    return {"success": True, "message": "Чат удален"}


@router.post("/{chat_id}/message")
async def send_message(
    chat_id: str,
    message_data: MessageCreate,
    service: ChatService = Depends(get_chat_service),
    api_key: str = Depends(verify_api_key)
):
    """
    Отправка сообщения в чат
    
    - **chat_id**: ID чата
    - **content**: Текст сообщения
    - **stream**: Использовать streaming (по умолчанию true)
    
    Возвращает:
    - При stream=true: text/event-stream с частями ответа
    - При stream=false: JSON с полным ответом
    """
    try:
        # Добавляем сообщение пользователя
        user_message = await service.add_message(chat_id, message_data)
        
        if message_data.stream:
            # Streaming режим
            async def generate():
                try:
                    async for chunk in service.generate_response(chat_id, stream=True):
                        # Отправляем в формате Server-Sent Events
                        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                    
                    # Сигнал завершения
                    yield f"data: {json.dumps({'done': True})}\n\n"
                
                except Exception as e:
                    logger.error(f"Ошибка streaming: {e}")
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
            return StreamingResponse(
                generate(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        else:
            # Обычный режим
            full_response = ""
            async for chunk in service.generate_response(chat_id, stream=False):
                full_response += chunk
            
            # Получаем обновленный чат
            chat = await service.get_chat(chat_id)
            assistant_message = chat.messages[-1]
            
            return MessageResponse(
                message=assistant_message,
                chat_id=chat_id
            )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{chat_id}/regenerate")
async def regenerate_message(
    chat_id: str,
    request: RegenerateRequest,
    service: ChatService = Depends(get_chat_service),
    api_key: str = Depends(verify_api_key)
):
    """
    Регенерация ответа ассистента
    
    - **chat_id**: ID чата
    - **message_id**: ID сообщения для регенерации
    """
    try:
        async def generate():
            try:
                async for chunk in service.regenerate_response(chat_id, request.message_id):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                
                yield f"data: {json.dumps({'done': True})}\n\n"
            
            except Exception as e:
                logger.error(f"Ошибка регенерации: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка регенерации: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{chat_id}/message")
async def delete_message(
    chat_id: str,
    request: DeleteMessageRequest,
    service: ChatService = Depends(get_chat_service),
    api_key: str = Depends(verify_api_key)
):
    """
    Удаление сообщения
    
    - **chat_id**: ID чата
    - **message_id**: ID сообщения
    """
    success = await service.delete_message(chat_id, request.message_id)
    if not success:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")
    return {"success": True, "message": "Сообщение удалено"}


@router.put("/{chat_id}/title")
async def update_chat_title(
    chat_id: str,
    title: str,
    service: ChatService = Depends(get_chat_service),
    api_key: str = Depends(verify_api_key)
):
    """
    Обновление названия чата
    
    - **chat_id**: ID чата
    - **title**: Новое название
    """
    success = await service.update_chat_title(chat_id, title)
    if not success:
        raise HTTPException(status_code=404, detail="Чат не найден")
    return {"success": True, "message": "Название обновлено"}
