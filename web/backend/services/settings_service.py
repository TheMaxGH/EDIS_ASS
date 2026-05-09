"""
Сервис для управления настройками и валидации подключений
"""
import httpx
import asyncio
from typing import Dict, Any, Optional, Tuple
from loguru import logger

from database.settings_db import get_settings_db
from models.settings_models import (
    FullSettings, SettingsUpdateRequest, 
    ConnectionTestRequest, ConnectionTestResponse
)


class SettingsService:
    """Сервис управления настройками"""
    
    def __init__(self):
        self.db = get_settings_db()
        logger.info("SettingsService инициализирован")
    
    async def get_settings(self, mask_tokens: bool = True) -> FullSettings:
        """
        Получение настроек
        
        Args:
            mask_tokens: Маскировать ли токены для отображения
        """
        try:
            settings = self.db.load_settings(mask_tokens=mask_tokens)
            logger.info("Настройки загружены из БД")
            return settings
        except Exception as e:
            logger.error(f"Ошибка загрузки настроек: {e}")
            # Возвращаем настройки по умолчанию
            return FullSettings()
    
    async def update_settings(
        self, 
        update_request: SettingsUpdateRequest
    ) -> Tuple[bool, str, bool]:
        """
        Обновление настроек
        
        Returns:
            (success, message, restart_required)
        """
        try:
            # Загружаем текущие настройки
            current_settings = self.db.load_settings(mask_tokens=False)
            
            restart_required = False
            
            # Обновляем только переданные секции
            if update_request.models:
                # Проверяем изменение критичных параметров
                if (current_settings.models.creator.base_url != update_request.models.creator.base_url or
                    current_settings.models.logic.base_url != update_request.models.logic.base_url):
                    restart_required = True
                
                current_settings.models = update_request.models
            
            if update_request.autonomy:
                current_settings.autonomy = update_request.autonomy
            
            if update_request.tools:
                current_settings.tools = update_request.tools
            
            if update_request.system:
                # Изменение Qdrant требует перезапуска
                if (current_settings.system.qdrant_host != update_request.system.qdrant_host or
                    current_settings.system.qdrant_port != update_request.system.qdrant_port):
                    restart_required = True
                
                current_settings.system = update_request.system
            
            # Сохраняем в БД
            success = self.db.save_settings(current_settings)
            
            if success:
                message = "Настройки успешно обновлены"
                if restart_required:
                    message += ". Требуется перезапуск агента для применения изменений"
                logger.info(message)
                return True, message, restart_required
            else:
                return False, "Ошибка сохранения настроек", False
                
        except Exception as e:
            logger.error(f"Ошибка обновления настроек: {e}")
            return False, f"Ошибка: {str(e)}", False
    
    async def validate_model_connection(
        self, 
        base_url: str, 
        api_key: str, 
        model_name: str
    ) -> ConnectionTestResponse:
        """Валидация подключения к vLLM модели"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Проверяем /v1/models endpoint
                headers = {"Authorization": f"Bearer {api_key}"}
                
                response = await client.get(
                    f"{base_url}/models",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    models = data.get("data", [])
                    
                    # Проверяем наличие нужной модели
                    model_found = any(m.get("id") == model_name for m in models)
                    
                    if model_found:
                        return ConnectionTestResponse(
                            success=True,
                            message="Подключение успешно",
                            details={
                                "model": model_name,
                                "available_models": len(models)
                            }
                        )
                    else:
                        return ConnectionTestResponse(
                            success=False,
                            message=f"Модель {model_name} не найдена",
                            details={
                                "available_models": [m.get("id") for m in models]
                            }
                        )
                else:
                    return ConnectionTestResponse(
                        success=False,
                        message=f"Ошибка подключения: HTTP {response.status_code}",
                        details={"status_code": response.status_code}
                    )
                    
        except httpx.TimeoutException:
            return ConnectionTestResponse(
                success=False,
                message="Timeout: сервер не отвечает",
                details={"error": "timeout"}
            )
        except Exception as e:
            return ConnectionTestResponse(
                success=False,
                message=f"Ошибка подключения: {str(e)}",
                details={"error": str(e)}
            )
    
    async def validate_tavily_key(self, api_key: str) -> ConnectionTestResponse:
        """Валидация Tavily API ключа"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": api_key,
                        "query": "test",
                        "max_results": 1
                    }
                )
                
                if response.status_code == 200:
                    return ConnectionTestResponse(
                        success=True,
                        message="Tavily API ключ валиден",
                        details={"status": "active"}
                    )
                elif response.status_code == 401:
                    return ConnectionTestResponse(
                        success=False,
                        message="Неверный API ключ",
                        details={"status_code": 401}
                    )
                else:
                    return ConnectionTestResponse(
                        success=False,
                        message=f"Ошибка: HTTP {response.status_code}",
                        details={"status_code": response.status_code}
                    )
                    
        except Exception as e:
            return ConnectionTestResponse(
                success=False,
                message=f"Ошибка проверки: {str(e)}",
                details={"error": str(e)}
            )
    
    async def validate_github_token(self, token: str) -> ConnectionTestResponse:
        """Валидация GitHub токена"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                response = await client.get(
                    "https://api.github.com/user",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return ConnectionTestResponse(
                        success=True,
                        message="GitHub токен валиден",
                        details={
                            "username": data.get("login"),
                            "name": data.get("name")
                        }
                    )
                elif response.status_code == 401:
                    return ConnectionTestResponse(
                        success=False,
                        message="Неверный токен",
                        details={"status_code": 401}
                    )
                else:
                    return ConnectionTestResponse(
                        success=False,
                        message=f"Ошибка: HTTP {response.status_code}",
                        details={"status_code": response.status_code}
                    )
                    
        except Exception as e:
            return ConnectionTestResponse(
                success=False,
                message=f"Ошибка проверки: {str(e)}",
                details={"error": str(e)}
            )
    
    async def test_connection(
        self, 
        request: ConnectionTestRequest
    ) -> ConnectionTestResponse:
        """Универсальный метод тестирования подключений"""
        
        if request.type == "creator":
            return await self.validate_model_connection(
                base_url=request.config.get("base_url"),
                api_key=request.config.get("api_key"),
                model_name=request.config.get("model_name")
            )
        
        elif request.type == "logic":
            return await self.validate_model_connection(
                base_url=request.config.get("base_url"),
                api_key=request.config.get("api_key"),
                model_name=request.config.get("model_name")
            )
        
        elif request.type == "tavily":
            return await self.validate_tavily_key(
                api_key=request.config.get("api_key")
            )
        
        elif request.type == "github":
            return await self.validate_github_token(
                token=request.config.get("token")
            )
        
        else:
            return ConnectionTestResponse(
                success=False,
                message=f"Неизвестный тип подключения: {request.type}",
                details={}
            )
    
    def export_settings(self) -> Dict[str, Any]:
        """Экспорт настроек в словарь (для backup)"""
        settings = self.db.load_settings(mask_tokens=False)
        return settings.model_dump()
    
    async def import_settings(self, settings_dict: Dict[str, Any]) -> Tuple[bool, str]:
        """Импорт настроек из словаря"""
        try:
            settings = FullSettings(**settings_dict)
            success = self.db.save_settings(settings)
            
            if success:
                return True, "Настройки успешно импортированы"
            else:
                return False, "Ошибка сохранения настроек"
                
        except Exception as e:
            logger.error(f"Ошибка импорта настроек: {e}")
            return False, f"Ошибка: {str(e)}"


# Глобальный экземпляр
_service_instance: Optional[SettingsService] = None


def get_settings_service() -> SettingsService:
    """Получение глобального экземпляра сервиса"""
    global _service_instance
    if _service_instance is None:
        _service_instance = SettingsService()
    return _service_instance
