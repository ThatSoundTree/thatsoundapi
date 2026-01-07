from thatsoundapi.api.v1.models.yandex_music import YandexMusicTrack


def create_track_model(
    full_model: dict,
    played_at: str | None = None
) -> YandexMusicTrack | None:
    track_id = str(full_model.get("id", "")).strip()
    title = full_model.get("title", "").strip()

    if not track_id or not title:
        return None

    artists = [
        artist["name"].strip()
        for artist in full_model.get("artists", [])
        if artist.get("name")
    ]

    if not artists:
        return None

    album_cover_url = None
    track_url = None

    albums = full_model.get("albums") or []
    if albums:
        album = albums[0]

        cover_uri = album.get("coverUri") or album.get("cover_uri")
        if cover_uri:
            album_cover_url = f"https://{cover_uri.replace('%%', '200x200')}"

        album_id = album.get("id")
        if album_id:
            track_url = f"https://music.yandex.ru/album/{album_id}/track/{track_id}"

    return YandexMusicTrack(
        id=track_id,
        name=title,
        artists=artists,
        album_cover_url=album_cover_url,
        url=track_url,
        played_at=played_at,
    )


