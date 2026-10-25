
import sqlite3
import time
from datetime import datetime, timedelta, timezone

from memory.smart_forgetting.config import RECOMMENDATIONS_DB_PATH
from memory.smart_forgetting.pipeline import SmartForgettingPipeline


SCAN_INTERVAL_HOURS = 12
RETRY_INTERVAL_SECONDS = 300
MAX_SLEEP_SECONDS = 300


def initialize_state_db():
    RECOMMENDATIONS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(str(RECOMMENDATIONS_DB_PATH)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS smart_forgetting_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)


def get_last_successful_scan():
    with sqlite3.connect(str(RECOMMENDATIONS_DB_PATH)) as conn:
        row = conn.execute(
            """
            SELECT value
            FROM smart_forgetting_state
            WHERE key = 'last_successful_scan'
            """
        ).fetchone()

    if not row:
        return None

    return datetime.fromisoformat(row[0])


def save_successful_scan(timestamp):
    with sqlite3.connect(str(RECOMMENDATIONS_DB_PATH)) as conn:
        conn.execute(
            """
            INSERT INTO smart_forgetting_state (key, value)
            VALUES ('last_successful_scan', ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (timestamp.isoformat(),),
        )


def run_forever():
    initialize_state_db()

    print("[Smart Forgetting] Background runner started.")
    print(f"[Smart Forgetting] Scan interval: {SCAN_INTERVAL_HOURS} hours.")

    pipeline = SmartForgettingPipeline()
    interval = timedelta(hours=SCAN_INTERVAL_HOURS)

    while True:
        last_scan = get_last_successful_scan()
        now = datetime.now(timezone.utc)

        if last_scan is None:
            print("[Smart Forgetting] First run: starting initial scan.")
        else:
            # Handle timestamps saved by this runner in UTC.
            if last_scan.tzinfo is None:
                last_scan = last_scan.replace(tzinfo=timezone.utc)

            next_scan = last_scan + interval
            remaining = (next_scan - now).total_seconds()

            if remaining > 0:
                sleep_seconds = min(remaining, MAX_SLEEP_SECONDS)
                print(
                    f"[Smart Forgetting] Next scan due in "
                    f"{remaining / 3600:.2f} hours."
                )
                time.sleep(sleep_seconds)
                continue

            print("[Smart Forgetting] 12-hour interval elapsed.")

        try:
            pipeline.run()

            # Update the timer only after the pipeline completes.
            completed_at = datetime.now(timezone.utc)
            save_successful_scan(completed_at)

            print(
                "[Smart Forgetting] Scan completed successfully at "
                f"{completed_at.isoformat()}."
            )

        except KeyboardInterrupt:
            raise

        except Exception as exc:
            print(
                f"[Smart Forgetting] Scan failed: "
                f"{type(exc).__name__}: {exc}"
            )
            print(
                f"[Smart Forgetting] Retrying in "
                f"{RETRY_INTERVAL_SECONDS // 60} minutes."
            )
            time.sleep(RETRY_INTERVAL_SECONDS)


def main():
    try:
        run_forever()
    except KeyboardInterrupt:
        print("\n[Smart Forgetting] Background runner stopped.")


if __name__ == "__main__":
    main()
