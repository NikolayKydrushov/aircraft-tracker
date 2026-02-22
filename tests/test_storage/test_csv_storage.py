import pytest
import csv
import os
import tempfile
from src.models.aircraft import Aircraft
from src.storage.csv_storage import CSVStorage


@pytest.fixture
def temp_csv_file():
    """Фикстура для временного CSV файла"""
    fd, path = tempfile.mkstemp(suffix='.csv')
    os.close(fd)
    # Удаляем файл, чтобы тест создал его заново
    if os.path.exists(path):
        os.unlink(path)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def csv_storage(temp_csv_file):
    """Фикстура с CSV хранилищем"""
    return CSVStorage(temp_csv_file)


@pytest.fixture
def sample_aircraft_list():
    """Фикстура со списком самолетов"""
    return [
        Aircraft(
            callsign="AFL101",
            origin_country="Russia",
            velocity=280.5,
            altitude=11000.0,
            icao24="abc123",
            longitude=37.62,
            latitude=55.75,
            on_ground=False,
            vertical_rate=10.5
        ),
        Aircraft(
            callsign="UAL202",
            origin_country="United States",
            velocity=260.3,
            altitude=10500.0,
            icao24="def456",
            longitude=-73.94,
            latitude=40.69,
            on_ground=False,
            vertical_rate=8.2
        ),
        Aircraft(
            callsign="BAW303",
            origin_country="United Kingdom",
            velocity=240.1,
            altitude=9500.0,
            icao24="ghi789",
            longitude=-0.45,
            latitude=51.47,
            on_ground=True,
            vertical_rate=0.0
        )
    ]


class TestCSVStorage:
    """Тесты для CSVStorage"""

    def test_initialization(self, temp_csv_file):
        """Тест инициализации"""
        storage = CSVStorage(temp_csv_file)

        assert storage._file_path == temp_csv_file
        assert os.path.exists(temp_csv_file)

        # Проверяем, что файл содержит заголовки
        with open(temp_csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            assert 'callsign' in headers
            assert 'origin_country' in headers
            assert 'velocity' in headers
            assert 'altitude' in headers

    def test_aircraft_to_row(self, csv_storage, sample_aircraft_list):
        """Тест преобразования самолета в строку CSV"""
        aircraft = sample_aircraft_list[0]
        row = csv_storage._aircraft_to_row(aircraft)

        assert row['callsign'] == "AFL101"
        assert row['origin_country'] == "Russia"
        assert float(row['velocity']) == 280.5
        assert float(row['altitude']) == 11000.0
        assert row['icao24'] == "abc123"
        assert row['on_ground'] == "False"

    def test_row_to_aircraft(self, csv_storage):
        """Тест преобразования строки CSV в самолет"""
        row = {
            'callsign': 'TEST123',
            'origin_country': 'Russia',
            'velocity': '250.5',
            'altitude': '10000.0',
            'icao24': 'test123',
            'longitude': '37.62',
            'latitude': '55.75',
            'on_ground': 'False',
            'vertical_rate': '5.5'
        }

        aircraft = csv_storage._row_to_aircraft(row)

        assert aircraft.callsign == 'TEST123'
        assert aircraft.origin_country == 'Russia'
        assert aircraft.velocity == 250.5
        assert aircraft.altitude == 10000.0
        assert aircraft.icao24 == 'test123'
        assert aircraft.position[0] == 37.62
        assert aircraft.position[1] == 55.75

    def test_add_aircraft(self, csv_storage, sample_aircraft_list):
        """Тест добавления самолета"""
        aircraft = sample_aircraft_list[0]
        result = csv_storage.add_aircraft(aircraft)

        assert result is True
        assert csv_storage.count() == 1

        # Проверяем содержимое файла
        with open(csv_storage._file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]['callsign'] == 'AFL101'

    def test_add_duplicate_aircraft(self, csv_storage, sample_aircraft_list):
        """Тест добавления дубликата самолета"""
        aircraft = sample_aircraft_list[0]
        csv_storage.add_aircraft(aircraft)

        # Создаем самолет с тем же callsign, но другими данными
        duplicate = Aircraft(
            "AFL101",
            "New Country",
            500.0,
            20000.0,
            icao24="new123"
        )

        result = csv_storage.add_aircraft(duplicate)
        assert result is True
        assert csv_storage.count() == 1

        # Проверяем, что данные обновились
        aircraft_list = csv_storage.get_all()
        assert aircraft_list[0].origin_country == "New Country"
        assert aircraft_list[0].velocity == 500.0

    def test_add_multiple_aircraft(self, csv_storage, sample_aircraft_list):
        """Тест добавления нескольких самолетов"""
        added = csv_storage.add_multiple_aircraft(sample_aircraft_list)

        assert added == 3
        assert csv_storage.count() == 3

    def test_add_multiple_empty_list(self, csv_storage):
        """Тест добавления пустого списка"""
        added = csv_storage.add_multiple_aircraft([])

        assert added == 0
        assert csv_storage.count() == 0

    def test_get_all_aircraft(self, csv_storage, sample_aircraft_list):
        """Тест получения всех самолетов"""
        csv_storage.add_multiple_aircraft(sample_aircraft_list)

        result = csv_storage.get_all()

        assert len(result) == 3
        assert all(isinstance(a, Aircraft) for a in result)
        callsigns = [a.callsign for a in result]
        assert 'AFL101' in callsigns
        assert 'UAL202' in callsigns
        assert 'BAW303' in callsigns

    def test_get_aircraft_by_criteria(self, csv_storage, sample_aircraft_list):
        """Тест получения самолетов по критериям"""
        csv_storage.add_multiple_aircraft(sample_aircraft_list)

        # Поиск по стране
        result = csv_storage.get_aircraft({'origin_country': 'Russia'})
        assert len(result) == 1
        assert result[0].callsign == 'AFL101'

        # Поиск по статусу на земле
        result = csv_storage.get_aircraft({'on_ground': True})
        assert len(result) == 1
        assert result[0].callsign == 'BAW303'

    def test_get_aircraft_by_country(self, csv_storage, sample_aircraft_list):
        """Тест получения самолетов по стране"""
        csv_storage.add_multiple_aircraft(sample_aircraft_list)

        result = csv_storage.get_aircraft_by_country('United States')

        assert len(result) == 1
        assert result[0].callsign == 'UAL202'

    def test_get_top_by_altitude(self, csv_storage, sample_aircraft_list):
        """Тест получения топа по высоте"""
        csv_storage.add_multiple_aircraft(sample_aircraft_list)

        top2 = csv_storage.get_top_by_altitude(2)

        assert len(top2) == 2
        assert top2[0].altitude >= top2[1].altitude
        assert top2[0].callsign == 'AFL101'  # Самый высокий
        assert top2[1].callsign == 'UAL202'  # Второй по высоте

    def test_delete_aircraft(self, csv_storage, sample_aircraft_list):
        """Тест удаления самолета"""
        csv_storage.add_multiple_aircraft(sample_aircraft_list)

        result = csv_storage.delete_aircraft('AFL101')

        assert result is True
        assert csv_storage.count() == 2

        # Проверяем, что удалился правильный
        remaining = csv_storage.get_all()
        callsigns = [a.callsign for a in remaining]
        assert 'AFL101' not in callsigns
        assert 'UAL202' in callsigns
        assert 'BAW303' in callsigns

    def test_delete_nonexistent_aircraft(self, csv_storage, sample_aircraft_list):
        """Тест удаления несуществующего самолета"""
        csv_storage.add_multiple_aircraft(sample_aircraft_list)

        result = csv_storage.delete_aircraft('NONEXISTENT')

        assert result is False
        assert csv_storage.count() == 3

    def test_clear_storage(self, csv_storage, sample_aircraft_list):
        """Тест очистки хранилища"""
        csv_storage.add_multiple_aircraft(sample_aircraft_list)

        result = csv_storage.clear()

        assert result is True
        assert csv_storage.count() == 0

        # Проверяем, что файл содержит только заголовки
        with open(csv_storage._file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            rows = list(reader)
            assert len(rows) == 0

    def test_count(self, csv_storage, sample_aircraft_list):
        """Тест подсчета количества"""
        assert csv_storage.count() == 0

        csv_storage.add_multiple_aircraft(sample_aircraft_list)
        assert csv_storage.count() == 3

    def test_file_creation_with_directory(self):
        """Тест создания файла с директорией"""
        # Создаем путь с поддиректорией
        nested_path = os.path.join('test_data', 'nested', 'test.csv')

        try:
            storage = CSVStorage(nested_path)

            assert os.path.exists(nested_path)
        finally:
            # Очистка
            if os.path.exists(nested_path):
                os.remove(nested_path)
            if os.path.exists(os.path.join('test_data', 'nested')):
                os.rmdir(os.path.join('test_data', 'nested'))
            if os.path.exists('test_data'):
                os.rmdir('test_data')

    def test_load_empty_file(self, temp_csv_file):
        """Тест загрузки пустого файла"""
        # Создаем пустой файл без заголовков
        with open(temp_csv_file, 'w', encoding='utf-8') as f:
            f.write('')

        storage = CSVStorage(temp_csv_file)
        data = storage._load_data()

        assert data == []
