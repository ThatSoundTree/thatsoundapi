from thatsoundapi.api.v1.models.sounds import TrackView
from thatsoundapi.settings import Settings


def map_track(model: dict) -> TrackView | None:
    track_id = model.get("id")
    title = model.get("title")

    artists = [
        artist["name"]
        for artist in model.get("artists", [])
        if artist.get("name")
    ]

    if not (track_id and title and artists):
        return None

    album = (model.get("albums") or [None])[0]

    album_cover_url = None
    track_url = None

    if album:
        if cover_uri := album.get("coverUri") or album.get("cover_uri"):
            album_cover_url = f"https://{cover_uri.replace('%%', '200x200')}"

        if album_id := album.get("id"):
            track_url = (
                f"https://music.yandex.ru/album/{album_id}/track/{track_id}"
            )

    return TrackView(
        id=str(track_id),
        name=title,
        artists=artists,
        album_cover_url=album_cover_url,
        url=track_url,
        provider=Settings.Providers.YandexMusic.value
    )
