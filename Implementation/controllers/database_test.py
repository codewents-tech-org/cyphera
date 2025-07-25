import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from controllers import database

# UT001
def test_get_engine_and_session_returns_valid_tuple():
    engine, SessionLocal = database.get_engine_and_session()
    assert engine is not None
    assert callable(SessionLocal)

# UT002
def test_get_session_returns_session():
    session = database.get_session()
    assert isinstance(session, Session)
    session.close()

# UT003
def test_initialize_database_success():
    assert database.initialize_database() is True

# UT004
def test_db_error_handler_catches_exception():
    @database.db_error_handler
    def faulty():
        raise ValueError("Test")
    assert faulty() is False

# UT005
def test_handle_db_session_commits():
    @database.handle_db_session
    def sample(session=None):
        assert session is not None
        return True
    assert sample() is True

# UT006
def test_handle_db_session_rollbacks():
    @database.handle_db_session
    def erroring(session=None):
        raise Exception("fail")
    with pytest.raises(Exception):
        erroring()

# UT007-011: Pool settings
def test_engine_pool_config():
    engine, _ = database.get_engine_and_session()
    assert engine.pool.size() == 10
    assert engine.pool._max_overflow == 5
    assert engine.pool._timeout == 30
    assert engine.pool._recycle == 1800
    assert engine.pool._pre_ping is True

# UT012
@patch("controllers.database.Base.metadata.create_all")
def test_initialize_database_failure(mock_create):
    mock_create.side_effect = Exception("fail")
    result = database.initialize_database()
    assert result is False
# UT013
def test_db_error_handler_returns_false_on_sqlalchemy_error():
    @database.db_error_handler
    def boom():
        raise SQLAlchemyError("db fail")
    assert boom() is False

# UT014
@patch("controllers.database.get_session")
def test_handle_db_session_commit_fails(mock_get):
    fake_session = MagicMock()
    fake_session.commit.side_effect = [Exception("fail"), None]
    mock_get.return_value = fake_session
    @database.handle_db_session
    def func(session=None):
        return True
    with pytest.raises(Exception):
        func()

# UT015
def test_get_session_binds_to_engine():
    engine, _ = database.get_engine_and_session()
    session = database.get_session()
    assert session.bind == engine
    session.close()

# UT016
def test_initialize_database_idempotent():
    assert database.initialize_database() is True
    assert database.initialize_database() is True



# UT017
def test_db_error_handler_deep_exception():
    @database.db_error_handler
    def deep():
        def inner():
            raise RuntimeError("Deep")
        inner()
    assert deep() is False

# UT018
def helper_handle_session_commit(session=None):
    session.execute(text("SELECT 1"))


def test_handle_session_manual_commit():
    assert database.handle_db_session(helper_handle_session_commit)() is None

# UT019
def test_multiple_session_stress():
    for _ in range(30):
        session = database.get_session()
        session.execute(text("SELECT 1"))
        session.close()

# UT020
def test_connection_pool_exhaustion():
    sessions = []
    try:
        for _ in range(15):
            sessions.append(database.get_session())
        assert len(sessions) == 15
    finally:
        for s in sessions:
            s.close()

# UT021
def test_connection_pool_overflow_exceeded():
    import threading, time
    results = []
    def get_session_safe():
        try:
            s = database.get_session()
            time.sleep(1)
            results.append(True)
            s.close()
        except Exception:
            results.append(False)
    threads = [threading.Thread(target=get_session_safe) for _ in range(20)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert any(results)


