"""
Система записок и лора
"""
from enum import Enum
import random
from typing import List, Optional


class NoteType(Enum):
    """Типы записок"""
    DIARY = "diary"  # Дневник искателя
    WARNING = "warning"  # Предупреждение
    MAP = "map"  # Карта (показывает часть этажа)
    RECIPE = "recipe"  # Рецепт для крафта
    SPELL = "spell"  # Заклинание
    LORE = "lore"  # История мира


class Note:
    """Записка"""
    
    def __init__(
        self,
        x: int,
        y: int,
        note_type: NoteType,
        title: str,
        content: str,
        floor: int
    ):
        """
        Инициализация записки
        
        Args:
            x: Позиция X
            y: Позиция Y
            note_type: Тип записки
            title: Заголовок
            content: Содержание
            floor: Этаж, на котором найдена
        """
        self.x = x
        self.y = y
        self.note_type = note_type
        self.title = title
        self.content = content
        self.floor = floor
        self.read = False


class LoreGenerator:
    """Генератор лора и записок"""
    
    # Шаблоны дневников
    DIARY_TEMPLATES = [
        {
            "title": "Дневник неизвестного искателя",
            "content": "День {day}. Я спустился на {floor} этаж. Здесь темнее и опаснее. Враги сильнее. Надеюсь, руна устойчивости поможет мне вернуться..."
        },
        {
            "title": "Записи мага",
            "content": "Подземелье живое. Оно меняется каждый раз, когда я возвращаюсь. Только стабилизированные этажи остаются неизменными. Это ключ к выживанию."
        },
        {
            "title": "Последние слова воина",
            "content": "Я был слишком самоуверен. Этаж {floor} оказался смертельной ловушкой. Если кто-то найдёт это... бегите. Спасайтесь, пока можете."
        },
        {
            "title": "Заметки алхимика",
            "content": "Я нашёл интересные травы на этаже {floor}. Возможно, из них можно сварить зелье. Нужно попробовать смешать с кристаллами..."
        },
        {
            "title": "Дневник исследователя",
            "content": "Чем глубже я спускаюсь, тем больше загадок. Кто построил это подземелье? Зачем? Ответы должны быть на дне."
        }
    ]
    
    # Предупреждения
    WARNING_TEMPLATES = [
        {
            "title": "ОПАСНО!",
            "content": "Впереди ловушки! Смотрите под ноги. Трещины на полу - признак шипов. Странные символы - взрывные руны."
        },
        {
            "title": "Предупреждение",
            "content": "На этом этаже водятся {enemy}. Они атакуют группами. Будьте осторожны!"
        },
        {
            "title": "Внимание!",
            "content": "Не пейте из фонтана! Вода отравлена. Я потерял половину здоровья..."
        },
        {
            "title": "Осторожно",
            "content": "Телепорты на этом этаже непредсказуемы. Могут перенести в комнату с врагами."
        }
    ]
    
    # Лор
    LORE_TEMPLATES = [
        {
            "title": "История подземелья",
            "content": "Говорят, это подземелье было создано древним магом. Он искал бессмертие и спустился в самые глубины земли..."
        },
        {
            "title": "Легенда о 20-м этаже",
            "content": "На дне подземелья находится зеркало истины. Оно показывает твоё настоящее 'я'. Многие сошли с ума, увидев своё отражение."
        },
        {
            "title": "О рунах устойчивости",
            "content": "Руны устойчивости - это якоря реальности. Они фиксируют этаж в пространстве и времени. Без них подземелье постоянно меняется."
        },
        {
            "title": "Проклятие подземелья",
            "content": "Каждый, кто спускается сюда, чувствует зов. Что-то тянет вниз, всё глубже и глубже. Это не случайность. Подземелье выбирает нас."
        }
    ]
    
    @staticmethod
    def generate_notes_for_floor(
        rooms: List,
        floor: int,
        special_rooms: List = None
    ) -> List[Note]:
        """
        Сгенерировать записки для этажа
        
        Args:
            rooms: Список комнат
            floor: Номер этажа
            special_rooms: Список особых комнат
            
        Returns:
            Список записок
        """
        notes = []
        
        if len(rooms) < 2:
            return notes
        
        # Количество записок: 1-3 на этаж
        note_count = random.randint(1, 3)
        
        # Больше записок в библиотеках
        if special_rooms:
            from .special_rooms import SpecialRoomType
            for sr in special_rooms:
                if sr.room_type == SpecialRoomType.LIBRARY:
                    note_count += random.randint(3, 5)
        
        available_rooms = rooms[1:]  # Пропускаем первую комнату
        
        for _ in range(note_count):
            if not available_rooms:
                break
            
            room = random.choice(available_rooms)
            
            # Позиция в комнате
            margin = 1
            if room.width <= 2 * margin or room.height <= 2 * margin:
                continue
            
            x = room.x + margin + random.randint(0, room.width - 2 * margin - 1)
            y = room.y + margin + random.randint(0, room.height - 2 * margin - 1)
            
            # Выбираем тип записки
            note_type = LoreGenerator._choose_note_type(floor)
            
            # Генерируем содержание
            note = LoreGenerator._generate_note_content(x, y, note_type, floor)
            
            if note:
                notes.append(note)
        
        return notes
    
    @staticmethod
    def _choose_note_type(floor: int) -> NoteType:
        """Выбрать тип записки"""
        # Этажи 1-5: в основном дневники и предупреждения
        if floor <= 5:
            return random.choices(
                [NoteType.DIARY, NoteType.WARNING, NoteType.LORE],
                weights=[50, 30, 20],
                k=1
            )[0]
        
        # Этажи 6-10: добавляются рецепты
        elif floor <= 10:
            return random.choices(
                [NoteType.DIARY, NoteType.WARNING, NoteType.RECIPE, NoteType.LORE],
                weights=[40, 25, 20, 15],
                k=1
            )[0]
        
        # Этажи 11-15: добавляются заклинания
        elif floor <= 15:
            return random.choices(
                [NoteType.DIARY, NoteType.WARNING, NoteType.RECIPE, NoteType.SPELL, NoteType.LORE],
                weights=[30, 20, 20, 15, 15],
                k=1
            )[0]
        
        # Этажи 16-20: больше лора и заклинаний
        else:
            return random.choices(
                [NoteType.DIARY, NoteType.RECIPE, NoteType.SPELL, NoteType.LORE, NoteType.MAP],
                weights=[20, 15, 25, 30, 10],
                k=1
            )[0]
    
    @staticmethod
    def _generate_note_content(
        x: int,
        y: int,
        note_type: NoteType,
        floor: int
    ) -> Optional[Note]:
        """Сгенерировать содержание записки"""
        
        if note_type == NoteType.DIARY:
            template = random.choice(LoreGenerator.DIARY_TEMPLATES)
            content = template["content"].format(
                day=random.randint(1, 100),
                floor=floor
            )
            return Note(x, y, note_type, template["title"], content, floor)
        
        elif note_type == NoteType.WARNING:
            template = random.choice(LoreGenerator.WARNING_TEMPLATES)
            enemies = ["скелеты", "зомби", "пауки", "призраки", "демоны"]
            content = template["content"].format(
                enemy=random.choice(enemies)
            )
            return Note(x, y, note_type, template["title"], content, floor)
        
        elif note_type == NoteType.LORE:
            template = random.choice(LoreGenerator.LORE_TEMPLATES)
            return Note(x, y, note_type, template["title"], template["content"], floor)
        
        elif note_type == NoteType.RECIPE:
            # Заглушка для рецептов (будет реализовано в системе крафта)
            return Note(
                x, y, note_type,
                "Рецепт зелья",
                "Смешать лечебную траву (x2) с водой. Получится малое зелье здоровья.",
                floor
            )
        
        elif note_type == NoteType.SPELL:
            # Заглушка для заклинаний (будет реализовано в системе магии)
            spells = ["Огненный шар", "Ледяная стена", "Молния", "Телепорт"]
            spell_name = random.choice(spells)
            return Note(
                x, y, note_type,
                f"Свиток: {spell_name}",
                f"Изучите этот свиток, чтобы получить заклинание '{spell_name}'.",
                floor
            )
        
        elif note_type == NoteType.MAP:
            return Note(
                x, y, note_type,
                "Карта этажа",
                f"Частичная карта этажа {floor}. Показывает расположение комнат.",
                floor
            )
        
        return None
