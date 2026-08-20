from database.db import get_connection


connection = get_connection()
cursor = connection.cursor()

cursor.execute("SELECT id, source_type, title, captured_at FROM activities")

rows = cursor.fetchall()

for row in rows:
    print(row)

connection.close()