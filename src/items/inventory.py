"""
Система инвентаря
"""
from typing import Optional, List, Tuple
from .item import Item, ItemType


class InventorySlot:
    """Слот инвентаря"""
    
    def __init__(self, item: Optional[Item] = None, quantity: int = 1):
        """
        Инициализация слота
        
        Args:
            item: Предмет
            quantity: Количество
        """
        self.item = item
        self.quantity = quantity
        
    def is_empty(self) -> bool:
        """Проверить, пуст ли слот"""
        return self.item is None
        
    def can_add(self, item: Item, amount: int = 1) -> bool:
        """
        Можно ли добавить предмет в слот
        
        Args:
            item: Предмет
            amount: Количество
            
        Returns:
            True если можно добавить
        """
        if self.is_empty():
            return True
            
        if self.item.id == item.id and self.item.stackable:
            return self.quantity + amount <= self.item.max_stack
            
        return False
        
    def add(self, item: Item, amount: int = 1) -> int:
        """
        Добавить предмет в слот
        
        Args:
            item: Предмет
            amount: Количество
            
        Returns:
            Количество добавленных предметов
        """
        if self.is_empty():
            self.item = item
            self.quantity = amount
            return amount
            
        if self.item.id == item.id and self.item.stackable:
            space = self.item.max_stack - self.quantity
            added = min(space, amount)
            self.quantity += added
            return added
            
        return 0
        
    def remove(self, amount: int = 1) -> int:
        """
        Удалить предмет из слота
        
        Args:
            amount: Количество
            
        Returns:
            Количество удалённых предметов
        """
        if self.is_empty():
            return 0
            
        removed = min(self.quantity, amount)
        self.quantity -= removed
        
        if self.quantity <= 0:
            self.item = None
            self.quantity = 0
            
        return removed


class Inventory:
    """Инвентарь игрока"""
    
    def __init__(self, max_slots: int = 20):
        """
        Инициализация инвентаря
        
        Args:
            max_slots: Максимальное количество слотов
        """
        self.max_slots = max_slots
        self.slots: List[InventorySlot] = [InventorySlot() for _ in range(max_slots)]
        
        # Экипированное оружие
        self.equipped_weapon: Optional[Item] = None
        
        print(f"🎒 Инвентарь создан: {max_slots} слотов")
        
    def add_item(self, item: Item, quantity: int = 1) -> bool:
        """
        Добавить предмет в инвентарь
        
        Args:
            item: Предмет
            quantity: Количество
            
        Returns:
            True если добавлено успешно
        """
        remaining = quantity
        
        # Сначала пытаемся добавить в существующие стопки
        if item.stackable:
            print(f"🔍 Ищем стак для: {item.name} (id={item.id}, stackable={item.stackable}, max={item.max_stack})")
            for slot in self.slots:
                if not slot.is_empty():
                    print(f"   Слот: {slot.item.name} (id={slot.item.id}, кол-во={slot.quantity}/{slot.item.max_stack})")
                    if slot.item.id == item.id:
                        print(f"   ✅ ID совпадают! Добавляем в стак")
                        added = slot.add(item, remaining)
                        remaining -= added
                        if remaining <= 0:
                            print(f"✅ Добавлено: {item.name} x{quantity}")
                            return True
                    else:
                        print(f"   ❌ ID не совпадают: '{slot.item.id}' != '{item.id}'")
                        
        # Затем ищем пустые слоты
        for slot in self.slots:
            if slot.is_empty():
                added = slot.add(item, remaining)
                remaining -= added
                if remaining <= 0:
                    print(f"✅ Добавлено: {item.name} x{quantity}")
                    return True
                    
        if remaining < quantity:
            print(f"⚠️  Добавлено частично: {item.name} x{quantity - remaining}")
            return False
        else:
            print(f"❌ Инвентарь полон! Не удалось добавить: {item.name}")
            return False
            
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        Удалить предмет из инвентаря
        
        Args:
            item_id: ID предмета
            quantity: Количество
            
        Returns:
            True если удалено успешно
        """
        remaining = quantity
        
        for slot in self.slots:
            if not slot.is_empty() and slot.item.id == item_id:
                removed = slot.remove(remaining)
                remaining -= removed
                if remaining <= 0:
                    return True
                    
        return remaining < quantity
        
    def get_item_count(self, item_id: str) -> int:
        """
        Получить количество предмета
        
        Args:
            item_id: ID предмета
            
        Returns:
            Количество
        """
        count = 0
        for slot in self.slots:
            if not slot.is_empty() and slot.item.id == item_id:
                count += slot.quantity
        return count
        
    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        Проверить наличие предмета
        
        Args:
            item_id: ID предмета
            quantity: Требуемое количество
            
        Returns:
            True если есть
        """
        return self.get_item_count(item_id) >= quantity
        
    def use_item(self, slot_index: int, player) -> bool:
        """
        Использовать предмет из слота
        
        Args:
            slot_index: Индекс слота
            player: Игрок
            
        Returns:
            True если использовано успешно
        """
        if slot_index < 0 or slot_index >= self.max_slots:
            return False
            
        slot = self.slots[slot_index]
        if slot.is_empty():
            return False
            
        item = slot.item
        
        # Используем предмет
        if item.use(player):
            # Удаляем использованный предмет
            if item.item_type == ItemType.CONSUMABLE:
                slot.remove(1)
            return True
            
        return False
        
    def equip_weapon(self, slot_index: int) -> bool:
        """
        Экипировать оружие из слота
        
        Args:
            slot_index: Индекс слота
            
        Returns:
            True если экипировано успешно
        """
        if slot_index < 0 or slot_index >= self.max_slots:
            return False
            
        slot = self.slots[slot_index]
        if slot.is_empty():
            return False
            
        item = slot.item
        if item.item_type != ItemType.WEAPON:
            print(f"❌ {item.name} - не оружие!")
            return False
            
        # Снимаем текущее оружие
        if self.equipped_weapon:
            self.add_item(self.equipped_weapon)
            
        # Экипируем новое
        self.equipped_weapon = item
        slot.remove(1)
        print(f"⚔️  Экипировано: {item.name} ({item.damage} урона)")
        return True
        
    def unequip_weapon(self) -> bool:
        """
        Снять оружие
        
        Returns:
            True если снято успешно
        """
        if not self.equipped_weapon:
            print("❌ Оружие не экипировано!")
            return False
            
        weapon = self.equipped_weapon
        if self.add_item(weapon):
            self.equipped_weapon = None
            print(f"✅ Снято: {weapon.name}")
            return True
        else:
            print("❌ Нет места в инвентаре!")
            return False
    
    def drop_item(self, slot_index: int, quantity: int = 1) -> Optional[Tuple[Item, int]]:
        """
        Выбросить предмет из слота
        
        Args:
            slot_index: Индекс слота
            quantity: Количество для выброса
            
        Returns:
            Кортеж (предмет, количество) или None
        """
        if slot_index < 0 or slot_index >= self.max_slots:
            return None
            
        slot = self.slots[slot_index]
        if slot.is_empty():
            return None
        
        item = slot.item
        actual_quantity = min(quantity, slot.quantity)
        
        # Удаляем из слота
        slot.remove(actual_quantity)
        
        print(f"🗑️  Выброшено: {item.name} x{actual_quantity}")
        return (item, actual_quantity)
            
    def get_total_weight(self) -> float:
        """
        Получить общий вес инвентаря
        
        Returns:
            Вес
        """
        weight = 0.0
        for slot in self.slots:
            if not slot.is_empty():
                weight += slot.item.weight * slot.quantity
                
        if self.equipped_weapon:
            weight += self.equipped_weapon.weight
            
        return weight
        
    def get_items_by_type(self, item_type: ItemType) -> List[Tuple[int, InventorySlot]]:
        """
        Получить предметы по типу
        
        Args:
            item_type: Тип предмета
            
        Returns:
            Список (индекс, слот)
        """
        items = []
        for i, slot in enumerate(self.slots):
            if not slot.is_empty() and slot.item.item_type == item_type:
                items.append((i, slot))
        return items
        
    def print_inventory(self):
        """Вывести содержимое инвентаря"""
        print("\n🎒 ИНВЕНТАРЬ:")
        
        if self.equipped_weapon:
            print(f"⚔️  Оружие: {self.equipped_weapon.name} ({self.equipped_weapon.damage} урона)")
        else:
            print("⚔️  Оружие: не экипировано")
            
        print(f"\nВес: {self.get_total_weight():.1f} кг")
        print("\nПредметы:")
        
        has_items = False
        for i, slot in enumerate(self.slots):
            if not slot.is_empty():
                has_items = True
                quantity_str = f" x{slot.quantity}" if slot.quantity > 1 else ""
                print(f"  [{i}] {slot.item.name}{quantity_str}")
                
        if not has_items:
            print("  (пусто)")


if __name__ == "__main__":
    # Тест инвентаря
    from .item import ItemDatabase
    
    db = ItemDatabase()
    inventory = Inventory(max_slots=10)
    
    # Добавляем предметы
    inventory.add_item(db.get_item("rusty_pipe"))
    inventory.add_item(db.get_item("bandage"), 5)
    inventory.add_item(db.get_item("coffee"), 3)
    
    # Выводим инвентарь
    inventory.print_inventory()
    
    # Экипируем оружие
    inventory.equip_weapon(0)
    
    # Выводим снова
    inventory.print_inventory()
