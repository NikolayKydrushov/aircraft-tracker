from dataclasses import dataclass


@dataclass
class Config:
    """
    Класс с настройками проекта
    """

    # Пути к файлам
    DATA_DIR: str = "data"
    AIRCRAFT_DATA_FILE: str = "data/aircraft_data.json"

    # Настройки API
    NOMINIMAT_URL: str = "https://nominatim.openstreetmap.org"
    OPENSKY_URL: str = "https://opensky-network.org/api"

    # Таймауты запросов (секунды)
    REQUEST_TIMEOUT: int = 10

    # Лимиты для вывода
    DEFAULT_TOP_N: int = 10
    MAX_TOP_N: int = 50

    # Настройки кэширования
    ENABLE_CACHING: bool = True
    CACHE_TTL: int = 300  # 5 минут

    # Настройки валидации
    MAX_ALTITUDE: float = 50000.0  # метров
    MIN_ALTITUDE: float = -1000.0  # метров
    MAX_VELOCITY: float = 1000.0  # м/с

    @classmethod
    def get_instance(cls):
        """Синглтон для получения экземпляра конфигурации"""
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance
