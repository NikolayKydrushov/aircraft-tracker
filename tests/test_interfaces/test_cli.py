import pytest
from unittest.mock import Mock, patch, MagicMock
from src.models.aircraft import Aircraft
from src.interfaces.cli import (
    print_header,
    print_aircraft_list,
    get_top_by_altitude,
    filter_by_country,
    filter_by_altitude_range,
    sort_by_velocity,
    user_interaction
)


@pytest.fixture
def sample_aircraft_list():
    """Фикстура со списком самолетов"""
    return [
        Aircraft("AFL101", "Russia", 280.5, 11000.0),
        Aircraft("UAL202", "United States", 260.3, 10500.0),
        Aircraft("BAW303", "United Kingdom", 240.1, 9500.0),
        Aircraft("AFR404", "France", 290.7, 12000.0),
        Aircraft("DLH505", "Germany", 270.2, 10000.0)
    ]


class TestCLIHelpers:
    """Тесты вспомогательных функций CLI"""

    def test_print_header(self, capsys):
        """Тест вывода заголовка"""
        print_header("Test Header")

        captured = capsys.readouterr()
        assert "Test Header" in captured.out
        assert "=" * 60 in captured.out

    def test_print_aircraft_list_with_data(self, capsys, sample_aircraft_list):
        """Тест вывода списка самолетов с данными"""
        print_aircraft_list(sample_aircraft_list, "Test Title")

        captured = capsys.readouterr()
        assert "Test Title" in captured.out
        assert "AFL101" in captured.out
        assert "Russia" in captured.out
        assert "Всего: 5 самолетов" in captured.out

    def test_print_aircraft_list_empty(self, capsys):
        """Тест вывода пустого списка"""
        print_aircraft_list([], "Test Title")

        captured = capsys.readouterr()
        assert "Test Title" in captured.out
        assert "Нет данных для отображения" in captured.out

    def test_get_top_by_altitude(self, sample_aircraft_list):
        """Тест получения топа по высоте"""
        top3 = get_top_by_altitude(sample_aircraft_list, 3)

        assert len(top3) == 3
        # Проверяем, что отсортировано по убыванию высоты
        assert top3[0].altitude >= top3[1].altitude >= top3[2].altitude
        assert top3[0].callsign == "AFR404"  # Самый высокий (12000)
        assert top3[1].callsign == "AFL101"  # 11000
        assert top3[2].callsign == "UAL202"  # 10500

    def test_filter_by_country(self, sample_aircraft_list):
        """Тест фильтрации по стране"""
        # Фильтр по одной стране
        filtered = filter_by_country(sample_aircraft_list, ["Russia"])
        assert len(filtered) == 1
        assert filtered[0].callsign == "AFL101"

        # Фильтр по нескольким странам
        filtered = filter_by_country(sample_aircraft_list, ["Russia", "France"])
        assert len(filtered) == 2
        callsigns = [a.callsign for a in filtered]
        assert "AFL101" in callsigns
        assert "AFR404" in callsigns

        # Фильтр по несуществующей стране
        filtered = filter_by_country(sample_aircraft_list, ["NonExistent"])
        assert len(filtered) == 0

    def test_filter_by_altitude_range(self, sample_aircraft_list):
        """Тест фильтрации по диапазону высот"""
        # Диапазон, включающий несколько самолетов
        filtered = filter_by_altitude_range(sample_aircraft_list, 10000, 11000)
        assert len(filtered) == 3
        callsigns = [a.callsign for a in filtered]
        assert "AFL101" in callsigns  # 11000
        assert "UAL202" in callsigns  # 10500
        assert "DLH505" in callsigns  # 10000

        # Пустой диапазон
        filtered = filter_by_altitude_range(sample_aircraft_list, 20000, 30000)
        assert len(filtered) == 0

    def test_sort_by_velocity(self, sample_aircraft_list):
        """Тест сортировки по скорости"""
        # По убыванию (по умолчанию)
        sorted_list = sort_by_velocity(sample_aircraft_list)
        assert sorted_list[0].velocity >= sorted_list[-1].velocity
        assert sorted_list[0].callsign == "AFR404"  # Самая быстрая (290.7)

        # По возрастанию
        sorted_list = sort_by_velocity(sample_aircraft_list, reverse=False)
        assert sorted_list[0].velocity <= sorted_list[-1].velocity
        assert sorted_list[0].callsign == "BAW303"  # Самая медленная (240.1)


class TestUserInteraction:
    """Тесты функции user_interaction"""

    @patch('builtins.input')
    @patch('src.interfaces.cli.AircraftAPI')
    @patch('src.interfaces.cli.JSONStorage')
    def test_user_interaction_choice_1_success(self, mock_storage, mock_api, mock_input, sample_aircraft_list):
        """Тест выбора 1 (получение данных) - успешный сценарий"""
        # Настраиваем моки для ввода
        mock_input.side_effect = [
            '1',  # Формат JSON
            '1',  # Выбор действия 1
            'Canada',  # Название страны
            '',  # Нажатие Enter для продолжения
            '0'  # Выход
        ]

        # Настраиваем моки API
        mock_api_instance = Mock()
        mock_api.return_value = mock_api_instance
        mock_api_instance.get_aircraft_by_country.return_value = [['mock', 'data']]
        mock_api_instance.process_aircraft_data.return_value = [
            {'callsign': 'TEST1', 'origin_country': 'Canada', 'velocity': 100, 'altitude': 10000}
        ]

        # Настраиваем мок хранилища
        mock_storage_instance = Mock()
        mock_storage.return_value = mock_storage_instance
        mock_storage_instance.add_multiple_aircraft.return_value = 1

        # Создаем мок для Aircraft.cast_to_object_list
        with patch('src.interfaces.cli.Aircraft.cast_to_object_list') as mock_cast:
            mock_cast.return_value = sample_aircraft_list[:1]

            # Вызываем функцию
            user_interaction()

            # Проверяем, что методы были вызваны
            mock_api_instance.get_aircraft_by_country.assert_called_once_with("Canada")
            mock_api_instance.process_aircraft_data.assert_called_once()
            mock_cast.assert_called_once()
            mock_storage_instance.add_multiple_aircraft.assert_called_once()

    @patch('builtins.input')
    @patch('src.interfaces.cli.AircraftAPI')
    @patch('src.interfaces.cli.CSVStorage')
    def test_user_interaction_csv_format(self, mock_storage, mock_api, mock_input):
        """Тест выбора CSV формата"""
        # Настраиваем моки для ввода
        mock_input.side_effect = [
            '2',  # Формат CSV
            '0'  # Выход
        ]

        # Настраиваем мок хранилища
        mock_storage_instance = Mock()
        mock_storage.return_value = mock_storage_instance

        # Вызываем функцию
        user_interaction()

        # Проверяем, что CSVStorage был создан
        mock_storage.assert_called_once()

    @patch('builtins.input')
    @patch('src.interfaces.cli.AircraftAPI')
    @patch('src.interfaces.cli.JSONStorage')
    def test_user_interaction_choice_2(self, mock_storage, mock_api, mock_input, sample_aircraft_list):
        """Тест выбора 2 (топ по высоте)"""
        # Настраиваем моки для ввода
        mock_input.side_effect = [
            '1',  # Формат JSON
            '2',  # Выбор действия 2
            '3',  # Топ 3
            '',  # Нажатие Enter для продолжения
            '0'  # Выход
        ]

        # Настраиваем мок хранилища
        mock_storage_instance = Mock()
        mock_storage.return_value = mock_storage_instance
        mock_storage_instance.get_all.return_value = sample_aircraft_list
        mock_storage_instance.count.return_value = 5

        # Вызываем функцию
        with patch('src.interfaces.cli.get_top_by_altitude') as mock_top:
            mock_top.return_value = sample_aircraft_list[:3]

            user_interaction()

            mock_storage_instance.get_all.assert_called_once()
            mock_top.assert_called_once_with(sample_aircraft_list, 3)

    @patch('builtins.input')
    @patch('src.interfaces.cli.AircraftAPI')
    @patch('src.interfaces.cli.JSONStorage')
    def test_user_interaction_choice_3(self, mock_storage, mock_api, mock_input, sample_aircraft_list):
        """Тест выбора 3 (фильтр по стране)"""
        # Настраиваем моки для ввода
        mock_input.side_effect = [
            '1',  # Формат JSON
            '3',  # Выбор действия 3
            'Russia, United States',  # Страны через запятую
            '',  # Нажатие Enter для продолжения
            '0'  # Выход
        ]

        # Настраиваем мок хранилища
        mock_storage_instance = Mock()
        mock_storage.return_value = mock_storage_instance
        mock_storage_instance.get_all.return_value = sample_aircraft_list
        mock_storage_instance.count.return_value = 5

        # Вызываем функцию
        with patch('src.interfaces.cli.filter_by_country') as mock_filter:
            mock_filter.return_value = sample_aircraft_list[:2]

            user_interaction()

            mock_storage_instance.get_all.assert_called_once()
            mock_filter.assert_called_once_with(sample_aircraft_list, ['Russia', 'United States'])

    @patch('builtins.input')
    @patch('src.interfaces.cli.AircraftAPI')
    @patch('src.interfaces.cli.JSONStorage')
    def test_user_interaction_choice_4(self, mock_storage, mock_api, mock_input, sample_aircraft_list):
        """Тест выбора 4 (показать все)"""
        # Настраиваем моки для ввода
        mock_input.side_effect = [
            '1',  # Формат JSON
            '4',  # Выбор действия 4
            '',  # Нажатие Enter для продолжения
            '0'  # Выход
        ]

        # Настраиваем мок хранилища
        mock_storage_instance = Mock()
        mock_storage.return_value = mock_storage_instance
        mock_storage_instance.get_all.return_value = sample_aircraft_list
        mock_storage_instance.count.return_value = 5

        # Вызываем функцию
        user_interaction()

        mock_storage_instance.get_all.assert_called_once()
        mock_storage_instance.count.assert_called_once()

    @patch('builtins.input')
    @patch('src.interfaces.cli.AircraftAPI')
    @patch('src.interfaces.cli.JSONStorage')
    def test_user_interaction_choice_5_submenu_1(self, mock_storage, mock_api, mock_input, sample_aircraft_list):
        """Тест подменю 5.1 (фильтр по диапазону высот)"""
        # Настраиваем моки для ввода
        mock_input.side_effect = [
            '1',  # Формат JSON
            '5',  # Выбор действия 5
            '1',  # Фильтр по высоте
            '10000 - 11000',  # Диапазон
            '',  # Нажатие Enter для продолжения
            '0'  # Выход
        ]

        # Настраиваем мок хранилища
        mock_storage_instance = Mock()
        mock_storage.return_value = mock_storage_instance
        mock_storage_instance.get_all.return_value = sample_aircraft_list

        # Вызываем функцию
        with patch('src.interfaces.cli.parse_altitude_range') as mock_parse:
            mock_parse.return_value = (10000, 11000)
            with patch('src.interfaces.cli.filter_by_altitude_range') as mock_filter:
                mock_filter.return_value = sample_aircraft_list[:2]

                user_interaction()

                mock_storage_instance.get_all.assert_called_once()
                mock_parse.assert_called_once_with('10000 - 11000')
                mock_filter.assert_called_once_with(sample_aircraft_list, 10000, 11000)

    @patch('builtins.input')
    @patch('src.interfaces.cli.AircraftAPI')
    @patch('src.interfaces.cli.JSONStorage')
    def test_user_interaction_choice_5_submenu_2(self, mock_storage, mock_api, mock_input, sample_aircraft_list):
        """Тест подменю 5.2 (сортировка по скорости)"""
        # Настраиваем моки для ввода
        mock_input.side_effect = [
            '1',  # Формат JSON
            '5',  # Выбор действия 5
            '2',  # Сортировка по скорости
            '',  # Нажатие Enter для продолжения
            '0'  # Выход
        ]

        # Настраиваем мок хранилища
        mock_storage_instance = Mock()
        mock_storage.return_value = mock_storage_instance
        mock_storage_instance.get_all.return_value = sample_aircraft_list

        # Вызываем функцию
        with patch('src.interfaces.cli.sort_by_velocity') as mock_sort:
            mock_sort.return_value = sorted(sample_aircraft_list, key=lambda a: a.velocity, reverse=True)

            user_interaction()

            mock_storage_instance.get_all.assert_called_once()
            mock_sort.assert_called_once_with(sample_aircraft_list)

    @patch('builtins.input')
    @patch('src.interfaces.cli.AircraftAPI')
    @patch('src.interfaces.cli.JSONStorage')
    def test_user_interaction_choice_1_invalid_country(self, mock_storage, mock_api, mock_input):
        """Тест выбора 1 с некорректным названием страны"""
        # Настраиваем моки для ввода
        mock_input.side_effect = [
            '1',  # Формат JSON
            '1',  # Выбор действия 1
            '123',  # Некорректное название (цифры)
            '0'  # Выход
        ]

        # Настраиваем мок хранилища
        mock_storage_instance = Mock()
        mock_storage.return_value = mock_storage_instance

        # Вызываем функцию
        user_interaction()

        # Проверяем, что API не вызывался
        mock_api.return_value.get_aircraft_by_country.assert_not_called()

    @patch('builtins.input')
    @patch('src.interfaces.cli.AircraftAPI')
    @patch('src.interfaces.cli.JSONStorage')
    def test_user_interaction_choice_2_invalid_n(self, mock_storage, mock_api, mock_input, sample_aircraft_list):
        """Тест выбора 2 с некорректным числом"""
        # Настраиваем моки для ввода
        mock_input.side_effect = [
            '1',  # Формат JSON
            '2',  # Выбор действия 2
            '-5',  # Отрицательное число
            '0'  # Выход
        ]

        # Настраиваем мок хранилища
        mock_storage_instance = Mock()
        mock_storage.return_value = mock_storage_instance

        # Вызываем функцию
        user_interaction()

        # get_top_by_altitude не должен вызываться
        mock_storage_instance.get_all.assert_not_called()
