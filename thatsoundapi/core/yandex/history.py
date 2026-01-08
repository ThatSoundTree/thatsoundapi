from thatsoundapi.api.v1.models.yandex_music import YandexMusicTrack
from .normalizer import normalize_track
from .mapper import map_track


def extract_tracks(
    items: list[dict],
    limit: int,
) -> list[YandexMusicTrack]:
    tracks: list[YandexMusicTrack] = []

    for item in items:
        for raw_track in item.get("tracks", []):
            if model := normalize_track(raw_track):
                if track := map_track(model):
                    tracks.append(track)

                    if len(tracks) == limit:
                        return tracks

    return tracks
