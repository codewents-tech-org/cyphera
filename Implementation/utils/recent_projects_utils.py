import os
import json
import uuid
from datetime import datetime

RECENT_JSON_PATH = "tmp/recent_projects.json"


def _ensure_file():
    os.makedirs(os.path.dirname(RECENT_JSON_PATH), exist_ok=True)
    if not os.path.exists(RECENT_JSON_PATH):
        with open(RECENT_JSON_PATH, "w") as f:
            json.dump([], f)


def load_recent_projects():
    _ensure_file()
    with open(RECENT_JSON_PATH, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_recent_projects(data):
    _ensure_file()
    with open(RECENT_JSON_PATH, "w") as f:
        json.dump(data, f, indent=4)


def add_or_update_project(name, path, mode="local", db_url=None):
    _ensure_file()
    projects = load_recent_projects()
    path = path.strip()

    # Try to find existing entry
    existing = next((p for p in projects if p["path"] == path and p["mode"] == mode), None)

    if existing:
        existing["last_opened"] = datetime.now().isoformat()
        existing["name"] = name  # In case name changed
        if db_url:
            existing["db_url"] = db_url
    else:
        project_entry = {
            "uuid": str(uuid.uuid4()),
            "name": name,
            "path": path,
            "mode": mode,
            "last_opened": datetime.now().isoformat()
        }
        if db_url:
            project_entry["db_url"] = db_url

        projects.append(project_entry)

    save_recent_projects(projects)


def remove_project(path):
    _ensure_file()
    path = path.strip()
    projects = load_recent_projects()
    filtered = [p for p in projects if p["path"] != path]
    save_recent_projects(filtered)
