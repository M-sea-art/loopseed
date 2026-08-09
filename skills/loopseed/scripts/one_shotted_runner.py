"""Execute verification commands and emit machine-authored evidence receipts."""

from __future__ import annotations

import os
import signal
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from one_shotted_integrity import (
    artifact_identity,
    assert_binding_current,
    binding_subject,
    repository_identity,
    unexpected_untracked_paths,
)
from one_shotted_io import (
    append_jsonl,
    current_artifact_evidence_receipts,
    current_gate_evidence_ids,
    load_run,
    run_lock,
    verification_activity_lock,
    write_json_atomic,
)
from one_shotted_model import gate_map
from one_shotted_types import OneShottedError, clean_line, new_id, utc_now

PRODUCER = "loopseed.machine-evidence-runner"
MAX_OUTPUT = 4000


def _read_bounded(handle: Any) -> str:
    handle.seek(0)
    value = handle.read(MAX_OUTPUT + 1)
    text = value.decode(errors="replace") if isinstance(value, bytes) else str(value)
    return text if len(text) <= MAX_OUTPUT else text[:MAX_OUTPUT] + "\n...[truncated]"


def _missing_artifact(expected: dict[str, Any], error: Exception) -> dict[str, Any]:
    return {
        "path": str(expected.get("path", "")),
        "kind": "missing",
        "sha256": "",
        "error": str(error),
    }


def _prepare_execution(
    root: Path,
    gate_id: str,
    actor: str,
    project_id: str,
    candidate_commit: str,
    artifact: str,
) -> tuple[
    Path,
    str,
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    list[dict[str, Any]],
]:
    """Take a consistent pre-execution snapshot under the short state lock."""

    with run_lock(root):
        target, goal, acceptance, state = load_run(root)
        if str(state.get("status", "")).upper() != "ACTIVE":
            raise OneShottedError("Machine evidence may only be executed while the run is ACTIVE")
        gates = gate_map(acceptance)
        if gate_id not in gates:
            raise OneShottedError(f"Unknown acceptance gate: {gate_id}")
        gate = gates[gate_id]
        verifier = str(gate.get("verifier", "")).strip()
        owner = str(gate.get("owner", "")).strip()
        if actor != verifier:
            raise OneShottedError(
                f"Gate {gate_id} evidence must be executed by verifier {verifier!r}"
            )
        if actor == owner:
            raise OneShottedError("Implementation owner cannot self-approve a gate")

        binding = state.get("verification_binding")
        subject = binding_subject(binding)
        if subject is None:
            raise OneShottedError("Active run lacks a project binding; use the bind command first")
        evidence_artifacts = current_artifact_evidence_receipts(
            target, acceptance, binding
        )
        allowed_untracked = [str(item["path"]) for item in evidence_artifacts]
        before_receipt = assert_binding_current(
            root, binding, allowed_untracked=allowed_untracked
        )
        before = artifact_identity(root, artifact)
        if (
            project_id,
            candidate_commit,
            (before["path"], before["kind"], before["sha256"]),
        ) != subject:
            raise OneShottedError(
                "Machine evidence does not match the active project, candidate, and artifact binding"
            )
        return (
            target,
            str(goal.get("run_id", "")),
            dict(binding),
            before,
            before_receipt,
            evidence_artifacts,
        )


def _execute_command(
    root: Path,
    command: str,
    timeout_seconds: int,
) -> tuple[int, bool, str, str]:
    timed_out = False
    with tempfile.TemporaryFile() as stdout_handle, tempfile.TemporaryFile() as stderr_handle:
        process_options: dict[str, Any] = {}
        if os.name == "posix":
            process_options["start_new_session"] = True
        elif hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):  # pragma: no cover - Windows
            process_options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        try:
            process = subprocess.Popen(
                command,
                cwd=root.expanduser().resolve(),
                shell=True,
                stdout=stdout_handle,
                stderr=stderr_handle,
                **process_options,
            )
        except OSError as exc:
            return 126, False, "", str(exc)
        try:
            exit_code = int(process.wait(timeout=timeout_seconds))
        except subprocess.TimeoutExpired:
            timed_out = True
            if os.name == "posix":
                os.killpg(process.pid, signal.SIGKILL)
            else:  # pragma: no cover - Windows
                process.kill()
            process.wait()
            exit_code = 124
        stdout = _read_bounded(stdout_handle)
        stderr = _read_bounded(stderr_handle)
    return exit_code, timed_out, stdout, stderr


def _commit_evidence(
    root: Path,
    gate_id: str,
    actor: str,
    binding: dict[str, Any],
    entry: dict[str, Any],
) -> dict[str, Any]:
    """Merge a completed verifier receipt into the latest control-plane state."""

    with run_lock(root):
        target, goal, acceptance, state = load_run(root)
        if str(state.get("status", "")).upper() != "ACTIVE":
            raise OneShottedError(
                "Run became terminal while verification was executing; receipt was not committed"
            )
        current_binding = state.get("verification_binding")
        if (
            binding_subject(current_binding) != binding_subject(binding)
            or str(current_binding.get("binding_id", "")) != str(binding.get("binding_id", ""))
            or current_binding.get("generation") != binding.get("generation")
        ):
            raise OneShottedError(
                "Verification binding changed while the command was running; rerun against the current binding"
            )
        if str(goal.get("run_id", "")) != str(entry.get("run_id", "")):
            raise OneShottedError("Run identity changed while the verifier command was executing")

        gates = gate_map(acceptance)
        if gate_id not in gates:
            raise OneShottedError(f"Acceptance gate disappeared during verification: {gate_id}")
        gate = gates[gate_id]
        if str(gate.get("verifier", "")).strip() != actor:
            raise OneShottedError(f"Gate {gate_id} verifier changed during verification")
        if str(gate.get("owner", "")).strip() == actor:
            raise OneShottedError("Implementation owner cannot self-approve a gate")

        append_jsonl(target / "evidence.jsonl", entry)
        result = str(entry["result"])
        gate["status"] = result
        gate["evidence_ids"] = current_gate_evidence_ids(target, gate_id, current_binding)
        gate["updated_at"] = entry["created_at"]
        write_json_atomic(target / "acceptance.json", acceptance)

        state["round"] = int(state.get("round", 0)) + 1
        state["no_progress_rounds"] = (
            0 if result == "PASS" else int(state.get("no_progress_rounds", 0))
        )
        any_failed = any(
            str(candidate.get("status", "")).upper() == "FAIL"
            for candidate in gates.values()
        )
        current_phase = str(state.get("phase", "")).upper()
        if result == "FAIL":
            state["phase"] = "REPAIR"
            state["next_action"] = (
                f"Repair gate {gate_id} from machine evidence {entry['id']}, then rerun it."
            )
        elif current_phase in {"VERIFY", "REPAIR"}:
            state["phase"] = "REPAIR" if any_failed else "VERIFY"
            state["next_action"] = (
                "Repair the remaining failed gates and rerun their verifiers."
                if any_failed
                else "Evaluate the remaining acceptance gates."
            )
        state["updated_at"] = entry["created_at"]
        write_json_atomic(target / "state.json", state)
        return {
            "phase": state.get("phase"),
            "next_action": state.get("next_action"),
        }


def run_evidence(
    root: Path,
    gate_id: str,
    actor: str,
    command: str,
    project_id: str,
    candidate_commit: str,
    artifact: str,
    *,
    timeout_seconds: int = 120,
) -> dict[str, Any]:
    actor = clean_line(actor, name="evidence actor")
    if not isinstance(command, str) or not command.strip():
        raise OneShottedError("evidence command must not be empty")
    # Preserve quoting, repeated spaces, and newlines exactly; only surrounding
    # whitespace is not semantically part of the shell command.
    command = command.strip()
    project_id = clean_line(project_id, name="project id")
    candidate_commit = clean_line(candidate_commit, name="candidate commit")
    if timeout_seconds <= 0:
        raise OneShottedError("timeout_seconds must be positive")

    # Shared activity locks let independent gate commands execute in parallel.
    # Bind/finalize take the exclusive side, while ordinary task/status updates
    # remain available and each receipt merges under the short state lock.
    with verification_activity_lock(root, exclusive=False):
        target, run_id, binding, before, before_receipt, evidence_artifacts_before = _prepare_execution(
            root,
            gate_id,
            actor,
            project_id,
            candidate_commit,
            artifact,
        )
        started_at = utc_now()
        exit_code, timed_out, stdout, stderr = _execute_command(
            root, command, timeout_seconds
        )
        finished_at = utc_now()

        try:
            after = artifact_identity(root, artifact)
        except OneShottedError as exc:
            after = _missing_artifact(binding["artifact"], exc)
        repository_after = repository_identity(root)
        evidence_artifacts_after: list[dict[str, Any]] = []
        for expected_evidence_artifact in evidence_artifacts_before:
            try:
                evidence_artifacts_after.append(
                    artifact_identity(root, str(expected_evidence_artifact["path"]))
                )
            except OneShottedError as exc:
                evidence_artifacts_after.append(
                    _missing_artifact(expected_evidence_artifact, exc)
                )
        artifact_stable = before == after == binding["artifact"]
        evidence_artifacts_stable = (
            evidence_artifacts_before == evidence_artifacts_after
        )
        head_stable = (
            repository_after.get("detected") is True
            and str(repository_after.get("head") or "") == candidate_commit
        )
        tracked_worktree_stable = repository_after.get("tracked_worktree_dirty") is False
        unexpected_untracked_after = unexpected_untracked_paths(
            repository_after,
            [
                str(binding["artifact"]["path"]),
                *(str(item["path"]) for item in evidence_artifacts_before),
            ],
        )
        untracked_stable = not unexpected_untracked_after
        integrity_stable = (
            artifact_stable
            and evidence_artifacts_stable
            and head_stable
            and tracked_worktree_stable
            and untracked_stable
        )
        failure_reason: str | None = None
        if not artifact_stable:
            failure_reason = (
                "ARTIFACT_MISSING_AFTER_VERIFICATION"
                if after.get("kind") == "missing"
                else "ARTIFACT_MUTATED_DURING_VERIFICATION"
            )
        elif not evidence_artifacts_stable:
            failure_reason = "EVIDENCE_ARTIFACT_MUTATED_DURING_VERIFICATION"
        elif not head_stable:
            failure_reason = "CANDIDATE_COMMIT_CHANGED_DURING_VERIFICATION"
        elif not tracked_worktree_stable:
            failure_reason = "TRACKED_WORKTREE_CHANGED_DURING_VERIFICATION"
        elif not untracked_stable:
            failure_reason = "UNTRACKED_CONTENT_CHANGED_DURING_VERIFICATION"

        result = (
            "PASS"
            if exit_code == 0 and not timed_out and integrity_stable
            else "FAIL"
        )
        evidence_id = new_id("EV")
        entry = {
            "id": evidence_id,
            "schema_version": "1.2",
            "kind": "MACHINE",
            "producer": PRODUCER,
            "run_id": run_id,
            "gate_id": gate_id,
            "result": result,
            "actor": actor,
            "summary": (
                f"Command exited {exit_code}; timed_out={str(timed_out).lower()}; "
                f"integrity_stable={str(integrity_stable).lower()}"
            ),
            "command": command,
            "cwd": ".",
            "started_at": started_at,
            "finished_at": finished_at,
            "created_at": finished_at,
            "exit_code": exit_code,
            "timed_out": timed_out,
            "stdout_summary": stdout,
            "stderr_summary": stderr,
            "project_id": project_id,
            "candidate_commit": candidate_commit,
            "binding_id": binding.get("binding_id"),
            "generation": binding.get("generation"),
            "actual_candidate_commit": (
                repository_after.get("head") if repository_after.get("detected") else None
            ),
            "git_repository_detected": bool(
                before_receipt["repository"].get("detected")
            ),
            "worktree_dirty_before": before_receipt["repository"].get("worktree_dirty"),
            "worktree_dirty_after": repository_after.get("worktree_dirty"),
            "tracked_worktree_dirty_before": before_receipt["repository"].get(
                "tracked_worktree_dirty"
            ),
            "tracked_worktree_dirty_after": repository_after.get(
                "tracked_worktree_dirty"
            ),
            "unexpected_untracked_before": [],
            "unexpected_untracked_after": unexpected_untracked_after,
            "expected_artifact": dict(binding["artifact"]),
            "artifact_before": before,
            "artifact_after": after,
            "evidence_artifacts_before": evidence_artifacts_before,
            "evidence_artifacts_after": evidence_artifacts_after,
            "evidence_artifacts_stable": evidence_artifacts_stable,
            "integrity_stable": integrity_stable,
            "integrity_failure_reason": failure_reason,
        }
        state_result = _commit_evidence(root, gate_id, actor, binding, entry)

    return {
        "ok": result == "PASS",
        "evidence_id": evidence_id,
        "gate": gate_id,
        "result": result,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "integrity_stable": integrity_stable,
        "integrity_failure_reason": failure_reason,
        "artifact": after,
        **state_result,
    }
