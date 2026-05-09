"""
API Router для управления настройками
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from datetime import datetime
import json
from pathlib import Path
from loguru import logger

from models.settings_models import (
    FullSettings, SettingsUpdateRequest, SettingsUpdateResponse,
    ConnectionTestRequest, ConnectionTestResponse
)
from services.settings_service import get_settings_service

# Глобальная ссылка на агента (будет установлена из main.py)
agent = None

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])


@router.get("", response_model=FullSettings)
async def get_settings():
    """
    Получить все настройки (токены замаскированы)
    """
    try:
        service = get_settings_service()
        settings = await service.get_settings(mask_tokens=True)
        return settings
    except Exception as e:
        logger.error(f"Ошибка получения настроек: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("", response_model=SettingsUpdateResponse)
async def update_settings(request: SettingsUpdateRequest):
    """
    Обновить настройки
    
    Возвращает информацию о том, требуется ли перезапуск агента
    """
    try:
        service = get_settings_service()
        success, message, restart_required = await service.update_settings(request)
        
        if success:
            return SettingsUpdateResponse(
                success=True,
                message=message,
                restart_required=restart_required
            )
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка обновления настроек: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-connection", response_model=ConnectionTestResponse)
async def test_connection(request: ConnectionTestRequest):
    """
    Тестирование подключения
    
    Поддерживаемые типы:
    - creator: Creator Model (vLLM)
    - logic: Logic Model (vLLM)
    - tavily: Tavily API
    - github: GitHub API
    """
    try:
        service = get_settings_service()
        result = await service.test_connection(request)
        return result
    except Exception as e:
        logger.error(f"Ошибка тестирования подключения: {e}")
        return ConnectionTestResponse(
            success=False,
            message=f"Ошибка: {str(e)}",
            details={"error": str(e)}
        )


@router.get("/export")
async def export_settings():
    """
    Экспорт настроек в JSON файл (для backup)
    
    Токены НЕ маскируются для возможности восстановления
    """
    try:
        service = get_settings_service()
        settings_dict = service.export_settings()
        
        # Создаем временный файл
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"edis_settings_backup_{timestamp}.json"
        temp_path = Path(f"web/backend/data/{filename}")
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(settings_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Настройки экспортированы: {filename}")
        
        return FileResponse(
            path=str(temp_path),
            filename=filename,
            media_type="application/json"
        )
        
    except Exception as e:
        logger.error(f"Ошибка экспорта настроек: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import")
async def import_settings(file: UploadFile = File(...)):
    """
    Импорт настроек из JSON файла
    
    Файл должен быть в формате экспорта
    """
    try:
        # Читаем файл
        content = await file.read()
        settings_dict = json.loads(content.decode('utf-8'))
        
        service = get_settings_service()
        success, message = await service.import_settings(settings_dict)
        
        if success:
            logger.info(f"Настройки импортированы из {file.filename}")
            return JSONResponse(
                content={
                    "success": True,
                    "message": message
                }
            )
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Неверный формат JSON")
    except Exception as e:
        logger.error(f"Ошибка импорта настроек: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reload")
async def reload_agent_settings():
    """
    Перезагрузить настройки агента из базы данных
    
    Некоторые настройки (например, модели) требуют полного перезапуска агента.
    В этом случае возвращается restart_required=True
    """
    global agent
    
    if not agent:
        raise HTTPException(status_code=503, detail="Агент не инициализирован")
    
    try:
        result = await agent.reload_settings_from_db()
        
        if result["success"]:
            logger.info("✓ Настройки агента перезагружены из БД")
            return JSONResponse(
                content={
                    "success": True,
                    "message": result["message"],
                    "restart_required": result["restart_required"]
                }
            )
        else:
            logger.warning(f"⚠️ {result['message']}")
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "message": result["message"],
                    "restart_required": result["restart_required"]
                }
            )
            
    except Exception as e:
        logger.error(f"Ошибка перезагрузки настроек агента: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Проверка работоспособности settings API"""
    try:
        service = get_settings_service()
        # Пробуем загрузить настройки
        await service.get_settings(mask_tokens=True)
        
        return {
            "status": "healthy",
            "service": "settings",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")
