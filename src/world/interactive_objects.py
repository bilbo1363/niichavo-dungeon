"""
Интерактивные объекты на этажах
Доски с записками и кости путешественников
"""
from typing import Optional, List, Tuple
from enum import Enum
import random


class InteractiveObjectType(Enum):
    """Типы интерактивных объектов"""
    NOTICE_BOARD = "notice_board"  # Доска с записками
    SKELETON = "skeleton"  # Кости путешественника


class InteractiveObject:
    """Интерактивный объект на этаже"""
    
    def __init__(
        self,
        obj_type: InteractiveObjectType,
        x: int,
        y: int,
        note_title: str = "",
        note_text: str = "",
        loot: Optional[List[str]] = None
    ):
        """
        Инициализация интерактивного объекта
        
        Args:
            obj_type: Тип объекта
            x: Координата X
            y: Координата Y
            note_title: Заголовок записки (для досок и костей)
            note_text: Текст записки
            loot: Список предметов (для костей)
        """
        self.obj_type = obj_type
        self.x = x
        self.y = y
        self.note_title = note_title
        self.note_text = note_text
        self.loot = loot or []
        self.interacted = False  # Был ли объект использован
    
    def get_display_char(self) -> str:
        """Получить символ для отображения"""
        if self.obj_type == InteractiveObjectType.NOTICE_BOARD:
            return "B"  # Board (доска)
        elif self.obj_type == InteractiveObjectType.SKELETON:
            if self.interacted:
                return "b"  # bones (пустые кости)
            else:
                return "S"  # Skeleton (кости с лутом)
        return "?"
    
    def get_color(self) -> Tuple[int, int, int]:
        """Получить цвет объекта"""
        if self.obj_type == InteractiveObjectType.NOTICE_BOARD:
            return (139, 90, 43)  # Коричневый (дерево)
        elif self.obj_type == InteractiveObjectType.SKELETON:
            if self.interacted:
                return (150, 150, 150)  # Серый (обыскано)
            else:
                return (255, 255, 200)  # Желтоватый (есть лут)
        return (255, 255, 255)
    
    def get_interaction_hint(self) -> str:
        """Получить подсказку для взаимодействия"""
        if self.obj_type == InteractiveObjectType.NOTICE_BOARD:
            return "E - Прочитать записку"
        elif self.obj_type == InteractiveObjectType.SKELETON:
            if self.interacted:
                return "Уже обыскано"
            else:
                return "E - Обыскать останки"
        return "E - Взаимодействовать"
    
    def interact(self) -> dict:
        """
        Взаимодействие с объектом
        
        Returns:
            Словарь с результатами взаимодействия
        """
        result = {
            "type": self.obj_type.value,
            "note_title": self.note_title,
            "note_text": self.note_text,
            "loot": [],
            "already_used": self.interacted
        }
        
        # Для костей - выдаём лут только первый раз
        if self.obj_type == InteractiveObjectType.SKELETON and not self.interacted:
            result["loot"] = self.loot.copy()
            self.interacted = True
        
        return result


class InteractiveObjectManager:
    """Менеджер интерактивных объектов"""
    
    @staticmethod
    def create_notice_board(x: int, y: int, floor: int) -> InteractiveObject:
        """
        Создать доску с записками
        
        Args:
            x: Координата X
            y: Координата Y
            floor: Номер этажа
            
        Returns:
            Объект доски с записками
        """
        from src.world.niichavo_notes import NiichavoNoteManager
        note = NiichavoNoteManager.get_random_note_for_floor(floor)
        
        return InteractiveObject(
            obj_type=InteractiveObjectType.NOTICE_BOARD,
            x=x,
            y=y,
            note_title=note.title,
            note_text=note.text
        )
    
    @staticmethod
    def create_skeleton(x: int, y: int, floor: int) -> InteractiveObject:
        """
        Создать кости путешественника
        
        Args:
            x: Координата X
            y: Координата Y
            floor: Номер этажа
            
        Returns:
            Объект костей с лутом и запиской
        """
        from src.world.niichavo_notes import NiichavoNoteManager
        
        # Генерируем лут в зависимости от этажа
        loot = InteractiveObjectManager._generate_loot(floor)
        
        # Случайная записка для этого этажа
        note = NiichavoNoteManager.get_random_note_for_floor(floor)
        
        # Модифицируем записку для костей (добавляем контекст)
        skeleton_notes = [
            f"Последняя запись в дневнике:\n{note.text}",
            f"Записка в кармане:\n{note.text}",
            f"Нацарапано на стене рядом:\n{note.text}",
            f"Записка, зажатая в руке:\n{note.text}",
        ]
        
        modified_text = random.choice(skeleton_notes)
        
        return InteractiveObject(
            obj_type=InteractiveObjectType.SKELETON,
            x=x,
            y=y,
            note_title="Останки путешественника",
            note_text=modified_text,
            loot=loot
        )
    
    @staticmethod
    def _generate_loot(floor: int) -> List[str]:
        """
        Генерация лута для костей
        
        Args:
            floor: Номер этажа
            
        Returns:
            Список предметов
        """
        loot = []
        
        # Базовые предметы (всегда)
        base_items = ["Зелье здоровья (малое)", "Хлеб"]
        loot.append(random.choice(base_items))
        
        # Дополнительные предметы в зависимости от этажа
        if floor <= 5:
            # Ранние этажи - простой лут
            extra_items = [
                "Зелье здоровья (малое)",
                "Факел",
                "Верёвка",
                "Записная книжка",
            ]
        elif floor <= 10:
            # Средние этажи - средний лут
            extra_items = [
                "Зелье здоровья (среднее)",
                "Зелье выносливости",
                "Магический кристалл",
                "Древний свиток",
            ]
        elif floor <= 15:
            # Глубокие этажи - хороший лут
            extra_items = [
                "Зелье здоровья (большое)",
                "Зелье силы",
                "Редкий артефакт",
                "Магический амулет",
            ]
        else:
            # Бездна - отличный лут
            extra_items = [
                "Зелье здоровья (большое)",
                "Зелье бессмертия",
                "Легендарный артефакт",
                "Осколок реальности",
            ]
        
        # Добавляем 1-2 дополнительных предмета
        num_extra = random.randint(1, 2)
        for _ in range(num_extra):
            loot.append(random.choice(extra_items))
        
        # Шанс на золото
        if random.random() < 0.5:
            gold_amount = random.randint(10 * floor, 50 * floor)
            loot.append(f"Золото ({gold_amount})")
        
        return loot
    
    @staticmethod
    def generate_objects_for_floor(floor: int, level_width: int, level_height: int, walkable_tiles: List[Tuple[int, int]]) -> List[InteractiveObject]:
        """
        Генерация интерактивных объектов для этажа
        
        Args:
            floor: Номер этажа
            level_width: Ширина уровня
            level_height: Высота уровня
            walkable_tiles: Список проходимых тайлов
            
        Returns:
            Список интерактивных объектов
        """
        objects = []
        
        if not walkable_tiles:
            return objects
        
        # Количество досок (1-2 на этаж)
        num_boards = random.randint(1, 2)
        
        # Количество костей (зависит от этажа)
        if floor <= 5:
            num_skeletons = random.randint(1, 2)  # Гарантированно 1-2 кости
        elif floor <= 10:
            num_skeletons = random.randint(2, 3)
        elif floor <= 15:
            num_skeletons = random.randint(2, 4)
        else:
            num_skeletons = random.randint(3, 4)  # Много костей в бездне
        
        # Выбираем случайные позиции
        available_positions = walkable_tiles.copy()
        random.shuffle(available_positions)
        
        # Создаём доски
        for _ in range(min(num_boards, len(available_positions))):
            if available_positions:
                x, y = available_positions.pop()
                board = InteractiveObjectManager.create_notice_board(x, y, floor)
                objects.append(board)
        
        # Создаём кости
        for _ in range(min(num_skeletons, len(available_positions))):
            if available_positions:
                x, y = available_positions.pop()
                skeleton = InteractiveObjectManager.create_skeleton(x, y, floor)
                objects.append(skeleton)
        
        return objects


if __name__ == "__main__":
    # Тест системы
    print("🔮 Тест системы интерактивных объектов\n")
    
    # Тест доски
    board = InteractiveObjectManager.create_notice_board(10, 10, 5)
    print(f"Доска: {board.get_display_char()} на ({board.x}, {board.y})")
    print(f"Подсказка: {board.get_interaction_hint()}")
    result = board.interact()
    print(f"Записка: {result['note_title']}")
    print(f"{result['note_text']}\n")
    
    # Тест костей
    skeleton = InteractiveObjectManager.create_skeleton(15, 15, 10)
    print(f"Кости: {skeleton.get_display_char()} на ({skeleton.x}, {skeleton.y})")
    print(f"Подсказка: {skeleton.get_interaction_hint()}")
    result = skeleton.interact()
    print(f"Записка: {result['note_title']}")
    print(f"Лут: {result['loot']}")
    print(f"После обыска: {skeleton.get_display_char()}")
