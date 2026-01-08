import json
import websocket
from typing import Any, Iterable


class WsClient:
    @staticmethod
    def connect(
        url: str,
        headers: Iterable[str],
    ) -> websocket.WebSocket:

        ws = websocket.WebSocket()
        ws.connect(url, header=list(headers))
        return ws

    @staticmethod
    def send_json(ws: websocket.WebSocket, payload: dict) -> None:
        ws.send(json.dumps(payload))

    @staticmethod
    def recv_json(ws: websocket.WebSocket) -> dict[str, Any]:
        result: dict[str, Any] = json.loads(ws.recv())
        return result

    @staticmethod
    def close(ws: websocket.WebSocket) -> None:
        ws.close()
