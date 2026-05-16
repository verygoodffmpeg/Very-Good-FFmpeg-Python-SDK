"""Example: list jobs using both sync and async approaches.

Run:
    python main.py

Requires:
    VGFFMPEG_API_KEY env var
"""
import asyncio
import os

from very_good_ffmpeg import VGF

client = VGF(os.environ["VGFFMPEG_API_KEY"])


def sync_example() -> None:
    result = client.jobs.list()
    print("Jobs (sync):", result.data)


async def async_example() -> None:
    result = await client.jobs.alist()
    print("Jobs (async):", result.data)


sync_example()
asyncio.run(async_example())
