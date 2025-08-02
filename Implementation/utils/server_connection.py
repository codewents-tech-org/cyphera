import os
import json
import stat
import paramiko
import psycopg2
from dotenv import dotenv_values, load_dotenv
from urllib.parse import quote_plus
from controllers.schema_manager import initialize_database
import models.Parameters as P
from controllers.database import get_engine_and_session

def check_server_and_license():
    load_dotenv()

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
        print("✅ .env file fetched successfully.")

        # 🔐 Store the session globally
        P.ssh_transport = transport
        P.sftp = sftp

        return True, "Connected and verified"
    except Exception as e:
        print(f"[ERROR] check_server_and_license(): {type(e).__name__} - {e}")
        return False, f"Server or license check failed: {e}"


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

        # 🔐 Store session
        P.ssh_transport = transport
        P.sftp = sftp

        return True

    except Exception as e:
        print(f"❌ SFTP folder creation failed: {e}")
        return False


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

        # 🔐 Store session
        P.ssh_transport = transport
        P.sftp = sftp

        print("✅ Remote config folder and files created.")
        return True

    except Exception as e:
        print(f"❌ Failed to create remote structure: {e}")
        return False


def create_postgres_database_for_project(project_name: str, env_vars: dict) -> str | None:
    try:
        db_user = env_vars.get("DB_USER")
        db_password = env_vars.get("DB_PASSWORD")
        db_host = env_vars.get("DB_HOST")
        db_port = env_vars.get("DB_PORT", "5432")

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

        password_encoded = quote_plus(db_password)
        db_url = f"postgresql://{db_user}:{password_encoded}@{db_host}:{db_port}/{project_name}"

        # 🔗 Set Parameters globally
        P.db_type = "postgres"
        P.db_user = db_user
        P.db_password = db_password
        P.db_host = db_host
        P.db_port = db_port
        P.current_db_name = project_name
        P.SQLALCHEMY_DATABASE_URL = db_url

        get_engine_and_session()
        initialize_database()

        return db_url

    except Exception as e:
        print(f"❌ PostgreSQL DB creation failed: {e}")
        return None


def write_remote_tara_config(project_name: str, config_dict: dict) -> bool:
    try:
        _, sftp = get_sftp()
        remote_config_path = f"{os.getenv('REMOTE_BASE_PATH')}/{project_name}/{project_name}.tara"
        json_bytes = json.dumps(config_dict, indent=4).encode('utf-8')

        with sftp.file(remote_config_path, 'w') as remote_file:
            remote_file.write(json_bytes)
        print(f"✅ .tara config written to: {remote_config_path}")

        return True

    except Exception as e:
        print(f"❌ Failed to write .tara config: {e}")
        return False


def get_sftp():
    if hasattr(P, "sftp") and P.sftp and hasattr(P, "ssh_transport") and P.ssh_transport:
        return P.ssh_transport, P.sftp

    host = os.getenv("SERVER_HOST")
    port = int(os.getenv("SERVER_PORT", 22))
    username = os.getenv("SERVER_USER")
    password = os.getenv("SERVER_PASSWORD")
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    P.ssh_transport = transport
    P.sftp = sftp
    return transport, sftp


def close_ssh_session():
    if hasattr(P, "sftp") and P.sftp:
        P.sftp.close()
        P.sftp = None
    if hasattr(P, "ssh_transport") and P.ssh_transport:
        P.ssh_transport.close()
        P.ssh_transport = None


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
    tara_files = [f.filename for f in items if f.filename.lower().endswith(".tara")]
    other_files = [f.filename for f in items if not f.filename.lower().endswith(".tara") and not stat.S_ISDIR(f.st_mode)]
    return folders + tara_files + other_files


def fetch_env_from_server():
    load_dotenv()

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
        transport, sftp = get_sftp()
        sftp.get(remote_env_path, local_env_path)
        print("✅ .env file fetched successfully.")
        return True
    except Exception as e:
        print(f"❌ Failed to fetch .env: {e}")
        return False


def read_local_env():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    local_env_path = os.path.join(base_dir, "cyphera", ".env")
    env_vars = dotenv_values(local_env_path)
    if not env_vars:
        print(f"❌ Could not load env from {local_env_path}")
    return env_vars


def get_db_env_vars():
    print("🌐 [DEBUG] Attempting to fetch remote .env...")
    if not fetch_env_from_server():
        print("❌ [ERROR] Could not fetch remote .env.")
        return {}

    local_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cyphera", ".env"))
    print(f"📂 [DEBUG] Reading fetched .env from: {local_env_path}")

    try:
        with open(local_env_path, "rb") as f:
            raw_bytes = f.read()
            print("📜 [DEBUG] .env RAW BYTES:\n", repr(raw_bytes))
    except Exception as e:
        print("❌ [DEBUG] Failed to read .env:", e)
        return {}

    env_vars = dotenv_values(local_env_path)
    print("🔍 [DEBUG] Parsed DB environment variables:", env_vars)
    return env_vars


def connect_postgres_and_print_tables(db_name):
    env_vars = get_db_env_vars()
    db_user = env_vars.get("DB_USER")
    db_password = env_vars.get("DB_PASSWORD")
    db_host = env_vars.get("DB_HOST")
    db_port = env_vars.get("DB_PORT", "5434")

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
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
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
