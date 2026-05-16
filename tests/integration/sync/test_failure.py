from very_good_ffmpeg import VGF

INVALID_INPUT = "https://invalid.example/nope.mp4"
COMMANDS = ["-i {{input}} {{output.mp4}}"]
OUTPUTS = ["output.mp4"]


def test_failure_wait(client: VGF):
    job = client.run(
        input_files={"input": INVALID_INPUT},
        output_files=OUTPUTS,
        ffmpeg_commands=COMMANDS,
        wait=True,
    )
    assert job.status == "failed"
    assert job.error_message


def test_failure_poll(client: VGF):
    job = client.run(
        input_files={"input": INVALID_INPUT},
        output_files=OUTPUTS,
        ffmpeg_commands=COMMANDS,
    )
    job.wait(timeout=120)
    assert job.status == "failed"
    assert job.error_message
