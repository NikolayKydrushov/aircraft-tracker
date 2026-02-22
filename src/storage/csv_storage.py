import csv
import os
from typing import List, Optional, Dict, Any
from src.storage.base import BaseStorage
from src.models.aircraft import Aircraft


class CSVStorage(BaseStorage):
    """
    Класс для работы с CSV файлом как хранилищем данных о самолетах

    CSV формат удобен тем, что:
    1. Можно открыть в Excel для просмотра
    2. Легко читается человеком
    3. Занимает меньше места чем JSON
    4. Поддерживается многими программами
    """

    __slots__ = ('_file_path',)  # Экономия памяти

    def __init__(self, file_path: str = "data/aircraft_data.csv"):
        """
        Инициализация CSV хранилища

        Args:
            file_path: Путь к CSV файлу (по умолчанию data/aircraft_data.csv)
        """
        self._file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """
        Проверка существования файла и создание при необходимости
        Создает директорию и файл с заголовками, если их нет
        """
        # Создаем директорию, если её нет
        directory = os.path.dirname(self._file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Создана директория: {directory}")

        # Создаем файл с заголовками, если его нет
        if not os.path.exists(self._file_path):
            with open(self._file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Записываем заголовки столбцов
                writer.writerow([
                    'callsign',  # Позывной
                    'origin_country',  # Страна регистрации
                    'velocity',  # Скорость (м/с)
                    'altitude',  # Высота (м)
                    'icao24',  # ICAO24 код
                    'longitude',  # Долгота
                    'latitude',  # Широта
                    'on_ground',  # На земле?
                    'vertical_rate'  # Вертикальная скорость
                ])
            print(f"Создан CSV файл: {self._file_path}")

    def _aircraft_to_row(self, aircraft: Aircraft) -> Dict[str, Any]:
        """
        Преобразование объекта Aircraft в словарь для CSV

        Args:
            aircraft: Объект самолета

        Returns:
            Словарь с данными для записи в CSV
        """
        return {
            'callsign': aircraft.callsign,
            'origin_country': aircraft.origin_country,
            'velocity': f"{aircraft.velocity:.2f}",  # Форматируем с 2 знаками
            'altitude': f"{aircraft.altitude:.2f}",
            'icao24': getattr(aircraft, '_icao24', 'Unknown'),
            'longitude': f"{getattr(aircraft, '_longitude', 0.0):.6f}",
            'latitude': f"{getattr(aircraft, '_latitude', 0.0):.6f}",
            'on_ground': str(getattr(aircraft, '_on_ground', True)),
            'vertical_rate': f"{getattr(aircraft, '_vertical_rate', 0.0):.2f}"
        }

    def _row_to_aircraft(self, row: Dict[str, str]) -> Aircraft:
        """
        Преобразование строки из CSV в объект Aircraft

        Args:
            row: Словарь с данными из CSV

        Returns:
            Объект Aircraft
        """
        # Преобразуем строки в нужные типы
        return Aircraft(
            callsign=row['callsign'],
            origin_country=row['origin_country'],
            velocity=float(row['velocity']),
            altitude=float(row['altitude']),
            icao24=row['icao24'],
            longitude=float(row['longitude']),
            latitude=float(row['latitude']),
            on_ground=row['on_ground'].lower() == 'true',
            vertical_rate=float(row['vertical_rate'])
        )

    def _load_data(self) -> List[Dict[str, Any]]:
        """
        Загрузка данных из CSV файла

        Returns:
            Список словарей с данными о самолетах
        """
        data = []
        try:
            with open(self._file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Пропускаем пустые строки
                    if any(row.values()):
                        data.append(row)
            print(f"Загружено {len(data)} записей из CSV")
        except FileNotFoundError:
            print(f"Файл {self._file_path} не найден")
        except csv.Error as e:
            print(f"Ошибка при чтении CSV: {e}")

        return data

    def _save_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Сохранение данных в CSV файл

        Args:
            data: Список словарей для сохранения

        Returns:
            True если успешно, False в случае ошибки
        """
        try:
            with open(self._file_path, 'w', newline='', encoding='utf-8') as f:
                if data:
                    # Используем ключи первого словаря как заголовки
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                else:
                    # Если данных нет, создаем файл только с заголовками
                    writer = csv.writer(f)
                    writer.writerow([
                        'callsign', 'origin_country', 'velocity', 'altitude',
                        'icao24', 'longitude', 'latitude', 'on_ground', 'vertical_rate'
                    ])
            print(f"Сохранено {len(data)} записей в CSV")
            return True
        except IOError as e:
            print(f"Ошибка при сохранении CSV файла: {e}")
            return False

    def add_aircraft(self, aircraft: Aircraft) -> bool:
        """
        Добавление самолета в хранилище

        Args:
            aircraft: Объект самолета
        """
        # Загружаем существующие данные
        data = self._load_data()

        # Преобразуем самолет в словарь для CSV
        new_row = self._aircraft_to_row(aircraft)

        # Проверяем, есть ли уже такой самолет (по callsign)
        found = False
        for i, existing in enumerate(data):
            if existing.get('callsign') == aircraft.callsign:
                # Обновляем существующую запись
                data[i] = new_row
                found = True
                print(f"Обновлен самолет {aircraft.callsign}")
                break

        if not found:
            # Добавляем новую запись
            data.append(new_row)
            print(f"Добавлен новый самолет {aircraft.callsign}")

        # Сохраняем все данные
        return self._save_data(data)

    def add_multiple_aircraft(self, aircraft_list: List[Aircraft]) -> int:
        """
        Добавление нескольких самолетов

        Args:
            aircraft_list: Список самолетов

        Returns:
            Количество добавленных/обновленных самолетов
        """
        if not aircraft_list:
            return 0

        # Загружаем существующие данные
        data = self._load_data()

        # Создаем словарь для быстрого поиска по callsign
        existing_dict = {row['callsign']: i for i, row in enumerate(data)}

        added_count = 0
        for aircraft in aircraft_list:
            new_row = self._aircraft_to_row(aircraft)

            if aircraft.callsign in existing_dict:
                # Обновляем существующую запись
                data[existing_dict[aircraft.callsign]] = new_row
            else:
                # Добавляем новую запись
                data.append(new_row)
                existing_dict[aircraft.callsign] = len(data) - 1
            added_count += 1

        # Сохраняем все данные
        self._save_data(data)
        return added_count

    def get_aircraft(self, criteria: Optional[Dict[str, Any]] = None) -> List[Aircraft]:
        """
        Получение самолетов по критериям

        Args:
            criteria: Критерии фильтрации (например, {'origin_country': 'Russia'})

        Returns:
            Список объектов самолетов
        """
        data = self._load_data()

        if not criteria:
            # Возвращаем все
            return [self._row_to_aircraft(row) for row in data]

        # Фильтруем по критериям
        filtered_data = []
        for row in data:
            match = True
            for key, value in criteria.items():
                # Преобразуем значение из строки в нужный тип для сравнения
                row_value = row.get(key)
                if key in ['velocity', 'altitude', 'longitude', 'latitude', 'vertical_rate']:
                    try:
                        row_value = float(row_value) if row_value else 0.0
                    except (ValueError, TypeError):
                        row_value = 0.0
                elif key == 'on_ground':
                    row_value = row_value.lower() == 'true' if row_value else False

                if row_value != value:
                    match = False
                    break
            if match:
                filtered_data.append(self._row_to_aircraft(row))

        return filtered_data

    def get_aircraft_by_country(self, country: str) -> List[Aircraft]:
        """
        Получение самолетов по стране регистрации

        Args:
            country: Название страны
        """
        return self.get_aircraft({'origin_country': country})

    def get_top_by_altitude(self, n: int) -> List[Aircraft]:
        """
        Получение топ N самолетов по высоте

        Args:
            n: Количество самолетов
        """
        aircraft_list = self.get_all()
        # Сортируем по высоте (от большей к меньшей)
        sorted_aircraft = sorted(aircraft_list,
                                 key=lambda a: a.altitude,
                                 reverse=True)
        return sorted_aircraft[:n]

    def delete_aircraft(self, callsign: str) -> bool:
        """
        Удаление самолета по позывному

        Args:
            callsign: Позывной самолета

        Returns:
            True если удален, False если не найден
        """
        data = self._load_data()

        # Фильтруем, удаляя самолет с указанным позывным
        new_data = [row for row in data if row.get('callsign') != callsign]

        if len(new_data) < len(data):
            self._save_data(new_data)
            print(f"Удален самолет {callsign}")
            return True

        print(f"Самолет {callsign} не найден")
        return False

    def get_all(self) -> List[Aircraft]:
        """Получение всех самолетов"""
        return self.get_aircraft()

    def clear(self) -> bool:
        """Очистка хранилища"""
        return self._save_data([])

    def count(self) -> int:
        """Количество самолетов в хранилище"""
        return len(self._load_data())
