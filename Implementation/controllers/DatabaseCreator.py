from sqlalchemy import inspect
from controllers.database import Base, get_engine_and_session
import controllers.tablemodel as models  # ensure all table classes are imported


def setup_database():
    """
    Optional initializer if you want to prepare config early.
    This ensures Base and engine are imported and linked properly.
    """
    # Already handled by `from controllers.database import Base, engine`
    pass

def init_postgres_db():
    """
    Initializes all tables in PostgreSQL using SQLAlchemy ORM definitions.

    - Requires: Parameters.SQLALCHEMY_DATABASE_URL already set
    - Creates all tables from models/tablemodel.py
    - Prints status for each table
    """
    engine, _ = get_engine_and_session()
    if not Base or not engine:
        raise RuntimeError("❌ Base or engine not initialized. Call get_engine_and_session() before this.")

    try:
        print("🔄 [DB] Creating tables defined in models...")
        Base.metadata.create_all(bind=engine)

        # Introspect tables to confirm what got created
        inspector = inspect(engine)
        created_tables = inspector.get_table_names()
        for table in created_tables:
            print(f"✅ [DB] Table available: {table}")

        print("🎉 All tables initialized successfully in PostgreSQL.")

    except Exception as e:
        print(f"❌ [DB] Table creation failed: {e}")
