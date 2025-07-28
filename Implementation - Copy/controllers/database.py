"""
📦 Module        : database.py
🧱 Layer         : controllers
🔖 Module ID     : 
📋 Requirement ID(s): 
🧑‍💻 Developed By : Vijay
🕒 Created On    : 2025-05-14
🧾 File Version  : v1.0.5
🧾 Updated by    : GPT-4
🧾 Updated on    : 2025-07-16

🧠 Description:
This module manages SQLAlchemy engine, sessions, and ORM base for both PostgreSQL and SQLite.

🎯 Responsibilities:
- Setup SQLAlchemy engine from dynamic URL in Parameters
- Automatically choose config for SQLite or PostgreSQL
- Create session factory
- Manage schema creation from tablemodels
- Provide decorators for safe DB usage
"""

import functools
import traceback
import importlib
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import models.Parameters as P
import uuid
import inspect as pyinspect
# ---------------------------------------------------------------------
# Declarative Base and Global Placeholders
# ---------------------------------------------------------------------

Base = declarative_base()
_engine = None
_SessionLocal = None

# ---------------------------------------------------------------------
# Engine and Session Setup (SQLite or PostgreSQL)
# ---------------------------------------------------------------------

def get_engine_and_session():
    """
    Initializes engine and session factory based on Parameters.SQLALCHEMY_DATABASE_URL.

    Returns:
        tuple: (engine, session factory)
    """
    global _engine, _SessionLocal
    print("check get engine and session working--------------------------------")
    if not P.SQLALCHEMY_DATABASE_URL:
        raise ValueError("❌ Missing Parameters.SQLALCHEMY_DATABASE_URL. Cannot initialize DB.")

    if P.SQLALCHEMY_DATABASE_URL.startswith("sqlite:///"):
        # ✅ SQLite engine (no pool settings)
        _engine = create_engine(
            P.SQLALCHEMY_DATABASE_URL,
            echo=False,
            connect_args={"check_same_thread": False}
        )
    else:
        # ✅ PostgreSQL engine (with pool settings)
        _engine = create_engine(
            P.SQLALCHEMY_DATABASE_URL,
            echo=False,
            pool_size=10,
            max_overflow=5,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True
        )

    _SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=_engine
    )

    return _engine, _SessionLocal

def get_session():
    """
    Returns a SQLAlchemy session. Requires get_engine_and_session() first.

    Returns:
        sqlalchemy.orm.Session
    """
    if not _SessionLocal:
        raise RuntimeError("Session factory not initialized. Call get_engine_and_session() first.")
    return _SessionLocal()

# ---------------------------------------------------------------------
# Table Initialization
# ---------------------------------------------------------------------

def initialize_database():
    """
    Imports tablemodel module and initializes all ORM tables
    using SQLAlchemy Base metadata.

    Returns:
        bool: True if tables created successfully, False otherwise.
    """
    try:
        print("🔄 [DB Init] Importing ORM models and creating tables...")
        importlib.import_module("controllers.tablemodel")

        for table in Base.metadata.sorted_tables:
            table_name = table.name
            try:
                print(f"🔧 Creating table: {table_name} ...", end=" ")
                table.create(bind=_engine, checkfirst=True)
                print("✅ Done")
            except Exception as table_err:
                print(f"❌ Failed: {table_err}")

        print("✅ All available ORM tables processed.\n")
        return True
    except Exception as e:
        print(f"[DB Init Error] {e}")
        traceback.print_exc()
        return False

# ---------------------------------------------------------------------
# Decorators for DB Safety
# ---------------------------------------------------------------------

def db_error_handler(func):
    """
    Decorator for safely wrapping DB logic with try/except and stacktrace logging.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"❌ Error in {func.__name__}: {e}")
            traceback.print_exc()
            return False
    return wrapper

def handle_db_session(func):
    """
    Decorator that logs and manages DB session lifecycle, useful for debugging locks.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        session = get_session()
        session_id = str(uuid.uuid4())[:8]  # Short trace ID
        caller = pyinspect.stack()[1].function  # Who called this wrapper

        print(f"[🔓 OPEN] Session {session_id} started by '{func.__name__}' (called from '{caller}')")

        try:
            result = func(*args, session=session, **kwargs)
            session.commit()
            print(f"[✅ COMMIT] Session {session_id} committed in '{func.__name__}'")
            return result
        except SQLAlchemyError as e:
            session.rollback()
            print(f"[❌ ROLLBACK] Session {session_id} rolled back in '{func.__name__}' due to error: {e}")
            raise
        finally:
            session.close()
            print(f"[🔒 CLOSE] Session {session_id} closed from '{func.__name__}'\n")

    return wrapper