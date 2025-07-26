import os
import paramiko
from dotenv import dotenv_values, load_dotenv
import psycopg2
import stat  # <-- ADD THIS
import json
from controllers.schema_manager import initialize_database
from urllib.parse import quote_plus
def check_server_and_license():
    # Load local .env to read server credentials
    load_dotenv()

    host = os.getenv("SERVER_HOST")
    port = int(os.getenv("SERVER_PORT", "22"))  # Optional, default 22
    username = os.getenv("SERVER_USER")
    password = os.getenv("SERVER_PASSWORD")

    # ✅ Correct path on the server
    remote_env_path = os.getenv("REMOTE_ENV_PATH")

    # ✅ Local destination (will create `cyphera` if not exists)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    cyphera_dir = os.path.join(base_dir, "cyphera")
    os.makedirs(cyphera_dir, exist_ok=True)

    local_env_path = os.path.join(cyphera_dir, ".env")

    try:
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        sftp.get(remote_env_path, local_env_path)
        print("✅ .env file fetched successfully.")

        sftp.close()
        transport.close()

        return True, "Connected and verified"
    except Exception as e:
        return False, f"Server or license check failed: {e}"

# utils/server_connection.py

def create_remote_project_folder(project_name: str) -> bool:
    host = os.getenv("SERVER_HOST")
    port = int(os.getenv("SERVER_PORT", 22))
    username = os.getenv("SERVER_USER")
    password = os.getenv("SERVER_PASSWORD")
    base_path = os.getenv("REMOTE_BASE_PATH")

    project_path = f"{base_path}/{project_name}"

    try:
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        try:
            sftp.stat(project_path)
            print(f"ℹ️ Folder already exists: {project_path}")
        except IOError:
            sftp.mkdir(project_path)
            print(f"✅ Created folder: {project_path}")

        sftp.close()
        transport.close()
        return True

    except Exception as e:
        print(f"❌ SFTP folder creation failed: {e}")
        return False


# utils/server_connection.py (continued)
def create_remote_config_structure(project_name: str) -> bool:
    base_path = os.getenv("REMOTE_BASE_PATH")
    host = os.getenv("SERVER_HOST")
    port = int(os.getenv("SERVER_PORT", 22))
    username = os.getenv("SERVER_USER")
    password = os.getenv("SERVER_PASSWORD")

    project_dir = f"{base_path}/{project_name}"
    config_path = f"{project_dir}/config"

    try:
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        sftp.mkdir(config_path)
        sftp.file(f"{project_dir}/README.md", 'w').close()
        sftp.file(f"{project_dir}/requirements.txt", 'w').close()

        sftp.close()
        transport.close()
        print("✅ Remote config folder and files created.")
        return True

    except Exception as e:
        print(f"❌ Failed to create remote structure: {e}")
        return False


# utils/server_connection.py (continued)


def create_postgres_database_for_project(project_name: str, env_vars: dict) -> str | None:
    try:
        import models.Parameters as P
        from controllers.database import get_engine_and_session, initialize_database

        # 1. Load DB credentials from env_vars
        db_user = env_vars.get("DB_USER")
        db_password = env_vars.get("DB_PASSWORD")
        db_host = env_vars.get("DB_HOST")
        db_port = env_vars.get("DB_PORT", "5432")

        # 2. Connect to default 'postgres' DB to create new one
        conn = psycopg2.connect(
            dbname="postgres",
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (project_name,))
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE \"{project_name}\"")
            print(f"✅ Created PostgreSQL DB: {project_name}")
        else:
            print(f"ℹ️ Database '{project_name}' already exists.")

        cur.close()
        conn.close()

        # 3. Setup SQLAlchemy config to point to the new DB
        P.db_type = "postgres"
        P.db_user = db_user
        P.db_password = db_password
        P.db_host = db_host
        P.db_port = db_port
        P.current_db_name = project_name
        password_encoded = quote_plus(db_password)

        P.SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{password_encoded}@{db_host}:{db_port}/{project_name}"

        # 4. Initialize engine + create all tables defined in Base.metadata
        get_engine_and_session()
        initialize_database()

        return P.SQLALCHEMY_DATABASE_URL

    except Exception as e:
        print(f"❌ PostgreSQL DB creation failed: {e}")
        return None


# utils/server_connection.py (continued)
def write_remote_tara_config(project_name: str, config_dict: dict) -> bool:

    host = os.getenv("SERVER_HOST")
    port = int(os.getenv("SERVER_PORT", 22))
    username = os.getenv("SERVER_USER")
    password = os.getenv("SERVER_PASSWORD")
    base_path = os.getenv("REMOTE_BASE_PATH")

    remote_config_path = f"{base_path}/{project_name}/{project_name}.tara"
    json_bytes = json.dumps(config_dict, indent=4).encode('utf-8')

    try:
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        with sftp.file(remote_config_path, 'w') as remote_file:
            remote_file.write(json_bytes)
        print(f"✅ .tara config written to: {remote_config_path}")

        sftp.close()
        transport.close()
        return True

    except Exception as e:
        print(f"❌ Failed to write .tara config: {e}")
        return False

def get_sftp():
    from dotenv import load_dotenv
    load_dotenv()
    host = os.getenv("SERVER_HOST")
    port = int(os.getenv("SERVER_PORT", 22))
    username = os.getenv("SERVER_USER")
    password = os.getenv("SERVER_PASSWORD")
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    return transport, sftp  # <--- You need both to close later!


def list_cloud_folders_with_sftp(sftp, base=None):
    base_path = base or os.getenv("REMOTE_BASE_PATH")
    folders = []
    for entry in sftp.listdir_attr(base_path):
        if stat.S_ISDIR(entry.st_mode) and not entry.filename.startswith('.'):
            folders.append(entry.filename)
    return sorted(folders)

def list_cloud_files_with_sftp(sftp, folder, base=None):
    base_path = base or os.getenv("REMOTE_BASE_PATH")
    path = base_path.rstrip("/") + "/" + folder
    items = sftp.listdir_attr(path)
    folders = [f.filename for f in items if stat.S_ISDIR(f.st_mode) and not f.filename.startswith('.')]
    tara_files = [f.filename for f in items if f.filename.lower().endswith(".tara") and not stat.S_ISDIR(f.st_mode)]
    other_files = [f.filename for f in items if not f.filename.lower().endswith(".tara") and not stat.S_ISDIR(f.st_mode) and not f.filename.startswith('.')]
    return folders + tara_files + other_files


def fetch_env_from_server():
    """
    Fetches the remote /../..cyphera/.env to local ./cyphera/.env.
    Returns: True if fetched, False if error.
    """
    from dotenv import load_dotenv
    load_dotenv()  # Load local creds for SFTP

    host = os.getenv("SERVER_HOST")
    port = int(os.getenv("SERVER_PORT", "22"))
    username = os.getenv("SERVER_USER")
    password = os.getenv("SERVER_PASSWORD")

    remote_env_path = os.getenv("REMOTE_ENV_PATH")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    cyphera_dir = os.path.join(base_dir, "cyphera")
    os.makedirs(cyphera_dir, exist_ok=True)
    local_env_path = os.path.join(cyphera_dir, ".env")

    try:
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get(remote_env_path, local_env_path)
        sftp.close()
        transport.close()
        print("✅ .env file fetched successfully.")
        return True
    except Exception as e:
        print(f"❌ Failed to fetch .env: {e}")
        return False


def read_local_env():
    """
    Loads ./cyphera/.env and returns it as a dict (using dotenv_values).
    """
    from dotenv import dotenv_values
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    local_env_path = os.path.join(base_dir, "cyphera", ".env")
    env_vars = dotenv_values(local_env_path)
    if not env_vars:
        print(f"❌ Could not load env from {local_env_path}")
    return env_vars


def get_db_env_vars():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    local_env_path = os.path.join(base_dir, "cyphera", ".env")
    env_vars = dotenv_values(local_env_path)
    return env_vars

def connect_postgres_and_print_tables(db_name):
    env_vars = get_db_env_vars()
    db_user = env_vars.get("DB_USER")
    db_password = env_vars.get("DB_PASSWORD")
    db_host = env_vars.get("DB_HOST")
    db_port = env_vars.get("DB_PORT", "5434")  # Your default port per screenshot

    db_url = f"{db_host}:{db_port}/{db_name}"
    print(f"🔍 [DEBUG] Connecting to DB at: {db_url}")
    print(f"🔍 [DEBUG] Username: {db_user}")

    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'
        """)
        tables = cur.fetchall()
        print(f"📦 [DEBUG] Tables in DB '{db_name}':")
        for t in tables:
            print("   -", t[0])
        cur.close()
        conn.close()
        print(f"✅ [DEBUG] Connected successfully to: {db_url}")
        return True
    except Exception as e:
        print(f"❌ [DEBUG] DB Connection failed ({db_url}): {e}")
        return False