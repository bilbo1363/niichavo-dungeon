"""
Главный класс игры
"""
import pygame
import os
from typing import Optional
from ..entities.player import Player
from ..world.level import Level
from ..world.level_generator import LevelGenerator
from ..world.attic import Attic
from ..input.input_manager import InputManager
from ..save.save_manager import SaveManager, GameStateSerializer
from ..ui.inventory_ui import InventoryUI
from ..ui.storage_ui import StorageUI
from ..ui.riddle_ui import RiddleUI
from ..ui.message_log import MessageLog
from ..ui.main_menu import MainMenu
from ..combat.combat_system import CombatSystem
from ..graphics.sprite_manager import SpriteManager
from ..graphics.particle_system import ParticleSystem
from ..story.story_manager import StoryManager
from ..story.dialogue_system import DialogueUI


class Game:
    """Основной класс игры"""
    
    def __init__(self, width: int = 1200, height: int = 800, fullscreen: bool = False):
        """
        Инициализация игры
        
        Args:
            width: Ширина окна
            height: Высота окна
            fullscreen: Полноэкранный режим
        """
        # Инициализация Pygame
        pygame.init()
        
        # Параметры окна
        self.fullscreen = fullscreen
        self.windowed_size = (width, height)
        
        # Получаем размер экрана
        display_info = pygame.display.Info()
        self.screen_width = display_info.current_w
        self.screen_height = display_info.current_h
        
        # Устанавливаем режим отображения
        if fullscreen:
            self.width = self.screen_width
            self.height = self.screen_height
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        else:
            self.width = width
            self.height = height
            self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        
        pygame.display.set_caption("Подземелье НИИЧАВО")
        
        # Игровой цикл
        self.clock = pygame.time.Clock()
        self.running = False
        self.fps = 60
        
        # FPS счётчик
        self.show_fps = False  # Показывать ли FPS (F3 для переключения)
        self.fps_update_time = 0.0  # Время с последнего обновления FPS
        self.fps_frames = 0  # Количество кадров с последнего обновления
        self.current_fps = 0  # Текущий FPS для отображения
        
        # Создаём генератор уровней
        self.level_generator = LevelGenerator(game_id="game_001")
        
        # Создаём чердак
        self.attic = Attic()
        
        # Менеджер сохранений
        self.save_manager = SaveManager()
        self.serializer = GameStateSerializer()
        
        # UI (используем self.width и self.height - они уже учитывают fullscreen)
        self.inventory_ui = InventoryUI(self.width, self.height)
        self.storage_ui = StorageUI(self.width, self.height)
        self.riddle_ui = RiddleUI(self.width, self.height)
        self.message_log = MessageLog(self.width, self.height)
        
        from ..ui.settings_ui import SettingsUI
        self.settings_ui = SettingsUI(self.width, self.height)
        
        from ..ui.splash_screen import SplashScreen
        self.splash_screen = SplashScreen(self.width, self.height)
        
        self.show_inventory_ui = False
        self.show_storage_ui = False
        self.show_riddle_ui = False
        self.show_settings_ui = False
        self.show_splash = True  # Показываем заставку при запуске
        self.current_riddle = None
        
        # Боевая система
        self.combat = CombatSystem()
        
        # Графика
        self.sprite_manager = SpriteManager()
        self.particle_system = ParticleSystem()
        
        # Звук
        from ..audio.sound_manager import SoundManager
        self.sound_manager = SoundManager()
        
        # Подключаем колбэки настроек к звуковому менеджеру
        self.settings_ui.on_music_toggle = self._on_music_toggle
        self.settings_ui.on_sfx_toggle = self._on_sfx_toggle
        self.settings_ui.on_music_volume_change = self._on_music_volume_change
        self.settings_ui.on_sfx_volume_change = self._on_sfx_volume_change
        self.settings_ui.on_back = self._on_settings_back
        
        # Подключаем систему частиц и лог к боевой системе
        self.combat.particle_system = self.particle_system
        self.combat.message_log = self.message_log
        
        # Сюжет
        self.story_manager = StoryManager()
        self.dialogue_ui = DialogueUI(width, height)
        self.current_dialogue = None
        self.show_dialogue = False
        
        # Флаг смерти игрока
        self.player_dead = False
        self.death_timer = 0.0
        
        # Главное меню
        self.main_menu = MainMenu(width, height)
        self.show_main_menu = True
        self.current_profile = None
        
        # Диалог выхода
        self.show_exit_dialog = False
        
        # Трекинг времени игры
        self.session_start_time = 0.0
        self.total_play_time = 0.0
        
        # Текущая локация: "attic" или номер этажа (1-20)
        self.current_location = "attic"
        self.current_floor = 0  # 0 = чердак, 1-20 = этажи подземелья
        
        # Текущий уровень (None если на чердаке)
        self.current_level = None
        
        # Создаём игрока на чердаке
        if self.attic.spawn_pos:
            spawn_x, spawn_y = self.attic.spawn_pos
            self.player = Player(x=spawn_x, y=spawn_y)
        else:
            self.player = Player(x=15, y=10)
        
        # Устанавливаем message_log для игрока
        self.player.message_log = self.message_log
            
        self.input_manager = InputManager()
        
        # Камера
        self.camera_x = 0
        self.camera_y = 0
        
        # Флаг для предотвращения повторных переходов
        self.can_transition = True
        
        # Система записок НИИЧАВО
        self.current_note = None  # Текущая показываемая записка
        self.show_note = False  # Показывать ли записку
        
        # Система движения
        self.move_timer = 0.0
        self.move_delay = 0.08  # Задержка между шагами (секунды) - комфортная скорость
        self.run_move_delay = 0.05  # Задержка при беге (быстрее)
        self.run_endurance_cost = 2  # Стоимость бега в выносливости за шаг
        
        print("✅ Игра инициализирована")
        print(f"📺 Разрешение: {width}x{height}")
        print(f"⚙️  FPS: {self.fps}")
        print(f"🎮 Управление: WASD или стрелки (удерживайте для движения)")
        print(f"🏃 Бег: Shift + направление (тратит выносливость)")
        
    def run(self) -> None:
        """Главный игровой цикл"""
        self.running = True
        print("\n🎮 Игра запущена!")
        print("Нажмите ESC для выхода\n")
        
        # Запускаем фоновую музыку (тема чердака если на чердаке)
        if self.current_location == "attic":
            self.sound_manager.start_music("attic")
        else:
            self.sound_manager.start_music()
        
        while self.running:
            # Delta time
            dt = self.clock.tick(self.fps) / 1000.0
            
            # Обновляем FPS счётчик
            self._update_fps_counter(dt)
            
            # Если показываем заставку - только её обрабатываем
            if self.show_splash:
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        self.running = False
                    self.splash_screen.handle_input(event)
                
                # Обновляем заставку
                if self.splash_screen.update(dt):
                    self.show_splash = False
                
                # Рисуем заставку
                self.splash_screen.render(self.screen)
                pygame.display.flip()
                continue
            
            # Обработка событий
            self._handle_events()
            
            # Обновление (только если не открыт UI)
            if not self.show_main_menu and not self._any_ui_open():
                self._update(dt)
                # Трекаем время игры
                if self.current_profile:
                    self.total_play_time += dt
            
            # Отрисовка
            self._render()
            
            # Обновление экрана
            pygame.display.flip()
            
        self._quit()
        
    def _handle_events(self) -> None:
        """Обработка событий"""
        events = pygame.event.get()
        
        # ВАЖНО: Обновляем менеджер ввода ПЕРЕД всеми проверками
        # Это предотвращает "залипание" клавиш при открытии/закрытии UI
        self.input_manager.update(events)
        
        # Если открыты настройки - обрабатываем ТОЛЬКО их ввод (приоритет!)
        if self.show_settings_ui:
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                self.settings_ui.handle_input(event)
            return
        
        # Если показана записка НИИЧАВО - обрабатываем её закрытие
        if self.show_note:
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE]:
                        self.show_note = False
            return
        
        # Если показано главное меню - обрабатываем его ввод
        if self.show_main_menu:
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                result = self.main_menu.handle_event(event)
                if result:
                    action, profile_name = result
                    if action == "quit":
                        self.running = False
                    elif action == "start":
                        self.current_profile = profile_name
                        self.show_main_menu = False
                        self._start_game_with_profile(profile_name)
                    elif action == "settings":
                        self.show_settings_ui = True
            return
        
        # Если открыт инвентарь - обрабатываем его ввод
        if self.show_inventory_ui:
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                if self.inventory_ui.handle_input(event, self.player.inventory, self.player):
                    self.show_inventory_ui = False
                    self.inventory_ui.selected_slot = None
            return
        
        # Если открыто хранилище - обрабатываем его ввод
        if self.show_storage_ui:
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                if self.storage_ui.handle_input(event, self.player.inventory, self.attic.storage):
                    self.show_storage_ui = False
                    self.storage_ui.selected_inventory_slot = None
                    self.storage_ui.selected_storage_slot = None
            return
        
        # Если открыта загадка - обрабатываем её ввод
        if self.show_riddle_ui and self.current_riddle:
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                close, answer = self.riddle_ui.handle_input(event, self.current_riddle)
                if close:
                    if answer:
                        self.current_riddle.check_answer(answer)
                    self.show_riddle_ui = False
                    self.current_riddle = None
            return
        
        # Если открыт диалог - обрабатываем его ввод
        if self.show_dialogue and self.current_dialogue:
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                if self.dialogue_ui.handle_input(event, self.current_dialogue):
                    self.show_dialogue = False
                    self.current_dialogue = None
            return
        
        # Если открыт диалог выхода - обрабатываем его
        if self.show_exit_dialog:
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        # Подтверждено - выход в меню
                        self.show_exit_dialog = False
                        self.show_main_menu = True
                        self.message_log.clear()
                    elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                        # Отменено
                        self.show_exit_dialog = False
            return
        
        for event in events:
            # Закрытие окна
            if event.type == pygame.QUIT:
                self.running = False
                
            # Нажатие клавиш
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Показываем диалог подтверждения выхода
                    self.show_exit_dialog = True
                    
                # Переключение полноэкранного режима (F11)
                if event.key == pygame.K_F11:
                    self._toggle_fullscreen()
                
                # Переключение отображения FPS (F3)
                if event.key == pygame.K_F3:
                    self.show_fps = not self.show_fps
                    
                # Взаимодействие (E) - предметы, загадки, записки
                if event.key == pygame.K_e:
                    self._handle_e_interaction()
                    
                # Атака (пробел или A)
                if event.key in [pygame.K_SPACE, pygame.K_a]:
                    if self.current_location != "attic":
                        self.combat.player_attack(self.player, self.current_level)
                    
                # Быстрое сохранение (F5)
                if event.key == pygame.K_F5:
                    self._quick_save()
                    
                # Быстрая загрузка (F9)
                if event.key == pygame.K_F9:
                    self._quick_load()
                    
                # Открыть инвентарь (I)
                if event.key == pygame.K_i:
                    self.show_inventory_ui = not self.show_inventory_ui
                    if not self.show_inventory_ui:
                        self.inventory_ui.selected_slot = None
                    
                # Взаимодействие с хранилищем (T)
                if event.key == pygame.K_t:
                    self._open_storage_ui()
                    
    def _update(self, dt: float) -> None:
        """
        Обновление игровой логики
        
        Args:
            dt: Delta time (время между кадрами в секундах)
        """
        # Обновляем таймер движения
        self.move_timer += dt
        
        # Получаем ввод движения
        dx, dy = self.input_manager.get_movement_input()
        
        # Проверяем, зажат ли Shift (бег)
        keys = pygame.key.get_pressed()
        is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        # Определяем задержку движения
        current_delay = self.run_move_delay if is_running else self.move_delay
        
        # Двигаем игрока если прошло достаточно времени
        if (dx != 0 or dy != 0) and self.move_timer >= current_delay:
            # Проверяем выносливость для бега
            can_run = True
            if is_running:
                if self.player.stats.endurance >= self.run_endurance_cost:
                    self.player.stats.endurance -= self.run_endurance_cost
                else:
                    can_run = False
                    is_running = False  # Не можем бежать - идём обычным шагом
            
            # Двигаем игрока
            if self.current_location == "attic":
                moved = self.player.move(dx, dy, self.attic)
            else:
                moved = self.player.move(dx, dy, self.current_level)
            
            # Разрешаем переход только если игрок сдвинулся
            if moved:
                self.can_transition = True
                self.move_timer = 0.0  # Сбрасываем таймер после движения
                
                # Звук шага
                self.sound_manager.play_sound("step")
                
                # Сохраняем был ли последний шаг бегом (для обнаружения ловушек)
                self._last_move_was_running = is_running
                
                # Проверяем ловушки (только в подземелье)
                if self.current_location != "attic":
                    self._check_traps()
            
        # Проверяем переходы между локациями
        self._check_location_transition()
            
        # Обновляем игрока (передаём информацию о движении для анимации)
        is_moving = (dx != 0 or dy != 0) and self.move_timer >= current_delay
        self.player.update(dt, is_moving)
        
        # Обновляем боевую систему
        self.combat.update(dt)
        
        # Обновляем систему частиц
        self.particle_system.update(dt)
        
        # Обновляем лог сообщений
        self.message_log.update(dt)
        
        # Проверяем сбор рун и предметов (только в подземелье)
        if self.current_location != "attic":
            self._check_rune_collection()
            self._check_dropped_items()
            self._show_interaction_hints()
            
            # Обновляем врагов
            attacking_enemies = self.current_level.enemy_spawner.update_all(
                dt, 
                self.player.x, 
                self.player.y, 
                self.current_level
            )
            
            # Обрабатываем атаки врагов
            for enemy in attacking_enemies:
                self.combat.enemy_attack(enemy, self.player)
            
            # Проверяем смерть игрока
            if self.player.stats.health <= 0 and not self.player_dead:
                self._handle_player_death()
            
            # Обновляем туман войны
            self.current_level.update_fog_of_war(self.player.x, self.player.y)
        
        # Обновляем таймер смерти
        if self.player_dead:
            self.death_timer += dt
            if self.death_timer >= 3.0:  # 3 секунды показываем экран смерти
                self._respawn_player()
        
        # Проверяем сюжетные триггеры
        self._check_story_triggers()
        
        # Обновляем камеру (центрируем на игроке)
        self._update_camera()
        
    def _update_camera(self) -> None:
        """Обновление позиции камеры"""
        # Центрируем камеру на игроке
        player_screen_x = self.player.x * self.player.size
        player_screen_y = self.player.y * self.player.size
        
        self.camera_x = player_screen_x - self.width // 2
        self.camera_y = player_screen_y - self.height // 2
        
        # Ограничиваем камеру границами уровня
        if self.current_location == "attic":
            max_camera_x = self.attic.width * self.attic.tile_size - self.width
            max_camera_y = self.attic.height * self.attic.tile_size - self.height
        else:
            max_camera_x = self.current_level.width * self.current_level.tile_size - self.width
            max_camera_y = self.current_level.height * self.current_level.tile_size - self.height
        
        self.camera_x = max(0, min(self.camera_x, max_camera_x))
        self.camera_y = max(0, min(self.camera_y, max_camera_y))
        
    def _check_location_transition(self) -> None:
        """Проверка перехода между локациями"""
        if not self.can_transition:
            return
            
        player_pos = (self.player.x, self.player.y)
        
        # На чердаке
        if self.current_location == "attic":
            # Проверка входа в подземелье
            if self.attic.entrance_pos and player_pos == self.attic.entrance_pos:
                self.message_log.info("Спускаетесь в подземелье...")
                self._go_to_floor(1)
                self.can_transition = False
                
        # В подземелье
        else:
            # Проверка выхода (вниз)
            if self.current_level.exit_pos and player_pos == self.current_level.exit_pos:
                self.message_log.info(f"Спускаетесь на этаж {self.current_floor + 1}...")
                self._go_to_floor(self.current_floor + 1)
                self.can_transition = False
                
            # Проверка входа (вверх)
            elif self.current_level.entrance_pos and player_pos == self.current_level.entrance_pos:
                if self.current_floor > 1:
                    self.message_log.info(f"Поднимаетесь на этаж {self.current_floor - 1}...")
                    self._go_to_floor(self.current_floor - 1)
                else:
                    # Возврат на чердак
                    self.message_log.success("Возвращаетесь на чердак")
                    self._go_to_attic()
                self.can_transition = False
                
    def _go_to_floor(self, floor: int) -> None:
        """
        Переход на другой этаж
        
        Args:
            floor: Номер этажа
        """
        if floor < 1 or floor > 20:
            print(f"⚠️  Этаж {floor} недоступен")
            return
            
        old_location = self.current_location
        going_down = old_location == "attic" or (isinstance(old_location, int) and floor > old_location)
        
        print(f"\n🚪 Переход: {old_location} → этаж {floor}")
        
        # Обновляем локацию
        self.current_location = floor
        self.current_floor = floor
        
        # Генерируем новый уровень (загадки восстанавливаются автоматически в level_generator)
        self.current_level = self.level_generator.generate(floor)
        
        # Меняем музыку в зависимости от биома
        biome = self._get_biome_for_floor(floor)
        self.sound_manager.start_music(biome)
        
        # Телепортируем игрока
        if going_down:  # Спускаемся вниз
            # Появляемся на входе (зелёный круг) нового этажа
            if self.current_level.entrance_pos:
                self.player.x, self.player.y = self.current_level.entrance_pos
                print(f"↓ Спустились на этаж {floor} (появились у входа)")
        else:  # Поднимаемся вверх
            # Появляемся на выходе (красный круг) нового этажа
            if self.current_level.exit_pos:
                self.player.x, self.player.y = self.current_level.exit_pos
                print(f"↑ Поднялись на этаж {floor} (появились у выхода)")
                
    def _go_to_attic(self) -> None:
        """Возврат на чердак"""
        print(f"\n🏠 Возврат на чердак")
        
        self.current_location = "attic"
        self.current_floor = 0
        self.current_level = None
        
        # Меняем музыку на тему чердака
        self.sound_manager.start_music("attic")
        
        # Восстанавливаем выносливость при возвращении на базу
        old_endurance = self.player.stats.endurance
        self.player.stats.endurance = self.player.stats.max_endurance
        restored = self.player.stats.endurance - old_endurance
        
        if restored > 0:
            print(f"💪 Выносливость восстановлена: +{restored}")
            self.message_log.info(f"Выносливость восстановлена: +{restored}")
        
        # Телепортируем игрока на чердак (у люка)
        if self.attic.entrance_pos:
            self.player.x, self.player.y = self.attic.entrance_pos
            print(f"↑ Вернулись на чердак")
                
    def _test_stabilize_floor(self) -> None:
        """Тестовая функция стабилизации этажа (SPACE) - для отладки"""
        print("\n⚠️  [ТЕСТ] Принудительная стабилизация этажа")
        self._stabilize_current_floor()
            
    def _check_rune_collection(self) -> None:
        """Проверка сбора рун"""
        collected_runes = self.current_level.rune_manager.check_collection(
            self.player.x, 
            self.player.y
        )
        
        # Если собрали руну устойчивости - автоматически стабилизируем этаж
        for rune in collected_runes:
            from ..items.rune import RuneType
            if rune.rune_type == RuneType.STABILITY:
                # Эффект частиц
                effect_x = self.player.x * 32 + 16
                effect_y = self.player.y * 32 + 16
                self.particle_system.emit(effect_x, effect_y, 40, "sparkle")
                
                # Сообщение
                self.message_log.success("Собрали Руну устойчивости!")
                
                print("\n🔮 Руна устойчивости активирована!")
                self._stabilize_current_floor()
                
    def _stabilize_current_floor(self) -> None:
        """Стабилизировать текущий этаж"""
        floor_state_manager = self.level_generator.floor_state_manager
        
        # Проверяем, не стабилизирован ли уже
        if floor_state_manager.is_floor_stabilized(self.current_floor):
            return
            
        # Стабилизируем
        floor_state_manager.stabilize_floor(
            self.current_floor,
            self.current_level.tiles,
            self.current_level.entrance_pos,
            self.current_level.exit_pos,
            self.current_level.fog_of_war.visibility
        )
        
        # Создаём загадку на стене после стабилизации
        self._spawn_riddle_after_stabilization()
        
        # Показываем прогресс
        stabilized = floor_state_manager.get_stabilized_count()
        self.message_log.success(f"Этаж {self.current_floor} стабилизирован! ({stabilized}/20)")
        print(f"📊 Прогресс стабилизации: {stabilized}/20 этажей")
        
        if floor_state_manager.all_floors_stabilized():
            self.message_log.success("ВСЕ ЭТАЖИ СТАБИЛИЗИРОВАНЫ!")
            print("🎉 ВСЕ ЭТАЖИ СТАБИЛИЗИРОВАНЫ! Можно искать главный тайник!")
            
    def _spawn_riddle_after_stabilization(self) -> None:
        """Создать загадку после стабилизации этажа"""
        floor_state_manager = self.level_generator.floor_state_manager
        floor_state = floor_state_manager.floors.get(self.current_floor)
        
        # Проверяем, не создана ли уже загадка
        if floor_state and floor_state.riddle_spawned:
            print("⚠️  Загадка уже была создана на этом этаже")
            return
            
        # Ищем стену рядом с выходом для размещения загадки
        if self.current_level.exit_pos:
            exit_x, exit_y = self.current_level.exit_pos
            print(f"🔍 Ищу стену рядом с выходом ({exit_x}, {exit_y})")
            
            # Ищем ближайшую стену (расширенный поиск)
            found = False
            for radius in range(1, 10):  # Ищем в радиусе до 10 клеток
                if found:
                    break
                    
                for dx in range(-radius, radius + 1):
                    if found:
                        break
                    for dy in range(-radius, radius + 1):
                        if abs(dx) != radius and abs(dy) != radius:
                            continue  # Проверяем только периметр
                            
                        wall_x = exit_x + dx
                        wall_y = exit_y + dy
                        
                        if self.current_level.get_tile(wall_x, wall_y) == self.current_level.TILE_WALL:
                            # Создаём загадку на стене
                            seed = self.level_generator.generate_seed(self.current_floor) + 1000
                            self.current_level.riddle_manager.spawn_riddle(wall_x, wall_y, seed)
                            
                            # Отмечаем что загадка создана
                            if floor_state:
                                floor_state.riddle_spawned = True
                                
                            print(f"📜 На стене ({wall_x}, {wall_y}) появилась загадка!")
                            found = True
                            break
                            
            if not found:
                print("⚠️  Не нашёл стену рядом с выходом!")
                    
    def _interact_with_riddle(self) -> bool:
        """
        Взаимодействие с загадкой
        
        Returns:
            True если загадка найдена и открыта
        """
        # Проверяем соседние клетки
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            check_x = self.player.x + dx
            check_y = self.player.y + dy
            
            riddle = self.current_level.riddle_manager.get_riddle_at(check_x, check_y)
            
            if riddle:
                # Открываем GUI загадки
                self.current_riddle = riddle
                self.show_riddle_ui = True
                return True
        
        return False
        
    def _quick_save(self) -> None:
        """Быстрое сохранение (F5)"""
        # Можно сохраняться только на чердаке
        if self.current_location != "attic":
            print("❌ Сохранение доступно только на чердаке!")
            self.message_log.warning("Сохранение только на чердаке!")
            return
        
        if not self.current_profile:
            print("❌ Нет активного профиля!")
            return
            
        print(f"\n💾 Сохранение профиля {self.current_profile}...")
        
        # Собираем данные для сохранения
        game_data = {
            "player": self.serializer.serialize_player(self.player),
            "current_location": self.current_location,
            "current_floor": self.current_floor,
            "floor_states": self.serializer.serialize_floor_states(
                self.level_generator.floor_state_manager
            ),
            "attic_storage": self._serialize_attic_storage(),
            "story_flags": self.story_manager.story_flags
        }
        
        # Сохраняем в папку профиля
        profile_dir = f"saves/profiles/{self.current_profile}"
        os.makedirs(profile_dir, exist_ok=True)
        
        save_file = os.path.join(profile_dir, "save.json")
        
        try:
            import json
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, ensure_ascii=False, indent=2)
            
            # Обновляем метаданные профиля
            self._update_profile_metadata()
            
            print(f"✅ Игра сохранена: {save_file}")
            self.message_log.success("Игра сохранена!")
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            self.message_log.error("Ошибка сохранения!")
            
    def _quick_load(self) -> None:
        """Быстрая загрузка (F9)"""
        if not self.current_profile:
            print("❌ Нет активного профиля!")
            return
        
        profile_dir = f"saves/profiles/{self.current_profile}"
        save_file = os.path.join(profile_dir, "save.json")
        self._quick_load_from_file(save_file)
        
    def _quick_load_from_file(self, save_file: str) -> None:
        """
        Загрузка из файла
        
        Args:
            save_file: Путь к файлу сохранения
        """
        print(f"\n📂 Загрузка из {save_file}...")
        
        if not os.path.exists(save_file):
            print("❌ Сохранение не найдено!")
            return
        
        # Загружаем данные
        import json
        with open(save_file, 'r', encoding='utf-8') as f:
            game_data = json.load(f)
        
        if game_data is None:
            print("❌ Ошибка загрузки!")
            return
            
        # Восстанавливаем игрока
        self.serializer.deserialize_player(self.player, game_data["player"])
        
        # Восстанавливаем локацию
        self.current_location = game_data["current_location"]
        self.current_floor = game_data["current_floor"]
        
        # Восстанавливаем состояния этажей
        self.serializer.deserialize_floor_states(
            self.level_generator.floor_state_manager,
            game_data["floor_states"]
        )
        
        # Восстанавливаем хранилище на чердаке
        if "attic_storage" in game_data:
            self._deserialize_attic_storage(game_data["attic_storage"])
            print("   📦 Хранилище восстановлено")
        
        # Восстанавливаем флаги сюжета
        if "story_flags" in game_data:
            self.story_manager.story_flags = game_data["story_flags"]
            print("   📖 Флаги сюжета восстановлены")
        
        # Перезагружаем текущую локацию
        if self.current_location == "attic":
            self.current_level = None
        else:
            self.current_level = self.level_generator.generate(self.current_floor)
            
        print("✅ Игра загружена!")
        print(f"   Локация: {self.current_location}")
        print(f"   Здоровье: {self.player.stats.health}/{self.player.stats.max_health}")
        print(f"   Шагов: {self.player.steps}")
        
    def _show_inventory(self) -> None:
        """Показать инвентарь (I)"""
        self.player.inventory.print_inventory()
    
    def _handle_e_interaction(self) -> None:
        """Обработка взаимодействия по клавише E (приоритет: интерактивные объекты -> контейнеры -> предметы -> загадки -> записки)"""
        if self.current_location == "attic":
            return
        
        # 1. Проверяем интерактивные объекты (доски и кости) - высший приоритет
        if self._check_interactive_object():
            return
        
        # 2. Проверяем контейнеры
        if self._check_container_opening():
            return
        
        # 2. Проверяем предметы
        if self.current_level.item_spawner.has_item_at(self.player.x, self.player.y):
            self._check_item_pickup()
            return
        
        # 3. Проверяем загадки
        if self._interact_with_riddle():
            return
        
        # 4. Проверяем записки
        self._check_note_reading()
        
    def _check_interactive_object(self) -> bool:
        """
        Проверка взаимодействия с интерактивными объектами (доски, кости)
        
        Returns:
            True если было взаимодействие
        """
        # Ищем объект на позиции игрока
        for obj in self.current_level.interactive_objects:
            if obj.x == self.player.x and obj.y == self.player.y:
                # Взаимодействуем с объектом
                result = obj.interact()
                
                # Показываем записку
                self.current_note = type('Note', (), {
                    'title': result['note_title'],
                    'text': result['note_text']
                })()
                self.show_note = True
                
                # Если это кости - выдаём лут
                if result['type'] == 'skeleton' and result['loot'] and not result['already_used']:
                    self.sound_manager.play_sound("pickup")
                    self.message_log.success(f"☠️ Обыскали останки путешественника")
                    
                    for loot_item in result['loot']:
                        self.message_log.item(f"  + {loot_item}")
                        print(f"  + {loot_item}")
                    
                    # Эффект частиц
                    self.particle_system.emit(
                        self.player.x * 32 + 16,
                        self.player.y * 32 + 16,
                        count=15,
                        effect_type="sparkle"
                    )
                elif result['type'] == 'notice_board':
                    self.sound_manager.play_sound("page_turn")
                    self.message_log.info(f"📋 Прочитали записку на доске")
                
                return True
        
        return False
    
    def _check_container_opening(self) -> bool:
        """
        Проверка открытия контейнера
        
        Returns:
            True если контейнер был открыт
        """
        # Ищем контейнер на позиции игрока
        for container in self.current_level.containers:
            if container.x == self.player.x and container.y == self.player.y:
                # Проверяем видим ли контейнер (тайники)
                if not container.is_visible():
                    continue
                
                # Проверяем не открыт ли уже
                if container.opened:
                    self.message_log.info(f"{container.get_name()} уже пуст")
                    return True
                
                # Открываем контейнер
                items = container.open()
                
                if items:
                    # Звук открытия сундука
                    self.sound_manager.play_sound("chest_open")
                    
                    self.message_log.success(f"📦 Открыли {container.get_name()}!")
                    print(f"\n📦 Открыли {container.get_name()}!")
                    
                    # Добавляем предметы в инвентарь
                    for item in items:
                        if self.player.inventory.add_item(item):
                            from ..items.item import ItemRarity
                            rarity_names = {
                                ItemRarity.COMMON: "",
                                ItemRarity.UNCOMMON: "Необычный ",
                                ItemRarity.RARE: "Редкий ",
                                ItemRarity.EPIC: "Эпический ",
                                ItemRarity.LEGENDARY: "Легендарный "
                            }
                            rarity_prefix = rarity_names.get(item.rarity, "")
                            self.message_log.item(f"  + {rarity_prefix}{item.name}")
                            print(f"  + {rarity_prefix}{item.name}")
                        else:
                            self.message_log.warning("❌ Инвентарь полон!")
                            print("❌ Инвентарь полон!")
                            break
                    
                    # Эффект частиц
                    self.particle_system.emit(
                        self.player.x * 32 + 16,
                        self.player.y * 32 + 16,
                        count=20,
                        effect_type="sparkle"
                    )
                else:
                    self.message_log.info(f"{container.get_name()} пуст")
                
                return True
        
        return False
    
    def _check_item_pickup(self) -> None:
        """Подбор предмета (вызывается из _handle_e_interaction)"""
        # Пытаемся подобрать предмет
        item = self.current_level.item_spawner.check_pickup(
            self.player.x,
            self.player.y,
            self.player,
            manual=True  # Подбор по клавише
        )
        
        if item:
            # Звук подбора
            self.sound_manager.play_sound("pickup")
            
            # Эффект частиц
            effect_x = self.player.x * 32 + 16
            effect_y = self.player.y * 32 + 16
            self.particle_system.emit(effect_x, effect_y, 15, "sparkle")
            
            # Сообщение
            from ..items.item import ItemRarity
            rarity_names = {
                ItemRarity.COMMON: "",
                ItemRarity.UNCOMMON: "Необычный ",
                ItemRarity.RARE: "Редкий ",
                ItemRarity.EPIC: "Эпический ",
                ItemRarity.LEGENDARY: "Легендарный "
            }
            rarity_prefix = rarity_names.get(item.rarity, "")
            self.message_log.item(f"Подобрали: {rarity_prefix}{item.name}")
    
    def _check_note_reading(self) -> None:
        """Проверка чтения записок (вызывается из _handle_e_interaction)"""
        # Ищем записку на позиции игрока
        for note in self.current_level.notes:
            if note.x == self.player.x and note.y == self.player.y:
                # Показываем содержимое записки в консоли
                print(f"\n📜 {note.title}")
                print(f"   {note.content}")
                print()
                
                # Показываем в логе сообщений
                self.message_log.info(f"📜 {note.title}")
                self.message_log.info(f"   {note.content}")
                
                # Помечаем как прочитанную
                if not note.read:
                    note.read = True
                
                return
        
        # Если записки нет - проверяем соседние клетки
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            check_x = self.player.x + dx
            check_y = self.player.y + dy
            
            for note in self.current_level.notes:
                if note.x == check_x and note.y == check_y:
                    self.message_log.info("Подойдите ближе к записке и нажмите E")
                    return
    
    def _check_dropped_items(self) -> None:
        """Проверка выброшенных предметов и размещение их на карте"""
        if hasattr(self.player, '_dropped_items') and self.player._dropped_items:
            for item, quantity in self.player._dropped_items:
                # Размещаем предмет на позиции игрока
                self.current_level.item_spawner.spawn_dropped_item(
                    item,
                    self.player.x,
                    self.player.y,
                    quantity
                )
                
                # Сообщение в лог
                self.message_log.info(f"Выброшено: {item.name} x{quantity}")
            
            # Очищаем список выброшенных предметов
            self.player._dropped_items.clear()
    
    def _check_traps(self) -> None:
        """Проверка ловушек на позиции игрока"""
        if not self.current_level:
            return
        
        # Сначала пытаемся обнаружить ловушки и тайники в радиусе 2 клеток
        self._try_detect_nearby_traps()
        self._try_detect_nearby_containers()
        
        # Проверяем все ловушки на уровне
        for trap in self.current_level.traps:
            if trap.x == self.player.x and trap.y == self.player.y:
                # Активируем ловушку
                effect = trap.trigger()
                
                if effect["triggered"]:
                    # Показываем сообщение
                    self.message_log.warning(f"⚠️ {effect['message']}")
                    print(f"⚠️ {effect['message']}")
                    
                    # Наносим урон игроку
                    damage = effect.get("damage", 0)
                    if damage > 0:
                        # Звук урона
                        self.sound_manager.play_sound("damage")
                        
                        self.player.take_damage(damage)
                        self.message_log.combat(f"💥 Получено {damage} урона!")
                        print(f"💥 Получено {damage} урона! HP: {self.player.stats.health}/{self.player.stats.max_health}")
                    
                    # Создаём эффект частиц
                    from ..world.traps import TrapType
                    if trap.trap_type == TrapType.FIRE:
                        effect_type = "explosion"
                    elif trap.trap_type == TrapType.ICE:
                        effect_type = "sparkle"
                    elif trap.trap_type == TrapType.POISON:
                        effect_type = "smoke"
                    elif trap.trap_type == TrapType.EXPLOSIVE:
                        effect_type = "explosion"
                    else:
                        effect_type = "sparkle"
                    
                    # Добавляем частицы в позиции ловушки
                    self.particle_system.emit(
                        self.player.x * 32 + 16,
                        self.player.y * 32 + 16,
                        count=15,
                        effect_type=effect_type
                    )
                    
                    break  # Только одна ловушка за раз
    
    def _try_detect_nearby_traps(self) -> None:
        """Попытка обнаружить ловушки рядом с игроком"""
        if not self.current_level:
            return
        
        # Базовый шанс обнаружения
        base_chance = 0.20  # 20%
        
        # Бонус за медленное движение (не бег)
        # Проверяем был ли последний шаг бегом
        is_running = hasattr(self, '_last_move_was_running') and self._last_move_was_running
        if not is_running:
            base_chance += 0.30  # +30% при медленном движении
        
        # Радиус обнаружения (2 клетки)
        detection_radius = 2
        
        # Проверяем все ловушки в радиусе
        for trap in self.current_level.traps:
            # Вычисляем расстояние
            dx = abs(trap.x - self.player.x)
            dy = abs(trap.y - self.player.y)
            distance = max(dx, dy)  # Чебышёвское расстояние
            
            if distance <= detection_radius:
                # Шанс обнаружения уменьшается с расстоянием
                distance_penalty = distance * 0.15
                detection_chance = max(0.05, base_chance - distance_penalty)
                
                # Пытаемся обнаружить
                if trap.try_detect(detection_chance):
                    # Звук обнаружения
                    self.sound_manager.play_sound("discover")
                    
                    self.message_log.info(f"🔍 Вы заметили ловушку!")
                    print(f"🔍 Обнаружена ловушка на ({trap.x}, {trap.y})")
    
    def _try_detect_nearby_containers(self) -> None:
        """Попытка обнаружить тайники рядом с игроком"""
        if not self.current_level:
            return
        
        # Базовый шанс обнаружения (такой же как у ловушек)
        base_chance = 0.20  # 20%
        
        # Бонус за медленное движение
        is_running = hasattr(self, '_last_move_was_running') and self._last_move_was_running
        if not is_running:
            base_chance += 0.30  # +30% при медленном движении
        
        # Радиус обнаружения
        detection_radius = 2
        
        # Проверяем все контейнеры в радиусе
        for container in self.current_level.containers:
            # Вычисляем расстояние
            dx = abs(container.x - self.player.x)
            dy = abs(container.y - self.player.y)
            distance = max(dx, dy)
            
            if distance <= detection_radius:
                # Шанс обнаружения уменьшается с расстоянием
                distance_penalty = distance * 0.15
                detection_chance = max(0.05, base_chance - distance_penalty)
                
                # Пытаемся обнаружить тайник
                if container.try_discover(detection_chance):
                    # Звук обнаружения
                    self.sound_manager.play_sound("discover")
                    
                    self.message_log.info(f"🔍 Вы нашли тайник!")
                    print(f"🔍 Обнаружен тайник на ({container.x}, {container.y})")
    
    def _show_interaction_hints(self) -> None:
        """Показать подсказки о предметах и записках под игроком"""
        # Создаём ключ текущей позиции для отслеживания
        current_pos = (self.player.x, self.player.y)
        
        # Инициализируем атрибут если его нет
        if not hasattr(self, '_last_hint_pos'):
            self._last_hint_pos = None
        
        # Если позиция не изменилась, не показываем подсказку снова
        if self._last_hint_pos == current_pos:
            return
        
        # Обновляем последнюю позицию
        self._last_hint_pos = current_pos
        
        # Проверяем контейнеры на позиции игрока (высший приоритет)
        for container in self.current_level.containers:
            if container.x == self.player.x and container.y == self.player.y:
                # Проверяем видим ли контейнер
                if not container.is_visible():
                    continue
                
                # Показываем подсказку
                if container.opened:
                    self.message_log.info(f"{container.get_name()} [пуст]")
                else:
                    self.message_log.info(f"{container.get_name()} (нажмите E)")
                return
        
        # Проверяем предметы на позиции игрока
        for item_spawn in self.current_level.item_spawner.spawned_items:
            if item_spawn.picked_up:
                continue
            
            if item_spawn.x == self.player.x and item_spawn.y == self.player.y:
                # Показываем название предмета
                from ..items.item import ItemRarity
                rarity_names = {
                    ItemRarity.COMMON: "",
                    ItemRarity.UNCOMMON: "Необычный ",
                    ItemRarity.RARE: "Редкий ",
                    ItemRarity.EPIC: "Эпический ",
                    ItemRarity.LEGENDARY: "Легендарный "
                }
                rarity_prefix = rarity_names.get(item_spawn.item.rarity, "")
                self.message_log.info(f"Предмет: {rarity_prefix}{item_spawn.item.name} (нажмите E)")
                return
        
        # Проверяем записки на позиции игрока
        for note in self.current_level.notes:
            if note.x == self.player.x and note.y == self.player.y:
                # Показываем заголовок записки
                status = " [прочитана]" if note.read else ""
                self.message_log.info(f"Записка: {note.title}{status} (нажмите E)")
                return
        
    def _open_storage_ui(self) -> None:
        """Открыть GUI хранилища"""
        # Проверяем что мы на чердаке
        if self.current_location != "attic":
            print("❌ Хранилище доступно только на чердаке!")
            return
            
        # Проверяем что мы рядом с сундуком
        if self.attic.storage_pos:
            storage_x, storage_y = self.attic.storage_pos
            distance = abs(self.player.x - storage_x) + abs(self.player.y - storage_y)
            
            if distance > 1:
                print("❌ Подойдите ближе к сундуку!")
                return
        
        # Открываем GUI
        self.show_storage_ui = True
    
    def _interact_with_storage(self) -> None:
        """Взаимодействие с хранилищем (T)"""
        # Проверяем что мы на чердаке
        if self.current_location != "attic":
            print("❌ Хранилище доступно только на чердаке!")
            return
            
        # Проверяем что мы рядом с сундуком
        if self.attic.storage_pos:
            storage_x, storage_y = self.attic.storage_pos
            distance = abs(self.player.x - storage_x) + abs(self.player.y - storage_y)
            
            if distance > 1:
                print("❌ Подойдите ближе к сундуку!")
                return
        
        # Цикл взаимодействия с хранилищем
        while True:
            # Показываем меню хранилища
            print("\n" + "="*60)
            print("📦 ХРАНИЛИЩЕ (СУНДУК)")
            print("="*60)
            self.attic.storage.print_storage()
            print("\n🎒 ВАШ ИНВЕНТАРЬ:")
            self.player.inventory.print_inventory()
            print("\n" + "="*60)
            print("Команды:")
            print("  1 - Положить предмет в сундук")
            print("  2 - Взять предмет из сундука")
            print("  0 - Выйти")
            print("="*60)
            
            try:
                choice = input("\nВыберите действие (0-2): ").strip()
                
                if choice == "0":
                    print("✅ Закрыто")
                    break
                elif choice == "1":
                    # Положить в сундук
                    slot = input("Введите номер слота инвентаря (или Enter для отмены): ").strip()
                    if slot:
                        try:
                            self._store_item(int(slot))
                        except ValueError:
                            print("❌ Неверный номер слота!")
                elif choice == "2":
                    # Взять из сундука
                    slot = input("Введите номер слота хранилища (или Enter для отмены): ").strip()
                    if slot:
                        try:
                            self._take_item(int(slot))
                        except ValueError:
                            print("❌ Неверный номер слота!")
                else:
                    print("❌ Неверный выбор! Введите 0, 1 или 2")
                    
            except KeyboardInterrupt:
                print("\n✅ Закрыто")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")
            
    def _store_item(self, inventory_slot: int) -> None:
        """
        Положить предмет в хранилище
        
        Args:
            inventory_slot: Номер слота в инвентаре
        """
        if inventory_slot < 0 or inventory_slot >= self.player.inventory.max_slots:
            print("❌ Неверный номер слота!")
            return
            
        slot = self.player.inventory.slots[inventory_slot]
        if slot.is_empty():
            print("❌ Слот пуст!")
            return
            
        item = slot.item
        quantity = slot.quantity
        
        # Добавляем в хранилище
        if self.attic.storage.add_item(item, quantity):
            # Удаляем из инвентаря
            self.player.inventory.remove_item(item.id, quantity)
            
    def _take_item(self, storage_slot: int) -> None:
        """
        Взять предмет из хранилища
        
        Args:
            storage_slot: Номер слота в хранилище
        """
        item, quantity = self.attic.storage.remove_item(storage_slot, 1)
        
        if item:
            # Добавляем в инвентарь
            self.player.inventory.add_item(item, quantity)
        
    def _render(self) -> None:
        """Отрисовка кадра"""
        # Очистка экрана (черный фон)
        self.screen.fill((0, 0, 0))
        
        # Если показано главное меню - рисуем только его
        if self.show_main_menu:
            self.main_menu.render(self.screen)
            # Если поверх меню открыты настройки
            if self.show_settings_ui:
                self.settings_ui.render(self.screen)
            return
        
        # Отрисовываем текущую локацию
        if self.current_location == "attic":
            self.attic.render(self.screen, self.camera_x, self.camera_y)
        else:
            self.current_level.render(self.screen, self.camera_x, self.camera_y)
        
        # Отрисовываем игрока
        self.player.render(self.screen, self.camera_x, self.camera_y)
        
        # HUD (информация на экране)
        self._render_hud()
        
        # Лог сообщений
        self.message_log.render(self.screen)
        
        # Эффекты боя (числа урона)
        self.combat.render_damage_numbers(self.screen, self.camera_x, self.camera_y)
        
        # Система частиц
        self.particle_system.render(self.screen, self.camera_x, self.camera_y)
        
        # GUI (поверх всего)
        if self.player_dead:
            self._render_death_screen()
        elif self.show_note and self.current_note:
            self._render_note()
        elif self.show_exit_dialog:
            self._render_exit_dialog()
        elif self.show_dialogue and self.current_dialogue:
            self.dialogue_ui.render(self.screen, self.current_dialogue)
        elif self.show_inventory_ui:
            self.inventory_ui.render_inventory(self.screen, self.player.inventory)
        elif self.show_storage_ui:
            self.storage_ui.render(self.screen, self.player.inventory, self.attic.storage)
        elif self.show_riddle_ui and self.current_riddle:
            self.riddle_ui.render(self.screen, self.current_riddle)
        
        # FPS счётчик (поверх всего)
        self._render_fps()
        
        # Обновление экрана
        pygame.display.flip()
        
    def _render_hud(self) -> None:
        """Отрисовка HUD"""
        font = pygame.font.Font(None, 24)
        
        # Позиция игрока
        pos_text = font.render(
            f"Позиция: ({self.player.x}, {self.player.y})",
            True,
            (255, 255, 255)
        )
        self.screen.blit(pos_text, (10, 10))
        
        # Здоровье
        hp_text = font.render(
            f"HP: {self.player.stats.health}/{self.player.stats.max_health}",
            True,
            (255, 0, 0)
        )
        self.screen.blit(hp_text, (10, 35))
        
        # Выносливость (с индикацией бега)
        keys = pygame.key.get_pressed()
        is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        stamina_color = (255, 165, 0) if is_running else (0, 255, 255)  # Оранжевый при беге
        stamina_prefix = "🏃 " if is_running else ""
        
        stamina_text = font.render(
            f"{stamina_prefix}Выносливость: {self.player.stats.endurance}/{self.player.stats.max_endurance}",
            True,
            stamina_color
        )
        self.screen.blit(stamina_text, (10, 60))
        
        # Шаги
        steps_text = font.render(
            f"Шагов: {self.player.steps}",
            True,
            (200, 200, 200)
        )
        self.screen.blit(steps_text, (10, 85))
        
        # Локация
        if self.current_location == "attic":
            location_text = "Чердак"
            biome_text = ""
        else:
            location_text = f"Этаж: {self.current_floor}"
            # Получаем название биома
            from src.world.biomes import BiomeManager
            biome = BiomeManager.get_biome_for_floor(self.current_floor)
            biome_text = biome.name
            
        floor_text = font.render(
            location_text,
            True,
            (255, 255, 255)
        )
        self.screen.blit(floor_text, (10, 110))
        
        # Название биома (если не на чердаке)
        if biome_text:
            biome_font = pygame.font.Font(None, 20)
            biome_render = biome_font.render(
                f"📍 {biome_text}",
                True,
                (150, 200, 255)  # Голубоватый цвет
            )
            self.screen.blit(biome_render, (10, 135))
        
        # Подсказка
        hint_font = pygame.font.Font(None, 20)
        hint_text = hint_font.render(
            "Красный круг = ВНИЗ (глубже), Зелёный круг = ВВЕРХ (назад)",
            True,
            (150, 150, 150)
        )
        self.screen.blit(hint_text, (10, self.height - 30))
        
        # Дополнительная подсказка
        hint2_text = hint_font.render(
            "Этаж 1 = поверхность, Этаж 20 = самое дно подземелья",
            True,
            (150, 150, 150)
        )
        self.screen.blit(hint2_text, (10, self.height - 50))
        
        # Подсказка для интерактивных объектов
        if self.current_location != "attic":
            for obj in self.current_level.interactive_objects:
                if obj.x == self.player.x and obj.y == self.player.y:
                    hint_text = hint_font.render(
                        obj.get_interaction_hint(),
                        True,
                        (255, 255, 100)  # Яркий жёлтый
                    )
                    self.screen.blit(hint_text, (10, self.height - 70))
                    break
        
        # Тестовая подсказка
        hint3_text = hint_font.render(
            "SHIFT = бег | SPACE/A = атака | E = подобрать/загадка/записка | I = инвентарь | T = сундук",
            True,
            (255, 255, 0)
        )
        self.screen.blit(hint3_text, (10, self.height - 70))
        
        # Подсказка сохранений
        hint4_text = hint_font.render(
            "F5 = сохранить (на чердаке) | F9 = загрузить | F11 = полный экран",
            True,
            (255, 255, 0)
        )
        self.screen.blit(hint4_text, (10, self.height - 90))
        
        # Подсказка предметов
        hint5_text = hint_font.render(
            "Предметы подбираются автоматически",
            True,
            (150, 150, 150)
        )
        self.screen.blit(hint5_text, (10, self.height - 110))
        
        # Прогресс стабилизации (только в подземелье)
        if self.current_location != "attic":
            stabilized = self.level_generator.floor_state_manager.get_stabilized_count()
            progress_text = font.render(
                f"Стабилизировано: {stabilized}/20",
                True,
                (0, 255, 255)
            )
            self.screen.blit(progress_text, (10, 135))
            
            # Статус текущего этажа
            is_stabilized = self.level_generator.floor_state_manager.is_floor_stabilized(self.current_floor)
            status_color = (0, 255, 0) if is_stabilized else (255, 100, 100)
            status_text = "СТАБИЛИЗИРОВАН" if is_stabilized else "НЕ СТАБИЛИЗИРОВАН"
            floor_status = font.render(
                f"Этаж {self.current_floor}: {status_text}",
                True,
                status_color
            )
            self.screen.blit(floor_status, (10, 160))
            
            # Количество врагов
            alive_enemies = self.current_level.enemy_spawner.get_alive_count()
            enemies_text = font.render(
                f"Врагов: {alive_enemies}",
                True,
                (255, 100, 100)
            )
            self.screen.blit(enemies_text, (10, 185))
        
    def _render_exit_dialog(self) -> None:
        """Отрисовка диалога выхода"""
        # Затемнение фона
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Окно диалога
        box_width = 700
        box_height = 300
        box_x = (self.width - box_width) // 2
        box_y = (self.height - box_height) // 2
        
        pygame.draw.rect(self.screen, (40, 40, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, (255, 200, 100), (box_x, box_y, box_width, box_height), 3)
        
        # Текст
        title_font = pygame.font.Font(None, 48)
        text_font = pygame.font.Font(None, 32)
        hint_font = pygame.font.Font(None, 28)
        
        title = title_font.render("Выход в меню?", True, (255, 200, 100))
        title_rect = title.get_rect(center=(self.width // 2, box_y + 70))
        self.screen.blit(title, title_rect)
        
        warning = text_font.render("Несохранённый прогресс будет утерян!", True, (255, 100, 100))
        warning_rect = warning.get_rect(center=(self.width // 2, box_y + 140))
        self.screen.blit(warning, warning_rect)
        
        hint = hint_font.render("Y - Да, выйти | N/ESC - Нет, продолжить", True, (200, 200, 200))
        hint_rect = hint.get_rect(center=(self.width // 2, box_y + 220))
        self.screen.blit(hint, hint_rect)
    
    def _render_note(self) -> None:
        """Отрисовка записки НИИЧАВО"""
        # Затемнение фона
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Размеры окна записки
        box_width = min(700, self.width - 100)
        box_height = min(500, self.height - 100)
        box_x = (self.width - box_width) // 2
        box_y = (self.height - box_height) // 2
        
        # Фон записки (старая бумага)
        pygame.draw.rect(self.screen, (240, 230, 200), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, (150, 120, 80), (box_x, box_y, box_width, box_height), 3)
        
        # Заголовок
        title_font = pygame.font.Font(None, 42)
        title = title_font.render(f"📜 {self.current_note.title}", True, (80, 50, 20))
        title_rect = title.get_rect(center=(self.width // 2, box_y + 50))
        self.screen.blit(title, title_rect)
        
        # Разделитель
        pygame.draw.line(
            self.screen,
            (150, 120, 80),
            (box_x + 50, box_y + 85),
            (box_x + box_width - 50, box_y + 85),
            2
        )
        
        # Текст записки (многострочный)
        text_font = pygame.font.Font(None, 28)
        lines = self.current_note.text.split('\n')
        y_offset = box_y + 120
        
        for line in lines:
            text = text_font.render(line, True, (60, 40, 10))
            text_rect = text.get_rect(center=(self.width // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 35
        
        # Подсказка
        hint_font = pygame.font.Font(None, 24)
        hint = hint_font.render("Нажмите ПРОБЕЛ, ENTER или ESC чтобы закрыть", True, (120, 100, 60))
        hint_rect = hint.get_rect(center=(self.width // 2, box_y + box_height - 30))
        self.screen.blit(hint, hint_rect)
    
    def _render_death_screen(self) -> None:
        """Отрисовка экрана смерти"""
        # Полупрозрачный красный оверлей
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill((100, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Текст "ВЫ ПОГИБЛИ"
        death_font = pygame.font.Font(None, 72)
        death_text = death_font.render("💀 ВЫ ПОГИБЛИ 💀", True, (255, 255, 255))
        death_rect = death_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(death_text, death_rect)
        
        # Таймер возрождения
        timer_font = pygame.font.Font(None, 36)
        remaining = max(0, 3.0 - self.death_timer)
        timer_text = timer_font.render(
            f"Возрождение через {remaining:.1f} сек...",
            True,
            (255, 255, 255)
        )
        timer_rect = timer_text.get_rect(center=(self.width // 2, self.height // 2 + 20))
        self.screen.blit(timer_text, timer_rect)
        
        # Подсказка
        hint_font = pygame.font.Font(None, 24)
        hint_text = hint_font.render(
            "Вы возродитесь на чердаке с полным здоровьем",
            True,
            (200, 200, 200)
        )
        hint_rect = hint_text.get_rect(center=(self.width // 2, self.height // 2 + 70))
        self.screen.blit(hint_text, hint_rect)
    
    def _handle_player_death(self) -> None:
        """Обработка смерти игрока"""
        self.player_dead = True
        self.death_timer = 0.0
        print("\n💀 ВЫ ПОГИБЛИ!")
        print("⏳ Возрождение через 3 секунды...")
        
    def _check_story_triggers(self) -> None:
        """Проверка сюжетных триггеров"""
        # Не показываем диалоги если уже открыт какой-то UI
        if self.show_dialogue or self.show_inventory_ui or self.show_storage_ui or self.show_riddle_ui:
            return
            
        # Вступительный диалог (на чердаке при первом запуске)
        if self.current_location == "attic":
            if self.story_manager.should_show_dialogue("intro", 0):
                self._show_story_dialogue("intro")
                self.story_manager.set_flag("intro_shown", True)
                return
                
        # Диалог на 10 этаже
        if self.current_location != "attic" and self.current_floor == 10:
            if self.story_manager.should_show_dialogue("midpoint", 10):
                self._show_story_dialogue("midpoint")
                self.story_manager.set_flag("midpoint_shown", True)
                return
                
        # Финальный диалог на 20 этаже
        if self.current_location != "attic" and self.current_floor == 20:
            # Проверяем что этаж стабилизирован
            if self.level_generator.floor_state_manager.is_floor_stabilized(20):
                if self.story_manager.should_show_dialogue("ending", 20):
                    self._show_story_dialogue("ending")
                    self.story_manager.set_flag("ending_shown", True)
                    return
    
    def _show_story_dialogue(self, dialogue_id: str) -> None:
        """
        Показать сюжетный диалог
        
        Args:
            dialogue_id: ID диалога
        """
        dialogue = self.story_manager.get_dialogue(dialogue_id)
        if dialogue:
            dialogue.reset()  # Сбрасываем на начало
            self.current_dialogue = dialogue
            self.show_dialogue = True
            print(f"\n📖 Начинается диалог: {dialogue_id}")
    
    def _respawn_player(self) -> None:
        """Возрождение игрока"""
        print("\n✨ Вы возродились на чердаке!")
        
        # Восстанавливаем здоровье
        self.player.stats.health = self.player.stats.max_health
        self.player.stats.endurance = self.player.stats.max_endurance
        
        # Телепортируем на чердак
        if self.attic.spawn_pos:
            spawn_x, spawn_y = self.attic.spawn_pos
            self.player.x = spawn_x
            self.player.y = spawn_y
            
        self.current_location = "attic"
        self.current_floor = 0
        self.current_level = None
        
        # Сбрасываем флаги
        self.player_dead = False
        self.death_timer = 0.0
        
        # Штраф: теряем часть предметов (опционально)
        # Можно добавить потерю случайных предметов
    
    def _toggle_fullscreen(self) -> None:
        """Переключение полноэкранного режима"""
        self.fullscreen = not self.fullscreen
        
        if self.fullscreen:
            # Переход в полноэкранный режим
            self.width = self.screen_width
            self.height = self.screen_height
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
            print(f"🖥️  Полноэкранный режим: {self.width}x{self.height}")
        else:
            # Переход в оконный режим
            self.width, self.height = self.windowed_size
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
            print(f"🪟 Оконный режим: {self.width}x{self.height}")
        
        # Пересоздаём UI с новыми размерами
        self.inventory_ui = InventoryUI(self.width, self.height)
        self.storage_ui = StorageUI(self.width, self.height)
        self.riddle_ui = RiddleUI(self.width, self.height)
        self.dialogue_ui = DialogueUI(self.width, self.height)
        self.message_log = MessageLog(self.width, self.height)
    
    def _serialize_attic_storage(self) -> list:
        """Сериализовать содержимое сундука на чердаке"""
        from ..items.item import Item
        
        storage_data = []
        for slot in self.attic.storage.slots:
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
                storage_data.append(item_data)
            else:
                storage_data.append(None)
        return storage_data
    
    def _deserialize_attic_storage(self, storage_data: list) -> None:
        """Десериализовать содержимое сундука на чердаке"""
        from ..items.item import Item, ItemType, ItemRarity
        from ..items.inventory import InventorySlot
        
        if not storage_data:
            return
        
        self.attic.storage.slots = []
        for slot_data in storage_data:
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
                self.attic.storage.slots.append(InventorySlot(item, slot_data["quantity"]))
            else:
                self.attic.storage.slots.append(InventorySlot())
    
    def _update_profile_metadata(self) -> None:
        """Обновить метаданные профиля"""
        if not self.current_profile:
            return
        
        from datetime import datetime
        import json
        
        # Путь к папке профиля и файлу метаданных
        profile_dir = f"saves/profiles/{self.current_profile}"
        profile_file = os.path.join(profile_dir, "profile.json")
        os.makedirs(profile_dir, exist_ok=True)
        
        # Загружаем существующий профиль или создаём новый
        if os.path.exists(profile_file):
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
            except:
                profile_data = {}
        else:
            profile_data = {
                "name": self.current_profile,
                "created_at": datetime.now().isoformat()
            }
        
        # Обновляем данные
        profile_data["last_played"] = datetime.now().isoformat()
        profile_data["play_time"] = profile_data.get("play_time", 0.0) + self.total_play_time
        profile_data["current_floor"] = self.current_floor
        profile_data["health"] = self.player.stats.health
        
        # Сохраняем
        try:
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)
            # Сбрасываем счётчик времени сессии
            self.total_play_time = 0.0
        except Exception as e:
            print(f"⚠️  Ошибка обновления метаданных профиля: {e}")
    
    def _start_game_with_profile(self, profile_name: str) -> None:
        """
        Запуск игры с выбранным профилем
        
        Args:
            profile_name: Имя профиля
        """
        print(f"\n🎮 Запуск игры с профилем: {profile_name}")
        
        # Загружаем метаданные профиля (время игры)
        profile_dir = f"saves/profiles/{profile_name}"
        profile_file = os.path.join(profile_dir, "profile.json")
        if os.path.exists(profile_file):
            try:
                import json
                with open(profile_file, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
                    # Загружаем накопленное время игры
                    self.total_play_time = 0.0  # Сбрасываем для новой сессии
            except Exception as e:
                print(f"⚠️  Ошибка загрузки метаданных профиля: {e}")
        
        # Пытаемся загрузить сохранение
        save_file = os.path.join(profile_dir, "save.json")
        has_save = os.path.exists(save_file)
        
        if has_save:
            try:
                self._quick_load_from_file(save_file)
                self.message_log.success(f"Добро пожаловать, {profile_name}!")
                print(f"✅ Сохранение загружено")
            except Exception as e:
                print(f"⚠️  Не удалось загрузить сохранение: {e}")
                print("Начинаем новую игру")
                self.message_log.info(f"Добро пожаловать, {profile_name}!")
                has_save = False
        else:
            print("Начинаем новую игру")
            self.message_log.info(f"Добро пожаловать, {profile_name}!")
            
        # Показываем вступительный диалог ТОЛЬКО для новых игроков (без сохранения)
        if not has_save and self.current_floor == 0:
            self._check_story_triggers()
    
    def _quit(self) -> None:
        """Завершение игры"""
        pygame.quit()
        print("\n👋 Игра завершена")
        print("✅ До новых встреч!")
    
    # Колбэки для меню настроек
    def _on_music_toggle(self, enabled: bool) -> None:
        """Переключение музыки"""
        self.sound_manager.music_enabled = enabled
        if enabled:
            self.sound_manager.start_music()
        else:
            self.sound_manager.stop_music()
        print(f"🎵 Музыка: {'ВКЛ' if enabled else 'ВЫКЛ'}")
    
    def _on_sfx_toggle(self, enabled: bool) -> None:
        """Переключение звуковых эффектов"""
        self.sound_manager.sfx_enabled = enabled
        print(f"🔊 Звуковые эффекты: {'ВКЛ' if enabled else 'ВЫКЛ'}")
    
    def _on_music_volume_change(self, volume: float) -> None:
        """Изменение громкости музыки"""
        self.sound_manager.music_volume = volume
        # Применяем новую громкость к текущей музыке
        if self.sound_manager.music_playing:
            pygame.mixer.music.set_volume(volume)
    
    def _on_sfx_volume_change(self, volume: float) -> None:
        """Изменение громкости звуковых эффектов"""
        self.sound_manager.sfx_volume = volume
    
    def _on_settings_back(self) -> None:
        """Закрытие меню настроек"""
        self.show_settings_ui = False
    
    def _get_biome_for_floor(self, floor: int) -> str:
        """
        Определить биом для этажа
        
        Args:
            floor: Номер этажа (1-20+)
            
        Returns:
            Название биома для музыки
        """
        if floor <= 5:
            return "dungeon"  # Этажи 1-5: Старые лаборатории
        elif floor <= 10:
            return "catacombs"  # Этажи 6-10: Архивы и хранилища
        elif floor <= 15:
            return "caves"  # Этажи 11-15: Экспериментальные зоны
        else:
            return "abyss"  # Этажи 16-20+: Зона катастрофы/Бездна
    
    def _any_ui_open(self) -> bool:
        """
        Проверка открыт ли какой-либо UI
        
        Returns:
            True если открыт любой UI (инвентарь, диалог, настройки и т.д.)
        """
        return (
            self.show_inventory_ui or
            self.show_storage_ui or
            self.show_riddle_ui or
            self.show_dialogue or
            self.show_settings_ui or
            self.show_exit_dialog or
            self.show_note
        )
    
    def _update_fps_counter(self, dt: float) -> None:
        """
        Обновление счётчика FPS
        
        Args:
            dt: Delta time
        """
        self.fps_update_time += dt
        self.fps_frames += 1
        
        # Обновляем FPS каждые 0.5 секунды
        if self.fps_update_time >= 0.5:
            self.current_fps = int(self.fps_frames / self.fps_update_time)
            self.fps_update_time = 0.0
            self.fps_frames = 0
    
    def _render_fps(self) -> None:
        """Отрисовка FPS счётчика"""
        if not self.show_fps:
            return
        
        # Создаём полупрозрачный фон
        fps_bg = pygame.Surface((100, 30))
        fps_bg.set_alpha(180)
        fps_bg.fill((0, 0, 0))
        
        # Рисуем фон в правом верхнем углу
        self.screen.blit(fps_bg, (self.width - 110, 10))
        
        # Выбираем цвет в зависимости от FPS
        if self.current_fps >= 55:
            color = (0, 255, 0)  # Зелёный - отлично
        elif self.current_fps >= 30:
            color = (255, 255, 0)  # Жёлтый - нормально
        else:
            color = (255, 0, 0)  # Красный - плохо
        
        # Рисуем текст FPS
        font = pygame.font.Font(None, 24)
        fps_text = font.render(f"FPS: {self.current_fps}", True, color)
        self.screen.blit(fps_text, (self.width - 100, 15))


if __name__ == "__main__":
    # Тест класса Game
    game = Game()
    game.run()
