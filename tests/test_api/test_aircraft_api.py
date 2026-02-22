import pytest
from unittest.mock import Mock, patch, MagicMock
from src.api.aircraft_api import AircraftAPI


class TestAircraftAPI:
    """Тесты для AircraftAPI"""

    def test_initialization(self):
        """Тест инициализации"""
        api = AircraftAPI()

        assert api.base_url == AircraftAPI.OPENSKY_URL
        assert api._nominatim_url == AircraftAPI.NOMINATIM_URL
        assert api.aeroplanes is None

    @patch('requests.Session.get')
    def test_get_aeroplanes_success(self, mock_get, mock_nominatim_response, mock_opensky_response):
        """Тест успешного получения самолетов"""
        # Настраиваем мок для Nominatim
        mock_nominatim_response_obj = Mock()
        mock_nominatim_response_obj.json.return_value = mock_nominatim_response
        mock_nominatim_response_obj.raise_for_status.return_value = None

        # Настраиваем мок для OpenSky
        mock_opensky_response_obj = Mock()
        mock_opensky_response_obj.json.return_value = mock_opensky_response
        mock_opensky_response_obj.raise_for_status.return_value = None

        # Устанавливаем возвращаемые значения для двух вызовов
        mock_get.side_effect = [mock_nominatim_response_obj, mock_opensky_response_obj]

        api = AircraftAPI()
        api.get_aeroplanes("Canada")

        assert api.aeroplanes is not None
        assert 'states' in api.aeroplanes
        assert len(api.aeroplanes['states']) == 2

    @patch('requests.Session.get')
    def test_get_aeroplanes_country_not_found(self, mock_get):
        """Тест когда страна не найдена"""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        api = AircraftAPI()
        api.get_aeroplanes("NonExistentCountry")

        assert api.aeroplanes == {"states": []}

    @patch('requests.Session.get')
    def test_get_country_boundingbox_success(self, mock_get, mock_nominatim_response):
        """Тест получения boundingbox"""
        mock_response = Mock()
        mock_response.json.return_value = mock_nominatim_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        api = AircraftAPI()
        result = api.get_country_boundingbox("Canada")

        assert result is not None
        assert len(result) == 4
        assert result[0] == 41.6765597  # south
        assert result[1] == 83.3362128  # north
        assert result[2] == -141.00275  # west
        assert result[3] == -52.3237664  # east

    @patch('requests.Session.get')
    def test_get_country_boundingbox_not_found(self, mock_get):
        """Тест получения boundingbox для несуществующей страны"""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        api = AircraftAPI()
        result = api.get_country_boundingbox("NonExistentCountry")

        assert result is None

    @patch('requests.Session.get')
    def test_get_aircraft_in_area(self, mock_get, mock_opensky_response):
        """Тест получения самолетов в области"""
        mock_response = Mock()
        mock_response.json.return_value = mock_opensky_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        api = AircraftAPI()
        result = api.get_aircraft_in_area(40.0, 50.0, -10.0, 10.0)

        assert len(result) == 2
        assert result[0][0] == "4b1812"
        assert result[1][0] == "abc123"

    def test_process_aircraft_data(self, mock_opensky_response):
        """Тест обработки данных самолетов"""
        api = AircraftAPI()
        raw_data = mock_opensky_response['states']

        processed = api.process_aircraft_data(raw_data)

        assert len(processed) == 2
        assert processed[0]['icao24'] == "4b1812"
        assert processed[0]['callsign'] == "SWR438A"
        assert processed[0]['origin_country'] == "Switzerland"
        assert processed[0]['velocity'] == 189.7
        assert processed[0]['altitude'] == 4267.2

        assert processed[1]['icao24'] == "abc123"
        assert processed[1]['callsign'] == "AFL101"
        assert processed[1]['origin_country'] == "Russia"

    def test_process_aircraft_data_invalid(self):
        """Тест обработки некорректных данных"""
        api = AircraftAPI()

        # Данные с недостаточной длиной
        raw_data = [["too", "short"]]
        processed = api.process_aircraft_data(raw_data)
        assert len(processed) == 0

        # Пустые данные
        processed = api.process_aircraft_data([])
        assert len(processed) == 0

    @patch('src.api.aircraft_api.AircraftAPI.get_aeroplanes')
    def test_get_aircraft_by_country(self, mock_get_aeroplanes, mock_opensky_response):
        """Тест получения самолетов по стране"""
        # Настраиваем мок так, чтобы после вызова get_aeroplanes
        # в объекте появились нужные данные
        api = AircraftAPI()

        def side_effect(country):
            api.aeroplanes = {"states": mock_opensky_response['states']}

        mock_get_aeroplanes.side_effect = side_effect

        result = api.get_aircraft_by_country("Canada")

        assert len(result) == 2
        mock_get_aeroplanes.assert_called_once_with("Canada")

    @patch('src.api.aircraft_api.AircraftAPI.get_aeroplanes')
    def test_get_aircraft_by_country_no_data(self, mock_get_aeroplanes):
        """Тест получения самолетов когда данных нет"""
        # Настраиваем мок так, чтобы после вызова get_aeroplanes
        # в объекте не было данных
        api = AircraftAPI()

        def side_effect(country):
            api.aeroplanes = {"states": []}

        mock_get_aeroplanes.side_effect = side_effect

        result = api.get_aircraft_by_country("NonExistentCountry")

        assert result == []
        mock_get_aeroplanes.assert_called_once_with("NonExistentCountry")

    @patch('src.api.aircraft_api.AircraftAPI.get_aeroplanes')
    def test_get_aircraft_by_country_aeroplanes_none(self, mock_get_aeroplanes):
        """Тест получения самолетов когда aeroplanes равен None"""
        # Настраиваем мок так, чтобы после вызова get_aeroplanes
        # в объекте aeroplanes остался None
        api = AircraftAPI()

        def side_effect(country):
            api.aeroplanes = None

        mock_get_aeroplanes.side_effect = side_effect

        result = api.get_aircraft_by_country("SomeCountry")

        assert result == []
        mock_get_aeroplanes.assert_called_once_with("SomeCountry")
