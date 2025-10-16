"""
Генератор звуков и музыки для игры
Запустите этот скрипт один раз для создания всех аудио файлов
"""
import os
import numpy as np
import pygame
from pathlib import Path


class SoundGenerator:
    """Генератор 8-битных звуков"""
    
    def __init__(self, sample_rate: int = 22050):
        """
        Инициализация генератора
        
        Args:
            sample_rate: Частота дискретизации
        """
        self.sample_rate = sample_rate
        pygame.mixer.init(frequency=sample_rate, size=-16, channels=2, buffer=512)
        
        # Создаём папки если не существуют
        self.sounds_dir = Path("assets/sounds")
        self.music_dir = Path("assets/music")
        self.sounds_dir.mkdir(parents=True, exist_ok=True)
        self.music_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_step_sound(self) -> pygame.mixer.Sound:
        """Генерация звука шага"""
        duration = 0.1
        frequency = 150
        
        samples = int(self.sample_rate * duration)
        wave = np.sin(2 * np.pi * frequency * np.linspace(0, duration, samples))
        
        # Затухание
        envelope = np.linspace(1, 0, samples)
        wave = wave * envelope * 0.3
        
        # Конвертация в 16-бит стерео
        wave = np.int16(wave * 32767)
        stereo_wave = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo_wave)
    
    def generate_chest_sound(self) -> pygame.mixer.Sound:
        """Генерация звука открытия сундука"""
        duration = 0.4
        freq1 = 200
        freq2 = 400
        
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples)
        
        # Две ноты (открытие)
        wave1 = np.sin(2 * np.pi * freq1 * t[:samples//2])
        wave2 = np.sin(2 * np.pi * freq2 * t[samples//2:])
        wave = np.concatenate([wave1, wave2])
        
        # Затухание
        envelope = np.linspace(1, 0, samples)
        wave = wave * envelope * 0.4
        
        wave = np.int16(wave * 32767)
        stereo_wave = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo_wave)
    
    def generate_pickup_sound(self) -> pygame.mixer.Sound:
        """Генерация звука подбора предмета"""
        duration = 0.2
        freqs = [400, 500, 600]
        samples_per_note = int(self.sample_rate * duration / len(freqs))
        
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
    
    def generate_damage_sound(self) -> pygame.mixer.Sound:
        """Генерация звука урона"""
        duration = 0.3
        samples = int(self.sample_rate * duration)
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
    
    def generate_heal_sound(self) -> pygame.mixer.Sound:
        """Генерация звука лечения"""
        duration = 0.3
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples)
        
        # Восходящий тон
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
    
    def generate_discover_sound(self) -> pygame.mixer.Sound:
        """Генерация звука обнаружения"""
        duration = 0.25
        freqs = [500, 700, 900, 1100]
        samples_per_note = int(self.sample_rate * duration / len(freqs))
        
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
    
    def generate_trap_sound(self) -> pygame.mixer.Sound:
        """Генерация звука ловушки"""
        duration = 0.4
        samples = int(self.sample_rate * duration)
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
    
    def generate_music(self, theme: str = "main") -> pygame.mixer.Sound:
        """
        Генерация музыкальной темы
        
        Args:
            theme: Тема музыки (main, catacombs, flooded, fire, abyss)
        """
        duration = 16.0  # 16 секунд для большего разнообразия
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples)
        
        # Разные паттерны для разных тем
        themes = {
            "main": {
                "notes": [262, 294, 330, 392, 440],  # C, D, E, G, A
                "pattern": [0, 2, 4, 2, 3, 1, 0, 4, 2, 0, 3, 1, 4, 2, 0, 1],
                "tempo": 0.5
            },
            "catacombs": {
                "notes": [220, 247, 262, 294, 330],  # A, B, C, D, E (минор)
                "pattern": [0, 1, 0, 2, 1, 0, 3, 2, 0, 1, 4, 3, 2, 1, 0, 0],
                "tempo": 0.6
            },
            "flooded": {
                "notes": [196, 220, 247, 294, 330],  # G, A, B, D, E
                "pattern": [0, 2, 1, 3, 2, 4, 3, 1, 0, 2, 4, 3, 1, 2, 0, 1],
                "tempo": 0.55
            },
            "fire": {
                "notes": [294, 330, 349, 392, 440],  # D, E, F, G, A
                "pattern": [0, 1, 2, 3, 4, 3, 2, 1, 0, 2, 4, 2, 3, 1, 0, 4],
                "tempo": 0.45
            },
            "abyss": {
                "notes": [174, 196, 220, 247, 262],  # F, G, A, B, C (низкие)
                "pattern": [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 3, 2, 1, 0, 0, 0],
                "tempo": 0.7
            }
        }
        
        theme_data = themes.get(theme, themes["main"])
        notes = theme_data["notes"]
        pattern = theme_data["pattern"]
        
        wave = np.zeros(samples)
        note_duration = duration / len(pattern)
        
        for i, note_idx in enumerate(pattern):
            start = int(i * note_duration * self.sample_rate)
            end = int((i + 1) * note_duration * self.sample_rate)
            
            freq = notes[note_idx]
            note_t = t[start:end] - t[start]
            
            # Основная нота
            note_wave = np.sin(2 * np.pi * freq * note_t)
            
            # Добавляем гармонику для богатства звука
            harmonic = np.sin(2 * np.pi * freq * 2 * note_t) * 0.3
            note_wave = note_wave + harmonic
            
            # Огибающая для каждой ноты
            attack = len(note_wave) // 10
            release = len(note_wave) // 5
            sustain = len(note_wave) - attack - release
            
            envelope = np.concatenate([
                np.linspace(0, 1, attack),
                np.ones(sustain),
                np.linspace(1, 0, release)
            ])
            
            wave[start:end] = note_wave * envelope
        
        # Нормализация
        wave = wave * 0.12  # Тихая фоновая музыка
        
        wave = np.int16(wave * 32767)
        stereo_wave = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo_wave)
    
    def save_sound(self, sound: pygame.mixer.Sound, filename: str, is_music: bool = False):
        """
        Сохранить звук в файл
        
        Args:
            sound: Звук для сохранения
            filename: Имя файла
            is_music: Музыка или звуковой эффект
        """
        directory = self.music_dir if is_music else self.sounds_dir
        filepath = directory / filename
        
        # Сохраняем через pygame
        pygame.mixer.Sound.play(sound)
        pygame.time.wait(int(sound.get_length() * 1000) + 100)
        
        # Получаем массив и сохраняем
        array = pygame.sndarray.array(sound)
        
        # Используем scipy для сохранения WAV
        try:
            from scipy.io import wavfile
            wavfile.write(str(filepath), self.sample_rate, array)
            print(f"✅ Сохранён: {filepath}")
        except ImportError:
            # Альтернативный метод через pygame
            pygame.mixer.Sound.stop(sound)
            # Создаём временный звук и сохраняем
            temp_sound = pygame.sndarray.make_sound(array)
            # К сожалению pygame не имеет прямого метода сохранения
            # Используем numpy для записи
            import wave
            with wave.open(str(filepath), 'w') as wav_file:
                wav_file.setnchannels(2)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(array.tobytes())
            print(f"✅ Сохранён: {filepath}")
    
    def generate_all(self):
        """Генерация всех звуков и музыки"""
        print("\n🎵 Генерация звуковых эффектов...")
        
        # Звуковые эффекты
        sounds = {
            "step.wav": self.generate_step_sound(),
            "chest_open.wav": self.generate_chest_sound(),
            "pickup.wav": self.generate_pickup_sound(),
            "damage.wav": self.generate_damage_sound(),
            "heal.wav": self.generate_heal_sound(),
            "discover.wav": self.generate_discover_sound(),
            "trap.wav": self.generate_trap_sound(),
        }
        
        for filename, sound in sounds.items():
            self.save_sound(sound, filename, is_music=False)
        
        print("\n🎶 Генерация музыкальных тем...")
        
        # Музыкальные темы
        music_themes = {
            "theme_main.wav": "main",
            "theme_catacombs.wav": "catacombs",
            "theme_flooded.wav": "flooded",
            "theme_fire.wav": "fire",
            "theme_abyss.wav": "abyss",
        }
        
        for filename, theme in music_themes.items():
            music = self.generate_music(theme)
            self.save_sound(music, filename, is_music=True)
        
        print("\n✅ Генерация завершена!")
        print(f"📁 Звуки: {self.sounds_dir}")
        print(f"📁 Музыка: {self.music_dir}")


if __name__ == "__main__":
    print("=" * 50)
    print("🎮 ГЕНЕРАТОР ЗВУКОВ - Подземелье НИИЧАВО")
    print("=" * 50)
    
    generator = SoundGenerator()
    generator.generate_all()
    
    print("\n" + "=" * 50)
    print("🎉 Готово! Теперь можно запускать игру.")
    print("=" * 50)
