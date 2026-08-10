#!/usr/bin/env python3
"""Evaluate the bounded v0.8 Reality Gate equal-budget A/B experiment.

This tool does not judge whether a game is enjoyable. It verifies control parity,
counts predefined first-use improvements, and applies the admission thresholds
frozen by the experiment contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

EXPECTED_SCHEMA = "0.1"
EXPECTED_PAIR_IDS = ("P1", "P2", "P3")
VALID_STATUSES = {"VERIFIED", "BLOCKED", "FAIL"}


class ExperimentError(ValueError):
    """Raised when an experiment record is malformed or internally inconsistent."""


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _as_non_negative_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if number < 0 or not math.isfinite(number):
        return None
    return number


def _as_string_list(value: Any) -> list[str] | None:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        return None
    return [item.strip() for item in value]


def _arm_errors(
    arm: Any,
    *,
    label: str,
    expected_fingerprint: str,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(arm, dict):
        return [f"{label} must be an object"]

    _require(
        arm.get("controls_sha256") == expected_fingerprint,
        f"{label}.controls_sha256 does not match frozen controls",
        errors,
    )
    _require(
        str(arm.get("status", "")).upper() in VALID_STATUSES,
        f"{label}.status must be VERIFIED, BLOCKED, or FAIL",
        errors,
    )
    _require(
        isinstance(arm.get("integrity_verified"), bool),
        f"{label}.integrity_verified must be boolean",
        errors,
    )
    _require(
        isinstance(arm.get("scope_expanded"), bool),
        f"{label}.scope_expanded must be boolean",
        errors,
    )
    _require(
        isinstance(arm.get("first_action_success"), bool),
        f"{label}.first_action_success must be boolean",
        errors,
    )

    for field in (
        "candidate_commit",
        "artifact_sha256",
    ):
        _require(
            isinstance(arm.get(field), str) and bool(str(arm.get(field)).strip()),
            f"{label}.{field} must be a non-empty string",
            errors,
        )

    commit = str(arm.get("candidate_commit", ""))
    _require(
        len(commit) in {40, 64}
        and all(ch in "0123456789abcdefABCDEF" for ch in commit),
        f"{label}.candidate_commit must be a 40- or 64-character hexadecimal digest",
        errors,
    )
    digest = str(arm.get("artifact_sha256", ""))
    _require(
        len(digest) == 64 and all(ch in "0123456789abcdefABCDEF" for ch in digest),
        f"{label}.artifact_sha256 must be a 64-character hexadecimal digest",
        errors,
    )

    for field in (
        "wall_clock_seconds",
        "repair_rounds",
        "first_meaningful_action_seconds",
    ):
        _require(
            _as_non_negative_number(arm.get(field)) is not None,
            f"{label}.{field} must be a finite non-negative number",
            errors,
        )

    cost_units = arm.get("cost_units")
    _require(
        cost_units is None or _as_non_negative_number(cost_units) is not None,
        f"{label}.cost_units must be null or a finite non-negative number",
        errors,
    )

    for field in (
        "confusion_points",
        "feedback_defects",
        "attention_defects",
    ):
        _require(
            _as_string_list(arm.get(field)) is not None,
            f"{label}.{field} must be an array of non-empty strings",
            errors,
        )

    return errors


def _clarity_improved(a: dict[str, Any], b: dict[str, Any], threshold: float) -> bool:
    a_success = bool(a["first_action_success"])
    b_success = bool(b["first_action_success"])
    a_time = float(a["first_meaningful_action_seconds"])
    b_time = float(b["first_meaningful_action_seconds"])
    a_confusion = len(a["confusion_points"])
    b_confusion = len(b["confusion_points"])

    if b_success and not a_success:
        return True
    if not b_success:
        return False
    if a_success and a_time > 0:
        time_gain = (a_time - b_time) / a_time
        if time_gain >= threshold and b_confusion <= a_confusion:
            return True
    return b_confusion < a_confusion and b_time <= a_time


def _pair_improvements(
    a: dict[str, Any],
    b: dict[str, Any],
    *,
    min_clarity_gain_ratio: float,
) -> list[str]:
    improvements: list[str] = []
    if _clarity_improved(a, b, min_clarity_gain_ratio):
        improvements.append("first_use_clarity")
    if len(b["feedback_defects"]) < len(a["feedback_defects"]):
        improvements.append("core_action_feedback")
    if len(b["attention_defects"]) < len(a["attention_defects"]):
        improvements.append("attention_path")
    return improvements


def evaluate(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(data, dict):
        raise ExperimentError("Experiment record must be a JSON object")

    _require(
        data.get("schema_version") == EXPECTED_SCHEMA,
        f"schema_version must be {EXPECTED_SCHEMA}",
        errors,
    )
    _require(
        data.get("experiment_id") == "v0.8-reality-gate-ab",
        "experiment_id must be v0.8-reality-gate-ab",
        errors,
    )

    controls = data.get("controls")
    if not isinstance(controls, dict) or not controls:
        errors.append("controls must be a non-empty object")
        controls = {}
    expected_fingerprint = canonical_sha256(controls)

    thresholds = data.get("thresholds")
    if not isinstance(thresholds, dict):
        errors.append("thresholds must be an object")
        thresholds = {}

    max_time_regression = _as_non_negative_number(
        thresholds.get("max_time_regression_ratio")
    )
    max_tool_regression = _as_non_negative_number(
        thresholds.get("max_cost_regression_ratio")
    )
    min_clarity_gain = _as_non_negative_number(
        thresholds.get("min_clarity_gain_ratio")
    )
    _require(
        max_time_regression is not None,
        "thresholds.max_time_regression_ratio must be non-negative",
        errors,
    )
    _require(
        max_tool_regression is not None,
        "thresholds.max_cost_regression_ratio must be non-negative",
        errors,
    )
    _require(
        min_clarity_gain is not None and min_clarity_gain <= 1,
        "thresholds.min_clarity_gain_ratio must be between 0 and 1",
        errors,
    )

    pairs = data.get("pairs")
    if not isinstance(pairs, list):
        errors.append("pairs must be an array")
        pairs = []
    pair_ids = [item.get("id") if isinstance(item, dict) else None for item in pairs]
    _require(
        tuple(pair_ids) == EXPECTED_PAIR_IDS,
        "pairs must contain exactly P1, P2, and P3 in order",
        errors,
    )

    pair_summaries: list[dict[str, Any]] = []
    valid_pairs = 0
    dimension_counts = {
        "first_use_clarity": 0,
        "core_action_feedback": 0,
        "attention_path": 0,
    }
    consecutive_no_effect = 0
    stop_no_effect = False
    any_cost_regression = False
    any_completion_regression = False
    any_scope_expansion = False

    for index, pair in enumerate(pairs):
        label = f"pairs[{index}]"
        if not isinstance(pair, dict):
            errors.append(f"{label} must be an object")
            continue
        _require(
            isinstance(pair.get("valid"), bool),
            f"{label}.valid must be boolean",
            errors,
        )
        if pair.get("valid") is False:
            _require(
                isinstance(pair.get("invalid_reason"), str)
                and bool(pair.get("invalid_reason", "").strip()),
                f"{label}.invalid_reason is required when valid is false",
                errors,
            )
            pair_summaries.append(
                {
                    "id": pair.get("id"),
                    "valid": False,
                    "reason": pair.get("invalid_reason"),
                }
            )
            continue

        preference = pair.get("blinded_human_preference")
        _require(
            preference in {"A", "B", "TIE", "UNAVAILABLE"},
            f"{label}.blinded_human_preference must be A, B, TIE, or UNAVAILABLE",
            errors,
        )
        a = pair.get("A")
        b = pair.get("B")
        errors.extend(
            _arm_errors(a, label=f"{label}.A", expected_fingerprint=expected_fingerprint)
        )
        errors.extend(
            _arm_errors(b, label=f"{label}.B", expected_fingerprint=expected_fingerprint)
        )
        if not isinstance(a, dict) or not isinstance(b, dict):
            continue

        valid_pairs += 1
        improvements = _pair_improvements(
            a,
            b,
            min_clarity_gain_ratio=float(min_clarity_gain or 0),
        )
        for dimension in improvements:
            dimension_counts[dimension] += 1
        if improvements:
            consecutive_no_effect = 0
        else:
            consecutive_no_effect += 1
            if consecutive_no_effect >= 2:
                stop_no_effect = True

        pair_scope_expanded = bool(a.get("scope_expanded")) or bool(b.get("scope_expanded"))
        any_scope_expansion = any_scope_expansion or pair_scope_expanded

        completion_regression = (
            str(a.get("status", "")).upper() == "VERIFIED"
            and str(b.get("status", "")).upper() != "VERIFIED"
        ) or (bool(a.get("integrity_verified")) and not bool(b.get("integrity_verified")))
        any_completion_regression = any_completion_regression or completion_regression

        a_time = float(a.get("wall_clock_seconds", 0))
        b_time = float(b.get("wall_clock_seconds", 0))
        time_regression_ratio = 0.0 if a_time == 0 else (b_time - a_time) / a_time

        a_cost = a.get("cost_units")
        b_cost = b.get("cost_units")
        tool_regression_ratio: float | None = None
        if a_cost is not None and b_cost is not None:
            a_cost_float = float(a_cost)
            tool_regression_ratio = (
                0.0
                if a_cost_float == 0
                else (float(b_cost) - a_cost_float) / a_cost_float
            )

        pair_cost_regression = time_regression_ratio > float(max_time_regression or 0)
        if tool_regression_ratio is not None:
            pair_cost_regression = pair_cost_regression or (
                tool_regression_ratio > float(max_tool_regression or 0)
            )
        any_cost_regression = any_cost_regression or pair_cost_regression

        pair_summaries.append(
            {
                "id": pair.get("id"),
                "valid": True,
                "improvements": improvements,
                "time_regression_ratio": round(time_regression_ratio, 4),
                "cost_units_regression_ratio": (
                    None
                    if tool_regression_ratio is None
                    else round(tool_regression_ratio, 4)
                ),
                "cost_regression": pair_cost_regression,
                "completion_regression": completion_regression,
                "scope_expanded": pair_scope_expanded,
            }
        )

    if errors:
        return {
            "decision": "INVALID",
            "errors": sorted(set(errors)),
            "controls_sha256": expected_fingerprint,
            "pair_summaries": pair_summaries,
        }

    if valid_pairs < 3:
        return {
            "decision": "INCOMPLETE",
            "errors": ["Three valid paired runs are required; rerun invalid pairs"],
            "controls_sha256": expected_fingerprint,
            "valid_pairs": valid_pairs,
            "pair_summaries": pair_summaries,
        }

    qualifying_dimensions = sorted(
        dimension for dimension, count in dimension_counts.items() if count >= 2
    )
    admitted = (
        bool(qualifying_dimensions)
        and not any_scope_expansion
        and not any_completion_regression
        and not any_cost_regression
        and not stop_no_effect
    )
    decision = "ADMIT" if admitted else ("STOP_NO_EFFECT" if stop_no_effect else "REJECT")
    return {
        "decision": decision,
        "errors": [],
        "controls_sha256": expected_fingerprint,
        "valid_pairs": valid_pairs,
        "dimension_counts": dimension_counts,
        "qualifying_dimensions": qualifying_dimensions,
        "scope_expansion": any_scope_expansion,
        "completion_regression": any_completion_regression,
        "cost_regression": any_cost_regression,
        "stop_no_effect": stop_no_effect,
        "pair_summaries": pair_summaries,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path, help="Path to the experiment JSON record")
    parser.add_argument(
        "--print-controls-sha",
        action="store_true",
        help="Print only the canonical SHA-256 of the frozen controls",
    )
    args = parser.parse_args(argv)

    try:
        data = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"decision": "INVALID", "errors": [str(exc)]}, indent=2))
        return 2

    if args.print_controls_sha:
        controls = data.get("controls") if isinstance(data, dict) else None
        if not isinstance(controls, dict) or not controls:
            print("controls must be a non-empty object", file=sys.stderr)
            return 2
        print(canonical_sha256(controls))
        return 0

    try:
        result = evaluate(data)
    except ExperimentError as exc:
        result = {"decision": "INVALID", "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["decision"] == "ADMIT" else (2 if result["decision"] in {"INVALID", "INCOMPLETE"} else 1)


if __name__ == "__main__":
    raise SystemExit(main())
