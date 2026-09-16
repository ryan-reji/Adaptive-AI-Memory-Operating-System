from pathlib import Path
import os
from datetime import datetime

from memory.database.db import get_connection


# ---------------------------------------------------------
# Built-in protected folders
# ---------------------------------------------------------

def get_protected_folders():
    """
    Return Windows system and application locations
    that should never be captured.
    """

    system_drive = Path(
        os.environ.get("SystemDrive", "C:") + "\\"
    )

    return [
        system_drive / "Windows",
        system_drive / "Program Files",
        system_drive / "Program Files (x86)",
        system_drive / "ProgramData",
        system_drive / "$Recycle.Bin",
        system_drive / "System Volume Information",
    ]


def is_protected(file_path):
    """
    Check whether a path belongs to a built-in protected
    Windows location.
    """

    file_path = Path(file_path).resolve()

    for folder in get_protected_folders():
        folder = folder.resolve()

        try:
            file_path.relative_to(folder)
            return True
        except ValueError:
            continue

    return False


# ---------------------------------------------------------
# Permission mode
# ---------------------------------------------------------

def get_permission_mode():
    """
    Get the current file permission mode from SQLite.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT permission_mode
        FROM file_permission_settings
        WHERE id = 1
    """)

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return "allow_all"

    return row[0]


def set_permission_mode(mode):
    """
    Set the file permission mode.

    Supported modes:
    - allow_all
    - allow_only
    """

    if mode not in ("allow_all", "allow_only"):
        raise ValueError(
            "Permission mode must be 'allow_all' or 'allow_only'."
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE file_permission_settings
        SET
            permission_mode = ?,
            updated_at = ?
        WHERE id = 1
    """, (
        mode,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


# ---------------------------------------------------------
# User-configured exclusions
# ---------------------------------------------------------

def is_excluded(file_path):
    """
    Check whether a path has been excluded by the user.
    """

    file_path = Path(file_path).resolve()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT path
        FROM file_exclusions
    """)

    excluded_paths = cursor.fetchall()

    connection.close()

    for row in excluded_paths:
        folder = Path(row[0]).resolve()

        try:
            file_path.relative_to(folder)
            return True
        except ValueError:
            continue

    return False


def add_exclusion(folder_path):
    """
    Add a folder to the user's exclusion list.
    """

    folder_path = str(Path(folder_path).resolve())

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO file_exclusions (
            path,
            created_at
        )
        VALUES (?, ?)
    """, (
        folder_path,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


def remove_exclusion(folder_path):
    """
    Remove a folder from the user's exclusion list.
    """

    folder_path = str(Path(folder_path).resolve())

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM file_exclusions
        WHERE path = ?
    """, (folder_path,))

    connection.commit()
    connection.close()


# ---------------------------------------------------------
# User-approved folders
# ---------------------------------------------------------

def is_in_allowed_folder(file_path):
    """
    Check whether a file belongs to a user-approved folder.
    """

    file_path = Path(file_path).resolve()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT path
        FROM file_allowed_folders
    """)

    allowed_paths = cursor.fetchall()

    connection.close()

    for row in allowed_paths:
        folder = Path(row[0]).resolve()

        try:
            file_path.relative_to(folder)
            return True
        except ValueError:
            continue

    return False


def add_allowed_folder(folder_path):
    """
    Add a folder to the user's allowed list.
    """

    folder_path = str(Path(folder_path).resolve())

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO file_allowed_folders (
            path,
            created_at
        )
        VALUES (?, ?)
    """, (
        folder_path,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


def remove_allowed_folder(folder_path):
    """
    Remove a folder from the user's allowed list.
    """

    folder_path = str(Path(folder_path).resolve())

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM file_allowed_folders
        WHERE path = ?
    """, (folder_path,))

    connection.commit()
    connection.close()


# ---------------------------------------------------------
# Permission check
# ---------------------------------------------------------

def is_allowed(file_path):
    """
    Determine whether a file can be captured.

    Permission priority:

    1. Built-in protected paths → BLOCK
    2. Active project folders → ALLOW
    3. User exclusions → BLOCK
    4. allow_all → ALLOW
    5. allow_only → Check allowed folders
    """

    file_path = Path(file_path).resolve()

    # Built-in protection always wins.
    if is_protected(file_path):
        return False

    # Active projects override user exclusions.
    if is_in_project_folder(file_path):
        return True

    # User exclusions apply next.
    if is_excluded(file_path):
        return False

    mode = get_permission_mode()

    if mode == "allow_all":
        return True

    if mode == "allow_only":
        return is_in_allowed_folder(file_path)

    return False


def is_in_project_folder(file_path):
    """
    Check whether a file belongs to an active project folder.
    """

    file_path = Path(file_path).resolve()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT path
        FROM project_folders
    """)

    project_paths = cursor.fetchall()
    connection.close()

    for row in project_paths:
        folder = Path(row[0]).resolve()

        try:
            file_path.relative_to(folder)
            return True
        except ValueError:
            continue

    return False


def add_project_folder(folder_path, project_name=None):
    """
    Add a folder to the active project folders.
    """

    folder_path = str(Path(folder_path).resolve())

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO project_folders (
            path,
            project_name,
            created_at
        )
        VALUES (?, ?, ?)
    """, (
        folder_path,
        project_name,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


def remove_project_folder(folder_path):
    """
    Remove a folder from the active project folders.
    """

    folder_path = str(Path(folder_path).resolve())

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM project_folders
        WHERE path = ?
    """, (folder_path,))

    connection.commit()
    connection.close()

# ---------------------------------------------------------
# Basic test
# ---------------------------------------------------------

if __name__ == "__main__":

    test_file = "memory/tests/test_data/test.pdf"

    print("Test file:", test_file)
    print("Permission mode:", get_permission_mode())
    print("Protected:", is_protected(test_file))
    print("Excluded:", is_excluded(test_file))
    print("Allowed folder:", is_in_allowed_folder(test_file))
    print("Allowed:", is_allowed(test_file))