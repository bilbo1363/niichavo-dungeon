# Музыкальные темы игры

## Структура музыкальных файлов

### Системные темы

| Тема | Файл | Описание | Когда играет |
|------|------|----------|--------------|
| Заставка | theme_splash.mp3 | Вступительная тема | При запуске игры |
| Главное меню | theme_menu.mp3 | Музыка главного меню | В меню выбора профиля |

### Игровые локации

| Локация | Файл | Описание | Атмосфера |
|---------|------|----------|-----------|
| Чердак/Лаборатория | theme_attic.mp3 | База игрока | Спокойная, релаксирующая |

### Биомы по этажам

| Биом | Этажи | Файл | Описание |
|------|-------|------|----------|
| Старые лаборатории | 1-5 | theme_dungeon.mp3 | Начальная локация |
| Архивы и хранилища | 6-10 | theme_catacombs.mp3 | Древние архивы |
| Экспериментальные зоны | 11-15 | theme_caves.mp3 | Опасные зоны |
| Зона катастрофы | 16-20+ | theme_abyss.mp3 | Самые глубокие уровни |

## Технические требования

- Формат: MP3 (приоритет) или WAV (fallback)
- Частота: 22050 Hz или 44100 Hz
- Битрейт: 128-192 kbps для MP3
- Длительность: 120-180 секунд
- Важно: Музыка должна зацикливаться без щелчков

## Структура папки

assets/music/
- theme_splash.mp3
- theme_menu.mp3
- theme_attic.mp3
- theme_dungeon.mp3
- theme_catacombs.mp3
- theme_caves.mp3
- theme_abyss.mp3
- arch/ (архив старых версий)

## Промпты для Suno

### Чердак/Лаборатория (300 символов)
Calm ambient laboratory theme, soft mysterious synths, gentle echoing piano, subtle scientific atmosphere, relaxing yet curious mood, slow tempo 60-80 BPM, ethereal pads, distant mechanical sounds, safe haven feeling, inspired by Soviet sci-fi aesthetics, loopable

### Старые лаборатории 1-5 (300 символов)
Mysterious dungeon exploration, ancient laboratory ambience, echoing footsteps, dusty corridors, subtle tension, moderate tempo 80-100 BPM, dark synths, distant machinery hum, forgotten experiments atmosphere, Soviet research facility vibes, loopable adventure music

### Архивы 6-10 (300 символов)
Dark catacombs theme, ancient archives atmosphere, heavy stone echoes, dusty books rustling, ominous mood, tempo 90-110 BPM, deep bass drones, whispered secrets, forbidden knowledge feeling, mysterious library ambience, eerie yet fascinating, loopable background

### Экспериментальные зоны 11-15 (300 символов)
Dangerous experimental zone, unstable magic energy, chaotic synths, crackling electricity, tense atmosphere, tempo 100-120 BPM, glitchy sounds, reality distortion effects, mad science vibes, unpredictable rhythms, Soviet sci-fi horror, loopable tension music

### Бездна 16-20+ (300 символов)
Abyss descent theme, reality breakdown, distorted soundscape, chaotic atmosphere, dark ambient horror, tempo 110-140 BPM, deep sub-bass, glitch effects, void sounds, existential dread, cosmic horror vibes, unstable time signatures, loopable nightmare music
