import threading
import time


PROCESSING_INTERVAL = 60

_ingestor = None


def start_all_monitors(*args, **kwargs):
    from memory.capture.activity_manager import (
        start_all_monitors as _start_all_monitors,
    )

    return _start_all_monitors(*args, **kwargs)


def process_pending_evidence(*args, **kwargs):
    from memory.relevance.relevance_pipeline import (
        process_pending_evidence as _process_pending_evidence,
    )

    return _process_pending_evidence(*args, **kwargs)


def process_retained_evidence(*args, **kwargs):
    from memory.memory_creation.memory_pipeline import (
        process_retained_evidence as _process_retained_evidence,
    )

    return _process_retained_evidence(*args, **kwargs)


def update_daily_json(*args, **kwargs):
    from memory.memory_creation.json_manager import (
        update_daily_json as _update_daily_json,
    )

    return _update_daily_json(*args, **kwargs)


def _create_memory_ingestor():
    from memory.ai_engine.ingestion.memory_ingestor import (
        MemoryIngestor,
    )

    return MemoryIngestor()


def _get_memory_ingestor():
    global _ingestor

    if _ingestor is None:
        _ingestor = _create_memory_ingestor()

    return _ingestor


def _run_ai_ingestion():
    try:
        ingestor = _get_memory_ingestor()

        result = ingestor.ingest_unprocessed_memories()

        print(
            "AI ingestion: "
            f"{len(result['processed_memory_ids'])} memories processed, "
            f"{result['chunks_added']} chunks added."
        )

        return result

    except Exception as error:
        print(f"AI ingestion error: {error}")

        return {
            "processed_memory_ids": [],
            "chunks_added": 0,
        }


def _run_stage(stage_name, function, default=None):
    try:
        result = function()

        print(
            f"{stage_name} completed successfully."
        )

        return result

    except Exception as error:
        print(
            f"{stage_name} error: {error}"
        )

        return default


def run_processing_pipeline():
    """
    Run the activity → relevance → memory → JSON → AI pipeline.

    Each stage is isolated so a failure in one stage does not
    prevent later stages from being attempted.
    """

    print("\nRunning processing pipeline...")

    _run_stage(
        "Relevance processing",
        process_pending_evidence,
    )

    _run_stage(
        "Memory creation",
        process_retained_evidence,
    )

    added = _run_stage(
        "Daily JSON update",
        update_daily_json,
        default=[],
    )

    print(
        f"JSON updated: {len(added)} new memories added."
    )

    return _run_ai_ingestion()


def start_orchestrator():
    """
    Start activity monitoring and continuously process
    captured activity.
    """

    print(
        "Starting Adaptive AI Memory System...\n"
    )

    monitor_thread = threading.Thread(
        target=start_all_monitors,
        daemon=True,
    )

    monitor_thread.start()

    print("Activity monitoring started.")

    try:
        while True:
            run_processing_pipeline()

            print(
                f"\nNext processing cycle in "
                f"{PROCESSING_INTERVAL} seconds."
            )

            time.sleep(PROCESSING_INTERVAL)

    except KeyboardInterrupt:
        print("\nOrchestrator stopped.")


if __name__ == "__main__":
    start_orchestrator()