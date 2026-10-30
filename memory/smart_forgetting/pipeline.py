
import json
import sqlite3
from datetime import datetime
from pathlib import Path

from memory.smart_forgetting.config import (
    MEMORY_DB_PATH,
    RECOMMENDATIONS_DB_PATH,
)
from memory.smart_forgetting.feature_extractor import extract_features
from memory.smart_forgetting.recommender import SmartForgettingRecommender
from memory.smart_forgetting.safety import get_protection_reason


class SmartForgettingPipeline:
    def __init__(self):
        self.recommender = SmartForgettingRecommender()
        RECOMMENDATIONS_DB_PATH.parent.mkdir(
            parents=True, exist_ok=True
        )
        self._initialize_db()

    def _connect(self):
        connection = sqlite3.connect(str(RECOMMENDATIONS_DB_PATH))
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_db(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT NOT NULL,
                    file_path TEXT NOT NULL UNIQUE,
                    label TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    confidence REAL,
                    prediction_source TEXT NOT NULL,
                    file_size_bytes INTEGER,
                    last_scanned_at TEXT NOT NULL
                )
            """)

    def _get_candidate_paths(self):
        """Collect paths observed in file activity evidence."""
        if not MEMORY_DB_PATH.is_file():
            raise FileNotFoundError(
                f"Activity database not found: {MEMORY_DB_PATH}"
            )

        with sqlite3.connect(str(MEMORY_DB_PATH)) as conn:
            rows = conn.execute("""
                SELECT details
                FROM activity_evidence
                WHERE source_type = 'file'
            """).fetchall()

        paths = set()

        for (details_text,) in rows:
            try:
                details = json.loads(details_text or "{}")
            except (TypeError, ValueError):
                continue

            file_path = details.get("source_path")
            if file_path:
                paths.add(str(file_path))

        return sorted(paths, key=str.casefold)

    def run(self):
        candidates = self._get_candidate_paths()
        scanned = 0
        skipped = 0
        saved = 0

        with self._connect() as conn:
            for raw_path in candidates:
                path = Path(raw_path).expanduser()

                try:
                    if not path.is_file():
                        skipped += 1
                        continue

                    protected_reason = get_protection_reason(str(path))
                    if protected_reason:
                        skipped += 1
                        continue

                    features = extract_features(
                        str(path), MEMORY_DB_PATH
                    )
                    result = self.recommender.recommend(features)

                    # Fail closed if an unexpected label is returned.
                    label = result.get("label", "review")
                    if label not in {"keep", "review"}:
                        label = "review"

                    reason = result.get("reason") or (
                        "Manual review recommended."
                    )

                    conn.execute("""
                        INSERT INTO recommendations (
                            file_name, file_path, label, reason,
                            confidence, prediction_source,
                            file_size_bytes, last_scanned_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(file_path) DO UPDATE SET
                            file_name = excluded.file_name,
                            label = excluded.label,
                            reason = excluded.reason,
                            confidence = excluded.confidence,
                            prediction_source = excluded.prediction_source,
                            file_size_bytes = excluded.file_size_bytes,
                            last_scanned_at = excluded.last_scanned_at
                    """, (
                        path.name,
                        str(path.resolve()),
                        label,
                        reason,
                        result.get("confidence"),
                        result.get("source", "unknown"),
                        path.stat().st_size,
                        datetime.now().isoformat(timespec="seconds"),
                    ))
                    scanned += 1
                    saved += 1

                except (OSError, ValueError, sqlite3.Error) as exc:
                    skipped += 1
                    print(f"[Smart Forgetting] Skipped {raw_path}: {exc}")

            conn.commit()

        print(
            f"[Smart Forgetting] Finished. Candidates={len(candidates)}, "
            f"scanned={scanned}, saved={saved}, skipped={skipped}"
        )


def main():
    pipeline = SmartForgettingPipeline()
    pipeline.run()


if __name__ == "__main__":
    main()
