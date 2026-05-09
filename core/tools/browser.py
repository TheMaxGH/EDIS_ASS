"""
Omni-Browser - автоматизация браузера на базе Playwright
Агент может заходить на сайты, кликать, скроллить и извлекать данные
"""
import asyncio
from typing import Optional, Dict, Any, List
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout
from loguru import logger
from bs4 import BeautifulSoup
import re


class OmniBrowser:
    """
    Умный браузер для автоматизации веб-задач
    Поддерживает навигацию, клики, скроллинг и извлечение данных
    """
    
    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30000,  # 30 секунд
        user_agent: Optional[str] = None
    ):
        """
        Args:
            headless: Запуск в headless режиме
            timeout: Таймаут операций в миллисекундах
            user_agent: Кастомный User-Agent
        """
        self.headless = headless
        self.timeout = timeout
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
        logger.info("OmniBrowser инициализирован")
    
    async def start(self):
        """Запуск браузера"""
        if self.browser:
            logger.warning("Браузер уже запущен")
            return
        
        logger.info("Запуск Playwright браузера...")
        self.playwright = await async_playwright().start()
        
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        # Создаем контекст с кастомными настройками
        context = await self.browser.new_context(
            user_agent=self.user_agent,
            viewport={'width': 1920, 'height': 1080},
            locale='ru-RU'
        )
        
        self.page = await context.new_page()
        self.page.set_default_timeout(self.timeout)
        
        logger.info("Браузер запущен")
    
    async def navigate(self, url: str) -> Dict[str, Any]:
        """
        Переход на URL
        
        Args:
            url: URL для перехода
        
        Returns:
            Dict с информацией о странице
        """
        if not self.page:
            await self.start()
        
        logger.info(f"Переход на {url}")
        
        try:
            response = await self.page.goto(url, wait_until='domcontentloaded')
            
            # Ждем загрузки
            await self.page.wait_for_load_state('networkidle', timeout=10000)
            
            title = await self.page.title()
            final_url = self.page.url
            
            return {
                "success": True,
                "url": final_url,
                "title": title,
                "status": response.status if response else None,
                "error": None
            }
            
        except PlaywrightTimeout:
            logger.warning(f"Таймаут при загрузке {url}")
            return {
                "success": False,
                "url": url,
                "title": None,
                "status": None,
                "error": "Timeout"
            }
        except Exception as e:
            logger.error(f"Ошибка навигации: {e}")
            return {
                "success": False,
                "url": url,
                "title": None,
                "status": None,
                "error": str(e)
            }
    
    async def extract_text(self, clean: bool = True) -> str:
        """
        Извлечение текста со страницы
        
        Args:
            clean: Очистить от лишних элементов (скрипты, стили)
        
        Returns:
            Текстовое содержимое страницы
        """
        if not self.page:
            raise RuntimeError("Браузер не запущен")
        
        html = await self.page.content()
        
        if clean:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Удаляем ненужные элементы
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Извлекаем текст
            text = soup.get_text(separator='\n', strip=True)
            
            # Очищаем множественные переносы
            text = re.sub(r'\n\s*\n', '\n\n', text)
            
            return text
        else:
            return html
    
    async def click(self, selector: str) -> Dict[str, Any]:
        """
        Клик по элементу
        
        Args:
            selector: CSS селектор элемента
        
        Returns:
            Результат операции
        """
        if not self.page:
            raise RuntimeError("Браузер не запущен")
        
        try:
            await self.page.click(selector)
            logger.debug(f"Клик по {selector}")
            
            # Ждем возможной навигации
            await asyncio.sleep(0.5)
            
            return {
                "success": True,
                "selector": selector,
                "error": None
            }
        except Exception as e:
            logger.error(f"Ошибка клика: {e}")
            return {
                "success": False,
                "selector": selector,
                "error": str(e)
            }
    
    async def fill_form(self, selector: str, value: str) -> Dict[str, Any]:
        """
        Заполнение формы
        
        Args:
            selector: CSS селектор поля
            value: Значение для ввода
        
        Returns:
            Результат операции
        """
        if not self.page:
            raise RuntimeError("Браузер не запущен")
        
        try:
            await self.page.fill(selector, value)
            logger.debug(f"Заполнено поле {selector}")
            
            return {
                "success": True,
                "selector": selector,
                "error": None
            }
        except Exception as e:
            logger.error(f"Ошибка заполнения формы: {e}")
            return {
                "success": False,
                "selector": selector,
                "error": str(e)
            }
    
    async def scroll(self, direction: str = "down", amount: int = 500) -> Dict[str, Any]:
        """
        Скроллинг страницы
        
        Args:
            direction: "down", "up", "bottom", "top"
            amount: Количество пикселей (для down/up)
        
        Returns:
            Результат операции
        """
        if not self.page:
            raise RuntimeError("Браузер не запущен")
        
        try:
            if direction == "down":
                await self.page.evaluate(f"window.scrollBy(0, {amount})")
            elif direction == "up":
                await self.page.evaluate(f"window.scrollBy(0, -{amount})")
            elif direction == "bottom":
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            elif direction == "top":
                await self.page.evaluate("window.scrollTo(0, 0)")
            
            await asyncio.sleep(0.3)  # Даем время на загрузку контента
            
            return {
                "success": True,
                "direction": direction,
                "error": None
            }
        except Exception as e:
            logger.error(f"Ошибка скроллинга: {e}")
            return {
                "success": False,
                "direction": direction,
                "error": str(e)
            }
    
    async def screenshot(self, path: str, full_page: bool = False) -> Dict[str, Any]:
        """
        Скриншот страницы
        
        Args:
            path: Путь для сохранения
            full_page: Скриншот всей страницы или только видимой части
        
        Returns:
            Результат операции
        """
        if not self.page:
            raise RuntimeError("Браузер не запущен")
        
        try:
            await self.page.screenshot(path=path, full_page=full_page)
            logger.info(f"Скриншот сохранен: {path}")
            
            return {
                "success": True,
                "path": path,
                "error": None
            }
        except Exception as e:
            logger.error(f"Ошибка создания скриншота: {e}")
            return {
                "success": False,
                "path": path,
                "error": str(e)
            }
    
    async def extract_links(self) -> List[Dict[str, str]]:
        """
        Извлечение всех ссылок со страницы
        
        Returns:
            Список словарей с информацией о ссылках
        """
        if not self.page:
            raise RuntimeError("Браузер не запущен")
        
        links = await self.page.evaluate("""
            () => {
                const anchors = Array.from(document.querySelectorAll('a'));
                return anchors.map(a => ({
                    href: a.href,
                    text: a.textContent.trim()
                })).filter(link => link.href && link.href.startsWith('http'));
            }
        """)
        
        logger.debug(f"Найдено {len(links)} ссылок")
        return links
    
    async def wait_for_selector(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Ожидание появления элемента
        
        Args:
            selector: CSS селектор
            timeout: Таймаут в миллисекундах
        
        Returns:
            True если элемент появился
        """
        if not self.page:
            raise RuntimeError("Браузер не запущен")
        
        try:
            await self.page.wait_for_selector(
                selector,
                timeout=timeout or self.timeout
            )
            return True
        except PlaywrightTimeout:
            logger.warning(f"Элемент {selector} не появился")
            return False
    
    async def execute_script(self, script: str) -> Any:
        """
        Выполнение JavaScript на странице
        
        Args:
            script: JavaScript код
        
        Returns:
            Результат выполнения
        """
        if not self.page:
            raise RuntimeError("Браузер не запущен")
        
        try:
            result = await self.page.evaluate(script)
            return result
        except Exception as e:
            logger.error(f"Ошибка выполнения скрипта: {e}")
            return None
    
    async def get_cookies(self) -> List[Dict[str, Any]]:
        """Получение cookies"""
        if not self.page:
            raise RuntimeError("Браузер не запущен")
        
        context = self.page.context
        cookies = await context.cookies()
        return cookies
    
    async def close(self):
        """Закрытие браузера"""
        if self.page:
            await self.page.close()
            self.page = None
        
        if self.browser:
            await self.browser.close()
            self.browser = None
        
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
        
        logger.info("Браузер закрыт")
    
    async def __aenter__(self):
        """Контекстный менеджер"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер"""
        await self.close()
