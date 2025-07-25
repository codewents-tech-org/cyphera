import os
from dotenv import load_dotenv

load_dotenv("tool.env")  # ✅ your EXE-side env

def resolve_database_path_from_server(project_name: str) -> str:
    """
    Returns connection string for SQLite or PostgreSQL dynamically.
    """

    db_type = os.getenv("DB_TYPE", "sqlite")

    if db_type.lower() == "sqlite":
        from pathlib import Path
        base_path = Path(os.getenv("PROJECT_FOLDER", ".")) / project_name / "config"
        base_path.mkdir(parents=True, exist_ok=True)
        return str(base_path / f"{project_name}.db")

    elif db_type.lower() == "postgres":
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT", "5432")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")

        # Use project-specific DB name
        db_name = f"{project_name}"

        # 🔐 Create DB if not exists
        import psycopg2
        try:
            conn = psycopg2.connect(
                dbname="postgres", user=user, password=password, host=host, port=port
            )
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
            exists = cur.fetchone()
            if not exists:
                cur.execute(f"CREATE DATABASE {db_name}")
                print(f"✅ Created new DB: {db_name}")
            else:
                print(f"ℹ️ DB already exists: {db_name}")
            cur.close()
            conn.close()
        except Exception as e:
            print(f"❌ Could not create DB: {e}")
            raise

        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"

    else:
        raise ValueError("Unsupported DB_TYPE in .env")
