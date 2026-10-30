import re
import time
from pathlib import Path

from memory.ai_engine.retrieval.retriever import Retriever
from memory.ai_engine.retrieval.activity_retriever import ActivityRetriever
from memory.ai_engine.rag.context_builder import ContextBuilder
from memory.ai_engine.rag.llm_client import OllamaLLM


class RAGPipeline:

    def __init__(self):
        self.retriever = Retriever()
        self.activity_retriever = ActivityRetriever()
        self.context_builder = ContextBuilder()
        self.llm = OllamaLLM()

    # =====================================================
    # QUERY CLASSIFICATION
    # =====================================================

    @staticmethod
    def is_activity_query(query):
        text = query.lower().strip()

        patterns = [
            # Latest file and path questions
            r"\blast(?:est)?\s+file\b",
            r"\bwhat\s+(?:was|is)\s+the\s+last\s+file\b",
            r"\bwhich\s+file\s+did\s+i\s+last\b",
            r"\blast\s+file\s+i\s+(?:edited|modified|opened|accessed)\b",
            r"\bfiles?\s+(?:path|location|full path)\b",
            r"\bpath\s+to\s+(?:the\s+)?file\b",
            r"\bfull\s+path\s+of\b",
            r"\bwhere\s+is\s+(?:the\s+)?file\b",
            r"\bfile\s+path\b",
            r"\bfile\s+location\b",
            r"\bin\s+vs\s*code\b",
            r"\bin\s+visual\s+studio\s+code\b",

            # General activity questions
            r"\bwhat\s+did\s+i\s+work\s+on\b",
            r"\bwhat\s+was\s+i\s+working\s+on\b",
            r"\bwhat\s+work\s+did\s+i\s+do\b",
            r"\bwhat\s+work\s+have\s+i\s+done\b",
            r"\bwhat\s+did\s+i\s+do\b",
            r"\bwhat\s+was\s+i\s+doing\b",
            r"\bwhat\s+did\s+i\s+change\b",
            r"\bwhat\s+changes\s+did\s+i\s+make\b",
            r"\bwhat\s+have\s+i\s+changed\b",
            r"\bwhat\s+files\b",
            r"\bwhich\s+files\b",
            r"\bfiles?\s+(?:did\s+i|have\s+i)\s+"
            r"(?:accessed|opened|edited|modified)\b",
            r"\bmy\s+activity\b",
            r"\bactivities\b",
            r"\blast\s+activity\b",
            r"\blatest\s+activity\b",
            r"\bwhat\s+projects\b",
            r"\bhow\s+much\s+time\b",
            r"\btime\s+spent\b",
            r"\bdid\s+i\s+use\b",
            r"\bwas\s+i\s+using\b",
            r"\bwhat\s+did\s+i\s+browse\b",
            r"\bwebsites\s+did\s+i\s+visit\b",
        ]

        if any(re.search(pattern, text) for pattern in patterns):
            return True

        if RAGPipeline.is_file_path_query(text):
            return True

        if re.search(
            r"\b(?:last|latest)\b.*\b(?:file|document)\b|"
            r"\b(?:file|document)\b.*\b(?:last|latest)\b",
            text
        ):
            return True

        project_activity_patterns = [
            r"\b(?:work|activity|activities|changes|files)"
            r"\b.{0,80}\b(?:on|in|for)\s+(?:my\s+)?"
            r"[a-z0-9][a-z0-9 _-]{2,}",
            r"\b(?:on|in)\s+(?:my\s+)?project\b",
        ]

        return any(
            re.search(pattern, text)
            for pattern in project_activity_patterns
        )

    # =====================================================
    # FILE QUERY CLASSIFICATION
    # =====================================================

    @staticmethod
    def is_latest_file_query(query):
        text = query.lower()

        has_latest = bool(
            re.search(r"\b(last|latest)\b", text)
        )

        has_file = bool(
            re.search(r"\b(file|files|document|documents)\b", text)
        )

        has_action = bool(
            re.search(
                r"\b(edit|edited|editing|modify|modified|"
                r"open|opened|access|accessed)\w*\b",
                text
            )
        )

        return has_latest and has_file and has_action

    @staticmethod
    def is_file_path_query(query):
        text = query.lower()

        has_path = bool(
            re.search(r"\b(path|location)\b", text)
        )

        has_file_reference = bool(
            re.search(
                r"\b(?:file|files|document|documents)\b|"
                r"(?<![\w])[^\s\\/]+\."
                r"(?:py|js|jsx|ts|tsx|html|css|json|sql|"
                r"md|txt|pdf|docx?|xlsx?|pptx?)"
                r"(?=$|[\s.,!?;:])",
                text,
                re.IGNORECASE
            )
        )

        return has_path and has_file_reference

    # =====================================================
    # FILE NAME VALIDATION
    # =====================================================

    @staticmethod
    def _valid_file_name(item):

        details = item.get("details") or {}

        if not isinstance(details, dict):
            details = {}

        file_name = (
            item.get("file_name")
            or details.get("file_name")
            or details.get("file")
        )

        file_path = (
            item.get("file_path")
            or details.get("file_path")
            or details.get("source_path")
        )

        if not file_name and file_path:
            file_name = Path(file_path).name

        if not file_name:
            return None

        if (
            not file_path
            and not Path(str(file_name)).suffix
        ):
            return None

        return str(file_name)

    @staticmethod
    def _get_file_path(item):

        details = item.get("details") or {}

        if not isinstance(details, dict):
            details = {}

        return (
            item.get("file_path")
            or details.get("file_path")
            or details.get("source_path")
        )

    # =====================================================
    # DETERMINISTIC FILE RETRIEVAL
    # =====================================================

    def answer_file_query(self, query):

        started = time.perf_counter()
        text = query.lower()

        latest_query = self.is_latest_file_query(query)
        path_query = self.is_file_path_query(query)

        vscode_only = bool(
            re.search(
                r"\b(vs\s*code|visual studio code)\b",
                text
            )
        )

        # Extract an explicitly mentioned filename.
        filename_match = re.search(
            r"(?<![\w])([^\s\\/]+\."
            r"(?:py|js|jsx|ts|tsx|html|css|json|sql|"
            r"md|txt|pdf|docx?|xlsx?|pptx?))"
            r"(?=$|[\s.,!?;:])",
            query,
            re.IGNORECASE
        )

        target_filename = (
            filename_match.group(1).casefold()
            if filename_match
            else None
        )

        # Retrieve structured activity records from SQLite.
        retrieval = self.activity_retriever.search(
            query=None,
            source_type="vscode" if vscode_only else None,
            limit=1000
        )

        results = retrieval["results"]

        # Keep actual file activity records.
        results = [
            item for item in results
            if self._valid_file_name(item)
        ]

        # Match a specifically requested filename.
        if target_filename:
            results = [
                item for item in results
                if (
                    self._valid_file_name(item) or ""
                ).casefold() == target_filename
            ]

        # Latest edit means editing or modified,
        # not merely opened or viewed.
        if latest_query:
            results = [
                item for item in results
                if (
                    item.get("action") or ""
                ).lower() in {"editing", "modified"}
            ]

        # Sort newest first.
        results.sort(
            key=lambda item: item.get("timestamp") or "",
            reverse=True
        )

        # -------------------------------------------------
        # NO MATCHES
        # -------------------------------------------------

        if not results:

            answer = (
                "I couldn't find a matching captured file event. "
                "The file or its path may not have been recorded."
            )

        # -------------------------------------------------
        # LATEST FILE QUERY
        # -------------------------------------------------

        elif latest_query:

            item = results[0]

            filename = self._valid_file_name(item)
            filepath = self._get_file_path(item)

            answer = (
                f"Your latest recorded file edit was "
                f"**{filename or 'Unknown file'}**.\n\n"
                f"Timestamp: {item.get('timestamp')}\n"
                f"Action: {item.get('action')}\n"
                f"Source: {item.get('source_type')}"
            )

            if filepath:
                answer += (
                    f"\n\nFull file path:\n`{filepath}`"
                )
            else:
                answer += (
                    "\n\nFull file path was not captured "
                    "in this event."
                )

        # -------------------------------------------------
        # FILE PATH QUERY
        # -------------------------------------------------

        elif path_query:

            unique_paths = {}

            for item in results:

                filepath = self._get_file_path(item)

                if filepath:
                    unique_paths.setdefault(
                        filepath,
                        item
                    )

            if unique_paths:

                path_lines = []

                for filepath, item in unique_paths.items():

                    filename = self._valid_file_name(item)

                    path_lines.append(
                        f"**{filename}**\n"
                        f"`{filepath}`"
                    )

                answer = (
                    "Captured file path(s):\n\n"
                    + "\n\n".join(path_lines)
                )

            else:

                answer = (
                    "Matching file events were found, "
                    "but their full paths were not captured."
                )

        # -------------------------------------------------
        # OTHER FILE QUERIES
        # -------------------------------------------------

        else:

            unique_files = {}

            for item in results:

                filename = self._valid_file_name(item)

                if filename:
                    unique_files.setdefault(
                        filename.casefold(),
                        item
                    )

            lines = []

            for item in unique_files.values():

                filename = self._valid_file_name(item)
                filepath = self._get_file_path(item)

                line = (
                    f"- **{filename}**"
                    f" | {item.get('action')}"
                    f" | {item.get('timestamp')}"
                )

                if filepath:
                    line += f"\n  `{filepath}`"

                lines.append(line)

            answer = (
                "Captured file activity:\n\n"
                + "\n".join(lines)
            )

        total_time_ms = (
            time.perf_counter() - started
        ) * 1000

        return {
            "query": query,
            "answer": answer,
            "retrieval_time_ms": retrieval["retrieval_time_ms"],
            "context_build_time_ms": 0,
            "generation_time_ms": 0,
            "total_time_ms": total_time_ms,
            "result_count": len(results)
        }

    # =====================================================
    # GENERAL ACTIVITY RETRIEVAL
    # =====================================================

    def answer_activity_query(self, query):

        # File-specific questions must never depend on
        # an LLM deciding which event is the latest.
        if (
            self.is_latest_file_query(query)
            or self.is_file_path_query(query)
        ):
            return self.answer_file_query(query)

        total_started = time.perf_counter()

        retrieval = self.activity_retriever.search(
            query=query,
            limit=200
        )

        retrieval_time_ms = retrieval["retrieval_time_ms"]
        results = retrieval["results"]

        if not results:
            return {
                "query": query,
                "answer": (
                    "I couldn't find captured activity matching "
                    "your question in the available activity database. "
                    "The requested period or project may not have "
                    "been captured."
                ),
                "retrieval_time_ms": retrieval_time_ms,
                "context_build_time_ms": 0,
                "generation_time_ms": 0,
                "total_time_ms": (
                    time.perf_counter() - total_started
                ) * 1000,
                "result_count": 0
            }

        results = sorted(
            results,
            key=lambda item: item.get("timestamp") or ""
        )

        context_started = time.perf_counter()
        context_parts = []

        for index, item in enumerate(results, start=1):

            details = item.get("details") or {}

            if not isinstance(details, dict):
                details = {}

            lines = [
                f"Event: {index}",
                f"Timestamp: {item.get('timestamp')}",
                f"Source: {item.get('source_type')}",
                f"Action: {item.get('action')}"
            ]

            file_path = self._get_file_path(item)

            if file_path:
                lines.append(
                    f"Full file path: {file_path}"
                )

            file_name = self._valid_file_name(item)

            if file_name:
                lines.append(
                    f"File name: {file_name}"
                )

            project = item.get("project")

            if project and str(project).lower() != "unknown":
                lines.append(
                    f"Project: {project}"
                )

            if item.get("duration_seconds") is not None:
                lines.append(
                    f"Duration seconds: "
                    f"{item['duration_seconds']}"
                )

            if item.get("first_seen"):
                lines.append(
                    f"First seen: {item['first_seen']}"
                )

            if item.get("last_seen"):
                lines.append(
                    f"Last seen: {item['last_seen']}"
                )

            if details.get("browser"):
                lines.append(
                    f"Browser: {details['browser']}"
                )

            if details.get("title"):
                lines.append(
                    f"Page title: {details['title']}"
                )

            context_parts.append(
                "\n".join(lines)
            )

        context = "\n\n".join(context_parts)

        context_build_time_ms = (
            time.perf_counter() - context_started
        ) * 1000

        prompt = f"""
You are a personal activity-history assistant.

Answer using ONLY the supplied activity records.

Rules:
- Summarize activities chronologically.
- Group related activities by project when useful.
- Include exact timestamps when relevant.
- Include complete file paths when available.
- Distinguish opened, modified, editing and viewed actions.
- Never claim a file was edited if evidence only says opened.
- Never interpret a workspace title as a filename.
- Treat missing or Unknown projects as unknown.
- Do not invent filenames, projects, dates or durations.
- Never calculate total time from potentially overlapping events.
- Distinguish first_seen and last_seen from event timestamps.
- If evidence is incomplete, explicitly state the limitation.
- Avoid listing repeated events unnecessarily.
- Keep the response concise and finish every sentence.

Number of retrieved records: {len(results)}

Activity records:
{context}

User question:
{query}

Answer:
"""

        generation_started = time.perf_counter()

        answer = self.llm.generate(prompt)

        generation_time_ms = (
            time.perf_counter() - generation_started
        ) * 1000

        return {
            "query": query,
            "answer": answer,
            "context": context,
            "result_count": len(results),
            "retrieval_time_ms": retrieval_time_ms,
            "context_build_time_ms": context_build_time_ms,
            "generation_time_ms": generation_time_ms,
            "total_time_ms": (
                time.perf_counter() - total_started
            ) * 1000
        }

    # =====================================================
    # MAIN RAG ROUTER
    # =====================================================

    def answer(self, query: str, top_k: int = 3) -> dict:

        # Route activity questions to structured retrieval.
        if self.is_activity_query(query):
            return self.answer_activity_query(query)

        # Otherwise use semantic retrieval.
        total_started = time.perf_counter()

        retrieval = self.retriever.search(
            query=query,
            top_k=top_k
        )

        retrieval_time_ms = retrieval["retrieval_time_ms"]

        context_started = time.perf_counter()

        context = self.context_builder.build(
            retrieval["results"]
        )

        context_build_time_ms = (
            time.perf_counter() - context_started
        ) * 1000

        prompt = f"""
You are a helpful AI assistant.

Answer the user's question using ONLY the provided context.

If the answer cannot be found in the context, say:
"I don't have enough information in the retrieved context."

Do not invent facts.

Context:
{context}

User Question:
{query}

Answer:
"""

        generation_started = time.perf_counter()

        answer = self.llm.generate(prompt)

        generation_time_ms = (
            time.perf_counter() - generation_started
        ) * 1000

        return {
            "query": query,
            "answer": answer,
            "context": context,
            "retrieval_time_ms": retrieval_time_ms,
            "context_build_time_ms": context_build_time_ms,
            "generation_time_ms": generation_time_ms,
            "total_time_ms": (
                time.perf_counter() - total_started
            ) * 1000
        }