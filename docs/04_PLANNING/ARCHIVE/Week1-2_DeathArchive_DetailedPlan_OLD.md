# Детальный план: Архив смертей
## Недели 1-2 разработки v0.4.0

**Приоритет:** ⭐⭐⭐ Критический  
**Сложность:** Низкая  
**Ценность:** Очень высокая  
**Срок:** 14 дней

---

## 🎯 ЦЕЛЬ

Создать систему, которая превращает смерть из наказания в обучение:
- Записывает каждую смерть игрока
- Даёт бонусы за повторные смерти от одного источника
- Мотивирует исследование и эксперименты
- Добавляет мета-прогрессию

---

## 📁 СТРУКТУРА ФАЙЛОВ

```
systems/
  └── death_archive.py          # Основная система (новый)

ui/
  └── death_archive_screen.py   # UI архива (новый)

data/
  └── death_bonuses.json         # Конфигурация бонусов (новый)

# Изменения в существующих:
game_state.py                    # Добавить death_archive
player.py                        # Интеграция бонусов
```

---

## 📝 ДЕНЬ 1-2: Проектирование и структура данных

### Создать: `systems/death_archive.py`

```python
"""
Система архива смертей
Записывает все смерти игрока и даёт бонусы за обучение
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import json


@dataclass
class DeathRecord:
    """Запись об одной смерти"""
    cause: str              # "enemy_rat", "trap_spike", "starvation"
    cause_category: str     # "enemy", "trap", "environment"
    floor: int
    location: str           # Название комнаты/зоны
    timestamp: datetime
    player_level: int
    player_health: int
    circumstances: Dict     # Дополнительная информация
    
    def to_dict(self) -> dict:
        """Сериализация для сохранения"""
        return {
            'cause': self.cause,
            'cause_category': self.cause_category,
            'floor': self.floor,
            'location': self.location,
            'timestamp': self.timestamp.isoformat(),
            'player_level': self.player_level,
            'player_health': self.player_health,
            'circumstances': self.circumstances
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DeathRecord':
        """Десериализация"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class DeathArchive:
    """Архив всех смертей игрока"""
    
    def __init__(self):
        self.deaths: List[DeathRecord] = []
        self.death_counts: Dict[str, int] = {}  # причина: количество
        self.unlocked_bonuses: List[str] = []
        self.total_deaths: int = 0
        
        # Загрузить конфигурацию бонусов
        self.bonus_config = self.load_bonus_config()
    
    def record_death(self, 
                     cause: str,
                     cause_category: str,
                     floor: int,
                     location: str,
                     player_level: int,
                     player_health: int,
                     circumstances: Dict = None) -> Optional[Dict]:
        """
        Записать смерть и проверить разблокировку бонусов
        
        Returns:
            Dict с информацией о разблокированном бонусе или None
        """
        # Создать запись
        record = DeathRecord(
            cause=cause,
            cause_category=cause_category,
            floor=floor,
            location=location,
            timestamp=datetime.now(),
            player_level=player_level,
            player_health=player_health,
            circumstances=circumstances or {}
        )
        
        # Добавить в архив
        self.deaths.append(record)
        self.total_deaths += 1
        
        # Обновить счётчик
        if cause not in self.death_counts:
            self.death_counts[cause] = 0
        self.death_counts[cause] += 1
        
        # Проверить разблокировку бонусов
        return self.check_bonus_unlock(cause)
    
    def check_bonus_unlock(self, cause: str) -> Optional[Dict]:
        """Проверить, разблокирован ли новый бонус"""
        if cause not in self.bonus_config:
            return None
        
        count = self.death_counts[cause]
        bonuses = self.bonus_config[cause]
        
        # Проверить каждый порог
        for threshold, bonus_data in bonuses.items():
            threshold_int = int(threshold)
            bonus_id = f"{cause}_{threshold}"
            
            if count == threshold_int and bonus_id not in self.unlocked_bonuses:
                self.unlocked_bonuses.append(bonus_id)
                return {
                    'cause': cause,
                    'threshold': threshold_int,
                    'bonus': bonus_data,
                    'message': self.get_unlock_message(cause, threshold_int, bonus_data)
                }
        
        return None
    
    def get_unlock_message(self, cause: str, threshold: int, bonus: Dict) -> str:
        """Сообщение о разблокировке бонуса"""
        cause_names = {
            'enemy_rat': 'крыс',
            'enemy_zombie': 'зомби',
            'trap_spike': 'шипованных ловушек',
            'trap_arrow': 'стреловых ловушек',
            'starvation': 'голода',
            'fall_damage': 'падений'
        }
        
        bonus_descriptions = {
            'resistance': f"+{int(bonus['value']*100)}% сопротивления",
            'damage_bonus': f"+{int(bonus['value']*100)}% урона",
            'detection_range': f"+{bonus['value']} к обнаружению",
            'immunity_chance': f"{int(bonus['value']*100)}% шанс иммунитета"
        }
        
        cause_name = cause_names.get(cause, cause)
        bonus_desc = bonus_descriptions.get(bonus['type'], str(bonus))
        
        return f"Погибнув от {cause_name} {threshold} раз, вы получили: {bonus_desc}"
    
    def get_active_bonuses(self) -> Dict[str, List[Dict]]:
        """Получить все активные бонусы игрока"""
        active_bonuses = {}
        
        for bonus_id in self.unlocked_bonuses:
            # Парсинг ID: "enemy_rat_3"
            parts = bonus_id.rsplit('_', 1)
            if len(parts) != 2:
                continue
            
            cause = parts[0]
            threshold = parts[1]
            
            if cause in self.bonus_config and threshold in self.bonus_config[cause]:
                bonus_data = self.bonus_config[cause][threshold]
                
                if cause not in active_bonuses:
                    active_bonuses[cause] = []
                
                active_bonuses[cause].append(bonus_data)
        
        return active_bonuses
    
    def get_statistics(self) -> Dict:
        """Статистика смертей"""
        if not self.deaths:
            return {
                'total_deaths': 0,
                'most_common_cause': None,
                'deadliest_floor': None,
                'death_by_category': {}
            }
        
        # Самая частая причина
        most_common = max(self.death_counts.items(), key=lambda x: x[1])
        
        # Самый опасный этаж
        floor_deaths = {}
        for death in self.deaths:
            floor_deaths[death.floor] = floor_deaths.get(death.floor, 0) + 1
        deadliest_floor = max(floor_deaths.items(), key=lambda x: x[1])
        
        # По категориям
        category_deaths = {}
        for death in self.deaths:
            cat = death.cause_category
            category_deaths[cat] = category_deaths.get(cat, 0) + 1
        
        return {
            'total_deaths': self.total_deaths,
            'most_common_cause': most_common,
            'deadliest_floor': deadliest_floor,
            'death_by_category': category_deaths,
            'unique_causes': len(self.death_counts),
            'unlocked_bonuses_count': len(self.unlocked_bonuses)
        }
    
    def load_bonus_config(self) -> Dict:
        """Загрузить конфигурацию бонусов из JSON"""
        try:
            with open('data/death_bonuses.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Вернуть дефолтную конфигурацию
            return self.get_default_bonus_config()
    
    def get_default_bonus_config(self) -> Dict:
        """Дефолтная конфигурация бонусов"""
        return {
            'enemy_rat': {
                '3': {'type': 'damage_bonus', 'value': 0.2},
                '5': {'type': 'resistance', 'value': 0.15},
                '10': {'type': 'damage_bonus', 'value': 0.5}
            },
            'enemy_zombie': {
                '3': {'type': 'resistance', 'value': 0.1},
                '5': {'type': 'damage_bonus', 'value': 0.25},
                '10': {'type': 'resistance', 'value': 0.3}
            },
            'trap_spike': {
                '3': {'type': 'detection_range', 'value': 1},
                '5': {'type': 'immunity_chance', 'value': 0.3},
                '10': {'type': 'immunity_chance', 'value': 0.6}
            },
            'trap_arrow': {
                '3': {'type': 'detection_range', 'value': 1},
                '5': {'type': 'immunity_chance', 'value': 0.25}
            },
            'starvation': {
                '3': {'type': 'hunger_rate', 'value': 0.9},
                '5': {'type': 'hunger_rate', 'value': 0.8},
                '10': {'type': 'hunger_rate', 'value': 0.7}
            },
            'fall_damage': {
                '3': {'type': 'fall_resistance', 'value': 0.3},
                '5': {'type': 'fall_resistance', 'value': 0.5}
            }
        }
    
    def save(self) -> dict:
        """Сохранить архив"""
        return {
            'deaths': [d.to_dict() for d in self.deaths],
            'death_counts': self.death_counts,
            'unlocked_bonuses': self.unlocked_bonuses,
            'total_deaths': self.total_deaths
        }
    
    def load(self, data: dict):
        """Загрузить архив"""
        self.deaths = [DeathRecord.from_dict(d) for d in data.get('deaths', [])]
        self.death_counts = data.get('death_counts', {})
        self.unlocked_bonuses = data.get('unlocked_bonuses', [])
        self.total_deaths = data.get('total_deaths', 0)
```

---

## 📝 ДЕНЬ 3-5: Интеграция с игрой

### Изменить: `game_state.py`

```python
# Добавить в класс GameState

from systems.death_archive import DeathArchive

class GameState:
    def __init__(self):
        # ... существующий код ...
        
        # Новое: Архив смертей
        self.death_archive = DeathArchive()
    
    def handle_player_death(self, cause: str, cause_category: str):
        """Обработка смерти игрока"""
        # Записать в архив
        bonus_unlocked = self.death_archive.record_death(
            cause=cause,
            cause_category=cause_category,
            floor=self.current_floor,
            location=self.current_location_name,
            player_level=self.player.level,
            player_health=self.player.health,
            circumstances={
                'enemies_nearby': len(self.get_nearby_enemies()),
                'items_in_inventory': len(self.player.inventory)
            }
        )
        
        # Если разблокирован бонус - показать уведомление
        if bonus_unlocked:
            self.show_bonus_unlock_notification(bonus_unlocked)
        
        # ... остальная логика смерти ...
    
    def save_game(self):
        """Сохранение игры"""
        save_data = {
            # ... существующие данные ...
            'death_archive': self.death_archive.save()
        }
        # ... сохранение ...
    
    def load_game(self, save_data):
        """Загрузка игры"""
        # ... существующая загрузка ...
        
        if 'death_archive' in save_data:
            self.death_archive.load(save_data['death_archive'])
```

---

## 📝 ДЕНЬ 6-8: Применение бонусов

### Изменить: `player.py`

```python
class Player:
    def __init__(self, game_state):
        # ... существующий код ...
        self.game_state = game_state
    
    def get_damage_multiplier(self, enemy_type: str) -> float:
        """Получить множитель урона с учётом бонусов архива"""
        multiplier = 1.0
        
        # Получить бонусы из архива
        active_bonuses = self.game_state.death_archive.get_active_bonuses()
        
        # Проверить бонусы для этого типа врага
        cause = f"enemy_{enemy_type}"
        if cause in active_bonuses:
            for bonus in active_bonuses[cause]:
                if bonus['type'] == 'damage_bonus':
                    multiplier += bonus['value']
        
        return multiplier
    
    def get_resistance(self, damage_source: str) -> float:
        """Получить сопротивление урону"""
        resistance = 0.0
        
        active_bonuses = self.game_state.death_archive.get_active_bonuses()
        
        if damage_source in active_bonuses:
            for bonus in active_bonuses[damage_source]:
                if bonus['type'] == 'resistance':
                    resistance += bonus['value']
        
        return min(resistance, 0.75)  # Максимум 75% сопротивления
    
    def get_trap_detection_range(self) -> int:
        """Дальность обнаружения ловушек"""
        base_range = 0
        
        active_bonuses = self.game_state.death_archive.get_active_bonuses()
        
        # Проверить бонусы от ловушек
        for trap_type in ['trap_spike', 'trap_arrow']:
            if trap_type in active_bonuses:
                for bonus in active_bonuses[trap_type]:
                    if bonus['type'] == 'detection_range':
                        base_range += bonus['value']
        
        return base_range
```

---

## 📝 ДЕНЬ 9-10: UI архива

### Создать: `ui/death_archive_screen.py`

```python
"""
UI для просмотра архива смертей
Доступен на чердаке
"""

import pygame
from typing import List, Dict


class DeathArchiveScreen:
    """Экран архива смертей"""
    
    def __init__(self, screen, death_archive):
        self.screen = screen
        self.archive = death_archive
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)
        
        self.selected_tab = 'statistics'  # statistics, deaths, bonuses
        self.scroll_offset = 0
    
    def draw(self):
        """Отрисовка экрана"""
        self.screen.fill((20, 20, 30))
        
        # Заголовок
        self.draw_title()
        
        # Вкладки
        self.draw_tabs()
        
        # Содержимое в зависимости от вкладки
        if self.selected_tab == 'statistics':
            self.draw_statistics()
        elif self.selected_tab == 'deaths':
            self.draw_death_list()
        elif self.selected_tab == 'bonuses':
            self.draw_bonuses()
        
        # Подсказки управления
        self.draw_controls()
    
    def draw_title(self):
        """Заголовок"""
        title = self.title_font.render("АРХИВ СМЕРТЕЙ", True, (200, 200, 200))
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 40))
        self.screen.blit(title, title_rect)
        
        # Подзаголовок
        subtitle_text = f"Всего смертей: {self.archive.total_deaths}"
        subtitle = self.font.render(subtitle_text, True, (150, 150, 150))
        subtitle_rect = subtitle.get_rect(center=(self.screen.get_width() // 2, 70))
        self.screen.blit(subtitle, subtitle_rect)
    
    def draw_tabs(self):
        """Вкладки"""
        tabs = [
            ('statistics', 'СТАТИСТИКА'),
            ('deaths', 'СПИСОК СМЕРТЕЙ'),
            ('bonuses', 'БОНУСЫ')
        ]
        
        tab_width = 200
        tab_height = 40
        start_x = (self.screen.get_width() - len(tabs) * tab_width) // 2
        y = 100
        
        for i, (tab_id, tab_name) in enumerate(tabs):
            x = start_x + i * tab_width
            
            # Цвет вкладки
            if tab_id == self.selected_tab:
                color = (60, 60, 80)
                text_color = (255, 255, 255)
            else:
                color = (40, 40, 50)
                text_color = (150, 150, 150)
            
            # Прямоугольник вкладки
            pygame.draw.rect(self.screen, color, (x, y, tab_width, tab_height))
            pygame.draw.rect(self.screen, (100, 100, 100), (x, y, tab_width, tab_height), 2)
            
            # Текст
            text = self.font.render(tab_name, True, text_color)
            text_rect = text.get_rect(center=(x + tab_width // 2, y + tab_height // 2))
            self.screen.blit(text, text_rect)
    
    def draw_statistics(self):
        """Вкладка статистики"""
        stats = self.archive.get_statistics()
        
        y = 160
        x = 100
        line_height = 30
        
        # Общая статистика
        lines = [
            f"Всего смертей: {stats['total_deaths']}",
            f"Уникальных причин: {stats['unique_causes']}",
            f"Разблокировано бонусов: {stats['unlocked_bonuses_count']}",
            "",
            f"Самая частая причина: {stats['most_common_cause'][0] if stats['most_common_cause'] else 'N/A'}",
            f"  (погибли {stats['most_common_cause'][1]} раз)" if stats['most_common_cause'] else "",
            "",
            f"Самый опасный этаж: {stats['deadliest_floor'][0] if stats['deadliest_floor'] else 'N/A'}",
            f"  ({stats['deadliest_floor'][1]} смертей)" if stats['deadliest_floor'] else "",
            "",
            "Смерти по категориям:"
        ]
        
        for line in lines:
            text = self.font.render(line, True, (200, 200, 200))
            self.screen.blit(text, (x, y))
            y += line_height
        
        # Категории
        for category, count in stats['death_by_category'].items():
            text = self.font.render(f"  {category}: {count}", True, (180, 180, 180))
            self.screen.blit(text, (x + 20, y))
            y += line_height
    
    def draw_death_list(self):
        """Список всех смертей"""
        y = 160
        x = 50
        line_height = 25
        
        # Последние 15 смертей
        recent_deaths = list(reversed(self.archive.deaths[-15:]))
        
        for i, death in enumerate(recent_deaths):
            # Формат: "Смерть #15: Крысы (Этаж 3, Лаборатория)"
            death_num = self.archive.total_deaths - i
            text_str = f"#{death_num}: {death.cause} (Этаж {death.floor}, {death.location})"
            
            text = self.font.render(text_str, True, (200, 180, 180))
            self.screen.blit(text, (x, y))
            y += line_height
    
    def draw_bonuses(self):
        """Активные бонусы"""
        active_bonuses = self.archive.get_active_bonuses()
        
        y = 160
        x = 100
        line_height = 30
        
        if not active_bonuses:
            text = self.font.render("Нет активных бонусов", True, (150, 150, 150))
            self.screen.blit(text, (x, y))
            return
        
        for cause, bonuses in active_bonuses.items():
            # Заголовок категории
            title = self.font.render(f"{cause}:", True, (220, 220, 220))
            self.screen.blit(title, (x, y))
            y += line_height
            
            # Бонусы
            for bonus in bonuses:
                bonus_text = f"  • {bonus['type']}: {bonus['value']}"
                text = self.font.render(bonus_text, True, (180, 200, 180))
                self.screen.blit(text, (x + 20, y))
                y += line_height
            
            y += 10  # Отступ между категориями
    
    def draw_controls(self):
        """Подсказки управления"""
        controls = "[TAB] Переключить вкладку  [ESC] Выход"
        text = self.font.render(controls, True, (120, 120, 120))
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, 
                                          self.screen.get_height() - 30))
        self.screen.blit(text, text_rect)
    
    def handle_input(self, event):
        """Обработка ввода"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.switch_tab()
            elif event.key == pygame.K_ESCAPE:
                return 'exit'
        
        return None
    
    def switch_tab(self):
        """Переключение вкладки"""
        tabs = ['statistics', 'deaths', 'bonuses']
        current_index = tabs.index(self.selected_tab)
        self.selected_tab = tabs[(current_index + 1) % len(tabs)]
```

---

## 📝 ДЕНЬ 11-14: Тестирование и полировка

### Тестовые сценарии:

**1. Запись смертей:**
- [ ] Смерть от врага записывается
- [ ] Смерть от ловушки записывается
- [ ] Смерть от голода записывается
- [ ] Все данные сохраняются корректно

**2. Разблокировка бонусов:**
- [ ] Бонус разблокируется после 3 смертей
- [ ] Бонус разблокируется после 5 смертей
- [ ] Бонус разблокируется после 10 смертей
- [ ] Уведомление показывается корректно

**3. Применение бонусов:**
- [ ] Урон увеличивается против нужного врага
- [ ] Сопротивление работает
- [ ] Обнаружение ловушек работает
- [ ] Бонусы сохраняются между сессиями

**4. UI:**
- [ ] Архив открывается на чердаке
- [ ] Все вкладки работают
- [ ] Статистика отображается корректно
- [ ] Список смертей корректен
- [ ] Бонусы отображаются правильно

**5. Сохранение/загрузка:**
- [ ] Архив сохраняется
- [ ] Архив загружается
- [ ] Бонусы сохраняются
- [ ] Статистика корректна после загрузки

---

## 📊 КОНФИГУРАЦИЯ БОНУСОВ

### Создать: `data/death_bonuses.json`

```json
{
  "enemy_rat": {
    "3": {
      "type": "damage_bonus",
      "value": 0.2,
      "description": "+20% урона по крысам"
    },
    "5": {
      "type": "resistance",
      "value": 0.15,
      "description": "+15% сопротивления урону от крыс"
    },
    "10": {
      "type": "damage_bonus",
      "value": 0.5,
      "description": "+50% урона по крысам"
    }
  },
  "enemy_zombie": {
    "3": {
      "type": "resistance",
      "value": 0.1,
      "description": "+10% сопротивления урону от зомби"
    },
    "5": {
      "type": "damage_bonus",
      "value": 0.25,
      "description": "+25% урона по зомби"
    },
    "10": {
      "type": "resistance",
      "value": 0.3,
      "description": "+30% сопротивления урону от зомби"
    }
  },
  "trap_spike": {
    "3": {
      "type": "detection_range",
      "value": 1,
      "description": "+1 клетка к обнаружению ловушек"
    },
    "5": {
      "type": "immunity_chance",
      "value": 0.3,
      "description": "30% шанс избежать урона от шипов"
    },
    "10": {
      "type": "immunity_chance",
      "value": 0.6,
      "description": "60% шанс избежать урона от шипов"
    }
  },
  "starvation": {
    "3": {
      "type": "hunger_rate",
      "value": 0.9,
      "description": "Голод наступает на 10% медленнее"
    },
    "5": {
      "type": "hunger_rate",
      "value": 0.8,
      "description": "Голод наступает на 20% медленнее"
    },
    "10": {
      "type": "hunger_rate",
      "value": 0.7,
      "description": "Голод наступает на 30% медленнее"
    }
  }
}
```

---

## ✅ КРИТЕРИИ ЗАВЕРШЕНИЯ

### Обязательно:
- [x] Класс DeathArchive реализован
- [x] Запись всех смертей работает
- [x] Система бонусов функциональна
- [x] UI архива создан
- [x] Интеграция с game_state
- [x] Сохранение/загрузка работает
- [x] Минимум 6 типов смертей с бонусами

### Желательно:
- [ ] 10+ типов смертей
- [ ] Красивые уведомления о бонусах
- [ ] Звуковые эффекты
- [ ] Анимации в UI

---

## 🎯 СЛЕДУЮЩИЙ ШАГ

После завершения архива смертей → **Неделя 3: Режимы сложности**

---

**Версия:** 1.0  
**Дата:** 21.10.2025  
**Статус:** Готов к реализации
