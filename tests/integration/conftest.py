from __future__ import annotations

import logging
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from very_good_ffmpeg import VGF

load_dotenv(Path(__file__).parent / ".env.test")


if os.environ.get("VGFFMPEG_DEBUG"):
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logging.getLogger("very_good_ffmpeg").setLevel(logging.DEBUG)
    logging.debug("Debug logging enabled")

log = logging.getLogger("very_good_ffmpeg.tests")


@pytest.fixture(scope="session")
def client() -> VGF:
    api_key = os.environ.get("VGFFMPEG_API_KEY")
    if not api_key:
        pytest.skip("VGFFMPEG_API_KEY not set")
    base_url = os.environ.get("VGFFMPEG_BASE_URL", "https://verygoodffmpeg.com/api")
    log.debug("client base_url=%s", base_url)
    return VGF(api_key=api_key, base_url=base_url)
