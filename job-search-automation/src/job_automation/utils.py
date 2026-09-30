"""Small, dependency-free helpers shared across modules."""

from __future__ import annotations

import asyncio
import logging
import re
from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import TypeVar

logger = logging.getLogger(__name__)
T = TypeVar("T")


def timestamp() -> str:
    """Filesystem-safe timestamp, e.g. ``20260930_101518``."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def slugify(text: str) -> str:
    """Turn arbitrary text into a safe file-name fragment."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()
    return slug or "item"


async def retry_async(
    operation: Callable[[], Awaitable[T]],
    *,
    attempts: int,
    delay_s: float,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    label: str = "operation",
) -> T:
    """Run ``operation`` up to ``attempts`` times with exponential backoff."""
    for attempt in range(1, attempts + 1):
        try:
            return await operation()
        except exceptions as exc:
            if attempt == attempts:
                logger.error("%s failed after %d attempts: %s", label, attempts, exc)
                raise
            wait = delay_s * 2 ** (attempt - 1)
            logger.warning(
                "%s failed (attempt %d/%d): %s - retrying in %.1fs",
                label, attempt, attempts, exc, wait,
            )
            await asyncio.sleep(wait)
    raise RuntimeError("unreachable")  # pragma: no cover
