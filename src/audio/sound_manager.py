"""
Менеджер звуков и музыки
"""
import pygame
import numpy as np
import os
from pathlib import Path
from typing import Dict, Optional


class SoundManager:
    """Менеджер звуков"""
    
    def __init__(self):
        """Инициализация менеджера звуков"""
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_playing = False
        self.sfx_enabled = True
        self.music_enabled = True
        self.sfx_volume = 0.5
        self.music_volume = 0.3
        
        # Пути к ресурсам
        self.sounds_dir = Path("assets/sounds")
        self.music_dir = Path("assets/music")
        
        # Текущий биом для музыки
        self.current_biome = None
        self.current_music = None
        
        # Загружаем или генерируем звуки
        self._load_or_generate_sounds()
        
        print("🔊 Звуковая система инициализирована")
    
    def _load_or_generate_sounds(self) -> None:
        """Загрузка звуков из файлов или генерация если файлов нет"""
        sound_files = {
            "step": "step.wav",
            "chest_open": "chest_open.wav",
            "pickup": "pickup.wav",
            "damage": "damage.wav",
            "heal": "heal.wav",
            "discover": "discover.wav",
            "trap": "trap.wav",
        }
        
        # Проверяем наличие папки со звуками
        if self.sounds_dir.exists():
            # Пытаемся загрузить из файлов
            loaded_count = 0
            for sound_name, filename in sound_files.items():
                filepath = self.sounds_dir / filename
                if filepath.exists():
                    try:
                        self.sounds[sound_name] = pygame.mixer.Sound(str(filepath))
                        loaded_count += 1
                    except Exception as e:
                        print(f"⚠️ Ошибка загрузки {filename}: {e}")
                        # Генерируем если не удалось загрузить
                        self.sounds[sound_name] = self._generate_sound(sound_name)
                else:
                    # Генерируем если файл не найден
                    self.sounds[sound_name] = self._generate_sound(sound_name)
            
            if loaded_count > 0:
                print(f"   📁 Загружено звуков из файлов: {loaded_count}/{len(sound_files)}")
            if loaded_count < len(sound_files):
                print(f"   🎵 Сгенерировано процедурно: {len(sound_files) - loaded_count}/{len(sound_files)}")
        else:
            # Папки нет - генерируем все
            print("   ⚠️ Папка assets/sounds не найдена")
            print("   🎵 Генерация звуков процедурно...")
            self._generate_sounds()
    
    def _generate_sound(self, sound_name: str) -> pygame.mixer.Sound:
        """
        Генерация конкретного звука
        
        Args:
            sound_name: Название звука
            
        Returns:
            Сгенерированный звук
        """
        generators = {
            "step": self._generate_step_sound,
            "chest_open": self._generate_chest_sound,
            "pickup": self._generate_pickup_sound,
            "damage": self._generate_damage_sound,
            "heal": self._generate_heal_sound,
            "discover": self._generate_discover_sound,
            "trap": self._generate_trap_sound,
        }
        
        generator = generators.get(sound_name)
        if generator:
            return generator()
        else:
            # Возвращаем пустой звук если генератор не найден
            return pygame.mixer.Sound(buffer=np.zeros((100, 2), dtype=np.int16))
    
    def _generate_sounds(self) -> None:
        """Генерация 8-битных звуков"""
        # Шаги
        self.sounds["step"] = self._generate_step_sound()
        
        # Открытие сундука
        self.sounds["chest_open"] = self._generate_chest_sound()
        
        # Подбор предмета
        self.sounds["pickup"] = self._generate_pickup_sound()
        
        # Урон
        self.sounds["damage"] = self._generate_damage_sound()
        
        # Лечение
        self.sounds["heal"] = self._generate_heal_sound()
        
        # Обнаружение
        self.sounds["discover"] = self._generate_discover_sound()
        
        # Ловушка
        self.sounds["trap"] = self._generate_trap_sound()
        
        print(f"   🎵 Сгенерировано звуков: {len(self.sounds)}")
    
    def _generate_step_sound(self) -> pygame.mixer.Sound:
        """Генерация звука шага"""
        sample_rate = 22050
        duration = 0.1
        frequency = 150
        
        samples = int(sample_rate * duration)
        wave = np.sin(2 * np.pi * frequency * np.linspace(0, duration, samples))
        
        # Затухание
        envelope = np.linspace(1, 0, samples)
        wave = wave * envelope * 0.3
        
        # Конвертация в 16-бит
        wave = np.int16(wave * 32767)
        stereo_wave = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo_wave)
    
    def _generate_chest_sound(self) -> pygame.mixer.Sound:
        """Генерация звука открытия сундука"""
        sample_rate = 22050
        duration = 0.4
        
        # Две ноты (открытие)
        freq1 = 200
        freq2 = 400
        
        samples = int(sample_rate * duration)
        t = np.linspace(0, duration, samples)
        
        # Первая нота
        wave1 = np.sin(2 * np.pi * freq1 * t[:samples//2])
        # Вторая нота
        wave2 = np.sin(2 * np.pi * freq2 * t[samples//2:])
        
        wave = np.concatenate([wave1, wave2])
        
        # Затухание
        envelope = np.linspace(1, 0, samples)
        wave = wave * envelope * 0.4
        
        wave = np.int16(wave * 32767)
        stereo_wave = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo_wave)
    
    def _generate_pickup_sound(self) -> pygame.mixer.Sound:
        """Генерация звука подбора предмета"""
        sample_rate = 22050
        duration = 0.2
        
        # Восходящая арпеджио
        freqs = [400, 500, 600]
        samples_per_note = int(sample_rate * duration / len(freqs))
        
        wave = np.array([])
        for freq in freqs:
            t = np.linspace(0, duration / len(freqs), samples_per_note)
            note = np.sin(2 * np.pi * freq * t)
            wave = np.concatenate([wave, note])
        
        # Затухание
        envelope = np.linspace(1, 0, len(wave))
        wave = wave * envelope * 0.3
        
        wave = np.int16(wave * 32767)
        stereo_wave = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo_wave)
    
    def _generate_damage_sound(self) -> pygame.mixer.Sound:
        """Генерация звука урона"""
        sample_rate = 22050
        duration = 0.3
        
        samples = int(sample_rate * duration)
        t = np.linspace(0, duration, samples)
        
        # Нисходящий тон с шумом
        freq_start = 400
        freq_end = 100
        freq = np.linspace(freq_start, freq_end, samples)
        
        wave = np.sin(2 * np.pi * freq * t)
        
        # Добавляем шум
        noise = np.random.uniform(-0.2, 0.2, samples)
        wave = wave * 0.7 + noise * 0.3
        
        # Затухание
        envelope = np.linspace(1, 0, samples)
        wave = wave * envelope * 0.5
        
        wave = np.int16(wave * 32767)
        stereo_wave = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo_wave)
    
    def _generate_heal_sound(self) -> pygame.mixer.Sound:
        """Генерация звука лечения"""
        sample_rate = 22050
        duration = 0.3
        
        # Восходящий тон
        samples = int(sample_rate * duration)
        t = np.linspace(0, duration, samples)
        
        freq_start = 300
        freq_end = 600
        freq = np.linspace(freq_start, freq_end, samples)
        
        wave = np.sin(2 * np.pi * freq * t)
        
        # Затухание
        envelope = np.linspace(0.5, 1, samples)
        wave = wave * envelope * 0.3
        
        wave = np.int16(wave * 32767)
        stereo_wave = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo_wave)
    
    def _generate_discover_sound(self) -> pygame.mixer.Sound:
        """Генерация звука обнаружения"""
        sample_rate = 22050
        duration = 0.25
        
        # Быстрая арпеджио вверх
        freqs = [500, 700, 900, 1100]
        samples_per_note = int(sample_rate * duration / len(freqs))
        
        wave = np.array([])
        for freq in freqs:
            t = np.linspace(0, duration / len(freqs), samples_per_note)
            note = np.sin(2 * np.pi * freq * t)
            wave = np.concatenate([wave, note])
        
        # Затухание
        envelope = np.linspace(1, 0, len(wave))
        wave = wave * envelope * 0.25
        
        wave = np.int16(wave * 32767)
        stereo_wave = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo_wave)
    
    def _generate_trap_sound(self) -> pygame.mixer.Sound:
        """Генерация звука ловушки"""
        sample_rate = 22050
        duration = 0.4
        
        samples = int(sample_rate * duration)
        t = np.linspace(0, duration, samples)
        
        # Резкий звук с вибрацией
        freq = 200
        wave = np.sin(2 * np.pi * freq * t)
        
        # Добавляем вибрацию
        vibrato = np.sin(2 * np.pi * 10 * t) * 0.3
        wave = wave * (1 + vibrato)
        
        # Добавляем шум
        noise = np.random.uniform(-0.3, 0.3, samples)
        wave = wave * 0.6 + noise * 0.4
        
        # Затухание
        envelope = np.linspace(1, 0, samples)
        wave = wave * envelope * 0.6
        
        wave = np.int16(wave * 32767)
        stereo_wave = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo_wave)
    
    def play_sound(self, sound_name: str) -> None:
        """
        Воспроизвести звук
        
        Args:
            sound_name: Название звука
        """
        if not self.sfx_enabled:
            return
        
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            sound.set_volume(self.sfx_volume)
            sound.play()
    
    def start_music(self, biome: str = "dungeon") -> None:
        """
        Запустить фоновую музыку
        
        Args:
            biome: Локация/биом для музыки:
                - splash: Заставка
                - menu: Главное меню
                - attic: Чердак/Лаборатория (база)
                - dungeon: Этажи 1-5 (Старые лаборатории)
                - catacombs: Этажи 6-10 (Архивы и хранилища)
                - caves: Этажи 11-15 (Экспериментальные зоны)
                - abyss: Этажи 16-20+ (Зона катастрофы/Бездна)
        """
        if not self.music_enabled:
            return
        
        # Если уже играет та же музыка - не перезапускаем
        if self.music_playing and self.current_biome == biome:
            return
        
        # Останавливаем текущую музыку
        if self.music_playing:
            self.stop_music()
        
        # Загружаем или генерируем музыку для биома
        self._load_and_play_music(biome)
        self.music_playing = True
        self.current_biome = biome
    
    def _load_and_play_music(self, biome: str) -> None:
        """
        Загрузка и воспроизведение музыки для биома
        
        Args:
            biome: Биом (attic, main, catacombs, flooded, fire, abyss)
        """
        # Соответствие локаций/биомов файлам (приоритет mp3, fallback на wav)
        music_files = {
            # Системные темы
            "splash": ["theme_splash.mp3", "theme_splash.wav"],           # Заставка при запуске
            "menu": ["theme_menu.mp3", "Menu.mp3"],                       # Главное меню
            
            # Игровые локации
            "attic": ["theme_attic.mp3", "theme_laboratory.mp3"],        # Чердак/Лаборатория (база)
            
            # Биомы по этажам (уровни сложности)
            "dungeon": ["theme_dungeon.mp3", "theme_main.mp3"],          # Этажи 1-5: Старые лаборатории
            "catacombs": ["theme_catacombs.mp3"],                         # Этажи 6-10: Архивы и хранилища
            "caves": ["theme_caves.mp3", "theme_experimental.mp3"],      # Этажи 11-15: Экспериментальные зоны
            "abyss": ["theme_abyss.mp3", "theme_catastrophe.mp3"],       # Этажи 16-20+: Зона катастрофы/Бездна
        }
        
        # Получаем список возможных файлов для биома
        possible_files = music_files.get(biome, ["theme_main.mp3", "theme_main.wav"])
        
        # Пытаемся загрузить первый существующий файл
        for filename in possible_files:
            filepath = self.music_dir / filename
            
            if filepath.exists():
                try:
                    # Используем pygame.mixer.music для фоновой музыки
                    pygame.mixer.music.load(str(filepath))
                    pygame.mixer.music.set_volume(self.music_volume)
                    pygame.mixer.music.play(loops=-1)  # Бесконечный цикл
                    print(f"   🎵 Музыка: {filename}")
                    return
                except Exception as e:
                    print(f"⚠️ Ошибка загрузки музыки {filename}: {e}")
                    continue  # Пробуем следующий файл
        
        # Если не удалось загрузить - генерируем
        print(f"   🎵 Генерация музыки для биома: {biome}")
        self._generate_and_play_music()
    
    def _generate_and_play_music(self) -> None:
        """Генерация и воспроизведение фоновой музыки"""
        sample_rate = 22050
        duration = 8.0  # 8 секунд, будет зацикливаться
        
        samples = int(sample_rate * duration)
        t = np.linspace(0, duration, samples)
        
        # Простая мелодия (пентатоника)
        notes = [262, 294, 330, 392, 440]  # C, D, E, G, A
        pattern = [0, 2, 4, 2, 3, 1, 0, 4]  # Паттерн нот
        
        wave = np.zeros(samples)
        note_duration = duration / len(pattern)
        
        for i, note_idx in enumerate(pattern):
            start = int(i * note_duration * sample_rate)
            end = int((i + 1) * note_duration * sample_rate)
            
            freq = notes[note_idx]
            note_t = t[start:end] - t[start]
            note_wave = np.sin(2 * np.pi * freq * note_t)
            
            # Огибающая для каждой ноты
            envelope = np.concatenate([
                np.linspace(0, 1, len(note_wave) // 10),
                np.ones(len(note_wave) - len(note_wave) // 10 - len(note_wave) // 5),
                np.linspace(1, 0, len(note_wave) // 5)
            ])
            
            wave[start:end] = note_wave * envelope
        
        # Нормализация
        wave = wave * 0.15  # Тихая фоновая музыка
        
        wave = np.int16(wave * 32767)
        stereo_wave = np.column_stack((wave, wave))
        
        music = pygame.sndarray.make_sound(stereo_wave)
        music.set_volume(self.music_volume)
        music.play(loops=-1)  # Бесконечный цикл
    
    def stop_music(self) -> None:
        """Остановить музыку"""
        pygame.mixer.music.stop()
        self.music_playing = False
        self.current_biome = None
    
    def toggle_sfx(self) -> None:
        """Переключить звуковые эффекты"""
        self.sfx_enabled = not self.sfx_enabled
        print(f"🔊 Звуковые эффекты: {'ВКЛ' if self.sfx_enabled else 'ВЫКЛ'}")
    
    def toggle_music(self) -> None:
        """Переключить музыку"""
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            self.start_music()
        else:
            self.stop_music()
        print(f"🎵 Музыка: {'ВКЛ' if self.music_enabled else 'ВЫКЛ'}")
