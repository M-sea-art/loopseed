"""Creative co-director dialogue and compiled-shot locking for One-Shotted mode."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from one_shotted_io import (
    append_jsonl,
    load_run,
    locked_mutation,
    read_json,
    read_jsonl,
    write_json_atomic,
)
from one_shotted_types import (
    DIALOGUE_EFFECTS,
    DIALOGUE_KINDS,
    PRODUCTION_MODES,
    PROJECT_DOMAINS,
    VERSION,
    OneShottedError,
    clean_line,
    new_id,
    utc_now,
)

GAME_SIGNALS = (
    "game",
    "gameplay",
    "player",
    "level",
    "roguelike",
    "rpg",
    "fps",
    "godot",
    "unity",
    "unreal",
    "three.js",
    "threejs",
    "phaser",
    "steam",
    "游戏",
    "小游戏",
    "玩家",
    "可玩",
    "关卡",
    "战斗",
    "肉鸽",
    "门派",
    "游戏感",
)

MODE_OPTIONS = {
    "focused": {
        "label": "Focused",
        "purpose": "Deliver the smallest complete result quickly without expanding the product idea.",
    },
    "studio": {
        "label": "Studio",
        "purpose": "Build a coherent, presentation-ready vertical slice with game feel, art direction, and production evidence.",
    },
    "moonshot": {
        "label": "Moonshot",
        "purpose": "Deliberately amplify the strongest experience and organize aggressive but bounded production fan-out.",
    },
}


def detect_domain(goal: str) -> str:
    normalized = goal.casefold()
    return "game" if any(signal in normalized for signal in GAME_SIGNALS) else "general"


def resolve_dialogue_enabled(project_domain: str, dialogue: str, production_mode: str) -> bool:
    value = dialogue.strip().lower()
    if value not in {"auto", "on", "off"}:
        raise OneShottedError("dialogue must be one of: auto, on, off")
    if value == "on":
        return True
    if value == "off":
        return False
    return project_domain == "game" or production_mode.strip().lower() == "moonshot"


def resolve_initial_mode(project_domain: str, production_mode: str, dialogue_enabled: bool) -> str:
    value = production_mode.strip().lower()
    if value == "auto":
        if dialogue_enabled:
            return "undecided"
        return "studio" if project_domain == "game" else "focused"
    if value not in PRODUCTION_MODES:
        raise OneShottedError(f"production mode must be one of: auto, {', '.join(sorted(PRODUCTION_MODES))}")
    return value


def normalize_domain(goal: str, domain: str) -> str:
    value = domain.strip().lower()
    if value == "auto":
        return detect_domain(goal)
    if value not in PROJECT_DOMAINS:
        raise OneShottedError(f"project domain must be one of: auto, {', '.join(sorted(PROJECT_DOMAINS))}")
    return value


def validate_max_rounds(value: int) -> int:
    if not 1 <= int(value) <= 8:
        raise OneShottedError("max dialogue rounds must be between 1 and 8")
    return int(value)


def _clean_values(values: Iterable[str] | None, *, name: str) -> list[str]:
    cleaned: list[str] = []
    for value in values or []:
        item = clean_line(value, name=name)
        if item not in cleaned:
            cleaned.append(item)
    return cleaned


def _parse_options(values: Iterable[str] | None) -> list[dict[str, str]]:
    options: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw in values or []:
        parts = [part.strip() for part in str(raw).split("|", 2)]
        if len(parts) != 3 or not all(parts):
            raise OneShottedError(
                "Each option must use 'ID|label|consequence', for example A|Studio|Build a polished vertical slice"
            )
        option_id = clean_line(parts[0], name="option id")
        if option_id in seen:
            raise OneShottedError(f"Duplicate dialogue option id: {option_id}")
        seen.add(option_id)
        options.append(
            {
                "id": option_id,
                "label": clean_line(parts[1], name="option label"),
                "consequence": clean_line(parts[2], name="option consequence"),
            }
        )
    return options


@locked_mutation
def record_dialogue_turn(
    root: Path,
    actor: str,
    kind: str,
    summary: str,
    *,
    effects: Iterable[str] | None = None,
    advances: Iterable[str] | None = None,
    options: Iterable[str] | None = None,
    recommended: str | None = None,
) -> dict[str, Any]:
    target, goal, _, state = load_run(root)
    calibration = goal.get("calibration", {})
    if not isinstance(calibration, dict) or not calibration.get("enabled", False):
        raise OneShottedError("This run did not enable creative dialogue")
    if str(calibration.get("status", "")).upper() != "OPEN":
        raise OneShottedError("Creative dialogue is already locked or skipped")
    if str(state.get("status", "")).upper() != "ACTIVE" or str(state.get("phase", "")).upper() != "CALIBRATE":
        raise OneShottedError("Dialogue turns may only be recorded during ACTIVE/CALIBRATE")

    actor_value = actor.strip().lower()
    kind_value = kind.strip().lower()
    if actor_value not in {"user", "model"}:
        raise OneShottedError("dialogue actor must be user or model")
    if kind_value not in DIALOGUE_KINDS:
        raise OneShottedError(f"dialogue kind must be one of {sorted(DIALOGUE_KINDS)}")
    if actor_value == "user" and kind_value not in {"seed", "answer", "decision"}:
        raise OneShottedError("User dialogue turns must be seed, answer, or decision")
    if actor_value == "model" and kind_value not in {"synthesis", "question"}:
        raise OneShottedError("Model dialogue turns must be synthesis or question")

    summary_value = clean_line(summary, name="dialogue summary")
    effects_value = _clean_values(effects, name="dialogue effect")
    invalid_effects = sorted(set(effects_value) - DIALOGUE_EFFECTS)
    if invalid_effects:
        raise OneShottedError(f"Unknown dialogue effects: {', '.join(invalid_effects)}")
    advances_value = _clean_values(advances, name="advanced decision surface")
    option_values = _parse_options(options)

    events, errors = read_jsonl(target / "dialogue.jsonl")
    if errors:
        raise OneShottedError("Cannot append to invalid dialogue ledger: " + "; ".join(errors))
    question_count = sum(
        1 for event in events if event.get("actor") == "model" and event.get("kind") == "question"
    )

    if actor_value == "model":
        if not effects_value:
            raise OneShottedError(
                "Model dialogue turns must declare at least one effect: preserve, clarify, correct, amplify, complete, continue, or offer_options"
            )
        if not advances_value:
            raise OneShottedError("Model dialogue turns must advance at least one material decision surface")

    recommendation: str | None = None
    if kind_value == "question":
        if len(option_values) < 2 or len(option_values) > 4:
            raise OneShottedError("A model question must offer between 2 and 4 meaningful options")
        recommendation = clean_line(recommended or "", name="recommended option")
        option_ids = {item["id"] for item in option_values}
        if recommendation not in option_ids:
            raise OneShottedError("The recommended option must match one offered option id")
        if "offer_options" not in effects_value:
            effects_value.append("offer_options")
        maximum = int(calibration.get("max_rounds", 5))
        if question_count >= maximum:
            raise OneShottedError(
                "Dialogue round limit reached; synthesize the strongest recommendation and lock the brief instead of asking another question"
            )
        fingerprint = json.dumps(
            {"summary": summary_value.casefold(), "advances": sorted(advances_value)},
            ensure_ascii=False,
            sort_keys=True,
        )
        for event in events:
            if event.get("kind") != "question":
                continue
            prior = json.dumps(
                {
                    "summary": str(event.get("summary", "")).casefold(),
                    "advances": sorted(event.get("advances", [])),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
            if prior == fingerprint:
                raise OneShottedError("Do not repeat the same creative question; advance or lock the shot")
    elif option_values or recommended:
        raise OneShottedError("Options and recommendations are only valid for model question turns")

    event_id = new_id("DIALOGUE")
    round_number = question_count + (1 if kind_value == "question" else 0)
    event: dict[str, Any] = {
        "id": event_id,
        "run_id": goal.get("run_id"),
        "actor": actor_value,
        "kind": kind_value,
        "round": round_number,
        "summary": summary_value,
        "effects": effects_value,
        "advances": advances_value,
        "created_at": utc_now(),
    }
    if option_values:
        event["options"] = option_values
        event["recommended"] = recommendation
    append_jsonl(target / "dialogue.jsonl", event)

    state["dialogue_rounds"] = round_number
    state["updated_at"] = utc_now()
    if kind_value == "question":
        state["next_action"] = "Await the user's choice or synthesis; preserve accepted ideas and continue from them."
    elif actor_value == "user":
        state["next_action"] = (
            "Synthesize the user's answer, improve or extend the idea, and ask another option-rich question only if a material decision remains."
        )
    else:
        state["next_action"] = "Lock the creative brief when all readiness conditions are resolved; otherwise advance one material choice."
    write_json_atomic(target / "state.json", state)

    return {
        "ok": True,
        "event_id": event_id,
        "actor": actor_value,
        "kind": kind_value,
        "round": round_number,
        "dialogue_status": "OPEN",
        "next_action": state["next_action"],
    }


def _require_text(container: dict[str, Any], key: str, *, context: str) -> str:
    value = clean_line(str(container.get(key, "")), name=f"{context}.{key}")
    container[key] = value
    return value


def _require_list(container: dict[str, Any], key: str, *, context: str) -> list[Any]:
    value = container.get(key)
    if not isinstance(value, list) or not value:
        raise OneShottedError(f"{context}.{key} must be a non-empty array")
    return value


def _render_list(values: list[Any]) -> str:
    return "\n".join(f"- {str(value)}" for value in values)


def _render_compiled_shot(brief: dict[str, Any]) -> str:
    lines = [
        "# LOOPSEED Compiled Shot",
        "",
        f"- Brief ID: `{brief['brief_id']}`",
        f"- Domain: `{brief['project_domain']}`",
        f"- Production mode: `{brief['production_mode']}`",
        "",
        "## Seed intent",
        "",
        brief["seed_intent"],
        "",
        "## Product outcome",
        "",
        brief["product_outcome"],
        "",
        "## North star",
        "",
        brief["north_star"],
        "",
        "## Must not lose",
        "",
        _render_list(brief["must_not_lose"]),
        "",
        "## Bounded scope",
        "",
        _render_list(brief["bounded_scope"]),
        "",
        "## Non-goals",
        "",
        _render_list(brief["non_goals"]),
    ]
    if brief["project_domain"] == "game":
        game = brief["game"]
        lines += [
            "",
            "## Game contract",
            "",
            f"- Player promise: {game['player_promise']}",
            f"- Player role: {game['player_role']}",
            f"- Core loop: {game['core_loop']}",
            f"- World response: {game['world_response']}",
            f"- Unique hook: {game['unique_hook']}",
            f"- Art direction: {game['art_direction']}",
            f"- Game feel: {game['game_feel']}",
            f"- Hero moment: {game['hero_moment']}",
            f"- Vertical slice: {game['vertical_slice']}",
            f"- Asset strategy: {game['asset_strategy']}",
            f"- Performance budget: {json.dumps(game['performance_budget'], ensure_ascii=False, sort_keys=True)}",
        ]
    else:
        general = brief["general"]
        lines += [
            "",
            "## Product contract",
            "",
            f"- User job: {general['user_job']}",
            f"- Primary flow: {general['primary_flow']}",
            f"- Artifact type: {general['artifact_type']}",
            f"- Target stage: {general['target_stage']}",
            f"- Success metrics: {general['success_metrics']}",
        ]
    if brief["production_mode"] == "moonshot":
        moonshot = brief["moonshot"]
        lines += [
            "",
            "## Moonshot expansion",
            "",
            moonshot["ambition_expansion"],
            "",
            "### Scope guard",
            "",
            moonshot["scope_guard"],
        ]
    lines += [
        "",
        "## Decisions",
        "",
        _render_list(brief["decisions"]),
        "",
        "## Required evidence",
        "",
        _render_list(brief["required_evidence"]),
        "",
        "After this lock, production proceeds without repeated confirmation. Fan-out may accelerate independent work, but no worker may rewrite this shot.",
    ]
    return "\n".join(lines) + "\n"


@locked_mutation
def lock_creative_brief(
    root: Path,
    brief: dict[str, Any],
    *,
    actor: str = "lead",
) -> dict[str, Any]:
    target, goal, _, state = load_run(root)
    calibration = goal.get("calibration", {})
    if not isinstance(calibration, dict) or not calibration.get("enabled", False):
        raise OneShottedError("This run does not require a creative brief lock")
    if str(calibration.get("status", "")).upper() != "OPEN":
        raise OneShottedError("Creative brief is already locked or skipped")
    if str(state.get("status", "")).upper() != "ACTIVE" or str(state.get("phase", "")).upper() != "CALIBRATE":
        raise OneShottedError("Creative brief may only be locked during ACTIVE/CALIBRATE")
    if not isinstance(brief, dict):
        raise OneShottedError("creative brief must be a JSON object")

    project_domain = str(brief.get("project_domain", "")).strip().lower()
    expected_domain = str(goal.get("project_domain", "")).strip().lower()
    if project_domain not in PROJECT_DOMAINS:
        raise OneShottedError(f"creative brief project_domain must be one of {sorted(PROJECT_DOMAINS)}")
    if project_domain != expected_domain:
        raise OneShottedError(
            f"creative brief domain {project_domain!r} does not match initialized domain {expected_domain!r}"
        )
    production_mode = str(brief.get("production_mode", "")).strip().lower()
    if production_mode not in PRODUCTION_MODES:
        raise OneShottedError(f"creative brief production_mode must be one of {sorted(PRODUCTION_MODES)}")

    for key in ("seed_intent", "product_outcome", "north_star"):
        _require_text(brief, key, context="creative_brief")
    for key in (
        "original_user_ideas",
        "preserved_ideas",
        "decisions",
        "bounded_scope",
        "non_goals",
        "must_not_lose",
        "reference_roles",
        "required_evidence",
        "dialogue_event_ids",
    ):
        _require_list(brief, key, context="creative_brief")
    for key in ("revisions", "amplifications"):
        value = brief.get(key, [])
        if not isinstance(value, list):
            raise OneShottedError(f"creative_brief.{key} must be an array")

    if project_domain == "game":
        game = brief.get("game")
        if not isinstance(game, dict):
            raise OneShottedError("creative_brief.game must be an object for game projects")
        for key in (
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
        ):
            _require_text(game, key, context="creative_brief.game")
        budget = game.get("performance_budget")
        if not isinstance(budget, dict) or not budget:
            raise OneShottedError("creative_brief.game.performance_budget must be a non-empty object")
    else:
        general = brief.get("general")
        if not isinstance(general, dict):
            raise OneShottedError("creative_brief.general must be an object for general projects")
        for key in ("user_job", "primary_flow", "artifact_type", "target_stage", "success_metrics"):
            _require_text(general, key, context="creative_brief.general")

    if production_mode == "moonshot":
        moonshot = brief.get("moonshot")
        if not isinstance(moonshot, dict):
            raise OneShottedError("Moonshot mode requires creative_brief.moonshot")
        _require_text(moonshot, "ambition_expansion", context="creative_brief.moonshot")
        _require_text(moonshot, "scope_guard", context="creative_brief.moonshot")
        if not brief.get("amplifications"):
            raise OneShottedError("Moonshot mode requires at least one explicit amplification of the user's idea")

    dialogue, errors = read_jsonl(target / "dialogue.jsonl")
    if errors:
        raise OneShottedError("Cannot lock against an invalid dialogue ledger: " + "; ".join(errors))
    events = {str(event.get("id", "")): event for event in dialogue if str(event.get("id", ""))}
    selected_ids = [str(value) for value in brief["dialogue_event_ids"]]
    missing_ids = [event_id for event_id in selected_ids if event_id not in events]
    if missing_ids:
        raise OneShottedError("creative brief references missing dialogue events: " + ", ".join(missing_ids))
    selected_events = [events[event_id] for event_id in selected_ids]
    if not any(event.get("actor") == "model" for event in selected_events):
        raise OneShottedError("creative brief must reference at least one model synthesis or option turn")
    if not any(event.get("actor") == "user" for event in selected_events):
        raise OneShottedError("creative brief must reference at least one user turn")

    authorization = brief.get("authorization")
    if not isinstance(authorization, dict):
        raise OneShottedError("creative_brief.authorization must be an object")
    user_event_id = clean_line(str(authorization.get("user_event_id", "")), name="authorization user_event_id")
    event = events.get(user_event_id)
    if event is None or event.get("actor") != "user" or event.get("kind") not in {"answer", "decision"}:
        raise OneShottedError("Authorization must reference a user answer or decision event")
    if user_event_id not in selected_ids:
        raise OneShottedError("Authorization event must be included in dialogue_event_ids")
    authorization["authorized_by"] = "user"
    authorization["locked_by"] = clean_line(actor, name="brief locking actor")

    locked_at = utc_now()
    stored_brief = read_json(target / "creative-brief.json")
    brief["schema_version"] = stored_brief.get("schema_version", "1.0")
    brief["loopseed_version"] = goal.get("loopseed_version", VERSION)
    brief["run_id"] = goal.get("run_id")
    brief["project_domain"] = project_domain
    brief["production_mode"] = production_mode
    brief["status"] = "LOCKED"
    brief["locked_at"] = locked_at
    brief.pop("brief_id", None)
    canonical = json.dumps(brief, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    brief_id = "BRIEF-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    brief["brief_id"] = brief_id

    write_json_atomic(target / "creative-brief.json", brief)
    (target / "compiled-shot.md").write_text(_render_compiled_shot(brief), encoding="utf-8")

    calibration.update(
        {
            "status": "LOCKED",
            "brief_id": brief_id,
            "locked_at": locked_at,
            "dialogue_rounds": int(state.get("dialogue_rounds", 0)),
        }
    )
    goal["production_mode"] = production_mode
    goal["terminal_goal"] = brief["product_outcome"]
    goal["compiled_shot"] = {
        "brief_id": brief_id,
        "path": ".loopseed/one-shotted/compiled-shot.md",
        "seed_intent_preserved": True,
    }
    state.update(
        {
            "phase": "BIND",
            "next_action": (
                "Freeze Project Binding, Artifact Contract, and Stage Target from the locked compiled shot, then plan one uninterrupted production run."
            ),
            "updated_at": locked_at,
        }
    )
    write_json_atomic(target / "goal-contract.json", goal)
    write_json_atomic(target / "state.json", state)
    return {
        "ok": True,
        "brief_id": brief_id,
        "project_domain": project_domain,
        "production_mode": production_mode,
        "dialogue_rounds": calibration["dialogue_rounds"],
        "phase": "BIND",
        "compiled_shot": str(target / "compiled-shot.md"),
        "next_action": state["next_action"],
    }


def lock_creative_brief_file(root: Path, path: Path, *, actor: str = "lead") -> dict[str, Any]:
    return lock_creative_brief(root, read_json(path), actor=actor)
