import asyncio
import urllib.request

from very_good_ffmpeg import VGF

SAMPLE_URL = "https://storage.verygoodffmpeg.com/sample.mp4"


async def test_tmp_file_upload_download_and_run(client: VGF):
    original = await asyncio.to_thread(
        lambda: urllib.request.urlopen(SAMPLE_URL).read()
    )

    download_url = await client.files.aupload(original, "video/mp4")

    downloaded = await asyncio.to_thread(
        lambda: urllib.request.urlopen(download_url).read()
    )
    assert downloaded == original

    job = await client.arun(
        input_files={"input": download_url},
        output_files=["output.mp4"],
        ffmpeg_commands=["-i {{input}} -t 2 {{output.mp4}}"],
        wait=True,
    )
    assert job.status == "succeeded"
