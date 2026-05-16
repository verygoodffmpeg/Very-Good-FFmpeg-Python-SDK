"""Sync example — list jobs.

Run:
    python examples/basic.py

Requires:
    VGFFMPEG_API_KEY env var
"""
import os

from very_good_ffmpeg import VGF

client = VGF(os.environ["VGFFMPEG_API_KEY"])

result = client.jobs.list()
print("Jobs:", result.data)
