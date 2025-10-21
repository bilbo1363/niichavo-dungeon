"""
UI дерева способностей
Версия: 0.4.0
Этап 0, Неделя 2, День 3
"""

import pygame
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from ..systems.abilities import Ability, AbilityTree, AbilityCategory, AbilityType
from ..systems.stats import PlayerStats
from ..systems.level_system import LevelSystem


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
        
        # Шрифты
        pygame.font.init()
        self.font_title = pygame.font.Font(None, 32)
        self.font_normal = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # Прокрутка
        self.scroll_offset = 0
        self.max_scroll = 0
    
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
        
        # Корректируем позицию с учётом прокрутки
        y = node.y - self.scroll_offset
        rect = pygame.Rect(node.x, y, node.width, node.height)
        
        # Пропускаем узлы вне экрана
        if y + node.height < 0 or y > self.height:
            return
        
        # Цвет узла
        node_color = self._get_node_color(ability)
        
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
        
        # Подсказка по управлению
        help_text = "ЛКМ - разблокировать | Колесо мыши - прокрутка | ESC - закрыть"
        help_surf = self.font_small.render(help_text, True, COLORS['text_dim'])
        help_rect = help_surf.get_rect(centerx=self.screen.get_width() // 2,
                                       bottom=self.y + self.height - 10)
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
                adjusted_pos = (mouse_pos[0], mouse_pos[1] + self.scroll_offset)
                
                # Проверяем клик по узлу
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
                print(f"✅ Разблокирована способность: {self.ability_tree.available_abilities[ability_id].name}")
