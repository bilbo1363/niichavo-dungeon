"""
Состояние этажа
"""
from dataclasses import dataclass, field
from typing import Optional
import numpy as np


@dataclass
class FloorState:
    """Состояние этажа подземелья"""
    
    floor_number: int
    seed: int
    is_stabilized: bool = False
    
    # Сохранённые данные уровня (если стабилизирован)
    saved_tiles: Optional[np.ndarray] = None
    entrance_pos: Optional[tuple] = None
    exit_pos: Optional[tuple] = None
    saved_fog_of_war: Optional[np.ndarray] = None  # Сохранённая карта видимости
    
    # Руна устойчивости собрана?
    stability_rune_collected: bool = False
    
    # Загадка на стене (появляется после стабилизации)
    riddle_spawned: bool = False  # Была ли создана загадка
    riddle_positions: list = field(default_factory=list)  # Позиции загадок (x, y)
    
    def stabilize(
        self, 
        level_tiles: np.ndarray, 
        entrance: tuple, 
        exit: tuple,
        fog_of_war: np.ndarray = None
    ) -> None:
        """
        Стабилизировать этаж
        
        Args:
            level_tiles: Тайлы уровня для сохранения
            entrance: Позиция входа
            exit: Позиция выхода
            fog_of_war: Карта видимости для сохранения
        """
        self.is_stabilized = True
        self.saved_tiles = level_tiles.copy()
        self.entrance_pos = entrance
        self.exit_pos = exit
        
        # Сохраняем fog of war если передан
        if fog_of_war is not None:
            self.saved_fog_of_war = fog_of_war.copy()
        
        print(f"🔒 Этаж {self.floor_number} стабилизирован!")
        print(f"   Планировка и разведанные области сохранены")
        
    def get_saved_data(self) -> Optional[dict]:
        """
        Получить сохранённые данные уровня
        
        Returns:
            Словарь с данными или None если не стабилизирован
        """
        if not self.is_stabilized:
            return None
            
        return {
            'tiles': self.saved_tiles,
            'entrance_pos': self.entrance_pos,
            'exit_pos': self.exit_pos,
            'fog_of_war': self.saved_fog_of_war,
            'riddle_positions': self.riddle_positions
        }


class FloorStateManager:
    """Менеджер состояний этажей"""
    
    def __init__(self):
        """Инициализация менеджера"""
        self.floors: dict[int, FloorState] = {}
        print("📚 Менеджер состояний этажей создан")
        
    def get_or_create_floor_state(self, floor_number: int, seed: int) -> FloorState:
        """
        Получить или создать состояние этажа
        
        Args:
            floor_number: Номер этажа
            seed: Seed для генерации
            
        Returns:
            Состояние этажа
        """
        if floor_number not in self.floors:
            self.floors[floor_number] = FloorState(
                floor_number=floor_number,
                seed=seed
            )
            print(f"📄 Создано состояние для этажа {floor_number}")
            
        return self.floors[floor_number]
        
    def is_floor_stabilized(self, floor_number: int) -> bool:
        """
        Проверить, стабилизирован ли этаж
        
        Args:
            floor_number: Номер этажа
            
        Returns:
            True если стабилизирован
        """
        if floor_number not in self.floors:
            return False
        return self.floors[floor_number].is_stabilized
        
    def stabilize_floor(
        self, 
        floor_number: int, 
        level_tiles: np.ndarray,
        entrance: tuple,
        exit: tuple,
        fog_of_war: np.ndarray = None
    ) -> None:
        """
        Стабилизировать этаж
        
        Args:
            floor_number: Номер этажа
            level_tiles: Тайлы уровня
            entrance: Позиция входа
            exit: Позиция выхода
            fog_of_war: Карта видимости
        """
        if floor_number in self.floors:
            self.floors[floor_number].stabilize(level_tiles, entrance, exit, fog_of_war)
        else:
            print(f"⚠️  Этаж {floor_number} не найден в менеджере")
            
    def get_stabilized_count(self) -> int:
        """
        Получить количество стабилизированных этажей
        
        Returns:
            Количество стабилизированных этажей
        """
        return sum(1 for floor in self.floors.values() if floor.is_stabilized)
        
    def all_floors_stabilized(self, total_floors: int = 20) -> bool:
        """
        Проверить, все ли этажи стабилизированы
        
        Args:
            total_floors: Общее количество этажей
            
        Returns:
            True если все этажи стабилизированы
        """
        return self.get_stabilized_count() >= total_floors


if __name__ == "__main__":
    # Тест FloorStateManager
    manager = FloorStateManager()
    
    # Создаём состояния для нескольких этажей
    floor1 = manager.get_or_create_floor_state(1, 12345)
    floor2 = manager.get_or_create_floor_state(2, 67890)
    
    print(f"\nЭтаж 1 стабилизирован: {floor1.is_stabilized}")
    print(f"Этаж 2 стабилизирован: {floor2.is_stabilized}")
    
    # Стабилизируем этаж 1
    test_tiles = np.zeros((40, 60), dtype=np.uint8)
    manager.stabilize_floor(1, test_tiles, (10, 10), (50, 30))
    
    print(f"\nПосле стабилизации:")
    print(f"Этаж 1 стабилизирован: {manager.is_floor_stabilized(1)}")
    print(f"Стабилизировано этажей: {manager.get_stabilized_count()}/20")
    print(f"Все этажи стабилизированы: {manager.all_floors_stabilized()}")
