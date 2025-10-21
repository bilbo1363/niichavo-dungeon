"""
Система крафта и рецептов
Версия: 0.4.0
Этап 0, Неделя 4
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum


class RecipeCategory(Enum):
    """Категория рецепта"""
    TOOLS = "tools"              # Инструменты
    WEAPONS = "weapons"          # Оружие
    ARMOR = "armor"              # Броня
    CONSUMABLES = "consumables"  # Расходники
    MATERIALS = "materials"      # Материалы
    ALCHEMY = "alchemy"          # Алхимия
    MAGIC = "magic"              # Магия
    TECHNOLOGY = "technology"    # Технологии


class CraftingDifficulty(Enum):
    """Сложность крафта"""
    EASY = "easy"          # Простой
    MEDIUM = "medium"      # Средний
    HARD = "hard"          # Сложный
    EXPERT = "expert"      # Экспертный


@dataclass
class Recipe:
    """Рецепт для крафта"""
    
    id: str                                 # Уникальный ID
    name: str                               # Название
    description: str                        # Описание
    category: RecipeCategory                # Категория
    
    # Требования
    required_station: str                   # ID требуемой станции
    required_station_tier: int = 1          # Минимальный tier станции
    required_level: int = 1                 # Минимальный уровень игрока
    difficulty: CraftingDifficulty = CraftingDifficulty.EASY
    
    # Ингредиенты
    ingredients: Dict[str, int] = field(default_factory=dict)  # item_id -> количество
    
    # Результат
    result_item: str = ""                   # ID результата
    result_count: int = 1                   # Количество результата
    
    # Параметры крафта
    crafting_time: float = 1.0              # Время крафта в секундах
    success_chance: float = 1.0             # Базовый шанс успеха (0.0-1.0)
    
    # Опциональные результаты при улучшенном качестве
    quality_bonus_item: Optional[str] = None  # Бонусный предмет при высоком качестве
    quality_bonus_chance: float = 0.0       # Шанс бонусного предмета
    
    def can_craft(self, player_level: int, player_inventory: Dict[str, int],
                  station_id: str, station_tier: int) -> bool:
        """
        Проверить, можно ли создать предмет
        
        Args:
            player_level: Уровень игрока
            player_inventory: Инвентарь игрока
            station_id: ID станции
            station_tier: Tier станции
            
        Returns:
            True если можно создать
        """
        # Проверка уровня
        if player_level < self.required_level:
            return False
        
        # Проверка станции
        if station_id != self.required_station:
            return False
        
        # Проверка tier станции
        if station_tier < self.required_station_tier:
            return False
        
        # Проверка ингредиентов
        for item_id, required_count in self.ingredients.items():
            if player_inventory.get(item_id, 0) < required_count:
                return False
        
        return True
    
    def to_dict(self) -> dict:
        """Сериализация в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category.value,
            'required_station': self.required_station,
            'required_station_tier': self.required_station_tier,
            'required_level': self.required_level,
            'difficulty': self.difficulty.value,
            'ingredients': self.ingredients,
            'result_item': self.result_item,
            'result_count': self.result_count,
            'crafting_time': self.crafting_time,
            'success_chance': self.success_chance,
            'quality_bonus_item': self.quality_bonus_item,
            'quality_bonus_chance': self.quality_bonus_chance,
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Recipe':
        """Десериализация из словаря"""
        return Recipe(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            category=RecipeCategory(data['category']),
            required_station=data['required_station'],
            required_station_tier=data.get('required_station_tier', 1),
            required_level=data.get('required_level', 1),
            difficulty=CraftingDifficulty(data.get('difficulty', 'easy')),
            ingredients=data.get('ingredients', {}),
            result_item=data.get('result_item', ''),
            result_count=data.get('result_count', 1),
            crafting_time=data.get('crafting_time', 1.0),
            success_chance=data.get('success_chance', 1.0),
            quality_bonus_item=data.get('quality_bonus_item'),
            quality_bonus_chance=data.get('quality_bonus_chance', 0.0),
        )


@dataclass
class CraftingResult:
    """Результат крафта"""
    success: bool                           # Успешен ли крафт
    result_item: str                        # ID результата
    result_count: int                       # Количество
    bonus_item: Optional[str] = None        # Бонусный предмет
    bonus_count: int = 0                    # Количество бонуса
    message: str = ""                       # Сообщение


class CraftingSystem:
    """Система крафта"""
    
    def __init__(self):
        """Инициализация системы"""
        self.recipes: Dict[str, Recipe] = {}
        self.unlocked_recipes: Set[str] = set()
    
    def add_recipe(self, recipe: Recipe):
        """
        Добавить рецепт
        
        Args:
            recipe: Рецепт для добавления
        """
        self.recipes[recipe.id] = recipe
    
    def unlock_recipe(self, recipe_id: str) -> bool:
        """
        Разблокировать рецепт
        
        Args:
            recipe_id: ID рецепта
            
        Returns:
            True если успешно разблокирован
        """
        if recipe_id in self.recipes and recipe_id not in self.unlocked_recipes:
            self.unlocked_recipes.add(recipe_id)
            return True
        return False
    
    def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        """
        Получить рецепт по ID
        
        Args:
            recipe_id: ID рецепта
            
        Returns:
            Рецепт или None
        """
        return self.recipes.get(recipe_id)
    
    def get_recipes_for_station(self, station_id: str, station_tier: int) -> List[Recipe]:
        """
        Получить рецепты для станции
        
        Args:
            station_id: ID станции
            station_tier: Tier станции
            
        Returns:
            Список доступных рецептов
        """
        recipes = []
        for recipe_id in self.unlocked_recipes:
            recipe = self.recipes.get(recipe_id)
            if recipe and recipe.required_station == station_id:
                if recipe.required_station_tier <= station_tier:
                    recipes.append(recipe)
        return recipes
    
    def get_recipes_by_category(self, category: RecipeCategory) -> List[Recipe]:
        """
        Получить рецепты по категории
        
        Args:
            category: Категория рецептов
            
        Returns:
            Список рецептов
        """
        return [r for r in self.recipes.values() 
                if r.category == category and r.id in self.unlocked_recipes]
    
    def craft_item(self, recipe_id: str, player_level: int,
                   player_inventory: Dict[str, int], station_id: str,
                   station_tier: int, quality_bonus: float = 0.0) -> CraftingResult:
        """
        Создать предмет
        
        Args:
            recipe_id: ID рецепта
            player_level: Уровень игрока
            player_inventory: Инвентарь игрока
            station_id: ID станции
            station_tier: Tier станции
            quality_bonus: Бонус качества от станции (0.0-1.0)
            
        Returns:
            Результат крафта
        """
        # Проверяем, есть ли рецепт
        recipe = self.get_recipe(recipe_id)
        if not recipe:
            return CraftingResult(
                success=False,
                result_item="",
                result_count=0,
                message="Рецепт не найден"
            )
        
        # Проверяем, разблокирован ли рецепт
        if recipe_id not in self.unlocked_recipes:
            return CraftingResult(
                success=False,
                result_item="",
                result_count=0,
                message="Рецепт не разблокирован"
            )
        
        # Проверяем возможность крафта
        if not recipe.can_craft(player_level, player_inventory, station_id, station_tier):
            return CraftingResult(
                success=False,
                result_item="",
                result_count=0,
                message="Не выполнены требования для крафта"
            )
        
        # Тратим ингредиенты
        for item_id, count in recipe.ingredients.items():
            player_inventory[item_id] -= count
        
        # Проверяем успех (с учётом сложности)
        import random
        success_roll = random.random()
        if success_roll > recipe.success_chance:
            return CraftingResult(
                success=False,
                result_item="",
                result_count=0,
                message="Крафт не удался! Материалы потеряны."
            )
        
        # Успешный крафт
        result = CraftingResult(
            success=True,
            result_item=recipe.result_item,
            result_count=recipe.result_count,
            message=f"Создано: {recipe.name}"
        )
        
        # Проверяем бонусный предмет (с учётом качества станции)
        if recipe.quality_bonus_item and recipe.quality_bonus_chance > 0:
            bonus_chance = recipe.quality_bonus_chance + quality_bonus
            bonus_roll = random.random()
            if bonus_roll <= bonus_chance:
                result.bonus_item = recipe.quality_bonus_item
                result.bonus_count = 1
                result.message += f" + бонус: {recipe.quality_bonus_item}!"
        
        return result
    
    def to_dict(self) -> dict:
        """Сериализация в словарь"""
        return {
            'recipes': {rid: recipe.to_dict() for rid, recipe in self.recipes.items()},
            'unlocked_recipes': list(self.unlocked_recipes),
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'CraftingSystem':
        """Десериализация из словаря"""
        system = CraftingSystem()
        
        for rid, recipe_data in data.get('recipes', {}).items():
            recipe = Recipe.from_dict(recipe_data)
            system.add_recipe(recipe)
        
        system.unlocked_recipes = set(data.get('unlocked_recipes', []))
        
        return system
