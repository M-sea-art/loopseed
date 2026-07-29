"""Evidence-bound recovery from BLOCKED for C1 runs."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from one_shotted_integrity import assert_artifact_matches
from one_shotted_io import load_run, read_jsonl, write_json_atomic
from one_shotted_runner import PRODUCER
from one_shotted_types import OneShottedError, clean_line, utc_now


def _parse_utc(value: str, *, name: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise OneShottedError(f"Invalid {name} timestamp: {value!r}") from exc


def resume(root: Path, evidence_id: str, actor: str) -> dict[str, Any]:
    target, _, _, state = load_run(root)
    if str(state.get("status", "")).upper() != "BLOCKED":
        raise OneShottedError("Only a BLOCKED run can be resumed")

    evidence_id = clean_line(evidence_id, name="resume evidence id")
    actor = clean_line(actor, name="resume actor")
    blocker = state.get("true_blocker")
    if not isinstance(blocker, dict):
        raise OneShottedError("BLOCKED state is missing true_blocker")
    blocker_id = str(blocker.get("id", "")).strip()
    blocked_at = str(blocker.get("blocked_at", "")).strip()
    binding = blocker.get("binding")
    if not blocker_id or not blocked_at or not isinstance(binding, dict):
        raise OneShottedError("Active blocker lacks C1 id, timestamp, or binding")

    items, errors = read_jsonl(target / "evidence.jsonl")
    if errors:
        raise OneShottedError("Cannot resume with an invalid evidence ledger: " + "; ".join(errors))
    matches = [item for item in items if str(item.get("id", "")) == evidence_id]
    if len(matches) != 1:
        raise OneShottedError(f"Resume evidence not found: {evidence_id}")
    evidence = matches[0]

    if evidence.get("kind") != "MACHINE" or evidence.get("producer") != PRODUCER:
        raise OneShottedError("Resume requires machine-produced evidence")
    if evidence.get("purpose") != "UNBLOCK":
        raise OneShottedError("Resume evidence must have purpose UNBLOCK")
    if str(evidence.get("blocker_id", "")) != blocker_id:
        raise OneShottedError("Resume evidence belongs to a different blocker")
    if str(evidence.get("actor", "")) != actor:
        raise OneShottedError("Resume actor must be the actor who produced the unblock evidence")
    if evidence.get("result") != "PASS" or int(evidence.get("exit_code", -1)) != 0:
        raise OneShottedError("Resume evidence did not pass")
    if _parse_utc(str(evidence.get("created_at", "")), name="evidence") <= _parse_utc(
        blocked_at, name="blocked_at"
    ):
        raise OneShottedError("Resume evidence is stale; it must be newer than the blocker")

    if str(evidence.get("project_id", "")) != str(binding.get("project_id", "")):
        raise OneShottedError("Resume evidence has the wrong project binding")
    if str(evidence.get("candidate_commit", "")) != str(binding.get("candidate_commit", "")):
        raise OneShottedError("Resume evidence has the wrong candidate commit")
    expected_artifact = binding.get("artifact")
    actual_artifact = evidence.get("artifact")
    if not isinstance(expected_artifact, dict) or not isinstance(actual_artifact, dict):
        raise OneShottedError("Resume evidence is missing artifact identity")
    if str(actual_artifact.get("path", "")) != str(expected_artifact.get("path", "")):
        raise OneShottedError("Resume evidence has the wrong artifact path")
    if str(actual_artifact.get("sha256", "")) != str(expected_artifact.get("sha256", "")):
        raise OneShottedError("Resume evidence has the wrong artifact hash")
    assert_artifact_matches(root, actual_artifact)

    resolved_at = utc_now()
    resolved = dict(blocker)
    resolved.update(
        {
            "status": "RESOLVED",
            "resolved_at": resolved_at,
            "resolved_by": actor,
            "resolved_by_evidence": evidence_id,
        }
    )
    state.setdefault("blocker_history", []).append(resolved)
    state["true_blocker"] = resolved
    state["status"] = "ACTIVE"
    state["phase"] = "VERIFY"
    state["round"] = int(state.get("round", 0)) + 1
    state["last_resume_at"] = resolved_at
    state["last_resume_evidence_id"] = evidence_id
    state["next_action"] = "Run fresh gate verification against the current bound candidate and artifact."
    state["updated_at"] = resolved_at
    write_json_atomic(target / "state.json", state)
    return {
        "ok": True,
        "status": "ACTIVE",
        "phase": "VERIFY",
        "blocker_id": blocker_id,
        "evidence_id": evidence_id,
        "next_action": state["next_action"],
    }
