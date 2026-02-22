import pytest
from src.utils.validators import (
    validate_country,
    validate_altitude,
    validate_velocity,
    validate_coordinates,
    parse_altitude_range
)


class TestValidators:
    """Тесты для функций валидации"""

    def test_validate_country(self):
        """Тест валидации названия страны"""
        # Валидные названия
        assert validate_country("Russia") is True
        assert validate_country("United States") is True
        assert validate_country("Россия") is True

        # Невалидные названия
        assert validate_country("") is False
        assert validate_country("123") is False
        assert validate_country(None) is False
        assert validate_country(123) is False

    def test_validate_altitude(self):
        """Тест валидации высоты"""
        # Валидные значения
        assert validate_altitude(10000) is True
        assert validate_altitude(0) is True
        assert validate_altitude(-500) is True  # Ниже уровня моря
        assert validate_altitude(45000) is True

        # Граничные значения
        assert validate_altitude(-1000) is True
        assert validate_altitude(50000) is True

        # Невалидные значения
        assert validate_altitude(-1001) is False
        assert validate_altitude(50001) is False
        assert validate_altitude("invalid") is False
        assert validate_altitude(None) is False

    def test_validate_velocity(self):
        """Тест валидации скорости"""
        # Валидные значения
        assert validate_velocity(0) is True
        assert validate_velocity(250) is True
        assert validate_velocity(1000) is True

        # Невалидные значения
        assert validate_velocity(-1) is False
        assert validate_velocity(1001) is False
        assert validate_velocity("invalid") is False
        assert validate_velocity(None) is False

    def test_validate_coordinates(self):
        """Тест валидации координат"""
        # Валидные координаты
        assert validate_coordinates(55.75, 37.62) is True
        assert validate_coordinates(0, 0) is True
        assert validate_coordinates(-90, -180) is True
        assert validate_coordinates(90, 180) is True

        # Невалидные координаты
        assert validate_coordinates(91, 37.62) is False
        assert validate_coordinates(-91, 37.62) is False
        assert validate_coordinates(55.75, 181) is False
        assert validate_coordinates(55.75, -181) is False
        assert validate_coordinates("invalid", 37.62) is False

    def test_parse_altitude_range(self):
        """Тест парсинга диапазона высот"""
        # Валидные строки
        min_alt, max_alt = parse_altitude_range("1000 - 5000")
        assert min_alt == 1000.0
        assert max_alt == 5000.0

        # С пробелами
        min_alt, max_alt = parse_altitude_range("1000-5000")
        assert min_alt == 1000.0
        assert max_alt == 5000.0

        # Невалидные строки - возвращаем значения по умолчанию
        min_alt, max_alt = parse_altitude_range("invalid")
        assert min_alt == 0.0
        assert max_alt == 50000.0

        min_alt, max_alt = parse_altitude_range("")
        assert min_alt == 0.0
        assert max_alt == 50000.0

        min_alt, max_alt = parse_altitude_range(None)
        assert min_alt == 0.0
        assert max_alt == 50000.0
