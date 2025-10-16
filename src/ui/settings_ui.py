"""
UI меню настроек
"""
import pygame
from typing import Optional, Callable


class SettingsUI:
    """UI меню настроек"""
    
    def __init__(self, width: int, height: int):
        """
        Инициализация UI настроек
        
        Args:
            width: Ширина окна
            height: Высота окна
        """
        self.width = width
        self.height = height
        
        # Размеры меню
        self.menu_width = 600
        self.menu_height = 500
        self.menu_x = (width - self.menu_width) // 2
        self.menu_y = (height - self.menu_height) // 2
        
        # Шрифты
        self.title_font = pygame.font.Font(None, 48)
        self.option_font = pygame.font.Font(None, 36)
        self.hint_font = pygame.font.Font(None, 24)
        
        # Настройки
        self.music_enabled = True
        self.sfx_enabled = True
        self.music_volume = 0.3
        self.sfx_volume = 0.5
        
        # Выбранный пункт
        self.selected_option = 0
        self.options = [
            "music_toggle",
            "music_volume",
            "sfx_toggle",
            "sfx_volume",
            "back"
        ]
        
        # Колбэки
        self.on_music_toggle: Optional[Callable] = None
        self.on_sfx_toggle: Optional[Callable] = None
        self.on_music_volume_change: Optional[Callable] = None
        self.on_sfx_volume_change: Optional[Callable] = None
        self.on_back: Optional[Callable] = None
        
    def handle_input(self, event: pygame.event.Event) -> bool:
        """
        Обработка ввода
        
        Args:
            event: Событие pygame
            
        Returns:
            True если событие обработано
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_option = (self.selected_option - 1) % len(self.options)
                return True
                
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_option = (self.selected_option + 1) % len(self.options)
                return True
                
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._activate_option()
                return True
                
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self._adjust_option(-1)
                return True
                
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self._adjust_option(1)
                return True
                
            elif event.key == pygame.K_ESCAPE:
                if self.on_back:
                    self.on_back()
                return True
        
        return False
    
    def _activate_option(self) -> None:
        """Активировать выбранный пункт"""
        option = self.options[self.selected_option]
        
        if option == "music_toggle":
            self.music_enabled = not self.music_enabled
            if self.on_music_toggle:
                self.on_music_toggle(self.music_enabled)
                
        elif option == "sfx_toggle":
            self.sfx_enabled = not self.sfx_enabled
            if self.on_sfx_toggle:
                self.on_sfx_toggle(self.sfx_enabled)
                
        elif option == "back":
            if self.on_back:
                self.on_back()
    
    def _adjust_option(self, direction: int) -> None:
        """
        Изменить значение опции
        
        Args:
            direction: Направление (-1 влево, 1 вправо)
        """
        option = self.options[self.selected_option]
        
        if option == "music_volume":
            self.music_volume = max(0.0, min(1.0, self.music_volume + direction * 0.1))
            if self.on_music_volume_change:
                self.on_music_volume_change(self.music_volume)
                
        elif option == "sfx_volume":
            self.sfx_volume = max(0.0, min(1.0, self.sfx_volume + direction * 0.1))
            if self.on_sfx_volume_change:
                self.on_sfx_volume_change(self.sfx_volume)
    
    def render(self, screen: pygame.Surface) -> None:
        """
        Отрисовка меню настроек
        
        Args:
            screen: Поверхность для отрисовки
        """
        # Получаем актуальные размеры экрана
        actual_width = screen.get_width()
        actual_height = screen.get_height()
        
        # Пересчитываем позицию меню по центру
        menu_x = (actual_width - self.menu_width) // 2
        menu_y = (actual_height - self.menu_height) // 2
        
        # Полупрозрачный фон
        overlay = pygame.Surface((actual_width, actual_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Фон меню
        menu_rect = pygame.Rect(menu_x, menu_y, self.menu_width, self.menu_height)
        pygame.draw.rect(screen, (40, 40, 60), menu_rect)
        pygame.draw.rect(screen, (100, 100, 150), menu_rect, 3)
        
        # Заголовок
        title = self.title_font.render("⚙️ НАСТРОЙКИ", True, (255, 255, 255))
        title_rect = title.get_rect(centerx=actual_width // 2, y=menu_y + 30)
        screen.blit(title, title_rect)
        
        # Опции
        y_offset = menu_y + 120
        spacing = 70
        
        # Музыка ВКЛ/ВЫКЛ
        self._render_toggle_option(
            screen,
            "🎵 Музыка:",
            self.music_enabled,
            y_offset,
            self.selected_option == 0,
            menu_x
        )
        
        # Громкость музыки
        y_offset += spacing
        self._render_slider_option(
            screen,
            "   Громкость музыки:",
            self.music_volume,
            y_offset,
            self.selected_option == 1,
            menu_x,
            actual_width
        )
        
        # Звуки ВКЛ/ВЫКЛ
        y_offset += spacing
        self._render_toggle_option(
            screen,
            "🔊 Звуковые эффекты:",
            self.sfx_enabled,
            y_offset,
            self.selected_option == 2,
            menu_x
        )
        
        # Громкость звуков
        y_offset += spacing
        self._render_slider_option(
            screen,
            "   Громкость звуков:",
            self.sfx_volume,
            y_offset,
            self.selected_option == 3,
            menu_x,
            actual_width
        )
        
        # Кнопка "Назад"
        y_offset += spacing + 20
        back_text = "← НАЗАД"
        back_color = (255, 255, 100) if self.selected_option == 4 else (200, 200, 200)
        back_surface = self.option_font.render(back_text, True, back_color)
        back_rect = back_surface.get_rect(centerx=actual_width // 2, y=y_offset)
        screen.blit(back_surface, back_rect)
        
        # Подсказки
        hint_y = menu_y + self.menu_height - 40
        hints = [
            "↑↓ - Выбор",
            "←→ - Изменить",
            "Enter - Применить",
            "ESC - Назад"
        ]
        hint_text = " | ".join(hints)
        hint_surface = self.hint_font.render(hint_text, True, (150, 150, 150))
        hint_rect = hint_surface.get_rect(centerx=actual_width // 2, y=hint_y)
        screen.blit(hint_surface, hint_rect)
    
    def _render_toggle_option(
        self,
        screen: pygame.Surface,
        label: str,
        enabled: bool,
        y: int,
        selected: bool,
        menu_x: int
    ) -> None:
        """
        Отрисовка переключателя
        
        Args:
            screen: Поверхность
            label: Текст опции
            enabled: Включено ли
            y: Позиция Y
            selected: Выбрано ли
        """
        # Текст опции
        color = (255, 255, 100) if selected else (200, 200, 200)
        label_surface = self.option_font.render(label, True, color)
        label_rect = label_surface.get_rect(x=menu_x + 50, y=y)
        screen.blit(label_surface, label_rect)
        
        # Статус
        status = "ВКЛ" if enabled else "ВЫКЛ"
        status_color = (100, 255, 100) if enabled else (255, 100, 100)
        if selected:
            status_color = tuple(min(255, c + 50) for c in status_color)
        
        status_surface = self.option_font.render(status, True, status_color)
        status_rect = status_surface.get_rect(x=menu_x + self.menu_width - 150, y=y)
        screen.blit(status_surface, status_rect)
    
    def _render_slider_option(
        self,
        screen: pygame.Surface,
        label: str,
        value: float,
        y: int,
        selected: bool,
        menu_x: int,
        actual_width: int
    ) -> None:
        """
        Отрисовка слайдера
        
        Args:
            screen: Поверхность
            label: Текст опции
            value: Значение (0.0 - 1.0)
            y: Позиция Y
            selected: Выбрано ли
        """
        # Текст опции
        color = (255, 255, 100) if selected else (200, 200, 200)
        label_surface = self.option_font.render(label, True, color)
        label_rect = label_surface.get_rect(x=menu_x + 50, y=y)
        screen.blit(label_surface, label_rect)
        
        # Слайдер
        slider_x = menu_x + self.menu_width - 250
        slider_y = y + 15
        slider_width = 150
        slider_height = 10
        
        # Фон слайдера
        slider_bg = pygame.Rect(slider_x, slider_y, slider_width, slider_height)
        pygame.draw.rect(screen, (80, 80, 80), slider_bg)
        
        # Заполнение слайдера
        fill_width = int(slider_width * value)
        slider_fill = pygame.Rect(slider_x, slider_y, fill_width, slider_height)
        fill_color = (100, 200, 255) if selected else (100, 150, 200)
        pygame.draw.rect(screen, fill_color, slider_fill)
        
        # Рамка
        border_color = (255, 255, 100) if selected else (150, 150, 150)
        pygame.draw.rect(screen, border_color, slider_bg, 2)
        
        # Процент
        percent_text = f"{int(value * 100)}%"
        percent_surface = self.hint_font.render(percent_text, True, color)
        percent_rect = percent_surface.get_rect(x=slider_x + slider_width + 10, y=y + 5)
        screen.blit(percent_surface, percent_rect)
