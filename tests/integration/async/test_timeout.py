import pytest

from very_good_ffmpeg import VGF

INPUT = "https://storage.verygoodffmpeg.com/sample.mp4"
COMMANDS = [
    "-stream_loop 50 -i {{input}} -c:v libx264 -preset veryslow -crf 18 {{output.mp4}}"
]
OUTPUTS = ["output.mp4"]


@pytest.mark.asyncio
async def test_timeout_enforced(client: VGF):
    job = await client.arun(
        input_files={"input": INPUT},
        output_files=OUTPUTS,
        ffmpeg_commands=COMMANDS,
        timeout_seconds=10,
        wait=True,
    )
    assert job.timeout_seconds == 10
    assert job.status == "failed"
    assert job.error_message
