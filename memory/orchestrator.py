import threading
import time

from memory.capture.activity_manager import start_all_monitors
from memory.relevance.relevance_pipeline import process_pending_evidence
from memory.memory_creation.memory_pipeline import process_retained_evidence
from memory.memory_creation.json_manager import update_daily_json


PROCESSING_INTERVAL = 60


def run_processing_pipeline():
    """
    Run Phase 4 → Phase 5 → daily JSON handoff.
    """

    print("\nRunning processing pipeline...")

    try:
        # Phase 4: Activity relevance
        process_pending_evidence()

        # Phase 5: Create memory records
        process_retained_evidence()

        # Daily JSON handoff
        added = update_daily_json()

        print(
            f"JSON updated: {len(added)} new memories added."
        )

    except Exception as error:
        print(f"Processing pipeline error: {error}")


def start_orchestrator():
    """
    Start activity monitoring and continuously process
    captured activity.
    """

    print("Starting Adaptive AI Memory System...\n")

    # Start File, Browser and VS Code monitors
    monitor_thread = threading.Thread(
        target=start_all_monitors,
        daemon=True
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