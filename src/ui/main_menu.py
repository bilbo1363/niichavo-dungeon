"""
Главное меню игры с системой профилей
"""
import pygame
import os
import json
from typing import Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PlayerProfile:
    """Профиль игрока"""
    name: str
    created_at: str
    last_played: str
    play_time: float = 0.0  # Время игры в секундах
    current_floor: int = 0
    health: int = 100
    
    def to_dict(self) -> dict:
        """Конвертировать в словарь"""
        return {
            "name": self.name,
            "created_at": self.created_at,
            "last_played": self.last_played,
            "play_time": self.play_time,
            "current_floor": self.current_floor,
            "health": self.health
        }
    
    @staticmethod
    def from_dict(data: dict) -> "PlayerProfile":
        """Создать из словаря"""
        return PlayerProfile(
            name=data["name"],
            created_at=data["created_at"],
            last_played=data["last_played"],
            play_time=data.get("play_time", 0.0),
            current_floor=data.get("current_floor", 0),
            health=data.get("health", 100)
        )


class MainMenu:
    """Главное меню игры"""
    
    def __init__(self, width: int, height: int):
        """
        Инициализация меню
        
        Args:
            width: Ширина окна
            height: Высота окна
        """
        self.width = width
        self.height = height
        
        # Шрифты
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 48)
        self.profile_font = pygame.font.Font(None, 36)
        self.info_font = pygame.font.Font(None, 24)
        
        # Состояние меню
        self.state = "main"  # main, profiles, new_profile, confirm_delete
        self.selected_index = 0
        self.selected_profile: Optional[PlayerProfile] = None
        self.profile_to_delete: Optional[str] = None
        
        # Профили
        self.profiles_dir = "saves/profiles"
        self.profiles: List[PlayerProfile] = []
        self._load_profiles()
        
        # Ввод имени нового профиля
        self.new_profile_name = ""
        self.input_active = False
        
        # Цвета
        self.bg_color = (20, 20, 30)
        self.title_color = (255, 215, 0)
        self.menu_color = (200, 200, 200)
        self.selected_color = (255, 255, 100)
        self.profile_color = (150, 200, 255)
        
    def _load_profiles(self) -> None:
        """Загрузить список профилей"""
        self.profiles = []
        
        # Создаём директорию если не существует
        os.makedirs(self.profiles_dir, exist_ok=True)
        
        # Загружаем все профили (каждый профиль - это папка)
        for profile_name in os.listdir(self.profiles_dir):
            profile_path = os.path.join(self.profiles_dir, profile_name)
            
            # Проверяем что это директория
            if not os.path.isdir(profile_path):
                continue
            
            # Ищем файл метаданных profile.json
            metadata_file = os.path.join(profile_path, "profile.json")
            if os.path.exists(metadata_file):
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        profile = PlayerProfile.from_dict(data)
                        self.profiles.append(profile)
                except Exception as e:
                    print(f"Ошибка загрузки профиля {profile_name}: {e}")
        
        # Сортируем по времени последней игры
        self.profiles.sort(key=lambda p: p.last_played, reverse=True)
        
    def _save_profile(self, profile: PlayerProfile) -> None:
        """
        Сохранить профиль
        
        Args:
            profile: Профиль для сохранения
        """
        # Создаём папку профиля
        profile_path = os.path.join(self.profiles_dir, profile.name)
        os.makedirs(profile_path, exist_ok=True)
        
        # Сохраняем метаданные в profile.json
        metadata_file = os.path.join(profile_path, "profile.json")
        
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения профиля: {e}")
            
    def _delete_profile(self, profile_name: str) -> None:
        """
        Удалить профиль
        
        Args:
            profile_name: Имя профиля
        """
        profile_path = os.path.join(self.profiles_dir, profile_name)
        
        try:
            # Удаляем всю папку профиля со всеми файлами
            if os.path.exists(profile_path):
                import shutil
                shutil.rmtree(profile_path)
                
            self._load_profiles()
        except Exception as e:
            print(f"Ошибка удаления профиля: {e}")
            
    def handle_event(self, event: pygame.event.Event) -> Optional[Tuple[str, Optional[str]]]:
        """
        Обработка событий
        
        Args:
            event: Событие pygame
            
        Returns:
            Tuple[действие, имя_профиля] или None
            Действия: "start", "quit"
        """
        if event.type == pygame.KEYDOWN:
            if self.state == "main":
                return self._handle_main_menu(event)
            elif self.state == "profiles":
                return self._handle_profiles_menu(event)
            elif self.state == "new_profile":
                return self._handle_new_profile_input(event)
            elif self.state == "confirm_delete":
                return self._handle_confirm_delete(event)
                
        return None
        
    def _handle_main_menu(self, event: pygame.event.Event) -> Optional[Tuple[str, Optional[str]]]:
        """Обработка главного меню"""
        if event.key == pygame.K_UP:
            self.selected_index = (self.selected_index - 1) % 4
        elif event.key == pygame.K_DOWN:
            self.selected_index = (self.selected_index + 1) % 4
        elif event.key == pygame.K_RETURN:
            if self.selected_index == 0:  # Продолжить
                if self.profiles:
                    self.state = "profiles"
                    self.selected_index = 0
                else:
                    # Нет профилей - создаём новый
                    self.state = "new_profile"
                    self.new_profile_name = ""
                    self.input_active = True
            elif self.selected_index == 1:  # Новая игра
                self.state = "new_profile"
                self.new_profile_name = ""
                self.input_active = True
            elif self.selected_index == 2:  # Настройки
                return ("settings", None)
            elif self.selected_index == 3:  # Выход
                return ("quit", None)
                
        return None
        
    def _handle_profiles_menu(self, event: pygame.event.Event) -> Optional[Tuple[str, Optional[str]]]:
        """Обработка меню выбора профиля"""
        max_index = len(self.profiles)  # +1 для "Назад"
        
        if event.key == pygame.K_UP:
            self.selected_index = (self.selected_index - 1) % (max_index + 1)
        elif event.key == pygame.K_DOWN:
            self.selected_index = (self.selected_index + 1) % (max_index + 1)
        elif event.key == pygame.K_RETURN:
            if self.selected_index < len(self.profiles):
                # Выбран профиль
                profile = self.profiles[self.selected_index]
                profile.last_played = datetime.now().isoformat()
                self._save_profile(profile)
                return ("start", profile.name)
            else:
                # Назад
                self.state = "main"
                self.selected_index = 0
        elif event.key == pygame.K_DELETE:
            if self.selected_index < len(self.profiles):
                # Удалить профиль
                self.profile_to_delete = self.profiles[self.selected_index].name
                self.state = "confirm_delete"
        elif event.key == pygame.K_ESCAPE:
            self.state = "main"
            self.selected_index = 0
            
        return None
        
    def _handle_new_profile_input(self, event: pygame.event.Event) -> Optional[Tuple[str, Optional[str]]]:
        """Обработка ввода имени нового профиля"""
        if event.key == pygame.K_RETURN:
            if self.new_profile_name.strip():
                # Создаём новый профиль
                profile = PlayerProfile(
                    name=self.new_profile_name.strip(),
                    created_at=datetime.now().isoformat(),
                    last_played=datetime.now().isoformat()
                )
                self._save_profile(profile)
                self._load_profiles()
                return ("start", profile.name)
        elif event.key == pygame.K_ESCAPE:
            self.state = "main"
            self.selected_index = 0
            self.input_active = False
        elif event.key == pygame.K_BACKSPACE:
            self.new_profile_name = self.new_profile_name[:-1]
        else:
            # Добавляем символ
            if event.unicode.isprintable() and len(self.new_profile_name) < 20:
                self.new_profile_name += event.unicode
                
        return None
        
    def _handle_confirm_delete(self, event: pygame.event.Event) -> Optional[Tuple[str, Optional[str]]]:
        """Обработка подтверждения удаления"""
        if event.key == pygame.K_y:
            # Подтверждено - удаляем
            if self.profile_to_delete:
                self._delete_profile(self.profile_to_delete)
                self.profile_to_delete = None
            self.state = "profiles" if self.profiles else "main"
            self.selected_index = 0
        elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
            # Отменено
            self.profile_to_delete = None
            self.state = "profiles"
            
        return None
        
    def render(self, screen: pygame.Surface) -> None:
        """
        Отрисовка меню
        
        Args:
            screen: Поверхность для отрисовки
        """
        screen.fill(self.bg_color)
        
        if self.state == "main":
            self._render_main_menu(screen)
        elif self.state == "profiles":
            self._render_profiles_menu(screen)
        elif self.state == "new_profile":
            self._render_new_profile_input(screen)
        elif self.state == "confirm_delete":
            self._render_confirm_delete(screen)
            
    def _render_main_menu(self, screen: pygame.Surface) -> None:
        """Отрисовка главного меню"""
        # Получаем актуальные размеры экрана
        actual_width = screen.get_width()
        actual_height = screen.get_height()
        
        # Заголовок
        title = self.title_font.render("ПОДЗЕМЕЛЬЕ НИИЧАВО", True, self.title_color)
        title_rect = title.get_rect(center=(actual_width // 2, actual_height // 2 - 200))
        screen.blit(title, title_rect)
        
        # Подзаголовок
        subtitle = self.info_font.render("Roguelike с элементами головоломок", True, (150, 150, 150))
        subtitle_rect = subtitle.get_rect(center=(actual_width // 2, actual_height // 2 - 140))
        screen.blit(subtitle, subtitle_rect)
        
        # Пункты меню
        menu_items = ["Продолжить", "Новая игра", "⚙️ Настройки", "Выход"]
        start_y = actual_height // 2 - 80
        
        for i, item in enumerate(menu_items):
            color = self.selected_color if i == self.selected_index else self.menu_color
            text = self.menu_font.render(item, True, color)
            text_rect = text.get_rect(center=(actual_width // 2, start_y + i * 80))
            screen.blit(text, text_rect)
            
        # Подсказка
        hint = self.info_font.render("↑↓ - выбор | ENTER - подтвердить", True, (100, 100, 100))
        hint_rect = hint.get_rect(center=(actual_width // 2, actual_height - 50))
        screen.blit(hint, hint_rect)
        
    def _render_profiles_menu(self, screen: pygame.Surface) -> None:
        """Отрисовка меню выбора профиля"""
        # Заголовок
        title = self.menu_font.render("Выберите профиль", True, self.title_color)
        title_rect = title.get_rect(center=(self.width // 2, 80))
        screen.blit(title, title_rect)
        
        # Профили
        start_y = 180
        for i, profile in enumerate(self.profiles):
            color = self.selected_color if i == self.selected_index else self.profile_color
            
            # Имя профиля
            name_text = self.profile_font.render(f"👤 {profile.name}", True, color)
            name_rect = name_text.get_rect(center=(self.width // 2, start_y + i * 100))
            screen.blit(name_text, name_rect)
            
            # Информация о профиле
            info_lines = []
            if profile.current_floor > 0:
                info_lines.append(f"Этаж: {profile.current_floor}")
            info_lines.append(f"HP: {profile.health}")
            
            hours = int(profile.play_time // 3600)
            minutes = int((profile.play_time % 3600) // 60)
            if hours > 0:
                info_lines.append(f"Время: {hours}ч {minutes}м")
            elif minutes > 0:
                info_lines.append(f"Время: {minutes}м")
            
            info_text = " | ".join(info_lines)
            info_surface = self.info_font.render(info_text, True, (150, 150, 150))
            info_rect = info_surface.get_rect(center=(self.width // 2, start_y + i * 100 + 30))
            screen.blit(info_surface, info_rect)
            
        # Кнопка "Назад"
        back_color = self.selected_color if self.selected_index == len(self.profiles) else self.menu_color
        back_text = self.profile_font.render("← Назад", True, back_color)
        back_rect = back_text.get_rect(center=(self.width // 2, start_y + len(self.profiles) * 100 + 50))
        screen.blit(back_text, back_rect)
        
        # Подсказки
        hint1 = self.info_font.render("↑↓ - выбор | ENTER - играть | DELETE - удалить | ESC - назад", True, (100, 100, 100))
        hint1_rect = hint1.get_rect(center=(self.width // 2, self.height - 50))
        screen.blit(hint1, hint1_rect)
        
    def _render_new_profile_input(self, screen: pygame.Surface) -> None:
        """Отрисовка ввода имени нового профиля"""
        # Заголовок
        title = self.menu_font.render("Создание нового профиля", True, self.title_color)
        title_rect = title.get_rect(center=(self.width // 2, 150))
        screen.blit(title, title_rect)
        
        # Подсказка
        prompt = self.profile_font.render("Введите имя:", True, self.menu_color)
        prompt_rect = prompt.get_rect(center=(self.width // 2, 250))
        screen.blit(prompt, prompt_rect)
        
        # Поле ввода
        input_text = self.new_profile_name + "_"
        input_surface = self.menu_font.render(input_text, True, self.selected_color)
        input_rect = input_surface.get_rect(center=(self.width // 2, 320))
        
        # Рамка вокруг поля ввода
        border_rect = pygame.Rect(input_rect.x - 20, input_rect.y - 10, input_rect.width + 40, input_rect.height + 20)
        pygame.draw.rect(screen, self.selected_color, border_rect, 2)
        
        screen.blit(input_surface, input_rect)
        
        # Подсказка
        hint = self.info_font.render("ENTER - создать | ESC - отмена | Макс. 20 символов", True, (100, 100, 100))
        hint_rect = hint.get_rect(center=(self.width // 2, self.height - 50))
        screen.blit(hint, hint_rect)
        
    def _render_confirm_delete(self, screen: pygame.Surface) -> None:
        """Отрисовка подтверждения удаления"""
        # Затемнение фона
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Окно подтверждения
        box_width = 600
        box_height = 300
        box_x = (self.width - box_width) // 2
        box_y = (self.height - box_height) // 2
        
        pygame.draw.rect(screen, (40, 40, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 100, 100), (box_x, box_y, box_width, box_height), 3)
        
        # Текст
        title = self.menu_font.render("Удалить профиль?", True, (255, 100, 100))
        title_rect = title.get_rect(center=(self.width // 2, box_y + 80))
        screen.blit(title, title_rect)
        
        if self.profile_to_delete:
            name = self.profile_font.render(f'"{self.profile_to_delete}"', True, (255, 255, 255))
            name_rect = name.get_rect(center=(self.width // 2, box_y + 140))
            screen.blit(name, name_rect)
        
        warning = self.info_font.render("Все сохранения будут удалены!", True, (255, 200, 100))
        warning_rect = warning.get_rect(center=(self.width // 2, box_y + 180))
        screen.blit(warning, warning_rect)
        
        # Кнопки
        hint = self.profile_font.render("Y - Да | N - Нет", True, (200, 200, 200))
        hint_rect = hint.get_rect(center=(self.width // 2, box_y + 230))
        screen.blit(hint, hint_rect)


if __name__ == "__main__":
    # Тест главного меню
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Main Menu Test")
    clock = pygame.time.Clock()
    
    menu = MainMenu(1200, 800)
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                result = menu.handle_event(event)
                if result:
                    action, profile_name = result
                    if action == "quit":
                        running = False
                    elif action == "start":
                        print(f"Запуск игры с профилем: {profile_name}")
                        running = False
                        
        menu.render(screen)
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()
