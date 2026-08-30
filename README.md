# very-good-ffmpeg

Python SDK for the Very Good FFmpeg API — run FFmpeg jobs in the cloud.

[![PyPI](https://img.shields.io/pypi/v/very-good-ffmpeg)](https://pypi.org/project/very-good-ffmpeg/)

[Homepage](https://verygoodffmpeg.com) · [API Docs](https://verygoodffmpeg.com/docs) · [GitHub](https://github.com/verygoodffmpeg/Very-Good-FFmpeg-Python-SDK)

## Installation

```
pip install very-good-ffmpeg
```

## Usage

```python
import os
from very_good_ffmpeg import VGF

client = VGF(os.environ["VGFFMPEG_API_KEY"])

# Create a job and wait for it to complete
job = client.run(
    input_files={"input.mp4": "https://example.com/input.mp4"},
    output_files=["output.mp4"],
    ffmpeg_commands=["-i inputs/input.mp4 -vf scale=1280:720 outputs/output.mp4"],
    wait=True,
)

print(job.status)       # "succeeded"
print(job.output_files) # {"output.mp4": "https://..."}
```

Async is also supported — use `arun`, `jobs.aget`, `jobs.alist`, `jobs.acancel`, `files.aupload`, etc.

```python
import asyncio, os
from very_good_ffmpeg import VGF

async def main():
    client = VGF(os.environ["VGFFMPEG_API_KEY"])
    job = await client.arun(
        input_files={"input.mp4": "https://example.com/input.mp4"},
        output_files=["output.mp4"],
        ffmpeg_commands=["-i inputs/input.mp4 -vf scale=1280:720 outputs/output.mp4"],
        wait=True,
    )
    print(job.status)

asyncio.run(main())
```

## Reference

### Create a job — `client.run(...)` / `client.arun(...)`

Submits an FFmpeg job. Pass `wait=True` to block until the job reaches a terminal state.

```python
job = client.run(
    input_files={"input.mp4": "https://example.com/input.mp4"},
    output_files=["output.mp4"],
    ffmpeg_commands=["-i inputs/input.mp4 -c:v libx264 outputs/output.mp4"],
    webhook_url="https://example.com/webhook",  # optional
    machine="nvidia",  # optional: "cpu" | "nvidia"
    wait=True,
)
```

See [Running Commands](https://verygoodffmpeg.com/docs/basics/running-commands) for the full request shape.

### Get a job — `client.jobs.get(id)` / `client.jobs.aget(id)`

```python
job = client.jobs.get("job_abc123")
print(job.status)  # "queued" | "running" | "succeeded" | "failed" | "cancelled"
```

### List jobs — `client.jobs.list(...)` / `client.jobs.alist(...)`

Returns a `JobList` with `data` (list of jobs) and `paging_params`.

```python
result = client.jobs.list(limit=20, offset=0)
print(result.data)          # list[Job]
print(result.paging_params) # PagingParams(limit=20, offset=0, total=100, has_more=True)
```

### Cancel a job — `client.jobs.cancel(id)` / `client.jobs.acancel(id)`

```python
job = client.jobs.cancel("job_abc123")
print(job.status)  # "cancelled"
```

### Poll until done — `job.wait(...)` / `job.async_wait(...)`

```python
job = client.run(input_files=..., output_files=..., ffmpeg_commands=...)
job.wait(timeout=120)
print(job.status)
```

### Upload a file — `client.files.upload(data, content_type?)` / `client.files.aupload(...)`

Upload bytes or a file path to temporary storage and get back a URL you can use as an `input_files` value.

```python
with open("input.mp4", "rb") as f:
    download_url = client.files.upload(f.read(), "video/mp4")

job = client.run(
    input_files={"input.mp4": download_url},
    output_files=["output.mp4"],
    ffmpeg_commands=["-i inputs/input.mp4 -vf scale=1280:720 outputs/output.mp4"],
)
```

Pass a file path directly to have the SDK read it for you:

```python
download_url = client.files.upload("input.mp4")
```

### Prepare upload — `client.files.prepare()` / `client.files.aprepare()`

Returns a `TmpFile` with `upload_url` and `download_url` if you need to stream a large file yourself.

```python
tmp = client.files.prepare()
# PUT your file to tmp.upload_url, then use tmp.download_url as input
```

## Referencing files in commands

Inputs are downloaded to `inputs/` and outputs are uploaded from `outputs/`, so reference
them as plain paths — the key in `input_files` and the entry in `output_files` are the
filenames.

```python
input_files={"input.mp4": "https://example.com/input.mp4"},
output_files=["output.wav"],
ffmpeg_commands=["-i inputs/input.mp4 -vn outputs/output.wav"],
```

See [File Reference Styles](https://verygoodffmpeg.com/docs/advanced/file-reference-styles) for more.

## Examples

See [`examples/example/main.py`](./examples/example/main.py) for a runnable example covering both sync and async usage.

```bash
cd examples/example
pip install -r requirements.txt
VGFFMPEG_API_KEY=your_key python main.py
```

## Support

Open an issue at [github.com/verygoodffmpeg/Very-Good-FFmpeg-Python-SDK](https://github.com/verygoodffmpeg/Very-Good-FFmpeg-Python-SDK) or email [please_help@verygoodffmpeg.com](mailto:please_help@verygoodffmpeg.com).
