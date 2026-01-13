import asyncio
from uuid import UUID

from loguru import logger

from thatsoundapi.db.models import Track
from thatsoundapi.settings import get_tsripper_settings
from thatsoundapi.utils.http_client import HttpClient


async def create_cache_task(hgramid: str, track: Track, scrobble_id: UUID) -> None:
    tsripper_settings = get_tsripper_settings()
    attempts = tsripper_settings.ATTEMPTS

    for attempt in range(1, attempts + 1):
        try:
            response = await HttpClient.put(
                url=tsripper_settings.BASE_URL + "/cache",
                json={
                    "scrobble_id": str(scrobble_id),
                    "hgramid": hgramid,
                    "track": track.as_dict()
                }
            )

            if response.status_code == 201:
                return None

            error_text = response.text[:200]
            logger.warning(
                "[{hgramid}] [ripper_create] [{scrobble_id}] attempt {attempt}/{attempts} failed: status={status}, error={error_text}",
                hgramid=hgramid[:8],
                scrobble_id=str(scrobble_id)[:8],
                attempt=attempt,
                attempts=attempts,
                status=response.status_code,
                error_text=error_text
            )

        except Exception as e:
            logger.warning(
                "[{hgramid}] [ripper_create] [{scrobble_id}] attempt {attempt}/{attempts} exception: {error}",
                hgramid=hgramid[:8],
                scrobble_id=str(scrobble_id)[:8],
                attempt=attempt,
                attempts=attempts,
                error=str(e)
            )

        if attempt < attempts:
            delay = 2 ** (attempt - 1)  # exponential backoff: 1s, 2s, 4s, 8s...
            logger.debug(
                "[{hgramid}] [ripper_create] [{scrobble_id}] retrying in {delay}s...",
                hgramid=hgramid[:8],
                scrobble_id=str(scrobble_id)[:8],
                delay=delay
            )
            await asyncio.sleep(delay)

    logger.error(
        "[{hgramid}] [ripper_create] [{scrobble_id}] all {attempts} attempts failed",
        hgramid=hgramid[:8],
        scrobble_id=str(scrobble_id)[:8],
        attempts=attempts
    )
    return None
