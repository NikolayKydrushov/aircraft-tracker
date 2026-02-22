import pytest
from src.storage.base import BaseStorage


class TestBaseStorage:
    """Тесты для BaseStorage"""

    def test_base_storage_abstract(self):
        """Тест, что BaseStorage абстрактный"""
        with pytest.raises(TypeError):
            BaseStorage()  # Нельзя создать напрямую

    def test_base_storage_methods(self):
        """Тест наличия всех абстрактных методов"""
        methods = [
            'add_aircraft',
            'add_multiple_aircraft',
            'get_aircraft',
            'delete_aircraft',
            'get_all',
            'clear',
            'count'
        ]

        for method in methods:
            assert hasattr(BaseStorage, method)
            assert hasattr(getattr(BaseStorage, method), '__isabstractmethod__')
