"""
Система загадок
"""
from dataclasses import dataclass
from typing import Optional, List
import random


@dataclass
class Riddle:
    """Класс загадки"""
    
    question: str
    answer: str
    x: int
    y: int
    solved: bool = False
    reward_description: str = "Знание"
    
    def render(self, screen, camera_x: int = 0, camera_y: int = 0, fog_of_war=None) -> None:
        """
        Отрисовка индикатора загадки на стене
        
        Args:
            screen: Поверхность для отрисовки
            camera_x: Смещение камеры по X
            camera_y: Смещение камеры по Y
            fog_of_war: Туман войны
        """
        import pygame
        
        # Проверяем видимость
        if fog_of_war and not fog_of_war.is_visible(self.x, self.y):
            return
            
        # Вычисляем позицию на экране
        tile_size = 32
        screen_x = self.x * tile_size - camera_x
        screen_y = self.y * tile_size - camera_y
        
        if self.solved:
            # Решённая загадка - серая с галочкой
            font = pygame.font.Font(None, 48)
            text = font.render("✓", True, (150, 150, 150))  # Серый
            text_rect = text.get_rect(center=(screen_x + tile_size // 2, screen_y + tile_size // 2))
            
            # Серый фон
            pygame.draw.circle(
                screen,
                (60, 60, 60),  # Тёмно-серый фон
                (screen_x + tile_size // 2, screen_y + tile_size // 2),
                16
            )
            
            # Галочка
            screen.blit(text, text_rect)
        else:
            # Нерешённая загадка - жёлтый знак вопроса
            font = pygame.font.Font(None, 48)
            text = font.render("?", True, (255, 255, 0))  # Жёлтый
            text_rect = text.get_rect(center=(screen_x + tile_size // 2, screen_y + tile_size // 2))
            
            # Фиолетовый фон
            pygame.draw.circle(
                screen,
                (100, 50, 150),  # Фиолетовый фон
                (screen_x + tile_size // 2, screen_y + tile_size // 2),
                16
            )
            
            # Знак вопроса
            screen.blit(text, text_rect)
    
    def check_answer(self, player_answer: str) -> bool:
        """
        Проверить ответ игрока
        
        Args:
            player_answer: Ответ игрока
            
        Returns:
            True если ответ правильный
        """
        # Нормализуем ответы (убираем пробелы, приводим к нижнему регистру)
        normalized_answer = player_answer.strip().lower()
        normalized_correct = self.answer.strip().lower()
        
        if normalized_answer == normalized_correct:
            self.solved = True
            print(f"\n✅ Правильно! Загадка решена!")
            print(f"🎁 Награда: {self.reward_description}")
            return True
        else:
            print(f"\n❌ Неправильно. Попробуйте ещё раз.")
            return False


class RiddleGenerator:
    """Генератор загадок"""
    
    def __init__(self):
        """Инициализация генератора"""
        # Банк математических загадок
        self.math_riddles = [
            {
                "question": "Сколько будет 7 × 8?",
                "answer": "56",
                "reward": "+10 HP"
            },
            {
                "question": "Последовательность Фибоначчи: 1, 1, 2, 3, 5, 8, 13, ?",
                "answer": "21",
                "reward": "+5 Ясность"
            },
            {
                "question": "Решите уравнение: 2x + 5 = 17. Чему равен x?",
                "answer": "6",
                "reward": "+15 Выносливость"
            },
            {
                "question": "Сколько граней у куба?",
                "answer": "6",
                "reward": "+10 HP"
            },
            {
                "question": "Простое число после 11?",
                "answer": "13",
                "reward": "+5 Ясность"
            },
            {
                "question": "Квадратный корень из 144?",
                "answer": "12",
                "reward": "+10 HP"
            },
            {
                "question": "Сколько градусов в прямом угле?",
                "answer": "90",
                "reward": "+15 Выносливость"
            },
            {
                "question": "Число π (пи) округлённое до сотых?",
                "answer": "3.14",
                "reward": "+5 Ясность"
            },
            {
                "question": "2 в степени 5 = ?",
                "answer": "32",
                "reward": "+10 HP"
            },
            {
                "question": "Факториал 5 (5!) = ?",
                "answer": "120",
                "reward": "+20 HP"
            },
        ]
        
        # Банк логических загадок
        self.logic_riddles = [
            {
                "question": "У отца Мэри пять дочерей: Чача, Чече, Чичи, Чочо. Как зовут пятую?",
                "answer": "мэри",
                "reward": "+10 Ясность"
            },
            {
                "question": "Что тяжелее: килограмм ваты или килограмм железа?",
                "answer": "одинаково",
                "reward": "+5 Ясность"
            },
            {
                "question": "Сколько месяцев в году имеют 28 дней?",
                "answer": "12",
                "reward": "+10 HP"
            },
        ]
        
        print("🧩 Генератор загадок создан")
        
    def generate_riddle(self, x: int, y: int, seed: int = None) -> Riddle:
        """
        Сгенерировать загадку
        
        Args:
            x: Позиция X
            y: Позиция Y
            seed: Seed для детерминированности
            
        Returns:
            Загадка
        """
        if seed is not None:
            random.seed(seed)
            
        # Выбираем случайную загадку
        all_riddles = self.math_riddles + self.logic_riddles
        riddle_data = random.choice(all_riddles)
        
        riddle = Riddle(
            question=riddle_data["question"],
            answer=riddle_data["answer"],
            x=x,
            y=y,
            reward_description=riddle_data["reward"]
        )
        
        print(f"📜 Загадка создана на ({x}, {y})")
        
        return riddle


class RiddleManager:
    """Менеджер загадок на уровне"""
    
    def __init__(self):
        """Инициализация менеджера"""
        self.riddles: List[Riddle] = []
        self.generator = RiddleGenerator()
        
    def add_riddle(self, riddle: Riddle) -> None:
        """
        Добавить загадку
        
        Args:
            riddle: Загадка
        """
        self.riddles.append(riddle)
        
    def spawn_riddle(self, x: int, y: int, seed: int = None) -> Riddle:
        """
        Создать загадку на стене
        
        Args:
            x: Позиция X
            y: Позиция Y
            seed: Seed для детерминированности
            
        Returns:
            Созданная загадка
        """
        riddle = self.generator.generate_riddle(x, y, seed)
        self.add_riddle(riddle)
        return riddle
        
    def get_riddle_at(self, x: int, y: int) -> Optional[Riddle]:
        """
        Получить загадку на позиции
        
        Args:
            x: Позиция X
            y: Позиция Y
            
        Returns:
            Загадка или None (возвращает даже решённые загадки)
        """
        for riddle in self.riddles:
            if riddle.x == x and riddle.y == y:
                return riddle
        return None
        
    def get_unsolved_count(self) -> int:
        """
        Получить количество нерешённых загадок
        
        Returns:
            Количество нерешённых загадок
        """
        return sum(1 for riddle in self.riddles if not riddle.solved)
        
    def get_solved_count(self) -> int:
        """
        Получить количество решённых загадок
        
        Returns:
            Количество решённых загадок
        """
        return sum(1 for riddle in self.riddles if riddle.solved)
        
    def render(self, screen, camera_x: int = 0, camera_y: int = 0, fog_of_war=None) -> None:
        """
        Отрисовка всех загадок
        
        Args:
            screen: Поверхность для отрисовки
            camera_x: Смещение камеры по X
            camera_y: Смещение камеры по Y
            fog_of_war: Туман войны
        """
        for riddle in self.riddles:
            riddle.render(screen, camera_x, camera_y, fog_of_war)


if __name__ == "__main__":
    # Тест системы загадок
    manager = RiddleManager()
    
    # Создаём загадку
    riddle = manager.spawn_riddle(10, 10, seed=42)
    print(f"\nВопрос: {riddle.question}")
    print(f"Правильный ответ: {riddle.answer}")
    
    # Проверяем неправильный ответ
    riddle.check_answer("999")
    
    # Проверяем правильный ответ
    riddle.check_answer(riddle.answer)
    
    print(f"\nРешено загадок: {manager.get_solved_count()}")
    print(f"Нерешённых загадок: {manager.get_unsolved_count()}")
