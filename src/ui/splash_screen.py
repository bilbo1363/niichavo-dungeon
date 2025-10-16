"""
Заставка игры (Splash Screen)
"""
import pygame
from pathlib import Path


class SplashScreen:
    """Заставка при запуске игры"""
    
    def __init__(self, width: int, height: int):
        """
        Инициализация заставки
        
        Args:
            width: Ширина окна
            height: Высота окна
        """
        self.width = width
        self.height = height
        
        # Загружаем изображение
        self.image = None
        self.scaled_image = None
        self.image_x = 0
        self.image_y = 0
        self._load_image()
        
        # Анимация fade
        self.alpha = 0
        self.fade_in_speed = 3  # Скорость появления
        self.fade_out_speed = 5  # Скорость исчезновения
        self.state = "fade_in"  # fade_in, showing, fade_out, done
        self.show_time = 0  # Время показа
        
        # Флаг пропуска
        self.can_skip = False
        self.skip_delay = 0.5  # Можно пропустить через 0.5 сек
        
    def _load_image(self) -> None:
        """Загрузка изображения заставки"""
        image_path = Path("assets/images/splash.png")
        
        if image_path.exists():
            try:
                # Загружаем изображение
                self.image = pygame.image.load(str(image_path)).convert()
                
                # Получаем размеры оригинального изображения
                img_width = self.image.get_width()
                img_height = self.image.get_height()
                
                # Вычисляем соотношение сторон
                img_ratio = img_width / img_height
                screen_ratio = self.width / self.height
                
                # Масштабируем с сохранением пропорций
                if img_ratio > screen_ratio:
                    # Изображение шире экрана - подгоняем по ширине
                    new_width = self.width
                    new_height = int(self.width / img_ratio)
                else:
                    # Изображение выше экрана - подгоняем по высоте
                    new_height = self.height
                    new_width = int(self.height * img_ratio)
                
                self.scaled_image = pygame.transform.scale(
                    self.image, 
                    (new_width, new_height)
                )
                
                # Вычисляем позицию для центрирования
                self.image_x = (self.width - new_width) // 2
                self.image_y = (self.height - new_height) // 2
                
                print(f"✅ Заставка загружена: {image_path}")
                print(f"   Размер: {new_width}x{new_height}, позиция: ({self.image_x}, {self.image_y})")
            except Exception as e:
                print(f"⚠️ Ошибка загрузки заставки: {e}")
                self.image = None
        else:
            print(f"⚠️ Файл заставки не найден: {image_path}")
            # Создаём простую заставку
            self._create_fallback_splash()
    
    def _create_fallback_splash(self) -> None:
        """Создание простой заставки если файл не найден"""
        self.scaled_image = pygame.Surface((self.width, self.height))
        self.scaled_image.fill((26, 26, 46))  # Тёмно-синий фон
        
        # Рисуем текст
        font_large = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 36)
        
        title = font_large.render("ПОДЗЕМЕЛЬЕ НИИЧАВО", True, (255, 215, 0))
        subtitle = font_small.render("Roguelike Adventure", True, (200, 200, 200))
        
        title_rect = title.get_rect(center=(self.width // 2, self.height // 2 - 50))
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, self.height // 2 + 50))
        
        self.scaled_image.blit(title, title_rect)
        self.scaled_image.blit(subtitle, subtitle_rect)
        
        # Для fallback координаты (0, 0) так как это полноэкранное изображение
        self.image_x = 0
        self.image_y = 0
    
    def update(self, dt: float) -> bool:
        """
        Обновление заставки
        
        Args:
            dt: Время с последнего кадра
            
        Returns:
            True если заставка завершена
        """
        if self.state == "done":
            return True
        
        # Обновляем время показа
        self.show_time += dt
        
        # Разрешаем пропуск после задержки
        if self.show_time >= self.skip_delay:
            self.can_skip = True
        
        # Fade in
        if self.state == "fade_in":
            self.alpha += self.fade_in_speed
            if self.alpha >= 255:
                self.alpha = 255
                self.state = "showing"
        
        # Showing - просто показываем, НЕ исчезаем автоматически
        elif self.state == "showing":
            # Ждём нажатия клавиши (обрабатывается в handle_input)
            pass
        
        # Fade out
        elif self.state == "fade_out":
            self.alpha -= self.fade_out_speed
            if self.alpha <= 0:
                self.alpha = 0
                self.state = "done"
                return True
        
        return False
    
    def handle_input(self, event: pygame.event.Event) -> None:
        """
        Обработка ввода
        
        Args:
            event: Событие pygame
        """
        # Пропуск по любой клавише или клику мыши
        if self.can_skip and self.state != "done":
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                # Начинаем fade out
                if self.state != "fade_out":
                    self.state = "fade_out"
    
    def render(self, screen: pygame.Surface) -> None:
        """
        Отрисовка заставки
        
        Args:
            screen: Поверхность для отрисовки
        """
        if self.scaled_image is None:
            return
        
        # Создаём копию с прозрачностью
        temp_surface = self.scaled_image.copy()
        temp_surface.set_alpha(int(self.alpha))
        
        # Рисуем на экране
        screen.fill((0, 0, 0))  # Чёрный фон
        screen.blit(temp_surface, (self.image_x, self.image_y))  # Используем вычисленные координаты
        
        # Подсказка "Press any key" (только после задержки)
        if self.can_skip and self.state == "showing":
            font = pygame.font.Font(None, 24)
            
            # Мигающий текст
            pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500.0
            alpha = int(100 + 155 * pulse)
            
            hint = font.render("Press any key to continue", True, (200, 200, 200))
            hint.set_alpha(alpha)
            hint_rect = hint.get_rect(center=(self.width // 2, self.height - 50))
            screen.blit(hint, hint_rect)
    
    def is_done(self) -> bool:
        """
        Проверка завершения заставки
        
        Returns:
            True если заставка завершена
        """
        return self.state == "done"
