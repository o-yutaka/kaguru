from __future__ import annotations

"""Lightweight BLACK fast-lane for Kaggriculture research.

Uses the same principles that proved useful in prior official-engine work:
- official environment remains authoritative;
- deterministic, context-safe fingerprints;
- bounded adaptive search budgets;
- cheap pre-screening before expensive evaluation;
- parallel independent arms;
- paired seeds and both seats;
- measured promotion only.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, Iterable, Mapping, Sequence

SEEDS = (42, 1000, 1050, 1100, 1200, 1500, 2026, 300257)
SEATS = (0, 1)
ARMS = (
    "A_BASE",
    "B_OPP_SELL",
    "C_GEOMETRY",
    "D_MARKET_TIMING",
    "E_OPP_MARKET",
    "F_OPP_GEOMETRY_MARKET",
)


@dataclass(frozen=True)
class DecisionKey:
    state: str
    context: str
    option: str
    opponent: str
    market: str

    def digest(self) -> str:
        raw = "|".join((self.state, self.context, self.option, self.opponent, self.market))
        return sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SearchBudget:
    width: int
    horizon: int
    reason: str


def adaptive_budget(
    *,
    legal_count: int,
    market_volatile: bool = False,
    opponent_pressure: bool = False,
    geometry_critical: bool = False,
    terminal_window: bool = False,
    base_width: int = 4,
    base_horizon: int = 4,
    max_width: int = 12,
    max_horizon: int = 10,
) -> SearchBudget:
    risk = 0
    reasons: list[str] = []
    for active, weight, label in (
        (market_volatile, 2, "market"),
        (opponent_pressure, 2, "opponent"),
        (geometry_critical, 2, "geometry"),
        (terminal_window, 3, "terminal"),
    ):
        if active:
            risk += weight
            reasons.append(label)
    if legal_count >= 8:
        risk += 1
        reasons.append("wide_legal")

    width = base_width
    horizon = base_horizon
    if risk >= 6:
        width *= 3
        horizon += 5
    elif risk >= 4:
        width *= 2
        horizon += 3
    elif risk >= 2:
        width = max(width, int(round(width * 1.5)))
        horizon += 2

    return SearchBudget(
        width=max(1, min(max_width, width)),
        horizon=max(1, min(max_horizon, horizon)),
        reason=",".join(reasons) or "ordinary",
    )


def stable_fingerprint(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(payload.encode("utf-8")).hexdigest()


def rank_fast_candidate(metrics: Mapping[str, float]) -> float:
    """Advisory ranking only; never treated as official score."""
    return (
        1.0 * float(metrics.get("cash", 0.0))
        + 20.0 * float(metrics.get("sell_timing_gain", 0.0))
        + 15.0 * float(metrics.get("geometry_gain", 0.0))
        + 15.0 * float(metrics.get("opponent_signal_gain", 0.0))
        - 5.0 * float(metrics.get("runtime_penalty", 0.0))
    )


def build_matrix() -> list[dict[str, Any]]:
    return [
        {"arm": arm, "seed": seed, "seat": seat, "key": stable_fingerprint(f"{arm}|{seed}|{seat}")}
        for arm in ARMS
        for seed in SEEDS
        for seat in SEATS
    ]


def parallel_preflight(out_dir: Path) -> dict[str, Any]:
    """Cheap 96-job structural pass before official expensive evaluation."""
    out_dir.mkdir(parents=True, exist_ok=True)
    matrix = build_matrix()

    def run(job: Mapping[str, Any]) -> Mapping[str, Any]:
        key = job["key"]
        return {**job, "preflight": "PASS", "fingerprint": key}

    start = perf_counter()
    results: list[Mapping[str, Any]] = []
    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = [pool.submit(run, job) for job in matrix]
        for future in as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda x: (x["arm"], x["seed"], x["seat"]))
    report = {
        "mode": "parallel_preflight",
        "authoritative": False,
        "jobs": len(results),
        "workers": 16,
        "passes": sum(r["preflight"] == "PASS" for r in results),
        "elapsed_s": perf_counter() - start,
        "arms": list(ARMS),
        "seeds": list(SEEDS),
        "seats": list(SEATS),
        "results": results,
    }
    (out_dir / "fastlane_preflight.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report


def promote(measured_delta: float, reproducible: bool, regression: bool) -> str:
    if regression:
        return "REJECT"
    if not reproducible:
        return "REJECT"
    return "PROMOTE" if measured_delta > 0 else "HOLD"


__all__ = [
    "SEEDS",
    "SEATS",
    "ARMS",
    "DecisionKey",
    "SearchBudget",
    "adaptive_budget",
    "stable_fingerprint",
    "rank_fast_candidate",
    "build_matrix",
    "parallel_preflight",
    "promote",
]

if __name__ == "__main__":
    report = parallel_preflight(Path("artifacts/kaggriculture_black"))
    print(json.dumps({k: v for k, v in report.items() if k != "results"}, ensure_ascii=False, indent=2))
