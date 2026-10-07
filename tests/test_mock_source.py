import pytest

pytest.importorskip("claimcheck")

from simlab.mock_source import make_session, stream
from simlab.records import check_stamps


def test_the_mock_stream_has_honest_stamps(tmp_path):
    samples = list(stream(make_session(tmp_path)))
    assert len(samples) > 1000
    assert check_stamps(samples) == []
    assert "throttle_pct" in samples[0].values
