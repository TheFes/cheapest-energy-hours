"""Rebuilding data with a gap of a day or more between datapoints.

timedelta.seconds only holds the seconds part (0-86399), so a gap of exactly
24 hours was read as 0 seconds (ZeroDivisionError) and a gap of 24h15m as 15
minutes.
"""
from datetime import datetime, timedelta, timezone

import pytest

from .conftest import call_macro, make_price_data

UTC = timezone.utc
YESTERDAY = datetime(2024, 1, 1, 0, 0, tzinfo=UTC)
NOW = datetime(2024, 1, 2, 12, 0, tzinfo=UTC)
TOMORROW = datetime(2024, 1, 3, 0, 0, tzinfo=UTC)


@pytest.mark.parametrize("gap_minutes", [24 * 60, 24 * 60 + 15, 26 * 60])
def test_gap_of_a_day_or_more(gap_minutes):
    # yesterday hourly (dph 1), then 15-minute data (dph 4) starting
    # gap_minutes after yesterday's last item, up to the end of tomorrow.
    # Mixed resolution forces a rebuild to 4 datapoints per hour.
    hourly = make_price_data(YESTERDAY, 60, [1.0] * 24)
    q_start = YESTERDAY + timedelta(hours=23, minutes=gap_minutes)
    n = int((TOMORROW + timedelta(days=1) - q_start).total_seconds() // 900)
    quarters = [
        dict(row, value=0.1 if TOMORROW + timedelta(hours=6) <= q_start + timedelta(minutes=15 * i) < TOMORROW + timedelta(hours=8) else 1.0)
        for i, row in enumerate(make_price_data(q_start, 15, [1.0] * n))
    ]
    result = call_macro(
        now=NOW, price_data=hourly + quarters, hours=2, mode="all",
        start=NOW, end=TOMORROW + timedelta(days=1),
    )
    assert datetime.fromisoformat(str(result["start"])) == TOMORROW + timedelta(hours=6)
    assert result["average"] == pytest.approx(0.1)
    assert result["datapoints_per_hour"] == 4
