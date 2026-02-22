from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.models.aircraft import Aircraft


class BaseStorage(ABC):
    """
    Абстрактный класс, определяющий интерфейс для всех хранилищ
    """

    @abstractmethod
    def add_aircraft(self, aircraft: Aircraft) -> bool:
        """
        Добавление информации о самолете в хранилище

        Args:
            aircraft: Объект самолета

        Returns:
            True если успешно, False в противном случае
        """
        pass

    @abstractmethod
    def add_multiple_aircraft(self, aircraft_list: List[Aircraft]) -> int:
        """
        Добавление нескольких самолетов в хранилище

        Args:
            aircraft_list: Список объектов самолетов

        Returns:
            Количество успешно добавленных самолетов
        """
        pass

    @abstractmethod
    def get_aircraft(self, criteria: Optional[Dict[str, Any]] = None) -> List[Aircraft]:
        """
        Получение списка самолетов по критериям

        Args:
            criteria: Словарь с критериями фильтрации

        Returns:
            Список объектов самолетов
        """
        pass

    @abstractmethod
    def delete_aircraft(self, callsign: str) -> bool:
        """
        Удаление самолета по позывному

        Args:
            callsign: Позывной самолета

        Returns:
            True если удален, False если не найден
        """
        pass

    @abstractmethod
    def get_all(self) -> List[Aircraft]:
        """
        Получение всех самолетов из хранилища

        Returns:
            Список всех самолетов
        """
        pass

    @abstractmethod
    def clear(self) -> bool:
        """
        Очистка хранилища

        Returns:
            True если успешно
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Получение количества самолетов в хранилище

        Returns:
            Количество самолетов
        """
        pass
