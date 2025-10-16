"""
Лог игровых сообщений
"""
import pygame
from typing import List, Tuple
from dataclasses import dataclass
from enum import Enum


class MessageType(Enum):
    """Типы сообщений"""
    INFO = "info"           # Обычная информация (белый)
    SUCCESS = "success"     # Успех (зелёный)
    WARNING = "warning"     # Предупреждение (жёлтый)
    ERROR = "error"         # Ошибка (красный)
    COMBAT = "combat"       # Бой (оранжевый)
    ITEM = "item"          # Предметы (голубой)
    STORY = "story"        # Сюжет (фиолетовый)


@dataclass
class Message:
    """Игровое сообщение"""
    text: str
    message_type: MessageType
    lifetime: float = 5.0  # Время жизни в секундах
    age: float = 0.0       # Возраст сообщения


class MessageLog:
    """Лог игровых сообщений"""
    
    def __init__(self, screen_width: int, screen_height: int, max_messages: int = 5):
        """
        Инициализация лога
        
        Args:
            screen_width: Ширина экрана
            screen_height: Высота экрана
            max_messages: Максимальное количество сообщений
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.max_messages = max_messages
        self.messages: List[Message] = []
        
        # Параметры отображения
        self.padding = 20
        self.y = 20  # Сверху справа
        self.line_height = 35
        self.font = pygame.font.Font(None, 32)  # Увеличенный размер
        
        # Цвета для разных типов сообщений
        self.colors = {
            MessageType.INFO: (255, 255, 255),      # Белый
            MessageType.SUCCESS: (100, 255, 100),   # Зелёный
            MessageType.WARNING: (255, 255, 100),   # Жёлтый
            MessageType.ERROR: (255, 100, 100),     # Красный
            MessageType.COMBAT: (255, 150, 50),     # Оранжевый
            MessageType.ITEM: (100, 200, 255),      # Голубой
            MessageType.STORY: (200, 100, 255),     # Фиолетовый
        }
        
    def add_message(self, text: str, message_type: MessageType = MessageType.INFO) -> None:
        """
        Добавить сообщение
        
        Args:
            text: Текст сообщения
            message_type: Тип сообщения
        """
        # Создаём новое сообщение
        message = Message(text=text, message_type=message_type)
        
        # Добавляем в начало списка
        self.messages.insert(0, message)
        
        # Ограничиваем количество сообщений
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[:self.max_messages]
            
    def update(self, dt: float) -> None:
        """
        Обновление сообщений
        
        Args:
            dt: Delta time
        """
        # Обновляем возраст сообщений
        for message in self.messages:
            message.age += dt
            
        # Удаляем старые сообщения
        self.messages = [m for m in self.messages if m.age < m.lifetime]
        
    def render(self, screen: pygame.Surface) -> None:
        """
        Отрисовка сообщений
        
        Args:
            screen: Поверхность для отрисовки
        """
        # Получаем актуальную ширину экрана
        actual_width = screen.get_width()
        
        y_offset = self.y
        
        for i, message in enumerate(self.messages):
            # Вычисляем прозрачность (исчезает к концу жизни)
            alpha_factor = 1.0 - (message.age / message.lifetime)
            alpha = int(255 * alpha_factor)
            
            # Получаем цвет для типа сообщения
            base_color = self.colors.get(message.message_type, (255, 255, 255))
            
            # Создаём поверхность с прозрачностью
            text_surface = self.font.render(message.text, True, base_color)
            text_surface.set_alpha(alpha)
            
            # Вычисляем позицию справа (выравнивание по правому краю)
            text_width = text_surface.get_width()
            x_pos = actual_width - text_width - self.padding
            
            # Рисуем полупрозрачный фон для читаемости
            bg_rect = pygame.Rect(x_pos - 10, y_offset - 5, text_width + 20, self.line_height - 5)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.set_alpha(alpha // 3)
            bg_surface.fill((0, 0, 0))
            screen.blit(bg_surface, bg_rect.topleft)
            
            # Рисуем тень для читаемости
            shadow_surface = self.font.render(message.text, True, (0, 0, 0))
            shadow_surface.set_alpha(alpha // 2)
            screen.blit(shadow_surface, (x_pos + 2, y_offset + 2))
            
            # Рисуем текст
            screen.blit(text_surface, (x_pos, y_offset))
            
            y_offset += self.line_height
            
    def clear(self) -> None:
        """Очистить все сообщения"""
        self.messages.clear()
        
    # Удобные методы для разных типов сообщений
    
    def info(self, text: str) -> None:
        """Информационное сообщение"""
        self.add_message(text, MessageType.INFO)
        
    def success(self, text: str) -> None:
        """Сообщение об успехе"""
        self.add_message(text, MessageType.SUCCESS)
        
    def warning(self, text: str) -> None:
        """Предупреждение"""
        self.add_message(text, MessageType.WARNING)
        
    def error(self, text: str) -> None:
        """Ошибка"""
        self.add_message(text, MessageType.ERROR)
        
    def combat(self, text: str) -> None:
        """Боевое сообщение"""
        self.add_message(text, MessageType.COMBAT)
        
    def item(self, text: str) -> None:
        """Сообщение о предмете"""
        self.add_message(text, MessageType.ITEM)
        
    def story(self, text: str) -> None:
        """Сюжетное сообщение"""
        self.add_message(text, MessageType.STORY)


if __name__ == "__main__":
    # Тест системы сообщений
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    clock = pygame.time.Clock()
    
    message_log = MessageLog(1200, 800)
    
    # Добавляем тестовые сообщения
    message_log.info("Добро пожаловать в подземелье!")
    message_log.success("Вы подобрали Ржавую трубу")
    message_log.combat("Крыса атаковала вас! Урон: 3")
    message_log.item("Найден Бинт x1")
    message_log.warning("Здоровье низкое!")
    
    running = True
    test_timer = 0
    
    while running:
        dt = clock.tick(60) / 1000.0
        test_timer += dt
        
        # Добавляем новое сообщение каждые 2 секунды
        if test_timer >= 2.0:
            test_timer = 0
            message_log.info(f"Тестовое сообщение {int(pygame.time.get_ticks() / 1000)}")
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    message_log.info("Информация")
                elif event.key == pygame.K_2:
                    message_log.success("Успех!")
                elif event.key == pygame.K_3:
                    message_log.warning("Внимание!")
                elif event.key == pygame.K_4:
                    message_log.error("Ошибка!")
                elif event.key == pygame.K_5:
                    message_log.combat("Бой!")
                elif event.key == pygame.K_6:
                    message_log.item("Предмет")
                elif event.key == pygame.K_7:
                    message_log.story("Сюжет")
                    
        message_log.update(dt)
        
        screen.fill((0, 0, 0))
        message_log.render(screen)
        
        # Подсказка
        font = pygame.font.Font(None, 20)
        hint = font.render("Press 1-7 to test different message types", True, (150, 150, 150))
        screen.blit(hint, (10, 10))
        
        pygame.display.flip()
        
    pygame.quit()
