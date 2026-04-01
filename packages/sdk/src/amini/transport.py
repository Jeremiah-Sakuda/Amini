from __future__ import annotations

import logging
import random
import time
from typing import Any

import httpx

from .config import AminiConfig
from .events import Event

logger = logging.getLogger("amini.transport")

MAX_RETRIES = 3
BASE_DELAY = 0.5  # seconds
MAX_DELAY = 10.0  # seconds


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

        payload = {"events": [e.to_dict() for e in events]}

        for attempt in range(MAX_RETRIES + 1):
            try:
                response = self._client.post("/api/v1/events/batch", json=payload)
                response.raise_for_status()
                return True
            except httpx.HTTPError as e:
                if attempt < MAX_RETRIES:
                    delay = min(BASE_DELAY * (2 ** attempt) + random.uniform(0, 0.5), MAX_DELAY)
                    logger.warning(
                        "Failed to send event batch (attempt %d/%d): %s — retrying in %.1fs",
                        attempt + 1, MAX_RETRIES + 1, e, delay,
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        "Failed to send event batch after %d attempts: %s — dropping %d events",
                        MAX_RETRIES + 1, e, len(events),
                    )
                    return False

        return False

    def close(self) -> None:
        self._client.close()
