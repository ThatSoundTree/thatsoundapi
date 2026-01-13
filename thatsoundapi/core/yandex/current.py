from thatsoundapi.api.v1.models.sounds import TrackView
from thatsoundapi.core.yandex.ynison import (
    generate_device_id,
    get_redirect_data,
    get_player_state,
)
from thatsoundapi.core.yandex.normalizer import normalize_track_model
from thatsoundapi.core.yandex.mapper import map_track
from thatsoundapi.settings import get_yandex_settings
from thatsoundapi.utils.http_client import HttpClient


async def get_track_by_id(
    access_token: str,
    track_id: str,
) -> TrackView | None:
    settings = get_yandex_settings()

    response = await HttpClient.get(
        url=f"{settings.API_BASE_URL}/tracks",
        headers=settings.get_header(access_token=access_token),
        params={"track-ids": track_id},
    )

    tracks = response.json().get("result") or []
    if not tracks:
        return None

    model = normalize_track_model(tracks[0])
    return map_track(model) if model else None


async def get_current_track(access_token: str) -> TrackView | None:
    device_id = generate_device_id()

    redirect, ws_proto = get_redirect_data(
        access_token=access_token,
        device_id=device_id,
    )

    state = get_player_state(
        access_token=access_token,
        redirect=redirect,
        ws_proto=ws_proto,
        device_id=device_id,
    )
    queue = state.get("player_state", {}).get("player_queue", {})
    index = queue.get("current_playable_index")
    playables = queue.get("playable_list", [])

    if index is None or not (0 <= index < len(playables)):
        return None

    playable_id = playables[index].get("playable_id")
    if not playable_id:
        return None

    return await get_track_by_id(
        access_token=access_token,
        track_id=str(playable_id),
    )
