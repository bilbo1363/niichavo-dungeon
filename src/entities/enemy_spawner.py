"""
Система спавна врагов
"""
import random
from typing import List
from .enemy import Enemy, EnemyType


class EnemySpawner:
    """Генератор врагов на уровнях"""
    
    def __init__(self):
        """Инициализация генератора"""
        self.enemies: List[Enemy] = []
        
    def spawn_enemies(self, level, floor_number: int) -> None:
        """
        Создать врагов на уровне
        
        Args:
            level: Уровень
            floor_number: Номер этажа
        """
        # Очищаем старых врагов
        self.enemies.clear()
        
        # Определяем количество врагов (больше на глубоких этажах)
        enemy_count = min(2 + floor_number // 3, 8)
        
        # Определяем типы врагов для этого этажа
        possible_types = self._get_enemy_types_for_floor(floor_number)
        
        spawned = 0
        attempts = 0
        max_attempts = enemy_count * 20
        
        while spawned < enemy_count and attempts < max_attempts:
            attempts += 1
            
            # Случайная позиция
            x = random.randint(1, level.width - 2)
            y = random.randint(1, level.height - 2)
            
            # Проверяем что это пол
            if level.get_tile(x, y) != level.TILE_FLOOR:
                continue
                
            # Проверяем что не на входе/выходе
            if (x, y) == level.entrance_pos or (x, y) == level.exit_pos:
                continue
                
            # Проверяем что не слишком близко к входу
            if level.entrance_pos:
                entrance_x, entrance_y = level.entrance_pos
                distance = abs(x - entrance_x) + abs(y - entrance_y)
                if distance < 5:  # Минимум 5 клеток от входа
                    continue
                    
            # Проверяем что не занято другим врагом
            if any(e.x == x and e.y == y and not e.is_dead for e in self.enemies):
                continue
                
            # Выбираем случайный тип врага
            enemy_type = random.choice(possible_types)
            
            # Создаём врага
            enemy = Enemy(enemy_type, x, y)
            self.enemies.append(enemy)
            spawned += 1
            
        print(f"👹 Создано {spawned} врагов на этаже {floor_number}")
        
    def _get_enemy_types_for_floor(self, floor_number: int) -> List[EnemyType]:
        """
        Получить возможные типы врагов для этажа
        
        Args:
            floor_number: Номер этажа
            
        Returns:
            Список типов врагов
        """
        types = []
        
        # Крысы на всех этажах
        types.append(EnemyType.RAT)
        
        # Зомби с 3 этажа
        if floor_number >= 3:
            types.extend([EnemyType.ZOMBIE, EnemyType.ZOMBIE])  # Чаще
            
        # Призраки с 8 этажа
        if floor_number >= 8:
            types.append(EnemyType.GHOST)
            
        # Мутанты с 15 этажа
        if floor_number >= 15:
            types.append(EnemyType.MUTANT)
            
        return types
        
    def update_all(self, dt: float, player_x: int, player_y: int, level) -> List[Enemy]:
        """
        Обновить всех врагов
        
        Args:
            dt: Delta time
            player_x: Позиция игрока X
            player_y: Позиция игрока Y
            level: Уровень
            
        Returns:
            Список врагов которые атакуют
        """
        attacking_enemies = []
        
        for enemy in self.enemies:
            if enemy.is_dead:
                continue
                
            action = enemy.update(dt, player_x, player_y, level)
            if action == "attack":
                attacking_enemies.append(enemy)
                
        return attacking_enemies
        
    def render_all(self, screen, camera_x: int = 0, camera_y: int = 0, fog_of_war=None) -> None:
        """
        Отрисовать всех врагов
        
        Args:
            screen: Поверхность для отрисовки
            camera_x: Смещение камеры по X
            camera_y: Смещение камеры по Y
            fog_of_war: Туман войны
        """
        for enemy in self.enemies:
            enemy.render(screen, camera_x, camera_y, fog_of_war)
            
    def get_enemy_at(self, x: int, y: int) -> Enemy:
        """
        Получить врага на позиции
        
        Args:
            x: Позиция X
            y: Позиция Y
            
        Returns:
            Враг или None
        """
        for enemy in self.enemies:
            if not enemy.is_dead and enemy.x == x and enemy.y == y:
                return enemy
        return None
        
    def get_alive_count(self) -> int:
        """
        Получить количество живых врагов
        
        Returns:
            Количество
        """
        return sum(1 for e in self.enemies if not e.is_dead)
        
    def clear(self) -> None:
        """Очистить всех врагов"""
        self.enemies.clear()


if __name__ == "__main__":
    # Тест спавнера
    spawner = EnemySpawner()
    
    # Тестируем типы врагов для разных этажей
    for floor in [1, 5, 10, 15, 20]:
        types = spawner._get_enemy_types_for_floor(floor)
        print(f"\nЭтаж {floor}: {[t.value for t in types]}")
