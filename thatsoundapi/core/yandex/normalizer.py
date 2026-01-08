def normalize_track(item: dict) -> dict | None:
    if item.get("type") != "track":
        return None

    data = item.get("data") or {}
    return data.get("fullModel") or data
