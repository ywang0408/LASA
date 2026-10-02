"""Agent-facing tools for the LASA host-city attendance pilot.

Each public function is a tool an LLM agent can call. Docstrings state the
arguments, the return fields, and the cases where the tool must refuse a
stronger claim than the file supports. The bundled congress file is simulated.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "simulated_congresses.csv"

REQUIRED_COLUMNS = (
    "year",
    "host_city",
    "host_country",
    "paid_member_registrations",
    "usa_registrations",
    "latam_and_other_registrations",
    "data_source",
)

# Approximate city-center coordinates for the demo hubs and candidates.
COORDINATES = {
    "barcelona": (41.39, 2.17),
    "buenos aires": (-34.60, -58.38),
    "rome": (41.90, 12.50),
    "berlin": (52.52, 13.40),
    "guatemala city": (14.63, -90.51),
    "boston": (42.36, -71.06),
    "lima": (-12.05, -77.04),
    "guadalajara": (20.66, -103.35),
    "montreal": (45.50, -73.57),
    "new york": (40.71, -74.01),
    "mexico city": (19.43, -99.13),
    "sao paulo": (-23.55, -46.63),
    "madrid": (40.42, -3.70),
}

DEFAULT_HUBS = ("New York", "Mexico City", "Sao Paulo", "Madrid")
CANDIDATE_CITIES = ("Barcelona", "Buenos Aires", "Rome", "Berlin", "Guatemala City")
PAID_MIN = 1900
PAID_MAX = 3400


def _norm(city: str) -> str:
    return " ".join(city.strip().lower().split())


def load_congresses(path: Path | None = None) -> list[dict]:
    """Load congress rows from CSV.

    Args:
        path: CSV path. Defaults to the bundled simulated file.

    Returns:
        One dict per congress. Registration fields are ints. The year is an int.
    """
    source = path or DATA_PATH
    with source.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    parsed = []
    for row in rows:
        parsed.append(
            {
                "year": int(row["year"]),
                "host_city": row["host_city"],
                "host_country": row["host_country"],
                "paid_member_registrations": int(row["paid_member_registrations"]),
                "usa_registrations": int(row["usa_registrations"]),
                "latam_and_other_registrations": int(row["latam_and_other_registrations"]),
                "data_source": row["data_source"],
            }
        )
    return parsed


def validate_simulation(path: Path | None = None) -> dict:
    """Check the bundled congress file against the written simulation rules.

    An agent should call this before quoting any attendance number. The check
    is for the simulated fixture only. A later LASA file needs its own rules
    and must not be committed to a public repository.

    Args:
        path: CSV path. Defaults to the bundled simulated file.

    Returns:
        A dict with keys ``ok`` (bool), ``errors`` (list of strings), and
        ``row_count`` (int). ``ok`` is true only when ``errors`` is empty.

    Raises:
        FileNotFoundError: If the CSV is missing.
    """
    source = path or DATA_PATH
    errors: list[str] = []
    with source.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        missing = [name for name in REQUIRED_COLUMNS if name not in fieldnames]
        if missing:
            errors.append(f"missing columns: {', '.join(missing)}")
        rows = list(reader)
    if not rows:
        errors.append("file has no congress rows")
    for index, row in enumerate(rows, start=2):
        for name in REQUIRED_COLUMNS:
            if not (row.get(name) or "").strip():
                errors.append(f"line {index}: {name} is blank")
        if (row.get("data_source") or "").strip() != "simulated":
            errors.append(f"line {index}: data_source must be 'simulated' in this fixture")
        try:
            paid = int(row["paid_member_registrations"])
            usa = int(row["usa_registrations"])
            other = int(row["latam_and_other_registrations"])
        except (KeyError, ValueError):
            errors.append(f"line {index}: registration fields must be integers")
            continue
        if usa + other != paid:
            errors.append(f"line {index}: origin segments do not add up to paid registrations")
        if not PAID_MIN <= paid <= PAID_MAX:
            errors.append(f"line {index}: paid registrations fall outside {PAID_MIN}-{PAID_MAX}")
    return {"ok": not errors, "errors": errors, "row_count": len(rows)}


def lookup_historical_attendance(city: str | None = None, year: int | None = None, path: Path | None = None) -> dict:
    """Retrieve simulated attendance for past congresses.

    The bundled file stores two origin segments, USA and Latin America & Others.
    A full per-country breakdown is not in this repository. If ``city`` and
    ``year`` are both omitted, the tool returns every row and says so.

    Args:
        city: Host city to match, case-insensitive. Optional.
        year: Congress year to match. Optional.
        path: CSV path. Defaults to the bundled simulated file.

    Returns:
        A dict with ``data_source``, ``matches`` (list of congress dicts), and
        ``note``. ``matches`` is empty when nothing fits the filter.
    """
    rows = load_congresses(path)
    matches = []
    for row in rows:
        if city is not None and _norm(row["host_city"]) != _norm(city):
            continue
        if year is not None and row["year"] != int(year):
            continue
        matches.append(row)
    return {
        "data_source": "simulated",
        "matches": matches,
        "note": (
            "Counts are simulated origin segments, not a per-country extract from LASA. "
            f"{len(matches)} row(s) matched."
        ),
    }


def haversine_km(origin: str, destination: str) -> float:
    """Great-circle distance in kilometers between two known cities.

    Args:
        origin: City name present in the coordinate table.
        destination: City name present in the coordinate table.

    Returns:
        Distance in kilometers, rounded to one decimal place.

    Raises:
        KeyError: If either city is absent from the coordinate table.
    """
    lat1, lon1 = COORDINATES[_norm(origin)]
    lat2, lon2 = COORDINATES[_norm(destination)]
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return round(2 * radius * math.asin(math.sqrt(a)), 1)


def estimate_travel_cost(city: str, usd_per_km: float, hubs: tuple[str, ...] = DEFAULT_HUBS) -> dict:
    """Estimate travel cost from member hubs with a stated airfare scenario.

    The scenario is ``usd_per_km`` multiplied by great-circle distance. The
    caller must supply that rate. This tool does not look up a current fare,
    and the result is not a ticket price two years ahead. It is a planning
    scenario the caller has already chosen.

    Args:
        city: Candidate host city. Must be in the coordinate table.
        usd_per_km: Planning assumption, dollars per kilometer. Must be positive.
        hubs: Origin cities. Defaults to New York, Mexico City, Sao Paulo, and Madrid.

    Returns:
        A dict with ``city``, ``usd_per_km``, ``by_hub`` (distance and scenario
        cost for each hub), and ``note``.

    Raises:
        ValueError: If ``usd_per_km`` is not positive.
        KeyError: If ``city`` or a hub is missing from the coordinate table.
    """
    rate = float(usd_per_km)
    if rate <= 0:
        raise ValueError("usd_per_km must be a positive scenario rate")
    by_hub = []
    for hub in hubs:
        distance = haversine_km(hub, city)
        by_hub.append(
            {
                "hub": hub,
                "distance_km": distance,
                "scenario_cost_usd": round(distance * rate, 2),
            }
        )
    return {
        "city": city,
        "usd_per_km": rate,
        "by_hub": by_hub,
        "note": "Scenario cost is distance times the supplied USD-per-km rate. It is not a live airfare quote.",
    }


def flag_confidence(city: str, path: Path | None = None) -> dict:
    """Signal when a candidate sits outside the historical hosts in the file.

    A city that never appears as a host in the loaded file is flagged. The
    flag is about this file only. Eight simulated rows are not a census of
    LASA congresses.

    Args:
        city: Candidate host city.
        path: CSV path. Defaults to the bundled simulated file.

    Returns:
        A dict with ``city``, ``hosted_in_file`` (bool), ``historical_hosts``,
        ``flag`` (``comparable_host_in_file`` or ``no_comparable_host``), and
        ``data_source``.
    """
    rows = load_congresses(path)
    hosts = sorted({row["host_city"] for row in rows})
    hosted = any(_norm(row["host_city"]) == _norm(city) for row in rows)
    return {
        "city": city,
        "hosted_in_file": hosted,
        "historical_hosts": hosts,
        "flag": "comparable_host_in_file" if hosted else "no_comparable_host",
        "data_source": "simulated",
    }


def _average(values: list[int]) -> float:
    return round(sum(values) / len(values), 1)


def estimate_attendance(city: str, guardrails: bool = True, path: Path | None = None) -> dict:
    """Produce an attendance baseline, or a clearly labeled gap, for one city.

    With guardrails on, a city that has no host row in the file gets no point
    estimate. The historical average of the file is still reported as context
    under ``historical_average_paid``, and ``estimate`` is null.

    With guardrails off, that same city receives the file-wide average as
    ``estimate``. That output is the behavior the guardrail exists to block.
    It is still computed from simulated rows and is not a validated forecast.

    Regularized regression is not fit. The file has eight simulated congresses.

    Args:
        city: Candidate host city.
        guardrails: When true, withhold a point estimate for an unseen host.
            Defaults to true.
        path: CSV path. Defaults to the bundled simulated file.

    Returns:
        A dict with ``city``, ``estimate`` (float or null), ``unit``,
        ``historical_average_paid``, ``method``, ``guardrails``,
        ``data_source``, and ``note``.
    """
    rows = load_congresses(path)
    paid = [row["paid_member_registrations"] for row in rows]
    average = _average(paid)
    confidence = flag_confidence(city, path)
    unseen = confidence["flag"] == "no_comparable_host"
    if unseen and guardrails:
        estimate = None
        note = (
            "No point estimate. This city has no comparable host in the simulated file, "
            "and the guardrail withholds a file-wide average presented as a forecast."
        )
    elif unseen:
        estimate = average
        note = (
            "Guardrails are off. The estimate is the average of every simulated congress, "
            "including cities that are not this one. This is the overconfident output the guardrail blocks."
        )
    else:
        same_city = [
            row["paid_member_registrations"]
            for row in rows
            if _norm(row["host_city"]) == _norm(city)
        ]
        estimate = _average(same_city)
        note = "Average paid registrations for this city inside the simulated file. This is not a validated forecast."
    return {
        "city": city,
        "estimate": estimate,
        "unit": "paid_member_registrations",
        "historical_average_paid": average,
        "method": "historical_average_baseline",
        "regression_fit": False,
        "guardrails": guardrails,
        "data_source": "simulated",
        "note": note,
    }


def compare_cities(
    cities: tuple[str, ...] = CANDIDATE_CITIES,
    usd_per_km: float = 0.10,
    guardrails: bool = True,
    path: Path | None = None,
) -> dict:
    """Place candidate cities side by side without a predictive rank.

    Ranking by predicted attendance is withheld. The scope allows that rank
    only after held-out evaluation supports it, and this demo has no such
    evaluation. Host-feasibility items from the bid book are marked
    unverified because the bid book is not in this repository.

    Args:
        cities: Candidate host cities. Defaults to the working set named in
            the scope: Barcelona, Buenos Aires, Rome, Berlin, and Guatemala City.
        usd_per_km: Airfare scenario passed through to ``estimate_travel_cost``.
            Defaults to 0.10 as an explicit demo rate, not a market quote.
        guardrails: Passed through to ``estimate_attendance``. Defaults to true.
        path: CSV path. Defaults to the bundled simulated file.

    Returns:
        A dict with ``predictive_rank`` set to null, ``rows`` in the input
        order, ``usd_per_km``, and ``note``.
    """
    rows = []
    for city in cities:
        attendance = estimate_attendance(city, guardrails=guardrails, path=path)
        travel = estimate_travel_cost(city, usd_per_km=usd_per_km)
        confidence = flag_confidence(city, path)
        rows.append(
            {
                "city": city,
                "confidence_flag": confidence["flag"],
                "attendance_estimate": attendance["estimate"],
                "attendance_note": attendance["note"],
                "scenario_cost_from_new_york_usd": next(
                    item["scenario_cost_usd"] for item in travel["by_hub"] if item["hub"] == "New York"
                ),
                "host_feasibility": "unverified",
            }
        )
    return {
        "predictive_rank": None,
        "rows": rows,
        "usd_per_km": usd_per_km,
        "data_source": "simulated",
        "note": "Side-by-side comparison only. No predictive rank is assigned.",
    }


def answer_decision_question(question: str, city: str = "Rome", guardrails: bool = True) -> dict:
    """Answer a city question, and refuse profitability language when guarded.

    The pilot's outcome is paid registrations. With guardrails on, a question
    that asks about profit, revenue, cost, financial success, or success versus
    failure is refused. With guardrails off, the tool emits the success/failure
    sentence the scope excludes, using the simulated file-wide median as a
    stand-in. That sentence is demonstration output, not a LASA result.

    Args:
        question: The user's question, plain text.
        city: City named in the unguarded demonstration. Defaults to Rome,
            which has no row in the simulated file.
        guardrails: When true, refuse profitability and success/failure
            conclusions. Defaults to true.

    Returns:
        A dict with ``refused`` (bool), ``answer`` (str), ``guardrails``, and
        ``data_source``.
    """
    text = question.lower()
    profitability_terms = (
        "profit",
        "revenue",
        "financially successful",
        "financial success",
        "success or failure",
        "successful or unsuccessful",
    )
    asks_profit = any(term in text for term in profitability_terms)
    if asks_profit and guardrails:
        return {
            "refused": True,
            "answer": (
                "This pilot reports paid-registration context only. "
                "It does not state whether a congress will be financially successful."
            ),
            "guardrails": True,
            "data_source": "simulated",
        }
    if asks_profit:
        rows = load_congresses()
        paid = sorted(row["paid_member_registrations"] for row in rows)
        median = paid[len(paid) // 2]
        return {
            "refused": False,
            "answer": (
                f"Guardrails are off. A success/failure label would call {city} financially successful "
                f"when a borrowed average exceeds the simulated median of {median}. "
                "That label is the output this pilot excludes."
            ),
            "guardrails": False,
            "data_source": "simulated",
        }
    attendance = estimate_attendance(city, guardrails=guardrails)
    if attendance["estimate"] is None:
        answer = attendance["note"]
    else:
        answer = (
            f"Simulated baseline for {city}: {attendance['estimate']} paid registrations. {attendance['note']}"
        )
    return {
        "refused": False,
        "answer": answer,
        "guardrails": guardrails,
        "data_source": "simulated",
    }
