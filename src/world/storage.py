"""
Система хранилища на чердаке
"""
from typing import List
from ..items.inventory import InventorySlot
from ..items.item import Item


class Storage:
    """Хранилище (сундук на чердаке)"""
    
    def __init__(self, max_slots: int = 50):
        """
        Инициализация хранилища
        
        Args:
            max_slots: Максимальное количество слотов
        """
        self.max_slots = max_slots
        self.slots: List[InventorySlot] = [InventorySlot() for _ in range(max_slots)]
        
        print(f"📦 Хранилище создано: {max_slots} слотов")
        
    def add_item(self, item: Item, quantity: int = 1) -> bool:
        """
        Добавить предмет в хранилище
        
        Args:
            item: Предмет
            quantity: Количество
            
        Returns:
            True если добавлено успешно
        """
        remaining = quantity
        
        # Сначала пытаемся добавить в существующие стопки
        if item.stackable:
            for slot in self.slots:
                if not slot.is_empty() and slot.item.id == item.id:
                    added = slot.add(item, remaining)
                    remaining -= added
                    if remaining <= 0:
                        print(f"✅ В хранилище добавлено: {item.name} x{quantity}")
                        return True
                        
        # Затем ищем пустые слоты
        for slot in self.slots:
            if slot.is_empty():
                added = slot.add(item, remaining)
                remaining -= added
                if remaining <= 0:
                    print(f"✅ В хранилище добавлено: {item.name} x{quantity}")
                    return True
                    
        if remaining < quantity:
            print(f"⚠️  Добавлено частично: {item.name} x{quantity - remaining}")
            return False
        else:
            print(f"❌ Хранилище полно!")
            return False
            
    def remove_item(self, slot_index: int, quantity: int = 1) -> tuple[Item, int]:
        """
        Взять предмет из хранилища
        
        Args:
            slot_index: Индекс слота
            quantity: Количество
            
        Returns:
            (предмет, количество)
        """
        if slot_index < 0 or slot_index >= self.max_slots:
            return None, 0
            
        slot = self.slots[slot_index]
        if slot.is_empty():
            return None, 0
            
        item = slot.item
        removed = slot.remove(quantity)
        
        if removed > 0:
            print(f"✅ Взято из хранилища: {item.name} x{removed}")
            
        return item, removed
        
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
        
    def print_storage(self):
        """Вывести содержимое хранилища"""
        print("\n📦 ХРАНИЛИЩЕ (СУНДУК):")
        
        has_items = False
        for i, slot in enumerate(self.slots):
            if not slot.is_empty():
                has_items = True
                quantity_str = f" x{slot.quantity}" if slot.quantity > 1 else ""
                print(f"  [{i}] {slot.item.name}{quantity_str}")
                
        if not has_items:
            print("  (пусто)")
            
    def get_used_slots(self) -> int:
        """
        Получить количество занятых слотов
        
        Returns:
            Количество занятых слотов
        """
        return sum(1 for slot in self.slots if not slot.is_empty())


if __name__ == "__main__":
    # Тест хранилища
    from ..items.item import ItemDatabase
    
    db = ItemDatabase()
    storage = Storage(max_slots=20)
    
    # Добавляем предметы
    storage.add_item(db.get_item("crowbar"))
    storage.add_item(db.get_item("medkit"), 10)
    storage.add_item(db.get_item("coffee"), 5)
    
    # Выводим хранилище
    storage.print_storage()
    
    print(f"\nЗанято слотов: {storage.get_used_slots()}/{storage.max_slots}")
