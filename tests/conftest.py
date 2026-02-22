import pytest
import json
import os
import tempfile
from typing import Dict, Any, List
from src.models.aircraft import Aircraft
from src.api.aircraft_api import AircraftAPI
from src.storage.json_storage import JSONStorage


@pytest.fixture
def sample_aircraft_dict() -> Dict[str, Any]:
    """Фикстура с данными самолета в виде словаря"""
    return {
        'callsign': 'TEST123',
        'origin_country': 'Russia',
        'velocity': 250.5,
        'altitude': 10000.0,
        'icao24': '123abc',
        'longitude': 37.62,
        'latitude': 55.75,
        'on_ground': False,
        'vertical_rate': 5.5
    }


@pytest.fixture
def sample_aircraft(sample_aircraft_dict) -> Aircraft:
    """Фикстура с объектом самолета"""
    return Aircraft.from_dict(sample_aircraft_dict)


@pytest.fixture
def sample_aircraft_list() -> List[Dict[str, Any]]:
    """Фикстура со списком самолетов"""
    return [
        {
            'callsign': 'AFL101',
            'origin_country': 'Russia',
            'velocity': 280.5,
            'altitude': 11000.0,
            'icao24': 'abc123',
            'on_ground': False
        },
        {
            'callsign': 'UAL202',
            'origin_country': 'United States',
            'velocity': 260.3,
            'altitude': 10500.0,
            'icao24': 'def456',
            'on_ground': False
        },
        {
            'callsign': 'BAW303',
            'origin_country': 'United Kingdom',
            'velocity': 240.1,
            'altitude': 9500.0,
            'icao24': 'ghi789',
            'on_ground': True
        }
    ]


@pytest.fixture
def temp_json_file():
    """Фикстура для временного JSON файла"""
    fd, path = tempfile.mkstemp(suffix='.json')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def json_storage(temp_json_file):
    """Фикстура с JSON хранилищем"""
    return JSONStorage(temp_json_file)


@pytest.fixture
def mock_nominatim_response():
    """Фикстура с мок-ответом от Nominatim API"""
    return [
        {
            "place_id": 346277167,
            "licence": "Data © OpenStreetMap contributors",
            "boundingbox": [
                "41.6765597",
                "83.3362128",
                "-141.0027500",
                "-52.3237664"
            ]
        }
    ]


@pytest.fixture
def mock_opensky_response():
    """Фикстура с мок-ответом от OpenSky API"""
    return {
        "time": 1766142246,
        "states": [
            [
                "4b1812",
                "SWR438A ",
                "Switzerland",
                1766166618,
                1766166618,
                -0.0168,
                51.0888,
                4267.2,
                False,
                189.7,
                129.39,
                14.63,
                None,
                4282.44,
                "2061",
                False,
                0
            ],
            [
                "abc123",
                "AFL101 ",
                "Russia",
                1766166619,
                1766166619,
                37.62,
                55.75,
                11000.0,
                False,
                280.5,
                130.0,
                10.5,
                None,
                11200.0,
                "1234",
                False,
                0
            ]
        ]
    }


@pytest.fixture
def mock_aircraft_list():
    """Фикстура со списком самолетов для CLI тестов"""
    from src.models.aircraft import Aircraft
    return [
        Aircraft("TEST1", "Russia", 280.5, 11000.0),
        Aircraft("TEST2", "USA", 260.3, 10500.0),
        Aircraft("TEST3", "UK", 240.1, 9500.0)
    ]
