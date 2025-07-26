import os, sqlite3, tempfile, sys
import pytest
# — Ensure your project root is on PYTHONPATH —
HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
from components.description.model import DescriptionModel

@pytest.fixture
def temp_db(tmp_path):
    return str(tmp_path / "test.db")

def test_empty_db_load_creates_table_and_returns_empty(temp_db):
    model = DescriptionModel(db_path=temp_db)
    assert os.path.exists(temp_db)
    assert model.load(1) == ""

def test_no_record_returns_empty(temp_db):
    model = DescriptionModel(db_path=temp_db)
    # ensure table exists but no data
    assert model.load(42) == ""

def test_insert_and_load(temp_db):
    model = DescriptionModel(db_path=temp_db)
    html = "<p>Test</p>"
    assert model.save(html, record_id=5) is True
    assert model.load(5) == html

def test_update_existing(temp_db):
    model = DescriptionModel(db_path=temp_db)
    first, second = "<div>One</div>", "<div>Two</div>"
    assert model.save(first, record_id=7)
    assert model.load(7) == first
    assert model.save(second, record_id=7)
    assert model.load(7) == second

def test_save_empty_html(temp_db):
    model = DescriptionModel(db_path=temp_db)
    assert model.save("", record_id=3) is True
    assert model.load(3) == ""

def test_large_html(temp_db):
    model = DescriptionModel(db_path=temp_db)
    large = "A" * 1_000_000
    assert model.save(large, record_id=9)
    assert model.load(9) == large

def test_sql_injection_content(temp_db):
    model = DescriptionModel(db_path=temp_db)
    inj = "'; DROP TABLE scope_description;--<p>"
    assert model.save(inj, record_id=10)
    assert model.load(10) == inj

def test_invalid_db_path_save_fails():
    # Attempt to save to a directory
    model = DescriptionModel(db_path="/")
    assert model.save("<p>Hi</p>", record_id=1) is False

def test_null_record_id_handling(temp_db):
    model = DescriptionModel(db_path=temp_db)
    # load with None -> returns empty string
    assert model.load(None) == ""
    # save with None -> fails
    assert model.save("<p>X</p>", record_id=None) is False

def test_multiple_records(temp_db):
    model = DescriptionModel(db_path=temp_db)
    data = {1:"a", 2:"b", 3:"c"}
    for rid, html in data.items():
        assert model.save(html, record_id=rid)
    for rid, html in data.items():
        assert model.load(rid) == html

if __name__ == '__main__':
    # This will run all tests in this file.
    sys.exit(pytest.main([__file__]))
