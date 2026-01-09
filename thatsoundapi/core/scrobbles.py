from uuid import UUID

from thatsoundapi.core.ripper import create_cache_task
from thatsoundapi.db.models import Track, Scrobble
from thatsoundapi.repositories.tracks import TracksRepository, ScrobblesRepository


async def get_or_create_track(provider_id: int, external_track_id: str) -> Track:
    track = await TracksRepository.get_by_external_id(
        external_id=external_track_id,
    )
    if track:
        return track

    return await TracksRepository.create(
        provider_id=provider_id,
        external_id=external_track_id,
    )


async def get_or_create_scrobble(listener_id: str, track_id: UUID) -> Scrobble:
    scrobble = await ScrobblesRepository.get(
        listener_id=listener_id,
        track_id=track_id,
    )
    if scrobble:
        return scrobble

    return await ScrobblesRepository.create(
        listener_id=listener_id,
        track_id=track_id,
    )


async def process_scrobble_track(hgramid: str, provider_id: int, external_track_id: str) -> Scrobble:
    track = await get_or_create_track(
        provider_id=provider_id,
        external_track_id=external_track_id,
    )

    scrobble = await get_or_create_scrobble(
        listener_id=hgramid,
        track_id=UUID(str(track.id)),
    )

    if not track.tfile_url:
        await create_cache_task(
            hgramid=hgramid,
            track=track,
            scrobble_id=UUID(str(scrobble.id)),
        )

    return scrobble
