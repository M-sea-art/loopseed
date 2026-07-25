from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HOOKS = REPO_ROOT / "hooks"


def write_state(root: Path, status: str, next_action: str = "Run the verifier") -> None:
    (root / ".git").mkdir(exist_ok=True)
    (root / ".loopseed.md").write_text(
        "\n".join(
            [
                "# LoopSeed State",
                "",
                "```loopseed-state",
                "version=0.2.0",
                f"status={status}",
                f"next={next_action}",
                "```",
                "",
            ]
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
    if not result.stdout.strip():
        return None
    return json.loads(result.stdout)


class HookTests(unittest.TestCase):
    def test_stop_blocks_once_for_active_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_state(root, "ACTIVE", "Capture a real screenshot")
            output = run_hook(
                "stop_continue.py",
                root,
                stop_hook_active=False,
                last_assistant_message="done",
            )
            self.assertEqual(output["decision"], "block")
            self.assertIn("Capture a real screenshot", output["reason"])

    def test_stop_does_not_recurse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_state(root, "ACTIVE")
            output = run_hook("stop_continue.py", root, stop_hook_active=True)
            self.assertIsNone(output)

    def test_terminal_states_allow_stop(self) -> None:
        for status in ("VERIFIED", "BLOCKED", "ABORTED"):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                write_state(root, status)
                output = run_hook("stop_continue.py", root, stop_hook_active=False)
                self.assertIsNone(output)

    def test_session_start_injects_active_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_state(root, "ACTIVE", "Run the full user flow")
            output = run_hook("session_start.py", root, source="resume")
            context = output["hookSpecificOutput"]["additionalContext"]
            self.assertIn("ACTIVE", context)
            self.assertIn("Run the full user flow", context)

    def test_no_state_is_noop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            self.assertIsNone(
                run_hook("stop_continue.py", root, stop_hook_active=False)
            )
            self.assertIsNone(run_hook("session_start.py", root, source="startup"))


if __name__ == "__main__":
    unittest.main()
