"""
Подземелье НИИЧАВО
Roguelike игра с элементами головоломок

Главный файл запуска игры
"""
import sys
import argparse
from src.core.game import Game


def main():
    """Точка входа в игру"""
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description="Подземелье НИИЧАВО - Roguelike игра")
    parser.add_argument("--fullscreen", "-f", action="store_true", 
                       help="Запустить в полноэкранном режиме")
    parser.add_argument("--width", "-w", type=int, default=1200,
                       help="Ширина окна (по умолчанию: 1200)")
    parser.add_argument("--height", type=int, default=800,
                       help="Высота окна (по умолчанию: 800)")
    args = parser.parse_args()
    
    print("=" * 50)
    print("ПОДЗЕМЕЛЬЕ НИИЧАВО")
    print("=" * 50)
    print()
    print("📋 Этап 1: Базовый функционал - ЗАВЕРШЁН")
    print("📋 Этап 2: Расширенный функционал - В РАЗРАБОТКЕ")
    print()
    
    if args.fullscreen:
        print("🖥️  Режим: Полноэкранный")
    else:
        print(f"🪟 Режим: Оконный ({args.width}x{args.height})")
    print("💡 Подсказка: Нажмите F11 для переключения режима")
    print()
    
    try:
        # Создаём и запускаем игру
        game = Game(width=args.width, height=args.height, fullscreen=args.fullscreen)
        game.run()
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
