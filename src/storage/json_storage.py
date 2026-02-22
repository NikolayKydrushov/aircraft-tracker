import json
import os
from typing import Any, Dict, List, Optional

from src.models.aircraft import Aircraft
from src.storage.base import BaseStorage


class JSONStorage(BaseStorage):
    """
    Класс для работы с JSON файлом как хранилищем данных о самолетах
    """

    def __init__(self, file_path: str = "data/aircraft_data.json"):
        """
        Инициализация JSON хранилища

        Args:
            file_path: Путь к JSON файлу
        """
        self._file_path = file_path  # Приватный атрибут
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Проверка существования файла и создание при необходимости"""
        directory = os.path.dirname(self._file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        if not os.path.exists(self._file_path):
            self._save_data([])

    def _load_data(self) -> List[Dict[str, Any]]:
        """
        Загрузка данных из JSON файла

        Returns:
            Список словарей с данными о самолетах
        """
        try:
            with open(self._file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Сохранение данных в JSON файл

        Args:
            data: Список словарей для сохранения
        """
        try:
            with open(self._file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"Ошибка при сохранении файла: {e}")
            return False

    def add_aircraft(self, aircraft: Aircraft) -> bool:
        """
        Добавление самолета в хранилище

        Args:
            aircraft: Объект самолета
        """
        data = self._load_data()

        # Проверяем, нет ли уже такого самолета
        aircraft_dict = aircraft.to_dict()
        for existing in data:
            if existing.get("callsign") == aircraft.callsign:
                # Обновляем существующий
                existing.update(aircraft_dict)
                return self._save_data(data)

        # Добавляем новый
        data.append(aircraft_dict)
        return self._save_data(data)

    def add_multiple_aircraft(self, aircraft_list: List[Aircraft]) -> int:
        """
        Добавление нескольких самолетов

        Args:
            aircraft_list: Список самолетов
        """
        data = self._load_data()
        added_count = 0

        for aircraft in aircraft_list:
            aircraft_dict = aircraft.to_dict()
            found = False

            for existing in data:
                if existing.get("callsign") == aircraft.callsign:
                    existing.update(aircraft_dict)
                    found = True
                    added_count += 1
                    break

            if not found:
                data.append(aircraft_dict)
                added_count += 1

        self._save_data(data)
        return added_count

    def get_aircraft(self, criteria: Optional[Dict[str, Any]] = None) -> List[Aircraft]:
        """
        Получение самолетов по критериям

        Args:
            criteria: Критерии фильтрации
        """
        data = self._load_data()

        if not criteria:
            # Возвращаем все
            return Aircraft.cast_to_object_list(data)

        # Фильтруем по критериям
        filtered_data = []
        for item in data:
            match = True
            for key, value in criteria.items():
                if key not in item or item[key] != value:
                    match = False
                    break
            if match:
                filtered_data.append(item)

        return Aircraft.cast_to_object_list(filtered_data)

    def get_aircraft_by_country(self, country: str) -> List[Aircraft]:
        """
        Получение самолетов по стране регистрации

        Args:
            country: Название страны
        """
        return self.get_aircraft({"origin_country": country})

    def get_top_by_altitude(self, n: int) -> List[Aircraft]:
        """
        Получение топ N самолетов по высоте

        Args:
            n: Количество самолетов
        """
        aircraft_list = self.get_all()
        # Сортируем по высоте (от большей к меньшей)
        sorted_aircraft = sorted(aircraft_list, key=lambda a: a.altitude, reverse=True)
        return sorted_aircraft[:n]

    def delete_aircraft(self, callsign: str) -> bool:
        """
        Удаление самолета по позывному

        Args:
            callsign: Позывной самолета
        """
        data = self._load_data()

        # Фильтруем, удаляя самолет с указанным позывным
        new_data = [item for item in data if item.get("callsign") != callsign]

        if len(new_data) < len(data):
            return self._save_data(new_data)

        return False  # Самолет не найден

    def get_all(self) -> List[Aircraft]:
        """Получение всех самолетов"""
        return Aircraft.cast_to_object_list(self._load_data())

    def clear(self) -> bool:
        """Очистка хранилища"""
        return self._save_data([])

    def count(self) -> int:
        """Количество самолетов в хранилище"""
        return len(self._load_data())
