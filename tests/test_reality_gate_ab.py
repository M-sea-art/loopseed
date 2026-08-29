from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "evaluate_reality_gate_ab.py"
SPEC = importlib.util.spec_from_file_location("evaluate_reality_gate_ab", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def arm(
    fingerprint: str,
    *,
    action_time: float,
    confusion: list[str],
    feedback: list[str],
    attention: list[str],
    wall_time: float = 100,
    cost_units: float | None = 10,
    success: bool = True,
    status: str = "VERIFIED",
    integrity: bool = True,
    scope_expanded: bool = False,
) -> dict[str, object]:
    return {
        "controls_sha256": fingerprint,
        "candidate_commit": "a" * 40,
        "artifact_sha256": "b" * 64,
        "wall_clock_seconds": wall_time,
        "cost_units": cost_units,
        "repair_rounds": 1,
        "first_meaningful_action_seconds": action_time,
        "first_action_success": success,
        "confusion_points": confusion,
        "feedback_defects": feedback,
        "attention_defects": attention,
        "status": status,
        "integrity_verified": integrity,
        "scope_expanded": scope_expanded,
    }


def base_record() -> dict[str, object]:
    controls = {
        "baseline_commit": "772e2961a17ddc199b25b8b2ec4f4e926c9f9615",
        "seed_id": "single-screen-lantern-v1",
        "seed_sha256": "c" * 64,
        "model": "GPT-5.6 Pro",
        "execution_surface": "same-surface",
        "max_wall_clock_seconds": 900,
        "max_tool_calls": 40,
        "production_mode": "focused",
        "asset_access": "none",
        "target_platform": "browser",
        "playable_scope": "one screen, one loop, success, failure, restart",
        "acceptance_contract_sha256": "d" * 64,
    }
    fingerprint = MODULE.canonical_sha256(controls)
    pairs = []
    for pair_id in ("P1", "P2", "P3"):
        pairs.append(
            {
                "id": pair_id,
                "valid": True,
                "invalid_reason": None,
                "blinded_human_preference": "UNAVAILABLE",
                "A": arm(
                    fingerprint,
                    action_time=10,
                    confusion=["goal unclear", "control unclear"],
                    feedback=["weak hit feedback", "failure unclear"],
                    attention=["objective not prominent"],
                ),
                "B": arm(
                    fingerprint,
                    action_time=6,
                    confusion=["control unclear"],
                    feedback=["failure unclear"],
                    attention=[],
                    wall_time=110,
                    cost_units=11,
                ),
            }
        )
    return {
        "schema_version": "0.1",
        "experiment_id": "v0.8-reality-gate-ab",
        "controls": controls,
        "thresholds": {
            "min_clarity_gain_ratio": 0.2,
            "max_time_regression_ratio": 0.25,
            "max_cost_regression_ratio": 0.25,
        },
        "pairs": pairs,
    }


class RealityGateExperimentTests(unittest.TestCase):
    def test_admits_repeated_equal_budget_improvement(self) -> None:
        result = MODULE.evaluate(base_record())
        self.assertEqual(result["decision"], "ADMIT")
        self.assertIn("first_use_clarity", result["qualifying_dimensions"])

    def test_rejects_scope_expansion(self) -> None:
        data = base_record()
        data["pairs"][1]["B"]["scope_expanded"] = True
        result = MODULE.evaluate(data)
        self.assertEqual(result["decision"], "REJECT")
        self.assertTrue(result["scope_expansion"])

    def test_rejects_material_cost_regression(self) -> None:
        data = base_record()
        data["pairs"][0]["B"]["wall_clock_seconds"] = 150
        result = MODULE.evaluate(data)
        self.assertEqual(result["decision"], "REJECT")
        self.assertTrue(result["cost_regression"])

    def test_invalidates_control_drift(self) -> None:
        data = base_record()
        data["pairs"][0]["B"]["controls_sha256"] = "0" * 64
        result = MODULE.evaluate(data)
        self.assertEqual(result["decision"], "INVALID")
        self.assertTrue(any("frozen controls" in item for item in result["errors"]))

    def test_requires_three_valid_pairs(self) -> None:
        data = base_record()
        data["pairs"][2] = {
            "id": "P3",
            "valid": False,
            "invalid_reason": "Budget parity broke",
        }
        result = MODULE.evaluate(data)
        self.assertEqual(result["decision"], "INCOMPLETE")
        self.assertEqual(result["valid_pairs"], 2)

    def test_two_consecutive_no_effect_pairs_stop(self) -> None:
        data = base_record()
        for pair in data["pairs"][:2]:
            pair["B"] = copy.deepcopy(pair["A"])
        result = MODULE.evaluate(data)
        self.assertEqual(result["decision"], "STOP_NO_EFFECT")
        self.assertTrue(result["stop_no_effect"])


if __name__ == "__main__":
    unittest.main()
