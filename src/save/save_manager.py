"""
Система сохранений
"""
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


class SaveManager:
    """Менеджер сохранений"""
    
    def __init__(self, save_dir: str = "saves"):
        """
        Инициализация менеджера сохранений
        
        Args:
            save_dir: Директория для сохранений
        """
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
        print(f"💾 Менеджер сохранений создан (директория: {self.save_dir})")
        
    def save_game(self, save_name: str, game_data: Dict[str, Any]) -> bool:
        """
        Сохранить игру
        
        Args:
            save_name: Имя сохранения
            game_data: Данные для сохранения
            
        Returns:
            True если успешно
        """
        try:
            # Добавляем метаданные
            save_data = {
                "metadata": {
                    "save_name": save_name,
                    "timestamp": datetime.now().isoformat(),
                    "version": "0.1.0"
                },
                "game_data": game_data
            }
            
            # Путь к файлу сохранения
            save_path = self.save_dir / f"{save_name}.json"
            
            # Сохраняем в JSON
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
                
            print(f"💾 Игра сохранена: {save_path}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            return False
            
    def load_game(self, save_name: str) -> Optional[Dict[str, Any]]:
        """
        Загрузить игру
        
        Args:
            save_name: Имя сохранения
            
        Returns:
            Данные игры или None
        """
        try:
            save_path = self.save_dir / f"{save_name}.json"
            
            if not save_path.exists():
                print(f"⚠️  Сохранение не найдено: {save_name}")
                return None
                
            # Загружаем из JSON
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
                
            print(f"📂 Игра загружена: {save_path}")
            print(f"   Дата сохранения: {save_data['metadata']['timestamp']}")
            
            return save_data['game_data']
            
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            return None
            
    def list_saves(self) -> list[str]:
        """
        Получить список сохранений
        
        Returns:
            Список имён сохранений
        """
        saves = []
        for file in self.save_dir.glob("*.json"):
            saves.append(file.stem)
        return sorted(saves)
        
    def delete_save(self, save_name: str) -> bool:
        """
        Удалить сохранение
        
        Args:
            save_name: Имя сохранения
            
        Returns:
            True если успешно
        """
        try:
            save_path = self.save_dir / f"{save_name}.json"
            
            if save_path.exists():
                save_path.unlink()
                print(f"🗑️  Сохранение удалено: {save_name}")
                return True
            else:
                print(f"⚠️  Сохранение не найдено: {save_name}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка удаления: {e}")
            return False
            
    def get_save_info(self, save_name: str) -> Optional[Dict[str, Any]]:
        """
        Получить информацию о сохранении
        
        Args:
            save_name: Имя сохранения
            
        Returns:
            Метаданные сохранения
        """
        try:
            save_path = self.save_dir / f"{save_name}.json"
            
            if not save_path.exists():
                return None
                
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
                
            return save_data['metadata']
            
        except Exception as e:
            print(f"❌ Ошибка чтения метаданных: {e}")
            return None


class GameStateSerializer:
    """Сериализатор состояния игры"""
    
    @staticmethod
    def serialize_player(player) -> Dict[str, Any]:
        """
        Сериализовать игрока
        
        Args:
            player: Объект игрока
            
        Returns:
            Данные игрока
        """
        from ..items.item import Item
        
        # Сериализуем инвентарь
        inventory_data = []
        for slot in player.inventory.slots:
            if slot.item:
                item_data = {
                    "id": slot.item.id,
                    "name": slot.item.name,
                    "item_type": slot.item.item_type.value,
                    "rarity": slot.item.rarity.value,
                    "description": slot.item.description,
                    "damage": slot.item.damage,
                    "durability": slot.item.durability,
                    "max_durability": slot.item.max_durability,
                    "heal_amount": slot.item.heal_amount,
                    "endurance_amount": slot.item.endurance_amount,
                    "clarity_amount": slot.item.clarity_amount,
                    "stackable": slot.item.stackable,
                    "max_stack": slot.item.max_stack,
                    "weight": slot.item.weight,
                    "value": slot.item.value,
                    "quantity": slot.quantity
                }
                inventory_data.append(item_data)
            else:
                inventory_data.append(None)
        
        # Сериализуем экипированное оружие
        equipped_weapon_data = None
        if player.inventory.equipped_weapon:
            item = player.inventory.equipped_weapon
            equipped_weapon_data = {
                "id": item.id,
                "name": item.name,
                "item_type": item.item_type.value,
                "rarity": item.rarity.value,
                "description": item.description,
                "damage": item.damage,
                "durability": item.durability,
                "max_durability": item.max_durability,
                "heal_amount": item.heal_amount,
                "endurance_amount": item.endurance_amount,
                "clarity_amount": item.clarity_amount,
                "stackable": item.stackable,
                "max_stack": item.max_stack,
                "weight": item.weight,
                "value": item.value
            }
        
        return {
            "x": player.x,
            "y": player.y,
            "steps": player.steps,
            "money": player.money,
            "stats": {
                "health": player.stats.health,
                "max_health": player.stats.max_health,
                "endurance": player.stats.endurance,
                "max_endurance": player.stats.max_endurance,
                "thirst": player.stats.thirst,
                "clarity": player.stats.clarity
            },
            "backpack": player.backpack,
            "inventory": inventory_data,
            "equipped_weapon": equipped_weapon_data
        }
        
    @staticmethod
    def deserialize_player(player, data: Dict[str, Any]) -> None:
        """
        Десериализовать игрока
        
        Args:
            player: Объект игрока
            data: Данные для загрузки
        """
        from ..items.item import Item, ItemType, ItemRarity
        
        player.x = data["x"]
        player.y = data["y"]
        player.steps = data["steps"]
        player.money = data.get("money", 0)
        
        stats_data = data["stats"]
        player.stats.health = stats_data["health"]
        player.stats.max_health = stats_data["max_health"]
        player.stats.endurance = stats_data["endurance"]
        player.stats.max_endurance = stats_data["max_endurance"]
        player.stats.thirst = stats_data["thirst"]
        player.stats.clarity = stats_data["clarity"]
        
        player.backpack = data["backpack"]
        
        # Восстанавливаем инвентарь
        if "inventory" in data:
            from ..items.inventory import InventorySlot
            player.inventory.slots = []
            for slot_data in data["inventory"]:
                if slot_data:
                    item = Item(
                        id=slot_data["id"],
                        name=slot_data["name"],
                        item_type=ItemType(slot_data["item_type"]),
                        rarity=ItemRarity(slot_data["rarity"]),
                        description=slot_data["description"],
                        damage=slot_data.get("damage", 0),
                        durability=slot_data.get("durability", 100),
                        max_durability=slot_data.get("max_durability", 100),
                        heal_amount=slot_data.get("heal_amount", 0),
                        endurance_amount=slot_data.get("endurance_amount", 0),
                        clarity_amount=slot_data.get("clarity_amount", 0),
                        stackable=slot_data.get("stackable", False),
                        max_stack=slot_data.get("max_stack", 1),
                        weight=slot_data.get("weight", 1.0),
                        value=slot_data.get("value", 0)
                    )
                    player.inventory.slots.append(InventorySlot(item, slot_data["quantity"]))
                else:
                    player.inventory.slots.append(InventorySlot())
        
        # Восстанавливаем экипированное оружие
        if "equipped_weapon" in data and data["equipped_weapon"]:
            item_data = data["equipped_weapon"]
            item = Item(
                id=item_data["id"],
                name=item_data["name"],
                item_type=ItemType(item_data["item_type"]),
                rarity=ItemRarity(item_data["rarity"]),
                description=item_data["description"],
                damage=item_data.get("damage", 0),
                durability=item_data.get("durability", 100),
                max_durability=item_data.get("max_durability", 100),
                heal_amount=item_data.get("heal_amount", 0),
                endurance_amount=item_data.get("endurance_amount", 0),
                clarity_amount=item_data.get("clarity_amount", 0),
                stackable=item_data.get("stackable", False),
                max_stack=item_data.get("max_stack", 1),
                weight=item_data.get("weight", 1.0),
                value=item_data.get("value", 0)
            )
            player.inventory.equipped_weapon = item
        else:
            player.inventory.equipped_weapon = None
        
    @staticmethod
    def serialize_floor_states(floor_state_manager) -> Dict[str, Any]:
        """
        Сериализовать состояния этажей
        
        Args:
            floor_state_manager: Менеджер состояний этажей
            
        Returns:
            Данные состояний этажей
        """
        import numpy as np
        floors_data = {}
        
        for floor_num, floor_state in floor_state_manager.floors.items():
            floor_data = {
                "floor_number": floor_state.floor_number,
                "seed": floor_state.seed,
                "is_stabilized": floor_state.is_stabilized,
                "stability_rune_collected": floor_state.stability_rune_collected,
                "riddle_spawned": floor_state.riddle_spawned,
                "riddle_positions": floor_state.riddle_positions
            }
            
            # Сохраняем тайлы и позиции только для стабилизированных этажей
            if floor_state.is_stabilized and floor_state.saved_tiles is not None:
                floor_data["saved_tiles"] = floor_state.saved_tiles.tolist()
                floor_data["entrance_pos"] = floor_state.entrance_pos
                floor_data["exit_pos"] = floor_state.exit_pos
                
                # Сохраняем fog of war если есть
                if floor_state.saved_fog_of_war is not None:
                    floor_data["saved_fog_of_war"] = floor_state.saved_fog_of_war.tolist()
            
            floors_data[str(floor_num)] = floor_data
            
        return floors_data
        
    @staticmethod
    def deserialize_floor_states(floor_state_manager, data: Dict[str, Any]) -> None:
        """
        Десериализовать состояния этажей
        
        Args:
            floor_state_manager: Менеджер состояний этажей
            data: Данные для загрузки
        """
        import numpy as np
        from ..world.floor_state import FloorState
        
        for floor_num_str, floor_data in data.items():
            floor_num = int(floor_num_str)
            
            floor_state = FloorState(
                floor_number=floor_data["floor_number"],
                seed=floor_data["seed"],
                is_stabilized=floor_data["is_stabilized"]
            )
            
            floor_state.stability_rune_collected = floor_data["stability_rune_collected"]
            floor_state.riddle_spawned = floor_data["riddle_spawned"]
            floor_state.riddle_positions = floor_data.get("riddle_positions", [])
            
            # Восстанавливаем тайлы и позиции для стабилизированных этажей
            if floor_state.is_stabilized and "saved_tiles" in floor_data:
                floor_state.saved_tiles = np.array(floor_data["saved_tiles"], dtype=np.uint8)
                floor_state.entrance_pos = tuple(floor_data["entrance_pos"]) if floor_data.get("entrance_pos") else None
                floor_state.exit_pos = tuple(floor_data["exit_pos"]) if floor_data.get("exit_pos") else None
                
                # Восстанавливаем fog of war если есть
                if "saved_fog_of_war" in floor_data:
                    floor_state.saved_fog_of_war = np.array(floor_data["saved_fog_of_war"], dtype=np.uint8)
            
            floor_state_manager.floors[floor_num] = floor_state


if __name__ == "__main__":
    # Тест системы сохранений
    manager = SaveManager()
    
    # Тестовые данные
    test_data = {
        "player": {
            "x": 10,
            "y": 20,
            "health": 80
        },
        "current_floor": 5
    }
    
    # Сохранение
    manager.save_game("test_save", test_data)
    
    # Список сохранений
    saves = manager.list_saves()
    print(f"\nСохранения: {saves}")
    
    # Загрузка
    loaded_data = manager.load_game("test_save")
    print(f"\nЗагруженные данные: {loaded_data}")
    
    # Информация о сохранении
    info = manager.get_save_info("test_save")
    print(f"\nИнформация: {info}")
