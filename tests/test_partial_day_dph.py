"""Issue #286: 15-minute price_data covering only part of a day must still be
detected as 4 datapoints per hour."""
from datetime import datetime, timedelta, timezone

import pytest

from .conftest import call_macro

UTC = timezone.utc
NOW = datetime(2024, 1, 2, 16, 0, tzinfo=UTC)
B = NOW


def _partial_quarters():
    rows = []
    for i in range(32):  # 16:00 - 24:00
        ts = B + timedelta(minutes=15 * i)
        h = ts.hour + ts.minute / 60
        rate = 10 if 17 <= h < 19 else (0 if 21 <= h < 21.5 else 30)
        rows.append({"start": ts.isoformat(), "value": rate})
    return rows


@pytest.mark.parametrize(
    "s,e,dph",
    [((16, 0), (23, 59), 4), ((16, 0), (22, 0), 4), ((16, 0), (23, 0), 4),
     # start not on the 15-minute grid: data is resampled to 5-minute slots
     # (same behaviour as with full-day data)
     ((16, 7), (22, 0), 12), ((16, 0), (23, 45), 4)],
)
def test_partial_day_quarters(s, e, dph):
    r = call_macro(
        now=NOW, price_data=_partial_quarters(), hours=2, mode="all",
        start=B.replace(hour=s[0], minute=s[1]),
        end=B.replace(hour=e[0], minute=e[1]),
    )
    assert datetime.fromisoformat(str(r["start"])) == datetime(2024, 1, 2, 17, 0, tzinfo=UTC)
    assert datetime.fromisoformat(str(r["end"])) == datetime(2024, 1, 2, 19, 0, tzinfo=UTC)
    assert r["average"] == pytest.approx(10)
    assert r["datapoints_per_hour"] == dph
    assert len(r["list"]) == 2 * dph
