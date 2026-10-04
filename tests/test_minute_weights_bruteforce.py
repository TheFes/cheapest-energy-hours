"""Independent brute-force cross-check of the minute-precise weighted path.

The reference below is deliberately naive and shares no code with the macro or
with conftest.reference_weighted_best: for every candidate start minute it sums
w[m] x price(slot containing minute m) over every single minute of the program.

Defined behaviour verified here
  * start snapping: the earliest allowed start is max(start, now if look_ahead)
    rounded UP to a whole minute (12:41:37 -> 12:42:00). Returned start/end
    never carry seconds and never lie before that earliest start.
  * the window must end no later than `end` rounded UP to a whole minute (the
    macro rounds `end` up to the grid, as for coarser weights) and no later
    than the end of the last price slot; candidates step one minute.
  * ties (averages equal after rounding to 9 decimals): the earliest start
    wins, or the latest one when latest_possible=true.
"""
import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from .conftest import call_macro, make_price_data

UTC = timezone.utc
DAY = datetime(2024, 1, 2, 0, 0, tzinfo=UTC)
FIXTURES = Path(__file__).parent / "fixtures"
MAX_DEV = {"v": 0.0, "n": 0}


def load_csv(path):
    """Per-minute energy totals (Wh). Second column is `wh` (or legacy `watts`)."""
    rows = [r for r in csv.reader(path.read_text().splitlines()) if r and not r[0].startswith("#")]
    assert rows[0][1].strip() in ("wh", "watts")
    return [float(r[1]) for r in rows[1:]]


def ceil_minute(dt):
    floored = dt.replace(second=0, microsecond=0)
    return floored if floored == dt else floored + timedelta(minutes=1)


def brute(prices, slot_min, weights, start, end, now, look_ahead, lowest, latest):
    t0 = DAY
    earliest = ceil_minute(max(start, now) if look_ahead else start)
    last_end = t0 + timedelta(minutes=slot_min * len(prices))
    window_end = min(ceil_minute(end), last_end)
    L = len(weights)
    total = sum(weights)
    best = None
    c = earliest
    while c + timedelta(minutes=L) <= window_end:
        cost = 0.0
        for m in range(L):
            minute = c + timedelta(minutes=m)
            k = int((minute - t0).total_seconds() // 60 // slot_min)
            cost += weights[m] * prices[k]
        avg = round(cost / total, 9)
        if best is None:
            better = True
        elif latest:
            better = avg <= best[0] if lowest else avg >= best[0]
        else:
            better = avg < best[0] if lowest else avg > best[0]
        if better:
            best = (avg, c)
        c += timedelta(minutes=1)
    return best, earliest


def rand_profile(seed, n):  # random per-minute Wh totals
    r = random.Random(seed)
    return [round(r.choice([0.0, 5.0, 40.0, 1800.0, 2100.0]) * r.uniform(0.5, 1.5), 1) or 1.0 for _ in range(n)]


def rand_prices(seed, n):
    r = random.Random(seed)
    return [round(r.uniform(-0.12, 0.55), 4) for _ in range(n)]


PROFILES = {p.name.split("_286_")[1][:-4]: load_csv(p) for p in sorted(FIXTURES.glob("*_286_*.csv"))}
PROFILES.update({f"rand{n}": rand_profile(n, n) for n in (45, 137, 270)})

PRICES = {
    "q-seed1": (15, rand_prices(1, 192)),
    "q-seed2": (15, rand_prices(2, 192)),
    "h-seed3": (60, rand_prices(3, 48)),
}

S = DAY
SCENARIOS = {
    "aligned": dict(start=S, end=S + timedelta(days=2), now=S + timedelta(hours=12)),
    "start-12:41:37": dict(start=S + timedelta(hours=12, minutes=41, seconds=37), end=S + timedelta(days=2), now=S + timedelta(hours=12)),
    "end-mid": dict(start=S + timedelta(hours=1, minutes=3), end=S + timedelta(hours=30, minutes=17, seconds=40), now=S + timedelta(hours=12)),
    "look_ahead-now-12:41:37": dict(start=S, end=S + timedelta(days=2), now=S + timedelta(hours=12, minutes=41, seconds=37), look_ahead=True),
    "look_ahead-now-before-start": dict(start=S + timedelta(hours=14, minutes=7), end=S + timedelta(days=2), now=S + timedelta(hours=9, minutes=1, seconds=5), look_ahead=True),
    "latest": dict(start=S + timedelta(hours=5, seconds=30), end=S + timedelta(days=2), now=S + timedelta(hours=12), latest=True),
    "highest": dict(start=S, end=S + timedelta(days=2), now=S + timedelta(hours=12), lowest=False),
    "highest-latest-look_ahead": dict(start=S + timedelta(hours=2), end=S + timedelta(hours=40, seconds=59), now=S + timedelta(hours=20, minutes=33, seconds=59), lowest=False, latest=True, look_ahead=True),
}


def run(prices, slot_min, weights, sc):
    return call_macro(
        now=sc["now"],
        price_data=make_price_data(DAY, slot_min, prices),
        no_weight_points=60,
        weight=weights,
        start=sc["start"],
        end=sc["end"],
        mode="all",
        time_format="datetime",
        lowest=sc.get("lowest", True),
        look_ahead=sc.get("look_ahead", False),
        latest_possible=sc.get("latest", False),
    )


@pytest.mark.parametrize("scenario", SCENARIOS)
@pytest.mark.parametrize("price_key", PRICES)
@pytest.mark.parametrize("profile", PROFILES)
def test_matches_bruteforce(profile, price_key, scenario):
    weights = PROFILES[profile]
    slot_min, prices = PRICES[price_key]
    sc = SCENARIOS[scenario]
    (avg, exp_start), earliest = brute(
        prices, slot_min, weights, sc["start"], sc["end"], sc["now"],
        sc.get("look_ahead", False), sc.get("lowest", True), sc.get("latest", False),
    )
    res = run(prices, slot_min, weights, sc)
    assert res["start"].second == 0 and res["start"].microsecond == 0
    assert res["end"].second == 0 and res["end"].microsecond == 0
    assert res["start"] >= earliest
    assert res["start"] == exp_start
    assert res["end"] == exp_start + timedelta(minutes=len(weights))
    dev = abs(res["weighted_average"] - avg)
    assert dev < 2e-5  # macro rounds output to 5 decimals
    MAX_DEV["v"] = max(MAX_DEV["v"], dev)
    MAX_DEV["n"] += 1


@pytest.mark.parametrize("scenario", ["aligned", "start-12:41:37", "highest-latest-look_ahead"])
@pytest.mark.parametrize("price_key", PRICES)
@pytest.mark.parametrize("profile", PROFILES)
def test_estimated_costs_exact(profile, price_key, scenario):
    """estimated_costs == sum(wh[m] x price(m)) / 1000 for kwh = sum(wh)/1000.

    Tolerance: abs 2e-5 (macro rounds estimated_costs to 5 decimals).
    """
    wh = PROFILES[profile]
    slot_min, prices = PRICES[price_key]
    sc = SCENARIOS[scenario]
    res = call_macro(
        now=sc["now"],
        price_data=make_price_data(DAY, slot_min, prices),
        no_weight_points=60,
        weight=wh,
        kwh=sum(wh) / 1000,
        start=sc["start"],
        end=sc["end"],
        mode="all",
        time_format="datetime",
        lowest=sc.get("lowest", True),
        look_ahead=sc.get("look_ahead", False),
        latest_possible=sc.get("latest", False),
    )
    start = res["start"]
    cost = 0.0
    for m, e in enumerate(wh):
        minute = start + timedelta(minutes=m)
        k = int((minute - DAY).total_seconds() // 60 // slot_min)
        cost += e * prices[k]
    assert res["estimated_costs"] == pytest.approx(cost / 1000, abs=2e-5)


def test_report_max_deviation(capsys):
    # informational: runs last within this module
    with capsys.disabled():
        print(f"\nbrute-force cases checked: {MAX_DEV['n']}, max deviation: {MAX_DEV['v']:.3e}")


# ---------------------------------------------------------------------------
# ties
# ---------------------------------------------------------------------------

class TestTies:
    flat = [0.25] * 192
    weights = [1.0] * 90

    def _run(self, **kw):
        return call_macro(
            now=DAY + timedelta(hours=12),
            price_data=make_price_data(DAY, 15, self.flat),
            no_weight_points=60,
            weight=self.weights,
            start=DAY + timedelta(hours=3, minutes=10, seconds=20),
            end=DAY + timedelta(hours=20),
            mode="all",
            time_format="datetime",
            **kw,
        )

    def test_tie_earliest_is_default(self):
        assert self._run()["start"] == DAY + timedelta(hours=3, minutes=11)

    def test_tie_latest_possible(self):
        assert self._run(latest_possible=True)["start"] == DAY + timedelta(hours=18, minutes=30)

    def test_tie_highest_same_rules(self):
        assert self._run(lowest=False)["start"] == DAY + timedelta(hours=3, minutes=11)
