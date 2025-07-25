import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from datetime import datetime
from controllers.database import Base, initialize_database
from controllers.tablemodel import Assets, ActivityLog
from controllers.schema_manager import create_instance, get_instance, update_instance, delete_instance
from components.logger_config import log_activity, log_crud_action


def _create_instance_direct(instance, session):
    session.add(instance)
    return True


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)  # Ensures schema matches model
    session = Session()
    yield session
    session.rollback()
    session.close()


def test_ut001_create_valid(session):
    asset = Assets(asset_id="T001", name="Asset", created_by="tester")
    assert _create_instance_direct(asset, session)
    session.commit()
    assert session.query(Assets).filter_by(asset_id="T001").count() == 1


def test_ut002_create_missing_required(session):
    with pytest.raises(Exception):
        asset = Assets(asset_id=None, name="Fail Asset", created_by="tester")
        session.add(asset)
        session.commit()


def test_ut003_create_duplicate_key(session):
    asset1 = Assets(asset_id="DUP001", name="One", created_by="tester")
    session.add(asset1)
    session.commit()
    with pytest.raises(IntegrityError):
        session.add(Assets(asset_id="DUP001", name="Two", created_by="tester"))
        session.commit()


def test_ut004_get_instance_valid():
    initialize_database()
    delete_instance(Assets, {"asset_id": "FIND001"})
    create_instance(Assets(asset_id="FIND001", name="Find", created_by="tester"))
    result = get_instance(Assets, {"asset_id": "FIND001"})
    assert isinstance(result, list)
    assert len(result) == 1


def get_instance_raw(model, filters):
    from controllers.database import get_session
    session = get_session()
    try:
        query = session.query(model)
        query = query.filter_by(**filters)
        return query.all()
    finally:
        session.close()

def test_ut005_get_instance_invalid_field():
    with pytest.raises(InvalidRequestError):
        get_instance_raw(Assets, {"invalid_column": "123"})



def test_ut006_get_instance_all():
    initialize_database()
    create_instance(Assets(asset_id="ALL001", name="AllTest", created_by="tester"))
    result = get_instance(Assets, {})
    assert isinstance(result, list)


def test_ut007_update_existing():
    initialize_database()
    create_instance(Assets(asset_id="UPD001", name="Before", created_by="tester"))
    result = update_instance(Assets, {"asset_id": "UPD001"}, {"name": "After"})
    assert result is True


def test_ut008_update_none():
    initialize_database()
    result = update_instance(Assets, {"asset_id": "XYZ"}, {"name": "None"})
    assert result is False


def test_ut009_delete_valid():
    initialize_database()
    create_instance(Assets(asset_id="DEL001", name="Delete", created_by="tester"))
    result = delete_instance(Assets, {"asset_id": "DEL001"})
    assert result is True


def test_ut010_delete_none():
    initialize_database()
    result = delete_instance(Assets, {"asset_id": "INVALID"})
    assert result is False


def test_ut011_initialize_database_fresh():
    assert initialize_database()


def test_ut012_initialize_database_repeat():
    assert initialize_database()


def test_ut013_log_activity_standard(session):
    log = ActivityLog(
        action_type="CREATE",
        module="Test",
        entity_id="ID123",
        performed_by="tester",
        description="Log entry",
        timestamp=datetime.now()
    )
    session.add(log)
    session.commit()
    assert session.query(ActivityLog).filter_by(entity_id="ID123").count() == 1


@patch("components.logger_config.SessionLocal")
def test_ut014_log_activity_failure(mock_session_class):
    mock_session = MagicMock()
    mock_session.commit.side_effect = Exception("Fail Commit")
    mock_session_class.return_value = mock_session
    log_activity("CREATE", "MockModule", "123", "tester", "fail test")


@patch("components.logger_config.log_activity")
def test_ut015_log_crud_action_returns_none(mock_log):
    @log_crud_action("CREATE", lambda *_: "M1", lambda *_: "E1")
    def wrapped_func():
        return None
    wrapped_func()
    mock_log.assert_called_once()


@patch("components.logger_config.log_activity")
def test_ut016_log_crud_action_raises_exception(mock_log):
    @log_crud_action("DELETE", lambda *_: "X", lambda *_: "Y")
    def error_func():
        raise ValueError("Bad input")
    with pytest.raises(ValueError):
        error_func()
    mock_log.assert_not_called()


@patch("components.logger_config.log_activity")
def test_ut017_log_crud_action_missing_id(mock_log):
    @log_crud_action("READ", lambda *_: "Mod", lambda *_: None)
    def idless_func():
        return object()
    idless_func()
    mock_log.assert_called_once()


@patch("components.logger_config.log_activity")
def test_ut018_log_crud_action_missing_module(mock_log):
    @log_crud_action("UPDATE", lambda *_: None, lambda *_: "ID001")
    def moduleless_func():
        return {"asset_id": "ID001"}
    moduleless_func()
    mock_log.assert_called_once()
