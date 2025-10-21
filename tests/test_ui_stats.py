"""
Тест UI для характеристик
Версия: 0.4.0
"""

import sys
sys.path.insert(0, 'src')

import pygame
from systems import PlayerStats, LevelSystem, ModifierManager, create_ability_modifier, ModifierType
from ui import StatsScreen, LevelUpNotification, ExperienceGainNotification


def test_stats_screen():
    """Тест экрана характеристик"""
    print("=== Тест StatsScreen ===")
    
    # Инициализация pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Test Stats Screen")
    clock = pygame.time.Clock()
    
    # Создать данные
    stats = PlayerStats()
    level_system = LevelSystem(level=5, experience=500)
    level_system.ability_points = 2
    
    modifier_manager = ModifierManager()
    modifier_manager.add_modifier(create_ability_modifier(
        'attack', 5, ModifierType.FLAT, 'combat_training', "Боевая подготовка +5"
    ))
    modifier_manager.add_modifier(create_ability_modifier(
        'defense', 3, ModifierType.FLAT, 'tough', "Живучесть +3"
    ))
    
    # Создать UI
    stats_screen = StatsScreen(screen)
    stats_screen.show()
    
    print("Экран характеристик создан")
    print("Нажмите C для закрытия, ESC для выхода")
    
    # Главный цикл
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                # Обработка ввода UI
                result = stats_screen.handle_input(event)
                if result == 'close':
                    print("Экран закрыт")
                elif result == 'abilities':
                    print("Открыть экран способностей (не реализовано)")
        
        # Отрисовка
        screen.fill((30, 30, 40))
        
        # Информация
        font = pygame.font.Font(None, 24)
        info = font.render("Тест экрана характеристик. ESC - выход", True, (200, 200, 200))
        screen.blit(info, (10, 10))
        
        # Отрисовать экран характеристик
        stats_screen.draw(stats, level_system, modifier_manager)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("Тест завершён\n")


def test_level_up_notification():
    """Тест уведомления о повышении уровня"""
    print("=== Тест LevelUpNotification ===")
    
    # Инициализация pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Test Level Up")
    clock = pygame.time.Clock()
    
    # Создать уведомление
    notification = LevelUpNotification(screen)
    
    print("Уведомление создано")
    print("Нажмите SPACE для показа уведомления, ESC для выхода")
    
    # Главный цикл
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    notification.show(level=5, ability_points=1)
                    print("Показано уведомление: Уровень 5")
        
        # Обновление
        notification.update()
        
        # Отрисовка
        screen.fill((30, 30, 40))
        
        # Информация
        font = pygame.font.Font(None, 24)
        info = font.render("SPACE - показать уведомление, ESC - выход", True, (200, 200, 200))
        screen.blit(info, (10, 10))
        
        # Отрисовать уведомление
        notification.draw()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("Тест завершён\n")


def test_experience_notification():
    """Тест уведомлений о получении опыта"""
    print("=== Тест ExperienceGainNotification ===")
    
    # Инициализация pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Test Experience Gain")
    clock = pygame.time.Clock()
    
    # Создать уведомления
    exp_notifications = ExperienceGainNotification(screen)
    
    print("Уведомления созданы")
    print("Кликните мышью для добавления уведомления, ESC для выхода")
    
    # Главный цикл
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                exp_notifications.add(amount=10, x=x, y=y)
                print(f"Добавлено уведомление +10 XP в ({x}, {y})")
        
        # Обновление
        exp_notifications.update()
        
        # Отрисовка
        screen.fill((30, 30, 40))
        
        # Информация
        font = pygame.font.Font(None, 24)
        info = font.render("Кликните для добавления +10 XP, ESC - выход", True, (200, 200, 200))
        screen.blit(info, (10, 10))
        
        # Отрисовать уведомления
        exp_notifications.draw()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("Тест завершён\n")


if __name__ == '__main__':
    print("Тесты UI для системы характеристик")
    print("=" * 50)
    print()
    
    choice = input("Выберите тест:\n1. Экран характеристик\n2. Уведомление о повышении уровня\n3. Уведомления об опыте\n4. Все тесты\nВыбор: ")
    
    if choice == '1':
        test_stats_screen()
    elif choice == '2':
        test_level_up_notification()
    elif choice == '3':
        test_experience_notification()
    elif choice == '4':
        test_stats_screen()
        test_level_up_notification()
        test_experience_notification()
    else:
        print("Неверный выбор")
    
    print("\n=== Все тесты завершены ===")
