from __future__ import annotations

import json
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
    finalize,
    initialize,
    record_gate_result,
    resume,
    run_evidence,
    transition,
    validate,
)


class C1RuntimeTests(unittest.TestCase):
    def make_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path, str]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        (root / ".git").mkdir()
        (root / "artifact.txt").write_text("candidate-v1\n", encoding="utf-8")
        script = root / "verify.py"
        script.write_text("print('verified')\n", encoding="utf-8")
        command = f'"{sys.executable}" "{script}"'
        return temporary, root, command

    def prepare_blocked(self) -> tuple[tempfile.TemporaryDirectory[str], Path, str, str]:
        temporary, root, command = self.make_root()
        initialize(root, "Verify resumable C1 evidence")
        add_gate(
            root,
            "PRIMARY",
            "Primary machine gate",
            "Verification command exits zero",
            "builder",
            "verifier",
            requires_machine_evidence=True,
        )
        blocked = transition(
            root,
            blocked_reason="Verification surface unavailable",
            unblock_condition="Verification command succeeds",
            project_id="demo-project",
            candidate_commit="candidate-1",
            artifact="artifact.txt",
        )
        return temporary, root, command, str(blocked["blocker_id"])

    def unblock(self, root: Path, command: str, blocker_id: str) -> str:
        result = run_evidence(
            root,
            "verifier",
            command,
            "demo-project",
            "candidate-1",
            "artifact.txt",
            blocker_id=blocker_id,
        )
        self.assertTrue(result["ok"])
        return str(result["evidence_id"])

    def test_complete_blocked_resume_verify_finalize_flow(self) -> None:
        temporary, root, command, blocker_id = self.prepare_blocked()
        with temporary:
            evidence_id = self.unblock(root, command, blocker_id)
            recovered = resume(root, evidence_id, "verifier")
            self.assertEqual(recovered["phase"], "VERIFY")
            gate = run_evidence(
                root,
                "verifier",
                command,
                "demo-project",
                "candidate-1",
                "artifact.txt",
                gate_id="PRIMARY",
            )
            self.assertEqual(gate["result"], "PASS")
            self.assertEqual(finalize(root)["status"], "VERIFIED")
            self.assertTrue(validate(root, require_final=True)["ok"])

    def test_resume_rejects_absent_evidence(self) -> None:
        temporary, root, _, _ = self.prepare_blocked()
        with temporary:
            with self.assertRaisesRegex(OneShottedError, "not found"):
                resume(root, "EV-missing", "verifier")

    def test_resume_rejects_stale_evidence(self) -> None:
        temporary, root, command, blocker_id = self.prepare_blocked()
        with temporary:
            evidence_id = self.unblock(root, command, blocker_id)
            ledger = root / ".loopseed" / "one-shotted" / "evidence.jsonl"
            item = json.loads(ledger.read_text(encoding="utf-8").strip())
            self.assertEqual(item["id"], evidence_id)
            item["created_at"] = "2000-01-01T00:00:00.000000Z"
            ledger.write_text(json.dumps(item) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(OneShottedError, "stale"):
                resume(root, evidence_id, "verifier")

    def test_runner_rejects_wrong_blocker(self) -> None:
        temporary, root, command, _ = self.prepare_blocked()
        with temporary:
            with self.assertRaisesRegex(OneShottedError, "active blocker"):
                run_evidence(
                    root,
                    "verifier",
                    command,
                    "demo-project",
                    "candidate-1",
                    "artifact.txt",
                    blocker_id="BLK-wrong",
                )

    def test_runner_rejects_wrong_binding(self) -> None:
        temporary, root, command, blocker_id = self.prepare_blocked()
        with temporary:
            with self.assertRaisesRegex(OneShottedError, "project binding"):
                run_evidence(
                    root,
                    "verifier",
                    command,
                    "other-project",
                    "candidate-1",
                    "artifact.txt",
                    blocker_id=blocker_id,
                )

    def test_finalize_rejects_artifact_drift(self) -> None:
        temporary, root, command, blocker_id = self.prepare_blocked()
        with temporary:
            evidence_id = self.unblock(root, command, blocker_id)
            resume(root, evidence_id, "verifier")
            run_evidence(
                root,
                "verifier",
                command,
                "demo-project",
                "candidate-1",
                "artifact.txt",
                gate_id="PRIMARY",
            )
            (root / "artifact.txt").write_text("candidate-v2\n", encoding="utf-8")
            with self.assertRaisesRegex(OneShottedError, "invalid run"):
                finalize(root)
            report = validate(root)
            self.assertTrue(any("artifact drift" in error for error in report["errors"]))

    def test_machine_gate_rejects_hand_forged_manual_pass(self) -> None:
        temporary, root, _ = self.make_root()
        with temporary:
            initialize(root, "Reject manual PASS")
            add_gate(
                root,
                "PRIMARY",
                "Machine gate",
                "Must execute",
                "builder",
                "verifier",
                requires_machine_evidence=True,
            )
            record_gate_result(root, "PRIMARY", "PASS", "verifier", "Trust me")
            report = validate(root)
            self.assertFalse(report["ok"])
            self.assertTrue(any("requires machine-executed" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
