"""Async example — list jobs.

Run:
    python examples/async_basic.py

Requires:
    VGFFMPEG_API_KEY env var
"""
import asyncio
import os

from very_good_ffmpeg import VGF


async def main() -> None:
    client = VGF(os.environ["VGFFMPEG_API_KEY"])
    result = await client.jobs.alist()
    print("Jobs:", result.data)


asyncio.run(main())
