from __future__ import annotations

import asyncio
import logging
import queue
import threading
import time

from .config import AminiConfig
from .events import Event
from .transport import AsyncHttpTransport, HttpTransport

logger = logging.getLogger("amini.emitter")


class EventEmitter:
    """Threaded emitter that uses a synchronous ``HttpTransport``."""

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


class AsyncEventEmitter:
    """Async emitter that uses ``AsyncHttpTransport``.

    Use this for async agent frameworks (LangChain, CrewAI, etc.) to avoid
    blocking the event loop with synchronous HTTP and sleep calls.
    """

    def __init__(
        self, config: AminiConfig, transport: AsyncHttpTransport | None = None
    ) -> None:
        self._config = config
        self._transport = transport or AsyncHttpTransport(config)
        self._queue: asyncio.Queue[Event | None] = asyncio.Queue(maxsize=config.max_queue_size)
        self._running = False
        self._flush_task: asyncio.Task | None = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._flush_task = asyncio.ensure_future(self._flush_loop())

    def emit(self, event: Event) -> None:
        if not self._config.enabled:
            return
        try:
            self._queue.put_nowait(event)
        except asyncio.QueueFull:
            logger.warning("Event queue full, dropping event %s", event.event_id)

    async def flush(self) -> None:
        batch = self._drain_queue()
        if batch:
            await self._transport.send_batch(batch)

    async def shutdown(self) -> None:
        self._running = False
        await self._queue.put(None)  # sentinel
        if self._flush_task and not self._flush_task.done():
            await self._flush_task
        await self.flush()
        await self._transport.close()

    async def _flush_loop(self) -> None:
        while self._running:
            await asyncio.sleep(self._config.flush_interval_seconds)
            batch = self._drain_queue()
            if batch:
                await self._transport.send_batch(batch)

    def _drain_queue(self) -> list[Event]:
        batch: list[Event] = []
        while len(batch) < self._config.flush_batch_size:
            try:
                item = self._queue.get_nowait()
                if item is None:
                    self._running = False
                    break
                batch.append(item)
            except asyncio.QueueEmpty:
                break
        return batch
