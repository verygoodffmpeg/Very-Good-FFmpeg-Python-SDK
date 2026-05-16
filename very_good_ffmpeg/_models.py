from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._client import VGF

_TERMINAL = {"succeeded", "failed", "cancelled"}

log = logging.getLogger("very_good_ffmpeg")


@dataclass
class Job:
    id: str
    status: str
    queued_at: str
    started_at: str | None
    finished_at: str | None
    created_at: str
    updated_at: str
    error_message: str
    ffmpeg_commands: list[str]
    input_files: dict[str, str]
    output_files: dict[str, str]
    webhook_url: str | None
    total_input_bytes: int | None
    total_output_bytes: int | None

    _client: VGF = field(repr=False, compare=False, default=None)

    @classmethod
    def _from_dict(cls, data: dict, client: VGF = None) -> Job:
        return cls(
            id=data["id"],
            status=data["status"],
            queued_at=data["queued_at"],
            started_at=data.get("started_at"),
            finished_at=data.get("finished_at"),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            error_message=data.get("error_message", ""),
            ffmpeg_commands=data.get("ffmpeg_commands", []),
            input_files=data.get("input_files", {}),
            output_files=data.get("output_files", {}),
            webhook_url=data.get("webhook_url"),
            total_input_bytes=data.get("total_input_bytes"),
            total_output_bytes=data.get("total_output_bytes"),
            _client=client,
        )

    def _apply_update(self, updated: Job) -> None:
        self.status = updated.status
        self.started_at = updated.started_at
        self.finished_at = updated.finished_at
        self.output_files = updated.output_files
        self.error_message = updated.error_message
        self.total_input_bytes = updated.total_input_bytes
        self.total_output_bytes = updated.total_output_bytes
        self.updated_at = updated.updated_at

    def wait(self, poll_interval: float = 2.0, timeout: float | None = None) -> Job:
        deadline = time.monotonic() + timeout if timeout else None
        while self.status not in _TERMINAL:
            if deadline and time.monotonic() >= deadline:
                raise TimeoutError(f"Job {self.id} did not finish within timeout")
            log.debug("job %s polling, status=%s, sleeping %.1fs", self.id, self.status, poll_interval)
            time.sleep(poll_interval)
            self._apply_update(self._client.jobs.get(self.id))
        log.debug("job %s terminal, status=%s", self.id, self.status)
        return self

    async def async_wait(self, poll_interval: float = 2.0, timeout: float | None = None) -> Job:
        deadline = time.monotonic() + timeout if timeout else None
        while self.status not in _TERMINAL:
            if deadline and time.monotonic() >= deadline:
                raise TimeoutError(f"Job {self.id} did not finish within timeout")
            log.debug("job %s polling, status=%s, sleeping %.1fs", self.id, self.status, poll_interval)
            await asyncio.sleep(poll_interval)
            self._apply_update(await self._client.jobs.aget(self.id))
        log.debug("job %s terminal, status=%s", self.id, self.status)
        return self

    def cancel(self) -> Job:
        return self._client.jobs.cancel(self.id)

    async def acancel(self) -> Job:
        return await self._client.jobs.acancel(self.id)


@dataclass
class PagingParams:
    limit: int
    offset: int
    total: int
    has_more: bool


@dataclass
class JobList:
    data: list[Job]
    paging_params: PagingParams


@dataclass
class TmpFile:
    upload_url: str
    download_url: str
