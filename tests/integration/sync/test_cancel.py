from very_good_ffmpeg import VGF

INPUT = "https://storage.verygoodffmpeg.com/sample.mp4"
COMMANDS = ["-i {{input}} -t 60 {{output.mp4}}"]
OUTPUTS = ["output.mp4"]


def test_cancel(client: VGF):
    job = client.run(
        input_files={"input": INPUT},
        output_files=OUTPUTS,
        ffmpeg_commands=COMMANDS,
    )
    assert job.id

    cancelled = client.jobs.cancel(job.id)
    assert cancelled.status == "cancelled"

    job.wait(timeout=30)
    assert job.status == "cancelled"
