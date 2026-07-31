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
    record_gate_result,
    resume,
    run_evidence,
    status,
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

    def prepare_bound(self) -> tuple[tempfile.TemporaryDirectory[str], Path, str]:
        temporary, root, command = self.make_root()
        initialize(root, "Verify resumable C1.1 evidence")
        bind_project(root, "demo-project", "candidate-1", "artifact.txt")
        add_gate(
            root,
            "PRIMARY",
            "Primary machine gate",
            "Verification command exits zero without mutating the subject",
            "builder",
            "verifier",
            requires_machine_evidence=True,
        )
        return temporary, root, command

    def prepare_blocked(self) -> tuple[tempfile.TemporaryDirectory[str], Path, str, str]:
        temporary, root, command = self.prepare_bound()
        blocked = transition(
            root,
            blocked_reason="Verification surface unavailable",
            unblock_condition="Verification command succeeds",
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
        self.assertTrue(result["integrity_stable"])
        return str(result["evidence_id"])

    def test_explicit_binding_allows_machine_gate_without_blocker(self) -> None:
        temporary, root, command = self.prepare_bound()
        with temporary:
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

    def test_binding_is_idempotent_but_cannot_silently_change_subject(self) -> None:
        temporary, root, _ = self.prepare_bound()
        with temporary:
            same = bind_project(root, "demo-project", "candidate-1", "artifact.txt")
            self.assertTrue(same["idempotent"])
            with self.assertRaisesRegex(OneShottedError, "already bound"):
                bind_project(root, "other-project", "candidate-1", "artifact.txt")

    def test_binding_rejects_artifact_from_another_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            root = Path(first)
            other_root = Path(second)
            (root / ".git").mkdir()
            external_artifact = other_root / "artifact.txt"
            external_artifact.write_text("candidate-from-project-b\n", encoding="utf-8")
            initialize(root, "Reject repository A plus artifact B")
            with self.assertRaisesRegex(OneShottedError, "within the project root"):
                bind_project(root, "project-a", "candidate-a", str(external_artifact))

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

    def test_finalize_rejects_artifact_drift_after_verification(self) -> None:
        temporary, root, command = self.prepare_bound()
        with temporary:
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

    def test_verifier_mutating_artifact_and_exiting_zero_is_rejected(self) -> None:
        temporary, root, _ = self.prepare_bound()
        with temporary:
            mutator = root / "mutate.py"
            mutator.write_text(
                "from pathlib import Path\nPath('artifact.txt').write_text('mutated\\n')\nprint('ok')\n",
                encoding="utf-8",
            )
            command = f'"{sys.executable}" "{mutator}"'
            result = run_evidence(
                root,
                "verifier",
                command,
                "demo-project",
                "candidate-1",
                "artifact.txt",
                gate_id="PRIMARY",
            )
            self.assertFalse(result["ok"])
            self.assertEqual(result["result"], "FAIL")
            self.assertEqual(result["integrity_failure_reason"], "ARTIFACT_MUTATED_DURING_VERIFICATION")
            self.assertEqual(status(root)["gate_counts"]["FAIL"], 1)
            with self.assertRaises(OneShottedError):
                finalize(root)

    def test_unblock_command_mutating_artifact_is_not_resumable(self) -> None:
        temporary, root, _, blocker_id = self.prepare_blocked()
        with temporary:
            mutator = root / "mutate.py"
            mutator.write_text(
                "from pathlib import Path\nPath('artifact.txt').write_text('mutated\\n')\nprint('ok')\n",
                encoding="utf-8",
            )
            command = f'"{sys.executable}" "{mutator}"'
            result = run_evidence(
                root,
                "verifier",
                command,
                "demo-project",
                "candidate-1",
                "artifact.txt",
                blocker_id=blocker_id,
            )
            self.assertEqual(result["result"], "FAIL")
            with self.assertRaisesRegex(OneShottedError, "did not pass"):
                resume(root, str(result["evidence_id"]), "verifier")
            self.assertEqual(status(root)["status"], "BLOCKED")

    def test_audit_rejects_forged_pass_with_mismatched_subject_hashes(self) -> None:
        temporary, root, command = self.prepare_bound()
        with temporary:
            run_evidence(
                root,
                "verifier",
                command,
                "demo-project",
                "candidate-1",
                "artifact.txt",
                gate_id="PRIMARY",
            )
            ledger = root / ".loopseed" / "one-shotted" / "evidence.jsonl"
            item = json.loads(ledger.read_text(encoding="utf-8").strip())
            item["artifact_after"]["sha256"] = "0" * 64
            item["artifact"]["sha256"] = "0" * 64
            ledger.write_text(json.dumps(item) + "\n", encoding="utf-8")
            report = validate(root)
            self.assertFalse(report["ok"])
            self.assertTrue(any("integrity_stable is inconsistent" in error for error in report["errors"]))

    def test_machine_gate_rejects_hand_forged_manual_pass(self) -> None:
        temporary, root, _ = self.make_root()
        with temporary:
            initialize(root, "Reject manual PASS")
            bind_project(root, "demo-project", "candidate-1", "artifact.txt")
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

    def test_runner_rejects_actual_git_head_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "LoopSeed Test"], cwd=root, check=True)
            (root / "artifact.txt").write_text("candidate-v1\n", encoding="utf-8")
            (root / "verify.py").write_text("print('verified')\n", encoding="utf-8")
            subprocess.run(["git", "add", "artifact.txt", "verify.py"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "candidate one"], cwd=root, check=True)
            first = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=True
            ).stdout.strip()

            initialize(root, "Reject wrong actual HEAD")
            bind_project(root, "demo-project", first, "artifact.txt")
            add_gate(
                root,
                "PRIMARY",
                "Machine gate",
                "Must execute at bound HEAD",
                "builder",
                "verifier",
                requires_machine_evidence=True,
            )
            (root / "unrelated.txt").write_text("next\n", encoding="utf-8")
            subprocess.run(["git", "add", "unrelated.txt"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "candidate two"], cwd=root, check=True)
            command = f'"{sys.executable}" "{root / "verify.py"}"'
            with self.assertRaisesRegex(OneShottedError, "Actual Git HEAD"):
                run_evidence(
                    root,
                    "verifier",
                    command,
                    "demo-project",
                    first,
                    "artifact.txt",
                    gate_id="PRIMARY",
                )


if __name__ == "__main__":
    unittest.main()
