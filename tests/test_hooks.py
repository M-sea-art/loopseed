from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HOOKS = REPO_ROOT / "hooks"


def write_legacy(root: Path, status: str, next_action: str = "Run the verifier") -> None:
    (root / ".git").mkdir(exist_ok=True)
    (root / ".loopseed.md").write_text(
        "\n".join(
            [
                "# LoopSeed State",
                "",
                "```loopseed-state",
                "version=0.3.0",
                f"status={status}",
                f"next={next_action}",
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_one_shotted(
    root: Path,
    status: str = "ACTIVE",
    phase: str = "VERIFY",
    next_action: str = "Run gate FLOW",
) -> None:
    (root / ".git").mkdir(exist_ok=True)
    target = root / ".loopseed" / "one-shotted"
    target.mkdir(parents=True, exist_ok=True)
    (target / "state.json").write_text(
        json.dumps(
            {
                "mode": "one-shotted",
                "status": status,
                "phase": phase,
                "next_action": next_action,
            }
        ),
        encoding="utf-8",
    )


def run_hook(name: str, cwd: Path, **extra: object) -> dict[str, object] | None:
    event = {
        "session_id": "test-session",
        "cwd": str(cwd),
        "hook_event_name": name,
        **extra,
    }
    result = subprocess.run(
        [sys.executable, str(HOOKS / name)],
        input=json.dumps(event),
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout) if result.stdout.strip() else None


class HookTests(unittest.TestCase):
    def test_legacy_active_requests_one_continuation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_legacy(root, "ACTIVE", "Capture a screenshot")
            output = run_hook("stop_continue.py", root, stop_hook_active=False)
            self.assertEqual(output["decision"], "block")
            self.assertIn("Capture a screenshot", output["reason"])

    def test_stop_does_not_recurse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_legacy(root, "ACTIVE")
            self.assertIsNone(run_hook("stop_continue.py", root, stop_hook_active=True))

    def test_legacy_terminal_states_allow_stop(self) -> None:
        for status in ("VERIFIED", "BLOCKED", "ABORTED"):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                write_legacy(root, status)
                self.assertIsNone(run_hook("stop_continue.py", root, stop_hook_active=False))

    def test_one_shotted_takes_precedence_over_legacy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_legacy(root, "VERIFIED")
            write_one_shotted(root, "ACTIVE", "REPAIR", "Repair gate VISUAL")
            output = run_hook("stop_continue.py", root, stop_hook_active=False)
            self.assertEqual(output["decision"], "block")
            self.assertIn("One-Shotted", output["reason"])
            self.assertIn("REPAIR", output["reason"])

    def test_one_shotted_session_start_names_phase(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_one_shotted(root, "ACTIVE", "IMPLEMENT", "Build the primary flow")
            output = run_hook("session_start.py", root, source="resume")
            context = output["hookSpecificOutput"]["additionalContext"]
            self.assertIn("IMPLEMENT", context)
            self.assertIn("Build the primary flow", context)
            self.assertIn("independent verifier", context)
            self.assertIn("runnable tasks before waiting", context)

    def test_one_shotted_terminal_allows_stop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_one_shotted(root, "VERIFIED", "FINALIZE")
            self.assertIsNone(run_hook("stop_continue.py", root, stop_hook_active=False))

    def test_no_state_is_noop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            self.assertIsNone(run_hook("stop_continue.py", root, stop_hook_active=False))
            self.assertIsNone(run_hook("session_start.py", root, source="startup"))


if __name__ == "__main__":
    unittest.main()
