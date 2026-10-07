from simlab.records import Sample, check_stamps, read_jsonl, write_jsonl


def _samples(n=5):
    return [Sample(i * 0.1, i * 0.1 + 0.02, {"speed": 100.0 + i}) for i in range(n)]


def test_a_recording_round_trips(tmp_path):
    p = tmp_path / "x.jsonl"
    assert write_jsonl(p, _samples()) == 5
    assert list(read_jsonl(p)) == _samples()


def test_good_stamps_have_no_problems():
    assert check_stamps(_samples()) == []


def test_source_time_must_increase():
    s = _samples()
    s[3] = Sample(s[2].source_t, s[3].receive_t, s[3].values)
    assert any("source_t" in p for p in check_stamps(s))


def test_receive_time_must_not_go_backwards():
    s = _samples()
    s[3] = Sample(s[3].source_t, s[1].receive_t, s[3].values)
    assert any("receive_t" in p for p in check_stamps(s))
