import json
import websocket
from loguru import logger
from typing import Iterable


class WsClient:
    @staticmethod
    def connect(
        url: str,
        headers: Iterable[str],
    ) -> websocket.WebSocket:
        logger.debug("WS CONNECT {url}", url=url)

        ws = websocket.WebSocket()
        ws.connect(url, header=list(headers))
        return ws

    @staticmethod
    def send_json(ws: websocket.WebSocket, payload: dict) -> None:
        logger.debug("WS SEND")
        ws.send(json.dumps(payload))

    @staticmethod
    def recv_json(ws: websocket.WebSocket) -> dict:
        logger.debug("WS RECV")
        return json.loads(ws.recv())

    @staticmethod
    def close(ws: websocket.WebSocket) -> None:
        logger.debug("WS CLOSE")
        ws.close()
