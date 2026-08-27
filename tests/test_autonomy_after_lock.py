from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "skills" / "loopseed" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from one_shotted_core import OneShottedError, initialize, transition  # noqa: E402


class AutonomyAfterLockTests(unittest.TestCase):
    def make_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        (root / ".git").mkdir()
        return temporary, root

    def test_routine_human_visual_approval_cannot_block_production(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "Prepare a verified migration report")
            with self.assertRaisesRegex(OneShottedError, "Routine human approval"):
                transition(
                    root,
                    blocked_reason="Await human visual approval of the current screenshots",
                    unblock_condition="User approves the visual result",
                )

    def test_chinese_routine_user_confirmation_cannot_block_production(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "Prepare a verified migration report")
            with self.assertRaisesRegex(OneShottedError, "Routine human approval"):
                transition(
                    root,
                    blocked_reason="等待用户验收当前视觉效果",
                    unblock_condition="用户确认截图可以继续",
                )

    def test_true_external_account_permission_blocker_remains_legal(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            initialize(root, "Prepare a verified migration report")
            result = transition(
                root,
                blocked_reason="Missing account permission for the external service",
                unblock_condition="Owner grants the required account permission",
            )
            self.assertEqual(result["status"], "BLOCKED")
            self.assertEqual(
                result["true_blocker"]["reason"],
                "Missing account permission for the external service",
            )


if __name__ == "__main__":
    unittest.main()
