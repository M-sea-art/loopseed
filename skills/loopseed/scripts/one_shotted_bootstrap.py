"""One-Shotted project control-plane bootstrap."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from one_shotted_io import load_template_json, load_template_text, write_json_atomic
from one_shotted_types import VERSION, OneShottedError, clean_line, new_id, run_dir, utc_now

def initialize(root: Path, goal: str, force: bool = False) -> dict[str, Any]:
    root_goal = clean_line(goal, name="root goal")
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

    goal_contract = load_template_json("goal-contract.json")
    goal_contract.update(
        {
            "loopseed_version": VERSION,
            "mode": "one-shotted",
            "run_id": run_id,
            "root_goal": root_goal,
            "terminal_goal": root_goal,
            "created_at": created_at,
        }
    )
    goal_contract.setdefault("authority", {})["user_instruction"] = root_goal

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
            "phase": "BIND",
            "round": 0,
            "no_progress_rounds": 0,
            "next_action": "Inspect project authority and define observable acceptance gates before implementation.",
            "updated_at": created_at,
        }
    )

    write_json_atomic(target / "goal-contract.json", goal_contract)
    write_json_atomic(target / "acceptance.json", acceptance)
    write_json_atomic(target / "expert-registry.json", experts)
    write_json_atomic(target / "state.json", state)
    (target / "project-identity.md").write_text(
        load_template_text("project-identity.md").replace("{{ROOT_GOAL}}", root_goal),
        encoding="utf-8",
    )
    (target / "architecture-contract.md").write_text(
        load_template_text("architecture-contract.md"), encoding="utf-8"
    )
    (target / "evidence.jsonl").write_text("", encoding="utf-8")
    (target / "defects.jsonl").write_text("", encoding="utf-8")

    return {
        "ok": True,
        "run_id": run_id,
        "mode": "one-shotted",
        "run_dir": str(target),
        "status": "ACTIVE",
        "phase": "BIND",
        "next_action": state["next_action"],
    }

