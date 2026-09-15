import sqlite3
from datetime import datetime

DB_PATH = "memory/database/memory.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    # Activity storage
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT NOT NULL,
            source_path TEXT,
            title TEXT,
            content TEXT,
            captured_at TEXT NOT NULL
        )
    """)

    # Memory storage
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            context TEXT,
            importance_score REAL,
            status TEXT DEFAULT 'active',
            created_at TEXT NOT NULL
        )
    """)

    # Browser permissions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS browser_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            browser_name TEXT NOT NULL UNIQUE,
            is_allowed INTEGER NOT NULL DEFAULT 0,
            capture_private INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # Blocked domains
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blocked_domains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL UNIQUE,
            reason TEXT,
            created_at TEXT NOT NULL
        )
    """)
    cursor.execute("""
     CREATE TABLE IF NOT EXISTS browser_activity (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity_key TEXT NOT NULL UNIQUE,
        browser TEXT NOT NULL,
        title TEXT NOT NULL,
        total_duration_seconds REAL NOT NULL DEFAULT 0,
        session_count INTEGER NOT NULL DEFAULT 0,
        first_seen TEXT NOT NULL,
        last_seen TEXT NOT NULL
     )
    """)
    cursor.execute("""
     CREATE TABLE IF NOT EXISTS vscode_activity (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity_key TEXT NOT NULL UNIQUE,
        project TEXT NOT NULL,
        file TEXT,
        total_duration_seconds REAL NOT NULL DEFAULT 0,
        session_count INTEGER NOT NULL DEFAULT 0,
        first_seen TEXT NOT NULL,
        last_seen TEXT NOT NULL
     )
    """)
        # File daily activity history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS file_daily_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_id INTEGER NOT NULL,
            activity_date TEXT NOT NULL,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            duration_seconds REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (activity_id) REFERENCES activities(id),
            UNIQUE(activity_id, activity_date)
        )
    """)

    # Browser daily activity history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS browser_daily_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_id INTEGER NOT NULL,
            activity_date TEXT NOT NULL,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            duration_seconds REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (activity_id) REFERENCES browser_activity(id),
            UNIQUE(activity_id, activity_date)
        )
    """)

    # VS Code daily activity history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vscode_daily_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_id INTEGER NOT NULL,
            activity_date TEXT NOT NULL,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            duration_seconds REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (activity_id) REFERENCES vscode_activity(id),
            UNIQUE(activity_id, activity_date)
        )
    """)

    # Default browser permissions
    browsers = ["Chrome", "Brave", "Edge", "Firefox"]
    now = datetime.now().isoformat()

    for browser in browsers:
        cursor.execute("""
            INSERT OR IGNORE INTO browser_permissions
            (browser_name, is_allowed, capture_private, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            browser,
            1,
            0,
            now,
            now
        ))

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully.")