from very_good_ffmpeg import VGF


def test_list_jobs_offset(client: VGF):
    page1 = client.jobs.list(limit=2, offset=0)
    page2 = client.jobs.list(limit=2, offset=2)

    assert len(page1.data) <= 2
    assert len(page2.data) <= 2

    page1_ids = {j.id for j in page1.data}
    for job in page2.data:
        assert job.id not in page1_ids

    p = page2.paging_params
    assert isinstance(p.limit, int)
    assert isinstance(p.offset, int)
    assert isinstance(p.total, int)
    assert isinstance(p.has_more, bool)
