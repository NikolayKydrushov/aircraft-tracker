from typing import Any, Dict, List, Optional


class Aircraft:
    """
    Класс, представляющий самолет с его характеристиками
    Реализует принципы инкапсуляции и методы сравнения
    """

    __slots__ = (
        "_callsign",
        "_origin_country",
        "_velocity",
        "_altitude",
        "_icao24",
        "_longitude",
        "_latitude",
        "_on_ground",
        "_vertical_rate",
    )

    def __init__(
        self,
        callsign: str,
        origin_country: str,
        velocity: float,
        altitude: float,
        **kwargs,
    ):
        """
        Инициализация объекта самолета

        Args:
            callsign: Позывной самолета
            origin_country: Страна регистрации
            velocity: Скорость (м/с)
            altitude: Высота (метры)
            **kwargs: Дополнительные параметры
        """
        # Приватные атрибуты (инкапсуляция)
        self._callsign = self._validate_callsign(callsign)
        self._origin_country = self._validate_country(origin_country)
        self._velocity = self._validate_velocity(velocity)
        self._altitude = self._validate_altitude(altitude)

        # Дополнительные атрибуты
        self._icao24 = kwargs.get("icao24", "Unknown")
        self._longitude = kwargs.get("longitude", 0.0)
        self._latitude = kwargs.get("latitude", 0.0)
        self._on_ground = kwargs.get("on_ground", True)
        self._vertical_rate = kwargs.get("vertical_rate", 0.0)

    # Свойства для доступа к приватным атрибутам
    @property
    def callsign(self) -> str:
        """Геттер для позывного"""
        return self._callsign

    @property
    def origin_country(self) -> str:
        """Геттер для страны регистрации"""
        return self._origin_country

    @property
    def velocity(self) -> float:
        """Геттер для скорости"""
        return self._velocity

    @velocity.setter
    def velocity(self, value: float):
        """Сеттер для скорости с валидацией"""
        self._velocity = self._validate_velocity(value)

    @property
    def altitude(self) -> float:
        """Геттер для высоты"""
        return self._altitude

    @altitude.setter
    def altitude(self, value: float):
        """Сеттер для высоты с валидацией"""
        self._altitude = self._validate_altitude(value)

    @property
    def icao24(self) -> str:
        """Геттер для ICAO24 кода"""
        return self._icao24

    @property
    def position(self) -> tuple:
        """Геттер для позиции (долгота, широта)"""
        return (self._longitude, self._latitude)

    # Методы валидации
    def _validate_callsign(self, value: str) -> str:
        """Валидация позывного"""
        if not value or not isinstance(value, str):
            return "Unknown"
        return value.strip()

    def _validate_country(self, value: str) -> str:
        """Валидация страны"""
        if not value or not isinstance(value, str):
            return "Unknown"
        return value.strip()

    def _validate_velocity(self, value: float) -> float:
        """Валидация скорости"""
        try:
            val = float(value)
            return max(0.0, val)  # Скорость не может быть отрицательной
        except (TypeError, ValueError):
            return 0.0

    def _validate_altitude(self, value: float) -> float:
        """Валидация высоты"""
        try:
            val = float(value)
            return max(
                -1000.0, val
            )  # Высота может быть отрицательной (ниже уровня моря)
        except (TypeError, ValueError):
            return 0.0

    # Методы сравнения
    def __lt__(self, other: "Aircraft") -> bool:
        """
        Меньше чем (по скорости)

        Args:
            other: Другой самолет для сравнения
        """
        if not isinstance(other, Aircraft):
            return NotImplemented
        return self.velocity < other.velocity

    def __le__(self, other: "Aircraft") -> bool:
        """Меньше или равно (по скорости)"""
        if not isinstance(other, Aircraft):
            return NotImplemented
        return self.velocity <= other.velocity

    def __gt__(self, other: "Aircraft") -> bool:
        """Больше чем (по скорости)"""
        if not isinstance(other, Aircraft):
            return NotImplemented
        return self.velocity > other.velocity

    def __ge__(self, other: "Aircraft") -> bool:
        """Больше или равно (по скорости)"""
        if not isinstance(other, Aircraft):
            return NotImplemented
        return self.velocity >= other.velocity

    def __eq__(self, other: object) -> bool:
        """Равно (по всем основным атрибутам)"""
        if not isinstance(other, Aircraft):
            return False
        return (
            self.callsign == other.callsign
            and self.origin_country == other.origin_country
            and abs(self.velocity - other.velocity) < 0.1
            and abs(self.altitude - other.altitude) < 1.0
        )

    # Дополнительные методы сравнения по высоте
    def higher_than(self, other: "Aircraft") -> bool:
        """Сравнение по высоте (выше чем)"""
        if not isinstance(other, Aircraft):
            return NotImplemented
        return self.altitude > other.altitude

    def faster_than(self, other: "Aircraft") -> bool:
        """Сравнение по скорости (быстрее чем)"""
        if not isinstance(other, Aircraft):
            return NotImplemented
        return self.velocity > other.velocity

    # Классовые методы для создания объектов
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Aircraft":
        """
        Создание объекта самолета из словаря

        Args:
            data: Словарь с данными о самолете
        """
        return cls(
            callsign=data.get("callsign", "Unknown"),
            origin_country=data.get("origin_country", "Unknown"),
            velocity=data.get("velocity", 0.0),
            altitude=data.get("altitude", 0.0),
            icao24=data.get("icao24", "Unknown"),
            longitude=data.get("longitude", 0.0),
            latitude=data.get("latitude", 0.0),
            on_ground=data.get("on_ground", True),
            vertical_rate=data.get("vertical_rate", 0.0),
        )

    @classmethod
    def cast_to_object_list(cls, data_list: List[Dict[str, Any]]) -> List["Aircraft"]:
        """
        Преобразование списка словарей в список объектов Aircraft

        Args:
            data_list: Список словарей с данными о самолетах
        """
        return [cls.from_dict(data) for data in data_list]

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразование объекта в словарь для сохранения
        """
        return {
            "callsign": self.callsign,
            "origin_country": self.origin_country,
            "velocity": self.velocity,
            "altitude": self.altitude,
            "icao24": self._icao24,
            "longitude": self._longitude,
            "latitude": self._latitude,
            "on_ground": self._on_ground,
            "vertical_rate": self._vertical_rate,
        }

    def __str__(self) -> str:
        """Строковое представление самолета"""
        status = "на земле" if self._on_ground else "в воздухе"
        return (
            f"{self.callsign} ({self.origin_country}) | "
            f"Скорость: {self.velocity:.1f} м/с | "
            f"Высота: {self.altitude:.0f} м | {status}"
        )

    def __repr__(self) -> str:
        """Представление для отладки"""
        return f"Aircraft(callsign='{self.callsign}', country='{self.origin_country}')"
