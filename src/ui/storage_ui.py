"""
GUI для хранилища
"""
import pygame
from typing import Optional


class StorageUI:
    """Визуальный интерфейс хранилища"""
    
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
        self.height = 600
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        
        # Параметры слотов
        self.slot_size = 50
        self.slot_padding = 5
        self.slots_per_row = 5
        
        # Выбранные слоты
        self.selected_inventory_slot: Optional[int] = None
        self.selected_storage_slot: Optional[int] = None
        self.active_panel = "inventory"  # "inventory" или "storage"
        
        # Шрифты
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Текущее хранилище
        self.current_storage = None
    
    def set_storage(self, storage):
        """Установить текущее хранилище"""
        self.current_storage = storage
        
    def render(self, screen: pygame.Surface, inventory, storage) -> None:
        """
        Отрисовка хранилища
        
        Args:
            screen: Поверхность для отрисовки
            inventory: Инвентарь игрока
            storage: Хранилище
        """
        # Полупрозрачный фон
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Окно хранилища
        pygame.draw.rect(screen, (40, 40, 40), (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, (100, 100, 100), (self.x, self.y, self.width, self.height), 3)
        
        # Заголовок
        title = self.font.render("📦 ХРАНИЛИЩЕ (СУНДУК)", True, (255, 255, 255))
        screen.blit(title, (self.x + 20, self.y + 15))
        
        # Разделитель
        mid_x = self.x + self.width // 2
        pygame.draw.line(screen, (100, 100, 100), 
                        (mid_x, self.y + 50), 
                        (mid_x, self.y + self.height - 100), 2)
        
        # Левая панель - Инвентарь
        inv_title = self.font.render("🎒 Ваш инвентарь", True, (200, 200, 200))
        screen.blit(inv_title, (self.x + 20, self.y + 60))
        
        self._render_slots(
            screen, 
            inventory.slots, 
            self.x + 20, 
            self.y + 100,
            self.selected_inventory_slot,
            self.active_panel == "inventory"
        )
        
        # Правая панель - Хранилище
        stor_title = self.font.render("📦 Сундук", True, (200, 200, 200))
        screen.blit(stor_title, (mid_x + 20, self.y + 60))
        
        self._render_slots(
            screen, 
            storage.slots, 
            mid_x + 20, 
            self.y + 100,
            self.selected_storage_slot,
            self.active_panel == "storage"
        )
        
        # Информация о выбранном предмете
        self._render_item_info(screen, inventory, storage)
        
        # Подсказки
        hint_y = self.y + self.height - 80
        hints = [
            "Стрелки - навигация | Tab - переключить панель",
            "Enter - переместить предмет | ESC - закрыть"
        ]
        for i, hint in enumerate(hints):
            hint_text = self.small_font.render(hint, True, (150, 150, 150))
            hint_rect = hint_text.get_rect(center=(self.x + self.width // 2, hint_y + i * 20))
            screen.blit(hint_text, hint_rect)
    
    def _render_slots(self, screen, slots, start_x, start_y, selected_slot, is_active):
        """Отрисовка слотов"""
        for i, slot in enumerate(slots[:20]):  # Показываем первые 20 слотов
            row = i // self.slots_per_row
            col = i % self.slots_per_row
            
            slot_x = start_x + col * (self.slot_size + self.slot_padding)
            slot_y = start_y + row * (self.slot_size + self.slot_padding)
            
            # Рамка слота
            color = (100, 100, 100)
            if selected_slot == i and is_active:
                color = (255, 255, 0)
            elif not slot.is_empty():
                color = (150, 150, 150)
                
            pygame.draw.rect(screen, color, (slot_x, slot_y, self.slot_size, self.slot_size), 2)
            
            # Предмет в слоте
            if not slot.is_empty():
                item_color = slot.item.get_rarity_color()
                pygame.draw.rect(
                    screen,
                    item_color,
                    (slot_x + 5, slot_y + 5, self.slot_size - 10, self.slot_size - 10)
                )
                
                # Количество
                if slot.quantity > 1:
                    qty_text = self.small_font.render(str(slot.quantity), True, (255, 255, 255))
                    screen.blit(qty_text, (slot_x + 5, slot_y + 5))
    
    def _render_item_info(self, screen, inventory, storage):
        """Отрисовка информации о предмете"""
        slot = None
        
        if self.active_panel == "inventory" and self.selected_inventory_slot is not None:
            if self.selected_inventory_slot < len(inventory.slots):
                slot = inventory.slots[self.selected_inventory_slot]
        elif self.active_panel == "storage" and self.selected_storage_slot is not None:
            if self.selected_storage_slot < len(storage.slots):
                slot = storage.slots[self.selected_storage_slot]
        
        if slot and not slot.is_empty():
            info_y = self.y + self.height - 150
            
            # Название
            name_text = self.font.render(slot.item.name, True, slot.item.get_rarity_color())
            name_rect = name_text.get_rect(center=(self.x + self.width // 2, info_y))
            screen.blit(name_text, name_rect)
            
            # Описание
            desc_text = self.small_font.render(slot.item.description, True, (200, 200, 200))
            desc_rect = desc_text.get_rect(center=(self.x + self.width // 2, info_y + 25))
            screen.blit(desc_text, desc_rect)
    
    def handle_input(self, event: pygame.event.Event, inventory, storage) -> bool:
        """
        Обработка ввода
        
        Args:
            event: Событие pygame
            inventory: Инвентарь
            storage: Хранилище
            
        Returns:
            True если нужно закрыть окно
        """
        if event.type == pygame.KEYDOWN:
            # Закрыть
            if event.key == pygame.K_ESCAPE:
                return True
            
            # Переключить панель
            elif event.key == pygame.K_TAB:
                if self.active_panel == "inventory":
                    self.active_panel = "storage"
                    if self.selected_storage_slot is None:
                        self.selected_storage_slot = 0
                else:
                    self.active_panel = "inventory"
                    if self.selected_inventory_slot is None:
                        self.selected_inventory_slot = 0
            
            # Навигация
            elif event.key == pygame.K_RIGHT:
                self._move_selection(1, inventory, storage)
            elif event.key == pygame.K_LEFT:
                self._move_selection(-1, inventory, storage)
            elif event.key == pygame.K_DOWN:
                self._move_selection(self.slots_per_row, inventory, storage)
            elif event.key == pygame.K_UP:
                self._move_selection(-self.slots_per_row, inventory, storage)
            
            # Переместить предмет
            elif event.key == pygame.K_RETURN:
                self._transfer_item(inventory, storage)
        
        return False
    
    def _move_selection(self, delta, inventory, storage):
        """Переместить выбор"""
        if self.active_panel == "inventory":
            if self.selected_inventory_slot is None:
                self.selected_inventory_slot = 0
            else:
                self.selected_inventory_slot = (self.selected_inventory_slot + delta) % min(20, inventory.max_slots)
        else:
            if self.selected_storage_slot is None:
                self.selected_storage_slot = 0
            else:
                self.selected_storage_slot = (self.selected_storage_slot + delta) % min(20, storage.max_slots)
    
    def _transfer_item(self, inventory, storage):
        """Переместить предмет между инвентарем и хранилищем"""
        if self.active_panel == "inventory" and self.selected_inventory_slot is not None:
            # Из инвентаря в хранилище
            slot = inventory.slots[self.selected_inventory_slot]
            if not slot.is_empty():
                item = slot.item
                quantity = slot.quantity
                if storage.add_item(item, quantity):
                    inventory.remove_item(item.id, quantity)
        
        elif self.active_panel == "storage" and self.selected_storage_slot is not None:
            # Из хранилища в инвентарь
            item, quantity = storage.remove_item(self.selected_storage_slot, 1)
            if item:
                inventory.add_item(item, quantity)
