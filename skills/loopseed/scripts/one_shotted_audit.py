"""Consistency audit for One-Shotted contracts, evidence, dialogue, and defects."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from one_shotted_io import read_json, read_jsonl
from one_shotted_model import gate_map, latest_defects
from one_shotted_types import (
    CALIBRATION_FILES,
    DIALOGUE_EFFECTS,
    DIALOGUE_KINDS,
    PRODUCTION_MODES,
    PROJECT_DOMAINS,
    REQUIRED_FILES,
    VALID_GATE_STATUSES,
    VALID_PHASES,
    VALID_STATUSES,
    OneShottedError,
    run_dir,
)


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def _validation_data(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    target = run_dir(root)
    errors: list[str] = []
    warnings: list[str] = []
    for name in REQUIRED_FILES:
        if not (target / name).exists():
            errors.append(f"Missing required file: {target / name}")
    try:
        goal = read_json(target / "goal-contract.json")
        acceptance = read_json(target / "acceptance.json")
        state = read_json(target / "state.json")
        experts = read_json(target / "expert-registry.json")
    except OneShottedError as exc:
        return {"ok": False, "errors": [str(exc)], "warnings": [], "run_dir": str(target)}, {}

    run_ids = {str(item.get("run_id", "")) for item in (goal, acceptance, state, experts)}
    if "" in run_ids or len(run_ids) != 1:
        errors.append("Goal, acceptance, expert registry, and state must share one non-empty run_id")
    if goal.get("mode") != "one-shotted" or state.get("mode") != "one-shotted":
        errors.append("Goal contract and state must declare mode='one-shotted'")
    if not _non_empty_string(goal.get("root_goal")):
        errors.append("Goal contract requires a non-empty root_goal")

    status = str(state.get("status", "")).upper()
    phase = str(state.get("phase", "")).upper()
    if status not in VALID_STATUSES:
        errors.append(f"Invalid state status: {status!r}")
    if phase not in VALID_PHASES:
        errors.append(f"Invalid state phase: {phase!r}")
    if status == "BLOCKED":
        blocker = state.get("true_blocker")
        if not isinstance(blocker, dict) or not _non_empty_string(
            blocker.get("reason")
        ) or not _non_empty_string(blocker.get("unblock_condition")):
            errors.append("BLOCKED requires true_blocker.reason and true_blocker.unblock_condition")

    project_domain = str(goal.get("project_domain", "general")).lower()
    production_mode = str(goal.get("production_mode", "focused")).lower()
    calibration = goal.get("calibration", {})
    calibration_enabled = isinstance(calibration, dict) and bool(calibration.get("enabled", False))
    calibration_status = (
        str(calibration.get("status", "SKIPPED")).upper() if isinstance(calibration, dict) else "SKIPPED"
    )
    creative_brief: dict[str, Any] = {}
    dialogue: list[dict[str, Any]] = []
    dialogue_by_id: dict[str, dict[str, Any]] = {}
    dialogue_rounds = 0

    if project_domain not in PROJECT_DOMAINS:
        errors.append(f"Invalid project_domain: {project_domain!r}")

    if calibration_enabled:
        for name in CALIBRATION_FILES:
            if not (target / name).exists():
                errors.append(f"Missing calibration file: {target / name}")
        try:
            creative_brief = read_json(target / "creative-brief.json")
        except OneShottedError as exc:
            errors.append(str(exc))
        dialogue, dialogue_errors = read_jsonl(target / "dialogue.jsonl")
        errors.extend(dialogue_errors)

        try:
            max_dialogue_rounds = int(calibration.get("max_rounds", 0))
        except (TypeError, ValueError):
            max_dialogue_rounds = 0
        if not 1 <= max_dialogue_rounds <= 8:
            errors.append("calibration.max_rounds must be between 1 and 8")

        question_fingerprints: set[str] = set()
        for event in dialogue:
            event_id = str(event.get("id", "")).strip()
            if not event_id:
                errors.append("Every dialogue entry requires a non-empty id")
            elif event_id in dialogue_by_id:
                errors.append(f"Duplicate dialogue id: {event_id}")
            else:
                dialogue_by_id[event_id] = event

            if event.get("run_id") != goal.get("run_id"):
                errors.append(f"Dialogue event {event_id or '<missing>'} must share the run_id")
            actor = str(event.get("actor", "")).lower()
            kind = str(event.get("kind", "")).lower()
            if actor not in {"user", "model"}:
                errors.append(f"Dialogue event {event_id or '<missing>'} has invalid actor {actor!r}")
            if kind not in DIALOGUE_KINDS:
                errors.append(f"Dialogue event {event_id or '<missing>'} has invalid kind {kind!r}")
            if actor == "user" and kind not in {"seed", "answer", "decision"}:
                errors.append(f"User dialogue event {event_id or '<missing>'} has invalid kind {kind!r}")
            if actor == "model" and kind not in {"synthesis", "question"}:
                errors.append(f"Model dialogue event {event_id or '<missing>'} has invalid kind {kind!r}")
            if not _non_empty_string(event.get("summary")):
                errors.append(f"Dialogue event {event_id or '<missing>'} requires a summary")

            effects = event.get("effects", [])
            advances = event.get("advances", [])
            if not isinstance(effects, list):
                errors.append(f"Dialogue event {event_id or '<missing>'} effects must be an array")
                effects = []
            if not isinstance(advances, list):
                errors.append(f"Dialogue event {event_id or '<missing>'} advances must be an array")
                advances = []
            invalid_effects = sorted({str(value) for value in effects} - DIALOGUE_EFFECTS)
            if invalid_effects:
                errors.append(
                    f"Dialogue event {event_id or '<missing>'} has unknown effects: {', '.join(invalid_effects)}"
                )
            if actor == "model" and not effects:
                errors.append(f"Model dialogue event {event_id or '<missing>'} requires at least one effect")
            if actor == "model" and not advances:
                errors.append(f"Model dialogue event {event_id or '<missing>'} must advance a material decision surface")

            options = event.get("options")
            recommended = event.get("recommended")
            if kind == "question":
                dialogue_rounds += 1
                if not isinstance(options, list) or not 2 <= len(options) <= 4:
                    errors.append(f"Question {event_id or '<missing>'} must offer between 2 and 4 options")
                    options = []
                option_ids: list[str] = []
                for option in options:
                    if not isinstance(option, dict):
                        errors.append(f"Question {event_id or '<missing>'} has a non-object option")
                        continue
                    option_id = str(option.get("id", "")).strip()
                    if not option_id or not _non_empty_string(option.get("label")) or not _non_empty_string(
                        option.get("consequence")
                    ):
                        errors.append(
                            f"Every option in question {event_id or '<missing>'} requires id, label, and consequence"
                        )
                    option_ids.append(option_id)
                if len(option_ids) != len(set(option_ids)):
                    errors.append(f"Question {event_id or '<missing>'} has duplicate option ids")
                if str(recommended or "") not in set(option_ids):
                    errors.append(f"Question {event_id or '<missing>'} recommendation must match an offered option")
                if "offer_options" not in effects:
                    errors.append(f"Question {event_id or '<missing>'} must declare offer_options")
                fingerprint = json.dumps(
                    {
                        "summary": str(event.get("summary", "")).casefold(),
                        "advances": sorted(str(value) for value in advances),
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
                if fingerprint in question_fingerprints:
                    errors.append(f"Repeated creative question detected: {event_id or '<missing>'}")
                question_fingerprints.add(fingerprint)
            elif options is not None or recommended is not None:
                errors.append(f"Only a question event may contain options or a recommendation: {event_id or '<missing>'}")

        if dialogue_rounds > max_dialogue_rounds:
            errors.append(
                f"Dialogue ledger contains {dialogue_rounds} model question rounds, above maximum {max_dialogue_rounds}"
            )
        try:
            state_dialogue_rounds = int(state.get("dialogue_rounds", -1))
        except (TypeError, ValueError):
            state_dialogue_rounds = -1
        if state_dialogue_rounds != dialogue_rounds:
            errors.append("state.dialogue_rounds must match the dialogue ledger")

        if calibration_status == "OPEN":
            if phase != "CALIBRATE" and status == "ACTIVE":
                errors.append("An OPEN creative dialogue must remain in phase CALIBRATE")
            if production_mode not in PRODUCTION_MODES | {"undecided"}:
                errors.append(f"Invalid open production_mode: {production_mode!r}")
            if creative_brief and str(creative_brief.get("status", "")).upper() not in {"DRAFT", ""}:
                errors.append("An OPEN calibration requires creative-brief.json status DRAFT")
        elif calibration_status == "LOCKED":
            if phase == "CALIBRATE":
                errors.append("A LOCKED creative brief cannot remain in phase CALIBRATE")
            if production_mode not in PRODUCTION_MODES:
                errors.append(f"Locked production_mode must be one of {sorted(PRODUCTION_MODES)}")
            if str(creative_brief.get("status", "")).upper() != "LOCKED":
                errors.append("goal calibration is LOCKED but creative-brief.json is not LOCKED")
            if creative_brief.get("run_id") != goal.get("run_id"):
                errors.append("Creative brief must share the run_id")
            brief_id = str(creative_brief.get("brief_id", "")).strip()
            if not brief_id or brief_id != str(calibration.get("brief_id", "")).strip():
                errors.append("Goal calibration and creative brief must share one non-empty brief_id")
            if str(creative_brief.get("project_domain", "")).lower() != project_domain:
                errors.append("Creative brief project_domain must match the goal contract")
            if str(creative_brief.get("production_mode", "")).lower() != production_mode:
                errors.append("Creative brief production_mode must match the goal contract")
            if not (target / "compiled-shot.md").is_file():
                errors.append("A locked creative brief requires compiled-shot.md")

            required_common_strings = ("seed_intent", "product_outcome", "north_star")
            for key in required_common_strings:
                if not _non_empty_string(creative_brief.get(key)):
                    errors.append(f"Locked creative brief requires non-empty {key}")
            required_common_lists = (
                "original_user_ideas",
                "preserved_ideas",
                "decisions",
                "bounded_scope",
                "non_goals",
                "must_not_lose",
                "reference_roles",
                "required_evidence",
                "dialogue_event_ids",
            )
            for key in required_common_lists:
                if not _non_empty_list(creative_brief.get(key)):
                    errors.append(f"Locked creative brief requires non-empty {key}")

            selected_ids = creative_brief.get("dialogue_event_ids", [])
            if not isinstance(selected_ids, list):
                selected_ids = []
            missing_dialogue_ids = [str(value) for value in selected_ids if str(value) not in dialogue_by_id]
            if missing_dialogue_ids:
                errors.append(
                    "Creative brief references missing dialogue events: " + ", ".join(missing_dialogue_ids)
                )
            selected_events = [dialogue_by_id[str(value)] for value in selected_ids if str(value) in dialogue_by_id]
            if not any(event.get("actor") == "user" for event in selected_events):
                errors.append("Locked creative brief must reference at least one user dialogue event")
            if not any(event.get("actor") == "model" for event in selected_events):
                errors.append("Locked creative brief must reference at least one model dialogue event")

            authorization = creative_brief.get("authorization", {})
            if not isinstance(authorization, dict):
                errors.append("Locked creative brief requires an authorization object")
            else:
                user_event_id = str(authorization.get("user_event_id", "")).strip()
                event = dialogue_by_id.get(user_event_id)
                if event is None or event.get("actor") != "user" or event.get("kind") not in {
                    "answer",
                    "decision",
                }:
                    errors.append("Locked creative brief authorization must reference a user answer or decision")
                if user_event_id not in {str(value) for value in selected_ids}:
                    errors.append("Creative brief authorization event must be included in dialogue_event_ids")

            if project_domain == "game":
                game = creative_brief.get("game")
                required_game_fields = (
                    "player_promise",
                    "player_role",
                    "core_loop",
                    "world_response",
                    "unique_hook",
                    "art_direction",
                    "game_feel",
                    "hero_moment",
                    "vertical_slice",
                    "asset_strategy",
                )
                if not isinstance(game, dict):
                    errors.append("Locked game brief requires a game object")
                else:
                    for key in required_game_fields:
                        if not _non_empty_string(game.get(key)):
                            errors.append(f"Locked game brief requires non-empty game.{key}")
                    if not isinstance(game.get("performance_budget"), dict) or not game.get(
                        "performance_budget"
                    ):
                        errors.append("Locked game brief requires non-empty game.performance_budget")
            else:
                general = creative_brief.get("general")
                required_general_fields = (
                    "user_job",
                    "primary_flow",
                    "artifact_type",
                    "target_stage",
                    "success_metrics",
                )
                if not isinstance(general, dict):
                    errors.append("Locked general brief requires a general object")
                else:
                    for key in required_general_fields:
                        if not _non_empty_string(general.get(key)):
                            errors.append(f"Locked general brief requires non-empty general.{key}")

            if production_mode == "moonshot":
                moonshot = creative_brief.get("moonshot")
                if not isinstance(moonshot, dict):
                    errors.append("Locked Moonshot brief requires moonshot object")
                else:
                    if not _non_empty_string(moonshot.get("ambition_expansion")):
                        errors.append("Locked Moonshot brief requires moonshot.ambition_expansion")
                    if not _non_empty_string(moonshot.get("scope_guard")):
                        errors.append("Locked Moonshot brief requires moonshot.scope_guard")
                if not _non_empty_list(creative_brief.get("amplifications")):
                    errors.append("Locked Moonshot brief requires at least one explicit amplification")

            try:
                recorded_rounds = int(calibration.get("dialogue_rounds", -1))
            except (TypeError, ValueError):
                recorded_rounds = -1
            if recorded_rounds != dialogue_rounds:
                errors.append("Locked calibration dialogue_rounds must match the dialogue ledger")
        else:
            errors.append("Enabled calibration status must be OPEN or LOCKED")
    else:
        if phase == "CALIBRATE":
            errors.append("Phase CALIBRATE requires calibration.enabled=true")
        if production_mode not in PRODUCTION_MODES:
            errors.append(f"Non-dialogue production_mode must be one of {sorted(PRODUCTION_MODES)}")

    evidence, evidence_errors = read_jsonl(target / "evidence.jsonl")
    defects, defect_errors = read_jsonl(target / "defects.jsonl")
    errors.extend(evidence_errors)
    errors.extend(defect_errors)
    evidence_by_id: dict[str, dict[str, Any]] = {}
    for item in evidence:
        evidence_id = str(item.get("id", "")).strip()
        if not evidence_id:
            errors.append("Every evidence entry requires a non-empty id")
        elif evidence_id in evidence_by_id:
            errors.append(f"Duplicate evidence id: {evidence_id}")
        else:
            evidence_by_id[evidence_id] = item

    try:
        gates = gate_map(acceptance)
    except OneShottedError as exc:
        errors.append(str(exc))
        gates = {}
    policy = acceptance.get("policy", {})
    for gate_id, gate in gates.items():
        gate_status = str(gate.get("status", "PENDING")).upper()
        if gate_status not in VALID_GATE_STATUSES:
            errors.append(f"Gate {gate_id} has invalid status {gate_status!r}")
        owner = str(gate.get("owner", "")).strip()
        verifier = str(gate.get("verifier", "")).strip()
        if not owner or not verifier:
            errors.append(f"Gate {gate_id} requires owner and verifier")
        if policy.get("worker_self_approval_forbidden", True) and owner == verifier:
            errors.append(f"Gate {gate_id} has the same owner and verifier")
        ids = gate.get("evidence_ids", [])
        if not isinstance(ids, list):
            errors.append(f"Gate {gate_id} evidence_ids must be an array")
            ids = []
        missing = [item for item in ids if item not in evidence_by_id]
        if missing:
            errors.append(f"Gate {gate_id} references missing evidence: {', '.join(missing)}")
        if gate_status == "PASS":
            pass_items = [
                evidence_by_id[item]
                for item in ids
                if item in evidence_by_id
                and evidence_by_id[item].get("result") == "PASS"
                and evidence_by_id[item].get("actor") == verifier
                and evidence_by_id[item].get("gate_id") == gate_id
            ]
            if not pass_items:
                errors.append(f"Gate {gate_id} is PASS without verifier-authored PASS evidence")

    defect_state = latest_defects(defects)
    blocking_open = sorted(
        defect_id
        for defect_id, item in defect_state.items()
        if str(item.get("status", "")).upper() == "OPEN"
        and str(item.get("severity", "")).upper() in {"P0", "P1"}
    )
    if blocking_open:
        warnings.append(f"Open P0/P1 defects: {', '.join(blocking_open)}")

    data = {
        "target": target,
        "goal": goal,
        "acceptance": acceptance,
        "state": state,
        "gates": gates,
        "evidence": evidence,
        "defects": defects,
        "blocking_open_defects": blocking_open,
        "creative_brief": creative_brief,
        "dialogue": dialogue,
        "dialogue_rounds": dialogue_rounds,
        "project_domain": project_domain,
        "production_mode": production_mode,
        "calibration_status": calibration_status,
    }
    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "run_dir": str(target),
        "run_id": goal.get("run_id"),
        "status": status,
        "phase": phase,
        "project_domain": project_domain,
        "production_mode": production_mode,
        "calibration_status": calibration_status,
        "dialogue_rounds": dialogue_rounds,
        "gate_count": len(gates),
        "evidence_count": len(evidence),
        "blocking_open_defects": blocking_open,
    }, data
