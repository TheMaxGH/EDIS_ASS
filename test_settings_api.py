"""
Автоматизированный тест API endpoints для настроек EDIS
Проверяет все endpoints и функциональность
"""
import asyncio
import httpx
import json
from pathlib import Path
from datetime import datetime

# Настройки тестирования
BASE_URL = "http://localhost:8000"
API_KEY = "your-secret-key-here"  # Замените на ваш API ключ из .env


class SettingsAPITester:
    """Класс для тестирования Settings API"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={"X-API-Key": api_key},
            timeout=30.0
        )
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "warnings": 0
        }
    
    def print_header(self, text: str):
        """Печать заголовка"""
        print(f"\n{'='*60}")
        print(f"TEST: {text}")
        print(f"{'='*60}")
    
    def print_success(self, text: str):
        """Печать успеха"""
        print(f"[OK] {text}")
    
    def print_error(self, text: str):
        """Печать ошибки"""
        print(f"[ERROR] {text}")
    
    def print_warning(self, text: str):
        """Печать предупреждения"""
        print(f"[WARNING] {text}")
    
    def print_info(self, text: str):
        """Печать информации"""
        print(f"[INFO] {text}")
    
    async def test_health_check(self) -> bool:
        """Тест 1: Health Check"""
        self.print_header("Health Check")
        
        try:
            response = await self.client.get("/api/v1/settings/health")
            
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Health check passed: {data['status']}")
                self.print_info(f"Service: {data['service']}")
                self.print_info(f"Timestamp: {data['timestamp']}")
                self.test_results["passed"] += 1
                return True
            else:
                self.print_error(f"Health check failed: {response.status_code}")
                self.test_results["failed"] += 1
                return False
                
        except Exception as e:
            self.print_error(f"Health check error: {e}")
            self.test_results["failed"] += 1
            return False
    
    async def test_get_settings(self) -> dict:
        """Тест 2: Получение настроек"""
        self.print_header("Get Settings")
        
        try:
            response = await self.client.get("/api/v1/settings")
            
            if response.status_code == 200:
                settings = response.json()
                self.print_success("Settings retrieved successfully")
                
                # Проверяем структуру
                required_keys = ["models", "autonomy", "tools", "system"]
                for key in required_keys:
                    if key in settings:
                        self.print_success(f"Section '{key}' present")
                    else:
                        self.print_error(f"Section '{key}' missing")
                        self.test_results["failed"] += 1
                        return None
                
                # Проверяем маскировку токенов
                creator_key = settings["models"]["creator"]["api_key"]
                if "********" in creator_key or "••" in creator_key:
                    self.print_success(f"API keys are masked: {creator_key}")
                else:
                    self.print_warning("API keys might not be masked properly")
                    self.test_results["warnings"] += 1
                
                self.test_results["passed"] += 1
                return settings
                
            else:
                self.print_error(f"Failed to get settings: {response.status_code}")
                self.print_error(f"Response: {response.text}")
                self.test_results["failed"] += 1
                return None
                
        except Exception as e:
            self.print_error(f"Get settings error: {e}")
            self.test_results["failed"] += 1
            return None
    
    async def test_update_settings(self, current_settings: dict) -> bool:
        """Тест 3: Обновление настроек"""
        self.print_header("Update Settings")
        
        if not current_settings:
            self.print_error("Cannot test update without current settings")
            self.test_results["failed"] += 1
            return False
        
        try:
            # Создаем тестовое обновление (меняем log_level)
            update_request = {
                "settings": current_settings
            }
            
            # Меняем log_level для теста
            original_log_level = current_settings["system"]["log_level"]
            test_log_level = "DEBUG" if original_log_level != "DEBUG" else "INFO"
            update_request["settings"]["system"]["log_level"] = test_log_level
            
            self.print_info(f"Changing log_level: {original_log_level} -> {test_log_level}")
            
            response = await self.client.put("/api/v1/settings", json=update_request)
            
            if response.status_code == 200:
                result = response.json()
                self.print_success(f"Settings updated: {result['message']}")
                
                if result.get("restart_required"):
                    self.print_warning("Restart required for changes to take effect")
                    self.test_results["warnings"] += 1
                
                # Проверяем, что изменения применились
                updated_settings = await self.test_get_settings()
                if updated_settings and updated_settings["system"]["log_level"] == test_log_level:
                    self.print_success(f"Change verified: log_level = {test_log_level}")
                else:
                    self.print_error("Change not verified")
                    self.test_results["failed"] += 1
                    return False
                
                # Возвращаем обратно
                update_request["settings"]["system"]["log_level"] = original_log_level
                await self.client.put("/api/v1/settings", json=update_request)
                self.print_info(f"Restored log_level to: {original_log_level}")
                
                self.test_results["passed"] += 1
                return True
                
            else:
                self.print_error(f"Failed to update settings: {response.status_code}")
                self.print_error(f"Response: {response.text}")
                self.test_results["failed"] += 1
                return False
                
        except Exception as e:
            self.print_error(f"Update settings error: {e}")
            self.test_results["failed"] += 1
            return False
    
    async def test_connection_test(self) -> bool:
        """Тест 4: Тестирование подключений"""
        self.print_header("Connection Testing")
        
        try:
            # Тест Creator Model (может не работать если vLLM не запущен)
            self.print_info("Testing Creator Model connection...")
            test_request = {
                "type": "creator",
                "config": {
                    "base_url": "http://localhost:8001",
                    "api_key": "test-key",
                    "model_name": "Qwen/Qwen2.5-32B-Instruct"
                }
            }
            
            response = await self.client.post("/api/v1/settings/test-connection", json=test_request)
            
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    self.print_success(f"Creator connection test passed: {result['message']}")
                    self.test_results["passed"] += 1
                else:
                    self.print_warning(f"Creator connection test failed (expected if vLLM not running): {result['message']}")
                    self.test_results["warnings"] += 1
                return True
            else:
                self.print_error(f"Connection test endpoint error: {response.status_code}")
                self.test_results["failed"] += 1
                return False
                
        except Exception as e:
            self.print_error(f"Connection test error: {e}")
            self.test_results["failed"] += 1
            return False
    
    async def test_export_settings(self) -> str:
        """Тест 5: Экспорт настроек"""
        self.print_header("Export Settings")
        
        try:
            response = await self.client.get("/api/v1/settings/export")
            
            if response.status_code == 200:
                # Сохраняем файл
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"test_export_{timestamp}.json"
                
                with open(filename, "wb") as f:
                    f.write(response.content)
                
                self.print_success(f"Settings exported to: {filename}")
                
                # Проверяем содержимое
                with open(filename, "r", encoding="utf-8") as f:
                    exported_data = json.load(f)
                
                if "models" in exported_data and "autonomy" in exported_data:
                    self.print_success("Export file structure is valid")
                    self.test_results["passed"] += 1
                    return filename
                else:
                    self.print_error("Export file structure is invalid")
                    self.test_results["failed"] += 1
                    return None
                    
            else:
                self.print_error(f"Failed to export settings: {response.status_code}")
                self.test_results["failed"] += 1
                return None
                
        except Exception as e:
            self.print_error(f"Export settings error: {e}")
            self.test_results["failed"] += 1
            return None
    
    async def test_import_settings(self, export_file: str) -> bool:
        """Тест 6: Импорт настроек"""
        self.print_header("Import Settings")
        
        if not export_file or not Path(export_file).exists():
            self.print_error("Cannot test import without export file")
            self.test_results["failed"] += 1
            return False
        
        try:
            with open(export_file, "rb") as f:
                files = {"file": (export_file, f, "application/json")}
                response = await self.client.post("/api/v1/settings/import", files=files)
            
            if response.status_code == 200:
                result = response.json()
                self.print_success(f"Settings imported: {result['message']}")
                self.test_results["passed"] += 1
                return True
            else:
                self.print_error(f"Failed to import settings: {response.status_code}")
                self.print_error(f"Response: {response.text}")
                self.test_results["failed"] += 1
                return False
                
        except Exception as e:
            self.print_error(f"Import settings error: {e}")
            self.test_results["failed"] += 1
            return False
    
    async def test_reload_agent_settings(self) -> bool:
        """Тест 7: Перезагрузка настроек агента"""
        self.print_header("Reload Agent Settings")
        
        try:
            response = await self.client.post("/api/v1/settings/reload")
            
            if response.status_code == 200:
                result = response.json()
                
                if result["success"]:
                    self.print_success(f"Agent settings reloaded: {result['message']}")
                    
                    if result.get("restart_required"):
                        self.print_warning("Full agent restart required for some changes")
                        self.test_results["warnings"] += 1
                    
                    self.test_results["passed"] += 1
                    return True
                else:
                    self.print_warning(f"Reload returned success=False: {result['message']}")
                    self.test_results["warnings"] += 1
                    return True
                    
            elif response.status_code == 503:
                self.print_warning("Agent not initialized (expected if backend just started)")
                self.test_results["warnings"] += 1
                return True
            else:
                self.print_error(f"Failed to reload agent settings: {response.status_code}")
                self.test_results["failed"] += 1
                return False
                
        except Exception as e:
            self.print_error(f"Reload agent settings error: {e}")
            self.test_results["failed"] += 1
            return False
    
    async def run_all_tests(self):
        """Запуск всех тестов"""
        print(f"\n{'='*60}")
        print(f"EDIS Settings API Test Suite")
        print(f"Base URL: {self.base_url}")
        print(f"{'='*60}\n")
        
        # Тест 1: Health Check
        health_ok = await self.test_health_check()
        if not health_ok:
            self.print_error("\nHealth check failed - stopping tests")
            return
        
        # Тест 2: Get Settings
        current_settings = await self.test_get_settings()
        
        # Тест 3: Update Settings
        if current_settings:
            await self.test_update_settings(current_settings)
        
        # Тест 4: Connection Testing
        await self.test_connection_test()
        
        # Тест 5: Export Settings
        export_file = await self.test_export_settings()
        
        # Тест 6: Import Settings
        if export_file:
            await self.test_import_settings(export_file)
            # Удаляем тестовый файл
            try:
                Path(export_file).unlink()
                self.print_info(f"Cleaned up test file: {export_file}")
            except:
                pass
        
        # Тест 7: Reload Agent Settings
        await self.test_reload_agent_settings()
        
        # Итоговый отчет
        self.print_summary()
    
    def print_summary(self):
        """Печать итогового отчета"""
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        
        total = self.test_results["passed"] + self.test_results["failed"]
        
        print(f"\n[OK] Passed:  {self.test_results['passed']}/{total}")
        print(f"[ERROR] Failed:  {self.test_results['failed']}/{total}")
        print(f"[WARNING] Warnings: {self.test_results['warnings']}")
        
        if self.test_results["failed"] == 0:
            print(f"\n*** ALL TESTS PASSED! ***")
        else:
            print(f"\n*** SOME TESTS FAILED ***")
        
        print(f"\n{'='*60}\n")
    
    async def close(self):
        """Закрытие клиента"""
        await self.client.aclose()


async def main():
    """Главная функция"""
    print(f"\nStarting EDIS Settings API Tests...\n")
    
    # Проверяем, что backend запущен
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/")
            if response.status_code != 200:
                print(f"[ERROR] Backend is not responding properly at {BASE_URL}")
                print("[INFO] Please start the backend first:")
                print("[INFO]   cd web/backend")
                print("[INFO]   python main.py")
                return
    except Exception as e:
        print(f"[ERROR] Cannot connect to backend at {BASE_URL}")
        print(f"[ERROR] Error: {e}")
        print("\n[INFO] Please start the backend first:")
        print("[INFO]   cd web/backend")
        print("[INFO]   python main.py")
        print("\n[INFO] Or if you want to test without running backend,")
        print("[INFO] the test script is ready and will work once backend is started.")
        return
    
    # Запускаем тесты
    tester = SettingsAPITester(BASE_URL, API_KEY)
    
    try:
        await tester.run_all_tests()
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
