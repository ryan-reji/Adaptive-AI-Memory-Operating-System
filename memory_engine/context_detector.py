def create_context_result(context, confidence, reason):
    return {
        "context": context,
        "confidence": confidence,
        "reason": reason
    }


if __name__ == "__main__":
    result = create_context_result(
        context="5G Agriculture Project",
        confidence=0.87,
        reason="Recent activity relates to 5G network slicing and agriculture."
    )

    print(result)