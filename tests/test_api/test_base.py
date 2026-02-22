import pytest
from unittest.mock import Mock, patch
from src.api.base import BaseAPI


class TestBaseAPI:
    """Тесты для BaseAPI"""

    def test_base_api_abstract(self):
        """Тест, что BaseAPI абстрактный"""
        with pytest.raises(TypeError):
            BaseAPI("http://test.com")  # Нельзя создать напрямую

    def test_base_api_initialization(self):
        """Тест инициализации через наследника"""

        class TestAPI(BaseAPI):
            def get_data(self, endpoint, params=None):
                return self._make_request(endpoint, params)

        api = TestAPI("http://test.com")
        assert api.base_url == "http://test.com"
        assert api.session is not None

    @patch('requests.Session.get')
    def test_make_request_success(self, mock_get):
        """Тест успешного запроса"""

        class TestAPI(BaseAPI):
            def get_data(self, endpoint, params=None):
                return self._make_request(endpoint, params)

        mock_response = Mock()
        mock_response.json.return_value = {"key": "value"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        api = TestAPI("http://test.com")
        result = api._make_request("endpoint", {"param": "value"})

        assert result == {"key": "value"}
        mock_get.assert_called_once_with(
            "http://test.com/endpoint",
            params={"param": "value"},
            timeout=10
        )

    @patch('requests.Session.get')
    def test_make_request_http_error(self, mock_get):
        """Тест HTTP ошибки"""

        class TestAPI(BaseAPI):
            def get_data(self, endpoint, params=None):
                return self._make_request(endpoint, params)

        from requests.exceptions import HTTPError
        mock_get.side_effect = HTTPError("404 Client Error")

        api = TestAPI("http://test.com")
        result = api._make_request("endpoint")

        assert result == {}

    @patch('requests.Session.get')
    def test_make_request_json_error(self, mock_get):
        """Тест ошибки парсинга JSON"""

        class TestAPI(BaseAPI):
            def get_data(self, endpoint, params=None):
                return self._make_request(endpoint, params)

        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        api = TestAPI("http://test.com")
        result = api._make_request("endpoint")

        assert result == {}
