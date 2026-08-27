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
    initialize,
    lock_project_context,
    status,
    transition,
)


class ContextShellV08Tests(unittest.TestCase):
    def make_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        return temporary, root

    def test_direct_path_still_requires_existing_planning_recovery(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            (root / "README.md").write_text(
                "# Existing product\nPreserve the current public API and continue the existing plan.\n",
                encoding="utf-8",
            )
            result = initialize(
                root,
                "Add the next verified feature",
                dialogue="off",
            )
            self.assertEqual(result["phase"], "BIND")
            self.assertEqual(result["calibration_status"], "SKIPPED")
            self.assertEqual(result["context_recovery_status"], "PENDING")
            self.assertIn("README.md", result["context_candidate_paths"])

            with self.assertRaisesRegex(OneShottedError, "context recovery is not locked"):
                add_gate(
                    root,
                    "FLOW",
                    "Complete flow",
                    "The existing flow remains complete",
                    "lead",
                    "verifier",
                )
            with self.assertRaisesRegex(OneShottedError, "context recovery is not locked"):
                transition(root, phase="PLAN", next_action="Plan new work")

            locked = lock_project_context(
                root,
                {
                    "planning_status": "FOUND",
                    "searched_locations": ["README.md"],
                    "sources": [
                        {
                            "locator": "README.md",
                            "role": "Existing product plan",
                            "authority": "NAMED_PROJECT_PLAN",
                        }
                    ],
                    "inherited_decisions": ["Preserve the current public API"],
                    "open_decisions": ["How to implement the next feature"],
                    "unresolved_conflicts": [],
                    "summary": "Continue the existing product and preserve its public API.",
                },
            )
            self.assertEqual(locked["context_status"], "LOCKED")
            current = status(root)
            self.assertTrue(current["ok"])

            gate = add_gate(
                root,
                "FLOW",
                "Complete flow",
                "The existing flow remains complete",
                "lead",
                "verifier",
            )
            self.assertEqual(gate["role"], "hard")
            moved = transition(root, phase="PLAN", next_action="Plan bounded work")
            self.assertEqual(moved["phase"], "PLAN")

    def test_direct_existing_project_without_planning_source_gets_none_found_receipt(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            (root / "artifact.bin").write_bytes(b"existing candidate")
            result = initialize(root, "Improve the existing artifact", dialogue="off")
            self.assertEqual(result["context_recovery_status"], "LOCKED")
            context = json.loads(
                (root / ".loopseed/one-shotted/project-context.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(context["planning_status"], "NONE_FOUND")
            gate = add_gate(
                root,
                "FLOW",
                "Complete flow",
                "The artifact remains usable",
                "lead",
                "verifier",
            )
            self.assertEqual(gate["status"], "PENDING")


if __name__ == "__main__":
    unittest.main()
