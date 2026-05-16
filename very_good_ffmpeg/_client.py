from __future__ import annotations

import asyncio
import json
import logging
import urllib.error
import urllib.request
from pathlib import Path

from ._exceptions import VGFAuthError, VGFError, VGFNotFoundError
from ._models import Job, JobList, PagingParams, TmpFile

_BASE_URL = "https://verygoodffmpeg.com/api"
_DEFAULT_TIMEOUT = 30

log = logging.getLogger("very_good_ffmpeg")


def _raise_for_status(status: int, body: bytes, url: str) -> None:
    if status == 401:
        raise VGFAuthError("Invalid or missing API key", status_code=status)
    if status == 404:
        raise VGFNotFoundError(f"Not found: {url}", status_code=status)
    if status >= 400:
        try:
            msg = json.loads(body).get("message", body.decode())
        except Exception:
            msg = body.decode(errors="replace")
        raise VGFError(msg, status_code=status)


def _parse_paging(raw: dict) -> PagingParams:
    p = raw.get("pagingParams", {})
    return PagingParams(
        limit=p.get("limit", 0),
        offset=p.get("offset", 0),
        total=p.get("total", 0),
        has_more=p.get("hasMore", False),
    )


class _JobsResource:
    def __init__(self, client: VGF):
        self._c = client

    def get(self, job_id: str) -> Job:
        data = self._c._request("GET", f"/jobs/{job_id}")
        return Job._from_dict(data["data"], client=self._c)

    async def aget(self, job_id: str) -> Job:
        data = await self._c._arequest("GET", f"/jobs/{job_id}")
        return Job._from_dict(data["data"], client=self._c)

    def list(self, *, limit: int = 50, offset: int = 0) -> JobList:
        raw = self._c._request("GET", f"/jobs?limit={limit}&offset={offset}")
        return JobList(
            data=[Job._from_dict(j, client=self._c) for j in raw["data"]],
            paging_params=_parse_paging(raw),
        )

    async def alist(self, *, limit: int = 50, offset: int = 0) -> JobList:
        raw = await self._c._arequest("GET", f"/jobs?limit={limit}&offset={offset}")
        return JobList(
            data=[Job._from_dict(j, client=self._c) for j in raw["data"]],
            paging_params=_parse_paging(raw),
        )

    def cancel(self, job_id: str) -> Job:
        data = self._c._request("POST", f"/jobs/{job_id}/cancel")
        return Job._from_dict(data["data"], client=self._c)

    async def acancel(self, job_id: str) -> Job:
        data = await self._c._arequest("POST", f"/jobs/{job_id}/cancel")
        return Job._from_dict(data["data"], client=self._c)


class _FilesResource:
    def __init__(self, client: VGF):
        self._c = client

    def prepare(self) -> TmpFile:
        data = self._c._request("POST", "/tmp-file")
        return TmpFile(
            upload_url=data["data"]["upload_url"],
            download_url=data["data"]["download_url"],
        )

    async def aprepare(self) -> TmpFile:
        data = await self._c._arequest("POST", "/tmp-file")
        return TmpFile(
            upload_url=data["data"]["upload_url"],
            download_url=data["data"]["download_url"],
        )

    def upload(self, data: bytes | str | Path, content_type: str = "application/octet-stream") -> str:
        tmp = self.prepare()
        body = data if isinstance(data, bytes) else Path(data).read_bytes()
        _put(tmp.upload_url, body, content_type)
        return tmp.download_url

    async def aupload(self, data: bytes | str | Path, content_type: str = "application/octet-stream") -> str:
        tmp = await self.aprepare()
        body = data if isinstance(data, bytes) else Path(data).read_bytes()
        await asyncio.to_thread(_put, tmp.upload_url, body, content_type)
        return tmp.download_url


def _put(url: str, body: bytes, content_type: str = "application/octet-stream") -> None:
    log.debug("PUT %s (%d bytes)", url, len(body))
    req = urllib.request.Request(url, data=body, method="PUT")
    req.add_header("Content-Type", content_type)
    req.add_header("Content-Length", str(len(body)))
    try:
        with urllib.request.urlopen(req, timeout=_DEFAULT_TIMEOUT) as resp:
            log.debug("PUT response: %s", resp.status)
            if resp.status not in (200, 204):
                raise VGFError(f"Upload failed with status {resp.status}")
    except urllib.error.HTTPError as e:
        raise VGFError(f"Upload failed: {e}", status_code=e.code) from e


class VGF:
    def __init__(self, api_key: str, base_url: str = _BASE_URL):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self.jobs = _JobsResource(self)
        self.files = _FilesResource(self)

    def _request(self, method: str, path: str, body: dict | None = None) -> dict:
        url = self._base_url + path
        log.debug("%s %s", method, url)
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self._api_key}")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=_DEFAULT_TIMEOUT) as resp:
                result = json.loads(resp.read())
                log.debug("%s %s -> 200", method, url)
                return result
        except urllib.error.HTTPError as e:
            raw = e.read()
            log.debug("%s %s -> %s", method, url, e.code)
            _raise_for_status(e.code, raw, url)

    async def _arequest(self, method: str, path: str, body: dict | None = None) -> dict:
        return await asyncio.to_thread(self._request, method, path, body)

    def run(
        self,
        input_files: dict[str, str],
        output_files: list[str],
        ffmpeg_commands: list[str],
        *,
        webhook_url: str | None = None,
        machine: str = "cpu",
        wait: bool = False,
    ) -> Job:
        body: dict = {
            "input_files": input_files,
            "output_files": output_files,
            "ffmpeg_commands": ffmpeg_commands,
            "machine": machine,
        }
        if webhook_url is not None:
            body["webhook_url"] = webhook_url
        qs = "?wait=true" if wait else ""
        data = self._request("POST", f"/ffmpeg{qs}", body)
        job = Job._from_dict(data["data"], client=self)
        log.debug("job %s submitted, status=%s", job.id, job.status)
        return job

    async def arun(
        self,
        input_files: dict[str, str],
        output_files: list[str],
        ffmpeg_commands: list[str],
        *,
        webhook_url: str | None = None,
        machine: str = "cpu",
        wait: bool = False,
    ) -> Job:
        body: dict = {
            "input_files": input_files,
            "output_files": output_files,
            "ffmpeg_commands": ffmpeg_commands,
            "machine": machine,
        }
        if webhook_url is not None:
            body["webhook_url"] = webhook_url
        qs = "?wait=true" if wait else ""
        data = await self._arequest("POST", f"/ffmpeg{qs}", body)
        job = Job._from_dict(data["data"], client=self)
        log.debug("job %s submitted, status=%s", job.id, job.status)
        return job
