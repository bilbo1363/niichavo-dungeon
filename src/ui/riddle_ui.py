"""
GUI для загадок
"""
import pygame


class RiddleUI:
    """Визуальный интерфейс загадок"""
    
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
        self.width = 700
        self.height = 400
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        
        # Шрифты
        self.title_font = pygame.font.Font(None, 32)
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 20)
        
        # Ввод ответа
        self.answer_input = ""
        self.max_input_length = 20
        
    def render(self, screen: pygame.Surface, riddle) -> None:
        """
        Отрисовка загадки
        
        Args:
            screen: Поверхность для отрисовки
            riddle: Загадка
        """
        # Полупрозрачный фон
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Окно загадки
        pygame.draw.rect(screen, (40, 30, 50), (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, (150, 100, 200), (self.x, self.y, self.width, self.height), 4)
        
        # Заголовок (меняется если загадка решена)
        if riddle.solved:
            title = self.title_font.render("✓ РЕШЁННАЯ ЗАГАДКА", True, (150, 150, 150))
        else:
            title = self.title_font.render("📜 ЗАГАДКА НА СТЕНЕ", True, (255, 200, 100))
        title_rect = title.get_rect(center=(self.x + self.width // 2, self.y + 30))
        screen.blit(title, title_rect)
        
        # Вопрос (многострочный)
        question_y = self.y + 80
        words = riddle.question.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.font.render(test_line, True, (255, 255, 255))
            if test_surface.get_width() > self.width - 60:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            else:
                current_line.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        for i, line in enumerate(lines):
            line_surface = self.font.render(line, True, (255, 255, 255))
            line_rect = line_surface.get_rect(center=(self.x + self.width // 2, question_y + i * 35))
            screen.blit(line_surface, line_rect)
        
        # Если загадка решена - показываем ответ и награду
        if riddle.solved:
            # Показываем правильный ответ
            answer_y = self.y + self.height - 150
            answer_label = self.font.render("Правильный ответ:", True, (150, 200, 150))
            screen.blit(answer_label, (self.x + 30, answer_y))
            
            answer_text = self.font.render(riddle.answer, True, (100, 255, 100))
            answer_rect = answer_text.get_rect(center=(self.x + self.width // 2, answer_y + 40))
            screen.blit(answer_text, answer_rect)
            
            # Показываем награду
            reward_y = answer_y + 80
            reward_label = self.small_font.render(f"Награда: {riddle.reward_description}", True, (255, 200, 100))
            reward_rect = reward_label.get_rect(center=(self.x + self.width // 2, reward_y))
            screen.blit(reward_label, reward_rect)
            
            # Подсказка
            hint_y = self.y + self.height - 30
            hint_text = self.small_font.render("ESC - закрыть", True, (150, 150, 150))
            hint_rect = hint_text.get_rect(center=(self.x + self.width // 2, hint_y))
            screen.blit(hint_text, hint_rect)
        else:
            # Поле ввода для нерешённой загадки
            input_y = self.y + self.height - 150
            input_label = self.font.render("Ваш ответ:", True, (200, 200, 200))
            screen.blit(input_label, (self.x + 30, input_y))
            
            # Рамка ввода
            input_box_y = input_y + 40
            pygame.draw.rect(screen, (60, 50, 70), (self.x + 30, input_box_y, self.width - 60, 50))
            pygame.draw.rect(screen, (150, 150, 150), (self.x + 30, input_box_y, self.width - 60, 50), 2)
            
            # Текст ввода
            input_text = self.font.render(self.answer_input, True, (255, 255, 255))
            screen.blit(input_text, (self.x + 40, input_box_y + 12))
            
            # Курсор (мигающий)
            if pygame.time.get_ticks() % 1000 < 500:
                cursor_x = self.x + 40 + input_text.get_width() + 2
                pygame.draw.line(screen, (255, 255, 255), 
                               (cursor_x, input_box_y + 10), 
                               (cursor_x, input_box_y + 40), 2)
            
            # Подсказки
            hint_y = self.y + self.height - 50
            hints = [
                "Введите ответ и нажмите Enter",
                "ESC - закрыть без ответа"
            ]
            for i, hint in enumerate(hints):
                hint_text = self.small_font.render(hint, True, (150, 150, 150))
                hint_rect = hint_text.get_rect(center=(self.x + self.width // 2, hint_y + i * 20))
                screen.blit(hint_text, hint_rect)
    
    def handle_input(self, event: pygame.event.Event, riddle) -> tuple[bool, str]:
        """
        Обработка ввода
        
        Args:
            event: Событие pygame
            riddle: Загадка
            
        Returns:
            (закрыть_окно, ответ)
        """
        if event.type == pygame.KEYDOWN:
            # Закрыть без ответа
            if event.key == pygame.K_ESCAPE:
                self.answer_input = ""
                return True, ""
            
            # Отправить ответ
            elif event.key == pygame.K_RETURN:
                answer = self.answer_input
                self.answer_input = ""
                return True, answer
            
            # Backspace
            elif event.key == pygame.K_BACKSPACE:
                self.answer_input = self.answer_input[:-1]
            
            # Ввод символов
            elif len(self.answer_input) < self.max_input_length:
                if event.unicode.isprintable():
                    self.answer_input += event.unicode
        
        return False, ""
