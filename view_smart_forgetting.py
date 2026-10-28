import sqlite3

db = "memory/smart_forgetting/recommendations.db"
conn = sqlite3.connect(db)

print("=== SMART FORGETTING RESULTS ===")
for row in conn.execute("""
    SELECT file_name, file_path, label, reason,
           confidence, prediction_source, last_scanned_at
    FROM recommendations
    ORDER BY label, file_name
"""):
    print("\nFile:", row[0])
    print("Path:", row[1])
    print("Recommendation:", row[2].upper())
    print("Reason:", row[3])
    print("Confidence:", row[4])
    print("Source:", row[5])
    print("Last scanned:", row[6])

print("\n=== SUMMARY ===")
for row in conn.execute("""
    SELECT label, COUNT(*) FROM recommendations GROUP BY label
"""):
    print(f"{row[0]}: {row[1]}")

conn.close()
