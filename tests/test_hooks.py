from __future__ import annotations

import json
import os
import shutil
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
                "loopseed_version": "0.8.1",
                "run_id": "RUN-old",
                "status": status,
                "phase": phase,
                "next_action": next_action,
            }
        ),
        encoding="utf-8",
    )


def write_vision(
    root: Path, status: str = "ACTIVE", *, after: str = "", deadline: str | None = None
) -> None:
    (root / ".git").mkdir(exist_ok=True)
    fields = ["version=0.9.0", "mode=vision", f"status={status}"]
    if after:
        fields.append(f"after_one_shotted={after}")
    if deadline is not None:
        fields.append(f"deadline_utc={deadline}")
    (root / ".loopseed.md").write_text(
        "\n".join(["# Saved vision", "```loopseed-state", *fields, "```", "Players replayed the first voyage."]),
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
    def test_manifest_commands_launch_from_an_installed_path_with_spaces(self) -> None:
        with tempfile.TemporaryDirectory(prefix="loopseed hook ") as tmp:
            installed = Path(tmp) / "installed plugin"
            project = Path(tmp) / "game"
            project.mkdir()
            shutil.copytree(HOOKS, installed / "hooks")
            shutil.copytree(REPO_ROOT / "skills", installed / "skills")
            manifest = json.loads((installed / "hooks/hooks.json").read_text(encoding="utf-8"))
            env = {**os.environ, "PLUGIN_ROOT": str(installed)}
            if os.name == "nt":
                shell = [shutil.which("pwsh") or "powershell.exe", "-NoProfile", "-Command"]
                command_key = "commandWindows"
            else:
                shell = ["/bin/sh", "-c"]
                command_key = "command"

            write_vision(project)
            for event in ("SessionStart", "Stop"):
                if event == "Stop":
                    write_one_shotted(project, phase="REPAIR")
                command = manifest["hooks"][event][0]["hooks"][0][command_key]
                result = subprocess.run(
                    [*shell, command], cwd=project, env=env, check=True, capture_output=True,
                    input=json.dumps({"cwd": str(project), "source": "startup"}), text=True,
                )
                output = json.loads(result.stdout)
                if event == "SessionStart":
                    self.assertIn(".loopseed.md", output["hookSpecificOutput"]["additionalContext"])
                else:
                    self.assertIn("REPAIR", output["reason"])

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

    def test_saved_vision_resumes_in_a_new_session_and_leaves_stop_to_the_host(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_vision(root)
            nested = root / "src"
            nested.mkdir()
            for source in ("startup", "resume", "compact"):
                context = run_hook("session_start.py", nested, session_id="new-session", source=source)
                self.assertIn(".loopseed.md", context["hookSpecificOutput"]["additionalContext"])
            self.assertIsNone(run_hook("stop_continue.py", nested, session_id="bounded-task"))

    def test_named_terminal_strict_run_allows_a_new_vision(self) -> None:
        for status in ("VERIFIED", "ABORTED", "BLOCKED"):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                write_one_shotted(root, status, "FINALIZE")
                write_vision(root, after="RUN-old")
                context = run_hook("session_start.py", root)
                self.assertIn(".loopseed.md", context["hookSpecificOutput"]["additionalContext"])
                self.assertIsNone(run_hook("stop_continue.py", root))

    def test_active_strict_run_owns_recovery_even_when_a_vision_names_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_one_shotted(root, phase="REPAIR")
            write_vision(root, after="RUN-old")
            context = run_hook("session_start.py", root)["hookSpecificOutput"]["additionalContext"]
            self.assertIn("One-Shotted", context)
            self.assertIn("REPAIR", run_hook("stop_continue.py", root)["reason"])

    def test_terminal_strict_run_does_not_wake_an_older_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_one_shotted(root, "VERIFIED")
            for after in ("", "RUN-unrelated"):
                write_vision(root, after=after)
                self.assertIsNone(run_hook("session_start.py", root))
            write_legacy(root, "ACTIVE")
            self.assertIsNone(run_hook("stop_continue.py", root))

    def test_unreadable_strict_state_cannot_be_claimed_by_a_vision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_one_shotted(root)
            write_vision(root, after="RUN-old")
            (root / ".loopseed/one-shotted/state.json").write_text("{", encoding="utf-8")
            self.assertIsNone(run_hook("session_start.py", root))

    def test_stopped_or_spent_vision_stays_dormant(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for status in ("ABORTED", "BLOCKED"):
                write_vision(root, status)
                self.assertIsNone(run_hook("session_start.py", root))
                self.assertIsNone(run_hook("stop_continue.py", root))
            for deadline in ("2001-01-01T00:00:00Z", "2099-01-01T00:00:00", "invalid", ""):
                write_vision(root, deadline=deadline)
                self.assertIsNone(run_hook("session_start.py", root))
            write_vision(root, deadline="2099-01-01T00:00:00+00:00")
            self.assertIsNotNone(run_hook("session_start.py", root))

    def test_no_state_is_noop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            self.assertIsNone(run_hook("stop_continue.py", root, stop_hook_active=False))
            self.assertIsNone(run_hook("session_start.py", root, source="startup"))


if __name__ == "__main__":
    unittest.main()
