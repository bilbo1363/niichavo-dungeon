"""
Система крафт-станций
Версия: 0.4.0
Этап 0, Неделя 3
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum


class StationType(Enum):
    """Тип крафт-станции"""
    WORKBENCH = "workbench"          # Верстак
    LABORATORY = "laboratory"        # Лаборатория
    ALCHEMY_TABLE = "alchemy_table"  # Алхимический стол
    MAGIC_CIRCLE = "magic_circle"    # Магический круг
    ALDAN_TERMINAL = "aldan_terminal"  # Терминал АЛДАН


class StationCategory(Enum):
    """Категория крафта станции"""
    BASIC = "basic"          # Базовый крафт
    ADVANCED = "advanced"    # Продвинутый крафт
    ALCHEMY = "alchemy"      # Алхимия
    MAGIC = "magic"          # Магия
    TECHNOLOGY = "technology"  # Технологии


@dataclass
class StationUpgrade:
    """Улучшение станции"""
    
    tier: int                           # Уровень станции (1-3)
    name: str                           # Название уровня
    description: str                    # Описание улучшения
    
    # Требования для улучшения
    required_materials: Dict[str, int] = field(default_factory=dict)  # item_id -> количество
    required_level: int = 1             # Минимальный уровень игрока
    cost: int = 0                       # Стоимость в монетах
    
    # Бонусы
    crafting_speed_bonus: float = 0.0   # Бонус к скорости крафта (0.0 = нет, 0.2 = +20%)
    quality_bonus: float = 0.0          # Бонус к качеству (шанс улучшенного результата)
    unlocked_recipes: List[str] = field(default_factory=list)  # Разблокированные рецепты
    
    def to_dict(self) -> dict:
        """Сериализация в словарь"""
        return {
            'tier': self.tier,
            'name': self.name,
            'description': self.description,
            'required_materials': self.required_materials,
            'required_level': self.required_level,
            'cost': self.cost,
            'crafting_speed_bonus': self.crafting_speed_bonus,
            'quality_bonus': self.quality_bonus,
            'unlocked_recipes': self.unlocked_recipes,
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'StationUpgrade':
        """Десериализация из словаря"""
        return StationUpgrade(
            tier=data['tier'],
            name=data['name'],
            description=data['description'],
            required_materials=data.get('required_materials', {}),
            required_level=data.get('required_level', 1),
            cost=data.get('cost', 0),
            crafting_speed_bonus=data.get('crafting_speed_bonus', 0.0),
            quality_bonus=data.get('quality_bonus', 0.0),
            unlocked_recipes=data.get('unlocked_recipes', []),
        )


@dataclass
class CraftingStation:
    """Крафт-станция"""
    
    id: str                             # Уникальный ID
    station_type: StationType           # Тип станции
    category: StationCategory           # Категория
    
    # Базовая информация
    name: str                           # Название
    description: str                    # Описание
    
    # Состояние
    current_tier: int = 1               # Текущий уровень (1-3)
    is_unlocked: bool = False           # Разблокирована ли
    
    # Улучшения
    upgrades: Dict[int, StationUpgrade] = field(default_factory=dict)  # tier -> upgrade
    
    # Позиция на чердаке
    x: int = 0
    y: int = 0
    
    # Визуал
    sprite_path: str = ""               # Путь к спрайту
    
    def __post_init__(self):
        """Инициализация после создания"""
        if not self.upgrades:
            self.upgrades = {}
    
    def can_upgrade(self, player_level: int, player_inventory: Dict[str, int],
                   player_money: int) -> bool:
        """
        Проверить, можно ли улучшить станцию
        
        Args:
            player_level: Уровень игрока
            player_inventory: Инвентарь игрока (item_id -> количество)
            player_money: Деньги игрока
            
        Returns:
            True если можно улучшить
        """
        next_tier = self.current_tier + 1
        
        # Проверяем, есть ли следующий уровень
        if next_tier not in self.upgrades:
            return False
        
        upgrade = self.upgrades[next_tier]
        
        # Проверка уровня
        if player_level < upgrade.required_level:
            return False
        
        # Проверка денег
        if player_money < upgrade.cost:
            return False
        
        # Проверка материалов
        for item_id, required_count in upgrade.required_materials.items():
            if player_inventory.get(item_id, 0) < required_count:
                return False
        
        return True
    
    def upgrade(self) -> bool:
        """
        Улучшить станцию
        
        Returns:
            True если улучшение успешно
        """
        next_tier = self.current_tier + 1
        
        if next_tier not in self.upgrades:
            return False
        
        self.current_tier = next_tier
        return True
    
    def get_crafting_speed_multiplier(self) -> float:
        """
        Получить множитель скорости крафта
        
        Returns:
            Множитель (1.0 = нормальная скорость, 1.2 = +20% скорости)
        """
        total_bonus = 0.0
        
        # Суммируем бонусы от всех разблокированных улучшений
        for tier in range(1, self.current_tier + 1):
            if tier in self.upgrades:
                total_bonus += self.upgrades[tier].crafting_speed_bonus
        
        return 1.0 + total_bonus
    
    def get_quality_bonus(self) -> float:
        """
        Получить бонус к качеству
        
        Returns:
            Бонус к качеству (0.0 - 1.0)
        """
        total_bonus = 0.0
        
        # Суммируем бонусы от всех разблокированных улучшений
        for tier in range(1, self.current_tier + 1):
            if tier in self.upgrades:
                total_bonus += self.upgrades[tier].quality_bonus
        
        return min(total_bonus, 1.0)  # Максимум 100%
    
    def get_unlocked_recipes(self) -> Set[str]:
        """
        Получить все разблокированные рецепты
        
        Returns:
            Множество ID рецептов
        """
        recipes = set()
        
        # Собираем рецепты от всех разблокированных улучшений
        for tier in range(1, self.current_tier + 1):
            if tier in self.upgrades:
                recipes.update(self.upgrades[tier].unlocked_recipes)
        
        return recipes
    
    def to_dict(self) -> dict:
        """Сериализация в словарь"""
        return {
            'id': self.id,
            'station_type': self.station_type.value,
            'category': self.category.value,
            'name': self.name,
            'description': self.description,
            'current_tier': self.current_tier,
            'is_unlocked': self.is_unlocked,
            'upgrades': {tier: upgrade.to_dict() for tier, upgrade in self.upgrades.items()},
            'x': self.x,
            'y': self.y,
            'sprite_path': self.sprite_path,
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'CraftingStation':
        """Десериализация из словаря"""
        upgrades = {}
        for tier_str, upgrade_data in data.get('upgrades', {}).items():
            upgrades[int(tier_str)] = StationUpgrade.from_dict(upgrade_data)
        
        return CraftingStation(
            id=data['id'],
            station_type=StationType(data['station_type']),
            category=StationCategory(data['category']),
            name=data['name'],
            description=data['description'],
            current_tier=data.get('current_tier', 1),
            is_unlocked=data.get('is_unlocked', False),
            upgrades=upgrades,
            x=data.get('x', 0),
            y=data.get('y', 0),
            sprite_path=data.get('sprite_path', ''),
        )


class StationManager:
    """Менеджер крафт-станций"""
    
    def __init__(self):
        """Инициализация менеджера"""
        self.stations: Dict[str, CraftingStation] = {}
        self.unlocked_stations: Set[str] = set()
    
    def add_station(self, station: CraftingStation):
        """
        Добавить станцию
        
        Args:
            station: Станция для добавления
        """
        self.stations[station.id] = station
        if station.is_unlocked:
            self.unlocked_stations.add(station.id)
    
    def unlock_station(self, station_id: str) -> bool:
        """
        Разблокировать станцию
        
        Args:
            station_id: ID станции
            
        Returns:
            True если успешно разблокирована
        """
        if station_id not in self.stations:
            return False
        
        station = self.stations[station_id]
        if not station.is_unlocked:
            station.is_unlocked = True
            self.unlocked_stations.add(station_id)
            return True
        
        return False
    
    def get_station(self, station_id: str) -> Optional[CraftingStation]:
        """
        Получить станцию по ID
        
        Args:
            station_id: ID станции
            
        Returns:
            Станция или None
        """
        return self.stations.get(station_id)
    
    def get_stations_by_type(self, station_type: StationType) -> List[CraftingStation]:
        """
        Получить все станции определённого типа
        
        Args:
            station_type: Тип станции
            
        Returns:
            Список станций
        """
        return [s for s in self.stations.values() if s.station_type == station_type]
    
    def get_unlocked_stations(self) -> List[CraftingStation]:
        """
        Получить все разблокированные станции
        
        Returns:
            Список разблокированных станций
        """
        return [self.stations[sid] for sid in self.unlocked_stations if sid in self.stations]
    
    def get_all_unlocked_recipes(self) -> Set[str]:
        """
        Получить все разблокированные рецепты со всех станций
        
        Returns:
            Множество ID рецептов
        """
        recipes = set()
        for station in self.get_unlocked_stations():
            recipes.update(station.get_unlocked_recipes())
        return recipes
    
    def to_dict(self) -> dict:
        """Сериализация в словарь"""
        return {
            'stations': {sid: station.to_dict() for sid, station in self.stations.items()},
            'unlocked_stations': list(self.unlocked_stations),
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'StationManager':
        """Десериализация из словаря"""
        manager = StationManager()
        
        for sid, station_data in data.get('stations', {}).items():
            station = CraftingStation.from_dict(station_data)
            manager.add_station(station)
        
        manager.unlocked_stations = set(data.get('unlocked_stations', []))
        
        return manager
