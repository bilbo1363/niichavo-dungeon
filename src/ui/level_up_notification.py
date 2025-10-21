"""
Уведомление о повышении уровня
Версия: 0.4.0
Этап 0, Неделя 1
"""

import pygame
from typing import Optional


class LevelUpNotification:
    """Уведомление о повышении уровня"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 48)
        self.font_normal = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Цвета
        self.COLOR_BG = (20, 20, 30, 220)
        self.COLOR_GLOW = (255, 215, 0)
        self.COLOR_TEXT = (255, 255, 255)
        self.COLOR_TEXT_DIM = (200, 200, 200)
        
        # Состояние
        self.active = False
        self.level = 0
        self.ability_points = 0
        self.timer = 0
        self.duration = 180  # 3 секунды при 60 FPS
        
        # Анимация
        self.scale = 0.0
        self.alpha = 0
    
    def show(self, level: int, ability_points: int):
        """
        Показать уведомление
        
        Args:
            level: Новый уровень
            ability_points: Количество очков способностей
        """
        self.active = True
        self.level = level
        self.ability_points = ability_points
        self.timer = self.duration
        self.scale = 0.0
        self.alpha = 0
    
    def update(self):
        """Обновить анимацию"""
        if not self.active:
            return
        
        self.timer -= 1
        
        # Анимация появления (первые 20 кадров)
        if self.timer > self.duration - 20:
            progress = (self.duration - self.timer) / 20.0
            self.scale = self._ease_out_back(progress)
            self.alpha = int(255 * progress)
        
        # Анимация исчезновения (последние 20 кадров)
        elif self.timer < 20:
            progress = self.timer / 20.0
            self.scale = 1.0
            self.alpha = int(255 * progress)
        
        # Полная видимость
        else:
            self.scale = 1.0
            self.alpha = 255
        
        # Завершить
        if self.timer <= 0:
            self.active = False
    
    def draw(self):
        """Отрисовать уведомление"""
        if not self.active:
            return
        
        # Размеры панели
        panel_width = 400
        panel_height = 200
        panel_x = (self.screen.get_width() - panel_width) // 2
        panel_y = (self.screen.get_height() - panel_height) // 2
        
        # Применить масштаб
        scaled_width = int(panel_width * self.scale)
        scaled_height = int(panel_height * self.scale)
        scaled_x = panel_x + (panel_width - scaled_width) // 2
        scaled_y = panel_y + (panel_height - scaled_height) // 2
        
        # Создать поверхность с альфа-каналом
        panel_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
        
        # Фон с прозрачностью
        bg_color = (*self.COLOR_BG[:3], int(self.COLOR_BG[3] * (self.alpha / 255)))
        pygame.draw.rect(panel_surface, bg_color, (0, 0, scaled_width, scaled_height), border_radius=10)
        
        # Свечение границы
        glow_color = (*self.COLOR_GLOW, int(self.alpha))
        pygame.draw.rect(panel_surface, glow_color, (0, 0, scaled_width, scaled_height), 3, border_radius=10)
        
        # Текст (только если достаточно масштаб)
        if self.scale > 0.5:
            self._draw_text(panel_surface, scaled_width, scaled_height)
        
        # Отрисовать на экране
        self.screen.blit(panel_surface, (scaled_x, scaled_y))
    
    def _draw_text(self, surface: pygame.Surface, width: int, height: int):
        """Отрисовать текст на поверхности"""
        y_offset = 30
        
        # "LEVEL UP!"
        title = self.font_large.render("LEVEL UP!", True, self.COLOR_GLOW)
        title.set_alpha(self.alpha)
        title_rect = title.get_rect(center=(width // 2, y_offset))
        surface.blit(title, title_rect)
        
        y_offset += 60
        
        # Новый уровень
        level_text = self.font_normal.render(f"Уровень {self.level}", True, self.COLOR_TEXT)
        level_text.set_alpha(self.alpha)
        level_rect = level_text.get_rect(center=(width // 2, y_offset))
        surface.blit(level_text, level_rect)
        
        y_offset += 50
        
        # Очки способностей
        if self.ability_points > 0:
            ap_text = self.font_small.render(
                f"+{self.ability_points} очко способностей", 
                True, 
                self.COLOR_TEXT_DIM
            )
            ap_text.set_alpha(self.alpha)
            ap_rect = ap_text.get_rect(center=(width // 2, y_offset))
            surface.blit(ap_text, ap_rect)
    
    @staticmethod
    def _ease_out_back(t: float) -> float:
        """
        Функция плавности с отскоком
        
        Args:
            t: Прогресс от 0.0 до 1.0
            
        Returns:
            Значение с эффектом отскока
        """
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)
    
    def is_active(self) -> bool:
        """Проверка, активно ли уведомление"""
        return self.active


class ExperienceGainNotification:
    """Уведомление о получении опыта"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        
        # Цвета
        self.COLOR_EXP = (255, 215, 0)
        
        # Активные уведомления
        self.notifications = []
    
    def add(self, amount: int, x: int, y: int):
        """
        Добавить уведомление о получении опыта
        
        Args:
            amount: Количество опыта
            x: X координата
            y: Y координата
        """
        self.notifications.append({
            'amount': amount,
            'x': x,
            'y': y,
            'timer': 60,  # 1 секунда при 60 FPS
            'offset_y': 0
        })
    
    def update(self):
        """Обновить все уведомления"""
        for notif in self.notifications[:]:
            notif['timer'] -= 1
            notif['offset_y'] -= 1  # Движение вверх
            
            if notif['timer'] <= 0:
                self.notifications.remove(notif)
    
    def draw(self):
        """Отрисовать все уведомления"""
        for notif in self.notifications:
            # Прозрачность зависит от времени
            alpha = int(255 * (notif['timer'] / 60.0))
            
            # Текст
            text = self.font.render(f"+{notif['amount']} XP", True, self.COLOR_EXP)
            text.set_alpha(alpha)
            
            # Позиция
            x = notif['x']
            y = notif['y'] + notif['offset_y']
            
            # Отрисовать
            self.screen.blit(text, (x, y))
    
    def clear(self):
        """Очистить все уведомления"""
        self.notifications.clear()
