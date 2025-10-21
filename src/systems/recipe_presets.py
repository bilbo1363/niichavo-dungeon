"""
Предустановленные рецепты
Версия: 0.4.0
Этап 0, Неделя 4
"""

from .crafting import Recipe, RecipeCategory, CraftingDifficulty, CraftingSystem


def create_workbench_recipes() -> list[Recipe]:
    """Создать рецепты для верстака"""
    recipes = []
    
    # Tier 1 - Базовые рецепты
    recipes.append(Recipe(
        id="wooden_stick",
        name="Деревянная палка",
        description="Простая палка из дерева",
        category=RecipeCategory.MATERIALS,
        required_station="workbench",
        required_station_tier=1,
        required_level=1,
        difficulty=CraftingDifficulty.EASY,
        ingredients={"wood": 1},
        result_item="wooden_stick",
        result_count=4,
        crafting_time=0.5,
    ))
    
    recipes.append(Recipe(
        id="wooden_plank",
        name="Деревянная доска",
        description="Обработанная доска",
        category=RecipeCategory.MATERIALS,
        required_station="workbench",
        required_station_tier=1,
        required_level=1,
        difficulty=CraftingDifficulty.EASY,
        ingredients={"wood": 1},
        result_item="wooden_plank",
        result_count=2,
        crafting_time=0.5,
    ))
    
    recipes.append(Recipe(
        id="simple_torch",
        name="Простой факел",
        description="Освещает путь во тьме",
        category=RecipeCategory.TOOLS,
        required_station="workbench",
        required_station_tier=1,
        required_level=1,
        difficulty=CraftingDifficulty.EASY,
        ingredients={"wooden_stick": 1, "cloth": 1},
        result_item="simple_torch",
        result_count=3,
        crafting_time=1.0,
    ))
    
    recipes.append(Recipe(
        id="rope",
        name="Верёвка",
        description="Прочная верёвка",
        category=RecipeCategory.MATERIALS,
        required_station="workbench",
        required_station_tier=1,
        required_level=1,
        difficulty=CraftingDifficulty.EASY,
        ingredients={"fiber": 3},
        result_item="rope",
        result_count=1,
        crafting_time=1.0,
    ))
    
    # Tier 2 - Улучшенные рецепты
    recipes.append(Recipe(
        id="iron_sword",
        name="Железный меч",
        description="Надёжное оружие ближнего боя",
        category=RecipeCategory.WEAPONS,
        required_station="workbench",
        required_station_tier=2,
        required_level=5,
        difficulty=CraftingDifficulty.MEDIUM,
        ingredients={"iron_ingot": 3, "wooden_stick": 1},
        result_item="iron_sword",
        result_count=1,
        crafting_time=3.0,
        success_chance=0.9,
        quality_bonus_item="iron_sword_sharp",
        quality_bonus_chance=0.1,
    ))
    
    recipes.append(Recipe(
        id="iron_armor",
        name="Железная броня",
        description="Защищает от ударов",
        category=RecipeCategory.ARMOR,
        required_station="workbench",
        required_station_tier=2,
        required_level=5,
        difficulty=CraftingDifficulty.MEDIUM,
        ingredients={"iron_ingot": 8, "leather": 4},
        result_item="iron_armor",
        result_count=1,
        crafting_time=5.0,
        success_chance=0.9,
    ))
    
    # Tier 3 - Мастерские рецепты
    recipes.append(Recipe(
        id="steel_sword",
        name="Стальной меч",
        description="Превосходное оружие",
        category=RecipeCategory.WEAPONS,
        required_station="workbench",
        required_station_tier=3,
        required_level=10,
        difficulty=CraftingDifficulty.HARD,
        ingredients={"steel_ingot": 5, "rare_wood": 1, "gem": 1},
        result_item="steel_sword",
        result_count=1,
        crafting_time=8.0,
        success_chance=0.8,
        quality_bonus_item="steel_sword_masterwork",
        quality_bonus_chance=0.15,
    ))
    
    return recipes


def create_laboratory_recipes() -> list[Recipe]:
    """Создать рецепты для лаборатории"""
    recipes = []
    
    # Tier 1 - Базовые зелья
    recipes.append(Recipe(
        id="healing_potion_basic",
        name="Базовое зелье лечения",
        description="Восстанавливает 50 HP",
        category=RecipeCategory.CONSUMABLES,
        required_station="laboratory",
        required_station_tier=1,
        required_level=3,
        difficulty=CraftingDifficulty.EASY,
        ingredients={"herb": 2, "water": 1},
        result_item="healing_potion_basic",
        result_count=1,
        crafting_time=2.0,
    ))
    
    recipes.append(Recipe(
        id="stamina_potion_basic",
        name="Базовое зелье выносливости",
        description="Восстанавливает 50 выносливости",
        category=RecipeCategory.CONSUMABLES,
        required_station="laboratory",
        required_station_tier=1,
        required_level=3,
        difficulty=CraftingDifficulty.EASY,
        ingredients={"mushroom": 2, "water": 1},
        result_item="stamina_potion_basic",
        result_count=1,
        crafting_time=2.0,
    ))
    
    # Tier 2 - Продвинутые зелья
    recipes.append(Recipe(
        id="healing_potion_advanced",
        name="Продвинутое зелье лечения",
        description="Восстанавливает 100 HP",
        category=RecipeCategory.CONSUMABLES,
        required_station="laboratory",
        required_station_tier=2,
        required_level=7,
        difficulty=CraftingDifficulty.MEDIUM,
        ingredients={"rare_herb": 2, "crystal_water": 1, "essence": 1},
        result_item="healing_potion_advanced",
        result_count=1,
        crafting_time=4.0,
        success_chance=0.9,
    ))
    
    return recipes


def create_alchemy_recipes() -> list[Recipe]:
    """Создать рецепты для алхимического стола"""
    recipes = []
    
    recipes.append(Recipe(
        id="health_elixir",
        name="Эликсир здоровья",
        description="Мощное лечебное средство",
        category=RecipeCategory.ALCHEMY,
        required_station="alchemy_table",
        required_station_tier=1,
        required_level=4,
        difficulty=CraftingDifficulty.MEDIUM,
        ingredients={"rare_herb": 3, "mana_crystal": 1, "pure_water": 1},
        result_item="health_elixir",
        result_count=1,
        crafting_time=5.0,
        success_chance=0.85,
        quality_bonus_item="health_elixir_greater",
        quality_bonus_chance=0.2,
    ))
    
    recipes.append(Recipe(
        id="antidote",
        name="Противоядие",
        description="Лечит отравление",
        category=RecipeCategory.ALCHEMY,
        required_station="alchemy_table",
        required_station_tier=1,
        required_level=4,
        difficulty=CraftingDifficulty.EASY,
        ingredients={"herb": 2, "mushroom": 1},
        result_item="antidote",
        result_count=2,
        crafting_time=2.0,
    ))
    
    return recipes


def create_magic_recipes() -> list[Recipe]:
    """Создать рецепты для магического круга"""
    recipes = []
    
    recipes.append(Recipe(
        id="magic_scroll_light",
        name="Свиток света",
        description="Создаёт яркий свет",
        category=RecipeCategory.MAGIC,
        required_station="magic_circle",
        required_station_tier=1,
        required_level=6,
        difficulty=CraftingDifficulty.MEDIUM,
        ingredients={"parchment": 1, "mana_crystal": 1, "silver_dust": 1},
        result_item="magic_scroll_light",
        result_count=1,
        crafting_time=3.0,
        success_chance=0.9,
    ))
    
    recipes.append(Recipe(
        id="enchanted_amulet",
        name="Зачарованный амулет",
        description="Даёт защиту от магии",
        category=RecipeCategory.MAGIC,
        required_station="magic_circle",
        required_station_tier=1,
        required_level=6,
        difficulty=CraftingDifficulty.HARD,
        ingredients={"silver": 2, "mana_crystal": 2, "gem": 1},
        result_item="enchanted_amulet",
        result_count=1,
        crafting_time=6.0,
        success_chance=0.8,
        quality_bonus_item="enchanted_amulet_greater",
        quality_bonus_chance=0.15,
    ))
    
    return recipes


def create_all_recipes() -> CraftingSystem:
    """
    Создать все рецепты
    
    Returns:
        Система крафта со всеми рецептами
    """
    system = CraftingSystem()
    
    # Добавляем все рецепты
    for recipe in create_workbench_recipes():
        system.add_recipe(recipe)
    
    for recipe in create_laboratory_recipes():
        system.add_recipe(recipe)
    
    for recipe in create_alchemy_recipes():
        system.add_recipe(recipe)
    
    for recipe in create_magic_recipes():
        system.add_recipe(recipe)
    
    return system
