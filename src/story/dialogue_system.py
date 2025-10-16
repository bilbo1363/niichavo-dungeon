"""
Система диалогов
"""
import pygame
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass


@dataclass
class DialogueChoice:
    """Выбор в диалоге"""
    text: str
    next_node: str
    condition: Optional[Callable] = None  # Функция проверки доступности


@dataclass
class DialogueNode:
    """Узел диалога"""
    speaker: str
    text: str
    choices: List[DialogueChoice]
    auto_next: Optional[str] = None  # Автоматический переход
    on_show: Optional[Callable] = None  # Действие при показе


class Dialogue:
    """Диалог"""
    
    def __init__(self, dialogue_id: str, start_node: str):
        """
        Инициализация диалога
        
        Args:
            dialogue_id: ID диалога
            start_node: Начальный узел
        """
        self.dialogue_id = dialogue_id
        self.start_node = start_node
        self.current_node = start_node
        self.nodes: Dict[str, DialogueNode] = {}
        self.completed = False
        
    def add_node(self, node_id: str, node: DialogueNode) -> None:
        """
        Добавить узел
        
        Args:
            node_id: ID узла
            node: Узел диалога
        """
        self.nodes[node_id] = node
        
    def get_current_node(self) -> Optional[DialogueNode]:
        """
        Получить текущий узел
        
        Returns:
            Текущий узел или None
        """
        return self.nodes.get(self.current_node)
        
    def choose(self, choice_index: int) -> bool:
        """
        Выбрать вариант
        
        Args:
            choice_index: Индекс выбора
            
        Returns:
            True если диалог продолжается
        """
        node = self.get_current_node()
        if not node or choice_index >= len(node.choices):
            return False
            
        choice = node.choices[choice_index]
        
        # Проверяем условие
        if choice.condition and not choice.condition():
            return True  # Выбор недоступен, диалог продолжается
            
        # Переходим к следующему узлу
        if choice.next_node == "END":
            self.completed = True
            return False
        else:
            self.current_node = choice.next_node
            
            # Выполняем действие при показе
            next_node = self.get_current_node()
            if next_node and next_node.on_show:
                next_node.on_show()
                
            return True
            
    def reset(self) -> None:
        """Сбросить диалог"""
        self.current_node = self.start_node
        self.completed = False


class DialogueUI:
    """UI для диалогов"""
    
    def __init__(self, screen_width: int, screen_height: int):
        """
        Инициализация UI
        
        Args:
            screen_width: Ширина экрана
            screen_height: Высота экрана
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Параметры окна
        self.width = 900
        self.height = 300
        self.x = (screen_width - self.width) // 2
        self.y = screen_height - self.height - 50
        
        # Шрифты
        self.speaker_font = pygame.font.Font(None, 32)
        self.text_font = pygame.font.Font(None, 26)
        self.choice_font = pygame.font.Font(None, 24)
        
        # Выбранный вариант
        self.selected_choice = 0
        
    def render(self, screen: pygame.Surface, dialogue: Dialogue) -> None:
        """
        Отрисовка диалога
        
        Args:
            screen: Поверхность для отрисовки
            dialogue: Диалог
        """
        node = dialogue.get_current_node()
        if not node:
            return
            
        # Полупрозрачный фон
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Окно диалога
        pygame.draw.rect(screen, (30, 30, 40), (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, (100, 100, 150), (self.x, self.y, self.width, self.height), 3)
        
        # Имя говорящего
        speaker_text = self.speaker_font.render(node.speaker, True, (255, 200, 100))
        screen.blit(speaker_text, (self.x + 20, self.y + 15))
        
        # Разделитель
        pygame.draw.line(screen, (100, 100, 150), 
                        (self.x + 20, self.y + 55), 
                        (self.x + self.width - 20, self.y + 55), 2)
        
        # Текст диалога (многострочный)
        self._render_wrapped_text(screen, node.text, self.x + 20, self.y + 70, self.width - 40)
        
        # Варианты выбора
        if node.choices:
            choice_y = self.y + 160
            for i, choice in enumerate(node.choices):
                # Проверяем доступность
                available = not choice.condition or choice.condition()
                
                # Цвет
                if not available:
                    color = (100, 100, 100)
                elif i == self.selected_choice:
                    color = (255, 255, 0)
                else:
                    color = (200, 200, 200)
                    
                # Рамка для выбранного
                if i == self.selected_choice and available:
                    pygame.draw.rect(screen, (100, 100, 150), 
                                   (self.x + 15, choice_y - 5, self.width - 30, 35), 2)
                
                # Текст выбора
                prefix = "▶ " if i == self.selected_choice else "  "
                choice_text = self.choice_font.render(f"{prefix}{i+1}. {choice.text}", True, color)
                screen.blit(choice_text, (self.x + 25, choice_y))
                
                choice_y += 40
                
        # Подсказка
        hint_text = self.choice_font.render(
            "Стрелки - выбор | Enter - подтвердить | ESC - закрыть",
            True,
            (150, 150, 150)
        )
        hint_rect = hint_text.get_rect(center=(self.x + self.width // 2, self.y + self.height - 20))
        screen.blit(hint_text, hint_rect)
        
    def _render_wrapped_text(self, screen: pygame.Surface, text: str, x: int, y: int, max_width: int) -> None:
        """
        Отрисовка текста с переносом
        
        Args:
            screen: Поверхность
            text: Текст
            x, y: Позиция
            max_width: Максимальная ширина
        """
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.text_font.render(test_line, True, (255, 255, 255))
            
            if test_surface.get_width() > max_width:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            else:
                current_line.append(word)
                
        if current_line:
            lines.append(' '.join(current_line))
            
        # Рисуем строки
        for i, line in enumerate(lines[:3]):  # Максимум 3 строки
            line_surface = self.text_font.render(line, True, (255, 255, 255))
            screen.blit(line_surface, (x, y + i * 30))
            
    def handle_input(self, event: pygame.event.Event, dialogue: Dialogue) -> bool:
        """
        Обработка ввода
        
        Args:
            event: Событие pygame
            dialogue: Диалог
            
        Returns:
            True если нужно закрыть диалог
        """
        node = dialogue.get_current_node()
        if not node:
            return True
            
        if event.type == pygame.KEYDOWN:
            # Закрыть
            if event.key == pygame.K_ESCAPE:
                return True
                
            # Навигация
            if event.key == pygame.K_DOWN:
                self.selected_choice = (self.selected_choice + 1) % len(node.choices)
            elif event.key == pygame.K_UP:
                self.selected_choice = (self.selected_choice - 1) % len(node.choices)
                
            # Выбор
            elif event.key == pygame.K_RETURN:
                if not dialogue.choose(self.selected_choice):
                    return True  # Диалог завершён
                self.selected_choice = 0  # Сбрасываем выбор
                
        return False


if __name__ == "__main__":
    # Тест системы диалогов
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    
    # Создаём тестовый диалог
    dialogue = Dialogue("test", "start")
    
    dialogue.add_node("start", DialogueNode(
        speaker="Старик",
        text="Добро пожаловать в подземелье, путник. Что привело тебя сюда?",
        choices=[
            DialogueChoice("Ищу сокровища", "treasure"),
            DialogueChoice("Хочу стать сильнее", "power"),
            DialogueChoice("Просто заблудился", "lost"),
        ]
    ))
    
    dialogue.add_node("treasure", DialogueNode(
        speaker="Старик",
        text="Жадность - опасная вещь. Но удачи тебе.",
        choices=[DialogueChoice("Спасибо", "END")]
    ))
    
    ui = DialogueUI(1200, 800)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if ui.handle_input(event, dialogue):
                running = False
                
        screen.fill((0, 0, 0))
        ui.render(screen, dialogue)
        pygame.display.flip()
        
    pygame.quit()
