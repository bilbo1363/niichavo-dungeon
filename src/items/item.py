"""
Система предметов
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ItemType(Enum):
    """Типы предметов"""
    WEAPON = "weapon"           # Оружие
    CONSUMABLE = "consumable"   # Расходуемое (еда, зелья)
    KEY_ITEM = "key_item"       # Ключевой предмет
    MATERIAL = "material"       # Материал для крафта
    ARTIFACT = "artifact"       # Артефакт


class ItemRarity(Enum):
    """Редкость предмета"""
    COMMON = "common"       # Обычный (серый)
    UNCOMMON = "uncommon"   # Необычный (зелёный)
    RARE = "rare"           # Редкий (синий)
    EPIC = "epic"           # Эпический (фиолетовый)
    LEGENDARY = "legendary" # Легендарный (оранжевый)


@dataclass
class Item:
    """Класс предмета"""
    
    id: str                          # Уникальный ID
    name: str                        # Название
    description: str                 # Описание
    item_type: ItemType              # Тип предмета
    rarity: ItemRarity = ItemRarity.COMMON
    
    # Характеристики оружия
    damage: int = 0                  # Урон
    durability: int = 100            # Прочность
    max_durability: int = 100        # Максимальная прочность
    
    # Характеристики расходуемых
    heal_amount: int = 0             # Восстановление здоровья
    endurance_amount: int = 0        # Восстановление выносливости
    clarity_amount: int = 0          # Восстановление ясности
    
    # Свойства
    stackable: bool = False          # Можно ли складывать в стопку
    max_stack: int = 1               # Максимальный размер стопки
    weight: float = 1.0              # Вес
    value: int = 0                   # Стоимость
    
    def use(self, player) -> bool:
        """
        Использовать предмет
        
        Args:
            player: Игрок
            
        Returns:
            True если предмет использован успешно
        """
        if self.item_type == ItemType.CONSUMABLE:
            # Восстанавливаем характеристики
            if self.heal_amount > 0:
                old_health = player.stats.health
                player.stats.health = min(
                    player.stats.max_health,
                    player.stats.health + self.heal_amount
                )
                healed = player.stats.health - old_health
                print(f"💊 Восстановлено {healed} HP")
                
            if self.endurance_amount > 0:
                old_endurance = player.stats.endurance
                player.stats.endurance = min(
                    player.stats.max_endurance,
                    player.stats.endurance + self.endurance_amount
                )
                restored = player.stats.endurance - old_endurance
                print(f"⚡ Восстановлено {restored} выносливости")
                
            if self.clarity_amount > 0:
                old_clarity = player.stats.clarity
                player.stats.clarity = min(100, player.stats.clarity + self.clarity_amount)
                restored = player.stats.clarity - old_clarity
                print(f"🧠 Восстановлено {restored} ясности")
                
            return True
            
        return False
        
    def get_rarity_color(self) -> tuple:
        """
        Получить цвет редкости
        
        Returns:
            RGB цвет
        """
        colors = {
            ItemRarity.COMMON: (150, 150, 150),      # Серый
            ItemRarity.UNCOMMON: (50, 200, 50),      # Зелёный
            ItemRarity.RARE: (50, 100, 255),         # Синий
            ItemRarity.EPIC: (200, 50, 255),         # Фиолетовый
            ItemRarity.LEGENDARY: (255, 150, 0)      # Оранжевый
        }
        return colors.get(self.rarity, (255, 255, 255))


class ItemDatabase:
    """База данных предметов"""
    
    def __init__(self):
        """Инициализация базы данных"""
        self.items = {}
        self._init_items()
        
    def _init_items(self):
        """Инициализация предметов"""
        # Оружие
        self.items["rusty_pipe"] = Item(
            id="rusty_pipe",
            name="Ржавая труба",
            description="Старая водопроводная труба. Лучше чем ничего.",
            item_type=ItemType.WEAPON,
            rarity=ItemRarity.COMMON,
            damage=5,
            durability=50,
            max_durability=50,
            weight=2.0,
            value=10
        )
        
        self.items["crowbar"] = Item(
            id="crowbar",
            name="Лом",
            description="Надёжный инструмент. Хорошо подходит для взлома и самообороны.",
            item_type=ItemType.WEAPON,
            rarity=ItemRarity.UNCOMMON,
            damage=10,
            durability=100,
            max_durability=100,
            weight=3.0,
            value=50
        )
        
        self.items["fire_axe"] = Item(
            id="fire_axe",
            name="Пожарный топор",
            description="Тяжёлый топор. Наносит серьёзный урон.",
            item_type=ItemType.WEAPON,
            rarity=ItemRarity.RARE,
            damage=20,
            durability=150,
            max_durability=150,
            weight=5.0,
            value=200
        )
        
        # Расходуемые предметы
        self.items["bandage"] = Item(
            id="bandage",
            name="Бинт",
            description="Простой медицинский бинт. Восстанавливает 20 HP.",
            item_type=ItemType.CONSUMABLE,
            rarity=ItemRarity.COMMON,
            heal_amount=20,
            stackable=True,
            max_stack=10,
            weight=0.1,
            value=15
        )
        
        self.items["medkit"] = Item(
            id="medkit",
            name="Аптечка",
            description="Полноценная аптечка. Восстанавливает 50 HP.",
            item_type=ItemType.CONSUMABLE,
            rarity=ItemRarity.UNCOMMON,
            heal_amount=50,
            stackable=True,
            max_stack=5,
            weight=0.5,
            value=50
        )
        
        self.items["energy_drink"] = Item(
            id="energy_drink",
            name="Энергетик",
            description="Восстанавливает 30 выносливости.",
            item_type=ItemType.CONSUMABLE,
            rarity=ItemRarity.COMMON,
            endurance_amount=30,
            stackable=True,
            max_stack=10,
            weight=0.3,
            value=20
        )
        
        self.items["coffee"] = Item(
            id="coffee",
            name="Кофе",
            description="Крепкий кофе. Восстанавливает 10 ясности.",
            item_type=ItemType.CONSUMABLE,
            rarity=ItemRarity.COMMON,
            clarity_amount=10,
            stackable=True,
            max_stack=10,
            weight=0.2,
            value=10
        )
        
        # ===== ЕДА =====
        self.items["bread"] = Item(
            id="bread",
            name="Хлеб",
            description="Кусок чёрствого хлеба. Восстанавливает 10 HP.",
            item_type=ItemType.CONSUMABLE,
            rarity=ItemRarity.COMMON,
            heal_amount=10,
            stackable=True,
            max_stack=20,
            weight=0.2,
            value=5
        )
        
        self.items["canned_food"] = Item(
            id="canned_food",
            name="Консервы",
            description="Консервированная еда. Восстанавливает 25 HP.",
            item_type=ItemType.CONSUMABLE,
            rarity=ItemRarity.COMMON,
            heal_amount=25,
            stackable=True,
            max_stack=10,
            weight=0.5,
            value=20
        )
        
        self.items["dried_meat"] = Item(
            id="dried_meat",
            name="Вяленое мясо",
            description="Сушёное мясо. Восстанавливает 15 HP и 10 выносливости.",
            item_type=ItemType.CONSUMABLE,
            rarity=ItemRarity.UNCOMMON,
            heal_amount=15,
            endurance_amount=10,
            stackable=True,
            max_stack=15,
            weight=0.3,
            value=30
        )
        
        self.items["chocolate"] = Item(
            id="chocolate",
            name="Шоколад",
            description="Плитка шоколада. Восстанавливает 5 HP и 20 выносливости.",
            item_type=ItemType.CONSUMABLE,
            rarity=ItemRarity.COMMON,
            heal_amount=5,
            endurance_amount=20,
            stackable=True,
            max_stack=20,
            weight=0.1,
            value=15
        )
        
        self.items["apple"] = Item(
            id="apple",
            name="Яблоко",
            description="Свежее яблоко. Восстанавливает 8 HP.",
            item_type=ItemType.CONSUMABLE,
            rarity=ItemRarity.COMMON,
            heal_amount=8,
            stackable=True,
            max_stack=20,
            weight=0.2,
            value=8
        )
        
        self.items["water_bottle"] = Item(
            id="water_bottle",
            name="Бутылка воды",
            description="Чистая вода. Восстанавливает 5 HP и 15 выносливости.",
            item_type=ItemType.CONSUMABLE,
            rarity=ItemRarity.COMMON,
            heal_amount=5,
            endurance_amount=15,
            stackable=True,
            max_stack=10,
            weight=0.5,
            value=10
        )
        
        self.items["hot_meal"] = Item(
            id="hot_meal",
            name="Горячая еда",
            description="Тёплая домашняя еда. Восстанавливает 40 HP и 20 выносливости.",
            item_type=ItemType.CONSUMABLE,
            rarity=ItemRarity.RARE,
            heal_amount=40,
            endurance_amount=20,
            stackable=True,
            max_stack=5,
            weight=1.0,
            value=80
        )
        
        self.items["protein_bar"] = Item(
            id="protein_bar",
            name="Протеиновый батончик",
            description="Питательный батончик. Восстанавливает 12 HP и 25 выносливости.",
            item_type=ItemType.CONSUMABLE,
            rarity=ItemRarity.UNCOMMON,
            heal_amount=12,
            endurance_amount=25,
            stackable=True,
            max_stack=15,
            weight=0.2,
            value=25
        )
        
        # ===== НАПИТКИ =====
        self.items["tea"] = Item(
            id="tea",
            name="Чай",
            description="Горячий чай. Восстанавливает 5 ясности и 10 выносливости.",
            item_type=ItemType.CONSUMABLE,
            rarity=ItemRarity.COMMON,
            clarity_amount=5,
            endurance_amount=10,
            stackable=True,
            max_stack=10,
            weight=0.2,
            value=12
        )
        
        self.items["juice"] = Item(
            id="juice",
            name="Сок",
            description="Фруктовый сок. Восстанавливает 10 HP и 5 выносливости.",
            item_type=ItemType.CONSUMABLE,
            rarity=ItemRarity.COMMON,
            heal_amount=10,
            endurance_amount=5,
            stackable=True,
            max_stack=10,
            weight=0.4,
            value=15
        )
        
        # Ключевые предметы
        self.items["master_key"] = Item(
            id="master_key",
            name="Мастер-ключ",
            description="Открывает любые двери в институте.",
            item_type=ItemType.KEY_ITEM,
            rarity=ItemRarity.RARE,
            weight=0.1,
            value=0
        )
        
        self.items["flashlight"] = Item(
            id="flashlight",
            name="Фонарик",
            description="Освещает тёмные этажи.",
            item_type=ItemType.KEY_ITEM,
            rarity=ItemRarity.UNCOMMON,
            weight=0.5,
            value=30
        )
        
        print(f"📦 База данных предметов создана: {len(self.items)} предметов")
        
    def get_item(self, item_id: str) -> Optional[Item]:
        """
        Получить предмет по ID
        
        Args:
            item_id: ID предмета
            
        Returns:
            Предмет или None
        """
        item = self.items.get(item_id)
        if item:
            # Возвращаем копию чтобы не изменять оригинал
            from copy import deepcopy
            return deepcopy(item)
        return None
        
    def list_items_by_type(self, item_type: ItemType) -> list[Item]:
        """
        Получить список предметов по типу
        
        Args:
            item_type: Тип предмета
            
        Returns:
            Список предметов
        """
        return [item for item in self.items.values() if item.item_type == item_type]


if __name__ == "__main__":
    # Тест системы предметов
    db = ItemDatabase()
    
    # Получаем предмет
    pipe = db.get_item("rusty_pipe")
    print(f"\nПредмет: {pipe.name}")
    print(f"Описание: {pipe.description}")
    print(f"Урон: {pipe.damage}")
    print(f"Редкость: {pipe.rarity.value}")
    
    # Список оружия
    weapons = db.list_items_by_type(ItemType.WEAPON)
    print(f"\nОружие ({len(weapons)}):")
    for weapon in weapons:
        print(f"  - {weapon.name}: {weapon.damage} урона")
