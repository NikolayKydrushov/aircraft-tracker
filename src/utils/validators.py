from typing import Tuple, Union


def validate_country(country: str) -> bool:
    """
    Валидация названия страны

    Args:
        country: Название страны
    """
    if not country or not isinstance(country, str):
        return False

    country = country.strip()
    # Проверяем, что название не пустое и не состоит только из цифр
    return len(country) > 0 and not country.isdigit()


def validate_altitude(altitude: Union[int, float]) -> bool:
    """
    Валидация высоты полета

    Args:
        altitude: Высота в метрах
    """
    try:
        alt = float(altitude)
        # Разрешаем небольшие отрицательные значения (ниже уровня моря)
        return -1000 <= alt <= 50000  # Максимальная высота ~50 км
    except (TypeError, ValueError):
        return False


def validate_velocity(velocity: Union[int, float]) -> bool:
    """
    Валидация скорости

    Args:
        velocity: Скорость в м/с
    """
    try:
        vel = float(velocity)
        # Скорость звука ~343 м/с, максимальная скорость самолетов ~1000 м/с
        return 0 <= vel <= 1000
    except (TypeError, ValueError):
        return False


def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Валидация географических координат

    Args:
        lat: Широта (-90 до 90)
        lon: Долгота (-180 до 180)
    """
    try:
        lat = float(lat)
        lon = float(lon)
        return -90 <= lat <= 90 and -180 <= lon <= 180
    except (TypeError, ValueError):
        return False


def parse_altitude_range(range_str: str) -> Tuple[float, float]:
    """
    Парсинг строки диапазона высот

    Args:
        range_str: Строка вида "min - max"
    """
    try:
        parts = range_str.split("-")
        if len(parts) == 2:
            min_alt = float(parts[0].strip())
            max_alt = float(parts[1].strip())
            return (min_alt, max_alt)
    except (ValueError, AttributeError):
        pass

    return (0.0, 50000.0)  # Значения по умолчанию
