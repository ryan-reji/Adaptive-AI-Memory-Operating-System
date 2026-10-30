
import json
import re
import time
import calendar
from datetime import datetime, timedelta

from memory.database.db import get_connection


class ActivityRetriever:

    PATH_MATCH_WINDOW_SECONDS = 10
    FILE_EVIDENCE_LIMIT = 2000

    def interpret_query(self, query):
        """Convert natural-language date expressions into date boundaries."""

        if not isinstance(query, str) or not query.strip():
            return None, None

        today = datetime.now().date()
        text = query.lower().strip()

        if re.search(r"\byesterday\b", text):
            day = today - timedelta(days=1)
            return day.isoformat(), (day + timedelta(days=1)).isoformat()

        if re.search(r"\btoday\b", text):
            return today.isoformat(), (today + timedelta(days=1)).isoformat()

        if re.search(r"\b(last 7 days|past 7 days)\b", text):
            return (
                (today - timedelta(days=6)).isoformat(),
                (today + timedelta(days=1)).isoformat()
            )

        if re.search(r"\blast week\b", text):
            monday = today - timedelta(days=today.weekday() + 7)
            return monday.isoformat(), (monday + timedelta(days=7)).isoformat()

        # ISO date: 2026-09-22
        iso_match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", text)

        if iso_match:
            try:
                day = datetime.strptime(
                    iso_match.group(1), "%Y-%m-%d"
                ).date()
                return day.isoformat(), (day + timedelta(days=1)).isoformat()
            except ValueError:
                return None, None

        month_names = {}

        for month in range(1, 13):
            month_names[calendar.month_name[month].lower()] = month
            month_names[calendar.month_abbr[month].lower()] = month

        months = "|".join(
            sorted(
                (re.escape(name) for name in month_names),
                key=len,
                reverse=True
            )
        )

        patterns = [
            rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+({months})(?:\s+(20\d{{2}}))?\b",
            rf"\b({months})\s+(\d{{1,2}})(?:st|nd|rd|th)?(?:,?\s+(20\d{{2}}))?\b"
        ]

        for index, pattern in enumerate(patterns):
            match = re.search(pattern, text, re.IGNORECASE)

            if not match:
                continue

            try:
                if index == 0:
                    day_number = int(match.group(1))
                    month_number = month_names[match.group(2).lower()]
                    year = int(match.group(3)) if match.group(3) else today.year
                else:
                    month_number = month_names[match.group(1).lower()]
                    day_number = int(match.group(2))
                    year = int(match.group(3)) if match.group(3) else today.year

                day = datetime(year, month_number, day_number).date()

                return day.isoformat(), (day + timedelta(days=1)).isoformat()

            except (ValueError, TypeError):
                return None, None

        return None, None

    @staticmethod
    def _parse_timestamp(value):
        if not value:
            return None

        try:
            return datetime.fromisoformat(
                str(value).replace("Z", "+00:00")
            )
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _path_parts(path):
        return [
            part.casefold()
            for part in str(path).replace("/", "\\").split("\\")
            if part
        ]

    @classmethod
    def _associate_vscode_paths(cls, results, connection):
        """Associate VS Code records with matching filesystem evidence."""

        vscode_results = [
            item for item in results
            if item["source_type"] == "vscode"
            and (item.get("file_name") or item.get("file"))
            and not item.get("file_path")
        ]

        if not vscode_results:
            return

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, timestamp, action, details
            FROM activity_evidence
            WHERE source_type = 'file'
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (cls.FILE_EVIDENCE_LIMIT,)
        )

        file_evidence = []

        for row in cursor.fetchall():
            try:
                details = json.loads(row[3]) if row[3] else {}
            except (json.JSONDecodeError, TypeError):
                continue

            path = details.get("source_path") or details.get("file_path")

            if not path:
                continue

            filename = (
                details.get("file_name")
                or details.get("file")
                or cls._path_parts(path)[-1]
            )

            file_evidence.append({
                "evidence_id": row[0],
                "timestamp": row[1],
                "action": row[2],
                "file_name": str(filename),
                "file_path": str(path),
                "path_parts": cls._path_parts(path)
            })

        for vscode in vscode_results:
            vscode_time = cls._parse_timestamp(vscode.get("timestamp"))

            if not vscode_time:
                continue

            filename = str(
                vscode.get("file_name") or vscode.get("file") or ""
            ).casefold()

            # Remove unsaved markers from VS Code filenames.
            filename = re.sub(r"^[*●•]+\s*", "", filename).strip()

            project = str(vscode.get("project") or "").casefold()

            matches = []

            for evidence in file_evidence:
                if evidence["file_name"].casefold() != filename:
                    continue

                file_time = cls._parse_timestamp(evidence["timestamp"])

                if not file_time:
                    continue

                if vscode_time.tzinfo != file_time.tzinfo:
                    continue

                difference = abs(
                    (vscode_time - file_time).total_seconds()
                )

                if difference > cls.PATH_MATCH_WINDOW_SECONDS:
                    continue

                if project and project not in evidence["path_parts"]:
                    continue

                matches.append((difference, evidence))

            if not matches:
                continue

            matches.sort(key=lambda item: item[0])

            best_difference, best_match = matches[0]

            equally_close = [
                match for difference, match in matches
                if abs(difference - best_difference) < 0.001
            ]

            distinct_paths = {
                match["file_path"].casefold()
                for match in equally_close
            }

            if len(distinct_paths) > 1:
                continue

            vscode["file_path"] = best_match["file_path"]
            vscode["path_source_evidence_id"] = best_match["evidence_id"]
            vscode["path_match_method"] = "filename_project_timestamp"
            vscode["path_match_difference_seconds"] = round(
                best_difference, 3
            )

    def search(
        self,
        query=None,
        start_date=None,
        end_date=None,
        source_type=None,
        search_term=None,
        limit=200
    ):
        started = time.perf_counter()

        if query:
            parsed_start, parsed_end = self.interpret_query(query)

            start_date = start_date or parsed_start
            end_date = end_date or parsed_end

            if search_term is None and parsed_start is None:
                search_term = self._extract_search_term(query)

        conditions = []
        params = []

        if start_date:
            conditions.append("timestamp >= ?")
            params.append(start_date)

        if end_date:
            conditions.append("timestamp < ?")
            params.append(end_date)

        if source_type:
            conditions.append("source_type = ?")
            params.append(source_type)

        if search_term:
            conditions.append("(details LIKE ? OR action LIKE ?)")
            term = f"%{search_term}%"
            params.extend([term, term])

        where = "WHERE " + " AND ".join(conditions) if conditions else ""

        connection = get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute(
                f"""
                SELECT id, source_type, timestamp, action,
                       duration_seconds, details, created_at
                FROM activity_evidence
                {where}
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                params + [max(1, min(limit, 1000))]
            )

            rows = cursor.fetchall()
            results = []

            for row in rows:
                try:
                    details = json.loads(row[5]) if row[5] else {}
                except (json.JSONDecodeError, TypeError):
                    details = {}

                results.append({
                    "evidence_id": row[0],
                    "source_type": row[1],
                    "timestamp": row[2],
                    "action": row[3],
                    "duration_seconds": row[4],
                    "details": details,
                    "created_at": row[6],
                    "file_path": (
                        details.get("file_path")
                        or details.get("source_path")
                    ),
                    "file_name": (
                        details.get("file_name")
                        or details.get("file")
                    ),
                    "project": details.get("project"),
                    "first_seen": details.get("first_seen"),
                    "last_seen": details.get("last_seen")
                })

            self._associate_vscode_paths(results, connection)

            return {
                "query": query,
                "results": results,
                "count": len(results),
                "retrieval_time_ms": (
                    time.perf_counter() - started
                ) * 1000
            }

        finally:
            connection.close()

    @staticmethod
    def _extract_search_term(query):
        """Extract a project, application or subject from an activity query."""

        text = query.lower().strip()

        phrases = [
            "what work did i do",
            "what work have i done",
            "what did i work on",
            "what was i working on",
            "what did i do",
            "what was i doing",
            "what changes did i make",
            "what did i change",
            "what have i changed",
            "what files did i access",
            "which files did i access",
            "what files did i edit",
            "which files did i edit",
            "show me my activity",
            "show my activity",
            "summarize my activity",
            "summarise my activity",
            "what projects",
            "how much time",
            "time spent",
            "did i use",
            "was i using",
            "what did i browse",
            "websites did i visit",
            "on the",
            "on my",
            "in the",
            "in my",
            "for the",
            "for my",
            "project",
            "projects",
            "activity",
            "activities",
            "today",
            "yesterday",
            "last 7 days",
            "past 7 days",
            "last week"
        ]

        for phrase in sorted(phrases, key=len, reverse=True):
            text = text.replace(phrase, " ")

        text = re.sub(
            r"\b(?:i|my|me|did|do|have|has|was|were|the|a|an|on|in|for|of|and)\b",
            " ",
            text
        )

        text = re.sub(r"[^a-z0-9]+", "-", text)
        text = text.strip("-")

        return text or None
