def normalize_track_model(data: dict) -> dict | None:
    if not data:
        return None

    return data.get("fullModel") or data
