"""
Author: https://github.com/MIPOHBOPOHIH/YMMBFA/blob/main/main.py#L115-L16
Реально БОЛЬШОЕ СПАСИБО этому бро. У тебя MIT, я типа тебя упомянул, надеюсь не обидешься, @MIPOHBOPOHIH
Звёздочку ему поставьте на репо!
"""
import json
import random
import string

import websockets
from websockets.client import ClientProtocol


YNISON_REDIRECT_URL = (
    "wss://ynison.music.yandex.ru/"
    "redirector.YnisonRedirectService/GetRedirectToYnison"
)

# Патчим ClientProtocol один раз при импорте модуля для максимальной производительности
_original_process_subprotocol = ClientProtocol.process_subprotocol
ClientProtocol.process_subprotocol = lambda self, headers: None


def generate_device_id(length: int = 16) -> str:
    return ''.join(random.choices(string.ascii_lowercase, k=length))


async def get_redirect_data(
    access_token: str,
    device_id: str,
) -> tuple[dict, dict]:
    ws_proto = {
        "Ynison-Device-Id": device_id,
        "Ynison-Device-Info": json.dumps({"app_name": "Chrome", "type": 1}),
    }

    ws_proto_json = json.dumps(ws_proto)
    headers = {
        "Origin": "http://music.yandex.ru",
        "Authorization": f"OAuth {access_token}",
        "Sec-WebSocket-Protocol": f"Bearer, v2, {ws_proto_json}",
    }

    async with websockets.connect(
        YNISON_REDIRECT_URL,
        additional_headers=headers,
    ) as ws:
        response = json.loads(await ws.recv())

    return response, ws_proto


async def get_player_state(
    access_token: str,
    redirect: dict,
    ws_proto: dict,
    device_id: str,
) -> dict:
    ws_proto["Ynison-Redirect-Ticket"] = redirect["redirect_ticket"]

    payload = {
        "update_full_state": {
            "player_state": {
                "player_queue": {
                    "current_playable_index": -1,
                    "entity_id": "",
                    "entity_type": "VARIOUS",
                    "playable_list": [],
                    "options": {"repeat_mode": "NONE"},
                    "entity_context": "BASED_ON_ENTITY_BY_DEFAULT",
                    "version": {
                        "device_id": device_id,
                        "version": 9021243204784341000,
                        "timestamp_ms": 0,
                    },
                    "from_optional": "",
                },
                "status": {
                    "duration_ms": 0,
                    "paused": True,
                    "playback_speed": 1,
                    "progress_ms": 0,
                    "version": {
                        "device_id": device_id,
                        "version": 8321822175199937000,
                        "timestamp_ms": 0,
                    },
                },
            },
            "device": {
                "capabilities": {
                    "can_be_player": True,
                    "can_be_remote_controller": False,
                    "volume_granularity": 16,
                },
                "info": {
                    "device_id": device_id,
                    "type": "WEB",
                    "title": "Chrome Browser",
                    "app_name": "Chrome",
                },
                "volume_info": {"volume": 0},
                "is_shadow": True,
            },
            "is_currently_active": False,
        },
        "rid": "ac281c26-a047-4419-ad00-e4fbfda1cba3",
        "player_action_timestamp_ms": 0,
        "activity_interception_type": "DO_NOT_INTERCEPT_BY_DEFAULT",
    }

    ws_proto_json = json.dumps(ws_proto)
    url = f"wss://{redirect['host']}/ynison_state.YnisonStateService/PutYnisonState"
    headers = {
        "Origin": "http://music.yandex.ru",
        "Authorization": f"OAuth {access_token}",
        "Sec-WebSocket-Protocol": f"Bearer, v2, {ws_proto_json}",
    }

    async with websockets.connect(url, additional_headers=headers) as ws:
        await ws.send(json.dumps(payload))
        response = json.loads(await ws.recv())

    return response
