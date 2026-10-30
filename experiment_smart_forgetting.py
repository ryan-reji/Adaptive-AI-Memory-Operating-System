
import csv
from pathlib import Path

from memory.smart_forgetting.model import SmartForgettingModel
from memory.smart_forgetting.recommender import SmartForgettingRecommender


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

OUTPUT = Path("experiment/results")
OUTPUT.mkdir(parents=True, exist_ok=True)

CONFIDENCE_THRESHOLD = 0.70

REVIEW_CASES = {
    "temporary_recent_log",
    "unused_old_installer",
    "unimportant_project_image",
    "old_temp_archive",
    "recently_opened_installer",
}


# --------------------------------------------------
# SYNTHETIC TEST DATASET
# --------------------------------------------------

# Format:
# name, category, extension, size, age, inactivity,
# access30, access90, modifications, relevance,
# importance, installer, temporary

cases = [
    # Expected KEEP: important despite inactivity
    ("old_project_code", "source_code_configuration", ".py",
     250, 400, 250, 0, 0, 0, "unknown", "high", "false", "false"),

    ("critical_document", "documents", ".pdf",
     12000000, 500, 300, 0, 0, 0, "low", "high", "false", "false"),

    ("rarely_used_database", "datasets_models_databases", ".db",
     5000000, 350, 200, 0, 0, 0, "unknown", "high", "false", "false"),

    ("old_project_backup", "archives_backups", ".zip",
     80000000, 600, 400, 0, 0, 0, "medium", "high", "false", "false"),

    ("important_sql", "source_code_configuration", ".sql",
     150000, 300, 180, 0, 0, 0, "unknown", "medium", "false", "false"),

    # Expected REVIEW: low importance with conflicting signals
    ("temporary_recent_log", "temporary_generated", ".log",
     20000, 180, 5, 3, 5, 2, "low", "low", "false", "true"),

    ("unused_old_installer", "executables_installers", ".exe",
     90000000, 300, 90, 0, 0, 0, "high", "low", "true", "false"),

    ("unimportant_project_image", "images_media", ".jpg",
     500000, 220, 60, 1, 2, 0, "high", "low", "false", "false"),

    ("old_temp_archive", "temporary_generated", ".7z",
     15000000, 350, 180, 0, 0, 0, "high", "low", "false", "true"),

    ("recently_opened_installer", "executables_installers", ".msi",
     40000000, 280, 2, 4, 8, 1, "unknown", "low", "true", "false"),
]


# --------------------------------------------------
# INITIALIZE MODELS
# --------------------------------------------------

model = SmartForgettingModel()
recommender = SmartForgettingRecommender()

results = []


# --------------------------------------------------
# RUN EXPERIMENT
# --------------------------------------------------

for case in cases:

    (
        name,
        category,
        extension,
        size,
        age,
        inactive_days,
        access30,
        access90,
        modifications,
        relevance,
        importance,
        installer,
        temporary,
    ) = case

    # Construct the complete feature dictionary
    features = {
        "file_category": category,
        "file_extension": extension,
        "file_size_bytes": size,
        "file_age_days": age,
        "days_since_last_access": inactive_days,
        "access_count_30d": access30,
        "access_count_90d": access90,
        "modification_count_30d": modifications,
        "project_relevance": relevance,
        "importance_indicator": importance,
        "is_installer": installer,
        "is_temporary": temporary,
        "source_type": "file",
        "action": "inventory_snapshot",
        "metadata_completeness": 0.8,
    }

    # Step 1: Random Forest prediction
    rf = model.predict(features)

    # Step 2: Production hybrid recommender
    # It internally checks RF confidence and invokes Ollama
    # only when confidence is below the configured threshold.
    hybrid = recommender.recommend(features)

    # Determine whether Ollama actually handled the case
    llm_called = hybrid.get("source") == "ollama"

    # Independent ground-truth labels
    expected = (
        "review" if name in REVIEW_CASES else "keep"
    )

    # Step 3: Verify routing behaviour
    if rf["confidence"] is not None:

        if rf["confidence"] >= CONFIDENCE_THRESHOLD:

            assert not rf["needs_llm_fallback"], (
                f"{name}: RF confidence is above threshold "
                "but fallback was requested."
            )

            assert not llm_called, (
                f"{name}: Ollama was called despite "
                "RF confidence >= 70%."
            )

            assert hybrid["label"] == rf["label"], (
                f"{name}: Hybrid decision differs from "
                "high-confidence RF decision."
            )

        else:

            assert rf["needs_llm_fallback"], (
                f"{name}: RF confidence is below threshold "
                "but fallback was not requested."
            )

    # Step 4: Save results
    result = {
        "case": name,
        "expected": expected,
        "rf_prediction": rf["label"],
        "rf_confidence": rf["confidence"],
        "rf_needs_llm": rf["needs_llm_fallback"],
        "llm_called": llm_called,
        "hybrid_prediction": hybrid["label"],
        "hybrid_confidence": hybrid.get("confidence"),
        "prediction_source": hybrid.get("source"),
        "fallback_error": hybrid.get("fallback_error", ""),
    }

    results.append(result)

    confidence_display = (
        f"{rf['confidence']:.2%}"
        if rf["confidence"] is not None
        else "N/A"
    )

    print(
        f"{name}: "
        f"Expected={expected} | "
        f"RF={rf['label']} ({confidence_display}) | "
        f"LLM called={llm_called} | "
        f"Final={hybrid['label']}"
    )


# --------------------------------------------------
# SAVE INDIVIDUAL PREDICTIONS
# --------------------------------------------------

results_file = OUTPUT / "smart_forgetting_predictions.csv"

with results_file.open(
    "w", newline="", encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=results[0].keys()
    )

    writer.writeheader()
    writer.writerows(results)


# --------------------------------------------------
# EVALUATION METRICS
# --------------------------------------------------

def accuracy(prediction_key):

    return sum(
        row[prediction_key] == row["expected"]
        for row in results
    ) / len(results)


def preservation_rate(prediction_key):

    important = [
        row for row in results
        if row["expected"] == "keep"
    ]

    return sum(
        row[prediction_key] == "keep"
        for row in important
    ) / len(important)


def review_detection_rate(prediction_key):

    review_cases = [
        row for row in results
        if row["expected"] == "review"
    ]

    return sum(
        row[prediction_key] == "review"
        for row in review_cases
    ) / len(review_cases)


# --------------------------------------------------
# COMPARE RANDOM FOREST AND HYBRID
# --------------------------------------------------

summary = [
    {
        "method": "Random Forest",
        "accuracy": accuracy("rf_prediction"),
        "important_file_preservation_rate":
            preservation_rate("rf_prediction"),
        "review_detection_rate":
            review_detection_rate("rf_prediction"),
    },
    {
        "method": "RF + Ollama",
        "accuracy": accuracy("hybrid_prediction"),
        "important_file_preservation_rate":
            preservation_rate("hybrid_prediction"),
        "review_detection_rate":
            review_detection_rate("hybrid_prediction"),
    },
]


# --------------------------------------------------
# ADD FALLBACK STATISTICS
# --------------------------------------------------

fallbacks = sum(
    row["llm_called"] for row in results
)

fallback_errors = sum(
    bool(row["fallback_error"])
    for row in results
)

high_confidence_cases = sum(
    row["rf_confidence"] is not None
    and row["rf_confidence"] >= CONFIDENCE_THRESHOLD
    for row in results
)

low_confidence_cases = sum(
    row["rf_needs_llm"] for row in results
)


# --------------------------------------------------
# SAVE METRICS CSV
# --------------------------------------------------

summary_file = OUTPUT / "smart_forgetting_metrics.csv"

with summary_file.open(
    "w", newline="", encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=summary[0].keys()
    )

    writer.writeheader()
    writer.writerows(summary)


# --------------------------------------------------
# PRINT FINAL REPORT
# --------------------------------------------------

print("\n========== EXPERIMENT SUMMARY ==========")

for row in summary:

    print(f"\n{row['method']}")

    print(
        f"Accuracy: "
        f"{row['accuracy']:.2%}"
    )

    print(
        f"Important File Preservation: "
        f"{row['important_file_preservation_rate']:.2%}"
    )

    print(
        f"Review Detection: "
        f"{row['review_detection_rate']:.2%}"
    )


print("\n========== LLM ROUTING STATISTICS ==========")

print(f"Confidence threshold: {CONFIDENCE_THRESHOLD:.0%}")
print(f"High-confidence RF cases: {high_confidence_cases}")
print(f"Low-confidence RF cases: {low_confidence_cases}")
print(f"Ollama calls: {fallbacks}/10")
print(f"Fallback errors: {fallback_errors}")

print("\n========== OUTPUT FILES ==========")
print(f"Predictions: {results_file}")
print(f"Metrics: {summary_file}")
