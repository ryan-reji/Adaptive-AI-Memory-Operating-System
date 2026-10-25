
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


def _parse_details(value):
    if isinstance(value, dict):
        return value
    try:
        return json.loads(value or "{}")
    except (TypeError, ValueError):
        return {}


def _classify_file(path):
    ext = path.suffix.lower()

    categories = {
        "source_code_configuration": {
            ".py", ".js", ".ts", ".tsx", ".jsx", ".java",
            ".c", ".cpp", ".h", ".cs", ".php", ".html",
            ".css", ".json", ".yaml", ".yml", ".toml",
            ".ini", ".env", ".sql", ".sh", ".bat"
        },
        "documents": {
            ".pdf", ".doc", ".docx", ".txt", ".rtf",
            ".md", ".ppt", ".pptx", ".xls", ".xlsx", ".csv"
        },
        "images": {
            ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"
        },
        "archives_backups": {
            ".zip", ".rar", ".7z", ".tar", ".gz", ".bak"
        },
        "temporary_generated": {
            ".tmp", ".temp", ".log", ".cache", ".pyc"
        },
        "installers": {
            ".exe", ".msi", ".msix", ".apk", ".dmg"
        },
    }

    for category, extensions in categories.items():
        if ext in extensions:
            return category

    if ext in {".mp4", ".mkv", ".avi", ".mov"}:
        return "videos"

    return "other"


def _folder_category(path):
    parts = {part.lower() for part in path.parts}

    if "downloads" in parts:
        return "Downloads"
    if "desktop" in parts:
        return "Desktop"
    if "documents" in parts:
        return "Documents"
    if "pictures" in parts:
        return "Pictures"
    if "videos" in parts:
        return "Videos"
    if "appdata" in parts:
        return "AppData"
    if "windows" in parts or "program files" in parts:
        return "SystemOrInstalledApp"
    if any(part in parts for part in {"backup", "backups"}):
        return "BackupDriveOrFolder"
    if any(part in parts for part in {".git", "src", "project", "projects"}):
        return "Project"

    return "Other"


def _is_temporary(path):
    name = path.name.lower()
    ext = path.suffix.lower()

    return (
        ext in {".tmp", ".temp", ".cache", ".pyc", ".part"}
        or name.startswith("~$")
        or name.endswith(".tmp")
    )


def _is_installer(path):
    return path.suffix.lower() in {
        ".exe", ".msi", ".msix", ".dmg", ".apk", ".deb", ".rpm"
    }


def extract_features(file_path, db_path, now=None):
    """
    Build the feature dictionary expected by the trained model.

    Activity timestamps are used as observed activity, not guaranteed
    filesystem access timestamps.
    """
    now = now or datetime.now()
    path = Path(file_path).expanduser().resolve()

    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    stat = path.stat()
    ext = path.suffix.lower() or "<no_extension>"

    first_seen = datetime.fromtimestamp(stat.st_ctime)
    modified = datetime.fromtimestamp(stat.st_mtime)

    access_timestamps = []
    modification_count_30d = 0
    actions = []

    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row

    try:
        rows = connection.execute("""
            SELECT timestamp, action, details, source_type
            FROM activity_evidence
            WHERE source_type = 'file'
            ORDER BY timestamp DESC
        """).fetchall()
    finally:
        connection.close()

    target_path = str(path).casefold()

    for row in rows:
        details = _parse_details(row["details"])
        recorded_path = details.get("source_path")

        if not recorded_path:
            continue

        try:
            same_path = (
                str(Path(recorded_path).expanduser().resolve()).casefold()
                == target_path
            )
        except (OSError, ValueError):
            same_path = str(recorded_path).casefold() == target_path

        if not same_path:
            continue

        try:
            timestamp = datetime.fromisoformat(row["timestamp"])
        except (TypeError, ValueError):
            continue

        actions.append(row["action"] or "unknown")

        if timestamp >= now - timedelta(days=90):
            access_timestamps.append(timestamp)

        if (
            timestamp >= now - timedelta(days=30)
            and row["action"] == "modified"
        ):
            modification_count_30d += 1

    recent_30 = sum(
        timestamp >= now - timedelta(days=30)
        for timestamp in access_timestamps
    )

    recent_90 = len(access_timestamps)

    latest_observed = max(access_timestamps, default=None)

    # Filesystem access time can be unreliable on Windows.
    # Use recorded activity when available; otherwise use mtime.
    last_activity = latest_observed or modified
    days_since_last_access = max(
        0, (now - last_activity).days
    )

    file_age_days = max(0, (now - first_seen).days)

    folder = _folder_category(path)
    protected_hint = (
        folder in {"AppData", "SystemOrInstalledApp"}
        or any(part.lower() == "windows" for part in path.parts)
    )

    # Conservative starter heuristics. These are not user-confirmed labels.
    if protected_hint:
        importance = "high"
        project_relevance = "high"
    elif folder == "Project":
        importance = "high"
        project_relevance = "high"
    elif recent_30 > 0:
        importance = "high"
        project_relevance = "medium"
    elif recent_90 == 0 and file_age_days > 90:
        importance = "low"
        project_relevance = "low"
    else:
        importance = "medium"
        project_relevance = "unknown"

    if actions:
        action = actions[0]
    else:
        action = "modified" if modified >= now - timedelta(days=30) else "unknown"

    known_metadata = sum([
        bool(path.name),
        bool(ext),
        stat.st_size >= 0,
        bool(folder),
        bool(actions),
    ])

    return {
        "file_size_bytes": float(stat.st_size),
        "file_age_days": float(file_age_days),
        "days_since_last_access": float(days_since_last_access),
        "access_count_90d": int(recent_90),
        "access_count_30d": int(recent_30),
        "modification_count_30d": float(modification_count_30d),
        "file_extension": ext,
        "file_category": _classify_file(path),
        "project_relevance": project_relevance,
        "action": action,
        "importance_indicator": importance,
        "is_temporary": str(_is_temporary(path)).lower(),
        "is_installer": str(_is_installer(path)).lower(),
        "metadata_completeness": float(known_metadata / 5),
        "source_type": "file",
    }
