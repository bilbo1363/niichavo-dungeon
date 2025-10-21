"""
Демонстрация UI дерева способностей
Версия: 0.4.0
Этап 0, Неделя 2, День 3
"""

import pygame
import sys
import os

# Добавляем путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.systems.abilities import AbilityTree
from src.systems.ability_presets import create_all_abilities
from src.systems.stats import PlayerStats
from src.systems.level_system import LevelSystem
from src.systems.modifiers import ModifierManager
from src.ui.ability_tree_ui import AbilityTreeUI


def main():
    """Главная функция демонстрации"""
    # Инициализация Pygame
    pygame.init()
    
    # Создаём окно
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Дерево способностей - Демо")
    clock = pygame.time.Clock()
    
    # Создаём игровые системы
    player_stats = PlayerStats()
    level_system = LevelSystem(level=5, experience=0)
    level_system.ability_points = 10  # Даём очки для тестирования
    
    modifier_manager = ModifierManager()
    
    # Создаём дерево способностей
    abilities = create_all_abilities()
    ability_tree = AbilityTree(abilities, modifier_manager)
    
    # Создаём UI
    ability_tree_ui = AbilityTreeUI(screen, ability_tree, player_stats, level_system)
    
    # Главный цикл
    running = True
    dt = 0
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Даём дополнительные очки для тестирования
                    level_system.ability_points += 1
                    print(f"Добавлено очко способности. Всего: {level_system.ability_points}")
            else:
                # Передаём событие в UI
                ability_tree_ui.handle_event(event)
        
        # Обновляем анимации
        ability_tree_ui.update(dt)
        
        # Отрисовка
        screen.fill((15, 15, 20))
        ability_tree_ui.draw()
        
        # Информация для отладки
        font = pygame.font.Font(None, 20)
        debug_texts = [
            f"FPS: {int(clock.get_fps())}",
            f"Уровень: {level_system.level}",
            f"Очки способностей: {level_system.ability_points}",
            f"Разблокировано: {len(ability_tree.unlocked_abilities)}/{len(abilities)}",
            "",
            "Управление:",
            "SPACE - добавить очко способности",
            "ESC - выход",
        ]
        
        y = 10
        for text in debug_texts:
            surf = font.render(text, True, (200, 200, 200))
            screen.blit(surf, (10, y))
            y += 22
        
        # Обновление экрана
        pygame.display.flip()
        dt = clock.tick(60) / 1000.0  # Конвертируем в секунды
    
    pygame.quit()


if __name__ == "__main__":
    main()
