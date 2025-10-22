# Неделя 5-6: Журнал исследователя + Архив смертей

**Дата начала:** 22.10.2025  
**Статус:** 🔄 В процессе  
**Приоритет:** ⭐⭐⭐ Высокий

---

## 🎯 ЦЕЛЬ

Реализовать систему прогрессии через **наблюдение и изучение**, а не через смерти.

### Философия
> "Знание через наблюдение, а не через страдание"

---

## 📋 ТРИ СИСТЕМЫ

### 1. Журнал исследователя (Research Journal)
**Основная система прогрессии**

Игрок получает бонусы за:
- 👁️ Наблюдение за врагами (узнать слабости)
- 🚫 Успешное избегание ловушек (улучшить обнаружение)
- ⚔️ Убийство без урона (мастерство)
- 🗺️ Исследование новых зон
- 📦 Открытие контейнеров
- 📜 Чтение записок

**Награды:**
- Постоянные бонусы к характеристикам
- Разблокировка новых способностей
- Улучшение обнаружения
- Бонусы к крафту

### 2. Архив смертей (Death Archive)
**Только статистика, БЕЗ бонусов**

Записывает:
- Все смерти игрока
- Причины смерти
- Локации смертей
- Статистику забегов

Показывает:
- Мотивационные сообщения
- Лучший забег
- Прогресс по сравнению с предыдущими попытками

**НЕ даёт бонусов!**

### 3. Безсмертные забеги (Deathless Runs)
**Награды за мастерство**

Награды за:
- 5 этажей без смерти → малые бонусы
- 10 этажей без смерти → средние бонусы
- 15 этажей без смерти → большие бонусы
- 20 этажей без смерти → специальная концовка

---

## 🏗️ АРХИТЕКТУРА

### Файлы
```
src/systems/
├── research_journal.py      - Журнал исследователя
├── death_archive.py          - Архив смертей
└── deathless_runs.py         - Безсмертные забеги

src/ui/
├── research_journal_ui.py    - UI журнала
└── death_archive_ui.py       - UI архива
```

### Классы

#### ResearchJournal
```python
@dataclass
class ResearchEntry:
    id: str
    name: str
    description: str
    category: ResearchCategory  # ENEMY, TRAP, LOCATION, ITEM
    progress: int = 0
    max_progress: int = 100
    is_complete: bool = False
    rewards: List[ResearchReward] = field(default_factory=list)

class ResearchJournal:
    def __init__(self):
        self.entries: Dict[str, ResearchEntry] = {}
        self.completed: Set[str] = set()
        self.total_research_points: int = 0
    
    def observe_enemy(self, enemy_type: str, damage_taken: int = 0)
    def avoid_trap(self, trap_type: str)
    def explore_location(self, location_id: str)
    def complete_entry(self, entry_id: str) -> List[ResearchReward]
```

#### DeathArchive
```python
@dataclass
class DeathRecord:
    timestamp: float
    floor: int
    location: str
    cause: str
    enemy_type: Optional[str]
    steps: int
    kills: int
    items_collected: int

class DeathArchive:
    def __init__(self):
        self.deaths: List[DeathRecord] = []
        self.best_run: Optional[DeathRecord] = None
        self.total_deaths: int = 0
    
    def record_death(self, record: DeathRecord)
    def get_statistics(self) -> Dict
    def get_motivational_message(self) -> str
```

#### DeathlessRuns
```python
@dataclass
class DeathlessReward:
    floors_survived: int
    reward_type: str
    reward_value: Any

class DeathlessRuns:
    def __init__(self):
        self.current_streak: int = 0
        self.best_streak: int = 0
        self.rewards_claimed: Set[int] = set()
    
    def floor_completed(self)
    def death_occurred(self)
    def get_available_rewards(self) -> List[DeathlessReward]
    def claim_reward(self, floors: int)
```

---

## 📊 КАТЕГОРИИ ИССЛЕДОВАНИЙ

### 1. Враги (Enemies)
```python
ENEMY_RESEARCH = {
    "rat": {
        "name": "Крыса-мутант",
        "observations": [
            (10, "Базовое поведение"),
            (25, "Паттерны атаки"),
            (50, "Слабые места"),
            (100, "Полное понимание")
        ],
        "rewards": [
            StatModifier(ModifierType.FLAT, "attack", 1),
            StatModifier(ModifierType.PERCENTAGE, "damage_vs_rats", 10)
        ]
    },
    "ghost": {...},
    "mutant": {...}
}
```

### 2. Ловушки (Traps)
```python
TRAP_RESEARCH = {
    "spike_trap": {
        "name": "Шипованная ловушка",
        "avoidances": [
            (5, "Первое избегание"),
            (15, "Опытное избегание"),
            (30, "Мастерское избегание")
        ],
        "rewards": [
            StatModifier(ModifierType.FLAT, "perception", 1),
            StatModifier(ModifierType.PERCENTAGE, "trap_detection", 15)
        ]
    }
}
```

### 3. Локации (Locations)
```python
LOCATION_RESEARCH = {
    "floor_1": {
        "name": "Первый этаж",
        "exploration": [
            (25, "Частичное исследование"),
            (50, "Половина карты"),
            (75, "Почти всё"),
            (100, "Полное исследование")
        ],
        "rewards": [
            StatModifier(ModifierType.FLAT, "luck", 1)
        ]
    }
}
```

---

## 🎨 UI ДИЗАЙН

### Research Journal UI
```
┌─────────────────────────────────────────┐
│  📖 ЖУРНАЛ ИССЛЕДОВАТЕЛЯ                │
├─────────────────────────────────────────┤
│                                          │
│  [Враги] [Ловушки] [Локации] [Предметы] │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │ 🐀 Крыса-мутант        [██░░] 50%│   │
│  │ Изучено: Паттерны атаки          │   │
│  │ Награды: +1 Атака                │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │ 👻 Призрак             [░░░░]  0%│   │
│  │ Не изучен                        │   │
│  └──────────────────────────────────┘   │
│                                          │
│  Очки исследований: 127                 │
│  Завершено записей: 8/45                │
└─────────────────────────────────────────┘
```

### Death Archive UI
```
┌─────────────────────────────────────────┐
│  💀 АРХИВ СМЕРТЕЙ                        │
├─────────────────────────────────────────┤
│                                          │
│  Всего смертей: 23                      │
│  Лучший забег: Этаж 8                   │
│                                          │
│  📊 СТАТИСТИКА                           │
│  ├─ Крысы: 12 смертей                   │
│  ├─ Ловушки: 7 смертей                  │
│  ├─ Призраки: 3 смерти                  │
│  └─ Голод: 1 смерть                     │
│                                          │
│  💬 "Каждая смерть - урок.              │
│      Ты уже прошёл дальше!"             │
│                                          │
│  🏆 БЕЗСМЕРТНЫЕ ЗАБЕГИ                  │
│  ├─ 5 этажей: ✅ Получено               │
│  ├─ 10 этажей: ⏳ Текущий: 3/10         │
│  ├─ 15 этажей: 🔒 Недоступно           │
│  └─ 20 этажей: 🔒 Недоступно           │
└─────────────────────────────────────────┘
```

---

## 📝 ПЛАН РЕАЛИЗАЦИИ

### День 1-2: Research Journal (40%)
- [ ] ResearchEntry, ResearchCategory
- [ ] ResearchJournal класс
- [ ] Предустановленные исследования
- [ ] Система наблюдений
- [ ] Система наград
- [ ] 10 автотестов

### День 3-4: Death Archive (20%)
- [ ] DeathRecord класс
- [ ] DeathArchive класс
- [ ] Статистика смертей
- [ ] Мотивационные сообщения
- [ ] 5 автотестов

### День 5-6: Deathless Runs (20%)
- [ ] DeathlessRuns класс
- [ ] Система наград
- [ ] Отслеживание стриков
- [ ] 5 автотестов

### День 7-9: UI (15%)
- [ ] ResearchJournalUI
- [ ] DeathArchiveUI
- [ ] Интеграция с game.py
- [ ] Демо-приложения

### День 10-12: Интеграция (5%)
- [ ] Интеграция с боевой системой
- [ ] Интеграция с системой ловушек
- [ ] Сохранение/загрузка
- [ ] Финальное тестирование

---

## 🎯 КРИТЕРИИ УСПЕХА

### Функциональность
- ✅ Журнал отслеживает наблюдения
- ✅ Архив записывает смерти
- ✅ Безсмертные забеги дают награды
- ✅ UI интуитивно понятен
- ✅ Сохранение/загрузка работает

### Баланс
- ✅ Награды мотивируют исследование
- ✅ Смерти не дают преимуществ
- ✅ Безсмертные забеги достижимы

### UX
- ✅ Игрок понимает систему
- ✅ Прогресс виден и ощутим
- ✅ Мотивация избегать смертей

---

## 📚 ССЫЛКИ

- `Week1-2_DeathArchive_REVISED.md` - Пересмотренная концепция
- `plan.md` - Общий план разработки

---

**Начинаем реализацию! 🚀**
