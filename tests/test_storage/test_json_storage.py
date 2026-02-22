import pytest
import json
import os
from src.models.aircraft import Aircraft
from src.storage.json_storage import JSONStorage


class TestJSONStorage:
    """Тесты для JSONStorage"""

    def test_initialization(self, temp_json_file):
        """Тест инициализации"""
        storage = JSONStorage(temp_json_file)

        assert storage._file_path == temp_json_file
        assert os.path.exists(temp_json_file)

    def test_add_aircraft(self, json_storage, sample_aircraft):
        """Тест добавления самолета"""
        result = json_storage.add_aircraft(sample_aircraft)

        assert result is True
        assert json_storage.count() == 1

        # Проверяем содержимое файла
        with open(json_storage._file_path, 'r') as f:
            data = json.load(f)
            assert len(data) == 1
            assert data[0]['callsign'] == sample_aircraft.callsign

    def test_add_duplicate_aircraft(self, json_storage, sample_aircraft):
        """Тест добавления дубликата самолета"""
        json_storage.add_aircraft(sample_aircraft)

        # Создаем самолет с тем же callsign, но другими данными
        duplicate = Aircraft(
            sample_aircraft.callsign,
            "New Country",
            500.0,
            20000.0
        )

        result = json_storage.add_aircraft(duplicate)
        assert result is True
        assert json_storage.count() == 1

        # Проверяем, что данные обновились
        aircraft_list = json_storage.get_all()
        assert aircraft_list[0].origin_country == "New Country"
        assert aircraft_list[0].velocity == 500.0

    def test_add_multiple_aircraft(self, json_storage, sample_aircraft_list):
        """Тест добавления нескольких самолетов"""
        aircraft_list = Aircraft.cast_to_object_list(sample_aircraft_list)

        added = json_storage.add_multiple_aircraft(aircraft_list)

        assert added == 3
        assert json_storage.count() == 3

    def test_get_all_aircraft(self, json_storage, sample_aircraft_list):
        """Тест получения всех самолетов"""
        aircraft_list = Aircraft.cast_to_object_list(sample_aircraft_list)
        json_storage.add_multiple_aircraft(aircraft_list)

        result = json_storage.get_all()

        assert len(result) == 3
        assert all(isinstance(a, Aircraft) for a in result)

    def test_get_aircraft_by_criteria(self, json_storage, sample_aircraft_list):
        """Тест получения самолетов по критериям"""
        aircraft_list = Aircraft.cast_to_object_list(sample_aircraft_list)
        json_storage.add_multiple_aircraft(aircraft_list)

        # Поиск по стране
        result = json_storage.get_aircraft({'origin_country': 'Russia'})
        assert len(result) == 1
        assert result[0].callsign == 'AFL101'

        # Поиск по статусу на земле
        result = json_storage.get_aircraft({'on_ground': True})
        assert len(result) == 1
        assert result[0].callsign == 'BAW303'

    def test_get_aircraft_by_country(self, json_storage, sample_aircraft_list):
        """Тест получения самолетов по стране"""
        aircraft_list = Aircraft.cast_to_object_list(sample_aircraft_list)
        json_storage.add_multiple_aircraft(aircraft_list)

        result = json_storage.get_aircraft_by_country('United States')

        assert len(result) == 1
        assert result[0].callsign == 'UAL202'

    def test_get_top_by_altitude(self, json_storage, sample_aircraft_list):
        """Тест получения топа по высоте"""
        aircraft_list = Aircraft.cast_to_object_list(sample_aircraft_list)
        json_storage.add_multiple_aircraft(aircraft_list)

        top2 = json_storage.get_top_by_altitude(2)

        assert len(top2) == 2
        assert top2[0].altitude >= top2[1].altitude

    def test_delete_aircraft(self, json_storage, sample_aircraft_list):
        """Тест удаления самолета"""
        aircraft_list = Aircraft.cast_to_object_list(sample_aircraft_list)
        json_storage.add_multiple_aircraft(aircraft_list)

        result = json_storage.delete_aircraft('AFL101')

        assert result is True
        assert json_storage.count() == 2

        # Проверяем, что удалился правильный
        remaining = json_storage.get_all()
        callsigns = [a.callsign for a in remaining]
        assert 'AFL101' not in callsigns
        assert 'UAL202' in callsigns
        assert 'BAW303' in callsigns

    def test_delete_nonexistent_aircraft(self, json_storage, sample_aircraft_list):
        """Тест удаления несуществующего самолета"""
        aircraft_list = Aircraft.cast_to_object_list(sample_aircraft_list)
        json_storage.add_multiple_aircraft(aircraft_list)

        result = json_storage.delete_aircraft('NONEXISTENT')

        assert result is False
        assert json_storage.count() == 3

    def test_clear_storage(self, json_storage, sample_aircraft_list):
        """Тест очистки хранилища"""
        aircraft_list = Aircraft.cast_to_object_list(sample_aircraft_list)
        json_storage.add_multiple_aircraft(aircraft_list)

        result = json_storage.clear()

        assert result is True
        assert json_storage.count() == 0

    def test_count(self, json_storage, sample_aircraft_list):
        """Тест подсчета количества"""
        assert json_storage.count() == 0

        aircraft_list = Aircraft.cast_to_object_list(sample_aircraft_list)
        json_storage.add_multiple_aircraft(aircraft_list)

        assert json_storage.count() == 3

    def test_file_creation(self, temp_json_file):
        """Тест создания файла при инициализации"""
        # Удаляем файл, если он существует
        if os.path.exists(temp_json_file):
            os.unlink(temp_json_file)

        storage = JSONStorage(temp_json_file)

        assert os.path.exists(temp_json_file)
        with open(temp_json_file, 'r') as f:
            data = json.load(f)
            assert data == []

    def test_load_invalid_json(self, temp_json_file):
        """Тест загрузки поврежденного JSON"""
        with open(temp_json_file, 'w') as f:
            f.write("invalid json")

        storage = JSONStorage(temp_json_file)
        data = storage._load_data()

        assert data == []
