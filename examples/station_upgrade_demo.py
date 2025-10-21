"""
Демонстрация UI улучшения станций
Версия: 0.4.0
Этап 0, Неделя 3, День 3-4
"""

import pygame
import sys
import os

# Добавляем путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.objects.station_presets import create_all_stations
from src.ui.station_upgrade_ui import StationUpgradeUI


def main():
    """Главная функция демонстрации"""
    # Инициализация Pygame
    pygame.init()
    
    # Создаём окно
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Крафт-станции - Демо")
    clock = pygame.time.Clock()
    
    # Создаём менеджер станций
    station_manager = create_all_stations()
    
    # Разблокируем несколько станций для демонстрации
    station_manager.unlock_station("laboratory")
    station_manager.unlock_station("alchemy_table")
    
    # Тестовые данные игрока
    player_level = 10
    player_inventory = {
        # Материалы для верстака tier 2
        "iron_ingot": 15,
        "wooden_plank": 25,
        "rope": 10,
        # Материалы для верстака tier 3
        "steel_ingot": 20,
        "rare_wood": 15,
        "precision_tools": 2,
        # Материалы для лаборатории
        "glass": 20,
        "refined_glass": 20,
        "chemical_reagent": 10,
        # Материалы для алхимического стола
        "stone": 30,
        "herb": 20,
    }
    player_money = 10000
    
    # Создаём UI
    station_ui = StationUpgradeUI(
        screen,
        station_manager,
        player_level,
        player_inventory,
        player_money
    )
    
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
                    if station_ui.show_upgrade_panel:
                        station_ui.show_upgrade_panel = False
                        station_ui.selected_station = None
                    else:
                        running = False
                elif event.key == pygame.K_SPACE:
                    # Даём дополнительные деньги для тестирования
                    station_ui.player_money += 1000
                    print(f"Добавлено 1000 монет. Всего: {station_ui.player_money}")
                elif event.key == pygame.K_m:
                    # Даём материалы
                    for item in station_ui.player_inventory:
                        station_ui.player_inventory[item] += 10
                    print("Добавлено по 10 единиц всех материалов")
            else:
                # Передаём событие в UI
                station_ui.handle_event(event)
        
        # Обновляем анимации
        station_ui.update(dt)
        
        # Отрисовка
        screen.fill((15, 15, 20))
        station_ui.draw()
        
        # Информация для отладки
        font = pygame.font.Font(None, 20)
        debug_texts = [
            f"FPS: {int(clock.get_fps())}",
            f"Уровень: {player_level}",
            f"Монеты: {station_ui.player_money}",
            f"Станций разблокировано: {len(station_manager.get_unlocked_stations())}",
            "",
            "Управление:",
            "SPACE - добавить 1000 монет",
            "M - добавить материалы",
            "ESC - закрыть панель/выход",
        ]
        
        y = 10
        for text in debug_texts:
            surf = font.render(text, True, (200, 200, 200))
            screen.blit(surf, (10, y))
            y += 22
        
        # Обновление экрана
        pygame.display.flip()
        dt = clock.tick(60) / 1000.0
    
    pygame.quit()


if __name__ == "__main__":
    main()
