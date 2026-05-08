"""
Примеры использования Dual Qwen Brain
"""
import asyncio
from dual_qwen_brain import DualQwenAgent


async def example_1_simple_task():
    """Пример 1: Простая задача"""
    print("\n" + "=" * 60)
    print("ПРИМЕР 1: Простая задача")
    print("=" * 60)
    
    agent = DualQwenAgent()
    await agent.initialize()
    
    task = "Предложи инновационный подход к кэшированию в распределенных системах"
    result = await agent.process(task)
    
    print(f"\nЗадача: {task}")
    print(f"\nРезультат:\n{result}")
    
    await agent.shutdown()


async def example_2_with_autonomy():
    """Пример 2: Работа с автономным режимом"""
    print("\n" + "=" * 60)
    print("ПРИМЕР 2: Автономный режим")
    print("=" * 60)
    
    agent = DualQwenAgent()
    await agent.initialize()
    
    # Запускаем автономный мониторинг
    await agent.start_autonomy()
    print("Автономный режим запущен. Агент мониторит GitHub и Arxiv...")
    
    # Даем время на первый цикл мониторинга (для демонстрации)
    await asyncio.sleep(10)
    
    # Обрабатываем задачу
    task = "Какие новые технологии в AI появились недавно?"
    result = await agent.process(task)
    
    print(f"\nЗадача: {task}")
    print(f"\nРезультат (с учетом найденной информации):\n{result}")
    
    agent.stop_autonomy()
    await agent.shutdown()


async def example_3_iterative_refinement():
    """Пример 3: Итеративная доработка идеи"""
    print("\n" + "=" * 60)
    print("ПРИМЕР 3: Итеративная доработка")
    print("=" * 60)
    
    agent = DualQwenAgent()
    await agent.initialize()
    
    # Сложная задача, которая потребует нескольких итераций
    task = """
    Создай архитектуру для AI-агента, который может:
    1. Автономно обучаться на новых данных
    2. Взаимодействовать с внешними API
    3. Сохранять долгосрочную память
    4. Работать в режиме реального времени
    
    Учти все возможные проблемы и предложи конкретные решения.
    """
    
    result = await agent.process(task)
    
    print(f"\nСложная задача:\n{task}")
    print(f"\nФинальный результат после итераций:\n{result}")
    
    await agent.shutdown()


async def example_4_memory_search():
    """Пример 4: Работа с векторной памятью"""
    print("\n" + "=" * 60)
    print("ПРИМЕР 4: Поиск в памяти")
    print("=" * 60)
    
    agent = DualQwenAgent()
    await agent.initialize()
    
    # Добавляем знания в память
    from core.schemas import KnowledgeEntry
    from datetime import datetime
    
    entries = [
        KnowledgeEntry(
            content="Rust - системный язык программирования с гарантиями безопасности памяти",
            source="manual_entry",
            timestamp=datetime.utcnow().isoformat(),
            metadata={"type": "programming_language"}
        ),
        KnowledgeEntry(
            content="LangGraph - фреймворк для создания циклических графов агентов",
            source="manual_entry",
            timestamp=datetime.utcnow().isoformat(),
            metadata={"type": "framework"}
        )
    ]
    
    await agent.memory.add_entries(entries)
    print("Добавлено 2 записи в память")
    
    # Поиск
    results = await agent.memory.search("языки программирования", limit=3)
    
    print("\nРезультаты поиска:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Score: {result['score']:.3f}")
        print(f"   Контент: {result['content'][:100]}...")
    
    await agent.shutdown()


async def main():
    """Запуск всех примеров"""
    print("\n" + "=" * 60)
    print("DUAL QWEN BRAIN - ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ")
    print("=" * 60)
    
    # Выберите пример для запуска
    examples = {
        "1": ("Простая задача", example_1_simple_task),
        "2": ("Автономный режим", example_2_with_autonomy),
        "3": ("Итеративная доработка", example_3_iterative_refinement),
        "4": ("Работа с памятью", example_4_memory_search)
    }
    
    print("\nДоступные примеры:")
    for key, (name, _) in examples.items():
        print(f"{key}. {name}")
    
    choice = input("\nВыберите пример (1-4) или 'all' для всех: ").strip()
    
    if choice == "all":
        for name, func in examples.values():
            await func()
            await asyncio.sleep(2)
    elif choice in examples:
        _, func = examples[choice]
        await func()
    else:
        print("Неверный выбор. Запуск примера 1...")
        await example_1_simple_task()


if __name__ == "__main__":
    asyncio.run(main())
