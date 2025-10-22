"""
UI для улучшения крафт-станций
Версия: 0.4.0
Этап 0, Неделя 3, День 3-4
"""

import pygame
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from ..objects.crafting_stations import CraftingStation, StationUpgrade, StationManager


# Цветовая схема
COLORS = {
    'bg': (20, 20, 30),
    'panel': (30, 30, 45),
    'panel_light': (40, 40, 55),
    'border': (60, 60, 80),
    'text': (220, 220, 230),
    'text_dim': (140, 140, 150),
    'success': (100, 180, 100),
    'error': (220, 80, 80),
    'warning': (220, 180, 80),
    'active': (255, 200, 50),
    'hover': (255, 255, 255),
    'tier1': (150, 150, 150),
    'tier2': (100, 180, 255),
    'tier3': (255, 200, 50),
}


@dataclass
class StationCard:
    """Карточка станции"""
    station: CraftingStation
    x: int
    y: int
    width: int = 250
    height: int = 150
    
    def get_rect(self) -> pygame.Rect:
        """Получить прямоугольник карточки"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def contains_point(self, pos: Tuple[int, int]) -> bool:
        """Проверить, содержит ли карточка точку"""
        return self.get_rect().collidepoint(pos)


class StationUpgradeUI:
    """UI для улучшения станций"""
    
    def __init__(self, screen: pygame.Surface, station_manager: StationManager,
                 player_level: int, player_inventory: Dict[str, int], player_money: int,
                 crafting_system=None):
        """
        Инициализация UI
        
        Args:
            screen: Поверхность для рисования
            station_manager: Менеджер станций
            player_level: Уровень игрока
            player_inventory: Инвентарь игрока
            player_money: Деньги игрока
        """
        self.screen = screen
        self.station_manager = station_manager
        self.crafting_system = crafting_system
        self.player_level = player_level
        self.player_inventory = player_inventory
        self.player_money = player_money
        
        # Очередь скрафченных предметов
        self.crafted_queue = []
        
        # Кэш базы данных предметов (создаём ОДИН РАЗ!)
        from ..items.item import ItemDatabase
        self.item_db = ItemDatabase()
        
        # Размеры и позиции
        self.width = screen.get_width() - 100
        self.height = screen.get_height() - 100
        self.x = 50
        self.y = 50
        
        # Карточки станций
        self.cards: List[StationCard] = []
        self._build_cards()
        
        # Состояние UI
        self.selected_station: Optional[CraftingStation] = None
        self.hovered_card: Optional[str] = None
        self.view_mode = "recipes"  # "recipes" или "upgrade"
        self.selected_recipe = None
        self.show_upgrade_panel = False
        
        # Анимация улучшения
        self.upgrade_animation_progress = 0.0
        self.upgrading_station: Optional[str] = None
        
        # Шрифты
        pygame.font.init()
        self.font_title = pygame.font.Font(None, 32)
        self.font_normal = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        self.font_tiny = pygame.font.Font(None, 16)
        
        # Прокрутка
        self.scroll_offset = 0
        self.max_scroll = 0
    
    def _build_cards(self):
        """Построить карточки станций"""
        self.cards = []
        
        card_width = 250
        card_height = 150
        cards_per_row = 3
        horizontal_spacing = 20
        vertical_spacing = 20
        
        start_x = self.x + 20
        start_y = self.y + 80
        
        unlocked_stations = self.station_manager.get_unlocked_stations()
        
        for i, station in enumerate(unlocked_stations):
            row = i // cards_per_row
            col = i % cards_per_row
            
            x = start_x + col * (card_width + horizontal_spacing)
            y = start_y + row * (card_height + vertical_spacing)
            
            card = StationCard(
                station=station,
                x=x,
                y=y,
                width=card_width,
                height=card_height
            )
            self.cards.append(card)
        
        # Вычисляем максимальную прокрутку
        if self.cards:
            max_y = max(card.y + card.height for card in self.cards)
            self.max_scroll = max(0, max_y - self.height + 100)
    
    def _get_tier_color(self, tier: int) -> Tuple[int, int, int]:
        """Получить цвет для tier"""
        if tier == 1:
            return COLORS['tier1']
        elif tier == 2:
            return COLORS['tier2']
        else:
            return COLORS['tier3']
    
    def _draw_station_card(self, card: StationCard):
        """Нарисовать карточку станции"""
        station = card.station
        
        # Корректируем позицию с учётом прокрутки
        y = card.y - self.scroll_offset
        rect = pygame.Rect(card.x, y, card.width, card.height)
        
        # Пропускаем карточки вне экрана
        if y + card.height < 0 or y > self.height:
            return
        
        # Подсветка при наведении
        if self.hovered_card == station.id:
            border_color = COLORS['hover']
            border_width = 3
        else:
            border_color = COLORS['border']
            border_width = 2
        
        # Фон карточки
        pygame.draw.rect(self.screen, COLORS['panel'], rect, border_radius=8)
        pygame.draw.rect(self.screen, border_color, rect, border_width, border_radius=8)
        
        # Цветная полоска tier
        tier_color = self._get_tier_color(station.current_tier)
        tier_rect = pygame.Rect(rect.x, rect.y, rect.width, 5)
        pygame.draw.rect(self.screen, tier_color, tier_rect,
                        border_top_left_radius=8, border_top_right_radius=8)
        
        # Название станции
        name_surf = self.font_normal.render(station.name, True, COLORS['text'])
        name_rect = name_surf.get_rect(centerx=rect.centerx, top=rect.y + 15)
        self.screen.blit(name_surf, name_rect)
        
        # Текущий tier
        tier_text = f"Уровень {station.current_tier}"
        tier_surf = self.font_small.render(tier_text, True, tier_color)
        tier_rect_pos = tier_surf.get_rect(centerx=rect.centerx, top=rect.y + 45)
        self.screen.blit(tier_surf, tier_rect_pos)
        
        # Бонусы
        speed_bonus = (station.get_crafting_speed_multiplier() - 1.0) * 100
        quality_bonus = station.get_quality_bonus() * 100
        
        bonus_y = rect.y + 75
        if speed_bonus > 0:
            speed_text = f"Скорость: +{int(speed_bonus)}%"
            speed_surf = self.font_tiny.render(speed_text, True, COLORS['success'])
            speed_rect = speed_surf.get_rect(centerx=rect.centerx, top=bonus_y)
            self.screen.blit(speed_surf, speed_rect)
            bonus_y += 18
        
        if quality_bonus > 0:
            quality_text = f"Качество: +{int(quality_bonus)}%"
            quality_surf = self.font_tiny.render(quality_text, True, COLORS['success'])
            quality_rect = quality_surf.get_rect(centerx=rect.centerx, top=bonus_y)
            self.screen.blit(quality_surf, quality_rect)
        
        # Кнопка улучшения
        next_tier = station.current_tier + 1
        if next_tier in station.upgrades:
            can_upgrade = station.can_upgrade(
                self.player_level,
                self.player_inventory,
                self.player_money
            )
            
            button_color = COLORS['success'] if can_upgrade else COLORS['text_dim']
            button_text = "Улучшить"
            button_surf = self.font_small.render(button_text, True, button_color)
            button_rect = button_surf.get_rect(centerx=rect.centerx, bottom=rect.bottom - 10)
            self.screen.blit(button_surf, button_rect)
        else:
            max_text = "МАКС"
            max_surf = self.font_small.render(max_text, True, COLORS['active'])
            max_rect = max_surf.get_rect(centerx=rect.centerx, bottom=rect.bottom - 10)
            self.screen.blit(max_surf, max_rect)
    
    def _draw_inventory_panel(self):
        """Отрисовать панель инвентаря"""
        # Позиция справа от панели рецептов
        panel_x = self.x + 250 + (self.width - 270) // 2 + 20
        panel_y = self.y + 80
        panel_width = (self.width - 270) // 2 - 40
        panel_height = self.height - 120
        
        # Фон панели
        pygame.draw.rect(self.screen, COLORS['panel'], 
                        (panel_x, panel_y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(self.screen, COLORS['border'], 
                        (panel_x, panel_y, panel_width, panel_height), 2, border_radius=10)
        
        # Заголовок
        title_text = "Инвентарь"
        title_surf = self.font_normal.render(title_text, True, COLORS['text'])
        self.screen.blit(title_surf, (panel_x + 20, panel_y + 15))
        
        # Список предметов
        y_offset = panel_y + 60
        
        if not self.player_inventory:
            no_items_text = "Инвентарь пуст"
            no_items_surf = self.font_small.render(no_items_text, True, COLORS['text_dim'])
            self.screen.blit(no_items_surf, (panel_x + 20, y_offset))
            return
        
        # Отображаем предметы (используем кэшированную базу)
        for item_id, quantity in sorted(self.player_inventory.items()):
            item = self.item_db.get_item(item_id)
            if not item:
                continue
            
            # Имя предмета
            item_text = f"{item.name} x{quantity}"
            item_surf = self.font_small.render(item_text, True, COLORS['text'])
            self.screen.blit(item_surf, (panel_x + 20, y_offset))
            
            y_offset += 30
            
            # Ограничение по высоте
            if y_offset > panel_y + panel_height - 40:
                more_text = "..."
                more_surf = self.font_small.render(more_text, True, COLORS['text_dim'])
                self.screen.blit(more_surf, (panel_x + 20, y_offset))
                break
    
    def _draw_upgrade_panel(self):
        """Нарисовать панель улучшения"""
        if not self.selected_station:
            return
        
        station = self.selected_station
        next_tier = station.current_tier + 1
        
        if next_tier not in station.upgrades:
            return
        
        upgrade = station.upgrades[next_tier]
        
        # Размеры панели
        panel_width = 500
        panel_height = 400
        panel_x = (self.screen.get_width() - panel_width) // 2
        panel_y = (self.screen.get_height() - panel_height) // 2
        
        # Фон панели
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, COLORS['panel_light'], panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS['border'], panel_rect, 3, border_radius=10)
        
        # Заголовок
        title_text = f"Улучшение: {upgrade.name}"
        title_surf = self.font_title.render(title_text, True, COLORS['text'])
        title_rect = title_surf.get_rect(centerx=panel_rect.centerx, top=panel_y + 20)
        self.screen.blit(title_surf, title_rect)
        
        # Описание
        desc_surf = self.font_small.render(upgrade.description, True, COLORS['text_dim'])
        desc_rect = desc_surf.get_rect(centerx=panel_rect.centerx, top=panel_y + 60)
        self.screen.blit(desc_surf, desc_rect)
        
        # Требования
        req_y = panel_y + 100
        
        # Уровень
        level_met = self.player_level >= upgrade.required_level
        level_color = COLORS['success'] if level_met else COLORS['error']
        level_text = f"Уровень: {upgrade.required_level}"
        level_surf = self.font_normal.render(level_text, True, level_color)
        level_rect = level_surf.get_rect(left=panel_x + 30, top=req_y)
        self.screen.blit(level_surf, level_rect)
        req_y += 30
        
        # Деньги
        money_met = self.player_money >= upgrade.cost
        money_color = COLORS['success'] if money_met else COLORS['error']
        money_text = f"Стоимость: {upgrade.cost} монет"
        money_surf = self.font_normal.render(money_text, True, money_color)
        money_rect = money_surf.get_rect(left=panel_x + 30, top=req_y)
        self.screen.blit(money_surf, money_rect)
        req_y += 30
        
        # Материалы
        if upgrade.required_materials:
            materials_title = "Материалы:"
            materials_surf = self.font_normal.render(materials_title, True, COLORS['text'])
            materials_rect = materials_surf.get_rect(left=panel_x + 30, top=req_y)
            self.screen.blit(materials_surf, materials_rect)
            req_y += 25
            
            for item_id, required_count in upgrade.required_materials.items():
                current_count = self.player_inventory.get(item_id, 0)
                has_enough = current_count >= required_count
                mat_color = COLORS['success'] if has_enough else COLORS['error']
                
                mat_text = f"  • {item_id}: {current_count}/{required_count}"
                mat_surf = self.font_small.render(mat_text, True, mat_color)
                mat_rect = mat_surf.get_rect(left=panel_x + 40, top=req_y)
                self.screen.blit(mat_surf, mat_rect)
                req_y += 22
        
        # Бонусы
        req_y += 20
        bonuses_title = "Бонусы:"
        bonuses_surf = self.font_normal.render(bonuses_title, True, COLORS['active'])
        bonuses_rect = bonuses_surf.get_rect(left=panel_x + 30, top=req_y)
        self.screen.blit(bonuses_surf, bonuses_rect)
        req_y += 25
        
        if upgrade.crafting_speed_bonus > 0:
            speed_text = f"  • Скорость крафта: +{int(upgrade.crafting_speed_bonus * 100)}%"
            speed_surf = self.font_small.render(speed_text, True, COLORS['success'])
            speed_rect = speed_surf.get_rect(left=panel_x + 40, top=req_y)
            self.screen.blit(speed_surf, speed_rect)
            req_y += 22
        
        if upgrade.quality_bonus > 0:
            quality_text = f"  • Качество: +{int(upgrade.quality_bonus * 100)}%"
            quality_surf = self.font_small.render(quality_text, True, COLORS['success'])
            quality_rect = quality_surf.get_rect(left=panel_x + 40, top=req_y)
            self.screen.blit(quality_surf, quality_rect)
            req_y += 22
        
        if upgrade.unlocked_recipes:
            recipes_text = f"  • Новых рецептов: {len(upgrade.unlocked_recipes)}"
            recipes_surf = self.font_small.render(recipes_text, True, COLORS['success'])
            recipes_rect = recipes_surf.get_rect(left=panel_x + 40, top=req_y)
            self.screen.blit(recipes_surf, recipes_rect)
        
        # Кнопки
        button_y = panel_y + panel_height - 60
        
        # Кнопка "Улучшить"
        can_upgrade = station.can_upgrade(
            self.player_level,
            self.player_inventory,
            self.player_money
        )
        
        upgrade_button_rect = pygame.Rect(panel_x + 50, button_y, 180, 40)
        upgrade_button_color = COLORS['success'] if can_upgrade else COLORS['text_dim']
        pygame.draw.rect(self.screen, upgrade_button_color, upgrade_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, COLORS['border'], upgrade_button_rect, 2, border_radius=5)
        
        upgrade_text = "Улучшить"
        upgrade_surf = self.font_normal.render(upgrade_text, True, COLORS['text'])
        upgrade_text_rect = upgrade_surf.get_rect(center=upgrade_button_rect.center)
        self.screen.blit(upgrade_surf, upgrade_text_rect)
        
        # Кнопка "Отмена"
        cancel_button_rect = pygame.Rect(panel_x + 270, button_y, 180, 40)
        pygame.draw.rect(self.screen, COLORS['panel'], cancel_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, COLORS['border'], cancel_button_rect, 2, border_radius=5)
        
        cancel_text = "Отмена"
        cancel_surf = self.font_normal.render(cancel_text, True, COLORS['text'])
        cancel_text_rect = cancel_surf.get_rect(center=cancel_button_rect.center)
        self.screen.blit(cancel_surf, cancel_text_rect)
        
        # Сохраняем прямоугольники кнопок для обработки кликов
        self.upgrade_button_rect = upgrade_button_rect
        self.cancel_button_rect = cancel_button_rect
    
    def _draw_recipes_panel(self):
        """Отрисовать панель рецептов"""
        if not self.crafting_system or not self.selected_station:
            return
        
        # Получаем рецепты для текущей станции
        station_recipes = []
        for recipe_id, recipe in self.crafting_system.recipes.items():
            if recipe.required_station == self.selected_station.id:
                # Проверяем tier станции
                if recipe.required_station_tier <= self.selected_station.current_tier:
                    station_recipes.append(recipe)
        
        if not station_recipes:
            # Нет рецептов
            panel_x = self.x + 300
            panel_y = self.y + 100
            no_recipes_text = "Нет доступных рецептов"
            no_recipes_surf = self.font_normal.render(no_recipes_text, True, COLORS['text_dim'])
            self.screen.blit(no_recipes_surf, (panel_x, panel_y))
            return
        
        # Панель рецептов (уменьшена для инвентаря)
        panel_x = self.x + 250
        panel_y = self.y + 80
        panel_width = (self.width - 270) // 2  # Половина ширины
        panel_height = self.height - 120
        
        pygame.draw.rect(self.screen, COLORS['panel'], 
                        (panel_x, panel_y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(self.screen, COLORS['border'], 
                        (panel_x, panel_y, panel_width, panel_height), 2, border_radius=10)
        
        # Заголовок
        title_text = f"Рецепты: {self.selected_station.name}"
        title_surf = self.font_normal.render(title_text, True, COLORS['text'])
        self.screen.blit(title_surf, (panel_x + 20, panel_y + 15))
        
        # Список рецептов (первые 5)
        y_offset = panel_y + 60
        self.recipe_rects = []  # Сохраняем для обработки кликов
        
        for i, recipe in enumerate(station_recipes[:5]):
            # Проверяем наличие ингредиентов
            has_ingredients = True
            for item_id, count in recipe.ingredients.items():
                if self.player_inventory.get(item_id, 0) < count:
                    has_ingredients = False
                    break
            
            # Фон рецепта
            recipe_rect = pygame.Rect(panel_x + 15, y_offset, panel_width - 30, 70)
            
            # Подсветка выбранного рецепта
            if self.selected_recipe and self.selected_recipe.id == recipe.id:
                pygame.draw.rect(self.screen, (60, 80, 100), recipe_rect, border_radius=5)
                pygame.draw.rect(self.screen, (100, 150, 200), recipe_rect, 2, border_radius=5)
            else:
                pygame.draw.rect(self.screen, COLORS['bg'], recipe_rect, border_radius=5)
                border_color = (50, 200, 50) if has_ingredients else COLORS['border']
                pygame.draw.rect(self.screen, border_color, recipe_rect, 1, border_radius=5)
            
            # Название рецепта
            text_color = COLORS['text'] if has_ingredients else COLORS['text_dim']
            name_surf = self.font_normal.render(recipe.name, True, text_color)
            self.screen.blit(name_surf, (panel_x + 25, y_offset + 10))
            
            # Ингредиенты
            ingredients_text = ", ".join([f"{count}x {item_id}" for item_id, count in recipe.ingredients.items()])
            if len(ingredients_text) > 50:
                ingredients_text = ingredients_text[:47] + "..."
            ing_surf = self.font_small.render(ingredients_text, True, COLORS['text_dim'])
            self.screen.blit(ing_surf, (panel_x + 25, y_offset + 35))
            
            # Сохраняем rect и рецепт для обработки кликов
            self.recipe_rects.append((recipe_rect, recipe))
            
            y_offset += 80
        
        # Кнопка "Крафтить" если выбран рецепт
        if self.selected_recipe:
            # Проверяем наличие ингредиентов
            can_craft = True
            for item_id, count in self.selected_recipe.ingredients.items():
                if self.player_inventory.get(item_id, 0) < count:
                    can_craft = False
                    break
            
            button_y = panel_y + panel_height - 60
            self.craft_button_rect = pygame.Rect(panel_x + panel_width - 200, button_y, 180, 40)
            
            button_color = (50, 150, 50) if can_craft else (80, 80, 80)
            pygame.draw.rect(self.screen, button_color, self.craft_button_rect, border_radius=5)
            pygame.draw.rect(self.screen, COLORS['border'], self.craft_button_rect, 2, border_radius=5)
            
            button_text = "Крафтить" if can_craft else "Нет ресурсов"
            button_surf = self.font_normal.render(button_text, True, COLORS['text'])
            button_text_rect = button_surf.get_rect(center=self.craft_button_rect.center)
            self.screen.blit(button_surf, button_text_rect)
    
    def draw(self):
        """Отрисовать UI"""
        # Фон
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(self.screen, COLORS['bg'], bg_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS['border'], bg_rect, 2, border_radius=10)
        
        # Заголовок
        title_text = "Крафт-станции"
        title_surf = self.font_title.render(title_text, True, COLORS['text'])
        title_rect = title_surf.get_rect(centerx=self.screen.get_width() // 2, top=self.y + 10)
        self.screen.blit(title_surf, title_rect)
        
        # Информация об игроке
        info_text = f"Уровень: {self.player_level} | Монеты: {self.player_money}"
        info_surf = self.font_normal.render(info_text, True, COLORS['text_dim'])
        info_rect = info_surf.get_rect(right=self.x + self.width - 20, top=self.y + 15)
        self.screen.blit(info_surf, info_rect)
        
        # Рисуем карточки станций
        for card in self.cards:
            self._draw_station_card(card)
        
        # Рисуем панель в зависимости от режима
        if self.selected_station:
            if self.view_mode == "recipes":
                self._draw_recipes_panel()
                self._draw_inventory_panel()  # Добавлена панель инвентаря
            elif self.show_upgrade_panel:
                self._draw_upgrade_panel()
        
        # Подсказка
        help_text = "ЛКМ - выбрать | TAB - переключить режим | ESC - закрыть"
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
        if event.type == pygame.KEYDOWN:
            # TAB - переключение между рецептами и улучшениями
            if event.key == pygame.K_TAB and self.selected_station:
                if self.view_mode == "recipes":
                    self.view_mode = "upgrade"
                    self.show_upgrade_panel = True
                else:
                    self.view_mode = "recipes"
                    self.show_upgrade_panel = False
                return True
            
            # ESC - закрыть панель
            elif event.key == pygame.K_ESCAPE:
                if self.selected_station:
                    self.selected_station = None
                    self.show_upgrade_panel = False
                    return True
        
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            adjusted_pos = (mouse_pos[0], mouse_pos[1] + self.scroll_offset)
            
            # Обновляем наведение на карточки
            self.hovered_card = None
            for card in self.cards:
                if card.contains_point(adjusted_pos):
                    self.hovered_card = card.station.id
                    break
            
            return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # ЛКМ
                mouse_pos = event.pos
                
                # Проверяем клик по кнопке крафта
                if self.view_mode == "recipes" and hasattr(self, 'craft_button_rect'):
                    if self.craft_button_rect.collidepoint(mouse_pos):
                        return self._try_craft()
                
                # Проверяем клик по рецептам
                if self.view_mode == "recipes" and hasattr(self, 'recipe_rects'):
                    for rect, recipe in self.recipe_rects:
                        if rect.collidepoint(mouse_pos):
                            self.selected_recipe = recipe
                            return True
                
                # Если открыта панель улучшения
                if self.show_upgrade_panel:
                    # Проверяем клик по кнопкам
                    if hasattr(self, 'upgrade_button_rect') and self.upgrade_button_rect.collidepoint(mouse_pos):
                        self._try_upgrade()
                        return True
                    elif hasattr(self, 'cancel_button_rect') and self.cancel_button_rect.collidepoint(mouse_pos):
                        self.show_upgrade_panel = False
                        self.selected_station = None
                        return True
                
                # Проверяем клик по карточкам
                if not self.selected_station:
                    # Проверяем клик по карточкам
                    adjusted_pos = (mouse_pos[0], mouse_pos[1] + self.scroll_offset)
                    for card in self.cards:
                        if card.contains_point(adjusted_pos):
                            self.selected_station = card.station
                            # По умолчанию показываем рецепты, а не улучшения
                            self.view_mode = "recipes"
                            self.show_upgrade_panel = False
                            return True
            
            elif event.button == 4:  # Колесо вверх
                self.scroll_offset = max(0, self.scroll_offset - 30)
                return True
            
            elif event.button == 5:  # Колесо вниз
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 30)
                return True
        
        return False
    
    def _try_upgrade(self):
        """Попытаться улучшить станцию"""
        if not self.selected_station:
            return
        
        station = self.selected_station
        
        if station.can_upgrade(self.player_level, self.player_inventory, self.player_money):
            next_tier = station.current_tier + 1
            upgrade = station.upgrades[next_tier]
            
            # Тратим ресурсы
            self.player_money -= upgrade.cost
            for item_id, count in upgrade.required_materials.items():
                self.player_inventory[item_id] -= count
            
            # Улучшаем станцию
            success = station.upgrade()
            if success:
                print(f"✅ Станция '{station.name}' улучшена до уровня {station.current_tier}")
                self.show_upgrade_panel = False
                self.selected_station = None
                
                # Запускаем анимацию
                self.upgrading_station = station.id
                self.upgrade_animation_progress = 0.0
    
    def _try_craft(self) -> bool:
        """
        Попытаться скрафтить выбранный рецепт
        
        Returns:
            True если крафт успешен
        """
        if not self.selected_recipe or not self.crafting_system:
            return False
        
        recipe = self.selected_recipe
        
        # Проверяем наличие всех ингредиентов
        for item_id, count in recipe.ingredients.items():
            if self.player_inventory.get(item_id, 0) < count:
                print(f"❌ Недостаточно {item_id}: нужно {count}, есть {self.player_inventory.get(item_id, 0)}")
                return False
        
        # НЕ изменяем player_inventory здесь - это сделает game.py
        # Просто сохраняем информацию о крафте
        result_count = recipe.result_count
        
        print(f"✅ Скрафчено: {recipe.name} x{result_count}")
        
        # СРАЗУ обновляем словарь инвентаря в UI (вычитаем ингредиенты)
        for item_id, count in recipe.ingredients.items():
            if item_id in self.player_inventory:
                self.player_inventory[item_id] -= count
                if self.player_inventory[item_id] <= 0:
                    del self.player_inventory[item_id]
        
        # СРАЗУ добавляем результат в словарь UI
        if recipe.result_item in self.player_inventory:
            self.player_inventory[recipe.result_item] += result_count
        else:
            self.player_inventory[recipe.result_item] = result_count
        
        # Добавляем в очередь крафтов
        self.crafted_queue.append({
            "recipe": recipe,
            "result_item": recipe.result_item,
            "result_count": result_count,
            "ingredients": recipe.ingredients.copy()
        })
        
        # Сбрасываем выбор рецепта
        self.selected_recipe = None
        
        return True
    
    def get_and_clear_crafted(self):
        """Получить и очистить информацию о последнем крафте"""
        if self.crafted_queue:
            return self.crafted_queue.pop(0)
        return None
    
    def update(self, dt: float):
        """
        Обновить анимации
        
        Args:
            dt: Время с последнего кадра в секундах
        """
        # Обновляем анимацию улучшения
        if self.upgrading_station:
            self.upgrade_animation_progress += dt * 2
            if self.upgrade_animation_progress >= 1.0:
                self.upgrading_station = None
                self.upgrade_animation_progress = 0.0
