from memory.database.db import get_connection


def is_browser_allowed(browser_name):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT is_allowed
        FROM browser_permissions
        WHERE LOWER(browser_name) = LOWER(?)
    """, (browser_name,))

    row = cursor.fetchone()
    connection.close()

    return bool(row[0]) if row else False


def is_private_capture_allowed(browser_name):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT capture_private
        FROM browser_permissions
        WHERE LOWER(browser_name) = LOWER(?)
    """, (browser_name,))

    row = cursor.fetchone()
    connection.close()

    return bool(row[0]) if row else False


def is_domain_blocked(domain):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT 1
        FROM blocked_domains
        WHERE LOWER(?) = LOWER(domain)
           OR LOWER(?) LIKE '%.' || LOWER(domain)
    """, (domain, domain))

    row = cursor.fetchone()
    connection.close()

    return row is not None