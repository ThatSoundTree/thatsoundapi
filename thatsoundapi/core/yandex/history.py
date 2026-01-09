from thatsoundapi.api.v1.models.yandex_music import YandexMusicTrack
from thatsoundapi.core.yandex.normalizer import normalize_track_model
from thatsoundapi.core.yandex.mapper import map_track


def extract_tracks(
    items: list[dict],
    limit: int,
) -> list[YandexMusicTrack]:
    tracks: list[YandexMusicTrack] = []
    seen_track_ids: set[str] = set()

    for item in items:
        for track_item in item.get("tracks", []):
            if track_item.get("type") != "track":
                continue

            data = track_item.get("data") or {}
            model = normalize_track_model(data)

            if not model:
                continue

            if track := map_track(model):
                if track.id not in seen_track_ids:
                    tracks.append(track)

                    if len(tracks) == limit:
                        return tracks

    return tracks
