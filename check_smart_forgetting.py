import sqlite3

db = "memory/smart_forgetting/recommendations.db"
conn = sqlite3.connect(db)

print("Prediction sources:")
for row in conn.execute("""
    SELECT prediction_source, COUNT(*)
    FROM recommendations
    GROUP BY prediction_source
"""):
    print(row)

print("\nLatest fallback results:")
for row in conn.execute("""
    SELECT file_name, label, reason, prediction_source
    FROM recommendations
    WHERE prediction_source IN ('ollama', 'fallback_error')
    ORDER BY last_scanned_at DESC
    LIMIT 10
"""):
    print(row)

conn.close()
