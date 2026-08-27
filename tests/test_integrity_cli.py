from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CLI = REPO_ROOT / "skills" / "loopseed" / "scripts" / "one_shotted.py"


class IntegrityBridgeCliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> dict[str, object]:
        completed = subprocess.run(
            [sys.executable, str(CLI), *args],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        return json.loads(completed.stdout)

    def test_bind_run_evidence_and_finalize_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True
            )
            subprocess.run(
                ["git", "config", "user.name", "LoopSeed Test"], cwd=root, check=True
            )
            (root / "artifact.txt").write_text("candidate\n", encoding="utf-8")
            script = root / "verify.py"
            script.write_text("print('verified')\n", encoding="utf-8")
            subprocess.run(["git", "add", "artifact.txt", "verify.py"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "candidate"], cwd=root, check=True)
            head = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=root,
                text=True,
                capture_output=True,
                check=True,
            ).stdout.strip()

            root_args = ("--root", str(root))
            self.run_cli("init", *root_args, "--goal", "Verify a candidate")
            self.run_cli(
                "add-gate",
                *root_args,
                "--id",
                "SMOKE",
                "--title",
                "Smoke",
                "--criterion",
                "Verifier exits zero",
                "--owner",
                "builder",
                "--verifier",
                "verifier",
                "--machine",
            )
            self.run_cli(
                "add-gate",
                *root_args,
                "--id",
                "BAR",
                "--title",
                "Quality bar",
                "--criterion",
                "The bound candidate meets the declared CLI quality bar",
                "--owner",
                "builder",
                "--verifier",
                "fresh-critic",
                "--bar",
                "--machine",
            )
            self.run_cli(
                "transition", *root_args, "--phase", "PLAN", "--next", "Plan the candidate"
            )
            self.run_cli(
                "transition",
                *root_args,
                "--phase",
                "IMPLEMENT",
                "--next",
                "Build the candidate",
            )
            self.run_cli(
                "transition", *root_args, "--phase", "VERIFY", "--next", "Freeze candidate"
            )
            bound = self.run_cli(
                "bind",
                *root_args,
                "--project",
                "cli-smoke",
                "--candidate",
                head,
                "--artifact",
                "artifact.txt",
            )
            self.assertEqual(bound["verification_binding"]["candidate_commit"], head)
            evidence = self.run_cli(
                "run-evidence",
                *root_args,
                "--gate",
                "SMOKE",
                "--actor",
                "verifier",
                "--command",
                f'"{sys.executable}" "{script}"',
                "--project",
                "cli-smoke",
                "--candidate",
                head,
                "--artifact",
                "artifact.txt",
            )
            self.assertTrue(evidence["integrity_stable"])
            bar = self.run_cli(
                "run-evidence",
                *root_args,
                "--gate",
                "BAR",
                "--actor",
                "fresh-critic",
                "--command",
                f'"{sys.executable}" "{script}"',
                "--project",
                "cli-smoke",
                "--candidate",
                head,
                "--artifact",
                "artifact.txt",
            )
            self.assertTrue(bar["integrity_stable"])
            self.assertEqual(self.run_cli("finalize", *root_args)["status"], "VERIFIED")
            self.assertTrue(self.run_cli("validate", *root_args, "--require-final")["ok"])

    def test_help_exposes_integrity_commands(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(CLI), "--help"],
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("bind", completed.stdout)
        self.assertIn("run-evidence", completed.stdout)
        self.assertIn("add-gate", completed.stdout)


if __name__ == "__main__":
    unittest.main()
