from uuid import UUID

from loguru import logger

from thatsoundapi.db.models import Track
from thatsoundapi.settings import get_tsripper_settings
from thatsoundapi.utils.http_client import HttpClient


async def create_cache_task(hgramid: str, track: Track, scrobble_id: UUID) -> None:
    tsripper_settings = get_tsripper_settings()

    response = await HttpClient.put(
        url=tsripper_settings.BASE_URL + "/cache",
        json={
            "scrobble_id": str(scrobble_id),
            "hgramid": hgramid,
            "track": track.as_dict()
        }
    )

    if response.status_code != 201:
        logger.error(
            "[{hgramid}] [ripper_create] [{scrobble_id}] unknow api error: {error_text}",
            hgramid=hgramid[:8],
            scrobble_id=str(scrobble_id)[:8],
            error_text=response.text[:200]
        )
        return None
