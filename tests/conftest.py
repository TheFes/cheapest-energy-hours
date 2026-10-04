"""Pytest harness rendering cheapest_energy_hours.jinja outside Home Assistant.

Stubs every Home Assistant template extension the macro uses:
  - globals: now(), utcnow(), today_at(), as_datetime(), as_timestamp(),
    timedelta(), states, state_attr(), iif()
  - filters: as_local, as_datetime, as_timestamp, as_function, has_value,
    is_number, average, bool, iif
  - tests:   is_number, datetime, list, contains, search
  - jinja2 extensions: do, loopcontrols ({% break %})

Time is deterministic: tests set the stubbed "now" via the `ha_time` fixture
(or call_macro's `now=` argument), which drives now(), utcnow() and
today_at(). All stubbed datetimes are timezone-aware UTC.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jinja2
import pytest

ROOT = Path(__file__).resolve().parent.parent
MACRO_FILE = "cheapest_energy_hours.jinja"

# ---------------------------------------------------------------------------
# time stubs
# ---------------------------------------------------------------------------

_STUB_NOW = {"now": datetime(2024, 1, 2, 12, 0, 0, tzinfo=timezone.utc)}


def set_now(dt: datetime) -> None:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    _STUB_NOW["now"] = dt


@pytest.fixture()
def ha_time():
    """Fixture returning a setter for the stubbed current time."""
    return set_now


def _now() -> datetime:
    return _STUB_NOW["now"]


def _utcnow() -> datetime:
    return _STUB_NOW["now"].astimezone(timezone.utc)


def _today_at(value: str = "") -> datetime:
    n = _STUB_NOW["now"]
    hour, minute = 0, 0
    if isinstance(value, str) and ":" in value:
        parts = value.split(":")
        hour, minute = int(parts[0]), int(parts[1])
    return n.replace(hour=hour, minute=minute, second=0, microsecond=0)


# ---------------------------------------------------------------------------
# conversion / predicate stubs
# ---------------------------------------------------------------------------

def _as_datetime(value, default=None):
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return default
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    return default


def _as_local(value):
    dt = _as_datetime(value)
    if dt is None:
        raise ValueError(f"as_local: cannot parse {value!r}")
    return dt.astimezone(timezone.utc)  # test "local" timezone is UTC


def _as_timestamp(value, default=None):
    dt = _as_datetime(value)
    return dt.timestamp() if dt is not None else default


def _is_number(value) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str):
        try:
            float(value)
            return True
        except ValueError:
            return False
    return False


def _has_value(entity_id) -> bool:
    return entity_id not in (None, "", "unknown", "unavailable")


def _ha_bool(value, default=False):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value.lower() in ("true", "on", "yes", "1"):
            return True
        if value.lower() in ("false", "off", "no", "0"):
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def _average(seq):
    seq = [x for x in seq]
    if not seq:
        raise ZeroDivisionError("average of empty sequence")
    return sum(seq) / len(seq)


def _iif(condition, if_true=True, if_false=False):
    return if_true if condition else if_false


_SENTINEL = object()


def _ha_round(value, precision=0, method="common", default=_SENTINEL):
    """HA's round filter: like jinja2's round but with a default on failure."""
    try:
        if method == "ceil":
            import math

            return math.ceil(value * 10**precision) / 10**precision
        if method == "floor":
            import math

            return math.floor(value * 10**precision) / 10**precision
        return round(value, precision)
    except (TypeError, ValueError):
        if default is not _SENTINEL:
            return default
        raise


def _contains(value, item) -> bool:
    return item in value


def _search(value, pattern) -> bool:
    return re.search(str(pattern), str(value)) is not None


def _as_function(macro):
    """Emulate HA's as_function: run the macro, capture do returns(value)."""

    def wrapper(*args, **kwargs):
        captured = []
        kwargs["returns"] = captured.append
        rendered = macro(*args, **kwargs)
        if captured:
            return captured[0]
        return rendered

    return wrapper


# ---------------------------------------------------------------------------
# sensor stubs (only used by macro paths that need a real sensor; tests pass
# price_data instead, so these are never meaningfully exercised)
# ---------------------------------------------------------------------------

class _States:
    sensor: list = []

    def __getitem__(self, entity_id):
        raise KeyError(entity_id)


def _state_attr(entity_id, attribute):
    return None


class _LenientUndefined(jinja2.Undefined):
    """Tolerate count/iteration over undefined values (e.g. debug output
    referencing today/tomorrow when price_data is used directly)."""

    def __len__(self):
        return 0

    def __iter__(self):
        return iter([])


# ---------------------------------------------------------------------------
# environment / rendering
# ---------------------------------------------------------------------------

def make_env() -> jinja2.Environment:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(ROOT),
        extensions=["jinja2.ext.do", "jinja2.ext.loopcontrols"],
        undefined=_LenientUndefined,
        keep_trailing_newline=True,
    )
    env.globals.update(
        now=_now,
        utcnow=_utcnow,
        today_at=_today_at,
        as_datetime=_as_datetime,
        as_timestamp=_as_timestamp,
        timedelta=timedelta,
        states=_States(),
        state_attr=_state_attr,
        iif=_iif,
        int=int,
        float=float,
        str=str,
    )
    env.filters.update(
        as_local=_as_local,
        as_datetime=_as_datetime,
        as_timestamp=_as_timestamp,
        as_function=_as_function,
        has_value=_has_value,
        is_number=_is_number,
        average=_average,
        bool=_ha_bool,
        iif=_iif,
        round=_ha_round,
        combine=lambda d, other: {**d, **other},
    )
    env.tests.update(
        is_number=_is_number,
        datetime=lambda v: isinstance(v, datetime),
        list=lambda v: isinstance(v, list),
        contains=_contains,
        search=_search,
    )
    return env


_WRAPPER = (
    "{%- from '" + MACRO_FILE + "' import cheapest_energy_hours -%}"
    "{%- set r = cheapest_energy_hours(**kw) -%}"
    "{{ store(r) }}"
)


def call_macro(now: datetime | None = None, **kwargs):
    """Render the macro with the given keyword arguments, return its output.

    `now` sets both the stubbed HA clock (now/today_at/utcnow) and the
    macro's own `_now` parameter, unless `_now` is passed explicitly.
    """
    if now is not None:
        set_now(now)
        kwargs.setdefault("_now", now)
    holder = {}

    def store(value):
        holder["result"] = value
        return ""

    env = make_env()
    env.from_string(_WRAPPER).render(kw=kwargs, store=store)
    return holder["result"]


# ---------------------------------------------------------------------------
# data helpers
# ---------------------------------------------------------------------------

def make_price_data(start: datetime, slot_minutes: int, prices: list) -> list:
    """Build price_data rows (time_key='start', value_key='value')."""
    return [
        {
            "start": (start + timedelta(minutes=i * slot_minutes)).isoformat(),
            "value": p,
        }
        for i, p in enumerate(prices)
    ]


def reference_weighted_best(slots, slot_minutes, weights, start, end, lowest=True):
    """Reference implementation of the minute-precise weighted search.

    slots: list of (datetime, price) at native granularity.
    Candidates step 1 minute from max(start, first slot start); a candidate
    window must end no later than min(end, last slot end).
    Returns (weighted_average, start_datetime).
    """
    cum = [0]
    for w in weights:
        cum.append(cum[-1] + w)
    length = len(weights)
    win_secs = length * 60
    t0 = slots[0][0]
    slot_secs = slot_minutes * 60
    window_end = min(end, slots[-1][0] + timedelta(seconds=slot_secs))
    s0 = max(start, t0)
    n_c = int(((window_end - s0).total_seconds() - win_secs) // 60) + 1
    assert n_c > 0, "reference: no candidates"
    best = None
    for c in range(n_c):
        off = (s0 - t0).total_seconds() + c * 60
        cost = 0.0
        k0 = int(off // slot_secs)
        k1 = int((off + win_secs - 1) // slot_secs)
        for k in range(k0, k1 + 1):
            lo = max(k * slot_secs - off, 0)
            hi = min((k + 1) * slot_secs - off, win_secs)
            cost += slots[k][1] * (cum[int(hi // 60)] - cum[int(lo // 60)])
        avg = cost / cum[-1]
        if best is None or (avg < best[0] if lowest else avg > best[0]):
            best = (avg, s0 + timedelta(minutes=c))
    return best
