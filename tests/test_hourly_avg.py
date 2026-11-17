"""use_hourly_avg on 15-minute data.

The hourly averages were taken from the raw input instead of the processed
data, so price_factor was ignored and unsorted input gave wrong averages.
"""
import random
from datetime import datetime, timezone

import pytest

from .conftest import call_macro, make_price_data

UTC = timezone.utc
DAY = datetime(2024, 1, 2, 0, 0, tzinfo=UTC)
NOW = datetime(2024, 1, 2, 0, 0, tzinfo=UTC)

# 05:00-07:00 averages 0.15 per hour (quarters 0.1/0.2), everything else 1.0
PRICES = [1.0] * 20 + [0.1, 0.2, 0.1, 0.2] * 2 + [1.0] * 68


def quarters():
    return make_price_data(DAY, 15, PRICES)


def run(data, **kwargs):
    return call_macro(now=NOW, price_data=data, hours=2, mode="all",
                      use_hourly_avg=True, **kwargs)


def test_hourly_avg():
    r = run(quarters())
    assert r["datapoints_per_hour"] == 1
    assert datetime.fromisoformat(str(r["start"])) == DAY.replace(hour=5)
    assert r["average"] == pytest.approx(0.15)


def test_hourly_avg_price_factor():
    r = run(quarters(), price_factor=2)
    assert datetime.fromisoformat(str(r["start"])) == DAY.replace(hour=5)
    assert r["average"] == pytest.approx(0.3)


def test_hourly_avg_unsorted_input():
    data = quarters()
    random.Random(286).shuffle(data)
    r = run(data)
    assert datetime.fromisoformat(str(r["start"])) == DAY.replace(hour=5)
    assert r["average"] == pytest.approx(0.15)
