from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "skills" / "loopseed" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from one_shotted_core import (  # noqa: E402
    OneShottedError,
    add_gate,
    bind_project,
    finalize,
    initialize,
    record_defect,
    record_gate_result,
    status,
    transition,
    validate,
)


class OneShottedTests(unittest.TestCase):
    def make_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        return temporary, root

    def freeze_verification(self, root: Path) -> Path:
        artifact = root / "artifact.txt"
        artifact.write_text("candidate-v1\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True
        )
        subprocess.run(["git", "config", "user.name", "LoopSeed Test"], cwd=root, check=True)
        subprocess.run(["git", "add", "artifact.txt"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "candidate"], cwd=root, check=True)
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        transition(root, phase="PLAN", next_action="Plan the candidate")
        transition(root, phase="IMPLEMENT", next_action="Build the candidate")
        transition(root, phase="VERIFY", next_action="Freeze and verify the candidate")
        bind_project(root, "demo-project", head, "artifact.txt")
        return artifact

    def add_flow_gate(self, root: Path) -> None:
        add_gate(
            root,
            "FLOW",
            "Complete flow",
            "The documented primary flow completes",
            "lead",
            "verifier",
            role="hard",
        )

    def add_quality_bar_gate(self, root: Path) -> None:
        add_gate(
            root,
            "BAR",
            "Inspectable quality bar",
            "Against equivalent evidence, the candidate meets or beats the declared inspectable bar while preserving the product identity",
            "lead",
            "fresh-critic",
            role="bar",
        )

    def pass_required_gates(self, root: Path, artifact: Path) -> None:
        record_gate_result(
            root,
            "FLOW",
            "PASS",
            "verifier",
            "Flow completed",
            artifacts=[str(artifact)],
        )
        record_gate_result(
            root,
            "BAR",
            "PASS",
            "fresh-critic",
            "Blind/equivalent comparison met the declared quality bar",
            artifacts=[str(artifact)],
        )

    def test_initialize_creates_bounded_control_plane(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            result = initialize(root, "Build a verified demo")
            self.assertTrue(result["ok"])
            target = root / ".loopseed" / "one-shotted"
            self.assertTrue((target / "goal-contract.json").is_file())
            self.assertTrue((target / "evidence.jsonl").is_file())
            self.assertFalse((target / "final-report.json").exists())
            self.assertEqual(status(root)["phase"], "BIND")

    def test_gate_owner_cannot_be_verifier(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "Build a demo")
            with self.assertRaisesRegex(OneShottedError, "must be different"):
                add_gate(root, "BUILD", "Build", "Build exits zero", "lead", "lead")

    def test_only_declared_verifier_can_record_verdict(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "Build a demo")
            self.add_flow_gate(root)
            with self.assertRaisesRegex(OneShottedError, "must be recorded by verifier"):
                record_gate_result(root, "FLOW", "PASS", "lead", "It works")

    def test_fail_enters_repair(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "Build a demo")
            self.add_flow_gate(root)
            result = record_gate_result(root, "FLOW", "FAIL", "verifier", "Flow crashes")
            self.assertEqual(result["phase"], "REPAIR")
            self.assertEqual(status(root)["gate_counts"]["FAIL"], 1)

    def test_finalize_requires_at_least_one_required_gate(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "Build a demo")
            with self.assertRaisesRegex(OneShottedError, "At least one required"):
                finalize(root)

    def test_finalize_requires_all_required_gates_pass(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "Build a demo")
            self.add_flow_gate(root)
            self.add_quality_bar_gate(root)
            with self.assertRaisesRegex(OneShottedError, "not PASS"):
                finalize(root)

    def test_hard_floor_alone_cannot_finalize_v0_8(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "Build a demo")
            self.add_flow_gate(root)
            artifact = self.freeze_verification(root)
            record_gate_result(
                root,
                "FLOW",
                "PASS",
                "verifier",
                "Flow completed",
                artifacts=[str(artifact)],
            )
            with self.assertRaisesRegex(OneShottedError, "quality-bar"):
                finalize(root)

    def test_quality_bar_alone_cannot_finalize_v0_8(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "Build a demo")
            self.add_quality_bar_gate(root)
            artifact = self.freeze_verification(root)
            record_gate_result(
                root,
                "BAR",
                "PASS",
                "fresh-critic",
                "Bar met",
                artifacts=[str(artifact)],
            )
            with self.assertRaisesRegex(OneShottedError, "hard-floor"):
                finalize(root)

    def test_successful_finalize_writes_verified_report(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "Build a demo")
            self.add_flow_gate(root)
            self.add_quality_bar_gate(root)
            artifact = self.freeze_verification(root)
            self.pass_required_gates(root, artifact)
            result = finalize(root)
            self.assertEqual(result["status"], "VERIFIED")
            self.assertTrue(validate(root, require_final=True)["ok"])
            report = json.loads(Path(result["final_report"]).read_text(encoding="utf-8"))
            self.assertEqual(report["schema_version"], "1.3")
            self.assertEqual(report["verdict"], "VERIFIED")
            self.assertEqual(report["hard_gates"], ["FLOW"])
            self.assertEqual(report["quality_bar_gates"], ["BAR"])

    def test_status_exposes_quality_bar_state(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "Build a demo")
            self.add_flow_gate(root)
            self.add_quality_bar_gate(root)
            current = status(root)
            self.assertEqual(current["gate_role_counts"], {"hard": 1, "bar": 1})
            self.assertEqual(current["quality_bar_statuses"], {"BAR": "PENDING"})

    def test_open_p1_defect_blocks_then_resolution_allows_finalize(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "Build a demo")
            self.add_flow_gate(root)
            self.add_quality_bar_gate(root)
            artifact = self.freeze_verification(root)
            self.pass_required_gates(root, artifact)
            record_defect(root, "VIS-1", "P1", "OPEN", "Unreadable state", "verifier")
            with self.assertRaisesRegex(OneShottedError, "Open P0/P1"):
                finalize(root)
            record_defect(root, "VIS-1", "P1", "RESOLVED", "State is readable", "verifier")
            self.assertEqual(finalize(root)["status"], "VERIFIED")

    def test_two_no_progress_rounds_force_root_cause_replan(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "Build a demo")
            transition(root, phase="PLAN", next_action="Plan route A")
            transition(root, phase="IMPLEMENT", next_action="Try route A")
            first = transition(root, no_progress=True)
            second = transition(root, no_progress=True)
            self.assertFalse(first["reroute_required"])
            self.assertTrue(second["reroute_required"])
            self.assertEqual(second["phase"], "PLAN")
            self.assertIn("materially different route", second["next_action"])

    def test_blocked_requires_reason_and_unblock_condition(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "Build a demo")
            with self.assertRaisesRegex(OneShottedError, "requires both"):
                transition(root, blocked_reason="Need credentials")
            result = transition(
                root,
                blocked_reason="Deployment credentials are unavailable",
                unblock_condition="Owner supplies scoped deployment credentials",
            )
            self.assertEqual(result["status"], "BLOCKED")

    def test_validation_rejects_tampered_pass_without_evidence(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "Build a demo")
            self.add_flow_gate(root)
            path = root / ".loopseed" / "one-shotted" / "acceptance.json"
            acceptance = json.loads(path.read_text(encoding="utf-8"))
            acceptance["gates"][0]["status"] = "PASS"
            path.write_text(json.dumps(acceptance), encoding="utf-8")
            report = validate(root)
            self.assertFalse(report["ok"])
            self.assertTrue(any("without verifier-authored PASS evidence" in item for item in report["errors"]))


if __name__ == "__main__":
    unittest.main()
