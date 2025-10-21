"""
Предустановленные крафт-станции
Версия: 0.4.0
Этап 0, Неделя 3
"""

from .crafting_stations import (
    CraftingStation, StationType, StationCategory,
    StationUpgrade, StationManager
)


def create_workbench() -> CraftingStation:
    """Создать верстак"""
    station = CraftingStation(
        id="workbench",
        station_type=StationType.WORKBENCH,
        category=StationCategory.BASIC,
        name="Верстак",
        description="Базовая станция для создания простых предметов и инструментов",
        current_tier=1,
        is_unlocked=True,  # Доступен с самого начала
        sprite_path="assets/stations/workbench.png"
    )
    
    # Tier 1 - Базовый верстак
    station.upgrades[1] = StationUpgrade(
        tier=1,
        name="Базовый верстак",
        description="Простой деревянный верстак для базового крафта",
        required_materials={},
        required_level=1,
        cost=0,
        crafting_speed_bonus=0.0,
        quality_bonus=0.0,
        unlocked_recipes=[
            "wooden_stick",
            "wooden_plank",
            "simple_torch",
            "rope",
        ]
    )
    
    # Tier 2 - Улучшенный верстак
    station.upgrades[2] = StationUpgrade(
        tier=2,
        name="Улучшенный верстак",
        description="Верстак с металлическими инструментами и тисками",
        required_materials={
            "iron_ingot": 10,
            "wooden_plank": 20,
            "rope": 5,
        },
        required_level=5,
        cost=500,
        crafting_speed_bonus=0.2,  # +20% скорости
        quality_bonus=0.1,  # +10% качества
        unlocked_recipes=[
            "iron_sword",
            "iron_armor",
            "lockpick",
            "grappling_hook",
        ]
    )
    
    # Tier 3 - Мастерская верстак
    station.upgrades[3] = StationUpgrade(
        tier=3,
        name="Мастерская верстак",
        description="Профессиональный верстак с точными инструментами",
        required_materials={
            "steel_ingot": 15,
            "rare_wood": 10,
            "precision_tools": 1,
        },
        required_level=10,
        cost=2000,
        crafting_speed_bonus=0.3,  # +30% скорости (суммарно +50%)
        quality_bonus=0.15,  # +15% качества (суммарно +25%)
        unlocked_recipes=[
            "steel_sword",
            "steel_armor",
            "master_lockpick",
            "advanced_tools",
        ]
    )
    
    return station


def create_laboratory() -> CraftingStation:
    """Создать лабораторию"""
    station = CraftingStation(
        id="laboratory",
        station_type=StationType.LABORATORY,
        category=StationCategory.ADVANCED,
        name="Лаборатория",
        description="Научная станция для исследований и создания технологических устройств",
        current_tier=1,
        is_unlocked=False,
        sprite_path="assets/stations/laboratory.png"
    )
    
    # Tier 1 - Простая лаборатория
    station.upgrades[1] = StationUpgrade(
        tier=1,
        name="Простая лаборатория",
        description="Базовое оборудование для простых экспериментов",
        required_materials={
            "glass": 10,
            "iron_ingot": 5,
            "wooden_plank": 15,
        },
        required_level=3,
        cost=1000,
        crafting_speed_bonus=0.0,
        quality_bonus=0.0,
        unlocked_recipes=[
            "healing_potion_basic",
            "stamina_potion_basic",
            "smoke_bomb",
            "flashbang",
        ]
    )
    
    # Tier 2 - Продвинутая лаборатория
    station.upgrades[2] = StationUpgrade(
        tier=2,
        name="Продвинутая лаборатория",
        description="Улучшенное оборудование для сложных исследований",
        required_materials={
            "refined_glass": 15,
            "steel_ingot": 10,
            "chemical_reagent": 5,
        },
        required_level=7,
        cost=3000,
        crafting_speed_bonus=0.25,
        quality_bonus=0.15,
        unlocked_recipes=[
            "healing_potion_advanced",
            "stamina_potion_advanced",
            "acid_vial",
            "explosive_charge",
        ]
    )
    
    # Tier 3 - Научная лаборатория
    station.upgrades[3] = StationUpgrade(
        tier=3,
        name="Научная лаборатория",
        description="Современная лаборатория с высокоточным оборудованием",
        required_materials={
            "crystal_glass": 20,
            "titanium_ingot": 15,
            "rare_chemical": 10,
        },
        required_level=12,
        cost=8000,
        crafting_speed_bonus=0.35,
        quality_bonus=0.20,
        unlocked_recipes=[
            "healing_potion_master",
            "stamina_potion_master",
            "nano_repair_kit",
            "emp_grenade",
        ]
    )
    
    return station


def create_alchemy_table() -> CraftingStation:
    """Создать алхимический стол"""
    station = CraftingStation(
        id="alchemy_table",
        station_type=StationType.ALCHEMY_TABLE,
        category=StationCategory.ALCHEMY,
        name="Алхимический стол",
        description="Мистическая станция для создания зелий и эликсиров",
        current_tier=1,
        is_unlocked=False,
        sprite_path="assets/stations/alchemy_table.png"
    )
    
    # Tier 1 - Простой алхимический стол
    station.upgrades[1] = StationUpgrade(
        tier=1,
        name="Простой алхимический стол",
        description="Базовый стол для приготовления простых зелий",
        required_materials={
            "stone": 20,
            "glass": 10,
            "herb": 15,
        },
        required_level=4,
        cost=1500,
        crafting_speed_bonus=0.0,
        quality_bonus=0.05,
        unlocked_recipes=[
            "health_elixir",
            "mana_elixir",
            "antidote",
            "night_vision_potion",
        ]
    )
    
    # Tier 2 - Улучшенный алхимический стол
    station.upgrades[2] = StationUpgrade(
        tier=2,
        name="Улучшенный алхимический стол",
        description="Стол с магическими рунами для усиления эффектов",
        required_materials={
            "marble": 15,
            "crystal": 10,
            "rare_herb": 20,
            "mana_crystal": 5,
        },
        required_level=9,
        cost=5000,
        crafting_speed_bonus=0.3,
        quality_bonus=0.20,
        unlocked_recipes=[
            "greater_health_elixir",
            "greater_mana_elixir",
            "invisibility_potion",
            "strength_potion",
        ]
    )
    
    return station


def create_magic_circle() -> CraftingStation:
    """Создать магический круг"""
    station = CraftingStation(
        id="magic_circle",
        station_type=StationType.MAGIC_CIRCLE,
        category=StationCategory.MAGIC,
        name="Магический круг",
        description="Ритуальная станция для создания магических артефактов",
        current_tier=1,
        is_unlocked=False,
        sprite_path="assets/stations/magic_circle.png"
    )
    
    # Tier 1 - Простой магический круг
    station.upgrades[1] = StationUpgrade(
        tier=1,
        name="Простой магический круг",
        description="Базовый круг для простых ритуалов",
        required_materials={
            "silver_dust": 10,
            "mana_crystal": 5,
            "enchanted_chalk": 3,
        },
        required_level=6,
        cost=3000,
        crafting_speed_bonus=0.0,
        quality_bonus=0.10,
        unlocked_recipes=[
            "magic_scroll_light",
            "magic_scroll_shield",
            "enchanted_amulet",
            "mana_battery",
        ]
    )
    
    # Tier 2 - Усиленный магический круг
    station.upgrades[2] = StationUpgrade(
        tier=2,
        name="Усиленный магический круг",
        description="Круг с древними рунами силы",
        required_materials={
            "gold_dust": 15,
            "greater_mana_crystal": 10,
            "ancient_rune": 5,
        },
        required_level=11,
        cost=7000,
        crafting_speed_bonus=0.25,
        quality_bonus=0.25,
        unlocked_recipes=[
            "magic_scroll_fireball",
            "magic_scroll_teleport",
            "enchanted_ring",
            "soul_gem",
        ]
    )
    
    return station


def create_aldan_terminal() -> CraftingStation:
    """Создать терминал АЛДАН"""
    station = CraftingStation(
        id="aldan_terminal",
        station_type=StationType.ALDAN_TERMINAL,
        category=StationCategory.TECHNOLOGY,
        name="Терминал АЛДАН",
        description="Технологическая станция для взаимодействия с ИИ АЛДАН",
        current_tier=1,
        is_unlocked=False,
        sprite_path="assets/stations/aldan_terminal.png"
    )
    
    # Tier 1 - Базовый терминал
    station.upgrades[1] = StationUpgrade(
        tier=1,
        name="Базовый терминал",
        description="Простой терминал для связи с АЛДАН",
        required_materials={
            "electronic_component": 10,
            "wire": 20,
            "steel_ingot": 5,
        },
        required_level=5,
        cost=2500,
        crafting_speed_bonus=0.0,
        quality_bonus=0.0,
        unlocked_recipes=[
            "data_analysis",
            "artifact_scan",
            "recipe_database_access",
        ]
    )
    
    return station


def create_all_stations() -> StationManager:
    """
    Создать все станции
    
    Returns:
        Менеджер со всеми станциями
    """
    manager = StationManager()
    
    # Добавляем все станции
    manager.add_station(create_workbench())
    manager.add_station(create_laboratory())
    manager.add_station(create_alchemy_table())
    manager.add_station(create_magic_circle())
    manager.add_station(create_aldan_terminal())
    
    return manager
