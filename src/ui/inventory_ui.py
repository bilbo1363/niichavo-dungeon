"""
GUI для инвентаря и хранилища
"""
import pygame
from typing import Optional, Tuple


class InventoryUI:
    """Визуальный интерфейс инвентаря"""
    
    def __init__(self, screen_width: int, screen_height: int):
        """
        Инициализация UI
        
        Args:
            screen_width: Ширина экрана
            screen_height: Высота экрана
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Параметры окна инвентаря
        self.width = 600
        self.height = 500
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        
        # Параметры слотов
        self.slot_size = 50
        self.slot_padding = 5
        self.slots_per_row = 5
        
        # Выбранный слот
        self.selected_slot: Optional[int] = None
        
        # Шрифты
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
    def render_inventory(self, screen: pygame.Surface, inventory) -> None:
        """
        Отрисовка инвентаря
        
        Args:
            screen: Поверхность для отрисовки
            inventory: Инвентарь игрока
        """
        # Полупрозрачный фон
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Окно инвентаря
        pygame.draw.rect(screen, (40, 40, 40), (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, (100, 100, 100), (self.x, self.y, self.width, self.height), 3)
        
        # Заголовок
        title = self.font.render("🎒 ИНВЕНТАРЬ", True, (255, 255, 255))
        screen.blit(title, (self.x + 20, self.y + 15))
        
        # Экипированное оружие
        weapon_y = self.y + 60
        weapon_text = self.small_font.render("Оружие:", True, (200, 200, 200))
        screen.blit(weapon_text, (self.x + 20, weapon_y))
        
        if inventory.equipped_weapon:
            weapon_name = self.small_font.render(
                f"{inventory.equipped_weapon.name} ({inventory.equipped_weapon.damage} урона)",
                True,
                inventory.equipped_weapon.get_rarity_color()
            )
            screen.blit(weapon_name, (self.x + 100, weapon_y))
        else:
            no_weapon = self.small_font.render("не экипировано", True, (150, 150, 150))
            screen.blit(no_weapon, (self.x + 100, weapon_y))
        
        # Слоты инвентаря
        slots_y = self.y + 100
        for i, slot in enumerate(inventory.slots):
            row = i // self.slots_per_row
            col = i % self.slots_per_row
            
            slot_x = self.x + 20 + col * (self.slot_size + self.slot_padding)
            slot_y = slots_y + row * (self.slot_size + self.slot_padding)
            
            # Рамка слота
            color = (100, 100, 100)
            if self.selected_slot == i:
                color = (255, 255, 0)
            elif not slot.is_empty():
                color = (150, 150, 150)
                
            pygame.draw.rect(screen, color, (slot_x, slot_y, self.slot_size, self.slot_size), 2)
            
            # Предмет в слоте
            if not slot.is_empty():
                # Цвет по редкости
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
        
        # Информация о выбранном предмете
        if self.selected_slot is not None and self.selected_slot < len(inventory.slots):
            slot = inventory.slots[self.selected_slot]
            if not slot.is_empty():
                info_y = slots_y + 250
                
                # Название
                name_text = self.font.render(slot.item.name, True, slot.item.get_rarity_color())
                screen.blit(name_text, (self.x + 20, info_y))
                
                # Описание
                desc_text = self.small_font.render(slot.item.description, True, (200, 200, 200))
                screen.blit(desc_text, (self.x + 20, info_y + 30))
                
                # Характеристики
                stats_y = info_y + 60
                if slot.item.damage > 0:
                    dmg = self.small_font.render(f"Урон: {slot.item.damage}", True, (255, 100, 100))
                    screen.blit(dmg, (self.x + 20, stats_y))
                    stats_y += 20
                    
                if slot.item.heal_amount > 0:
                    heal = self.small_font.render(f"Лечение: +{slot.item.heal_amount} HP", True, (100, 255, 100))
                    screen.blit(heal, (self.x + 20, stats_y))
                    stats_y += 20
                    
                if slot.item.endurance_amount > 0:
                    end = self.small_font.render(f"Выносливость: +{slot.item.endurance_amount}", True, (100, 200, 255))
                    screen.blit(end, (self.x + 20, stats_y))
        
        # Подсказки
        hint_y = self.y + self.height - 80
        hints = [
            "Стрелки - выбор предмета",
            "Enter - использовать/экипировать",
            "D - выбросить предмет",
            "I или ESC - закрыть"
        ]
        for i, hint in enumerate(hints):
            hint_text = self.small_font.render(hint, True, (150, 150, 150))
            screen.blit(hint_text, (self.x + 20, hint_y + i * 20))
    
    def handle_input(self, event: pygame.event.Event, inventory, player=None) -> bool:
        """
        Обработка ввода
        
        Args:
            event: Событие pygame
            inventory: Инвентарь
            
        Returns:
            True если нужно закрыть инвентарь
        """
        if event.type == pygame.KEYDOWN:
            # Закрыть
            if event.key in [pygame.K_i, pygame.K_ESCAPE]:
                return True
                
            # Выбор слота
            if event.key == pygame.K_RIGHT:
                if self.selected_slot is None:
                    self.selected_slot = 0
                else:
                    self.selected_slot = (self.selected_slot + 1) % inventory.max_slots
                    
            elif event.key == pygame.K_LEFT:
                if self.selected_slot is None:
                    self.selected_slot = 0
                else:
                    self.selected_slot = (self.selected_slot - 1) % inventory.max_slots
                    
            elif event.key == pygame.K_DOWN:
                if self.selected_slot is None:
                    self.selected_slot = 0
                else:
                    self.selected_slot = (self.selected_slot + self.slots_per_row) % inventory.max_slots
                    
            elif event.key == pygame.K_UP:
                if self.selected_slot is None:
                    self.selected_slot = 0
                else:
                    self.selected_slot = (self.selected_slot - self.slots_per_row) % inventory.max_slots
                    
            # Использовать предмет
            elif event.key == pygame.K_RETURN:
                if self.selected_slot is not None and player is not None:
                    slot = inventory.slots[self.selected_slot]
                    if not slot.is_empty():
                        from ..items.item import ItemType
                        
                        # Экипировать оружие
                        if slot.item.item_type == ItemType.WEAPON:
                            inventory.equip_weapon(self.selected_slot)
                        # Использовать расходник
                        elif slot.item.item_type == ItemType.CONSUMABLE:
                            inventory.use_item(self.selected_slot, player)
            
            # Выбросить предмет (клавиша D - Drop)
            elif event.key == pygame.K_d:
                if self.selected_slot is not None:
                    slot = inventory.slots[self.selected_slot]
                    if not slot.is_empty():
                        # Возвращаем информацию о выброшенном предмете
                        # Игра должна обработать это и разместить предмет на карте
                        dropped = inventory.drop_item(self.selected_slot, 1)
                        if dropped and player is not None:
                            # Сохраняем информацию для размещения на карте
                            if not hasattr(player, '_dropped_items'):
                                player._dropped_items = []
                            player._dropped_items.append(dropped)
                            
        return False


if __name__ == "__main__":
    # Тест UI
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    
    from ..items.inventory import Inventory
    from ..items.item import ItemDatabase
    
    db = ItemDatabase()
    inventory = Inventory()
    inventory.add_item(db.get_item("rusty_pipe"))
    inventory.add_item(db.get_item("bandage"), 5)
    
    ui = InventoryUI(1200, 800)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if ui.handle_input(event, inventory):
                running = False
                
        screen.fill((0, 0, 0))
        ui.render_inventory(screen, inventory)
        pygame.display.flip()
        
    pygame.quit()
