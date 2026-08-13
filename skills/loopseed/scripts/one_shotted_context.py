#!/usr/bin/env python3
"""Project planning recovery gate for LoopSeed One-Shotted calibration."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from one_shotted_bootstrap import initialize as _initialize
from one_shotted_io import load_run, locked_mutation, read_json, write_json_atomic
from one_shotted_types import VERSION, OneShottedError, clean_line, utc_now

PLANNING_STATUSES = {"FOUND", "NONE_FOUND"}
SOURCE_AUTHORITIES = {
    "CURRENT_USER_DECISION",
    "LOCKED_CREATIVE_BRIEF",
    "NAMED_PROJECT_PLAN",
    "REPOSITORY_INSTRUCTION",
    "IMPLEMENTATION_EVIDENCE",
    "REFERENCE",
}

_IGNORED_CONTEXT_DIRS = {
    ".git",
    ".loopseed",
    ".venv",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "coverage",
    "__pycache__",
}
_CONTEXT_DIR_NAMES = {
    "docs",
    "design",
    "planning",
    "plans",
    "product",
    "spec",
    "specs",
    "decisions",
    "adr",
}
_CONTEXT_NAME_TOKENS = (
    "readme",
    "agents",
    "plan",
    "planning",
    "roadmap",
    "gdd",
    "brief",
    "north-star",
    "north_star",
    "design",
    "product-spec",
    "product_spec",
    "milestone",
    "decision",
    "adr",
)
_CONTEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml"}


def _existing_project_content(root: Path) -> bool:
    project = root.expanduser().resolve()
    if not project.exists() or not project.is_dir():
        return False
    for child in project.iterdir():
        if child.name in {".git", ".loopseed"}:
            continue
        return True
    return False


def _planning_source_candidates(root: Path, *, limit: int = 64) -> list[str]:
    """Find likely authority/context files by path only; contents must still be inspected by the Lead."""
    project = root.expanduser().resolve()
    found: list[str] = []
    if not project.is_dir():
        return found

    for current, dirnames, filenames in os.walk(project):
        dirnames[:] = [name for name in dirnames if name not in _IGNORED_CONTEXT_DIRS]
        current_path = Path(current)
        try:
            relative_dir = current_path.relative_to(project)
        except ValueError:
            continue
        context_dir = any(part.casefold() in _CONTEXT_DIR_NAMES for part in relative_dir.parts)

        for filename in filenames:
            path = current_path / filename
            if path.suffix.casefold() not in _CONTEXT_SUFFIXES:
                continue
            lowered = filename.casefold()
            likely_name = any(token in lowered for token in _CONTEXT_NAME_TOKENS)
            if not context_dir and not likely_name:
                continue
            try:
                relative = path.relative_to(project).as_posix()
            except ValueError:
                continue
            found.append(relative)
            if len(found) >= limit:
                return sorted(found)
    return sorted(found)


def _context_id(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "CONTEXT-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _draft_project_context(run_id: str, *, required: bool) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "loopseed_version": VERSION,
        "run_id": run_id,
        "status": "DRAFT" if required else "SKIPPED",
        "planning_status": "",
        "searched_locations": [],
        "sources": [],
        "inherited_decisions": [],
        "open_decisions": [],
        "unresolved_conflicts": [],
        "summary": "",
        "locked_at": None,
        "locked_by": None,
        "context_id": None,
    }


def _none_found_receipt(run_id: str, candidates: list[str]) -> dict[str, Any]:
    locked_at = utc_now()
    receipt: dict[str, Any] = {
        "schema_version": "1.0",
        "loopseed_version": VERSION,
        "run_id": run_id,
        "status": "LOCKED",
        "planning_status": "NONE_FOUND",
        "searched_locations": [
            "repository root planning/context filename scan",
            "README/AGENTS and docs/design/planning/product/spec/decision paths",
        ],
        "sources": [],
        "inherited_decisions": [],
        "open_decisions": [],
        "unresolved_conflicts": [],
        "summary": (
            "Existing implementation is present, but the bootstrap path scan found no likely project planning or decision source. "
            "Creative dialogue may proceed from the current user seed; implementation remains evidence rather than recovered planning authority."
        ),
        "candidate_paths": candidates,
        "locked_at": locked_at,
        "locked_by": "bootstrap-path-scan",
    }
    receipt["context_id"] = _context_id(receipt)
    return receipt


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
    """Initialize normally, then recover planning authority before calibrated dialogue."""
    existing_before = _existing_project_content(root)
    planning_candidates = _planning_source_candidates(root) if existing_before else []
    result = _initialize(
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
    dialogue_enabled = isinstance(calibration, dict) and bool(calibration.get("enabled", False))
    run_id = str(goal_contract.get("run_id", ""))

    context_required = bool(existing_before and dialogue_enabled and planning_candidates)
    auto_none_found = bool(existing_before and dialogue_enabled and not planning_candidates)
    if context_required:
        context_status = "PENDING"
        context = _draft_project_context(run_id, required=True)
        context["candidate_paths"] = planning_candidates
        next_action = (
            "Recover existing project planning before creative dialogue. Inspect the discovered candidate paths, current accepted user decisions, references, and implementation state; fill project-context.json and lock it before asking new product questions."
        )
    elif auto_none_found:
        context_status = "LOCKED"
        context = _none_found_receipt(run_id, planning_candidates)
        next_action = (
            "No likely planning source was discovered by the bootstrap scan. Begin creative co-director dialogue from the current user seed, while treating existing implementation as evidence rather than planning authority."
        )
    else:
        context_status = "SKIPPED"
        context = _draft_project_context(run_id, required=False)
        next_action = str(state.get("next_action", ""))

    if isinstance(calibration, dict):
        calibration["context_recovery"] = {
            "required": bool(context_required or auto_none_found),
            "status": context_status,
            "policy": "planning-before-dialogue",
            "context_id": context.get("context_id"),
            "planning_status": context.get("planning_status") or None,
            "candidate_paths": planning_candidates,
            "locked_at": context.get("locked_at"),
        }
    write_json_atomic(target / "project-context.json", context)
    if dialogue_enabled and existing_before:
        state["next_action"] = next_action
        state["updated_at"] = utc_now()
    write_json_atomic(target / "goal-contract.json", goal_contract)
    write_json_atomic(target / "state.json", state)
    result["context_recovery_status"] = context_status
    result["context_candidate_paths"] = planning_candidates
    result["next_action"] = state.get("next_action")
    return result


def _string_list(value: Any, *, name: str, allow_empty: bool = True) -> list[str]:
    if not isinstance(value, list):
        raise OneShottedError(f"{name} must be an array")
    cleaned = [clean_line(str(item), name=name) for item in value]
    if not allow_empty and not cleaned:
        raise OneShottedError(f"{name} must not be empty")
    return cleaned


def _normalize_sources(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise OneShottedError("project_context.sources must be an array")
    sources: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise OneShottedError(f"project_context.sources[{index}] must be an object")
        locator = clean_line(str(item.get("locator", "")), name=f"project_context.sources[{index}].locator")
        role = clean_line(str(item.get("role", "")), name=f"project_context.sources[{index}].role")
        authority = clean_line(
            str(item.get("authority", "")),
            name=f"project_context.sources[{index}].authority",
        ).upper()
        if authority not in SOURCE_AUTHORITIES:
            raise OneShottedError(
                f"project_context.sources[{index}].authority must be one of {sorted(SOURCE_AUTHORITIES)}"
            )
        sources.append({"locator": locator, "role": role, "authority": authority})
    return sources


def _recovery_contract(goal: dict[str, Any]) -> dict[str, Any]:
    calibration = goal.get("calibration")
    if not isinstance(calibration, dict) or not calibration.get("enabled", False):
        raise OneShottedError("This run does not enable creative calibration")
    recovery = calibration.get("context_recovery")
    if not isinstance(recovery, dict):
        recovery = {
            "required": True,
            "status": "PENDING",
            "policy": "planning-before-dialogue",
            "context_id": None,
            "locked_at": None,
        }
        calibration["context_recovery"] = recovery
    return recovery


def assert_project_context_ready(root: Path) -> dict[str, Any] | None:
    """Return locked context when required; reject dialogue when recovery is still pending."""
    target, goal, _, _ = load_run(root)
    calibration = goal.get("calibration", {})
    if not isinstance(calibration, dict) or not calibration.get("enabled", False):
        return None

    recovery = calibration.get("context_recovery")
    if not isinstance(recovery, dict):
        candidates = _planning_source_candidates(root)
        if not candidates:
            return None
        raise OneShottedError(
            "Project context recovery is required before creative dialogue. Inspect existing plans, accepted decisions, current project state, and references; fill .loopseed/one-shotted/project-context.json, then run one_shotted_context.py lock."
        )

    if not recovery.get("required", False):
        return None
    if str(recovery.get("status", "")).upper() != "LOCKED":
        raise OneShottedError(
            "Project context recovery is not locked. Recover existing planning before creative dialogue; do not reopen settled product decisions. Fill .loopseed/one-shotted/project-context.json and run one_shotted_context.py lock."
        )

    path = target / "project-context.json"
    if not path.is_file():
        raise OneShottedError("Locked project context is missing project-context.json")
    context = read_json(path)
    if str(context.get("status", "")).upper() != "LOCKED":
        raise OneShottedError("project-context.json must be LOCKED before creative dialogue")
    context_id = str(context.get("context_id", "")).strip()
    if not context_id or context_id != str(recovery.get("context_id", "")).strip():
        raise OneShottedError("Goal contract and project-context.json must share one context_id")
    return context


@locked_mutation
def lock_project_context(root: Path, context: dict[str, Any], *, actor: str = "lead") -> dict[str, Any]:
    target, goal, _, state = load_run(root)
    calibration = goal.get("calibration")
    if not isinstance(calibration, dict) or not calibration.get("enabled", False):
        raise OneShottedError("This run does not enable creative calibration")
    if str(calibration.get("status", "")).upper() != "OPEN":
        raise OneShottedError("Project context may only be recovered while creative calibration is OPEN")
    if str(state.get("status", "")).upper() != "ACTIVE" or str(state.get("phase", "")).upper() != "CALIBRATE":
        raise OneShottedError("Project context may only be locked during ACTIVE/CALIBRATE")
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
                "FOUND project planning requires inherited_decisions; recover what is already settled before asking new questions"
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

    recovery = _recovery_contract(goal)
    recovery.update(
        {
            "required": True,
            "status": "LOCKED",
            "policy": "planning-before-dialogue",
            "context_id": stored["context_id"],
            "planning_status": planning_status,
            "locked_at": locked_at,
        }
    )
    state["next_action"] = (
        "Begin creative co-director dialogue from the recovered project plan. Preserve inherited decisions, resolve explicit conflicts, and ask only about material open decisions."
        if planning_status == "FOUND"
        else "No authoritative prior planning was found after a real search. Begin creative co-director dialogue from the user's seed without inventing inherited decisions."
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


def lock_project_context_file(root: Path, file_path: Path, *, actor: str = "lead") -> dict[str, Any]:
    source = file_path.expanduser()
    if not source.is_absolute():
        source = root.expanduser().resolve() / source
    context = read_json(source)
    return lock_project_context(root, context, actor=actor)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Lock recovered project planning before LoopSeed creative dialogue"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    lock = subparsers.add_parser("lock", help="Validate and lock a recovered project context JSON")
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
