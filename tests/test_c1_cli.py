from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "skills" / "loopseed" / "scripts"
CLI = SCRIPTS / "one_shotted.py"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from one_shotted_core import add_gate, initialize, transition  # noqa: E402


class C1CliTests(unittest.TestCase):
    def test_duplicate_init_returns_structured_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            initialize(root, "Keep the original run")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "init",
                    "--root",
                    str(root),
                    "--goal",
                    "Do not replace this run",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 2)
            payload = json.loads(completed.stdout)
            self.assertFalse(payload["ok"])
            self.assertIn("already exists", payload["error"])

    def test_bind_and_run_evidence_subcommands_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            (root / "artifact.txt").write_text("candidate-v1\n", encoding="utf-8")
            script = root / "verify.py"
            script.write_text("print('verified')\n", encoding="utf-8")
            command = f'"{sys.executable}" "{script}"'

            initialize(root, "Exercise C1.1 CLI")
            bound = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "bind",
                    "--root",
                    str(root),
                    "--project",
                    "demo-project",
                    "--candidate",
                    "candidate-1",
                    "--artifact",
                    "artifact.txt",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(bound.returncode, 0, bound.stderr or bound.stdout)
            self.assertTrue(json.loads(bound.stdout)["ok"])

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
                blocked_reason="Verification unavailable",
                unblock_condition="Verification succeeds",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "run-evidence",
                    "--root",
                    str(root),
                    "--blocker",
                    str(blocked["blocker_id"]),
                    "--actor",
                    "verifier",
                    "--command",
                    command,
                    "--project",
                    "demo-project",
                    "--candidate",
                    "candidate-1",
                    "--artifact",
                    "artifact.txt",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
            payload = json.loads(completed.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["purpose"], "UNBLOCK")
            self.assertTrue(payload["integrity_stable"])
            self.assertTrue(str(payload["evidence_id"]).startswith("EV-"))

    def test_help_lists_c1_1_commands(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(CLI), "--help"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0)
        for command in ("bind", "run-evidence", "resume"):
            self.assertIn(command, completed.stdout)


if __name__ == "__main__":
    unittest.main()
