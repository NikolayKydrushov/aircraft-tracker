from typing import Any, Dict, List, Optional, Tuple

import requests

from src.api.base import BaseAPI


class AircraftAPI(BaseAPI):
    """
    Класс для работы с API самолетов и геоданными
    Наследуется от BaseAPI
    """

    # Константы с URL API
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    OPENSKY_URL = "https://opensky-network.org/api/states/all"

    def __init__(self):
        """Инициализация API для работы с самолетами"""
        # Для OpenSky API (основной)
        super().__init__(self.OPENSKY_URL)

        # Для Nominatim API сохраняем URL отдельно
        self._nominatim_url = self.NOMINATIM_URL
        self._session = requests.Session()

        # Переменная для хранения результатов (как в примере)
        self.aeroplanes = None

    def get_data(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> Any:
        """
        Реализация абстрактного метода получения данных
        """
        if "nominatim" in endpoint or endpoint == "nominatim":
            url = self._nominatim_url
        else:
            url = f"{self.base_url}?{endpoint}" if endpoint else self.base_url

        try:
            response = self._session.get(
                url, params=params, headers=headers, timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API: {e}")
            return {}
        except ValueError as e:
            print(f"Ошибка при парсинге JSON: {e}")
            return {}

    def get_aeroplanes(self, country: str) -> None:
        """
        Получение информации о самолетах в воздушном пространстве страны
        (Метод, соответствующий примеру из задания)

        Args:
            country: Название страны
        """
        # Заголовки для Nominatim API (обязательный параметр)
        headers_nominatim = {
            "User-Agent": "aircraft-tracker/1.0",  # Можно любое название
        }

        # Параметры для получения координат страны
        params_nominatim = {
            "country": country,
            "format": "json",
            "limit": 1,
        }

        # Получаем координаты страны
        response = self._session.get(
            url=self._nominatim_url, params=params_nominatim, headers=headers_nominatim
        )

        data = response.json()

        if not data or len(data) == 0:
            print(f"Страна '{country}' не найдена")
            self.aeroplanes = {"states": []}
            return

        # Извлекаем boundingbox
        geo_coordinates = data[0].get("boundingbox")

        if not geo_coordinates or len(geo_coordinates) < 4:
            print(f"Не удалось получить координаты для страны '{country}'")
            self.aeroplanes = {"states": []}
            return

        # Параметры для фильтрации самолетов по координатам
        params = {
            "lamin": geo_coordinates[0],
            "lamax": geo_coordinates[1],
            "lomin": geo_coordinates[2],
            "lomax": geo_coordinates[3],
        }

        # Получаем информацию о самолетах
        response = self._session.get(url=self.base_url, params=params)

        # Сохраняем результат
        self.aeroplanes = response.json()

    def get_country_boundingbox(
        self, country_name: str
    ) -> Optional[Tuple[float, float, float, float]]:
        """
        Получение координат bounding box для страны через Nominatim API

        Args:
            country_name: Название страны

        Returns:
            Кортеж (south, north, west, east) или None если страна не найдена
        """
        headers_nominatim = {
            "User-Agent": "aircraft-tracker/1.0",
        }

        params_nominatim = {
            "country": country_name,
            "format": "json",
            "limit": 1,
        }

        response = self._session.get(
            url=self._nominatim_url, params=params_nominatim, headers=headers_nominatim
        )

        data = response.json()

        if data and len(data) > 0:
            boundingbox = data[0].get("boundingbox", [])
            if len(boundingbox) == 4:
                south, north, west, east = map(float, boundingbox)
                return (south, north, west, east)

        print(f"Страна '{country_name}' не найдена")
        return None

    def get_aircraft_in_area(
        self, south: float, north: float, west: float, east: float
    ) -> List[Dict[str, Any]]:
        """
        Получение информации о самолетах в заданной области через OpenSky API

        Args:
            south: Южная широта
            north: Северная широта
            west: Западная долгота
            east: Восточная долгота

        Returns:
            Список самолетов в области
        """
        params = {
            "lamin": south,
            "lamax": north,
            "lomin": west,
            "lomax": east,
        }

        response = self._session.get(url=self.base_url, params=params)
        data = response.json()

        if data and "states" in data:
            return data["states"]

        return []

    def get_aircraft_by_country(self, country_name: str) -> List[Dict[str, Any]]:
        """
        Получение всех самолетов в воздушном пространстве страны

        Args:
            country_name: Название страны

        Returns:
            Список самолетов в стране
        """
        # Используем метод get_aeroplanes для совместимости с примером
        self.get_aeroplanes(country_name)

        if self.aeroplanes and "states" in self.aeroplanes:
            return self.aeroplanes["states"]

        return []

    def process_aircraft_data(self, raw_data: List[List[Any]]) -> List[Dict[str, Any]]:
        """
        Обработка сырых данных от OpenSky API в удобный формат

        Args:
            raw_data: Сырые данные от API (список списков)

        Returns:
            Список словарей с информацией о самолетах
        """
        processed = []

        for state in raw_data:
            if len(state) >= 14:
                aircraft = {
                    "icao24": state[0],
                    "callsign": state[1].strip() if state[1] else "Unknown",
                    "origin_country": state[2] if state[2] else "Unknown",
                    "longitude": state[5],
                    "latitude": state[6],
                    "altitude": state[7] if state[7] is not None else 0.0,
                    "on_ground": state[8],
                    "velocity": state[9] if state[9] is not None else 0.0,
                    "true_track": state[10],
                    "vertical_rate": state[11] if state[11] is not None else 0.0,
                    "geo_altitude": state[13] if state[13] is not None else 0.0,
                }
                processed.append(aircraft)

        return processed
