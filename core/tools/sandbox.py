"""
Code Sandbox - изолированное выполнение кода в Docker
Логик может писать, запускать и отлаживать код безопасно
"""
import asyncio
import docker
import tempfile
import os
from typing import Dict, Any, Optional, Literal
from loguru import logger
from pathlib import Path


class CodeSandbox:
    """
    Песочница для безопасного выполнения кода
    Поддерживает Python и Node.js в изолированных Docker контейнерах
    """
    
    def __init__(
        self,
        timeout: int = 30,
        memory_limit: str = "512m",
        cpu_quota: int = 50000  # 50% одного ядра
    ):
        """
        Args:
            timeout: Таймаут выполнения в секундах
            memory_limit: Лимит памяти (например, "512m", "1g")
            cpu_quota: CPU квота (100000 = 1 ядро)
        """
        self.timeout = timeout
        self.memory_limit = memory_limit
        self.cpu_quota = cpu_quota
        
        try:
            self.docker_client = docker.from_env()
            logger.info("CodeSandbox инициализирован с Docker")
        except Exception as e:
            logger.warning(f"Docker недоступен: {e}. Sandbox будет работать в ограниченном режиме")
            self.docker_client = None
    
    async def execute_python(
        self,
        code: str,
        requirements: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """
        Выполнение Python кода в изолированном контейнере
        
        Args:
            code: Python код для выполнения
            requirements: Список pip пакетов для установки
        
        Returns:
            Dict с результатом: {
                "success": bool,
                "output": str,
                "error": Optional[str],
                "execution_time": float
            }
        """
        logger.info("Запуск Python кода в sandbox...")
        
        if not self.docker_client:
            return await self._execute_local_python(code)
        
        # Создаем временную директорию
        with tempfile.TemporaryDirectory() as tmpdir:
            # Сохраняем код
            code_path = Path(tmpdir) / "script.py"
            code_path.write_text(code, encoding="utf-8")
            
            # Создаем requirements.txt если нужно
            if requirements:
                req_path = Path(tmpdir) / "requirements.txt"
                req_path.write_text("\n".join(requirements), encoding="utf-8")
            
            # Dockerfile для изолированного окружения
            dockerfile_content = """
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi
CMD ["python", "script.py"]
"""
            dockerfile_path = Path(tmpdir) / "Dockerfile"
            dockerfile_path.write_text(dockerfile_content)
            
            try:
                # Собираем образ
                logger.debug("Сборка Docker образа...")
                image, build_logs = self.docker_client.images.build(
                    path=tmpdir,
                    tag="qwen_sandbox_python:latest",
                    rm=True,
                    forcerm=True
                )
                
                # Запускаем контейнер
                logger.debug("Запуск контейнера...")
                container = self.docker_client.containers.run(
                    image.id,
                    detach=True,
                    mem_limit=self.memory_limit,
                    cpu_quota=self.cpu_quota,
                    network_disabled=True,  # Изоляция сети
                    remove=True
                )
                
                # Ждем завершения с таймаутом
                try:
                    result = container.wait(timeout=self.timeout)
                    logs = container.logs().decode("utf-8")
                    
                    success = result["StatusCode"] == 0
                    
                    return {
                        "success": success,
                        "output": logs if success else "",
                        "error": logs if not success else None,
                        "execution_time": None  # Docker не предоставляет точное время
                    }
                    
                except asyncio.TimeoutError:
                    container.kill()
                    return {
                        "success": False,
                        "output": "",
                        "error": f"Превышен таймаут выполнения ({self.timeout}s)",
                        "execution_time": self.timeout
                    }
                    
            except docker.errors.BuildError as e:
                logger.error(f"Ошибка сборки Docker образа: {e}")
                return {
                    "success": False,
                    "output": "",
                    "error": f"Ошибка сборки: {str(e)}",
                    "execution_time": None
                }
            except Exception as e:
                logger.error(f"Ошибка выполнения в Docker: {e}")
                return {
                    "success": False,
                    "output": "",
                    "error": str(e),
                    "execution_time": None
                }
    
    async def execute_nodejs(
        self,
        code: str,
        packages: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """
        Выполнение Node.js кода в изолированном контейнере
        
        Args:
            code: JavaScript/TypeScript код
            packages: Список npm пакетов для установки
        
        Returns:
            Dict с результатом выполнения
        """
        logger.info("Запуск Node.js кода в sandbox...")
        
        if not self.docker_client:
            return {
                "success": False,
                "output": "",
                "error": "Docker недоступен, Node.js sandbox не поддерживается в локальном режиме",
                "execution_time": None
            }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Сохраняем код
            code_path = Path(tmpdir) / "script.js"
            code_path.write_text(code, encoding="utf-8")
            
            # package.json если нужны пакеты
            if packages:
                package_json = {
                    "name": "sandbox",
                    "version": "1.0.0",
                    "dependencies": {pkg: "latest" for pkg in packages}
                }
                import json
                pkg_path = Path(tmpdir) / "package.json"
                pkg_path.write_text(json.dumps(package_json, indent=2))
            
            # Dockerfile
            dockerfile_content = """
FROM node:18-slim
WORKDIR /app
COPY . /app
RUN if [ -f package.json ]; then npm install --production; fi
CMD ["node", "script.js"]
"""
            dockerfile_path = Path(tmpdir) / "Dockerfile"
            dockerfile_path.write_text(dockerfile_content)
            
            try:
                # Собираем и запускаем
                image, _ = self.docker_client.images.build(
                    path=tmpdir,
                    tag="qwen_sandbox_node:latest",
                    rm=True
                )
                
                container = self.docker_client.containers.run(
                    image.id,
                    detach=True,
                    mem_limit=self.memory_limit,
                    cpu_quota=self.cpu_quota,
                    network_disabled=True,
                    remove=True
                )
                
                try:
                    result = container.wait(timeout=self.timeout)
                    logs = container.logs().decode("utf-8")
                    
                    return {
                        "success": result["StatusCode"] == 0,
                        "output": logs,
                        "error": None if result["StatusCode"] == 0 else logs,
                        "execution_time": None
                    }
                except asyncio.TimeoutError:
                    container.kill()
                    return {
                        "success": False,
                        "output": "",
                        "error": f"Таймаут ({self.timeout}s)",
                        "execution_time": self.timeout
                    }
                    
            except Exception as e:
                logger.error(f"Ошибка Node.js sandbox: {e}")
                return {
                    "success": False,
                    "output": "",
                    "error": str(e),
                    "execution_time": None
                }
    
    async def _execute_local_python(self, code: str) -> Dict[str, Any]:
        """
        Fallback: локальное выполнение Python (небезопасно!)
        Используется только если Docker недоступен
        """
        logger.warning("Выполнение Python кода локально (без изоляции)!")
        
        import sys
        from io import StringIO
        import time
        
        # Перехватываем stdout/stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        
        start_time = time.time()
        success = False
        error = None
        
        try:
            # Ограниченное окружение
            exec_globals = {
                "__builtins__": __builtins__,
                "print": print,
            }
            exec(code, exec_globals)
            success = True
        except Exception as e:
            error = str(e)
            logger.error(f"Ошибка выполнения: {e}")
        finally:
            output = sys.stdout.getvalue()
            error_output = sys.stderr.getvalue()
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            execution_time = time.time() - start_time
        
        return {
            "success": success,
            "output": output,
            "error": error or error_output or None,
            "execution_time": execution_time
        }
    
    async def execute(
        self,
        code: str,
        language: Literal["python", "nodejs"],
        dependencies: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """
        Универсальный метод выполнения кода
        
        Args:
            code: Код для выполнения
            language: Язык программирования
            dependencies: Зависимости (pip пакеты или npm пакеты)
        
        Returns:
            Результат выполнения
        """
        if language == "python":
            return await self.execute_python(code, dependencies)
        elif language == "nodejs":
            return await self.execute_nodejs(code, dependencies)
        else:
            return {
                "success": False,
                "output": "",
                "error": f"Неподдерживаемый язык: {language}",
                "execution_time": None
            }
    
    def cleanup(self):
        """Очистка ресурсов"""
        if self.docker_client:
            try:
                # Удаляем старые образы sandbox
                for image in self.docker_client.images.list():
                    if "qwen_sandbox" in str(image.tags):
                        self.docker_client.images.remove(image.id, force=True)
                logger.info("Sandbox образы очищены")
            except Exception as e:
                logger.warning(f"Ошибка очистки: {e}")
