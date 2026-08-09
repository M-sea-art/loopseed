from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "skills" / "loopseed" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from one_shotted_core import (  # noqa: E402
    OneShottedError,
    add_gate,
    add_task,
    bind_project,
    finalize,
    initialize,
    record_gate_result,
    run_evidence,
    set_task_required,
    set_task_status,
    transition,
    validate,
)


class IntegrityBridgeAdversarialTests(unittest.TestCase):
    def git(self, root: Path, *args: str) -> str:
        return subprocess.run(
            ["git", *args],
            cwd=root,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()

    def make_repo(self) -> tuple[tempfile.TemporaryDirectory[str], Path, str, str]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        self.git(root, "init", "-q")
        self.git(root, "config", "user.email", "test@example.invalid")
        self.git(root, "config", "user.name", "LoopSeed Test")
        (root / "artifact.txt").write_text("candidate-v1\n", encoding="utf-8")
        script = root / "verify.py"
        script.write_text("print('verified')\n", encoding="utf-8")
        self.git(root, "add", "artifact.txt", "verify.py")
        self.git(root, "commit", "-qm", "candidate one")
        head = self.git(root, "rev-parse", "HEAD")
        command = f'"{sys.executable}" "{script}"'
        return temporary, root, head, command

    def prepare(
        self,
        *,
        machine: bool = True,
        task_status: str | None = None,
        optional_cancelled: bool = False,
    ) -> tuple[tempfile.TemporaryDirectory[str], Path, str, str]:
        temporary, root, head, command = self.make_repo()
        initialize(root, "Verify a frozen product candidate")
        add_gate(
            root,
            "PRIMARY",
            "Primary gate",
            "The real verifier command succeeds against the frozen artifact",
            "builder",
            "verifier",
            requires_machine_evidence=machine,
        )
        transition(root, phase="PLAN", next_action="Declare bounded work")
        if task_status is not None:
            add_task(root, "BUILD", "Build the candidate", "builder", write_scope=["src"])
            if task_status in {"RUNNING", "FAILED", "SUCCEEDED"}:
                set_task_status(root, "BUILD", "RUNNING", "builder", "Build started")
            if task_status == "SUCCEEDED":
                set_task_status(root, "BUILD", "SUCCEEDED", "builder", "Build completed")
            elif task_status == "FAILED":
                set_task_status(root, "BUILD", "FAILED", "builder", "Build failed")
            elif task_status == "BLOCKED":
                set_task_status(
                    root,
                    "BUILD",
                    "BLOCKED",
                    "builder",
                    "Dependency unavailable",
                    unblock_condition="Dependency returns",
                )
            elif task_status == "CANCELLED":
                set_task_status(root, "BUILD", "CANCELLED", "builder", "Build cancelled")
        if optional_cancelled:
            add_task(
                root,
                "CANDIDATE-B",
                "Build an optional losing candidate",
                "builder-b",
                write_scope=["candidate-b"],
                required=False,
            )
            set_task_status(
                root,
                "CANDIDATE-B",
                "CANCELLED",
                "builder-b",
                "Another candidate won",
            )
        transition(root, phase="IMPLEMENT", next_action="Build the candidate")
        transition(root, phase="VERIFY", next_action="Freeze the verification subject")
        bind_project(root, "demo-project", head, "artifact.txt")
        return temporary, root, head, command

    def pass_machine(self, root: Path, head: str, command: str) -> dict[str, object]:
        return run_evidence(
            root,
            "PRIMARY",
            "verifier",
            command,
            "demo-project",
            head,
            "artifact.txt",
        )

    def test_machine_gate_rejects_summary_only_or_artifact_only_pass(self) -> None:
        temporary, root, _, _ = self.prepare(machine=True)
        with temporary:
            with self.assertRaisesRegex(OneShottedError, "hashed artifact"):
                record_gate_result(root, "PRIMARY", "PASS", "verifier", "Trust me")
            record_gate_result(
                root,
                "PRIMARY",
                "PASS",
                "verifier",
                "I inspected the artifact",
                artifacts=["artifact.txt"],
            )
            report = validate(root)
            self.assertFalse(report["ok"])
            self.assertTrue(
                any("requires machine-executed" in error for error in report["errors"])
            )
            with self.assertRaises(OneShottedError):
                finalize(root)
            self.assertFalse((root / ".loopseed/one-shotted/final-report.json").exists())

    def test_record_rejects_command_claim_and_missing_artifact(self) -> None:
        temporary, root, _, _ = self.prepare(machine=False)
        with temporary:
            with self.assertRaisesRegex(OneShottedError, "does not execute commands"):
                record_gate_result(
                    root,
                    "PRIMARY",
                    "PASS",
                    "verifier",
                    "Claimed execution",
                    commands=["false"],
                    artifacts=["artifact.txt"],
                )
            with self.assertRaisesRegex(OneShottedError, "does not exist"):
                record_gate_result(
                    root,
                    "PRIMARY",
                    "PASS",
                    "verifier",
                    "Missing screenshot",
                    artifacts=["missing.png"],
                )

    def test_machine_runner_records_failure_and_timeout_as_fail(self) -> None:
        for command, timeout, expected_code in (
            (f'"{sys.executable}" -c "raise SystemExit(1)"', 120, 1),
            (f'"{sys.executable}" -c "import time; time.sleep(2)"', 1, 124),
        ):
            with self.subTest(expected_code=expected_code):
                temporary, root, head, _ = self.prepare(machine=True)
                with temporary:
                    result = run_evidence(
                        root,
                        "PRIMARY",
                        "verifier",
                        command,
                        "demo-project",
                        head,
                        "artifact.txt",
                        timeout_seconds=timeout,
                    )
                    self.assertFalse(result["ok"])
                    self.assertEqual(result["result"], "FAIL")
                    self.assertEqual(result["exit_code"], expected_code)
                    with self.assertRaises(OneShottedError):
                        finalize(root)

    def test_binding_rejects_missing_control_or_external_artifact(self) -> None:
        temporary, root, head, _ = self.make_repo()
        with temporary, tempfile.TemporaryDirectory() as other:
            initialize(root, "Reject invalid verification subjects")
            transition(root, phase="PLAN", next_action="Plan")
            transition(root, phase="IMPLEMENT", next_action="Build")
            transition(root, phase="VERIFY", next_action="Bind")
            with self.assertRaisesRegex(OneShottedError, "does not exist"):
                bind_project(root, "demo-project", head, "missing.bin")
            with self.assertRaisesRegex(OneShottedError, "control data"):
                bind_project(root, "demo-project", head, ".loopseed")
            external = Path(other) / "outside.bin"
            external.write_text("outside\n", encoding="utf-8")
            with self.assertRaisesRegex(OneShottedError, "within the project root"):
                bind_project(root, "demo-project", head, str(external))

    def test_runner_rejects_actual_git_head_mismatch(self) -> None:
        temporary, root, head, command = self.prepare(machine=True)
        with temporary:
            (root / "next.txt").write_text("next\n", encoding="utf-8")
            self.git(root, "add", "next.txt")
            self.git(root, "commit", "-qm", "candidate two")
            with self.assertRaisesRegex(OneShottedError, "Actual Git HEAD"):
                self.pass_machine(root, head, command)

    def test_verifier_mutation_and_post_pass_drift_are_rejected(self) -> None:
        temporary, root, head, _ = self.prepare(machine=True)
        with temporary:
            mutator = (
                f'"{sys.executable}" -c "from pathlib import Path; '
                "Path('artifact.txt').write_text('mutated\\n')\""
            )
            result = self.pass_machine(root, head, mutator)
            self.assertEqual(result["result"], "FAIL")
            self.assertEqual(
                result["integrity_failure_reason"], "ARTIFACT_MUTATED_DURING_VERIFICATION"
            )

        temporary, root, head, command = self.prepare(machine=True)
        with temporary:
            self.assertTrue(self.pass_machine(root, head, command)["ok"])
            (root / "artifact.txt").write_text("candidate-v2\n", encoding="utf-8")
            report = validate(root)
            self.assertFalse(report["ok"])
            self.assertTrue(any("Artifact drift" in error for error in report["errors"]))
            with self.assertRaises(OneShottedError):
                finalize(root)

    def test_audit_rejects_forged_evidence_fields(self) -> None:
        mutations = {
            "run_id": "RUN-forged",
            "actor": "forger",
            "producer": "forged.runner",
            "timed_out": True,
            "binding_id": "BIND-forged",
            "gate_id": "UNKNOWN",
            "actual_candidate_commit": "0" * 40,
        }
        for field, value in mutations.items():
            with self.subTest(field=field):
                temporary, root, head, command = self.prepare(machine=True)
                with temporary:
                    self.pass_machine(root, head, command)
                    ledger = root / ".loopseed/one-shotted/evidence.jsonl"
                    item = json.loads(ledger.read_text(encoding="utf-8"))
                    item[field] = value
                    ledger.write_text(json.dumps(item) + "\n", encoding="utf-8")
                    self.assertFalse(validate(root)["ok"])
                    with self.assertRaises(OneShottedError):
                        finalize(root)

    def test_gate_cannot_reuse_an_older_pass_after_a_later_failure(self) -> None:
        temporary, root, head, command = self.prepare(machine=True)
        with temporary:
            self.assertTrue(self.pass_machine(root, head, command)["ok"])
            failed = run_evidence(
                root,
                "PRIMARY",
                "verifier",
                f'"{sys.executable}" -c "raise SystemExit(1)"',
                "demo-project",
                head,
                "artifact.txt",
            )
            self.assertEqual(failed["result"], "FAIL")
            path = root / ".loopseed/one-shotted/acceptance.json"
            acceptance = json.loads(path.read_text(encoding="utf-8"))
            acceptance["gates"][0]["status"] = "PASS"
            acceptance["gates"][0]["evidence_ids"] = acceptance["gates"][0][
                "evidence_ids"
            ][:1]
            path.write_text(json.dumps(acceptance), encoding="utf-8")
            report = validate(root)
            self.assertFalse(report["ok"])
            self.assertTrue(any("evidence ledger" in error for error in report["errors"]))

    def test_finalize_rejects_every_unsettled_required_task(self) -> None:
        for task_status in ("PENDING", "FAILED", "BLOCKED", "CANCELLED"):
            with self.subTest(task_status=task_status):
                temporary, root, head, command = self.prepare(
                    machine=True, task_status=task_status
                )
                with temporary:
                    self.assertTrue(self.pass_machine(root, head, command)["ok"])
                    with self.assertRaisesRegex(
                        OneShottedError, "Required tasks are not SUCCEEDED"
                    ):
                        finalize(root)

    def test_valid_machine_evidence_and_required_tasks_finalize(self) -> None:
        temporary, root, head, command = self.prepare(
            machine=True,
            task_status="SUCCEEDED",
            optional_cancelled=True,
        )
        with temporary:
            result = self.pass_machine(root, head, command)
            self.assertTrue(result["ok"])
            self.assertTrue(result["integrity_stable"])
            self.assertEqual(finalize(root)["status"], "VERIFIED")
            self.assertTrue(validate(root, require_final=True)["ok"])

    def test_repair_rebinds_new_generation_and_invalidates_old_gate(self) -> None:
        temporary, root, head, command = self.prepare(machine=True)
        with temporary:
            self.assertTrue(self.pass_machine(root, head, command)["ok"])
            transition(root, phase="PLAN", next_action="Replan the repaired candidate")
            transition(root, phase="IMPLEMENT", next_action="Repair the candidate")
            (root / "artifact.txt").write_text("candidate-v2\n", encoding="utf-8")
            self.git(root, "add", "artifact.txt")
            self.git(root, "commit", "-qm", "candidate two")
            second_head = self.git(root, "rev-parse", "HEAD")
            transition(root, phase="VERIFY", next_action="Rebind the repaired candidate")
            rebound = bind_project(root, "demo-project", second_head, "artifact.txt")
            self.assertTrue(rebound["gates_reset"])
            acceptance = json.loads(
                (root / ".loopseed/one-shotted/acceptance.json").read_text(encoding="utf-8")
            )
            self.assertEqual(acceptance["gates"][0]["status"], "PENDING")
            self.assertEqual(acceptance["gates"][0]["evidence_ids"], [])
            self.assertTrue(self.pass_machine(root, second_head, command)["ok"])
            self.assertEqual(finalize(root)["status"], "VERIFIED")

    def test_validate_rejects_final_report_tampering(self) -> None:
        mutations = {
            "run_id": "RUN-forged",
            "verdict": "NOT_VERIFIED",
            "required_gates": [],
            "gate_evidence": {},
            "verification_binding": {},
            "required_tasks": ["FORGED"],
            "open_blocking_defects": ["P0-forged"],
            "finished_at": "2000-01-01T00:00:00Z",
        }
        temporary, root, head, command = self.prepare(machine=True)
        with temporary:
            self.pass_machine(root, head, command)
            finalize(root)
            path = root / ".loopseed/one-shotted/final-report.json"
            original = json.loads(path.read_text(encoding="utf-8"))
            for field, value in mutations.items():
                with self.subTest(field=field):
                    tampered = dict(original)
                    tampered[field] = value
                    path.write_text(json.dumps(tampered), encoding="utf-8")
                    self.assertFalse(validate(root, require_final=True)["ok"])
            path.write_text(json.dumps(original), encoding="utf-8")
            self.assertTrue(validate(root, require_final=True)["ok"])

    def test_binding_rejects_untracked_candidate_content_and_symlink_artifact(self) -> None:
        temporary, root, head, _ = self.make_repo()
        with temporary:
            initialize(root, "Reject unbound candidate inputs")
            add_gate(root, "PRIMARY", "Primary", "Verifier passes", "builder", "verifier")
            transition(root, phase="PLAN", next_action="Plan")
            transition(root, phase="IMPLEMENT", next_action="Build")
            transition(root, phase="VERIFY", next_action="Bind")
            helper = root / "helper.py"
            helper.write_text("ALLOW = True\n", encoding="utf-8")
            with self.assertRaisesRegex(OneShottedError, "untracked candidate content"):
                bind_project(root, "demo-project", head, "artifact.txt")
            helper.unlink()
            if hasattr(os, "symlink"):
                link = root / "artifact-link.txt"
                try:
                    link.symlink_to("artifact.txt")
                except OSError:
                    pass
                else:
                    with self.assertRaisesRegex(OneShottedError, "symlink"):
                        bind_project(root, "demo-project", head, "artifact-link.txt")

    def test_dirty_tracked_verifier_is_rejected_before_execution(self) -> None:
        temporary, root, head, command = self.prepare(machine=True)
        with temporary:
            (root / "verify.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
            with self.assertRaisesRegex(OneShottedError, "Tracked worktree"):
                self.pass_machine(root, head, command)
            (root / "verify.py").write_text("print('verified')\n", encoding="utf-8")
            self.assertTrue(self.pass_machine(root, head, command)["ok"])

    def test_negative_dirty_receipt_remains_valid_after_repair(self) -> None:
        temporary, root, head, _ = self.prepare(machine=True)
        with temporary:
            command = (
                f'"{sys.executable}" -c "from pathlib import Path; '
                "Path('verify.py').write_text('changed\\n')\""
            )
            result = self.pass_machine(root, head, command)
            self.assertEqual(result["result"], "FAIL")
            self.assertEqual(
                result["integrity_failure_reason"],
                "TRACKED_WORKTREE_CHANGED_DURING_VERIFICATION",
            )
            (root / "verify.py").write_text("print('verified')\n", encoding="utf-8")
            self.assertTrue(validate(root)["ok"])

    def test_untracked_output_is_a_valid_negative_receipt_after_cleanup(self) -> None:
        temporary, root, head, _ = self.prepare(machine=True)
        with temporary:
            command = (
                f'"{sys.executable}" -c "from pathlib import Path; '
                "Path('surprise.tmp').write_text('x')\""
            )
            result = self.pass_machine(root, head, command)
            self.assertEqual(result["result"], "FAIL")
            self.assertEqual(
                result["integrity_failure_reason"],
                "UNTRACKED_CONTENT_CHANGED_DURING_VERIFICATION",
            )
            (root / "surprise.tmp").unlink()
            self.assertTrue(validate(root)["ok"])

    def test_human_gate_can_supersede_a_stale_artifact_receipt(self) -> None:
        temporary, root, _, _ = self.prepare(machine=False)
        with temporary:
            old = root / "old.png"
            old.write_bytes(b"old")
            record_gate_result(
                root, "PRIMARY", "PASS", "verifier", "Old capture", artifacts=["old.png"]
            )
            old.unlink()
            new = root / "new.png"
            new.write_bytes(b"new")
            record_gate_result(
                root, "PRIMARY", "PASS", "verifier", "New capture", artifacts=["new.png"]
            )
            self.assertTrue(validate(root)["ok"])
            self.assertEqual(finalize(root)["status"], "VERIFIED")

    def test_first_binding_resets_legacy_unattested_pass(self) -> None:
        temporary, root, head, command = self.make_repo()
        with temporary:
            initialize(root, "Upgrade a v0.7 run safely")
            add_gate(
                root,
                "PRIMARY",
                "Primary",
                "Verifier passes",
                "builder",
                "verifier",
                requires_machine_evidence=True,
            )
            target = root / ".loopseed/one-shotted"
            for name in ("goal-contract.json", "state.json", "task-graph.json"):
                path = target / name
                item = json.loads(path.read_text(encoding="utf-8"))
                item["loopseed_version"] = "0.7.0"
                path.write_text(json.dumps(item), encoding="utf-8")
            legacy_id = "EV-legacy"
            legacy = {
                "id": legacy_id,
                "run_id": json.loads(
                    (target / "goal-contract.json").read_text(encoding="utf-8")
                )["run_id"],
                "gate_id": "PRIMARY",
                "result": "PASS",
                "actor": "verifier",
                "summary": "Claimed command",
                "commands": ["false"],
                "artifacts": [],
                "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            (target / "evidence.jsonl").write_text(json.dumps(legacy) + "\n", encoding="utf-8")
            acceptance_path = target / "acceptance.json"
            acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
            acceptance["gates"][0].pop("requires_machine_evidence", None)
            acceptance["gates"][0].update(
                {"status": "PASS", "evidence_ids": [legacy_id]}
            )
            acceptance_path.write_text(json.dumps(acceptance), encoding="utf-8")
            transition(root, phase="PLAN", next_action="Plan")
            transition(root, phase="IMPLEMENT", next_action="Build")
            transition(root, phase="VERIFY", next_action="Bind")
            bound = bind_project(root, "demo-project", head, "artifact.txt")
            self.assertTrue(bound["gates_reset"])
            acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
            self.assertEqual(acceptance["gates"][0]["status"], "PENDING")
            self.assertEqual(acceptance["gates"][0]["evidence_ids"], [])
            self.assertTrue(acceptance["gates"][0]["requires_machine_evidence"])
            self.assertTrue(self.pass_machine(root, head, command)["ok"])
            self.assertEqual(finalize(root)["status"], "VERIFIED")

    def test_first_binding_normalizes_a_legacy_pending_gate(self) -> None:
        temporary, root, head, _ = self.make_repo()
        with temporary:
            initialize(root, "Normalize a pending v0.7 gate")
            add_gate(root, "PRIMARY", "Primary", "Visual check", "builder", "verifier")
            acceptance_path = root / ".loopseed/one-shotted/acceptance.json"
            acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
            acceptance["schema_version"] = "1.0"
            acceptance["policy"].pop("pass_requires_machine_or_hashed_artifact", None)
            acceptance["gates"][0].pop("requires_machine_evidence", None)
            acceptance_path.write_text(json.dumps(acceptance), encoding="utf-8")
            transition(root, phase="PLAN", next_action="Plan")
            transition(root, phase="IMPLEMENT", next_action="Build")
            transition(root, phase="VERIFY", next_action="Bind")
            result = bind_project(root, "demo-project", head, "artifact.txt")
            self.assertFalse(result["gates_reset"])
            self.assertTrue(result["acceptance_normalized"])
            acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
            self.assertEqual(acceptance["schema_version"], "1.2")
            self.assertIs(acceptance["gates"][0]["requires_machine_evidence"], False)

    def test_parallel_gate_receipts_merge_without_lost_updates(self) -> None:
        temporary, root, head, command = self.make_repo()
        with temporary:
            initialize(root, "Verify two independent gates")
            for gate_id in ("ONE", "TWO"):
                add_gate(
                    root,
                    gate_id,
                    gate_id,
                    "Verifier passes",
                    "builder",
                    f"verifier-{gate_id.lower()}",
                    requires_machine_evidence=True,
                )
            transition(root, phase="PLAN", next_action="Plan")
            transition(root, phase="IMPLEMENT", next_action="Build")
            transition(root, phase="VERIFY", next_action="Bind")
            bind_project(root, "demo-project", head, "artifact.txt")
            before_round = json.loads(
                (root / ".loopseed/one-shotted/state.json").read_text(encoding="utf-8")
            )["round"]

            def verify(gate_id: str) -> dict[str, object]:
                return run_evidence(
                    root,
                    gate_id,
                    f"verifier-{gate_id.lower()}",
                    command,
                    "demo-project",
                    head,
                    "artifact.txt",
                )

            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(verify, ("ONE", "TWO")))
            self.assertTrue(all(item["ok"] for item in results))
            acceptance = json.loads(
                (root / ".loopseed/one-shotted/acceptance.json").read_text(encoding="utf-8")
            )
            self.assertEqual([gate["status"] for gate in acceptance["gates"]], ["PASS", "PASS"])
            state = json.loads(
                (root / ".loopseed/one-shotted/state.json").read_text(encoding="utf-8")
            )
            self.assertEqual(state["round"], before_round + 2)
            self.assertTrue(validate(root)["ok"])

    def test_retry_resynchronizes_a_prior_orphan_receipt(self) -> None:
        temporary, root, head, command = self.prepare(machine=True)
        with temporary:
            first = self.pass_machine(root, head, command)
            acceptance_path = root / ".loopseed/one-shotted/acceptance.json"
            acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
            acceptance["gates"][0].update({"status": "PENDING", "evidence_ids": []})
            acceptance_path.write_text(json.dumps(acceptance), encoding="utf-8")
            second = self.pass_machine(root, head, command)
            acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
            self.assertEqual(
                acceptance["gates"][0]["evidence_ids"],
                [first["evidence_id"], second["evidence_id"]],
            )
            self.assertTrue(validate(root)["ok"])

    def test_legacy_cancelled_task_can_be_explicitly_migrated_optional(self) -> None:
        temporary, root, head, command = self.prepare(machine=True, task_status="CANCELLED")
        with temporary:
            self.assertTrue(self.pass_machine(root, head, command)["ok"])
            set_task_required(
                root,
                "BUILD",
                False,
                "lead",
                "Legacy FIRST_SUCCESS loser is intentionally optional",
            )
            self.assertEqual(finalize(root)["status"], "VERIFIED")

    def test_optional_pending_task_and_non_boolean_gate_cannot_finalize(self) -> None:
        temporary, root, head, command = self.prepare(machine=True)
        with temporary:
            transition(root, phase="PLAN", next_action="Declare optional work")
            add_task(
                root,
                "OPTIONAL",
                "Optional candidate",
                "builder",
                write_scope=["optional"],
                required=False,
            )
            transition(root, phase="IMPLEMENT", next_action="Resume")
            transition(root, phase="VERIFY", next_action="Verify")
            self.assertTrue(self.pass_machine(root, head, command)["ok"])
            with self.assertRaisesRegex(OneShottedError, "terminal disposition"):
                finalize(root)
            set_task_status(root, "OPTIONAL", "RUNNING", "builder", "Try candidate")
            set_task_status(root, "OPTIONAL", "FAILED", "builder", "Candidate failed")
            with self.assertRaisesRegex(OneShottedError, "terminal disposition"):
                finalize(root)
            set_task_status(root, "OPTIONAL", "CANCELLED", "builder", "Discard candidate")
            self.assertEqual(finalize(root)["status"], "VERIFIED")

        temporary, root, head, command = self.prepare(machine=True)
        with temporary:
            self.assertTrue(self.pass_machine(root, head, command)["ok"])
            path = root / ".loopseed/one-shotted/acceptance.json"
            acceptance = json.loads(path.read_text(encoding="utf-8"))
            acceptance["gates"][0]["required"] = 0
            path.write_text(json.dumps(acceptance), encoding="utf-8")
            self.assertFalse(validate(root)["ok"])
            with self.assertRaises(OneShottedError):
                finalize(root)

    def test_command_preserves_quoted_repeated_spaces(self) -> None:
        temporary, root, _, _ = self.make_repo()
        with temporary:
            script = root / "verify-spaces.py"
            script.write_text(
                "import sys\nraise SystemExit(0 if sys.argv[1] == 'a  b' else 9)\n",
                encoding="utf-8",
            )
            self.git(root, "add", "verify-spaces.py")
            self.git(root, "commit", "-qm", "add whitespace verifier")
            head = self.git(root, "rev-parse", "HEAD")
            initialize(root, "Preserve verifier command bytes")
            add_gate(
                root,
                "PRIMARY",
                "Primary",
                "Quoted argument is preserved",
                "builder",
                "verifier",
                requires_machine_evidence=True,
            )
            transition(root, phase="PLAN", next_action="Plan")
            transition(root, phase="IMPLEMENT", next_action="Build")
            transition(root, phase="VERIFY", next_action="Bind")
            bind_project(root, "demo-project", head, "artifact.txt")
            command = f'"{sys.executable}" "{script}" "a  b"'
            self.assertTrue(self.pass_machine(root, head, command)["ok"])
            entry = json.loads(
                (root / ".loopseed/one-shotted/evidence.jsonl").read_text(encoding="utf-8")
            )
            self.assertEqual(entry["command"], command)

    def test_late_gate_declaration_is_rejected(self) -> None:
        temporary, root, _, _ = self.prepare(machine=True)
        with temporary:
            with self.assertRaisesRegex(OneShottedError, "before implementation"):
                add_gate(root, "LATE", "Late", "Too late", "builder", "verifier-2")

    def test_failed_artifact_receipt_does_not_allowlist_untracked_source(self) -> None:
        temporary, root, head, command = self.make_repo()
        with temporary:
            initialize(root, "Reject a failed artifact allowlist")
            add_gate(
                root,
                "PRIMARY",
                "Primary",
                "Machine verifier passes",
                "builder",
                "machine-verifier",
                requires_machine_evidence=True,
            )
            add_gate(
                root,
                "OPTIONAL",
                "Optional visual",
                "Visual reference",
                "builder",
                "visual-verifier",
                required=False,
            )
            transition(root, phase="PLAN", next_action="Plan")
            transition(root, phase="IMPLEMENT", next_action="Build")
            transition(root, phase="VERIFY", next_action="Bind")
            bind_project(root, "demo-project", head, "artifact.txt")
            helper_dir = root / "helper-output"
            helper_dir.mkdir()
            (helper_dir / "helper.py").write_text("ALLOW = True\n", encoding="utf-8")
            record_gate_result(
                root,
                "OPTIONAL",
                "FAIL",
                "visual-verifier",
                "Rejected output",
                artifacts=["helper-output"],
            )
            with self.assertRaisesRegex(OneShottedError, "Untracked project content"):
                run_evidence(
                    root,
                    "PRIMARY",
                    "machine-verifier",
                    command,
                    "demo-project",
                    head,
                    "artifact.txt",
                )

    def test_machine_receipt_detects_human_evidence_artifact_mutation(self) -> None:
        temporary, root, head, _ = self.make_repo()
        with temporary:
            initialize(root, "Protect current human evidence during machine verification")
            add_gate(
                root,
                "PRIMARY",
                "Primary",
                "Machine verifier passes",
                "builder",
                "machine-verifier",
                requires_machine_evidence=True,
            )
            add_gate(
                root,
                "VISUAL",
                "Visual",
                "Capture remains stable",
                "builder",
                "visual-verifier",
                required=False,
            )
            transition(root, phase="PLAN", next_action="Plan")
            transition(root, phase="IMPLEMENT", next_action="Build")
            transition(root, phase="VERIFY", next_action="Bind")
            bind_project(root, "demo-project", head, "artifact.txt")
            capture = root / "capture.png"
            capture.write_bytes(b"capture")
            record_gate_result(
                root,
                "VISUAL",
                "PASS",
                "visual-verifier",
                "Stable capture",
                artifacts=["capture.png"],
            )
            command = (
                f'"{sys.executable}" -c "from pathlib import Path; '
                "Path('capture.png').write_bytes(b'changed')\""
            )
            result = run_evidence(
                root,
                "PRIMARY",
                "machine-verifier",
                command,
                "demo-project",
                head,
                "artifact.txt",
            )
            self.assertEqual(result["result"], "FAIL")
            self.assertEqual(
                result["integrity_failure_reason"],
                "EVIDENCE_ARTIFACT_MUTATED_DURING_VERIFICATION",
            )
            capture.write_bytes(b"capture")
            self.assertTrue(validate(root)["ok"])

    def test_same_binding_is_idempotent_with_current_untracked_artifact_evidence(self) -> None:
        temporary, root, head, _ = self.make_repo()
        with temporary:
            initialize(root, "Keep a current visual receipt across an idempotent bind")
            add_gate(
                root,
                "VISUAL",
                "Visual",
                "Capture remains stable",
                "builder",
                "visual-verifier",
            )
            transition(root, phase="PLAN", next_action="Plan")
            transition(root, phase="IMPLEMENT", next_action="Build")
            transition(root, phase="VERIFY", next_action="Bind")
            first = bind_project(root, "demo-project", head, "artifact.txt")
            capture = root / "capture.png"
            capture.write_bytes(b"capture")
            record_gate_result(
                root,
                "VISUAL",
                "PASS",
                "visual-verifier",
                "Stable capture",
                artifacts=["capture.png"],
            )
            self.assertTrue(validate(root)["ok"])
            second = bind_project(root, "demo-project", head, "artifact.txt")
            self.assertTrue(second["idempotent"])
            self.assertEqual(
                second["verification_binding"]["binding_id"],
                first["verification_binding"]["binding_id"],
            )
            self.assertTrue(validate(root)["ok"])

    def test_tracked_loopseed_control_data_is_excluded_from_candidate_dirtiness(self) -> None:
        temporary, root, _, command = self.make_repo()
        with temporary:
            initialize(root, "Allow durable tracked control state")
            add_gate(
                root,
                "PRIMARY",
                "Primary",
                "Verifier passes",
                "builder",
                "verifier",
                requires_machine_evidence=True,
            )
            self.git(root, "add", ".loopseed")
            self.git(root, "commit", "-qm", "track LoopSeed control plane")
            head = self.git(root, "rev-parse", "HEAD")
            transition(root, phase="PLAN", next_action="Plan")
            transition(root, phase="IMPLEMENT", next_action="Build")
            transition(root, phase="VERIFY", next_action="Bind")
            bind_project(root, "demo-project", head, "artifact.txt")
            self.assertTrue(self.pass_machine(root, head, command)["ok"])
            self.assertEqual(finalize(root)["status"], "VERIFIED")

    def test_version_downgrade_cannot_disable_integrity_or_task_graph(self) -> None:
        temporary, root, head, command = self.prepare(machine=True)
        with temporary:
            self.assertTrue(self.pass_machine(root, head, command)["ok"])
            target = root / ".loopseed/one-shotted"
            for name in ("goal-contract.json", "state.json"):
                path = target / name
                item = json.loads(path.read_text(encoding="utf-8"))
                item["loopseed_version"] = "0.6.9"
                path.write_text(json.dumps(item), encoding="utf-8")
            (target / "task-graph.json").unlink()
            ledger = target / "evidence.jsonl"
            item = json.loads(ledger.read_text(encoding="utf-8"))
            item["producer"] = "forged.runner"
            ledger.write_text(json.dumps(item) + "\n", encoding="utf-8")
            report = validate(root)
            self.assertFalse(report["ok"])
            self.assertTrue(any("Missing required file" in error for error in report["errors"]))
            self.assertTrue(any("unknown producer" in error for error in report["errors"]))
            with self.assertRaises(OneShottedError):
                finalize(root)


if __name__ == "__main__":
    unittest.main()
