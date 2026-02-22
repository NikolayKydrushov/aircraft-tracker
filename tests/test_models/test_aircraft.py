import pytest
from src.models.aircraft import Aircraft


class TestAircraft:
    """Тесты для класса Aircraft"""

    def test_aircraft_creation(self, sample_aircraft_dict):
        """Тест создания объекта самолета"""
        aircraft = Aircraft.from_dict(sample_aircraft_dict)

        assert aircraft.callsign == sample_aircraft_dict['callsign']
        assert aircraft.origin_country == sample_aircraft_dict['origin_country']
        assert aircraft.velocity == sample_aircraft_dict['velocity']
        assert aircraft.altitude == sample_aircraft_dict['altitude']
        assert aircraft.icao24 == sample_aircraft_dict['icao24']

    def test_aircraft_creation_with_minimal_data(self):
        """Тест создания с минимальными данными"""
        aircraft = Aircraft("TEST", "Russia", 100.0, 5000.0)

        assert aircraft.callsign == "TEST"
        assert aircraft.origin_country == "Russia"
        assert aircraft.velocity == 100.0
        assert aircraft.altitude == 5000.0
        assert aircraft.icao24 == "Unknown"

    def test_aircraft_validation_callsign(self):
        """Тест валидации позывного"""
        # Пустой позывной
        aircraft = Aircraft("", "Russia", 100.0, 5000.0)
        assert aircraft.callsign == "Unknown"

        # None позывной (через from_dict)
        aircraft = Aircraft.from_dict({
            'callsign': None,
            'origin_country': 'Russia',
            'velocity': 100.0,
            'altitude': 5000.0
        })
        assert aircraft.callsign == "Unknown"

    def test_aircraft_validation_velocity(self):
        """Тест валидации скорости"""
        # Отрицательная скорость
        aircraft = Aircraft("TEST", "Russia", -100.0, 5000.0)
        assert aircraft.velocity == 0.0

        # None скорость
        aircraft = Aircraft.from_dict({
            'callsign': 'TEST',
            'origin_country': 'Russia',
            'velocity': None,
            'altitude': 5000.0
        })
        assert aircraft.velocity == 0.0

    def test_aircraft_validation_altitude(self):
        """Тест валидации высоты"""
        # Отрицательная высота
        aircraft = Aircraft("TEST", "Russia", 100.0, -500.0)
        assert aircraft.altitude == -500.0  # Отрицательная допустима

        # None высота
        aircraft = Aircraft.from_dict({
            'callsign': 'TEST',
            'origin_country': 'Russia',
            'velocity': 100.0,
            'altitude': None
        })
        assert aircraft.altitude == 0.0

    def test_aircraft_comparison_operators(self):
        """Тест операторов сравнения"""
        aircraft1 = Aircraft("TEST1", "Russia", 200.0, 10000.0)
        aircraft2 = Aircraft("TEST2", "USA", 250.0, 12000.0)
        aircraft3 = Aircraft("TEST3", "UK", 200.0, 8000.0)

        # Сравнение по скорости
        assert aircraft1 < aircraft2
        assert aircraft2 > aircraft1
        assert aircraft1 <= aircraft3
        assert aircraft2 >= aircraft1

        # Специальные методы сравнения
        assert aircraft2.faster_than(aircraft1)
        assert not aircraft1.faster_than(aircraft2)
        assert aircraft2.higher_than(aircraft1)
        assert not aircraft1.higher_than(aircraft2)

    def test_aircraft_equality(self):
        """Тест равенства самолетов"""
        aircraft1 = Aircraft("TEST", "Russia", 200.0, 10000.0)
        aircraft2 = Aircraft("TEST", "Russia", 200.0, 10000.0)
        aircraft3 = Aircraft("DIFF", "Russia", 200.0, 10000.0)

        assert aircraft1 == aircraft2
        assert aircraft1 != aircraft3
        assert aircraft1 != "not an aircraft"

    def test_aircast_cast_to_object_list(self, sample_aircraft_list):
        """Тест преобразования списка словарей в список объектов"""
        aircraft_list = Aircraft.cast_to_object_list(sample_aircraft_list)

        assert len(aircraft_list) == 3
        assert all(isinstance(a, Aircraft) for a in aircraft_list)
        assert aircraft_list[0].callsign == "AFL101"
        assert aircraft_list[1].callsign == "UAL202"
        assert aircraft_list[2].callsign == "BAW303"

    def test_aircraft_to_dict(self, sample_aircraft):
        """Тест преобразования объекта в словарь"""
        aircraft_dict = sample_aircraft.to_dict()

        assert isinstance(aircraft_dict, dict)
        assert aircraft_dict['callsign'] == sample_aircraft.callsign
        assert aircraft_dict['origin_country'] == sample_aircraft.origin_country
        assert aircraft_dict['velocity'] == sample_aircraft.velocity
        assert aircraft_dict['altitude'] == sample_aircraft.altitude

    def test_aircraft_str_repr(self, sample_aircraft):
        """Тест строкового представления"""
        str_repr = str(sample_aircraft)
        repr_repr = repr(sample_aircraft)

        assert sample_aircraft.callsign in str_repr
        assert sample_aircraft.origin_country in str_repr
        assert "Aircraft" in repr_repr
        assert sample_aircraft.callsign in repr_repr

    def test_aircraft_property_setters(self, sample_aircraft):
        """Тест сеттеров свойств"""
        # Изменение скорости
        sample_aircraft.velocity = 300.0
        assert sample_aircraft.velocity == 300.0

        # Изменение высоты
        sample_aircraft.altitude = 15000.0
        assert sample_aircraft.altitude == 15000.0

        # Проверка валидации в сеттерах
        sample_aircraft.velocity = -50.0
        assert sample_aircraft.velocity == 0.0

    def test_aircraft_position_property(self, sample_aircraft_dict):
        """Тест свойства position"""
        aircraft = Aircraft.from_dict(sample_aircraft_dict)
        lon, lat = aircraft.position

        assert lon == sample_aircraft_dict['longitude']
        assert lat == sample_aircraft_dict['latitude']

    def test_aircraft_slots(self):
        """Тест использования __slots__"""
        aircraft = Aircraft("TEST", "Russia", 100.0, 5000.0)

        # Попытка создать новый атрибут должна вызвать AttributeError
        with pytest.raises(AttributeError):
            aircraft.new_attribute = "test"
