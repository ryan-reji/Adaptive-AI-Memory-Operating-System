SENSITIVE_DETAIL_KEYS = {
    "content",
    "path",
    "source_path",
    "old_path",
    "raw",
}


def sanitize_details(value):
    """
    Recursively remove sensitive or internal fields from
    activity and memory details before they are returned
    through the API.
    """

    if isinstance(value, dict):
        sanitized = {}

        for key, item in value.items():
            normalized_key = str(key).lower()

            if (
                normalized_key in SENSITIVE_DETAIL_KEYS
                or normalized_key.endswith("_path")
            ):
                continue

            sanitized[key] = sanitize_details(item)

        return sanitized

    if isinstance(value, list):
        return [sanitize_details(item) for item in value]

    return value