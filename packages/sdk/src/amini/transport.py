from __future__ import annotations

import logging
from typing import Any

import httpx

from .config import AminiConfig
from .events import Event

logger = logging.getLogger("amini.transport")


class HttpTransport:
    def __init__(self, config: AminiConfig) -> None:
        self._config = config
        self._client = httpx.Client(
            base_url=config.base_url,
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=10.0,
        )

    def send_batch(self, events: list[Event]) -> bool:
        if not events:
            return True
        try:
            response = self._client.post(
                "/api/v1/events/batch",
                json={"events": [e.to_dict() for e in events]},
            )
            response.raise_for_status()
            return True
        except httpx.HTTPError as e:
            logger.warning("Failed to send event batch: %s", e)
            return False

    def close(self) -> None:
        self._client.close()
