from unittest.mock import AsyncMock

import pytest

from job_automation.browser import screenshot_on_failure
from job_automation.utils import retry_async


async def test_retry_succeeds_after_transient_failures():
    operation = AsyncMock(side_effect=[RuntimeError("boom"), RuntimeError("boom"), "ok"])
    result = await retry_async(operation, attempts=3, delay_s=0, exceptions=(RuntimeError,))
    assert result == "ok"
    assert operation.await_count == 3


async def test_retry_reraises_after_last_attempt():
    operation = AsyncMock(side_effect=RuntimeError("always"))
    with pytest.raises(RuntimeError, match="always"):
        await retry_async(operation, attempts=2, delay_s=0, exceptions=(RuntimeError,))
    assert operation.await_count == 2


async def test_screenshot_taken_only_on_failure(tmp_path):
    page = AsyncMock()
    async with screenshot_on_failure(page, tmp_path, "ok"):
        pass
    page.screenshot.assert_not_awaited()

    with pytest.raises(ValueError):
        async with screenshot_on_failure(page, tmp_path, "bad step"):
            raise ValueError("fail")
    page.screenshot.assert_awaited_once()
    assert "failure_bad_step" in page.screenshot.await_args.kwargs["path"]
