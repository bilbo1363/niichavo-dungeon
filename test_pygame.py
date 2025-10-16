"""
Тест установки Pygame
"""
import pygame
import sys

def test_pygame():
    """Простой тест Pygame"""
    print("Тестирование Pygame...")
    print(f"Версия Pygame: {pygame.version.ver}")
    
    # Инициализация
    pygame.init()
    
    # Создание окна
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Тест Pygame - Подземелье НИИЧАВО")
    
    # Цвета
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    WHITE = (255, 255, 255)
    
    # Шрифт
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 24)
    
    # Текст
    title = font.render("Pygame работает!", True, GREEN)
    subtitle = small_font.render("Нажмите ESC для выхода", True, WHITE)
    
    # Игровой цикл
    clock = pygame.time.Clock()
    running = True
    
    print("\n✅ Pygame успешно инициализирован!")
    print("📺 Окно открыто. Нажмите ESC для выхода.")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Отрисовка
        screen.fill(BLACK)
        screen.blit(title, (200, 250))
        screen.blit(subtitle, (250, 320))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("\n✅ Тест завершен успешно!")
    print("🎮 Готовы к разработке игры!")

if __name__ == "__main__":
    try:
        test_pygame()
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)
