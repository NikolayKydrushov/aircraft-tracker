"""
Точка входа в программу Aircraft Tracker
"""
from src.interfaces.cli import user_interaction


def main():
    """Главная функция программы"""
    try:
        user_interaction()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем. До свидания! ✈️")
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")
        print("Попробуйте перезапустить программу.")


if __name__ == "__main__":
    main()
