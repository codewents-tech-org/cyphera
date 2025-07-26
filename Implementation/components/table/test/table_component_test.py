import pytest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from components.table import table_component
from components.table.table_component import TableComponent 
import pytest
import sys
from PyQt5.QtWidgets import QApplication

@pytest.fixture(scope="session", autouse=True)
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def mock_table():
    table = QTableWidget()
    table.setColumnCount(4)
    for i in range(4):
        item = QTableWidgetItem(f"Header {i}")
        table.setHorizontalHeaderItem(i, item)
    return table


def test_auto_adjust_column_width_valid_key(mock_table):
    component = TableComponent()
    component._table_column_mappings = {'asset': ['ID', 'Name', 'Type']}
    component.auto_adjust_column_width(mock_table, 'asset')
    assert mock_table.columnWidth(0) == 70



def test_auto_adjust_column_width_invalid_key(mock_table):
    component = TableComponent()
    component.auto_adjust_column_width(mock_table, 'invalid')
    assert mock_table.columnWidth(0) == 70


def test_auto_adjust_column_width_short_headers(mock_table):
    component = TableComponent()
    component._table_column_mappings = {'asset': ['OnlyOne']}
    component.auto_adjust_column_width(mock_table, 'asset')
    assert mock_table.columnWidth(1) > 0  # still adjusts what exists



def test_auto_adjust_column_width_no_columns():
    component = TableComponent()
    table = QTableWidget()
    table.setColumnCount(0)
    component.auto_adjust_column_width(table, 'asset')
    assert table.columnCount() == 0


def test_auto_adjust_column_width_exception():
    component = TableComponent()
    table = MagicMock()
    table.columnCount.side_effect = Exception("Error")
    component.auto_adjust_column_width(table, 'asset')  # Should not raise an error due to exception handling


def test_setup_table_headers_valid(mock_table):
    component = TableComponent()
    header_list = ['ID', 'Name', 'Type']
    with patch.object(TableComponent, 'auto_adjust_column_width') as mock_adjust:
        component.setup_table_headers(mock_table, 4, header_list, 'asset')
        assert mock_table.columnCount() == 4
        mock_adjust.assert_called_once()


def test_setup_table_headers_empty_headers(mock_table):
    component = TableComponent()
    with patch.object(TableComponent, 'auto_adjust_column_width') as mock_adjust:
        component.setup_table_headers(mock_table, 2, [], 'scope')
        assert mock_table.columnCount() == 2
        mock_adjust.assert_called_once()


def test_setup_table_headers_more_headers_than_columns():
    component = TableComponent()
    table = QTableWidget()
    header_list = ['H1', 'H2', 'H3', 'H4', 'H5']
    with patch.object(TableComponent, 'auto_adjust_column_width') as mock_adjust:
        component.setup_table_headers(table, 3, header_list, 'scope')
        assert table.columnCount() == 3
        mock_adjust.assert_called_once()



def test_setup_table_headers_exception():
    component = TableComponent()
    table = MagicMock()
    table.setColumnCount.side_effect = Exception("Error")
    component.setup_table_headers(table, 3, ['A', 'B'], 'scope')  # Should not raise due to exception handling


def test_auto_adjust_column_width_known_width(mock_table):
    component = TableComponent()
    component._table_column_mappings = {'asset': ['TestColumn1', 'TestColumn2', 'TestColumn3']}
    component.auto_adjust_column_width(mock_table, 'asset')
    assert mock_table.columnWidth(1) > 100


def test_auto_adjust_column_width_preserves_column_count(mock_table):
    component = TableComponent()
    component._table_column_mappings = {'asset': ['ID', 'Name', 'Type']}
    original_count = mock_table.columnCount()
    component.auto_adjust_column_width(mock_table, 'asset')
    assert mock_table.columnCount() == original_count



def test_setup_table_headers_applies_text(mock_table):
    component = TableComponent()
    headers = ['Col A', 'Col B', 'Col C']
    component.setup_table_headers(mock_table, 4, headers, 'asset')
    assert mock_table.horizontalHeaderItem(1).text() == 'Col A'
    assert mock_table.horizontalHeaderItem(2).text() == 'Col B'


def test_setup_table_headers_sidebar_column_blank(mock_table):
    component = TableComponent()
    headers = ['Col A', 'Col B', 'Col C']
    component.setup_table_headers(mock_table, 4, headers, 'asset')
    assert mock_table.horizontalHeaderItem(0).text() == ''


def test_setup_table_headers_last_column_stretch(mock_table):
    component = TableComponent()
    headers = ['Col A', 'Col B', 'Col C']
    table = MagicMock(spec=QTableWidget)
    table.setColumnCount.return_value = None
    table.horizontalHeader().setStretchLastSection = MagicMock()

    with patch.object(component, 'auto_adjust_column_width'):
        component.setup_table_headers(table, 4, headers, 'asset')

    table.horizontalHeader().setStretchLastSection.assert_called_with(True)

