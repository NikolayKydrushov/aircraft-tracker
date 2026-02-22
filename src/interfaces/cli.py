from typing import List

from src.api.aircraft_api import AircraftAPI
from src.models.aircraft import Aircraft
from src.storage.csv_storage import CSVStorage
from src.storage.json_storage import JSONStorage
from src.utils.validators import parse_altitude_range, validate_country


def print_header(text: str):
    """Вывод заголовка"""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)


def print_aircraft_list(aircraft_list: List[Aircraft], title: str = ""):
    """
    Вывод списка самолетов в отформатированном виде

    Args:
        aircraft_list: Список самолетов
        title: Заголовок для вывода
    """
    if title:
        print(f"\n--- {title} ---")

    if not aircraft_list:
        print("Нет данных для отображения")
        return

    for i, aircraft in enumerate(aircraft_list, 1):
        print(f"{i:2}. {aircraft}")

    print(f"\nВсего: {len(aircraft_list)} самолетов")


def get_top_by_altitude(aircraft_list: List[Aircraft], n: int) -> List[Aircraft]:
    """
    Получение топ N самолетов по высоте

    Args:
        aircraft_list: Список самолетов
        n: Количество самолетов
    """
    # Сортируем по высоте (от большей к меньшей)
    sorted_aircraft = sorted(aircraft_list, key=lambda a: a.altitude, reverse=True)
    return sorted_aircraft[:n]


def filter_by_country(
    aircraft_list: List[Aircraft], countries: List[str]
) -> List[Aircraft]:
    """
    Фильтрация самолетов по стране регистрации

    Args:
        aircraft_list: Список самолетов
        countries: Список стран для фильтрации
    """
    filtered = []
    for aircraft in aircraft_list:
        for country in countries:
            if country.lower() in aircraft.origin_country.lower():
                filtered.append(aircraft)
                break
    return filtered


def filter_by_altitude_range(
    aircraft_list: List[Aircraft], min_alt: float, max_alt: float
) -> List[Aircraft]:
    """
    Фильтрация самолетов по диапазону высот

    Args:
        aircraft_list: Список самолетов
        min_alt: Минимальная высота
        max_alt: Максимальная высота
    """
    return [a for a in aircraft_list if min_alt <= a.altitude <= max_alt]


def sort_by_velocity(
    aircraft_list: List[Aircraft], reverse: bool = True
) -> List[Aircraft]:
    """
    Сортировка самолетов по скорости

    Args:
        aircraft_list: Список самолетов
        reverse: True для сортировки по убыванию
    """
    return sorted(aircraft_list, key=lambda a: a.velocity, reverse=reverse)


def user_interaction():
    """Основная функция для взаимодействия с пользователем"""
    print_header("AIRCRAFT TRACKER")
    print("Программа для отслеживания самолетов в реальном времени\n")

    # Спрашиваем, в каком формате сохранять
    print("\nВыберите формат сохранения:")
    print("1. JSON (по умолчанию)")
    print("2. CSV (для просмотра в Excel)")

    format_choice = input("Ваш выбор (1/2): ").strip()

    # Создаем нужное хранилище
    if format_choice == '2':
        storage = CSVStorage()
        print("Используется CSV формат")
    else:
        storage = JSONStorage()
        print("Используется JSON формат")

    # Инициализация компонентов
    api = AircraftAPI()

    while True:
        print("\nГлавное меню")
        print("1. Получить данные о самолетах в стране")
        print("2. Показать топ N самолетов по высоте")
        print("3. Найти самолеты по стране регистрации")
        print("4. Показать все сохраненные самолеты")
        print("5. Дополнительные фильтры")
        print("0. Выход")

        choice = input("\nВыберите действие (0-5): ").strip()

        if choice == "0":
            print("\nДо свидания!")
            break

        elif choice == "1":
            # Получение данных о самолетах в стране
            country = input("\nВведите название страны: ").strip()

            if not validate_country(country):
                print("Ошибка: Некорректное название страны")
                continue

            print(f"\nПолучаем данные о самолетах в {country}...")
            raw_data = api.get_aircraft_by_country(country)

            if not raw_data:
                print("Не удалось получить данные или в стране нет самолетов")
                continue

            # Обрабатываем данные и создаем объекты
            processed_data = api.process_aircraft_data(raw_data)
            aircraft_list = Aircraft.cast_to_object_list(processed_data)

            # Сохраняем в хранилище
            added = storage.add_multiple_aircraft(aircraft_list)
            print(f"Найдено {len(aircraft_list)} самолетов")
            print(f"Сохранено {added} записей")

            # Показываем первые 10
            print_aircraft_list(aircraft_list[:10], "Первые 10 самолетов")

        elif choice == "2":
            # Топ N по высоте
            try:
                n = int(input("\nВведите количество самолетов для топа: "))
                if n <= 0:
                    print("Ошибка: Введите положительное число")
                    continue
            except ValueError:
                print("Ошибка: Введите число")
                continue

            aircraft_list = storage.get_all()
            if not aircraft_list:
                print("Нет данных. Сначала получите информацию о самолетах.")
                continue

            top_aircraft = get_top_by_altitude(aircraft_list, n)
            print_aircraft_list(top_aircraft, f"Топ {n} самолетов по высоте")

        elif choice == "3":
            # Фильтр по стране регистрации
            countries_input = input(
                "\nВведите страны для фильтрации (через запятую): "
            ).strip()
            countries = [c.strip() for c in countries_input.split(',') if c.strip()]

            if not countries:
                print("Ошибка: Введите хотя бы одну страну")
                continue

            aircraft_list = storage.get_all()
            if not aircraft_list:
                print("Нет данных. Сначала получите информацию о самолетах.")
                continue

            filtered = filter_by_country(aircraft_list, countries)
            print_aircraft_list(filtered, f"Самолеты из стран: {', '.join(countries)}")

        elif choice == "4":
            # Показать все сохраненные
            aircraft_list = storage.get_all()
            if not aircraft_list:
                print("Нет сохраненных данных о самолетах")
                continue

            print_aircraft_list(aircraft_list, "Все сохраненные самолеты")
            print(f"Всего записей: {storage.count()}")

        elif choice == "5":
            # Дополнительные фильтры
            print("\n--- Дополнительные фильтры ---")
            print("1. Фильтр по диапазону высот")
            print("2. Сортировка по скорости")
            print("3. Самолеты в воздухе/на земле")
            print("4. Поиск по позывному")

            sub_choice = input("Выберите действие: ").strip()

            aircraft_list = storage.get_all()
            if not aircraft_list:
                print("Нет данных. Сначала получите информацию о самолетах.")
                continue

            if sub_choice == "1":
                # Фильтр по высоте
                range_str = input("Введите диапазон высот (мин - макс): ").strip()
                min_alt, max_alt = parse_altitude_range(range_str)
                filtered = filter_by_altitude_range(aircraft_list, min_alt, max_alt)
                print_aircraft_list(
                    filtered, f"Самолеты на высоте {min_alt}-{max_alt} м"
                )

            elif sub_choice == "2":
                # Сортировка по скорости
                sorted_list = sort_by_velocity(aircraft_list)
                print_aircraft_list(sorted_list[:20], "Топ 20 по скорости")

            elif sub_choice == "3":
                # В воздухе или на земле
                print("1. В воздухе")
                print("2. На земле")
                status_choice = input("Выберите статус: ").strip()

                if status_choice == "1":
                    in_air = [a for a in aircraft_list if not a._on_ground]
                    print_aircraft_list(in_air, "Самолеты в воздухе")
                elif status_choice == "2":
                    on_ground = [a for a in aircraft_list if a._on_ground]
                    print_aircraft_list(on_ground, "Самолеты на земле")

            elif sub_choice == "4":
                # Поиск по позывному
                callsign = input("Введите позывной: ").strip().upper()
                found = [a for a in aircraft_list if callsign in a.callsign]
                print_aircraft_list(
                    found, f"Результаты поиска по позывному '{callsign}'"
                )

            else:
                print("Неверный выбор")

        else:
            print("Неверный выбор. Пожалуйста, выберите 0-5.")

        input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    user_interaction()
