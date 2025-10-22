"""
UI экран характеристик игрока
Версия: 0.4.0
Этап 0, Неделя 1
"""

import pygame
from typing import Optional, Tuple
from ..systems import PlayerStats, LevelSystem, ModifierManager


class StatsScreen:
    """Экран отображения характеристик игрока"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 36)
        self.font_normal = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        
        # Цвета
        self.COLOR_BG = (20, 20, 30)
        self.COLOR_PANEL = (40, 40, 50)
        self.COLOR_TEXT = (200, 200, 200)
        self.COLOR_TEXT_DIM = (150, 150, 150)
        self.COLOR_POSITIVE = (100, 255, 100)
        self.COLOR_NEGATIVE = (255, 100, 100)
        self.COLOR_HEALTH = (220, 50, 50)
        self.COLOR_STAMINA = (50, 150, 220)
        self.COLOR_EXP = (255, 215, 0)
        self.COLOR_BORDER = (100, 100, 100)
        
        self.visible = False
    
    def toggle(self):
        """Переключить видимость экрана"""
        self.visible = not self.visible
    
    def show(self):
        """Показать экран"""
        self.visible = True
    
    def hide(self):
        """Скрыть экран"""
        self.visible = False
    
    def draw(self, stats: PlayerStats, level_system: LevelSystem, 
             modifier_manager: Optional[ModifierManager] = None):
        """
        Отрисовать экран характеристик
        
        Args:
            stats: Характеристики игрока
            level_system: Система уровней
            modifier_manager: Менеджер модификаторов (опционально)
        """
        if not self.visible:
            return
        
        # Затемнённый фон
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Основная панель
        panel_width = 600
        panel_height = 700
        panel_x = (self.screen.get_width() - panel_width) // 2
        panel_y = (self.screen.get_height() - panel_height) // 2
        
        pygame.draw.rect(self.screen, self.COLOR_PANEL, 
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, self.COLOR_BORDER, 
                        (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Заголовок
        self._draw_title(panel_x, panel_y, panel_width, level_system)
        
        # Полосы здоровья и выносливости
        y_offset = panel_y + 80
        y_offset = self._draw_bars(panel_x, y_offset, panel_width, stats)
        
        # Опыт
        y_offset = self._draw_experience(panel_x, y_offset, panel_width, level_system)
        
        # Характеристики
        y_offset = self._draw_stats(panel_x, y_offset, panel_width, stats, modifier_manager)
        
        # Модификаторы
        if modifier_manager:
            self._draw_modifiers(panel_x, y_offset, panel_width, modifier_manager)
        
        # Подсказка
        self._draw_hint(panel_x, panel_y + panel_height - 40, panel_width)
    
    def _draw_title(self, x: int, y: int, width: int, level_system: LevelSystem):
        """Отрисовать заголовок"""
        title = self.font_title.render("ХАРАКТЕРИСТИКИ", True, self.COLOR_TEXT)
        title_rect = title.get_rect(center=(x + width // 2, y + 30))
        self.screen.blit(title, title_rect)
        
        # Уровень
        level_text = self.font_normal.render(f"Уровень {level_system.level}", True, self.COLOR_EXP)
        level_rect = level_text.get_rect(center=(x + width // 2, y + 60))
        self.screen.blit(level_text, level_rect)
    
    def _draw_bars(self, x: int, y: int, width: int, stats: PlayerStats) -> int:
        """Отрисовать полосы здоровья и выносливости"""
        bar_width = width - 80
        bar_height = 25
        bar_x = x + 40
        
        # Здоровье
        self._draw_bar(bar_x, y, bar_width, bar_height, 
                      stats.health, stats.max_health, 
                      self.COLOR_HEALTH, "Здоровье")
        
        # Выносливость
        self._draw_bar(bar_x, y + 40, bar_width, bar_height,
                      stats.stamina, stats.max_stamina,
                      self.COLOR_STAMINA, "Выносливость")
        
        return y + 100
    
    def _draw_bar(self, x: int, y: int, width: int, height: int,
                  current: int, maximum: int, color: Tuple[int, int, int], label: str):
        """Отрисовать одну полосу"""
        # Фон
        pygame.draw.rect(self.screen, (30, 30, 40), (x, y, width, height))
        pygame.draw.rect(self.screen, self.COLOR_BORDER, (x, y, width, height), 1)
        
        # Заполнение
        fill_width = int(width * (current / maximum))
        if fill_width > 0:
            pygame.draw.rect(self.screen, color, (x, y, fill_width, height))
        
        # Текст
        text = self.font_small.render(f"{label}: {current}/{maximum}", True, self.COLOR_TEXT)
        text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text, text_rect)
    
    def _draw_experience(self, x: int, y: int, width: int, level_system: LevelSystem) -> int:
        """Отрисовать опыт"""
        bar_width = width - 80
        bar_height = 20
        bar_x = x + 40
        
        # Полоса опыта
        pygame.draw.rect(self.screen, (30, 30, 40), (bar_x, y, bar_width, bar_height))
        pygame.draw.rect(self.screen, self.COLOR_BORDER, (bar_x, y, bar_width, bar_height), 1)
        
        # Заполнение
        progress = level_system.get_level_progress()
        fill_width = int(bar_width * progress)
        if fill_width > 0:
            pygame.draw.rect(self.screen, self.COLOR_EXP, (bar_x, y, fill_width, bar_height))
        
        # Текст опыта (зелёный для контраста с жёлтым фоном)
        exp_text = f"Опыт: {level_system.experience}/{level_system.exp_to_next_level}"
        text = self.font_small.render(exp_text, True, (50, 255, 50))  # Ярко-зелёный
        text_rect = text.get_rect(center=(bar_x + bar_width // 2, y + bar_height // 2))
        self.screen.blit(text, text_rect)
        
        # Очки способностей
        if level_system.ability_points > 0:
            ap_text = f"Очки способностей: {level_system.ability_points}"
            ap_surface = self.font_normal.render(ap_text, True, self.COLOR_POSITIVE)
            self.screen.blit(ap_surface, (bar_x, y + 30))
            return y + 70
        
        return y + 40
    
    def _draw_stats(self, x: int, y: int, width: int, stats: PlayerStats,
                   modifier_manager: Optional[ModifierManager]) -> int:
        """Отрисовать характеристики"""
        y += 10
        
        # Разделитель
        pygame.draw.line(self.screen, self.COLOR_BORDER, 
                        (x + 40, y), (x + width - 40, y), 1)
        y += 20
        
        col_width = (width - 80) // 2
        left_x = x + 40
        right_x = x + 40 + col_width
        
        # Левая колонка - боевые характеристики
        y_left = y
        y_left = self._draw_stat_category(left_x, y_left, "БОЕВЫЕ", [
            ("Атака", stats.attack, "attack", modifier_manager),
            ("Защита", stats.defense, "defense", modifier_manager),
            ("Точность", f"{int(stats.accuracy * 100)}%", None, None),
            ("Уклонение", f"{int(stats.evasion * 100)}%", None, None),
            ("Крит. шанс", f"{int(stats.critical_chance * 100)}%", None, None),
            ("Крит. урон", f"x{stats.critical_damage}", None, None),
        ])
        
        # Правая колонка - исследовательские характеристики
        y_right = y
        y_right = self._draw_stat_category(right_x, y_right, "ИССЛЕДОВАНИЕ", [
            ("Восприятие", stats.perception, "perception", modifier_manager),
            ("Интеллект", stats.intelligence, "intelligence", modifier_manager),
            ("Удача", stats.luck, "luck", modifier_manager),
            ("Скорость", f"x{stats.movement_speed}", None, None),
        ])
        
        return max(y_left, y_right) + 20
    
    def _draw_stat_category(self, x: int, y: int, title: str, 
                           stats_list: list) -> int:
        """Отрисовать категорию характеристик"""
        # Заголовок категории
        title_surface = self.font_normal.render(title, True, self.COLOR_TEXT)
        self.screen.blit(title_surface, (x, y))
        y += 30
        
        # Характеристики
        for stat_name, stat_value, modifier_key, modifier_manager in stats_list:
            y = self._draw_single_stat(x, y, stat_name, stat_value, 
                                      modifier_key, modifier_manager)
        
        return y
    
    def _draw_single_stat(self, x: int, y: int, name: str, value,
                         modifier_key: Optional[str],
                         modifier_manager: Optional[ModifierManager]) -> int:
        """Отрисовать одну характеристику"""
        # Название
        name_surface = self.font_small.render(f"{name}:", True, self.COLOR_TEXT_DIM)
        self.screen.blit(name_surface, (x, y))
        
        # Значение
        value_str = str(value) if isinstance(value, (int, float)) else value
        value_surface = self.font_small.render(value_str, True, self.COLOR_TEXT)
        self.screen.blit(value_surface, (x + 120, y))
        
        # Модификаторы
        if modifier_key and modifier_manager and isinstance(value, (int, float)):
            modified = modifier_manager.calculate_modified_value(value, modifier_key)
            if abs(modified - value) > 0.01:
                diff = modified - value
                color = self.COLOR_POSITIVE if diff > 0 else self.COLOR_NEGATIVE
                sign = "+" if diff > 0 else ""
                mod_text = f"({sign}{diff:.1f})"
                mod_surface = self.font_small.render(mod_text, True, color)
                self.screen.blit(mod_surface, (x + 180, y))
        
        return y + 25
    
    def _draw_modifiers(self, x: int, y: int, width: int, 
                       modifier_manager: ModifierManager):
        """Отрисовать активные модификаторы"""
        modifiers = modifier_manager.get_all_active_modifiers()
        if not modifiers:
            return
        
        # Разделитель
        pygame.draw.line(self.screen, self.COLOR_BORDER,
                        (x + 40, y), (x + width - 40, y), 1)
        y += 20
        
        # Заголовок
        title = self.font_normal.render("АКТИВНЫЕ ЭФФЕКТЫ", True, self.COLOR_TEXT)
        self.screen.blit(title, (x + 40, y))
        y += 30
        
        # Модификаторы (показываем первые 5)
        for i, mod in enumerate(modifiers[:5]):
            if mod.description:
                text = self.font_small.render(f"• {mod.description}", True, self.COLOR_TEXT_DIM)
                self.screen.blit(text, (x + 50, y))
                
                # Длительность
                if not mod.is_permanent():
                    duration_text = f"({mod.duration} ходов)"
                    duration_surface = self.font_small.render(duration_text, True, self.COLOR_TEXT_DIM)
                    self.screen.blit(duration_surface, (x + width - 120, y))
                
                y += 22
        
        # Если модификаторов больше
        if len(modifiers) > 5:
            more_text = f"...и ещё {len(modifiers) - 5}"
            more_surface = self.font_small.render(more_text, True, self.COLOR_TEXT_DIM)
            self.screen.blit(more_surface, (x + 50, y))
    
    def _draw_hint(self, x: int, y: int, width: int):
        """Отрисовать подсказку"""
        hint = self.font_small.render("[C] Закрыть  [A] Способности", True, self.COLOR_TEXT_DIM)
        hint_rect = hint.get_rect(center=(x + width // 2, y))
        self.screen.blit(hint, hint_rect)
    
    def handle_input(self, event: pygame.event.Event) -> Optional[str]:
        """
        Обработать ввод
        
        Args:
            event: Событие pygame
            
        Returns:
            Команда ('close', 'abilities') или None
        """
        if not self.visible:
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c or event.key == pygame.K_ESCAPE:
                self.hide()
                return 'close'
            elif event.key == pygame.K_a:
                return 'abilities'
        
        return None
