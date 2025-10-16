"""
Система ловушек
"""
from enum import Enum
import random
from typing import List


class TrapType(Enum):
    """Типы ловушек"""
    SPIKES = "spikes"  # Шипы (урон при наступании)
    ARROW = "arrow"  # Стрелы из стен
    FIRE = "fire"  # Огненные плиты
    ICE = "ice"  # Ледяные плиты (замедление)
    TELEPORT = "teleport"  # Телепорт
    POISON = "poison"  # Ядовитый газ
    COLLAPSE = "collapse"  # Обрушение потолка
    EXPLOSIVE = "explosive"  # Взрывные руны


class Trap:
    """Ловушка"""
    
    def __init__(
        self,
        x: int,
        y: int,
        trap_type: TrapType,
        damage: int = 10,
        active: bool = True,
        is_hidden: bool = True
    ):
        """
        Инициализация ловушки
        
        Args:
            x: Позиция X
            y: Позиция Y
            trap_type: Тип ловушки
            damage: Урон
            active: Активна ли ловушка
            is_hidden: Скрыта ли ловушка (True = ловушка, False = механизм)
        """
        self.x = x
        self.y = y
        self.trap_type = trap_type
        self.damage = damage
        self.active = active
        self.triggered = False
        self.is_hidden = is_hidden  # Скрытая ловушка или видимый механизм
        self.detected = False  # Обнаружена ли ловушка игроком
        
    def trigger(self) -> dict:
        """
        Активировать ловушку
        
        Returns:
            Словарь с эффектами ловушки
        """
        if not self.active or self.triggered:
            return {"triggered": False}
        
        self.triggered = True
        
        effect = {
            "triggered": True,
            "trap_type": self.trap_type,
            "damage": self.damage,
            "message": self._get_trigger_message()
        }
        
        # Некоторые ловушки можно использовать повторно
        if self.trap_type in [TrapType.FIRE, TrapType.ICE, TrapType.POISON]:
            self.triggered = False  # Сбрасываем для повторного использования
        
        return effect
    
    def _get_trigger_message(self) -> str:
        """Получить сообщение при активации"""
        messages = {
            TrapType.SPIKES: "Шипы выскакивают из пола!",
            TrapType.ARROW: "Стрела вылетает из стены!",
            TrapType.FIRE: "Пламя вырывается из плиты!",
            TrapType.ICE: "Ледяной холод сковывает движения!",
            TrapType.TELEPORT: "Магический круг телепортирует вас!",
            TrapType.POISON: "Ядовитый газ заполняет комнату!",
            TrapType.COLLAPSE: "Потолок начинает обрушиваться!",
            TrapType.EXPLOSIVE: "Руна взрывается!",
        }
        return messages.get(self.trap_type, "Ловушка активирована!")
    
    def is_visible(self) -> bool:
        """
        Проверить видима ли ловушка
        
        Returns:
            True если ловушка видима
        """
        # Видимые механизмы всегда видны
        if not self.is_hidden:
            return True
        
        # Скрытые ловушки видны только если обнаружены или сработали
        return self.detected or self.triggered
    
    def try_detect(self, detection_chance: float) -> bool:
        """
        Попытка обнаружить ловушку
        
        Args:
            detection_chance: Шанс обнаружения (0.0 - 1.0)
        
        Returns:
            True если ловушка обнаружена
        """
        if not self.is_hidden or self.detected:
            return False
        
        if random.random() < detection_chance:
            self.detected = True
            return True
        
        return False


class TrapGenerator:
    """Генератор ловушек"""
    
    @staticmethod
    def generate_traps_for_floor(
        rooms: List,
        floor: int
    ) -> List[Trap]:
        """
        Сгенерировать ловушки для этажа
        
        Args:
            rooms: Список комнат
            floor: Номер этажа
            
        Returns:
            Список ловушек
        """
        traps = []
        
        # Количество ловушек зависит от этажа
        num_traps = min(2 + floor // 3, 8)  # От 2 до 8 ловушек
        
        if len(rooms) < 2:
            return traps
        
        # Размещаем ловушки в случайных комнатах (не первая)
        available_rooms = rooms[1:]  # Пропускаем первую комнату (вход)
        
        for _ in range(num_traps):
            if not available_rooms:
                break
            
            # Выбираем случайную комнату
            room = random.choice(available_rooms)
            
            # Случайная позиция в комнате (с отступом от краёв)
            margin = 2
            if room.width <= 2 * margin or room.height <= 2 * margin:
                continue
            
            x = room.x + margin + random.randint(0, room.width - 2 * margin - 1)
            y = room.y + margin + random.randint(0, room.height - 2 * margin - 1)
            
            # Выбираем тип ловушки в зависимости от этажа
            trap_type = TrapGenerator._choose_trap_type(floor)
            
            # Урон зависит от этажа
            base_damage = 5 + floor * 2
            damage = random.randint(base_damage, base_damage + 10)
            
            # Определяем скрытая ли ловушка
            is_hidden = TrapGenerator._is_trap_hidden(trap_type)
            
            trap = Trap(x, y, trap_type, damage, is_hidden=is_hidden)
            traps.append(trap)
        
        return traps
    
    @staticmethod
    def _choose_trap_type(floor: int) -> TrapType:
        """
        Выбрать тип ловушки в зависимости от этажа
        
        Args:
            floor: Номер этажа
            
        Returns:
            Тип ловушки
        """
        # Этажи 1-5: Простые ловушки
        if floor <= 5:
            return random.choice([
                TrapType.SPIKES,
                TrapType.ARROW,
                TrapType.FIRE
            ])
        
        # Этажи 6-10: Средние ловушки
        elif floor <= 10:
            return random.choice([
                TrapType.SPIKES,
                TrapType.ARROW,
                TrapType.FIRE,
                TrapType.ICE,
                TrapType.POISON
            ])
        
        # Этажи 11-15: Сложные ловушки
        elif floor <= 15:
            return random.choice([
                TrapType.FIRE,
                TrapType.ICE,
                TrapType.POISON,
                TrapType.TELEPORT,
                TrapType.EXPLOSIVE
            ])
        
        # Этажи 16-20: Опасные ловушки
        else:
            return random.choice([
                TrapType.POISON,
                TrapType.TELEPORT,
                TrapType.COLLAPSE,
                TrapType.EXPLOSIVE
            ])
    
    @staticmethod
    def _is_trap_hidden(trap_type: TrapType) -> bool:
        """
        Определить является ли ловушка скрытой
        
        Args:
            trap_type: Тип ловушки
            
        Returns:
            True если ловушка скрытая, False если видимый механизм
        """
        # СКРЫТЫЕ ЛОВУШКИ (невидимы до обнаружения/срабатывания)
        hidden_traps = [
            TrapType.SPIKES,      # Шипы под полом
            TrapType.ARROW,       # Стрелы из стен
            TrapType.TELEPORT,    # Магический круг
            TrapType.COLLAPSE,    # Обрушение
            TrapType.EXPLOSIVE,   # Взрывные руны
        ]
        
        # ВИДИМЫЕ МЕХАНИЗМЫ (всегда видны)
        # TrapType.FIRE - огненные плиты
        # TrapType.ICE - ледяные поля
        # TrapType.POISON - ядовитые испарения
        
        return trap_type in hidden_traps
