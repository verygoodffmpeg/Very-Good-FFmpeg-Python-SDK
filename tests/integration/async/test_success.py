from very_good_ffmpeg import VGF

INPUT = "https://storage.verygoodffmpeg.com/sample.mp4"
COMMANDS = ["-i {{input}} -t 5 {{output.mp4}}"]
OUTPUTS = ["output.mp4"]


async def test_success_wait(client: VGF):
    job = await client.arun(
        input_files={"input": INPUT},
        output_files=OUTPUTS,
        ffmpeg_commands=COMMANDS,
        wait=True,
    )
    assert job.status == "succeeded"
    assert job.output_files


async def test_success_poll(client: VGF):
    job = await client.arun(
        input_files={"input": INPUT},
        output_files=OUTPUTS,
        ffmpeg_commands=COMMANDS,
    )
    assert job.status in ("queued", "running", "succeeded")

    await job.async_wait(timeout=120)
    assert job.status == "succeeded"
    assert job.output_files
