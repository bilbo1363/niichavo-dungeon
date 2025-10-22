"""
Система боя
"""
import pygame
import random
from typing import Optional


class CombatSystem:
    """Система боя между игроком и врагами"""
    
    def __init__(self):
        """Инициализация боевой системы"""
        self.player_attack_cooldown = 0.0
        self.player_attack_delay = 0.5  # Секунд между атаками игрока
        
        # Визуальные эффекты
        self.damage_numbers = []  # [(x, y, damage, timer, is_player)]
        
        # Ссылка на систему частиц (будет установлена извне)
        self.particle_system = None
        
        # Ссылка на лог сообщений (будет установлена извне)
        self.message_log = None
        
    def update(self, dt: float) -> None:
        """
        Обновление боевой системы
        
        Args:
            dt: Delta time
        """
        # Обновляем кулдаун атаки игрока
        self.player_attack_cooldown = max(0, self.player_attack_cooldown - dt)
        
        # Обновляем числа урона
        self.damage_numbers = [
            (x, y, dmg, timer - dt, is_player) 
            for x, y, dmg, timer, is_player in self.damage_numbers 
            if timer > 0
        ]
        
    def player_attack(self, player, level):
        """
        Атака игрока
        
        Args:
            player: Игрок
            level: Уровень
            
        Returns:
            Список убитых врагов (для выдачи опыта)
        """
        # Проверяем кулдаун
        if self.player_attack_cooldown > 0:
            return []
            
        # Проверяем что есть оружие
        if not player.inventory.equipped_weapon:
            print("❌ Нет экипированного оружия!")
            return []
            
        # Определяем направление атаки (последнее направление движения)
        attack_x = player.x
        attack_y = player.y
        
        # Ищем врагов в соседних клетках
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        attacked = False
        killed_enemies = []  # Список убитых врагов для выдачи опыта
        
        for dx, dy in directions:
            check_x = player.x + dx
            check_y = player.y + dy
            
            enemy = level.enemy_spawner.get_enemy_at(check_x, check_y)
            if enemy and not enemy.is_dead:
                # Вычисляем урон
                base_damage = player.inventory.equipped_weapon.damage
                damage = self._calculate_damage(base_damage)
                
                # Наносим урон
                is_dead = enemy.take_damage(damage)
                
                # Если враг умер - добавляем в список убитых
                if is_dead:
                    killed_enemies.append(enemy)
                
                # Добавляем визуальный эффект
                self._add_damage_number(check_x, check_y, damage)
                
                # Эффект частиц
                if self.particle_system:
                    effect_x = check_x * 32 + 16
                    effect_y = check_y * 32 + 16
                    if is_dead:
                        # Большой эффект при смерти
                        self.particle_system.emit(effect_x, effect_y, 30, "blood")
                    else:
                        # Маленький эффект при попадании
                        self.particle_system.emit(effect_x, effect_y, 10, "blood")
                
                # Сообщение в лог
                if self.message_log:
                    if is_dead:
                        self.message_log.combat(f"Убили {enemy.enemy_type.value}!")
                    else:
                        self.message_log.combat(f"Атаковали {enemy.enemy_type.value}: -{damage} HP")
                
                print(f"⚔️  Вы атаковали {enemy.enemy_type.value} и нанесли {damage} урона!")
                attacked = True
                
        if attacked:
            self.player_attack_cooldown = self.player_attack_delay
            return killed_enemies
        else:
            print("❌ Рядом нет врагов!")
            return []
            
    def enemy_attack(self, enemy, player) -> None:
        """
        Атака врага
        
        Args:
            enemy: Враг
            player: Игрок
        """
        # Вычисляем урон
        damage = self._calculate_damage(enemy.stats.damage)
        
        # Наносим урон игроку
        player.stats.health -= damage
        
        # Добавляем визуальный эффект
        self._add_damage_number(player.x, player.y, damage, is_player=True)
        
        # Эффект частиц
        if self.particle_system:
            effect_x = player.x * 32 + 16
            effect_y = player.y * 32 + 16
            self.particle_system.emit(effect_x, effect_y, 8, "blood")
        
        # Сообщение в лог
        if self.message_log:
            self.message_log.combat(f"{enemy.enemy_type.value.capitalize()} атаковал! -{damage} HP")
        
        print(f"💥 {enemy.enemy_type.value.capitalize()} атаковал вас! Урон: {damage}")
        
        # Проверяем смерть игрока
        if player.stats.health <= 0:
            player.stats.health = 0
            print("💀 ВЫ ПОГИБЛИ!")
            
    def _calculate_damage(self, base_damage: int) -> int:
        """
        Вычислить урон с учётом случайности
        
        Args:
            base_damage: Базовый урон
            
        Returns:
            Итоговый урон
        """
        # ±20% вариация
        variation = random.uniform(0.8, 1.2)
        return max(1, int(base_damage * variation))
        
    def _add_damage_number(self, x: int, y: int, damage: int, is_player: bool = False) -> None:
        """
        Добавить визуальное число урона
        
        Args:
            x: Позиция X
            y: Позиция Y
            damage: Урон
            is_player: Урон по игроку
        """
        self.damage_numbers.append((x, y, damage, 1.0, is_player))
        
    def render_damage_numbers(self, screen: pygame.Surface, camera_x: int, camera_y: int) -> None:
        """
        Отрисовка чисел урона
        
        Args:
            screen: Поверхность для отрисовки
            camera_x: Смещение камеры X
            camera_y: Смещение камеры Y
        """
        font = pygame.font.Font(None, 32)
        
        for x, y, damage, timer, is_player in self.damage_numbers:
            # Вычисляем позицию на экране
            screen_x = x * 32 - camera_x + 16
            screen_y = y * 32 - camera_y - int(timer * 20)  # Поднимается вверх
            
            # Цвет (красный для игрока, белый для врагов)
            color = (255, 100, 100) if is_player else (255, 255, 255)
            
            # Прозрачность
            alpha = int(255 * timer)
            
            # Рендерим текст
            text = font.render(f"-{damage}", True, color)
            text.set_alpha(alpha)
            screen.blit(text, (screen_x, screen_y))


if __name__ == "__main__":
    # Тест боевой системы
    combat = CombatSystem()
    print("Боевая система инициализирована")
    
    # Тест вычисления урона
    for i in range(5):
        damage = combat._calculate_damage(10)
        print(f"Урон {i+1}: {damage}")
