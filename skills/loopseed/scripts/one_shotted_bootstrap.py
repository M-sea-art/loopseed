"""One-Shotted project control-plane bootstrap."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from one_shotted_calibration import (
    MODE_OPTIONS,
    normalize_domain,
    resolve_dialogue_enabled,
    resolve_initial_mode,
    validate_max_rounds,
)
from one_shotted_io import load_template_json, load_template_text, write_json_atomic
from one_shotted_types import VERSION, OneShottedError, clean_line, new_id, run_dir, utc_now


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
    root_goal = clean_line(goal, name="root goal")
    project_domain = normalize_domain(root_goal, domain)
    dialogue_enabled = resolve_dialogue_enabled(project_domain, dialogue, production_mode)
    selected_mode = resolve_initial_mode(project_domain, production_mode, dialogue_enabled)
    maximum_rounds = validate_max_rounds(max_dialogue_rounds)

    target = run_dir(root)
    if target.exists() and any(target.iterdir()):
        if not force:
            raise OneShottedError(
                f"One-Shotted state already exists at {target}; use --force only to replace it"
            )
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)

    created_at = utc_now()
    run_id = new_id("RUN")
    phase = "CALIBRATE" if dialogue_enabled else "BIND"
    calibration_status = "OPEN" if dialogue_enabled else "SKIPPED"
    next_action = (
        "Begin creative co-director dialogue. Preserve the user's seed, improve or extend it, offer 2-4 meaningful options with a recommendation, and lock the brief when all material choices are resolved."
        if dialogue_enabled
        else "Inspect project authority and define observable acceptance gates before implementation."
    )

    goal_contract = load_template_json("goal-contract.json")
    goal_contract.update(
        {
            "loopseed_version": VERSION,
            "mode": "one-shotted",
            "run_id": run_id,
            "root_goal": root_goal,
            "terminal_goal": root_goal,
            "project_domain": project_domain,
            "production_mode": selected_mode,
            "created_at": created_at,
        }
    )
    goal_contract.setdefault("authority", {})["user_instruction"] = root_goal
    goal_contract["calibration"] = {
        "enabled": dialogue_enabled,
        "status": calibration_status,
        "policy": "game-first-creative-co-director",
        "max_rounds": maximum_rounds,
        "dialogue_rounds": 0,
        "brief_id": None,
        "locked_at": None,
    }

    acceptance = load_template_json("acceptance.json")
    acceptance["run_id"] = run_id
    experts = load_template_json("expert-registry.json")
    experts["run_id"] = run_id
    state = load_template_json("state.json")
    state.update(
        {
            "loopseed_version": VERSION,
            "mode": "one-shotted",
            "run_id": run_id,
            "status": "ACTIVE",
            "phase": phase,
            "round": 0,
            "dialogue_rounds": 0,
            "no_progress_rounds": 0,
            "next_action": next_action,
            "updated_at": created_at,
        }
    )

    creative_brief = load_template_json("creative-brief.json")
    creative_brief.update(
        {
            "loopseed_version": VERSION,
            "run_id": run_id,
            "status": "DRAFT" if dialogue_enabled else "SKIPPED",
            "project_domain": project_domain,
            "production_mode": selected_mode,
            "seed_intent": root_goal,
        }
    )

    write_json_atomic(target / "goal-contract.json", goal_contract)
    write_json_atomic(target / "acceptance.json", acceptance)
    write_json_atomic(target / "expert-registry.json", experts)
    write_json_atomic(target / "state.json", state)
    write_json_atomic(target / "creative-brief.json", creative_brief)
    (target / "project-identity.md").write_text(
        load_template_text("project-identity.md")
        .replace("{{ROOT_GOAL}}", root_goal)
        .replace("{{PROJECT_DOMAIN}}", project_domain)
        .replace("{{PRODUCTION_MODE}}", selected_mode),
        encoding="utf-8",
    )
    (target / "architecture-contract.md").write_text(
        load_template_text("architecture-contract.md"), encoding="utf-8"
    )
    (target / "dialogue.jsonl").write_text("", encoding="utf-8")
    (target / "evidence.jsonl").write_text("", encoding="utf-8")
    (target / "defects.jsonl").write_text("", encoding="utf-8")

    return {
        "ok": True,
        "run_id": run_id,
        "mode": "one-shotted",
        "project_domain": project_domain,
        "production_mode": selected_mode,
        "calibration_status": calibration_status,
        "suggested_modes": MODE_OPTIONS,
        "run_dir": str(target),
        "status": "ACTIVE",
        "phase": phase,
        "next_action": next_action,
    }
