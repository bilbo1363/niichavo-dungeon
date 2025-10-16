# Примеры кода на Python для проекта

## 1. Базовые классы

### 1.1 Главный класс Game

```python
# src/core/game.py
import pygame
from typing import Optional
from .state_manager import StateManager, GameState
from ..rendering.renderer import Renderer
from ..input.input_manager import InputManager
from ..world.level_generator import LevelGenerator
from ..entities.player import Player

class Game:
    def __init__(self, width: int = 1200, height: int = 800):
        pygame.init()
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Подземелье НИИЧАВО")
        
        self.clock = pygame.time.Clock()
        self.running = False
        self.fps = 60
        
        # Инициализация систем
        self.state_manager = StateManager()
        self.renderer = Renderer(self.screen)
        self.input_manager = InputManager()
        self.level_generator = LevelGenerator()
        
        # Игровые объекты
        self.player: Optional[Player] = None
        self.current_level = None
        
    def initialize(self) -> None:
        """Инициализация игры"""
        self.player = Player(x=30, y=20)
        self.current_level = self.level_generator.generate(
            floor=1, 
            width=60, 
            height=40
        )
        self.state_manager.set_state(GameState.PLAYING)
        
    def run(self) -> None:
        """Главный игровой цикл"""
        self.running = True
        
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0  # delta time в секундах
            
            # Обработка событий
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    
            # Обработка ввода
            self.input_manager.update(events)
            
            # Обновление игровой логики
            self.update(dt)
            
            # Рендеринг
            self.render()
            
        pygame.quit()
        
    def update(self, dt: float) -> None:
        """Обновление игровой логики"""
        if self.state_manager.current_state == GameState.PLAYING:
            # Обновление игрока
            if self.player:
                self.player.update(dt)
                
            # Обновление уровня
            if self.current_level:
                self.current_level.update(dt)
                
    def render(self) -> None:
        """Отрисовка кадра"""
        self.screen.fill((0, 0, 0))  # Черный фон
        
        if self.current_level and self.player:
            self.renderer.render_level(self.current_level, self.player)
            self.renderer.render_player(self.player)
            
        pygame.display.flip()
```

### 1.2 Класс Player

```python
# src/entities/player.py
from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np

@dataclass
class PlayerStats:
    """Характеристики игрока"""
    health: int = 100
    max_health: int = 100
    endurance: int = 100
    max_endurance: int = 100
    thirst: int = 100
    clarity: int = 100  # Для магии
    
@dataclass
class Item:
    """Предмет в инвентаре"""
    type: str
    durability: Optional[int] = None
    
class Player:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.stats = PlayerStats()
        self.backpack: List[Item] = []
        self.max_backpack_size = 10
        self.steps = 0
        
    def move(self, dx: int, dy: int, level) -> bool:
        """Перемещение игрока"""
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Проверка границ
        if not (0 <= new_x < level.width and 0 <= new_y < level.height):
            return False
            
        # Проверка проходимости
        if level.is_walkable(new_x, new_y):
            self.x = new_x
            self.y = new_y
            self.steps += 1
            self.update_stats()
            return True
            
        return False
        
    def update_stats(self) -> None:
        """Обновление характеристик при ходьбе"""
        if self.steps % 5 == 0:
            self.stats.endurance = max(0, self.stats.endurance - 1)
            
        if self.steps % 25 == 0:
            self.stats.health = max(0, self.stats.health - 1)
            
    def take_damage(self, amount: int) -> None:
        """Получение урона"""
        self.stats.health = max(0, self.stats.health - amount)
        
    def heal(self, amount: int) -> None:
        """Лечение"""
        self.stats.health = min(
            self.stats.max_health, 
            self.stats.health + amount
        )
        
    def add_item(self, item: Item) -> bool:
        """Добавление предмета в инвентарь"""
        if len(self.backpack) < self.max_backpack_size:
            self.backpack.append(item)
            return True
        return False
        
    def update(self, dt: float) -> None:
        """Обновление игрока"""
        pass  # Дополнительная логика
```

## 2. Система генерации уровней с рунами

### 2.1 Состояние этажа

```python
# src/world/floor_state.py
from dataclasses import dataclass
from typing import Optional
import numpy as np

@dataclass
class FloorState:
    """Состояние одного этажа"""
    floor_number: int
    seed: int
    is_stabilized: bool = False
    rune_found: bool = False
    level_data: Optional[np.ndarray] = None
    rune_position: Optional[tuple[int, int]] = None
    
    def stabilize(self, level_data: np.ndarray) -> None:
        """Закрепление уровня после нахождения руны"""
        self.is_stabilized = True
        self.rune_found = True
        self.level_data = level_data.copy()
```

### 2.2 Генератор уровней

```python
# src/world/level_generator.py
import numpy as np
import hashlib
from noise import pnoise2
from typing import Optional
from .floor_state import FloorState

class LevelGenerator:
    def __init__(self, game_id: str = "default"):
        self.game_id = game_id
        self.floors: dict[int, FloorState] = {}
        
    def generate_seed(self, floor: int) -> int:
        """Генерация детерминированного seed для этажа"""
        data = f"{self.game_id}_{floor}".encode()
        hash_obj = hashlib.sha256(data)
        return int.from_bytes(hash_obj.digest()[:4], 'big')
        
    def generate(self, floor: int, width: int, height: int) -> np.ndarray:
        """Генерация уровня"""
        # Проверяем, есть ли уже этот этаж
        if floor not in self.floors:
            seed = self.generate_seed(floor)
            self.floors[floor] = FloorState(
                floor_number=floor,
                seed=seed
            )
            
        floor_state = self.floors[floor]
        
        # Если этаж закреплен - возвращаем сохраненный
        if floor_state.is_stabilized and floor_state.level_data is not None:
            return floor_state.level_data
            
        # Генерируем новый уровень
        np.random.seed(floor_state.seed)
        level = self._generate_level_internal(width, height, floor_state.seed)
        
        # Размещаем руну, если еще не найдена
        if not floor_state.rune_found:
            rune_pos = self._place_rune(level)
            floor_state.rune_position = rune_pos
            
        return level
        
    def _generate_level_internal(
        self, 
        width: int, 
        height: int, 
        seed: int
    ) -> np.ndarray:
        """Внутренняя генерация уровня"""
        level = np.zeros((height, width), dtype=np.uint8)
        
        # Генерация с Perlin noise
        for y in range(height):
            for x in range(width):
                noise_val = pnoise2(
                    x / 10.0, 
                    y / 10.0, 
                    base=seed
                )
                # 0 = пустота, 1 = стена
                level[y, x] = 1 if noise_val > 0.3 else 0
                
        # Генерация границ
        level[0, :] = 1
        level[-1, :] = 1
        level[:, 0] = 1
        level[:, -1] = 1
        
        return level
        
    def _place_rune(self, level: np.ndarray) -> tuple[int, int]:
        """Размещение руны на уровне"""
        height, width = level.shape
        
        # Ищем случайное свободное место
        while True:
            x = np.random.randint(1, width - 1)
            y = np.random.randint(1, height - 1)
            
            if level[y, x] == 0:  # Пустая клетка
                return (x, y)
                
    def stabilize_floor(self, floor: int, level_data: np.ndarray) -> None:
        """Закрепление этажа после нахождения руны"""
        if floor in self.floors:
            self.floors[floor].stabilize(level_data)
```

## 3. Система рун

### 3.1 Класс Rune

```python
# src/entities/rune.py
from enum import Enum
from dataclasses import dataclass

class RuneType(Enum):
    """Типы рун"""
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    EARTH = "earth"
    VOID = "void"
    
@dataclass
class Rune:
    """Руна стабилизации"""
    type: RuneType
    floor: int
    x: int
    y: int
    
    def get_coordinate_hint(self) -> dict:
        """Получить подсказку для координат"""
        hints = {
            RuneType.FIRE: {"axis": "x", "value": self.floor * 2},
            RuneType.ICE: {"axis": "y", "value": self.floor * 3},
            RuneType.LIGHTNING: {"axis": "both", "multiplier": 1.5},
            RuneType.EARTH: {"axis": "x", "offset": 10},
            RuneType.VOID: {"axis": "y", "divider": 2},
        }
        return hints.get(self.type, {})
```

### 3.2 Система управления рунами

```python
# src/world/rune_system.py
from typing import List
from ..entities.rune import Rune, RuneType

class RuneSystem:
    def __init__(self, total_floors: int = 20):
        self.collected_runes: List[Rune] = []
        self.total_runes = total_floors
        
    def collect_rune(self, rune: Rune) -> None:
        """Собрать руну"""
        if rune not in self.collected_runes:
            self.collected_runes.append(rune)
            
    def all_runes_collected(self) -> bool:
        """Проверка, все ли руны собраны"""
        return len(self.collected_runes) >= self.total_runes
        
    def get_progress(self) -> tuple[int, int]:
        """Получить прогресс сбора рун"""
        return (len(self.collected_runes), self.total_runes)
        
    def get_puzzle_data(self) -> dict:
        """Получить данные для загадки"""
        if not self.all_runes_collected():
            return {}
            
        hints = [rune.get_coordinate_hint() for rune in self.collected_runes]
        return {
            'hints': hints,
            'puzzle_type': 'coordinate_cipher',
            'runes': self.collected_runes
        }
```

## 4. Загадка координат

```python
# src/quest/coordinate_puzzle.py
from typing import List, Tuple
from ..entities.rune import Rune, RuneType

class CoordinatePuzzle:
    def __init__(self, runes: List[Rune], map_width: int = 60, map_height: int = 40):
        self.runes = runes
        self.map_width = map_width
        self.map_height = map_height
        self.secret_x, self.secret_y = self._calculate_coordinates()
        
    def _calculate_coordinates(self) -> Tuple[int, int]:
        """Вычисление координат тайной комнаты на основе рун"""
        fire_runes = [r for r in self.runes if r.type == RuneType.FIRE]
        ice_runes = [r for r in self.runes if r.type == RuneType.ICE]
        lightning_runes = [r for r in self.runes if r.type == RuneType.LIGHTNING]
        earth_runes = [r for r in self.runes if r.type == RuneType.EARTH]
        void_runes = [r for r in self.runes if r.type == RuneType.VOID]
        
        # Формула для X координаты
        x = sum(r.floor for r in fire_runes) + sum(r.floor for r in earth_runes)
        x = (x * len(lightning_runes)) % self.map_width
        
        # Формула для Y координаты
        y = sum(r.floor for r in ice_runes)
        if void_runes:
            y = y // len(void_runes)
        y = y % self.map_height
        
        return (max(1, x), max(1, y))
        
    def get_hints(self) -> List[str]:
        """Получить подсказки для игрока"""
        return [
            "Огонь и Земля указывают путь по горизонтали...",
            "Лёд замораживает вертикаль...",
            "Молния усиливает истинный путь...",
            "Пустота делит координаты пополам...",
            f"Всего собрано рун: {len(self.runes)}",
        ]
        
    def check_coordinates(self, x: int, y: int) -> bool:
        """Проверка координат"""
        return x == self.secret_x and y == self.secret_y
        
    def get_distance_hint(self, x: int, y: int) -> str:
        """Подсказка о расстоянии до цели"""
        distance = abs(x - self.secret_x) + abs(y - self.secret_y)
        
        if distance == 0:
            return "Вы нашли тайную комнату!"
        elif distance < 5:
            return "Очень близко!"
        elif distance < 10:
            return "Близко..."
        elif distance < 20:
            return "Тепло"
        else:
            return "Холодно"
```

## 5. Сохранения

```python
# src/data/save_manager.py
import pickle
from pathlib import Path
from typing import Optional
from ..core.game_state import GameState

class SaveManager:
    def __init__(self, save_dir: str = "saves"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
    def save_game(self, game_state: GameState, slot: int) -> bool:
        """Сохранение игры"""
        try:
            save_path = self.save_dir / f"save_{slot}.pkl"
            
            with open(save_path, 'wb') as f:
                pickle.dump(game_state, f)
                
            print(f"Игра сохранена в слот {slot}")
            return True
            
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False
            
    def load_game(self, slot: int) -> Optional[GameState]:
        """Загрузка игры"""
        try:
            save_path = self.save_dir / f"save_{slot}.pkl"
            
            if not save_path.exists():
                print(f"Сохранение {slot} не найдено")
                return None
                
            with open(save_path, 'rb') as f:
                game_state = pickle.load(f)
                
            print(f"Игра загружена из слота {slot}")
            return game_state
            
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return None
            
    def list_saves(self) -> List[int]:
        """Список доступных сохранений"""
        saves = []
        for save_file in self.save_dir.glob("save_*.pkl"):
            slot = int(save_file.stem.split('_')[1])
            saves.append(slot)
        return sorted(saves)
```

## 6. Точка входа

```python
# main.py
from src.core.game import Game

def main():
    game = Game(width=1200, height=800)
    game.initialize()
    game.run()

if __name__ == "__main__":
    main()
```

Эти примеры показывают основную структуру кода на Python для проекта!
