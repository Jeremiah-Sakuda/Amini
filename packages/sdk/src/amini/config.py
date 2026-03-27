from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class AminiConfig:
    api_key: str = ""
    agent_id: str = ""
    environment: str = "development"
    base_url: str = "http://localhost:8000"
    flush_interval_seconds: float = 5.0
    flush_batch_size: int = 50
    max_queue_size: int = 10000
    enabled: bool = True

    @classmethod
    def from_env(cls) -> AminiConfig:
        return cls(
            api_key=os.getenv("AMINI_API_KEY", ""),
            agent_id=os.getenv("AMINI_AGENT_ID", ""),
            environment=os.getenv("AMINI_ENVIRONMENT", "development"),
            base_url=os.getenv("AMINI_BASE_URL", "http://localhost:8000"),
        )
