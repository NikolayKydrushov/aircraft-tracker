from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import requests


class BaseAPI(ABC):
    """
    Абстрактный класс, определяющий интерфейс для всех API-классов
    """

    def __init__(self, base_url: str):
        """
        Инициализация базового API класса

        Args:
            base_url: Базовый URL API
        """
        self.base_url = base_url
        self.session = requests.Session()

    @abstractmethod
    def get_data(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """
        Абстрактный метод для получения данных от API

        Args:
            endpoint: Конечная точка API
            params: Параметры запроса

        Returns:
            Данные от API
        """
        pass

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Вспомогательный метод для выполнения HTTP запросов

        Args:
            endpoint: Конечная точка API
            params: Параметры запроса

        Returns:
            JSON ответ от API
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()  # Проверка на HTTP ошибки
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API: {e}")
            return {}
        except ValueError as e:
            print(f"Ошибка при парсинге JSON: {e}")
            return {}
