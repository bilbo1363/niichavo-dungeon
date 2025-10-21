"""
UI дерева способностей
Версия: 0.4.0
Этап 0, Неделя 2, День 4-5
"""

import pygame
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from ..systems.abilities import Ability, AbilityTree, AbilityCategory, AbilityType
from ..systems.stats import PlayerStats
from ..systems.level_system import LevelSystem
from ..systems.modifiers import StatModifier


# Цветовая схема
COLORS = {
    'bg': (20, 20, 30),
    'panel': (30, 30, 45),
    'border': (60, 60, 80),
    'text': (220, 220, 230),
    'text_dim': (140, 140, 150),
    'locked': (80, 80, 90),
    'available': (100, 180, 100),
    'unlocked': (50, 150, 255),
    'active': (255, 200, 50),
    'line': (60, 60, 80),
    'line_unlocked': (50, 150, 255),
    'hover': (255, 255, 255),
    'category_combat': (220, 80, 80),
    'category_survival': (80, 180, 80),
    'category_exploration': (80, 150, 220),
    'category_crafting': (200, 150, 80),
    'category_magic': (180, 80, 220),
}


@dataclass
class AbilityNode:
    """Узел способности в дереве"""
    ability: Ability
    x: int
    y: int
    width: int = 120
    height: int = 100
    
    def get_rect(self) -> pygame.Rect:
        """Получить прямоугольник узла"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_center(self) -> Tuple[int, int]:
        """Получить центр узла"""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def contains_point(self, pos: Tuple[int, int]) -> bool:
        """Проверить, содержит ли узел точку"""
        return self.get_rect().collidepoint(pos)


class AbilityTreeUI:
    """UI для дерева способностей"""
    
    def __init__(self, screen: pygame.Surface, ability_tree: AbilityTree,
                 player_stats: PlayerStats, level_system: LevelSystem):
        """
        Инициализация UI дерева способностей
        
        Args:
            screen: Поверхность для рисования
            ability_tree: Система дерева способностей
            player_stats: Характеристики игрока
            level_system: Система уровней
        """
        self.screen = screen
        self.ability_tree = ability_tree
        self.player_stats = player_stats
        self.level_system = level_system
        
        # Размеры и позиции
        self.width = screen.get_width() - 100
        self.height = screen.get_height() - 100
        self.x = 50
        self.y = 50
        
        # Узлы дерева
        self.nodes: Dict[str, AbilityNode] = {}
        self._build_tree_layout()
        
        # Состояние UI
        self.selected_category: Optional[AbilityCategory] = None
        self.hovered_node: Optional[str] = None
        self.selected_node: Optional[str] = None
        
        # Фильтры
        self.show_locked = True
        self.show_available = True
        self.show_unlocked = True
        
        # Tooltip
        self.tooltip_visible = False
        self.tooltip_ability: Optional[Ability] = None
        self.tooltip_alpha = 0
        self.tooltip_target_alpha = 0
        
        # Анимации
        self.unlock_animations: Dict[str, float] = {}  # ability_id -> progress (0-1)
        self.pulse_animations: Dict[str, float] = {}   # ability_id -> phase (0-2π)
        
        # Шрифты
        pygame.font.init()
        self.font_title = pygame.font.Font(None, 32)
        self.font_normal = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        self.font_tiny = pygame.font.Font(None, 16)
        
        # Прокрутка
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Кнопки фильтров
        self._build_filter_buttons()
    
    def _build_tree_layout(self):
        """Построить расположение узлов дерева"""
        # Группируем способности по категориям и уровням
        categories: Dict[AbilityCategory, Dict[int, List[Ability]]] = {}
        
        for ability in self.ability_tree.available_abilities.values():
            if ability.category not in categories:
                categories[ability.category] = {}
            
            tier = ability.tier
            if tier not in categories[ability.category]:
                categories[ability.category][tier] = []
            
            categories[ability.category][tier].append(ability)
        
        # Размещаем узлы
        node_width = 120
        node_height = 100
        horizontal_spacing = 160
        vertical_spacing = 140
        category_spacing = 200
        
        current_y = self.y + 80
        
        for category, tiers in sorted(categories.items(), key=lambda x: x[0].value):
            # Заголовок категории
            current_x = self.x + 20
            
            # Размещаем способности по уровням
            max_tier = max(tiers.keys())
            for tier in range(1, max_tier + 1):
                if tier not in tiers:
                    continue
                
                abilities = tiers[tier]
                # Центрируем способности одного уровня
                tier_width = len(abilities) * horizontal_spacing
                start_x = current_x + (self.width - tier_width) // 2
                
                for i, ability in enumerate(abilities):
                    x = start_x + i * horizontal_spacing
                    y = current_y + (tier - 1) * vertical_spacing
                    
                    node = AbilityNode(
                        ability=ability,
                        x=x,
                        y=y,
                        width=node_width,
                        height=node_height
                    )
                    self.nodes[ability.id] = node
            
            # Переход к следующей категории
            current_y += (max_tier + 1) * vertical_spacing + category_spacing
        
        # Вычисляем максимальную прокрутку
        if self.nodes:
            max_y = max(node.y + node.height for node in self.nodes.values())
            self.max_scroll = max(0, max_y - self.height + 100)
    
    def _get_category_color(self, category: AbilityCategory) -> Tuple[int, int, int]:
        """Получить цвет категории"""
        color_map = {
            AbilityCategory.COMBAT: COLORS['category_combat'],
            AbilityCategory.SURVIVAL: COLORS['category_survival'],
            AbilityCategory.EXPLORATION: COLORS['category_exploration'],
            AbilityCategory.CRAFTING: COLORS['category_crafting'],
            AbilityCategory.MAGIC: COLORS['category_magic'],
        }
        return color_map.get(category, COLORS['text'])
    
    def _get_node_color(self, ability: Ability) -> Tuple[int, int, int]:
        """Получить цвет узла в зависимости от состояния"""
        if ability.id in self.ability_tree.unlocked_abilities:
            return COLORS['unlocked']
        elif self.ability_tree.can_unlock(
            ability.id,
            self.level_system.level,
            self.level_system.ability_points,
            self._get_player_stats_dict()
        ):
            return COLORS['available']
        else:
            return COLORS['locked']
    
    def _get_player_stats_dict(self) -> Dict[str, int]:
        """Получить характеристики игрока в виде словаря"""
        return {
            'attack': self.player_stats.attack,
            'defense': self.player_stats.defense,
            'perception': self.player_stats.perception,
            'intelligence': self.player_stats.intelligence,
            'luck': self.player_stats.luck,
        }
    
    def _draw_connection_line(self, from_node: AbilityNode, to_node: AbilityNode,
                             unlocked: bool = False):
        """Нарисовать линию связи между узлами"""
        from_center = from_node.get_center()
        to_center = to_node.get_center()
        
        # Корректируем позиции с учётом прокрутки
        from_pos = (from_center[0], from_center[1] - self.scroll_offset)
        to_pos = (to_center[0], to_center[1] - self.scroll_offset)
        
        color = COLORS['line_unlocked'] if unlocked else COLORS['line']
        width = 3 if unlocked else 2
        
        pygame.draw.line(self.screen, color, from_pos, to_pos, width)
    
    def _draw_node(self, node: AbilityNode):
        """Нарисовать узел способности"""
        ability = node.ability
        
        # Проверяем фильтры
        if not self._should_show_node(ability):
            return
        
        # Корректируем позицию с учётом прокрутки
        y = node.y - self.scroll_offset
        rect = pygame.Rect(node.x, y, node.width, node.height)
        
        # Пропускаем узлы вне экрана
        if y + node.height < 0 or y > self.height:
            return
        
        # Цвет узла
        node_color = self._get_node_color(ability)
        
        # Анимация пульсации для доступных способностей
        import math
        pulse_scale = 1.0
        if ability.id in self.pulse_animations:
            pulse = math.sin(self.pulse_animations[ability.id]) * 0.5 + 0.5
            pulse_scale = 1.0 + pulse * 0.05
        
        # Анимация разблокировки
        unlock_scale = 1.0
        if ability.id in self.unlock_animations:
            progress = self.unlock_animations[ability.id]
            unlock_scale = 1.0 + math.sin(progress * math.pi) * 0.2
        
        # Применяем масштаб
        if pulse_scale != 1.0 or unlock_scale != 1.0:
            scale = pulse_scale * unlock_scale
            scaled_width = int(node.width * scale)
            scaled_height = int(node.height * scale)
            offset_x = (scaled_width - node.width) // 2
            offset_y = (scaled_height - node.height) // 2
            rect = pygame.Rect(node.x - offset_x, y - offset_y, scaled_width, scaled_height)
        
        # Подсветка при наведении
        if self.hovered_node == ability.id:
            border_color = COLORS['hover']
            border_width = 3
        else:
            border_color = COLORS['border']
            border_width = 2
        
        # Рисуем фон узла
        pygame.draw.rect(self.screen, COLORS['panel'], rect, border_radius=8)
        pygame.draw.rect(self.screen, border_color, rect, border_width, border_radius=8)
        
        # Цветная полоска категории
        category_color = self._get_category_color(ability.category)
        category_rect = pygame.Rect(rect.x, rect.y, rect.width, 5)
        pygame.draw.rect(self.screen, category_color, category_rect,
                        border_top_left_radius=8, border_top_right_radius=8)
        
        # Индикатор состояния (кружок)
        indicator_radius = 8
        indicator_x = rect.x + rect.width - indicator_radius - 5
        indicator_y = rect.y + indicator_radius + 8
        pygame.draw.circle(self.screen, node_color, (indicator_x, indicator_y),
                          indicator_radius)
        
        # Название способности
        name_lines = self._wrap_text(ability.name, node.width - 10, self.font_small)
        text_y = rect.y + 15
        for line in name_lines:
            text_surf = self.font_small.render(line, True, COLORS['text'])
            text_rect = text_surf.get_rect(centerx=rect.centerx, top=text_y)
            self.screen.blit(text_surf, text_rect)
            text_y += 18
        
        # Тип способности
        type_text = {
            AbilityType.PASSIVE: "Пассивная",
            AbilityType.ACTIVE: "Активная",
            AbilityType.TOGGLE: "Переключаемая"
        }[ability.ability_type]
        
        type_surf = self.font_small.render(type_text, True, COLORS['text_dim'])
        type_rect = type_surf.get_rect(centerx=rect.centerx, bottom=rect.bottom - 25)
        self.screen.blit(type_surf, type_rect)
        
        # Стоимость
        cost_text = f"Стоимость: {ability.cost}"
        cost_surf = self.font_small.render(cost_text, True, COLORS['text_dim'])
        cost_rect = cost_surf.get_rect(centerx=rect.centerx, bottom=rect.bottom - 8)
        self.screen.blit(cost_surf, cost_rect)
    
    def _wrap_text(self, text: str, max_width: int, font: pygame.font.Font) -> List[str]:
        """Разбить текст на строки по ширине"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def draw(self):
        """Отрисовать UI дерева способностей"""
        # Фон
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(self.screen, COLORS['bg'], bg_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS['border'], bg_rect, 2, border_radius=10)
        
        # Заголовок
        title_text = "Дерево способностей"
        title_surf = self.font_title.render(title_text, True, COLORS['text'])
        title_rect = title_surf.get_rect(centerx=self.screen.get_width() // 2, top=self.y + 10)
        self.screen.blit(title_surf, title_rect)
        
        # Информация об очках способностей
        points_text = f"Очки способностей: {self.level_system.ability_points}"
        points_surf = self.font_normal.render(points_text, True, COLORS['active'])
        points_rect = points_surf.get_rect(right=self.x + self.width - 20, top=self.y + 15)
        self.screen.blit(points_surf, points_rect)
        
        # Создаём поверхность для прокрутки
        scroll_surface = pygame.Surface((self.width, self.height - 60))
        scroll_surface.fill(COLORS['bg'])
        
        # Рисуем линии связей
        for ability_id, node in self.nodes.items():
            ability = node.ability
            if ability.requirements.required_abilities:
                for req_id in ability.requirements.required_abilities:
                    if req_id in self.nodes:
                        from_node = self.nodes[req_id]
                        unlocked = (req_id in self.ability_tree.unlocked_abilities and
                                  ability_id in self.ability_tree.unlocked_abilities)
                        self._draw_connection_line(from_node, node, unlocked)
        
        # Рисуем узлы
        for node in self.nodes.values():
            self._draw_node(node)
        
        # Рисуем кнопки фильтров
        self._draw_filter_buttons()
        
        # Рисуем tooltip
        self._draw_tooltip()
        
        # Подсказка по управлению
        help_text = "ЛКМ - разблокировать | Колесо мыши - прокрутка | ESC - закрыть"
        help_surf = self.font_small.render(help_text, True, COLORS['text_dim'])
        help_rect = help_surf.get_rect(centerx=self.screen.get_width() // 2,
                                       bottom=self.y + self.height - 80)
        self.screen.blit(help_surf, help_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Обработать событие
        
        Args:
            event: Событие pygame
            
        Returns:
            True если событие обработано
        """
        if event.type == pygame.MOUSEMOTION:
            # Обновляем наведение
            mouse_pos = event.pos
            adjusted_pos = (mouse_pos[0], mouse_pos[1] + self.scroll_offset)
            
            self.hovered_node = None
            for ability_id, node in self.nodes.items():
                if node.contains_point(adjusted_pos):
                    self.hovered_node = ability_id
                    break
            
            return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # ЛКМ
                mouse_pos = event.pos
                
                # Проверяем клик по кнопкам фильтров
                for key, rect in self.filter_buttons.items():
                    if rect.collidepoint(mouse_pos):
                        if key == 'locked':
                            self.show_locked = not self.show_locked
                        elif key == 'available':
                            self.show_available = not self.show_available
                        elif key == 'unlocked':
                            self.show_unlocked = not self.show_unlocked
                        return True
                
                # Проверяем клик по кнопкам категорий
                for category, rect in self.category_buttons.items():
                    if rect.collidepoint(mouse_pos):
                        if self.selected_category == category:
                            self.selected_category = None  # Снять фильтр
                        else:
                            self.selected_category = category
                        return True
                
                # Проверяем клик по узлу
                adjusted_pos = (mouse_pos[0], mouse_pos[1] + self.scroll_offset)
                for ability_id, node in self.nodes.items():
                    if node.contains_point(adjusted_pos):
                        self._try_unlock_ability(ability_id)
                        return True
            
            elif event.button == 4:  # Колесо вверх
                self.scroll_offset = max(0, self.scroll_offset - 30)
                return True
            
            elif event.button == 5:  # Колесо вниз
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 30)
                return True
        
        return False
    
    def _try_unlock_ability(self, ability_id: str):
        """Попытаться разблокировать способность"""
        if self.ability_tree.can_unlock(
            ability_id,
            self.level_system.level,
            self.level_system.ability_points,
            self._get_player_stats_dict()
        ):
            success = self.ability_tree.unlock_ability(ability_id)
            if success:
                # Тратим очко способности
                self.level_system.ability_points -= self.ability_tree.available_abilities[ability_id].cost
                # Запускаем анимацию разблокировки
                self.unlock_animations[ability_id] = 0.0
                print(f"✅ Разблокирована способность: {self.ability_tree.available_abilities[ability_id].name}")
    
    def _build_filter_buttons(self):
        """Построить кнопки фильтров"""
        button_width = 150
        button_height = 35
        button_spacing = 10
        start_x = self.x + 20
        start_y = self.y + self.height - button_height - 40
        
        self.filter_buttons = {
            'locked': pygame.Rect(start_x, start_y, button_width, button_height),
            'available': pygame.Rect(start_x + button_width + button_spacing, start_y, button_width, button_height),
            'unlocked': pygame.Rect(start_x + (button_width + button_spacing) * 2, start_y, button_width, button_height),
        }
        
        # Кнопки категорий
        cat_button_width = 120
        cat_start_x = self.x + self.width - (cat_button_width + button_spacing) * 5 - 20
        cat_y = self.y + 50
        
        self.category_buttons = {}
        for i, category in enumerate(AbilityCategory):
            x = cat_start_x + i * (cat_button_width + button_spacing)
            self.category_buttons[category] = pygame.Rect(x, cat_y, cat_button_width, 30)
    
    def _draw_filter_buttons(self):
        """Отрисовать кнопки фильтров"""
        # Фильтры состояния
        filter_labels = {
            'locked': ('Заблокировано', self.show_locked, COLORS['locked']),
            'available': ('Доступно', self.show_available, COLORS['available']),
            'unlocked': ('Разблокировано', self.show_unlocked, COLORS['unlocked']),
        }
        
        for key, (label, active, color) in filter_labels.items():
            rect = self.filter_buttons[key]
            
            # Фон кнопки
            bg_color = color if active else COLORS['panel']
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=5)
            pygame.draw.rect(self.screen, COLORS['border'], rect, 2, border_radius=5)
            
            # Текст
            text_color = COLORS['text'] if active else COLORS['text_dim']
            text_surf = self.font_small.render(label, True, text_color)
            text_rect = text_surf.get_rect(center=rect.center)
            self.screen.blit(text_surf, text_rect)
        
        # Кнопки категорий
        for category, rect in self.category_buttons.items():
            active = self.selected_category == category
            color = self._get_category_color(category)
            
            # Фон кнопки
            bg_color = color if active else COLORS['panel']
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=5)
            pygame.draw.rect(self.screen, COLORS['border'], rect, 2, border_radius=5)
            
            # Текст
            label = {
                AbilityCategory.COMBAT: "Боевые",
                AbilityCategory.SURVIVAL: "Выживание",
                AbilityCategory.EXPLORATION: "Исследование",
                AbilityCategory.CRAFTING: "Крафт",
                AbilityCategory.MAGIC: "Магия",
            }[category]
            
            text_color = COLORS['text'] if active else COLORS['text_dim']
            text_surf = self.font_tiny.render(label, True, text_color)
            text_rect = text_surf.get_rect(center=rect.center)
            self.screen.blit(text_surf, text_rect)
    
    def _draw_tooltip(self):
        """Отрисовать tooltip с информацией о способности"""
        if not self.hovered_node or self.hovered_node not in self.nodes:
            self.tooltip_target_alpha = 0
            return
        
        # Плавное появление
        self.tooltip_target_alpha = 255
        if self.tooltip_alpha < self.tooltip_target_alpha:
            self.tooltip_alpha = min(self.tooltip_alpha + 15, self.tooltip_target_alpha)
        elif self.tooltip_alpha > self.tooltip_target_alpha:
            self.tooltip_alpha = max(self.tooltip_alpha - 15, self.tooltip_target_alpha)
        
        if self.tooltip_alpha < 10:
            return
        
        ability = self.nodes[self.hovered_node].ability
        
        # Размеры tooltip
        tooltip_width = 350
        tooltip_padding = 15
        line_height = 20
        
        # Собираем текст
        lines = []
        lines.append(("title", ability.name))
        lines.append(("category", f"Категория: {self._get_category_name(ability.category)}"))
        lines.append(("type", f"Тип: {self._get_type_name(ability.ability_type)}"))
        lines.append(("space", ""))
        
        # Описание
        desc_lines = self._wrap_text(ability.description, tooltip_width - tooltip_padding * 2, self.font_small)
        for line in desc_lines:
            lines.append(("desc", line))
        
        lines.append(("space", ""))
        
        # Эффекты
        if ability.stat_modifiers:
            lines.append(("header", "Эффекты:"))
            for mod in ability.stat_modifiers:
                effect_text = self._format_modifier(mod)
                lines.append(("effect", f"  • {effect_text}"))
        
        # Требования
        lines.append(("space", ""))
        lines.append(("header", "Требования:"))
        
        req = ability.requirements
        if req.required_level > 1:
            level_met = self.level_system.level >= req.required_level
            color_key = "success" if level_met else "error"
            lines.append((color_key, f"  • Уровень: {req.required_level}"))
        
        if req.required_abilities:
            for req_id in req.required_abilities:
                req_ability = self.ability_tree.available_abilities.get(req_id)
                if req_ability:
                    unlocked = req_id in self.ability_tree.unlocked_abilities
                    color_key = "success" if unlocked else "error"
                    lines.append((color_key, f"  • {req_ability.name}"))
        
        if req.required_stats:
            for stat_name, min_value in req.required_stats.items():
                current = self._get_player_stats_dict().get(stat_name, 0)
                met = current >= min_value
                color_key = "success" if met else "error"
                lines.append((color_key, f"  • {stat_name.capitalize()}: {min_value}"))
        
        # Стоимость
        lines.append(("space", ""))
        has_points = self.level_system.ability_points >= ability.cost
        cost_color = "success" if has_points else "error"
        lines.append((cost_color, f"Стоимость: {ability.cost} очков"))
        
        # Вычисляем высоту tooltip
        tooltip_height = len(lines) * line_height + tooltip_padding * 2
        
        # Позиция tooltip (справа от курсора)
        mouse_pos = pygame.mouse.get_pos()
        tooltip_x = min(mouse_pos[0] + 20, self.screen.get_width() - tooltip_width - 10)
        tooltip_y = min(mouse_pos[1], self.screen.get_height() - tooltip_height - 10)
        
        # Создаём поверхность с прозрачностью
        tooltip_surf = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
        
        # Фон
        bg_color = (*COLORS['panel'], int(self.tooltip_alpha * 0.95))
        pygame.draw.rect(tooltip_surf, bg_color, (0, 0, tooltip_width, tooltip_height), border_radius=8)
        
        # Рамка
        border_color = (*COLORS['border'], int(self.tooltip_alpha))
        pygame.draw.rect(tooltip_surf, border_color, (0, 0, tooltip_width, tooltip_height), 2, border_radius=8)
        
        # Цветная полоска категории
        cat_color = (*self._get_category_color(ability.category), int(self.tooltip_alpha))
        pygame.draw.rect(tooltip_surf, cat_color, (0, 0, tooltip_width, 5), border_top_left_radius=8, border_top_right_radius=8)
        
        # Текст
        y = tooltip_padding
        for line_type, text in lines:
            if line_type == "space":
                y += line_height // 2
                continue
            
            # Выбираем цвет и шрифт
            if line_type == "title":
                font = self.font_normal
                color = (*COLORS['text'], int(self.tooltip_alpha))
            elif line_type == "header":
                font = self.font_small
                color = (*COLORS['active'], int(self.tooltip_alpha))
            elif line_type == "success":
                font = self.font_small
                color = (*COLORS['available'], int(self.tooltip_alpha))
            elif line_type == "error":
                font = self.font_small
                color = (*COLORS['locked'], int(self.tooltip_alpha))
            else:
                font = self.font_small
                color = (*COLORS['text_dim'], int(self.tooltip_alpha))
            
            text_surf = font.render(text, True, color)
            tooltip_surf.blit(text_surf, (tooltip_padding, y))
            y += line_height
        
        # Рисуем tooltip на экране
        self.screen.blit(tooltip_surf, (tooltip_x, tooltip_y))
    
    def _format_modifier(self, mod: StatModifier) -> str:
        """Форматировать модификатор для отображения"""
        from ..systems.modifiers import ModifierType
        
        stat_names = {
            'attack': 'Атака',
            'defense': 'Защита',
            'max_health': 'Макс. здоровье',
            'max_stamina': 'Макс. выносливость',
            'perception': 'Восприятие',
            'intelligence': 'Интеллект',
            'luck': 'Удача',
            'critical_chance': 'Шанс крита',
            'evasion': 'Уклонение',
        }
        
        stat_name = stat_names.get(mod.stat_name, mod.stat_name)
        
        if mod.modifier_type == ModifierType.FLAT:
            sign = "+" if mod.value >= 0 else ""
            return f"{stat_name} {sign}{int(mod.value)}"
        elif mod.modifier_type == ModifierType.PERCENT:
            sign = "+" if mod.value >= 0 else ""
            return f"{stat_name} {sign}{int(mod.value * 100)}%"
        else:
            return f"{stat_name} x{mod.value}"
    
    def _get_category_name(self, category: AbilityCategory) -> str:
        """Получить название категории"""
        names = {
            AbilityCategory.COMBAT: "Боевые",
            AbilityCategory.SURVIVAL: "Выживание",
            AbilityCategory.EXPLORATION: "Исследование",
            AbilityCategory.CRAFTING: "Крафт",
            AbilityCategory.MAGIC: "Магия",
        }
        return names.get(category, "Неизвестно")
    
    def _get_type_name(self, ability_type: AbilityType) -> str:
        """Получить название типа способности"""
        names = {
            AbilityType.PASSIVE: "Пассивная",
            AbilityType.ACTIVE: "Активная",
            AbilityType.TOGGLE: "Переключаемая",
        }
        return names.get(ability_type, "Неизвестно")
    
    def _should_show_node(self, ability: Ability) -> bool:
        """Проверить, нужно ли показывать узел с учётом фильтров"""
        # Фильтр по категории
        if self.selected_category and ability.category != self.selected_category:
            return False
        
        # Фильтр по состоянию
        is_unlocked = ability.id in self.ability_tree.unlocked_abilities
        is_available = self.ability_tree.can_unlock(
            ability.id,
            self.level_system.level,
            self.level_system.ability_points,
            self._get_player_stats_dict()
        )
        
        if is_unlocked and not self.show_unlocked:
            return False
        if is_available and not is_unlocked and not self.show_available:
            return False
        if not is_available and not is_unlocked and not self.show_locked:
            return False
        
        return True
    
    def update(self, dt: float):
        """
        Обновить анимации
        
        Args:
            dt: Время с последнего кадра в секундах
        """
        # Обновляем анимации разблокировки
        to_remove = []
        for ability_id, progress in self.unlock_animations.items():
            self.unlock_animations[ability_id] = min(progress + dt * 2, 1.0)
            if self.unlock_animations[ability_id] >= 1.0:
                to_remove.append(ability_id)
        
        for ability_id in to_remove:
            del self.unlock_animations[ability_id]
        
        # Обновляем пульсацию доступных способностей
        import math
        for ability_id, node in self.nodes.items():
            if self.ability_tree.can_unlock(
                ability_id,
                self.level_system.level,
                self.level_system.ability_points,
                self._get_player_stats_dict()
            ) and ability_id not in self.ability_tree.unlocked_abilities:
                if ability_id not in self.pulse_animations:
                    self.pulse_animations[ability_id] = 0
                self.pulse_animations[ability_id] = (self.pulse_animations[ability_id] + dt * 2) % (2 * math.pi)
            elif ability_id in self.pulse_animations:
                del self.pulse_animations[ability_id]
