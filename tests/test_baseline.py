"""Baseline tests pinning current (v7.2.4) macro behaviour.

These run against unmodified upstream semantics and must keep passing after
the minute-precise weighted path is added.
"""
from datetime import datetime, timedelta, timezone

import pytest

from .conftest import call_macro, make_price_data

UTC = timezone.utc
DAY = datetime(2024, 1, 2, 0, 0, tzinfo=UTC)
NOW = datetime(2024, 1, 2, 12, 0, tzinfo=UTC)


def hourly(prices):
    return make_price_data(DAY, 60, prices)


def quarter(prices):
    return make_price_data(DAY, 15, prices)


# ---------------------------------------------------------------------------
# hourly data, no weights
# ---------------------------------------------------------------------------

class TestHourlyUnweighted:
    # cheapest 3h block is 05:00-08:00 (0.1, 0.1, 0.1)
    prices = [1.0] * 5 + [0.1, 0.1, 0.1] + [1.0] * 16

    def test_mode_start(self):
        result = call_macro(
            now=NOW, price_data=hourly(self.prices), hours=3, mode="start"
        )
        assert result == datetime(2024, 1, 2, 5, 0, tzinfo=UTC)

    def test_mode_end(self):
        result = call_macro(
            now=NOW, price_data=hourly(self.prices), hours=3, mode="end"
        )
        assert result == datetime(2024, 1, 2, 8, 0, tzinfo=UTC)

    def test_mode_average(self):
        result = call_macro(
            now=NOW, price_data=hourly(self.prices), hours=3, mode="average"
        )
        assert result == pytest.approx(0.1)

    def test_mode_all(self):
        result = call_macro(
            now=NOW, price_data=hourly(self.prices), hours=3, mode="all"
        )
        # mode 'all' forces isoformat output
        assert result["start"] == "2024-01-02T05:00:00+00:00"
        assert result["end"] == "2024-01-02T08:00:00+00:00"
        assert result["min"] == pytest.approx(0.1)
        assert result["max"] == pytest.approx(0.1)
        assert result["list"] == [0.1, 0.1, 0.1]
        assert result["datapoints_per_hour"] == 1
        assert result["datapoints"] == 3


# ---------------------------------------------------------------------------
# hourly data with weights (no_weight_points=1)
# ---------------------------------------------------------------------------

class TestWeightedHourly:
    # weights [1,2,1]; window 05:00-08:00: (0.1 + 2*0.3 + 0.05)/4 = 0.1875
    prices = [1.0] * 5 + [0.1, 0.3, 0.05] + [1.0] * 16

    def test_weighted_average(self):
        result = call_macro(
            now=NOW,
            price_data=hourly(self.prices),
            hours=3,
            weight=[1, 2, 1],
            mode="all",
        )
        assert result["start"] == "2024-01-02T05:00:00+00:00"
        assert result["weighted_average"] == pytest.approx(0.1875)

    def test_start(self):
        result = call_macro(
            now=NOW,
            price_data=hourly(self.prices),
            hours=3,
            weight=[1, 2, 1],
            mode="start",
        )
        assert result == datetime(2024, 1, 2, 5, 0, tzinfo=UTC)


# ---------------------------------------------------------------------------
# 15-minute data, no weights
# ---------------------------------------------------------------------------

class TestQuarterHourlyUnweighted:
    # cheapest single hour block at 10:00-11:00 (slots 40-43 = 0.1)
    prices = [1.0] * 40 + [0.1, 0.1, 0.1, 0.1] + [1.0] * 52

    def test_mode_start(self):
        result = call_macro(
            now=NOW, price_data=quarter(self.prices), hours=1, mode="start"
        )
        assert result == datetime(2024, 1, 2, 10, 0, tzinfo=UTC)

    def test_half_hour(self):
        result = call_macro(
            now=NOW, price_data=quarter(self.prices), hours=0.5, mode="start"
        )
        assert result == datetime(2024, 1, 2, 10, 0, tzinfo=UTC)


# ---------------------------------------------------------------------------
# hourly data with quarter-hour weights (no_weight_points=4)
# exercises the upsampling path: hourly prices repeated per 15 minutes
# ---------------------------------------------------------------------------

class TestWeightedQuarterPointsOnHourly:
    # hour 03:00-04:00 = 0.5, hour 04:00-05:00 = 0.9, rest 1.0
    # weights [1,2,3,4] (rising): best start is 03:00 (all weight in cheap hour)
    prices = [1.0] * 3 + [0.5, 0.9] + [1.0] * 19

    def test_start(self):
        result = call_macro(
            now=NOW,
            price_data=hourly(self.prices),
            hours=1,
            no_weight_points=4,
            weight=[1, 2, 3, 4],
            mode="start",
        )
        assert result == datetime(2024, 1, 2, 3, 0, tzinfo=UTC)

    def test_weighted_average(self):
        result = call_macro(
            now=NOW,
            price_data=hourly(self.prices),
            hours=1,
            no_weight_points=4,
            weight=[1, 2, 3, 4],
            mode="weighted_average",
        )
        assert result == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# split mode
# ---------------------------------------------------------------------------

class TestSplit:
    prices = [1.0] * 5 + [0.1, 0.1, 0.1] + [1.0] * 16

    def test_split_blocks(self):
        result = call_macro(
            now=NOW,
            price_data=hourly(self.prices),
            hours=3,
            mode="split",
        )
        # mode 'split' forces isoformat output
        assert result[0]["start"] == "2024-01-02T05:00:00+00:00"
        assert result[0]["hours"] == 3
        assert result[-1]["total_hours"] == 3


# ---------------------------------------------------------------------------
# error handling
# ---------------------------------------------------------------------------

class TestErrors:
    def test_insufficient_data(self):
        # 24h span but 5 datapoints missing in the middle -> 19 < 20 required
        data = hourly([1.0] * 24)
        del data[10:15]
        result = call_macro(
            now=NOW,
            price_data=data,
            hours=20,
            mode="start",
        )
        assert "datapoints" in result

    def test_hours_exceeding_window(self):
        result = call_macro(
            now=NOW,
            price_data=hourly([1.0] * 24),
            hours=30,
            mode="start",
        )
        assert "hours between start and end" in result

    def test_invalid_mode(self):
        result = call_macro(
            now=NOW, price_data=hourly([1.0] * 24), hours=3, mode="bogus"
        )
        assert "Invalid mode" in result
