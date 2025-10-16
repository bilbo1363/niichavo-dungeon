"""
Менеджер спрайтов и анимаций
"""
import pygame
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class Animation:
    """Класс анимации"""
    
    def __init__(self, frames: List[pygame.Surface], frame_duration: float = 0.1):
        """
        Инициализация анимации
        
        Args:
            frames: Список кадров
            frame_duration: Длительность одного кадра в секундах
        """
        self.frames = frames
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.time_accumulator = 0.0
        self.loop = True
        
    def update(self, dt: float) -> None:
        """
        Обновление анимации
        
        Args:
            dt: Delta time
        """
        self.time_accumulator += dt
        
        if self.time_accumulator >= self.frame_duration:
            self.time_accumulator = 0.0
            self.current_frame += 1
            
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    
    def get_current_frame(self) -> pygame.Surface:
        """
        Получить текущий кадр
        
        Returns:
            Поверхность текущего кадра
        """
        return self.frames[self.current_frame]
        
    def reset(self) -> None:
        """Сбросить анимацию"""
        self.current_frame = 0
        self.time_accumulator = 0.0


class SpriteManager:
    """Менеджер спрайтов"""
    
    def __init__(self):
        """Инициализация менеджера"""
        self.sprites: Dict[str, pygame.Surface] = {}
        self.animations: Dict[str, Animation] = {}
        self.assets_path = Path("assets")
        
        # Создаём базовые процедурные спрайты
        self._create_procedural_sprites()
        
    def _create_procedural_sprites(self) -> None:
        """Создание процедурных спрайтов (пока нет графики)"""
        
        # Игрок
        self._create_player_sprite()
        
        # Враги
        self._create_enemy_sprites()
        
        # Предметы
        self._create_item_sprites()
        
        # Тайлы
        self._create_tile_sprites()
        
        # Эффекты
        self._create_effect_sprites()
        
    def _create_player_sprite(self) -> None:
        """Создать спрайт игрока"""
        size = 32
        
        # Базовый спрайт (круг с лицом)
        sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Тело (синий круг)
        pygame.draw.circle(sprite, (100, 150, 255), (size // 2, size // 2), size // 3)
        
        # Глаза
        pygame.draw.circle(sprite, (255, 255, 255), (size // 2 - 5, size // 2 - 3), 3)
        pygame.draw.circle(sprite, (255, 255, 255), (size // 2 + 5, size // 2 - 3), 3)
        pygame.draw.circle(sprite, (0, 0, 0), (size // 2 - 5, size // 2 - 3), 2)
        pygame.draw.circle(sprite, (0, 0, 0), (size // 2 + 5, size // 2 - 3), 2)
        
        # Улыбка
        pygame.draw.arc(sprite, (0, 0, 0), 
                       (size // 2 - 8, size // 2 - 2, 16, 12), 
                       3.14, 6.28, 2)
        
        self.sprites["player"] = sprite
        
        # Анимация ходьбы (простая - покачивание)
        frames = []
        for i in range(4):
            frame = sprite.copy()
            offset = (i % 2) * 2 - 1
            # Можно добавить покачивание
            frames.append(frame)
        
        self.animations["player_walk"] = Animation(frames, 0.15)
        
    def _create_enemy_sprites(self) -> None:
        """Создать спрайты врагов"""
        size = 32
        
        enemies = {
            "rat": (139, 69, 19),      # Коричневый
            "zombie": (100, 150, 100), # Зелёный
            "ghost": (200, 200, 255),  # Голубой
            "mutant": (200, 50, 50),   # Красный
        }
        
        for enemy_name, color in enemies.items():
            sprite = pygame.Surface((size, size), pygame.SRCALPHA)
            
            # Тело (круг)
            pygame.draw.circle(sprite, color, (size // 2, size // 2), size // 3)
            
            # Злые глаза
            pygame.draw.circle(sprite, (255, 0, 0), (size // 2 - 5, size // 2 - 3), 3)
            pygame.draw.circle(sprite, (255, 0, 0), (size // 2 + 5, size // 2 - 3), 3)
            pygame.draw.circle(sprite, (0, 0, 0), (size // 2 - 5, size // 2 - 3), 2)
            pygame.draw.circle(sprite, (0, 0, 0), (size // 2 + 5, size // 2 - 3), 2)
            
            # Зубы/рот
            pygame.draw.line(sprite, (255, 255, 255), 
                           (size // 2 - 6, size // 2 + 5), 
                           (size // 2 + 6, size // 2 + 5), 2)
            
            self.sprites[f"enemy_{enemy_name}"] = sprite
            
    def _create_item_sprites(self) -> None:
        """Создать спрайты предметов"""
        size = 24
        
        # Оружие (меч)
        weapon = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(weapon, (150, 150, 150), (size // 2 - 2, 4, 4, size - 8))
        pygame.draw.polygon(weapon, (200, 200, 200), 
                          [(size // 2, 2), (size // 2 - 4, 6), (size // 2 + 4, 6)])
        self.sprites["item_weapon"] = weapon
        
        # Зелье (бутылка)
        potion = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(potion, (100, 200, 100), (size // 2 - 4, 8, 8, 12))
        pygame.draw.rect(potion, (150, 150, 150), (size // 2 - 2, 6, 4, 3))
        self.sprites["item_potion"] = potion
        
        # Бинт
        bandage = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(bandage, (255, 255, 255), (6, size // 2 - 3, 12, 6))
        pygame.draw.line(bandage, (255, 0, 0), (12, size // 2 - 2), (12, size // 2 + 2), 2)
        pygame.draw.line(bandage, (255, 0, 0), (10, size // 2), (14, size // 2), 2)
        self.sprites["item_bandage"] = bandage
        
        # Руна
        rune = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(rune, (255, 215, 0), (size // 2, size // 2), 8)
        pygame.draw.circle(rune, (255, 255, 0), (size // 2, size // 2), 6)
        # Символ
        pygame.draw.line(rune, (100, 50, 0), (size // 2, size // 2 - 4), (size // 2, size // 2 + 4), 2)
        pygame.draw.line(rune, (100, 50, 0), (size // 2 - 4, size // 2), (size // 2 + 4, size // 2), 2)
        self.sprites["item_rune"] = rune
        
    def _create_tile_sprites(self) -> None:
        """Создать спрайты тайлов"""
        size = 32
        
        # Пол (улучшенный)
        floor = pygame.Surface((size, size))
        floor.fill((60, 60, 60))
        # Добавляем текстуру
        for i in range(4):
            for j in range(4):
                if (i + j) % 2 == 0:
                    pygame.draw.rect(floor, (65, 65, 65), (i * 8, j * 8, 8, 8))
        self.sprites["tile_floor"] = floor
        
        # Стена (улучшенная)
        wall = pygame.Surface((size, size))
        wall.fill((40, 40, 40))
        # Кирпичи
        for i in range(2):
            for j in range(2):
                pygame.draw.rect(wall, (50, 50, 50), (i * 16 + 1, j * 16 + 1, 14, 14))
                pygame.draw.rect(wall, (30, 30, 30), (i * 16, j * 16, 16, 16), 1)
        self.sprites["tile_wall"] = wall
        
        # Вход/выход
        entrance = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(entrance, (0, 255, 0), (size // 2, size // 2), size // 3)
        pygame.draw.polygon(entrance, (255, 255, 255), 
                          [(size // 2, size // 2 - 6), 
                           (size // 2 - 4, size // 2 + 4), 
                           (size // 2 + 4, size // 2 + 4)])
        self.sprites["tile_entrance"] = entrance
        
        exit_sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(exit_sprite, (255, 0, 0), (size // 2, size // 2), size // 3)
        pygame.draw.polygon(exit_sprite, (255, 255, 255), 
                          [(size // 2, size // 2 + 6), 
                           (size // 2 - 4, size // 2 - 4), 
                           (size // 2 + 4, size // 2 - 4)])
        self.sprites["tile_exit"] = exit_sprite
        
    def _create_effect_sprites(self) -> None:
        """Создать спрайты эффектов"""
        size = 32
        
        # Эффект атаки (вспышка)
        frames = []
        for i in range(4):
            frame = pygame.Surface((size, size), pygame.SRCALPHA)
            radius = (4 - i) * 4
            alpha = 255 - i * 60
            color = (255, 255, 0, alpha)
            pygame.draw.circle(frame, color, (size // 2, size // 2), radius)
            frames.append(frame)
        
        self.animations["effect_attack"] = Animation(frames, 0.05)
        self.animations["effect_attack"].loop = False
        
    def get_sprite(self, name: str) -> Optional[pygame.Surface]:
        """
        Получить спрайт
        
        Args:
            name: Имя спрайта
            
        Returns:
            Поверхность спрайта или None
        """
        return self.sprites.get(name)
        
    def get_animation(self, name: str) -> Optional[Animation]:
        """
        Получить анимацию
        
        Args:
            name: Имя анимации
            
        Returns:
            Анимация или None
        """
        return self.animations.get(name)
        
    def load_sprite(self, name: str, path: str) -> bool:
        """
        Загрузить спрайт из файла
        
        Args:
            name: Имя спрайта
            path: Путь к файлу
            
        Returns:
            True если успешно
        """
        try:
            sprite = pygame.image.load(path).convert_alpha()
            self.sprites[name] = sprite
            return True
        except:
            print(f"⚠️  Не удалось загрузить спрайт: {path}")
            return False


if __name__ == "__main__":
    # Тест менеджера спрайтов
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    manager = SpriteManager()
    
    print(f"Загружено спрайтов: {len(manager.sprites)}")
    print(f"Загружено анимаций: {len(manager.animations)}")
    
    # Тест отрисовки
    running = True
    clock = pygame.time.Clock()
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        screen.fill((0, 0, 0))
        
        # Рисуем все спрайты
        x, y = 50, 50
        for name, sprite in manager.sprites.items():
            screen.blit(sprite, (x, y))
            x += 40
            if x > 700:
                x = 50
                y += 40
                
        pygame.display.flip()
        
    pygame.quit()
