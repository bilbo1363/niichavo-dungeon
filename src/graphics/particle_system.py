"""
Система частиц для визуальных эффектов
"""
import pygame
import random
from typing import List, Tuple


class Particle:
    """Класс частицы"""
    
    def __init__(self, x: float, y: float, vx: float, vy: float, 
                 color: Tuple[int, int, int], lifetime: float = 1.0, size: int = 3):
        """
        Инициализация частицы
        
        Args:
            x, y: Позиция
            vx, vy: Скорость
            color: Цвет RGB
            lifetime: Время жизни в секундах
            size: Размер
        """
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.gravity = 100.0  # Гравитация
        
    def update(self, dt: float) -> bool:
        """
        Обновление частицы
        
        Args:
            dt: Delta time
            
        Returns:
            True если частица жива
        """
        self.lifetime -= dt
        
        if self.lifetime <= 0:
            return False
            
        # Обновляем позицию
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Применяем гравитацию
        self.vy += self.gravity * dt
        
        return True
        
    def render(self, screen: pygame.Surface, camera_x: int = 0, camera_y: int = 0) -> None:
        """
        Отрисовка частицы
        
        Args:
            screen: Поверхность для отрисовки
            camera_x, camera_y: Смещение камеры
        """
        # Вычисляем прозрачность
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        
        # Вычисляем размер (уменьшается со временем)
        current_size = max(1, int(self.size * (self.lifetime / self.max_lifetime)))
        
        # Создаём поверхность с прозрачностью
        surf = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
        color_with_alpha = (*self.color, alpha)
        pygame.draw.circle(surf, color_with_alpha, (current_size, current_size), current_size)
        
        # Рисуем на экране
        screen_x = int(self.x - camera_x - current_size)
        screen_y = int(self.y - camera_y - current_size)
        screen.blit(surf, (screen_x, screen_y))


class ParticleSystem:
    """Система частиц"""
    
    def __init__(self):
        """Инициализация системы"""
        self.particles: List[Particle] = []
        
    def emit(self, x: float, y: float, count: int, effect_type: str = "explosion") -> None:
        """
        Создать эффект
        
        Args:
            x, y: Позиция
            count: Количество частиц
            effect_type: Тип эффекта
        """
        if effect_type == "explosion":
            self._emit_explosion(x, y, count)
        elif effect_type == "blood":
            self._emit_blood(x, y, count)
        elif effect_type == "sparkle":
            self._emit_sparkle(x, y, count)
        elif effect_type == "smoke":
            self._emit_smoke(x, y, count)
            
    def _emit_explosion(self, x: float, y: float, count: int) -> None:
        """Эффект взрыва"""
        for _ in range(count):
            angle = random.uniform(0, 6.28)
            speed = random.uniform(50, 150)
            vx = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).x
            vy = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).y
            
            color = random.choice([
                (255, 200, 0),   # Жёлтый
                (255, 100, 0),   # Оранжевый
                (255, 50, 0),    # Красный
            ])
            
            particle = Particle(x, y, vx, vy, color, 
                              lifetime=random.uniform(0.3, 0.8),
                              size=random.randint(2, 5))
            self.particles.append(particle)
            
    def _emit_blood(self, x: float, y: float, count: int) -> None:
        """Эффект крови"""
        for _ in range(count):
            angle = random.uniform(0, 6.28)
            speed = random.uniform(30, 100)
            vx = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).x
            vy = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).y - 50  # Вверх
            
            color = random.choice([
                (200, 0, 0),     # Тёмно-красный
                (255, 0, 0),     # Красный
                (150, 0, 0),     # Очень тёмно-красный
            ])
            
            particle = Particle(x, y, vx, vy, color,
                              lifetime=random.uniform(0.5, 1.0),
                              size=random.randint(2, 4))
            particle.gravity = 200.0  # Больше гравитация
            self.particles.append(particle)
            
    def _emit_sparkle(self, x: float, y: float, count: int) -> None:
        """Эффект искр"""
        for _ in range(count):
            angle = random.uniform(0, 6.28)
            speed = random.uniform(20, 80)
            vx = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).x
            vy = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).y
            
            color = random.choice([
                (255, 255, 0),   # Жёлтый
                (255, 255, 255), # Белый
                (255, 200, 100), # Золотой
            ])
            
            particle = Particle(x, y, vx, vy, color,
                              lifetime=random.uniform(0.2, 0.5),
                              size=random.randint(1, 3))
            particle.gravity = 0  # Без гравитации
            self.particles.append(particle)
            
    def _emit_smoke(self, x: float, y: float, count: int) -> None:
        """Эффект дыма"""
        for _ in range(count):
            vx = random.uniform(-20, 20)
            vy = random.uniform(-80, -40)  # Вверх
            
            color = random.choice([
                (100, 100, 100), # Серый
                (80, 80, 80),    # Тёмно-серый
                (120, 120, 120), # Светло-серый
            ])
            
            particle = Particle(x, y, vx, vy, color,
                              lifetime=random.uniform(0.8, 1.5),
                              size=random.randint(4, 8))
            particle.gravity = -20.0  # Поднимается вверх
            self.particles.append(particle)
            
    def update(self, dt: float) -> None:
        """
        Обновление всех частиц
        
        Args:
            dt: Delta time
        """
        # Обновляем и удаляем мёртвые частицы
        self.particles = [p for p in self.particles if p.update(dt)]
        
    def render(self, screen: pygame.Surface, camera_x: int = 0, camera_y: int = 0) -> None:
        """
        Отрисовка всех частиц
        
        Args:
            screen: Поверхность для отрисовки
            camera_x, camera_y: Смещение камеры
        """
        for particle in self.particles:
            particle.render(screen, camera_x, camera_y)
            
    def clear(self) -> None:
        """Очистить все частицы"""
        self.particles.clear()


if __name__ == "__main__":
    # Тест системы частиц
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    particle_system = ParticleSystem()
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if event.button == 1:  # ЛКМ
                    particle_system.emit(x, y, 20, "explosion")
                elif event.button == 3:  # ПКМ
                    particle_system.emit(x, y, 15, "blood")
                    
        particle_system.update(dt)
        
        screen.fill((0, 0, 0))
        particle_system.render(screen)
        
        # Подсказка
        font = pygame.font.Font(None, 24)
        text = font.render("ЛКМ - взрыв, ПКМ - кровь", True, (255, 255, 255))
        screen.blit(text, (10, 10))
        
        pygame.display.flip()
        
    pygame.quit()
