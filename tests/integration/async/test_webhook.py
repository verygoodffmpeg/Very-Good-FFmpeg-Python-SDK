from very_good_ffmpeg import VGF

WEBHOOK_URL = "https://example.com/webhook"


async def test_webhook_url_reflected(client: VGF):
    job = await client.arun(
        input_files={"input": "https://storage.verygoodffmpeg.com/sample.mp4"},
        output_files=["output.mp4"],
        ffmpeg_commands=["-i {{input}} -t 5 {{output.mp4}}"],
        webhook_url=WEBHOOK_URL,
        wait=True,
    )
    assert job.webhook_url == WEBHOOK_URL
