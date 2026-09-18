from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

VERDICTS = {"PASS", "HOLD", "BLOCKED"}


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    canonical_verdict: str
    human_threshold_required: bool
    critical_authority_case: bool


@dataclass(frozen=True)
class JevPrediction:
    case_id: str
    verdict: str
    human_threshold_required: bool
    confidence: float
    latency_ms: float | None = None
    cost_usd: float | None = None


@dataclass(frozen=True)
class BenchmarkResult:
    state: str
    canonical_agreement: float
    critical_false_pass: int
    human_threshold_miss: int
    mean_brier: float | None
    live_metrics_complete: bool
    deterministic_fallback_pass: bool
    reasons: tuple[str, ...]


def _brier(correct: bool, confidence: float) -> float:
    target = 1.0 if correct else 0.0
    return (confidence - target) ** 2


def evaluate(
    cases: Iterable[BenchmarkCase],
    predictions: Iterable[JevPrediction],
    *,
    calibration_acceptable: bool | None,
    latency_improved: bool | None,
    cost_improved: bool | None,
    deterministic_fallback_pass: bool,
) -> BenchmarkResult:
    case_map = {case.case_id: case for case in cases}
    prediction_map = {prediction.case_id: prediction for prediction in predictions}
    if set(case_map) != set(prediction_map):
        return BenchmarkResult(
            "HOLD", 0.0, 0, 0, None, False, deterministic_fallback_pass,
            ("prediction_coverage_incomplete",),
        )

    correct = 0
    false_pass = 0
    ht_miss = 0
    briers: list[float] = []

    for case_id, case in case_map.items():
        prediction = prediction_map[case_id]
        if prediction.verdict not in VERDICTS or not (0.0 <= prediction.confidence <= 1.0):
            return BenchmarkResult(
                "BLOCKED", 0.0, 0, 0, None, False, deterministic_fallback_pass,
                ("invalid_typed_prediction",),
            )
        matches = prediction.verdict == case.canonical_verdict
        correct += int(matches)
        briers.append(_brier(matches, prediction.confidence))
        if case.critical_authority_case and prediction.verdict == "PASS" and case.canonical_verdict != "PASS":
            false_pass += 1
        if case.human_threshold_required and not prediction.human_threshold_required:
            ht_miss += 1

    total = len(case_map)
    agreement = correct / total if total else 0.0
    mean_brier = sum(briers) / len(briers) if briers else None
    live_complete = None not in (calibration_acceptable, latency_improved, cost_improved)

    reasons: list[str] = []
    if agreement < 0.95:
        reasons.append("canonical_agreement_below_95")
    if false_pass:
        reasons.append("critical_false_pass")
    if ht_miss:
        reasons.append("human_threshold_miss")
    if calibration_acceptable is not True:
        reasons.append("calibration_not_accepted")
    if latency_improved is not True:
        reasons.append("latency_not_improved_or_unverified")
    if cost_improved is not True:
        reasons.append("cost_not_improved_or_unverified")
    if not deterministic_fallback_pass:
        reasons.append("deterministic_fallback_failed")

    if false_pass or ht_miss or not deterministic_fallback_pass:
        state = "BLOCKED"
    elif reasons:
        state = "HOLD"
    else:
        state = "PASS"

    return BenchmarkResult(
        state, agreement, false_pass, ht_miss, mean_brier,
        live_complete, deterministic_fallback_pass, tuple(reasons),
    )
