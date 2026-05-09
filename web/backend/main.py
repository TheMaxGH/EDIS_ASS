"""
EDIS FastAPI Backend
Провайдер интеллекта для удаленного доступа к Dual Qwen Brain
"""
import asyncio
import os
import sys
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import uvicorn
from loguru import logger

# Добавляем корневую директорию в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dual_qwen_brain import DualQwenAgent
from core.workflow.task_architect import TaskPriority, TaskStatus
from routers import chat, sandbox, voice, settings
from services.chat_service import ChatService


# ============================================
# Pydantic Models
# ============================================

class TaskRequest(BaseModel):
    """Запрос на выполнение задачи"""
    task: str = Field(..., description="Описание задачи")
    priority: str = Field(default="high", description="Приоритет: critical, high, medium, low")
    use_task_graph: bool = Field(default=True, description="Использовать декомпозицию задачи")


class TaskResponse(BaseModel):
    """Ответ с ID задачи"""
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    """Статус выполнения задачи"""
    task_id: str
    status: str
    result: Optional[str] = None
    graph: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class SystemStats(BaseModel):
    """Статистика системы"""
    gpu_count: int
    total_memory_gb: float
    active_tasks: int
    uptime_hours: float
    gpu_utilization: Optional[float] = 0
    memory_used_gb: Optional[float] = 0


# ============================================
# WebSocket Manager
# ============================================

class ConnectionManager:
    """Менеджер WebSocket соединений для трансляции логов"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.log_queue: asyncio.Queue = asyncio.Queue()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket подключен. Всего соединений: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket отключен. Осталось соединений: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Отправка сообщения всем подключенным клиентам"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Ошибка отправки в WebSocket: {e}")
    
    async def send_log(self, level: str, message: str, source: str = "System"):
        """Добавление лога в очередь для трансляции"""
        # Маппинг старых типов в новые уровни для совместимости
        level_map = {
            "info": "info",
            "success": "success",
            "warning": "warning",
            "error": "error",
            "debug": "debug",
            "task": "info",
            "brain": "debug"
        }
        
        log_entry = {
            "level": level_map.get(level.lower(), "info"),
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "source": source
        }
        await self.log_queue.put(log_entry)
        await self.broadcast(log_entry)


# ============================================
# FastAPI App
# ============================================

app = FastAPI(
    title="EDIS Backend API",
    description="Провайдер интеллекта для Dual Qwen Brain",
    version="1.0.0"
)

# CORS для доступа с локального фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production замените на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(chat.router, tags=["Chat"])
app.include_router(sandbox.router, tags=["Sandbox"])
app.include_router(voice.router, tags=["Voice"])
app.include_router(settings.router, tags=["Settings"])

# Глобальные переменные
agent: Optional[DualQwenAgent] = None
chat_service: Optional[ChatService] = None
ws_manager = ConnectionManager()
tasks_storage: Dict[str, Dict[str, Any]] = {}
start_time = datetime.now()


# ============================================
# Security
# ============================================

async def verify_api_key(x_api_key: str = Header(...)):
    """Проверка API ключа"""
    expected_key = os.getenv("EDIS_API_KEY", "your-secret-key-here")
    if x_api_key != expected_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key


# ============================================
# Startup & Shutdown
# ============================================

@app.on_event("startup")
async def startup_event():
    """Инициализация агента при запуске"""
    global agent, chat_service
    
    logger.info("🚀 Запуск EDIS Backend...")
    
    try:
        # Проверяем наличие базы данных с настройками
        db_path = Path(__file__).parent / "database" / "settings.db"
        use_db = db_path.exists()
        
        if use_db:
            logger.info("📊 Обнаружена база данных настроек - загружаем из БД")
            agent = DualQwenAgent(config_path="config/config.yaml", use_db_settings=True)
        else:
            logger.info("📄 База данных настроек не найдена - загружаем из config.yaml")
            agent = DualQwenAgent(config_path="config/config.yaml", use_db_settings=False)
        
        await agent.initialize()
        logger.info("✓ Dual Qwen Agent инициализирован")
        
        # Инициализация ChatService
        chat_service = ChatService(agent=agent)
        # Устанавливаем сервис в роутер
        chat.chat_service = chat_service
        logger.info("✓ Chat Service инициализирован")
        
        # Передаем ссылку на агента в settings router для reload функции
        settings.agent = agent
        logger.info("✓ Settings Router связан с агентом")
        
        await ws_manager.send_log("system", "EDIS Backend запущен и готов к работе")
        
    except Exception as e:
        logger.error(f"Ошибка инициализации агента: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Корректное завершение работы"""
    global agent
    
    logger.info("Завершение работы EDIS Backend...")
    
    if agent:
        await agent.shutdown()
    
    await ws_manager.send_log("system", "EDIS Backend остановлен")


# ============================================
# API Endpoints
# ============================================

@app.get("/")
async def root():
    """Проверка работоспособности API"""
    return {
        "service": "EDIS Backend",
        "status": "online",
        "version": "1.0.0",
        "uptime_seconds": (datetime.now() - start_time).total_seconds()
    }


@app.post("/api/v1/tasks", response_model=TaskResponse)
async def create_task(
    request: TaskRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Создание новой задачи для выполнения
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Конвертируем строку приоритета в enum
    priority_map = {
        "critical": TaskPriority.CRITICAL,
        "high": TaskPriority.HIGH,
        "medium": TaskPriority.MEDIUM,
        "low": TaskPriority.LOW
    }
    priority = priority_map.get(request.priority.lower(), TaskPriority.HIGH)
    
    # Сохраняем задачу
    tasks_storage[task_id] = {
        "status": "pending",
        "request": request.dict(),
        "created_at": datetime.now().isoformat(),
        "result": None,
        "error": None
    }
    
    # Запускаем выполнение в фоне
    asyncio.create_task(execute_task(task_id, request.task, priority, request.use_task_graph))
    
    await ws_manager.send_log(
        "task_created",
        f"Новая задача создана: {request.task[:100]}...",
        {"task_id": task_id, "priority": request.priority}
    )
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
        message="Задача принята в обработку"
    )


async def execute_task(task_id: str, task: str, priority: TaskPriority, use_graph: bool):
    """Фоновое выполнение задачи"""
    try:
        tasks_storage[task_id]["status"] = "running"
        
        await ws_manager.send_log(
            "task_started",
            f"Начато выполнение задачи {task_id}",
            {"task_id": task_id}
        )
        
        # Выполняем задачу
        result_data = await agent.process(
            task=task,
            priority=priority,
            use_task_graph=use_graph
        )
        
        # result_data теперь dict с ключами "result" и "graph"
        tasks_storage[task_id]["status"] = "completed"
        tasks_storage[task_id]["result"] = result_data.get("result", "")
        tasks_storage[task_id]["graph"] = result_data.get("graph")
        tasks_storage[task_id]["completed_at"] = datetime.now().isoformat()
        
        result_preview = result_data.get("result", "")[:200] if isinstance(result_data.get("result"), str) else ""
        
        await ws_manager.send_log(
            "task_completed",
            f"Задача {task_id} выполнена успешно",
            {"task_id": task_id, "result_preview": result_preview}
        )
        
    except Exception as e:
        logger.error(f"Ошибка выполнения задачи {task_id}: {e}")
        tasks_storage[task_id]["status"] = "failed"
        tasks_storage[task_id]["error"] = str(e)
        
        await ws_manager.send_log(
            "task_failed",
            f"Ошибка выполнения задачи {task_id}: {str(e)}",
            {"task_id": task_id}
        )


@app.get("/api/v1/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Получение статуса задачи с графом (если использовался)
    """
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data = tasks_storage[task_id]
    
    return TaskStatusResponse(
        task_id=task_id,
        status=task_data["status"],
        result=task_data.get("result"),
        graph=task_data.get("graph"),
        error=task_data.get("error")
    )


@app.get("/api/v1/tasks")
async def list_tasks(
    api_key: str = Depends(verify_api_key)
):
    """
    Список всех задач
    """
    return {
        "tasks": [
            {
                "task_id": task_id,
                "status": data["status"],
                "created_at": data["created_at"],
                "task_preview": data["request"]["task"][:100]
            }
            for task_id, data in tasks_storage.items()
        ]
    }


@app.get("/api/v1/workspace/files")
async def list_workspace_files(
    api_key: str = Depends(verify_api_key)
):
    """
    Список файлов в workspace (сгенерированные документы)
    """
    output_dir = Path("outputs")
    
    if not output_dir.exists():
        return {"files": []}
    
    files = []
    for file_path in output_dir.rglob("*"):
        if file_path.is_file():
            files.append({
                "name": file_path.name,
                "path": str(file_path.relative_to(output_dir)),
                "size": file_path.stat().st_size,
                "created_at": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat()
            })
    
    return {"files": files}


@app.get("/api/v1/workspace/files/{file_path:path}")
async def download_file(
    file_path: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Скачивание файла из workspace
    """
    full_path = Path("outputs") / file_path
    
    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=full_path,
        filename=full_path.name,
        media_type="application/octet-stream"
    )


@app.get("/api/v1/system/stats", response_model=SystemStats)
async def get_system_stats(
    api_key: str = Depends(verify_api_key)
):
    """
    Статистика системы (GPU, память, задачи)
    """
    gpu_count = 0
    total_memory_gb = 0.0
    memory_used_gb = 0.0
    gpu_utilization = 0.0
    
    try:
        import pynvml
        pynvml.nvmlInit()
        
        gpu_count = pynvml.nvmlDeviceGetCount()
        total_memory = 0.0
        used_memory = 0.0
        total_utilization = 0.0
        
        for i in range(gpu_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            total_memory += mem_info.total / 1024**3  # GB
            used_memory += mem_info.used / 1024**3    # GB
            
            # Получаем утилизацию GPU
            try:
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                total_utilization += util.gpu
            except:
                pass
        
        total_memory_gb = round(total_memory, 2)
        memory_used_gb = round(used_memory, 2)
        gpu_utilization = round(total_utilization / gpu_count, 1) if gpu_count > 0 else 0.0
        
        pynvml.nvmlShutdown()
        
    except Exception as e:
        logger.warning(f"Не удалось получить статистику GPU: {e}")
    
    active_tasks = sum(1 for task in tasks_storage.values() if task["status"] == "running")
    uptime_hours = round((datetime.now() - start_time).total_seconds() / 3600, 2)
    
    return SystemStats(
        gpu_count=gpu_count,
        total_memory_gb=total_memory_gb,
        active_tasks=active_tasks,
        uptime_hours=uptime_hours,
        gpu_utilization=gpu_utilization,
        memory_used_gb=memory_used_gb
    )


# ============================================
# WebSocket Endpoint
# ============================================

@app.websocket("/api/v1/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """
    WebSocket для трансляции логов в реальном времени
    """
    await ws_manager.connect(websocket)
    
    try:
        # Отправляем приветственное сообщение
        await websocket.send_json({
            "type": "connected",
            "message": "Подключено к EDIS Backend",
            "timestamp": datetime.now().isoformat()
        })
        
        # Держим соединение открытым
        while True:
            # Ждем сообщений от клиента (ping/pong)
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
    
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket ошибка: {e}")
        ws_manager.disconnect(websocket)


@app.websocket("/api/v1/ws/tasks")
async def websocket_tasks(websocket: WebSocket):
    """
    WebSocket для трансляции обновлений задач в реальном времени
    """
    await websocket.accept()
    
    try:
        # Отправляем приветственное сообщение
        await websocket.send_json({
            "type": "connected",
            "message": "Подключено к Task Updates",
            "timestamp": datetime.now().isoformat()
        })
        
        # Держим соединение открытым
        while True:
            # Ждем сообщений от клиента (ping/pong)
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Здесь можно добавить отправку обновлений задач
            # Например, при изменении статуса задачи в task_storage
    
    except WebSocketDisconnect:
        logger.info("Task WebSocket disconnected")
    except Exception as e:
        logger.error(f"Task WebSocket ошибка: {e}")


# ============================================
# Main
# ============================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
