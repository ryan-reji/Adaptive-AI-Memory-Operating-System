from memory.capture.common.permissions import (
    add_allowed_folder,
    add_exclusion,
    add_project_folder,
    get_permission_mode,
    remove_allowed_folder,
    remove_exclusion,
    remove_project_folder,
    set_permission_mode,
)
from memory.database.db import get_connection


VALID_PERMISSION_MODES = {
    "allow_all",
    "allow_only",
}


def get_mode():
    return get_permission_mode()


def set_mode(mode):
    if mode not in VALID_PERMISSION_MODES:
        raise ValueError(
            "Permission mode must be 'allow_all' or 'allow_only'."
        )

    set_permission_mode(mode)
    return get_permission_mode()


def _get_folder_paths(table_name):
    allowed_tables = {
        "file_exclusions",
        "file_allowed_folders",
    }

    if table_name not in allowed_tables:
        raise ValueError("Unsupported folder table.")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        f"""
        SELECT path
        FROM {table_name}
        ORDER BY path ASC
        """
    )

    rows = cursor.fetchall()
    connection.close()

    return [
        {
            "path": row[0],
        }
        for row in rows
    ]


def get_exclusions():
    return _get_folder_paths("file_exclusions")


def add_file_exclusion(path):
    add_exclusion(path)
    return {
        "path": str(path),
    }


def remove_file_exclusion(path):
    remove_exclusion(path)


def get_allowed_folders():
    return _get_folder_paths("file_allowed_folders")


def add_file_allowed_folder(path):
    add_allowed_folder(path)
    return {
        "path": str(path),
    }


def remove_file_allowed_folder(path):
    remove_allowed_folder(path)


def get_project_folders():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            path,
            project_name
        FROM project_folders
        ORDER BY path ASC
        """
    )

    rows = cursor.fetchall()
    connection.close()

    return [
        {
            "path": row[0],
            "project_name": row[1],
        }
        for row in rows
    ]


def add_file_project_folder(path, project_name=None):
    add_project_folder(
        path,
        project_name=project_name,
    )

    return {
        "path": str(path),
        "project_name": project_name,
    }


def remove_file_project_folder(path):
    remove_project_folder(path)