def get_track_played_at(item: dict) -> str | None:
    return item.get("played_at") or item.get("timestamp")


def extract_full_model(track_item: dict) -> dict | None:
    data = track_item.get("data") or {}
    full_model = data.get("fullModel")

    if full_model and full_model.get("id"):
        return full_model

    if data.get("id"):
        return data

    return None


def extract_track_id(item: dict) -> str | None:
    full_model = extract_full_model(item)
    if full_model and full_model.get("id"):
        return str(full_model["id"])

    if item.get("id"):
        return str(item["id"])

    return None

