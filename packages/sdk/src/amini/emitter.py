from __future__ import annotations

import logging
import queue
import threading
import time

from .config import AminiConfig
from .events import Event
from .transport import HttpTransport

logger = logging.getLogger("amini.emitter")


class EventEmitter:
    def __init__(self, config: AminiConfig, transport: HttpTransport | None = None) -> None:
        self._config = config
        self._transport = transport or HttpTransport(config)
        self._queue: queue.Queue[Event | None] = queue.Queue(maxsize=config.max_queue_size)
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._flush_loop, daemon=True)
        self._thread.start()

    def emit(self, event: Event) -> None:
        if not self._config.enabled:
            return
        try:
            self._queue.put_nowait(event)
        except queue.Full:
            logger.warning("Event queue full, dropping event %s", event.event_id)

    def flush(self) -> None:
        batch = self._drain_queue()
        if batch:
            self._transport.send_batch(batch)

    def shutdown(self, timeout: float = 5.0) -> None:
        self._running = False
        self._queue.put(None)  # sentinel to wake flush loop
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=timeout)
        self.flush()
        self._transport.close()

    def _flush_loop(self) -> None:
        while self._running:
            time.sleep(self._config.flush_interval_seconds)
            batch = self._drain_queue()
            if batch:
                self._transport.send_batch(batch)

    def _drain_queue(self) -> list[Event]:
        batch: list[Event] = []
        while len(batch) < self._config.flush_batch_size:
            try:
                item = self._queue.get_nowait()
                if item is None:
                    break
                batch.append(item)
            except queue.Empty:
                break
        return batch
