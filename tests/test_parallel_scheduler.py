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
    add_task,
    declare_wait,
    initialize,
    schedule_tasks,
    set_task_status,
    transition,
    validate,
)


class ParallelSchedulerTests(unittest.TestCase):
    def make_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        (root / ".git").mkdir()
        initialize(root, "Build a verified product slice")
        transition(root, phase="PLAN", next_action="Declare bounded tasks")
        return temporary, root

    def test_initialize_creates_task_graph(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            self.assertTrue((root / ".loopseed" / "one-shotted" / "task-graph.json").is_file())
            self.assertTrue(validate(root)["ok"])

    def test_pre_0_7_run_without_task_graph_remains_valid(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            target = root / ".loopseed" / "one-shotted"
            (target / "task-graph.json").unlink()
            for name in ("goal-contract.json", "state.json"):
                path = target / name
                value = json.loads(path.read_text(encoding="utf-8"))
                value["loopseed_version"] = "0.5.0"
                value.pop("scheduler_wait", None)
                path.write_text(json.dumps(value), encoding="utf-8")
            self.assertTrue(validate(root)["ok"])

    def test_soft_advice_never_blocks_builder(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            add_task(root, "ARCH", "Review the technical route", "architect", read_only=True)
            set_task_status(root, "ARCH", "RUNNING", "architect", "Review started")
            add_task(
                root,
                "BUILD",
                "Build candidate A",
                "builder",
                relations=[("ARCH", "SOFT_ADVICE")],
                write_scope=["Assets"],
                isolation="worktree:a",
            )
            snapshot = schedule_tasks(root)
            self.assertEqual(snapshot["runnable_task_ids"], ["BUILD"])
            self.assertTrue(snapshot["wait_forbidden"])

    def test_hard_dependency_blocks_only_direct_consumer(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            add_task(root, "ARCH", "Resolve a required interface", "architect", read_only=True)
            set_task_status(root, "ARCH", "RUNNING", "architect", "Resolution started")
            add_task(
                root,
                "BUILD",
                "Implement the resolved interface",
                "builder",
                relations=[("ARCH", "HARD_DEPENDENCY")],
                write_scope=["src"],
            )
            add_task(root, "TESTS", "Prepare independent tests", "tester", read_only=True)
            snapshot = schedule_tasks(root)
            self.assertEqual(snapshot["runnable_task_ids"], ["TESTS"])
            self.assertEqual(snapshot["blocked_by"], {"BUILD": ["ARCH"]})

    def test_wait_is_rejected_while_safe_work_is_runnable(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            add_task(root, "ADVICE", "Review material direction", "director", read_only=True)
            set_task_status(root, "ADVICE", "RUNNING", "director", "Review started")
            add_task(
                root,
                "BUILD",
                "Build an isolated candidate",
                "builder",
                relations=[("ADVICE", "SOFT_ADVICE")],
                write_scope=["Assets"],
                isolation="worktree:candidate",
            )
            with self.assertRaisesRegex(OneShottedError, "NO_IDLE_WHILE_RUNNABLE"):
                declare_wait(root, ["ADVICE"], "JOIN", "continue with current evidence")

    def test_audit_rejects_a_tampered_wait_with_runnable_work(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            add_task(root, "ADVICE", "Review direction", "director", read_only=True)
            set_task_status(root, "ADVICE", "RUNNING", "director", "Review started")
            add_task(
                root,
                "BUILD",
                "Build candidate",
                "builder",
                relations=[("ADVICE", "SOFT_ADVICE")],
                write_scope=["src"],
                isolation="worktree:build",
            )
            state_path = root / ".loopseed" / "one-shotted" / "state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["scheduler_wait"] = {
                "task_ids": ["ADVICE"],
                "reason": "JOIN",
                "fallback": "continue with current evidence",
                "declared_at": "2026-08-01T00:00:00Z",
            }
            state_path.write_text(json.dumps(state), encoding="utf-8")
            report = validate(root)
            self.assertFalse(report["ok"])
            self.assertTrue(
                any("NO_IDLE_WHILE_RUNNABLE" in error for error in report["errors"])
            )

    def test_wait_is_allowed_at_a_real_hard_dependency_join(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            add_task(root, "API", "Resolve the required API shape", "architect", read_only=True)
            set_task_status(root, "API", "RUNNING", "architect", "API check started")
            add_task(
                root,
                "BUILD",
                "Implement against the confirmed API",
                "builder",
                relations=[("API", "HARD_DEPENDENCY")],
                write_scope=["src"],
            )
            result = declare_wait(root, ["API"], "HARD_DEPENDENCY", "use the documented fallback API")
            self.assertTrue(result["wait_allowed"])
            self.assertTrue(validate(root)["ok"])
            completed = set_task_status(root, "API", "SUCCEEDED", "architect", "API shape confirmed")
            self.assertEqual(completed["runnable_task_ids"], ["BUILD"])
            self.assertTrue(validate(root)["ok"])

    def test_shared_writers_serialize_but_worktrees_parallelize(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            add_task(root, "SHARED-A", "Edit shared scene A", "builder-a", write_scope=["Assets/Scene"])
            add_task(root, "SHARED-B", "Edit shared scene B", "builder-b", write_scope=["Assets/Scene"])
            shared = schedule_tasks(root)
            self.assertEqual(shared["runnable_task_ids"], ["SHARED-A"])
            self.assertEqual(shared["held_task_ids"]["SHARED-B"], "write_conflict:SHARED-A")

        temporary, root = self.make_root()
        with temporary:
            add_task(
                root,
                "TREE-A",
                "Build candidate A",
                "builder-a",
                write_scope=["Assets/Scene"],
                isolation="worktree:a",
            )
            add_task(
                root,
                "TREE-B",
                "Build candidate B",
                "builder-b",
                write_scope=["Assets/Scene"],
                isolation="worktree:b",
            )
            isolated = schedule_tasks(root)
            self.assertEqual(isolated["runnable_task_ids"], ["TREE-A", "TREE-B"])

    def test_first_success_releases_consumer_without_waiting_for_all(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            add_task(
                root,
                "CANDIDATE-A",
                "Build route A",
                "builder-a",
                write_scope=["src"],
                isolation="worktree:a",
            )
            add_task(
                root,
                "CANDIDATE-B",
                "Build route B",
                "builder-b",
                write_scope=["src"],
                isolation="worktree:b",
            )
            add_task(
                root,
                "MERGE",
                "Integrate the first acceptable route",
                "lead",
                relations=[
                    ("CANDIDATE-A", "HARD_DEPENDENCY"),
                    ("CANDIDATE-B", "HARD_DEPENDENCY"),
                ],
                join_strategy="FIRST_SUCCESS",
                write_scope=["src"],
            )
            set_task_status(root, "CANDIDATE-A", "RUNNING", "builder-a", "Route A started")
            set_task_status(root, "CANDIDATE-B", "RUNNING", "builder-b", "Route B started")
            result = set_task_status(root, "CANDIDATE-A", "SUCCEEDED", "builder-a", "Route A passed")
            self.assertEqual(result["runnable_task_ids"], ["MERGE"])
            self.assertEqual(result["cancellation_candidate_task_ids"], ["CANDIDATE-B"])
            with self.assertRaisesRegex(OneShottedError, "NO_IDLE_WHILE_RUNNABLE"):
                declare_wait(root, ["CANDIDATE-B"], "JOIN", "use route A")

    def test_capacity_returns_maximum_safe_batch(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            for task_id in ("SCAN-A", "SCAN-B", "SCAN-C"):
                add_task(root, task_id, f"Run {task_id}", task_id.lower(), read_only=True)
            snapshot = schedule_tasks(root, capacity=2)
            self.assertEqual(snapshot["runnable_task_ids"], ["SCAN-A", "SCAN-B"])
            self.assertEqual(snapshot["held_task_ids"], {"SCAN-C": "concurrency_capacity"})

    def test_multiple_hard_dependencies_require_an_explicit_join(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            add_task(root, "A", "Build A", "a", read_only=True)
            add_task(root, "B", "Build B", "b", read_only=True)
            with self.assertRaisesRegex(OneShottedError, "explicitly choose"):
                add_task(
                    root,
                    "MERGE",
                    "Merge routes",
                    "lead",
                    relations=[("A", "HARD_DEPENDENCY"), ("B", "HARD_DEPENDENCY")],
                    read_only=True,
                )

    def test_global_blocked_is_rejected_while_internal_work_remains(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            add_task(root, "BUILD", "Build the product", "lead", write_scope=["src"])
            with self.assertRaisesRegex(OneShottedError, "internal work remains"):
                transition(
                    root,
                    blocked_reason="Waiting for an internal review",
                    unblock_condition="The reviewer responds",
                )

    def test_task_blocked_requires_an_unblock_condition(self) -> None:
        temporary, root = self.make_root()
        with temporary:
            add_task(root, "DEPLOY", "Deploy the product", "lead", write_scope=["deploy"])
            with self.assertRaisesRegex(OneShottedError, "requires an unblock"):
                set_task_status(root, "DEPLOY", "BLOCKED", "lead", "Credentials are unavailable")
            result = set_task_status(
                root,
                "DEPLOY",
                "BLOCKED",
                "lead",
                "Credentials are unavailable",
                unblock_condition="The owner supplies scoped credentials",
            )
            self.assertEqual(result["task_status"], "BLOCKED")
            self.assertTrue(validate(root)["ok"])


if __name__ == "__main__":
    unittest.main()
