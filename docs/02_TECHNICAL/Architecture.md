# 🏗️ Архитектура проекта

## 📁 Структура проекта

```
Gold/
├── main.py                      # Точка входа
├── requirements.txt             # Зависимости Python
├── src/                         # Исходный код
│   ├── core/                    # Ядро игры
│   │   └── game.py             # Главный игровой цикл
│   ├── entities/                # Игровые сущности
│   │   ├── player.py           # Игрок
│   │   └── stats.py            # Характеристики
│   ├── world/                   # Генерация мира
│   │   ├── level.py            # Уровень
│   │   ├── level_generator.py  # Генератор уровней
│   │   ├── biomes.py           # Биомы
│   │   ├── attic.py            # Чердак (база)
│   │   ├── floor_state.py      # Состояния этажей
│   │   ├── interactive_objects.py # Доски, кости
│   │   ├── niichavo_notes.py   # Записки НИИЧАВО
│   │   ├── traps.py            # Ловушки
│   │   ├── containers.py       # Контейнеры
│   │   └── loot_tables.py      # Таблицы лута
│   ├── items/                   # Система предметов
│   │   ├── item.py             # Предмет
│   │   ├── inventory.py        # Инвентарь
│   │   └── rune.py             # Руны
│   ├── puzzles/                 # Головоломки
│   │   └── riddle.py           # Загадки
│   ├── story/                   # Сюжет
│   │   ├── story_manager.py    # Менеджер сюжета
│   │   └── dialogue_system.py  # Диалоги
│   ├── ui/                      # Интерфейс
│   │   ├── main_menu.py        # Главное меню
│   │   ├── settings_ui.py      # Настройки
│   │   ├── inventory_ui.py     # UI инвентаря
│   │   └── message_log.py      # Лог сообщений
│   ├── graphics/                # Графика
│   │   ├── sprite_manager.py   # Менеджер спрайтов
│   │   ├── player_animation.py # Анимация игрока
│   │   └── particle_system.py  # Частицы
│   ├── audio/                   # Звук
│   │   └── sound_manager.py    # Менеджер звуков
│   ├── input/                   # Ввод
│   │   └── input_manager.py    # Менеджер ввода
│   └── save/                    # Сохранения
│       └── save_manager.py     # Менеджер сохранений
├── assets/                      # Ресурсы
│   ├── music/                  # Музыка (MP3)
│   └── sounds/                 # Звуки (WAV)
├── saves/                       # Файлы сохранений
└── docs/                        # Документация
```

---

## 🔧 Ключевые системы

### 1. Game (core/game.py)
**Главный игровой цикл**
- Управление состояниями (меню, игра, пауза)
- Обработка событий
- Рендеринг
- Координация всех систем

### 2. LevelGenerator (world/level_generator.py)
**Процедурная генерация уровней**
- Алгоритм BSP (Binary Space Partitioning)
- Генерация комнат и коридоров
- Размещение объектов
- Биомы и декорации

### 3. FloorStateManager (world/floor_state.py)
**Управление состояниями этажей**
- Сохранение состояния каждого этажа
- Стабилизация/дестабилизация
- Персистентность объектов

### 4. InteractiveObjectManager (world/interactive_objects.py)
**Интерактивные объекты**
- Доски с записками
- Кости путешественников (лут + записки)
- Генерация и взаимодействие

### 5. NiichavoNoteManager (world/niichavo_notes.py)
**Система записок**
- 100+ записок по биомам
- Случайный выбор для этажа
- Лор и атмосфера

### 6. SoundManager (audio/sound_manager.py)
**Аудио система**
- Музыкальные темы (MP3)
- Звуковые эффекты (WAV)
- Процедурная генерация звуков

### 7. SaveManager (save/save_manager.py)
**Система сохранений**
- Профили игроков
- Сериализация состояния
- Автосохранение

### 8. SpriteManager (graphics/sprite_manager.py)
**Графика**
- Процедурные спрайты
- Анимации
- Загрузка из файлов

---

## 🔄 Поток данных

```
main.py
  └─> Game.__init__()
       ├─> SoundManager
       ├─> SpriteManager
       ├─> SaveManager
       ├─> InputManager
       └─> LevelGenerator
            ├─> BiomeManager
            ├─> InteractiveObjectManager
            ├─> NiichavoNoteManager
            └─> LootTableGenerator
```

---

## 🎮 Игровой цикл

```python
while running:
    # 1. Обработка ввода
    events = pygame.event.get()
    input_manager.update(events)
    
    # 2. Обновление логики
    player.update(dt)
    level.update(dt)
    particle_system.update(dt)
    
    # 3. Рендеринг
    level.render(screen, camera)
    player.render(screen, camera)
    ui.render(screen)
    
    # 4. Обновление экрана
    pygame.display.flip()
```

---

## 💾 Формат сохранений

```json
{
  "player_name": "Игрок",
  "current_floor": 5,
  "current_location": "dungeon",
  "player_stats": {
    "health": 100,
    "max_health": 100,
    "endurance": 80,
    "max_endurance": 100
  },
  "inventory": [...],
  "floor_states": {...}
}
```

---

## 🔌 Зависимости

- **pygame** 2.5+ - Игровой движок
- **numpy** 1.24+ - Генерация звуков, математика
- **Python** 3.11+ - Язык программирования

---

## 📊 Производительность

- **FPS:** 60 (целевой)
- **Размер уровня:** 60x40 тайлов
- **Генерация уровня:** <100ms
- **Память:** ~100-200 MB

---

**Версия документа:** 1.0  
**Дата:** 20.10.2025
