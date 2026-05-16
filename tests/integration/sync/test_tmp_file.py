import urllib.request

from very_good_ffmpeg import VGF

SAMPLE_URL = "https://storage.verygoodffmpeg.com/sample.mp4"


def test_tmp_file_upload_download_and_run(client: VGF):
    with urllib.request.urlopen(SAMPLE_URL) as r:
        original = r.read()

    download_url = client.files.upload(original, "video/mp4")

    with urllib.request.urlopen(download_url) as r:
        downloaded = r.read()

    assert downloaded == original

    job = client.run(
        input_files={"input": download_url},
        output_files=["output.mp4"],
        ffmpeg_commands=["-i {{input}} -t 2 {{output.mp4}}"],
        wait=True,
    )
    assert job.status == "succeeded"
