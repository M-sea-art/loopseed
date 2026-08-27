#!/usr/bin/env python3
"""Dialogue-independent project-context shell for LoopSeed v0.8."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from one_shotted_context import (
    PLANNING_STATUSES,
    _context_id,
    _draft_project_context,
    _existing_project_content,
    _none_found_receipt,
    _normalize_sources,
    _planning_source_candidates,
    _string_list,
    initialize as _legacy_initialize,
    lock_project_context as _legacy_lock_project_context,
)
from one_shotted_io import load_run, locked_mutation, read_json, write_json_atomic
from one_shotted_types import VERSION, OneShottedError, clean_line, utc_now


def initialize(
    root: Path,
    goal: str,
    force: bool = False,
    *,
    domain: str = "auto",
    production_mode: str = "auto",
    dialogue: str = "auto",
    max_dialogue_rounds: int = 5,
) -> dict[str, Any]:
    """Initialize v0.8 and keep project-context recovery active even when dialogue is off."""
    existing_before = _existing_project_content(root)
    planning_candidates = _planning_source_candidates(root) if existing_before else []
    result = _legacy_initialize(
        root,
        goal,
        force=force,
        domain=domain,
        production_mode=production_mode,
        dialogue=dialogue,
        max_dialogue_rounds=max_dialogue_rounds,
    )
    target, goal_contract, _, state = load_run(root)
    calibration = goal_contract.get("calibration")
    if not isinstance(calibration, dict):
        calibration = {}
        goal_contract["calibration"] = calibration

    # v0.7.2 already handles dialogue-enabled recovery. v0.8 only fills the
    # missing direct-production path here so the shell never depends on the interview layer.
    if calibration.get("enabled", False) or not existing_before:
        return result

    run_id = str(goal_contract.get("run_id", ""))
    if planning_candidates:
        context_status = "PENDING"
        context = _draft_project_context(run_id, required=True)
        context["candidate_paths"] = planning_candidates
        next_action = (
            "Recover existing project planning before production. Inspect the discovered candidate paths, inherited decisions, current user authority, references, and implementation state; lock project-context.json, then declare the minimum hard-floor gates plus one inspectable quality-bar gate."
        )
    else:
        context_status = "LOCKED"
        context = _none_found_receipt(run_id, planning_candidates)
        next_action = (
            "No likely planning source was discovered by the bootstrap scan. Continue directly from the current user goal; treat existing implementation as evidence, then declare the minimum hard-floor gates plus one inspectable quality-bar gate."
        )

    calibration["context_recovery"] = {
        "required": True,
        "status": context_status,
        "policy": "planning-before-production",
        "context_id": context.get("context_id"),
        "planning_status": context.get("planning_status") or None,
        "candidate_paths": planning_candidates,
        "locked_at": context.get("locked_at"),
    }
    write_json_atomic(target / "project-context.json", context)
    state["next_action"] = next_action
    state["updated_at"] = utc_now()
    write_json_atomic(target / "goal-contract.json", goal_contract)
    write_json_atomic(target / "state.json", state)

    result["context_recovery_status"] = context_status
    result["context_candidate_paths"] = planning_candidates
    result["next_action"] = next_action
    return result


def assert_project_context_ready(root: Path) -> dict[str, Any] | None:
    """Require recovered planning before dialogue or direct production when needed."""
    target, goal, _, _ = load_run(root)
    calibration = goal.get("calibration", {})
    if not isinstance(calibration, dict):
        return None
    recovery = calibration.get("context_recovery")
    if not isinstance(recovery, dict) or not recovery.get("required", False):
        return None
    if str(recovery.get("status", "")).upper() != "LOCKED":
        raise OneShottedError(
            "Project context recovery is not locked. Recover existing planning before production; do not reopen settled product decisions. Fill .loopseed/one-shotted/project-context.json and run one_shotted_context_shell.py lock."
        )

    path = target / "project-context.json"
    if not path.is_file():
        raise OneShottedError("Locked project context is missing project-context.json")
    context = read_json(path)
    if str(context.get("status", "")).upper() != "LOCKED":
        raise OneShottedError("project-context.json must be LOCKED before production")
    context_id = str(context.get("context_id", "")).strip()
    if not context_id or context_id != str(recovery.get("context_id", "")).strip():
        raise OneShottedError("Goal contract and project-context.json must share one context_id")
    return context


@locked_mutation
def _lock_direct_project_context(
    root: Path,
    context: dict[str, Any],
    *,
    actor: str = "lead",
) -> dict[str, Any]:
    target, goal, _, state = load_run(root)
    calibration = goal.get("calibration")
    if not isinstance(calibration, dict):
        raise OneShottedError("Goal contract is missing calibration metadata")
    recovery = calibration.get("context_recovery")
    if not isinstance(recovery, dict) or not recovery.get("required", False):
        raise OneShottedError("This run does not require project-context recovery")
    if str(recovery.get("status", "")).upper() != "PENDING":
        raise OneShottedError("Project context is already locked or skipped")
    if str(state.get("status", "")).upper() != "ACTIVE" or str(state.get("phase", "")).upper() != "BIND":
        raise OneShottedError("Direct-path project context may only be locked during ACTIVE/BIND")
    if not isinstance(context, dict):
        raise OneShottedError("project context must be a JSON object")

    planning_status = clean_line(
        str(context.get("planning_status", "")), name="project_context.planning_status"
    ).upper()
    if planning_status not in PLANNING_STATUSES:
        raise OneShottedError(
            f"project_context.planning_status must be one of {sorted(PLANNING_STATUSES)}"
        )
    searched_locations = _string_list(
        context.get("searched_locations"),
        name="project_context.searched_locations",
        allow_empty=False,
    )
    sources = _normalize_sources(context.get("sources", []))
    inherited_decisions = _string_list(
        context.get("inherited_decisions", []), name="project_context.inherited_decisions"
    )
    open_decisions = _string_list(
        context.get("open_decisions", []), name="project_context.open_decisions"
    )
    unresolved_conflicts = _string_list(
        context.get("unresolved_conflicts", []), name="project_context.unresolved_conflicts"
    )
    summary = clean_line(str(context.get("summary", "")), name="project_context.summary")

    if planning_status == "FOUND":
        if not sources:
            raise OneShottedError("FOUND project planning requires at least one source")
        if not inherited_decisions:
            raise OneShottedError(
                "FOUND project planning requires inherited_decisions; recover what is already settled before production"
            )

    locked_at = utc_now()
    stored: dict[str, Any] = {
        "schema_version": "1.0",
        "loopseed_version": goal.get("loopseed_version", VERSION),
        "run_id": goal.get("run_id"),
        "status": "LOCKED",
        "planning_status": planning_status,
        "searched_locations": searched_locations,
        "sources": sources,
        "inherited_decisions": inherited_decisions,
        "open_decisions": open_decisions,
        "unresolved_conflicts": unresolved_conflicts,
        "summary": summary,
        "locked_at": locked_at,
        "locked_by": clean_line(actor, name="project context locking actor"),
    }
    stored["context_id"] = _context_id(stored)
    write_json_atomic(target / "project-context.json", stored)

    recovery.update(
        {
            "required": True,
            "status": "LOCKED",
            "policy": "planning-before-production",
            "context_id": stored["context_id"],
            "planning_status": planning_status,
            "locked_at": locked_at,
        }
    )
    state["next_action"] = (
        "Project planning is recovered. Preserve inherited decisions, resolve only genuine open conflicts, then declare the minimum hard-floor gates plus one inspectable quality-bar gate."
        if planning_status == "FOUND"
        else "No authoritative prior planning was found after a real search. Continue from the user's goal and declare the minimum hard-floor gates plus one inspectable quality-bar gate."
    )
    state["updated_at"] = locked_at
    write_json_atomic(target / "goal-contract.json", goal)
    write_json_atomic(target / "state.json", state)
    return {
        "ok": True,
        "context_id": stored["context_id"],
        "planning_status": planning_status,
        "context_status": "LOCKED",
        "project_context": str(target / "project-context.json"),
        "next_action": state["next_action"],
    }


def lock_project_context(root: Path, context: dict[str, Any], *, actor: str = "lead") -> dict[str, Any]:
    """Lock context on either calibrated or direct-production paths."""
    _, goal, _, _ = load_run(root)
    calibration = goal.get("calibration", {})
    if isinstance(calibration, dict) and calibration.get("enabled", False):
        return _legacy_lock_project_context(root, context, actor=actor)
    return _lock_direct_project_context(root, context, actor=actor)


def lock_project_context_file(root: Path, file_path: Path, *, actor: str = "lead") -> dict[str, Any]:
    source = file_path.expanduser()
    if not source.is_absolute():
        source = root.expanduser().resolve() / source
    return lock_project_context(root, read_json(source), actor=actor)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Lock recovered project planning before LoopSeed dialogue or direct production"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    lock = subparsers.add_parser("lock", help="Validate and lock recovered project-context JSON")
    lock.add_argument("--root", default=".", help="Target project root")
    lock.add_argument("--file", required=True, help="Recovered project-context JSON file")
    lock.add_argument("--actor", default="lead", help="Actor locking the context")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        result = lock_project_context_file(Path(args.root), Path(args.file), actor=args.actor)
    except OneShottedError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
