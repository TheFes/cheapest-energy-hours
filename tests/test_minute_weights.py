"""Tests for minute-precise cheapest-start with per-minute weights.

Enhancement under test: given a weight list with one element per MINUTE of a
device program (e.g. a dishwasher power profile measured from a smart socket)
and price data at ANY granularity (15-minute day-ahead prices, hourly prices),
the macro must return the minute-precise start/end with the lowest weighted
cost, and do so without upsampling the price data to minute resolution.

All expected values are computed by an independent brute-force reference
implementation (tests/conftest.py::reference_weighted_best).
"""
from datetime import datetime, timedelta, timezone

import pytest

from .conftest import call_macro, make_price_data, reference_weighted_best

UTC = timezone.utc
DAY = datetime(2024, 1, 2, 0, 0, tzinfo=UTC)
NOW = datetime(2024, 1, 2, 12, 0, tzinfo=UTC)

# 270-minute (4.5h) "dishwasher" profile: heating peak in minutes 12-30
PROFILE_270 = [2.0 if 12 <= i < 30 else 0.5 for i in range(270)]


def quarter_prices_15m():
    """192 slots (2 days), base 0.30, wiggle around 08:00-09:30 day 1."""
    prices = [0.30] * 192
    prices[30] = 0.47  # 07:30
    prices[31] = 0.44  # 07:45
    prices[32] = 0.25  # 08:00
    prices[33] = 0.10  # 08:15
    prices[34] = 0.22  # 08:30
    prices[35] = 0.28  # 08:45
    prices[36] = 0.35  # 09:00
    prices[37] = 0.42  # 09:15
    prices[38] = 0.50  # 09:30
    return prices


def hourly_prices_non_hour_optimum():
    """48 slots (2 days): cheap hours 02:00 (0.20) and 03:00 (0.11)."""
    prices = [0.30] * 48
    prices[1] = 0.45
    prices[2] = 0.20
    prices[3] = 0.11
    prices[4] = 0.45
    return prices


def ref(slots_data, slot_minutes, weights, start, end):
    slots = [
        (datetime.fromisoformat(d["start"]), d["value"]) for d in slots_data
    ]
    return reference_weighted_best(slots, slot_minutes, weights, start, end)


# ---------------------------------------------------------------------------
# minute-precise optimum on 15-minute prices
# ---------------------------------------------------------------------------

class TestMinutePrecisionQuarterHourPrices:
    def test_start_is_minute_precise(self):
        data = make_price_data(DAY, 15, quarter_prices_15m())
        expected_avg, expected_start = ref(
            data, 15, PROFILE_270, DAY, DAY + timedelta(days=1)
        )
        assert expected_start.minute % 15 != 0, "test data must not align to a quarter"
        result = call_macro(
            now=NOW,
            price_data=data,
            no_weight_points=60,
            weight=PROFILE_270,
            start="00:00",
            end="00:00",
            mode="start",
        )
        assert result == expected_start
        assert result.minute % 15 != 0

    def test_all_mode_output(self):
        data = make_price_data(DAY, 15, quarter_prices_15m())
        expected_avg, expected_start = ref(
            data, 15, PROFILE_270, DAY, DAY + timedelta(days=1)
        )
        result = call_macro(
            now=NOW,
            price_data=data,
            no_weight_points=60,
            weight=PROFILE_270,
            start="00:00",
            end="00:00",
            mode="all",
            time_format="datetime",
        )
        assert result["start"] == expected_start
        assert result["end"] == expected_start + timedelta(hours=4.5)
        assert result["weighted_average"] == pytest.approx(expected_avg, abs=1e-4)
        assert len(result["list"]) == 270
        assert result["hours"] == pytest.approx(4.5)

    def test_time_format_datetime_carries_minute(self):
        data = make_price_data(DAY, 15, quarter_prices_15m())
        result = call_macro(
            now=NOW,
            price_data=data,
            no_weight_points=60,
            weight=PROFILE_270,
            start="00:00",
            end="00:00",
            mode="start",
        )
        assert isinstance(result, datetime)
        assert result.second == 0
        assert result == datetime(2024, 1, 2, 8, 3, tzinfo=UTC)


# ---------------------------------------------------------------------------
# minute-precise optimum on hourly prices
# ---------------------------------------------------------------------------

class TestMinutePrecisionHourlyPrices:
    def test_start_is_minute_precise(self):
        data = make_price_data(DAY, 60, hourly_prices_non_hour_optimum())
        expected_avg, expected_start = ref(
            data, 60, PROFILE_270, DAY, DAY + timedelta(days=1)
        )
        assert expected_start.minute != 0, "test data must not align to a full hour"
        result = call_macro(
            now=NOW,
            price_data=data,
            no_weight_points=60,
            weight=PROFILE_270,
            start="00:00",
            end="00:00",
            mode="start",
        )
        assert result == expected_start == datetime(2024, 1, 2, 2, 48, tzinfo=UTC)

    def test_weighted_average(self):
        data = make_price_data(DAY, 60, hourly_prices_non_hour_optimum())
        expected_avg, _ = ref(data, 60, PROFILE_270, DAY, DAY + timedelta(days=1))
        result = call_macro(
            now=NOW,
            price_data=data,
            no_weight_points=60,
            weight=PROFILE_270,
            start="00:00",
            end="00:00",
            mode="weighted_average",
        )
        assert result == pytest.approx(expected_avg, abs=1e-4)


# ---------------------------------------------------------------------------
# flat per-minute weights == unweighted result
# ---------------------------------------------------------------------------

class TestFlatWeightsMatchUnweighted:
    # cheap region 10:00-15:15 (0.1) inside 1.0; any 270-min window fully
    # inside ties, earliest wins: 10:00
    prices = [1.0] * 40 + [0.1] * 21 + [1.0] * (96 - 61)

    def test_same_start_and_average(self):
        data = make_price_data(DAY, 15, self.prices)
        unweighted = call_macro(
            now=NOW, price_data=data, hours=4.5, mode="all", time_format="datetime"
        )
        flat = call_macro(
            now=NOW,
            price_data=data,
            no_weight_points=60,
            weight=[1.0] * 270,
            mode="all",
            time_format="datetime",
        )
        assert flat["start"] == unweighted["start"] == datetime(
            2024, 1, 2, 10, 0, tzinfo=UTC
        )
        assert flat["weighted_average"] == pytest.approx(unweighted["average"])
        assert flat["average"] == pytest.approx(unweighted["average"])


# ---------------------------------------------------------------------------
# hours derived from len(weight) / no_weight_points
# ---------------------------------------------------------------------------

class TestHoursDerivedFromWeights:
    def test_270_weights_is_4_5_hours(self):
        data = make_price_data(DAY, 15, quarter_prices_15m())
        result = call_macro(
            now=NOW,
            price_data=data,
            no_weight_points=60,
            weight=PROFILE_270,
            start="00:00",
            end="00:00",
            mode="all",
            time_format="datetime",
        )
        assert result["hours"] == pytest.approx(4.5)
        assert (result["end"] - result["start"]) == timedelta(hours=4.5)


# ---------------------------------------------------------------------------
# profile longer than the available window -> existing error handling
# ---------------------------------------------------------------------------

class TestInsufficientData:
    def test_profile_longer_than_window(self):
        # 6h window, but the first 4.5 hours of data are missing: only
        # 6 slots remain where 18 (4.5h x 4/h) are required
        data = make_price_data(DAY, 15, [0.30] * 96)
        del data[:18]
        result = call_macro(
            now=NOW,
            price_data=data,
            no_weight_points=60,
            weight=PROFILE_270,
            start="00:00",
            end="06:00",
            mode="start",
        )
        assert isinstance(result, str)
        assert "datapoints" in result

    def test_value_on_error(self):
        data = make_price_data(DAY, 15, [0.30] * 96)
        del data[:18]
        result = call_macro(
            now=NOW,
            price_data=data,
            no_weight_points=60,
            weight=PROFILE_270,
            start="00:00",
            end="06:00",
            mode="start",
            value_on_error="FALLBACK",
        )
        assert result == "FALLBACK"


# ---------------------------------------------------------------------------
# start / end / look_ahead boundaries at minute precision
# ---------------------------------------------------------------------------

class TestMinuteBoundaries:
    def test_start_boundary_minute(self):
        # prices cheap from 20:00 on: first candidate (20:07) wins the tie
        prices = [1.0] * 80 + [0.1] * (192 - 80)
        data = make_price_data(DAY, 15, prices)
        result = call_macro(
            now=NOW,
            price_data=data,
            no_weight_points=60,
            weight=PROFILE_270,
            start="20:07",
            end="02:00",
            mode="start",
        )
        assert result == datetime(2024, 1, 2, 20, 7, tzinfo=UTC)

    def test_end_boundary_minute(self):
        # prices strictly decreasing towards end -> last possible start wins:
        # window must end by 02:33 (day 2) -> start 22:03 (day 1)
        prices = [0.50] * 192
        for i in range(80, 107):  # 20:00 day1 .. 02:30 day2
            prices[i] = 1.0 - 0.01 * (i - 79)
        data = make_price_data(DAY, 15, prices)
        expected_avg, expected_start = ref(
            data, 15, PROFILE_270, DAY.replace(hour=20),
            DAY + timedelta(days=1, hours=2, minutes=33),
        )
        result = call_macro(
            now=NOW,
            price_data=data,
            no_weight_points=60,
            weight=PROFILE_270,
            start="20:00",
            end="02:33",
            mode="start",
        )
        assert result == expected_start == datetime(2024, 1, 2, 22, 3, tzinfo=UTC)

    def test_look_ahead_minute_precision(self):
        # cheap block 05:00-08:00; now = 07:23 so look_ahead pushes start there
        prices = [1.0] * 20 + [0.1] * 12 + [1.0] * (192 - 32)
        data = make_price_data(DAY, 15, prices)
        now = datetime(2024, 1, 2, 7, 23, tzinfo=UTC)
        result = call_macro(
            now=now,
            price_data=data,
            no_weight_points=60,
            weight=PROFILE_270,
            start="00:00",
            end="00:00",
            look_ahead=True,
            mode="start",
        )
        assert result == now

    def test_look_ahead_off_picks_earlier(self):
        prices = [1.0] * 20 + [0.1] * 12 + [1.0] * (192 - 32)
        data = make_price_data(DAY, 15, prices)
        now = datetime(2024, 1, 2, 7, 23, tzinfo=UTC)
        result = call_macro(
            now=now,
            price_data=data,
            no_weight_points=60,
            weight=PROFILE_270,
            start="00:00",
            end="00:00",
            look_ahead=False,
            mode="start",
        )
        assert result < now


# ---------------------------------------------------------------------------
# price_tolerance, kwh and highest-price mode on the minute path
# ---------------------------------------------------------------------------

class TestMinutePathOptions:
    prices = [0.30] * 192

    @classmethod
    def setup_class(cls):
        for i in range(30, 39):  # 07:30-09:45 cheap
            cls.prices[i] = 0.10

    def test_kwh_estimated_costs(self):
        data = make_price_data(DAY, 15, self.prices)
        result = call_macro(
            now=NOW,
            price_data=data,
            no_weight_points=60,
            weight=PROFILE_270,
            start="00:00",
            end="00:00",
            mode="all",
            time_format="datetime",
            kwh=2.5,
        )
        assert result["estimated_costs"] == pytest.approx(
            2.5 * result["weighted_average"], abs=1e-4
        )

    def test_price_tolerance(self):
        data = make_price_data(DAY, 15, self.prices)
        result = call_macro(
            now=NOW,
            price_data=data,
            no_weight_points=60,
            weight=PROFILE_270,
            start="00:00",
            end="00:00",
            mode="start",
            price_tolerance="10%",
        )
        # tolerance floors all prices to the same adjusted minimum, so the
        # first window fully inside the cheap block wins
        assert isinstance(result, datetime)

    def test_highest_price(self):
        data = make_price_data(DAY, 15, self.prices)
        result = call_macro(
            now=NOW,
            price_data=data,
            no_weight_points=60,
            weight=PROFILE_270,
            start="00:00",
            end="00:00",
            mode="start",
            lowest=False,
        )
        # flat 0.30 everywhere else -> first candidate wins
        assert result == DAY


# ---------------------------------------------------------------------------
# performance guard: no price upsampling, bounded render time
# ---------------------------------------------------------------------------

class TestPerformance:
    # 270-minute profile over 56h of 15-min data (224 slots).
    # Old algorithm: upsamples to 3360 minute rows and evaluates
    # ~3091 candidates x 270 weights (~835k inner iterations).
    # New algorithm: ~3091 candidates x ~19 overlapping slots (~59k iterations).
    BOUND_SECONDS = 10.0

    prices = [0.30 + (i % 7) * 0.01 for i in range(56 * 4)]
    for i in range(90, 111):  # distinct dip so the optimum is unique
        prices[i] -= 0.05

    def test_no_upsampling_and_fast(self):
        import time

        data = make_price_data(DAY, 15, self.prices)
        end = DAY + timedelta(hours=56)
        t0 = time.perf_counter()
        result = call_macro(
            now=NOW,
            price_data=data,
            no_weight_points=60,
            weight=PROFILE_270,
            start="00:00",
            end=end,
            mode="start",
            debug=True,
        )
        elapsed = time.perf_counter() - t0
        # prices must NOT be upsampled to 60 datapoints/hour
        assert result["data_used"]["datapoints_used"]["datapoints_hour"] == 4
        assert result["data_used"]["datapoints_used"]["datapoints"] == 18
        assert elapsed < self.BOUND_SECONDS, f"render took {elapsed:.2f}s"
        # and the result is still the reference optimum
        expected_avg, expected_start = ref(
            data, 15, PROFILE_270, DAY, end
        )
        # debug mode forces isoformat output
        assert datetime.fromisoformat(result["output"]) == expected_start
