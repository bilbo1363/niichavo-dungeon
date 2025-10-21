# Пересмотр порядка реализации v0.4.0

**Дата:** 21.10.2025  
**Причина:** Для "Журнала исследователя" нужна базовая система прогрессии

---

## ⚠️ ПРОБЛЕМА

### Текущий план:
```
Неделя 1-2: Журнал исследователя
Неделя 3: Режимы сложности
...
```

### Что не так:
**Журнал исследователя требует:**
- ❌ Систему характеристик/умений (для бонусов)
- ❌ Систему прокачки (для улучшений)
- ❌ Базовый крафт/исследования (для применения знаний)
- ❌ Систему способностей (для разблокировок)

**Этого всего ещё НЕТ в текущем проекте!**

---

## ✅ РЕШЕНИЕ: Новый порядок реализации

### ЭТАП 0: Фундамент (Недели 1-3) ← НОВОЕ
**Базовые системы для всех остальных функций**

#### Неделя 1: Система характеристик и прогрессии
- Базовые характеристики игрока
- Система уровней
- Опыт и прокачка
- Характеристики врагов

#### Неделя 2: Система способностей и умений
- Пассивные способности
- Активные способности
- Система разблокировок
- Применение способностей

#### Неделя 3: Базовый крафт и исследования
- Простой крафт предметов
- Система рецептов
- Исследование артефактов
- Улучшение предметов

---

### ЭТАП 1: Журнал исследователя (Недели 4-5)
**Теперь можно реализовать, т.к. есть фундамент**
- Наблюдение и изучение
- Разблокировка способностей
- Применение знаний через крафт

---

### ЭТАП 2: Остальные функции (Недели 6-14)
- Режимы сложности
- История деда
- ИИ АЛДАН
- Развитие базы
- Концовки

---

## 📊 НОВЫЙ ГРАФИК (16 НЕДЕЛЬ)

```
Неделя 1:     [████] Характеристики и прогрессия
Неделя 2:     [████] Способности и умения
Неделя 3:     [████] Базовый крафт
Неделя 4-5:   [████████] Журнал исследователя
Неделя 6:     [████] Режимы сложности
Неделя 7-9:   [████████████] История деда
Неделя 10-11: [████████] ИИ АЛДАН
Неделя 12-13: [████████] Развитие базы
Неделя 14:    [████] Концовки
Неделя 15-16: [████████] Баланс и тестирование
```

**Новая целевая дата:** Середина февраля 2026 (+2 недели)

---

## 🎯 ДЕТАЛЬНЫЙ ПЛАН ЭТАПА 0

### НЕДЕЛЯ 1: Система характеристик и прогрессии

#### Что реализовать:

**1. Базовые характеристики игрока:**
```python
class PlayerStats:
    # Основные
    health: int          # Здоровье
    max_health: int
    stamina: int         # Выносливость
    max_stamina: int
    
    # Боевые
    attack: int          # Урон
    defense: int         # Защита
    accuracy: float      # Точность (0.0-1.0)
    evasion: float       # Уклонение (0.0-1.0)
    
    # Исследовательские
    perception: int      # Восприятие (обнаружение)
    intelligence: int    # Интеллект (крафт, изучение)
    luck: int           # Удача (лут, критические удары)
    
    # Прогрессия
    level: int
    experience: int
    exp_to_next_level: int
```

**2. Система уровней:**
```python
class LevelSystem:
    def calculate_exp_for_level(level: int) -> int:
        """100 * level^1.5"""
        return int(100 * (level ** 1.5))
    
    def gain_exp(amount: int):
        """Получение опыта"""
        self.experience += amount
        while self.experience >= self.exp_to_next_level:
            self.level_up()
    
    def level_up():
        """Повышение уровня"""
        self.level += 1
        self.exp_to_next_level = self.calculate_exp_for_level(self.level)
        
        # Улучшение характеристик
        self.max_health += 10
        self.attack += 2
        self.defense += 1
        
        # Очки способностей
        self.ability_points += 1
```

**3. Модификаторы:**
```python
class StatModifier:
    """Временные или постоянные модификаторы"""
    stat_name: str
    value: float
    modifier_type: str  # 'flat' или 'percent'
    duration: int       # -1 для постоянных
    source: str         # Откуда бонус

class ModifierSystem:
    def apply_modifiers(base_value: float, modifiers: List[StatModifier]) -> float:
        """Применить все модификаторы"""
        # Сначала flat
        result = base_value
        for mod in modifiers:
            if mod.modifier_type == 'flat':
                result += mod.value
        
        # Потом percent
        for mod in modifiers:
            if mod.modifier_type == 'percent':
                result *= (1.0 + mod.value)
        
        return result
```

**Файлы:**
- `systems/stats.py` - характеристики
- `systems/level_system.py` - уровни и опыт
- `systems/modifiers.py` - модификаторы

---

### НЕДЕЛЯ 2: Система способностей и умений

#### Что реализовать:

**1. Базовые способности:**
```python
class Ability:
    id: str
    name: str
    description: str
    ability_type: str  # 'passive' или 'active'
    
    # Требования
    required_level: int
    required_abilities: List[str]  # Зависимости
    
    # Эффекты
    stat_modifiers: List[StatModifier]
    special_effects: List[str]
    
    # Для активных
    cooldown: int
    stamina_cost: int

class AbilityTree:
    """Дерево способностей"""
    abilities: Dict[str, Ability]
    unlocked: List[str]
    
    def can_unlock(self, ability_id: str) -> bool:
        """Можно ли разблокировать"""
        ability = self.abilities[ability_id]
        
        # Проверка уровня
        if player.level < ability.required_level:
            return False
        
        # Проверка зависимостей
        for req in ability.required_abilities:
            if req not in self.unlocked:
                return False
        
        return True
    
    def unlock(self, ability_id: str):
        """Разблокировать способность"""
        if self.can_unlock(ability_id):
            self.unlocked.append(ability_id)
            self.apply_ability_effects(ability_id)
```

**2. Примеры способностей:**
```python
ABILITIES = {
    # Боевые
    'combat_basic': {
        'name': 'Базовый бой',
        'type': 'passive',
        'effects': [{'stat': 'attack', 'value': 5, 'type': 'flat'}]
    },
    'combat_advanced': {
        'name': 'Продвинутый бой',
        'type': 'passive',
        'required_abilities': ['combat_basic'],
        'required_level': 5,
        'effects': [{'stat': 'attack', 'value': 0.15, 'type': 'percent'}]
    },
    
    # Исследовательские
    'keen_eye': {
        'name': 'Зоркий глаз',
        'type': 'passive',
        'effects': [{'stat': 'perception', 'value': 2, 'type': 'flat'}]
    },
    'trap_sense': {
        'name': 'Чувство ловушек',
        'type': 'passive',
        'required_abilities': ['keen_eye'],
        'effects': [{'special': 'trap_detection_range', 'value': 1}]
    },
    
    # Выживание
    'tough': {
        'name': 'Живучесть',
        'type': 'passive',
        'effects': [{'stat': 'max_health', 'value': 20, 'type': 'flat'}]
    },
    'quick_recovery': {
        'name': 'Быстрое восстановление',
        'type': 'passive',
        'required_abilities': ['tough'],
        'effects': [{'special': 'health_regen', 'value': 1}]
    }
}
```

**Файлы:**
- `systems/abilities.py` - система способностей
- `data/abilities.json` - конфигурация способностей
- `ui/ability_tree_screen.py` - UI дерева способностей

---

### НЕДЕЛЯ 3: Базовый крафт и исследования

#### Что реализовать:

**1. Система рецептов:**
```python
class Recipe:
    id: str
    name: str
    result_item: str
    result_count: int
    
    # Ингредиенты
    ingredients: Dict[str, int]  # item_id: количество
    
    # Требования
    required_level: int
    required_intelligence: int
    required_station: str  # 'workbench', 'laboratory', None
    
    # Знания
    requires_knowledge: List[str]  # Из журнала исследователя

class CraftingSystem:
    known_recipes: List[str]
    
    def can_craft(self, recipe_id: str) -> bool:
        """Можно ли создать предмет"""
        recipe = RECIPES[recipe_id]
        
        # Проверка требований
        if player.level < recipe.required_level:
            return False
        if player.intelligence < recipe.required_intelligence:
            return False
        
        # Проверка ингредиентов
        for item_id, count in recipe.ingredients.items():
            if not player.has_item(item_id, count):
                return False
        
        # Проверка знаний
        for knowledge in recipe.requires_knowledge:
            if knowledge not in research_journal.unlocked_bonuses:
                return False
        
        return True
    
    def craft(self, recipe_id: str):
        """Создать предмет"""
        if self.can_craft(recipe_id):
            recipe = RECIPES[recipe_id]
            
            # Удалить ингредиенты
            for item_id, count in recipe.ingredients.items():
                player.remove_item(item_id, count)
            
            # Создать результат
            player.add_item(recipe.result_item, recipe.result_count)
            
            # Опыт
            player.gain_exp(recipe.exp_reward)
```

**2. Примеры рецептов:**
```python
RECIPES = {
    # Базовые
    'healing_potion': {
        'name': 'Зелье лечения',
        'ingredients': {'herb': 2, 'water': 1},
        'result': 'potion_healing',
        'required_level': 1,
        'required_station': 'laboratory'
    },
    
    # Требуют знания
    'fire_bomb': {
        'name': 'Огненная бомба',
        'ingredients': {'oil': 1, 'cloth': 1, 'gunpowder': 1},
        'result': 'bomb_fire',
        'required_level': 3,
        'required_intelligence': 5,
        'requires_knowledge': ['rat_weakness']  # Узнали что крысы боятся огня
    },
    
    # Улучшение оружия
    'weapon_upgrade_fire': {
        'name': 'Огненное улучшение оружия',
        'ingredients': {'weapon': 1, 'fire_essence': 1},
        'result': 'weapon_fire',
        'required_level': 5,
        'required_station': 'workbench',
        'requires_knowledge': ['fire_mastery']
    }
}
```

**3. Исследование артефактов:**
```python
class ResearchSystem:
    def research_item(self, item_id: str):
        """Исследовать предмет"""
        item = ITEMS[item_id]
        
        # Требует времени и интеллекта
        if player.intelligence < item.research_difficulty:
            return "Слишком сложно для исследования"
        
        # Получить знания
        knowledge = item.research_result
        research_journal.unlock_knowledge(knowledge)
        
        # Возможно разблокировать рецепт
        if knowledge in RECIPE_UNLOCKS:
            recipe_id = RECIPE_UNLOCKS[knowledge]
            crafting_system.learn_recipe(recipe_id)
```

**Файлы:**
- `systems/crafting.py` - система крафта
- `systems/research.py` - исследования
- `data/recipes.json` - рецепты
- `ui/crafting_screen.py` - UI крафта

---

## 🔗 КАК ЭТО СВЯЗЫВАЕТСЯ

### Журнал исследователя → Способности
```python
# Наблюдение за крысами разблокирует способность
if research_journal.enemy_knowledge['rat'].observations >= 10:
    ability_tree.unlock('rat_hunter')  # +25% урона по крысам
```

### Журнал исследователя → Крафт
```python
# Изучение слабости открывает рецепт
if 'rat_weakness' in research_journal.unlocked_bonuses:
    crafting_system.learn_recipe('fire_bomb')  # Эффективно против крыс
```

### Способности → Характеристики
```python
# Способность даёт модификатор
if 'keen_eye' in ability_tree.unlocked:
    player.add_modifier(StatModifier(
        stat='perception',
        value=2,
        type='flat',
        source='keen_eye'
    ))
```

---

## ✅ ПРЕИМУЩЕСТВА НОВОГО ПОРЯДКА

### 1. Логичная последовательность
- Сначала фундамент
- Потом функции на его основе
- Нет "костылей"

### 2. Переиспользование кода
- Характеристики используются везде
- Способности для всех систем
- Крафт для базы и журнала

### 3. Проще тестировать
- Каждая система независима
- Можно тестировать отдельно
- Легче находить баги

### 4. Лучшая архитектура
- Чистый код
- Модульность
- Расширяемость

---

## 📊 СРАВНЕНИЕ ПЛАНОВ

| Аспект | Старый план | Новый план |
|--------|-------------|------------|
| **Длительность** | 14 недель | 16 недель (+2) |
| **Фундамент** | ❌ Нет | ✅ Да (3 недели) |
| **Костыли** | ⚠️ Возможны | ✅ Нет |
| **Архитектура** | ⚠️ Хаотичная | ✅ Чистая |
| **Тестируемость** | ⚠️ Сложная | ✅ Простая |
| **Расширяемость** | ⚠️ Ограничена | ✅ Высокая |

---

## 🎯 РЕКОМЕНДАЦИЯ

**ПРИНЯТЬ НОВЫЙ ПЛАН:**

**Причины:**
1. ✅ Логичная последовательность
2. ✅ Чистая архитектура
3. ✅ Всего +2 недели
4. ✅ Избежим переделок
5. ✅ Лучше для будущего

**Альтернатива (НЕ рекомендуется):**
- Делать "на коленке" для каждой функции
- Потом переделывать
- Технический долг
- Больше времени в итоге

---

## 📝 СЛЕДУЮЩИЕ ШАГИ

### Если согласен с новым планом:
1. Обновить `Integration_Plan_v0.4.0.md`
2. Создать детальный план Этапа 0
3. Начать с системы характеристик

### Если нужны изменения:
- Обсудить какие системы критичны
- Возможно упростить некоторые
- Скорректировать план

---

**Вопрос:** Согласен с новым порядком? Или есть предложения по корректировке?

---

**Версия:** 1.0  
**Дата:** 21.10.2025  
**Статус:** Ожидает утверждения
