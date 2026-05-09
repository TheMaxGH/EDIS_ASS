"""
API роутер для управления файлами в песочнице
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Header
from fastapi.responses import FileResponse, StreamingResponse
from typing import List, Optional
from pydantic import BaseModel
from pathlib import Path
import os
import shutil
from loguru import logger
import mimetypes


router = APIRouter(prefix="/api/v1/sandbox", tags=["sandbox"])


class FileInfo(BaseModel):
    """Информация о файле"""
    name: str
    path: str
    size: int
    is_directory: bool
    modified: str
    mime_type: Optional[str] = None


class DirectoryListing(BaseModel):
    """Список файлов в директории"""
    current_path: str
    parent_path: Optional[str]
    files: List[FileInfo]


class CreateDirectoryRequest(BaseModel):
    """Запрос на создание директории"""
    path: str


class DeleteRequest(BaseModel):
    """Запрос на удаление"""
    path: str


class RenameRequest(BaseModel):
    """Запрос на переименование"""
    old_path: str
    new_path: str


# Базовая директория песочницы
SANDBOX_BASE = Path("sandbox_workspace")
SANDBOX_BASE.mkdir(exist_ok=True)


def get_safe_path(relative_path: str) -> Path:
    """Получить безопасный путь внутри песочницы"""
    # Нормализуем путь и проверяем, что он внутри песочницы
    safe_path = (SANDBOX_BASE / relative_path).resolve()
    
    if not str(safe_path).startswith(str(SANDBOX_BASE.resolve())):
        raise HTTPException(status_code=400, detail="Invalid path: outside sandbox")
    
    return safe_path


async def verify_api_key(x_api_key: str = Header(...)):
    """Проверка API ключа"""
    expected_key = os.getenv("EDIS_API_KEY", "your-secret-key-here")
    if x_api_key != expected_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key


@router.get("/files", response_model=DirectoryListing)
async def list_files(
    path: str = "",
    api_key: str = Depends(verify_api_key)
):
    """
    Получить список файлов в директории
    
    - **path**: Относительный путь к директории (пустая строка = корень)
    """
    try:
        target_path = get_safe_path(path)
        
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="Directory not found")
        
        if not target_path.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")
        
        files = []
        for item in target_path.iterdir():
            stat = item.stat()
            mime_type = None
            
            if item.is_file():
                mime_type, _ = mimetypes.guess_type(str(item))
            
            files.append(FileInfo(
                name=item.name,
                path=str(item.relative_to(SANDBOX_BASE)),
                size=stat.st_size,
                is_directory=item.is_dir(),
                modified=str(stat.st_mtime),
                mime_type=mime_type
            ))
        
        # Сортировка: сначала директории, потом файлы
        files.sort(key=lambda x: (not x.is_directory, x.name.lower()))
        
        # Родительская директория
        parent_path = None
        if path:
            parent = Path(path).parent
            parent_path = str(parent) if str(parent) != "." else ""
        
        return DirectoryListing(
            current_path=path,
            parent_path=parent_path,
            files=files
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    path: str = "",
    api_key: str = Depends(verify_api_key)
):
    """
    Загрузить файл в песочницу
    
    - **file**: Файл для загрузки
    - **path**: Относительный путь к директории назначения
    """
    try:
        target_dir = get_safe_path(path)
        
        if not target_dir.exists():
            target_dir.mkdir(parents=True)
        
        if not target_dir.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")
        
        file_path = target_dir / file.filename
        
        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File uploaded: {file_path}")
        
        return {
            "success": True,
            "filename": file.filename,
            "path": str(file_path.relative_to(SANDBOX_BASE)),
            "size": file_path.stat().st_size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{file_path:path}")
async def download_file(
    file_path: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Скачать файл из песочницы
    
    - **file_path**: Относительный путь к файлу
    """
    try:
        target_file = get_safe_path(file_path)
        
        if not target_file.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if not target_file.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")
        
        return FileResponse(
            path=str(target_file),
            filename=target_file.name,
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/directory")
async def create_directory(
    request: CreateDirectoryRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Создать новую директорию
    
    - **path**: Относительный путь к новой директории
    """
    try:
        target_path = get_safe_path(request.path)
        
        if target_path.exists():
            raise HTTPException(status_code=400, detail="Directory already exists")
        
        target_path.mkdir(parents=True)
        logger.info(f"Directory created: {target_path}")
        
        return {
            "success": True,
            "path": str(target_path.relative_to(SANDBOX_BASE))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating directory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete")
async def delete_item(
    request: DeleteRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Удалить файл или директорию
    
    - **path**: Относительный путь к файлу/директории
    """
    try:
        target_path = get_safe_path(request.path)
        
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        if target_path.is_dir():
            shutil.rmtree(target_path)
        else:
            target_path.unlink()
        
        logger.info(f"Deleted: {target_path}")
        
        return {
            "success": True,
            "path": request.path
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/rename")
async def rename_item(
    request: RenameRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Переименовать файл или директорию
    
    - **old_path**: Текущий путь
    - **new_path**: Новый путь
    """
    try:
        old_path = get_safe_path(request.old_path)
        new_path = get_safe_path(request.new_path)
        
        if not old_path.exists():
            raise HTTPException(status_code=404, detail="Source path not found")
        
        if new_path.exists():
            raise HTTPException(status_code=400, detail="Destination already exists")
        
        old_path.rename(new_path)
        logger.info(f"Renamed: {old_path} -> {new_path}")
        
        return {
            "success": True,
            "old_path": request.old_path,
            "new_path": str(new_path.relative_to(SANDBOX_BASE))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error renaming: {e}")
        raise HTTPException(status_code=500, detail=str(e))
