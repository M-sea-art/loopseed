"""Consistency audit for One-Shotted contracts, evidence, dialogue, and defects."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from one_shotted_evidence import ARTIFACT_PRODUCER
from one_shotted_integrity import (
    artifact_identity,
    artifact_subject,
    assert_binding_current,
    binding_subject,
)
from one_shotted_io import current_artifact_evidence_paths, read_json, read_jsonl
from one_shotted_model import gate_map, latest_defects
from one_shotted_runner import PRODUCER
from one_shotted_tasks import scheduler_snapshot, task_graph_errors
from one_shotted_types import (
    CALIBRATION_FILES,
    DIALOGUE_EFFECTS,
    DIALOGUE_KINDS,
    PRODUCTION_MODES,
    PROJECT_DOMAINS,
    REQUIRED_FILES,
    SCHEDULER_FILE,
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


def _version_at_least_0_7(value: Any) -> bool:
    try:
        major, minor, *_ = (int(part) for part in str(value).split("."))
    except (TypeError, ValueError):
        return False
    return (major, minor) >= (0, 7)


def _version_at_least_0_7_1(value: Any) -> bool:
    try:
        parts = [int(part) for part in str(value).split(".")]
    except (TypeError, ValueError):
        return False
    return tuple((parts + [0, 0, 0])[:3]) >= (0, 7, 1)


def _machine_errors(item: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    evidence_id = str(item.get("id", "<unknown>"))
    required = (
        "producer",
        "summary",
        "command",
        "cwd",
        "started_at",
        "finished_at",
        "created_at",
        "exit_code",
        "timed_out",
        "stdout_summary",
        "stderr_summary",
        "project_id",
        "candidate_commit",
        "actual_candidate_commit",
        "binding_id",
        "generation",
        "expected_artifact",
        "artifact_before",
        "artifact_after",
        "evidence_artifacts_before",
        "evidence_artifacts_after",
        "evidence_artifacts_stable",
        "integrity_stable",
        "integrity_failure_reason",
        "git_repository_detected",
        "tracked_worktree_dirty_before",
        "tracked_worktree_dirty_after",
        "unexpected_untracked_before",
        "unexpected_untracked_after",
    )
    nullable_required = {
        "actual_candidate_commit",
        "tracked_worktree_dirty_after",
        "integrity_failure_reason",
    }
    for field in required:
        if field not in item or (
            field not in {"stdout_summary", "stderr_summary", *nullable_required}
            and item.get(field) in (None, "")
        ):
            errors.append(f"Machine evidence {evidence_id} is missing {field}")
    if item.get("producer") != PRODUCER:
        errors.append(f"Machine evidence {evidence_id} has an unknown producer")
    if item.get("git_repository_detected") is not True:
        errors.append(f"Machine evidence {evidence_id} must come from a real Git worktree")
    if not isinstance(item.get("timed_out"), bool):
        errors.append(f"Machine evidence {evidence_id} has invalid timed_out")
    if item.get("tracked_worktree_dirty_before") is not False:
        errors.append(
            f"Machine evidence {evidence_id} must start from clean tracked Git content"
        )
    if item.get("tracked_worktree_dirty_after") is not None and not isinstance(
        item.get("tracked_worktree_dirty_after"), bool
    ):
        errors.append(
            f"Machine evidence {evidence_id} has invalid tracked_worktree_dirty_after"
        )
    if item.get("unexpected_untracked_before") != []:
        errors.append(f"Machine evidence {evidence_id} must start without unbound untracked content")
    unexpected_after = item.get("unexpected_untracked_after")
    if not isinstance(unexpected_after, list) or any(
        not _non_empty_string(value) for value in unexpected_after
    ):
        errors.append(f"Machine evidence {evidence_id} has invalid unexpected_untracked_after")
        unexpected_after = ["<invalid>"]

    exit_code = item.get("exit_code")
    if not isinstance(exit_code, int) or isinstance(exit_code, bool):
        errors.append(f"Machine evidence {evidence_id} has invalid exit_code")
        exit_code = -1
    expected = artifact_subject(item.get("expected_artifact"))
    before = artifact_subject(item.get("artifact_before"))
    after_raw = item.get("artifact_after")
    after = artifact_subject(after_raw)
    after_missing = (
        isinstance(after_raw, dict)
        and after_raw.get("kind") == "missing"
        and not str(after_raw.get("sha256", ""))
    )
    if expected is None:
        errors.append(f"Machine evidence {evidence_id} requires expected_artifact identity")
    if before is None:
        errors.append(f"Machine evidence {evidence_id} requires artifact_before identity")
    if after is None and not after_missing:
        errors.append(f"Machine evidence {evidence_id} has invalid artifact_after identity")

    evidence_before_raw = item.get("evidence_artifacts_before")
    evidence_after_raw = item.get("evidence_artifacts_after")
    if not isinstance(evidence_before_raw, list):
        errors.append(f"Machine evidence {evidence_id} has invalid evidence_artifacts_before")
        evidence_before_raw = []
    if not isinstance(evidence_after_raw, list):
        errors.append(f"Machine evidence {evidence_id} has invalid evidence_artifacts_after")
        evidence_after_raw = []
    evidence_before = [artifact_subject(value) for value in evidence_before_raw]
    evidence_after = [artifact_subject(value) for value in evidence_after_raw]
    evidence_artifacts_stable = (
        len(evidence_before) == len(evidence_after)
        and all(value is not None for value in evidence_before)
        and evidence_before == evidence_after
    )
    if item.get("evidence_artifacts_stable") != evidence_artifacts_stable:
        errors.append(
            f"Machine evidence {evidence_id} evidence_artifacts_stable is inconsistent"
        )

    artifact_stable = expected is not None and expected == before == after
    candidate = str(item.get("candidate_commit", ""))
    actual = str(item.get("actual_candidate_commit", ""))
    head_stable = bool(candidate) and actual == candidate
    tracked_worktree_stable = (
        item.get("tracked_worktree_dirty_before") is False
        and item.get("tracked_worktree_dirty_after") is False
    )
    untracked_stable = not unexpected_after
    calculated_integrity = (
        artifact_stable
        and evidence_artifacts_stable
        and head_stable
        and tracked_worktree_stable
        and untracked_stable
    )
    if item.get("integrity_stable") != calculated_integrity:
        errors.append(f"Machine evidence {evidence_id} integrity_stable is inconsistent")
    failure_reason = str(item.get("integrity_failure_reason") or "")
    expected_failure_reason = ""
    if not artifact_stable:
        expected_failure_reason = (
            "ARTIFACT_MISSING_AFTER_VERIFICATION"
            if after_missing
            else "ARTIFACT_MUTATED_DURING_VERIFICATION"
        )
    elif not evidence_artifacts_stable:
        expected_failure_reason = "EVIDENCE_ARTIFACT_MUTATED_DURING_VERIFICATION"
    elif not head_stable:
        expected_failure_reason = "CANDIDATE_COMMIT_CHANGED_DURING_VERIFICATION"
    elif not tracked_worktree_stable:
        expected_failure_reason = "TRACKED_WORKTREE_CHANGED_DURING_VERIFICATION"
    elif not untracked_stable:
        expected_failure_reason = "UNTRACKED_CONTENT_CHANGED_DURING_VERIFICATION"
    if failure_reason != expected_failure_reason:
        errors.append(f"Machine evidence {evidence_id} has an inconsistent integrity failure reason")
    expected_result = (
        "PASS"
        if exit_code == 0 and item.get("timed_out") is False and calculated_integrity
        else "FAIL"
    )
    if item.get("result") != expected_result:
        errors.append(
            f"Machine evidence {evidence_id} result does not match command, timeout, and integrity outcome"
        )
    return errors


def _artifact_evidence_errors(item: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    evidence_id = str(item.get("id", "<unknown>"))
    if item.get("producer") != ARTIFACT_PRODUCER:
        errors.append(f"Artifact evidence {evidence_id} has an unknown producer")
    artifacts = item.get("artifacts")
    if not isinstance(artifacts, list):
        return errors + [f"Artifact evidence {evidence_id} artifacts must be an array"]
    if item.get("result") == "PASS" and not artifacts:
        errors.append(f"Artifact evidence {evidence_id} PASS requires a hashed artifact")
    for artifact in artifacts:
        subject = artifact_subject(artifact)
        if subject is None:
            errors.append(f"Artifact evidence {evidence_id} contains an invalid artifact identity")
            continue
    return errors


def _current_artifact_evidence_errors(root: Path, item: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    evidence_id = str(item.get("id", "<unknown>"))
    for artifact in item.get("artifacts", []):
        subject = artifact_subject(artifact)
        if subject is None:
            continue
        try:
            current = artifact_identity(root, subject[0])
        except OneShottedError as exc:
            errors.append(str(exc))
        else:
            if artifact_subject(current) != subject:
                errors.append(f"Artifact evidence {evidence_id} is stale after artifact drift")
    return errors


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
    if goal.get("loopseed_version") != state.get("loopseed_version"):
        errors.append("Goal contract and state must share the LoopSeed version")

    # v0.7 introduced the current control-plane shape. Any v0.7 PASS created
    # before the Integrity Bridge is legacy/unattested and must be rerun.
    verification_binding = state.get("verification_binding")
    strict_integrity = _version_at_least_0_7(
        goal.get("loopseed_version")
    ) or verification_binding is not None
    binding_identity = binding_subject(verification_binding)
    if verification_binding is not None:
        if binding_identity is None:
            errors.append(
                "verification_binding requires project, candidate commit, and artifact identity"
            )
        else:
            if not str(verification_binding.get("binding_id", "")).strip():
                errors.append("verification_binding requires binding_id")
            generation = verification_binding.get("generation")
            if not isinstance(generation, int) or isinstance(generation, bool) or generation < 1:
                errors.append("verification_binding generation must be a positive integer")
            if verification_binding.get("git_repository_detected") is not True:
                errors.append("verification_binding requires a real Git worktree")
            try:
                allowed_untracked = current_artifact_evidence_paths(
                    target, acceptance, verification_binding
                )
                assert_binding_current(
                    root,
                    verification_binding,
                    allowed_untracked=allowed_untracked,
                )
            except OneShottedError as exc:
                errors.append(str(exc))
    history = state.get("verification_history", [])
    if not isinstance(history, list):
        errors.append("state.verification_history must be an array")
        history = []
    binding_lineage: dict[tuple[str, int], dict[str, Any]] = {}
    lineage_entries = [*history]
    if isinstance(verification_binding, dict):
        lineage_entries.append(verification_binding)
    lineage_generations: list[int] = []
    for index, receipt in enumerate(lineage_entries):
        label = "verification_binding" if receipt is verification_binding else f"verification_history[{index}]"
        subject = binding_subject(receipt)
        binding_id = str(receipt.get("binding_id", "")).strip() if isinstance(receipt, dict) else ""
        generation = receipt.get("generation") if isinstance(receipt, dict) else None
        if subject is None or not binding_id:
            errors.append(f"{label} requires a complete binding identity")
            continue
        if not isinstance(generation, int) or isinstance(generation, bool) or generation < 1:
            errors.append(f"{label} generation must be a positive integer")
            continue
        if not _non_empty_string(receipt.get("bound_at")):
            errors.append(f"{label} requires bound_at")
        ledger_count = receipt.get("evidence_ledger_count")
        if (
            not isinstance(ledger_count, int)
            or isinstance(ledger_count, bool)
            or ledger_count < 0
        ):
            errors.append(f"{label} evidence_ledger_count must be a non-negative integer")
        if receipt.get("git_repository_detected") is not True:
            errors.append(f"{label} requires a real Git worktree receipt")
        if str(receipt.get("actual_candidate_commit", "")) != subject[1]:
            errors.append(f"{label} actual_candidate_commit must match candidate_commit")
        if receipt.get("tracked_worktree_dirty") is not False:
            errors.append(f"{label} must have clean tracked Git content at bind time")
        key = (binding_id, generation)
        if key in binding_lineage:
            errors.append(f"Duplicate verification binding receipt: {binding_id}/{generation}")
        else:
            binding_lineage[key] = receipt
            lineage_generations.append(generation)
    if isinstance(verification_binding, dict):
        current_generation_value = verification_binding.get("generation")
        if isinstance(current_generation_value, int) and not isinstance(
            current_generation_value, bool
        ):
            expected_generations = list(range(1, current_generation_value + 1))
            if sorted(lineage_generations) != expected_generations:
                errors.append(
                    "Verification binding history must contain every prior generation exactly once"
                )
        lineage_counts = [
            receipt.get("evidence_ledger_count")
            for receipt in sorted(
                binding_lineage.values(), key=lambda item: int(item.get("generation", 0))
            )
        ]
        if all(isinstance(value, int) and not isinstance(value, bool) for value in lineage_counts):
            if lineage_counts != sorted(lineage_counts):
                errors.append("Verification binding ledger boundaries must be monotonic")

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

    task_graph: dict[str, Any] = {}
    scheduler: dict[str, Any] = {}
    task_graph_path = target / SCHEDULER_FILE
    if task_graph_path.is_file():
        try:
            task_graph = read_json(task_graph_path)
        except OneShottedError as exc:
            errors.append(str(exc))
        if task_graph:
            graph_errors = task_graph_errors(task_graph, str(goal.get("run_id", "")))
            errors.extend(graph_errors)
            if task_graph.get("loopseed_version") != goal.get("loopseed_version"):
                errors.append("Task graph and goal contract must share the LoopSeed version")
            if not graph_errors:
                scheduler = scheduler_snapshot(task_graph)
    elif strict_integrity:
        errors.append(f"Missing required file: {task_graph_path}")

    scheduler_wait = state.get("scheduler_wait")
    if scheduler_wait is not None:
        if not isinstance(scheduler_wait, dict):
            errors.append("state.scheduler_wait must be an object or null")
        else:
            wait_ids = scheduler_wait.get("task_ids")
            if not isinstance(wait_ids, list) or not wait_ids or any(
                not _non_empty_string(task_id) for task_id in wait_ids
            ):
                errors.append("scheduler_wait.task_ids must contain at least one task id")
                wait_ids = []
            if str(scheduler_wait.get("reason", "")).upper() not in {
                "HARD_DEPENDENCY",
                "JOIN",
            }:
                errors.append("scheduler_wait.reason must be HARD_DEPENDENCY or JOIN")
            if not _non_empty_string(scheduler_wait.get("fallback")):
                errors.append("scheduler_wait requires a fallback")
            if scheduler.get("runnable_task_ids"):
                errors.append(
                    "NO_IDLE_WHILE_RUNNABLE: state declares a wait while runnable tasks exist: "
                    + ", ".join(scheduler["runnable_task_ids"])
                )
            running_ids = set(scheduler.get("running_task_ids", []))
            stale_ids = sorted(set(str(task_id) for task_id in wait_ids) - running_ids)
            if stale_ids:
                errors.append("scheduler_wait targets are not RUNNING: " + ", ".join(stale_ids))
    if status == "BLOCKED" and scheduler:
        internal_work = (
            scheduler["runnable_task_ids"]
            + scheduler["running_task_ids"]
            + scheduler["failed_task_ids"]
        )
        if internal_work:
            errors.append(
                "A globally BLOCKED run cannot retain actionable internal work: "
                + ", ".join(internal_work)
            )

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
            if not _non_empty_string(creative_brief.get("schema_version")):
                if _version_at_least_0_7_1(goal.get("loopseed_version")):
                    errors.append("Locked creative brief requires schema_version")
                else:
                    warnings.append("Legacy locked creative brief has no schema_version")
            brief_version = creative_brief.get("loopseed_version")
            if brief_version in (None, ""):
                if _version_at_least_0_7_1(goal.get("loopseed_version")):
                    errors.append("Locked creative brief requires loopseed_version")
                else:
                    warnings.append("Legacy locked creative brief has no loopseed_version")
            elif brief_version != goal.get("loopseed_version"):
                errors.append("Creative brief must share the goal contract LoopSeed version")
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
    current_binding_id = (
        str(verification_binding.get("binding_id", ""))
        if isinstance(verification_binding, dict)
        else ""
    )
    current_generation = (
        verification_binding.get("generation")
        if isinstance(verification_binding, dict)
        else None
    )
    current_binding_key = (
        (current_binding_id, current_generation)
        if current_binding_id and isinstance(current_generation, int)
        else None
    )
    current_ledger_start = (
        verification_binding.get("evidence_ledger_count")
        if isinstance(verification_binding, dict)
        else None
    )
    current_evidence_ids: set[str] = set()
    for evidence_index, item in enumerate(evidence):
        evidence_id = str(item.get("id", "")).strip()
        if not evidence_id:
            errors.append("Every evidence entry requires a non-empty id")
        elif evidence_id in evidence_by_id:
            errors.append(f"Duplicate evidence id: {evidence_id}")
        else:
            evidence_by_id[evidence_id] = item
        if item.get("run_id") != goal.get("run_id"):
            errors.append(f"Evidence {evidence_id or '<missing>'} must share the One-Shotted run_id")
        if str(item.get("result", "")).upper() not in {"PASS", "FAIL"}:
            errors.append(f"Evidence {evidence_id or '<missing>'} has invalid result")
        if not _non_empty_string(item.get("actor")):
            errors.append(f"Evidence {evidence_id or '<missing>'} requires an actor")
        if not _non_empty_string(item.get("gate_id")):
            errors.append(f"Evidence {evidence_id or '<missing>'} requires a gate_id")
        created_at = str(item.get("created_at", "")).strip()
        if not created_at:
            errors.append(f"Evidence {evidence_id or '<missing>'} requires created_at")
        item_binding_id = str(item.get("binding_id", "")).strip()
        item_generation = item.get("generation")
        item_key = (
            (item_binding_id, item_generation)
            if item_binding_id
            and isinstance(item_generation, int)
            and not isinstance(item_generation, bool)
            else None
        )
        receipt = binding_lineage.get(item_key) if item_key is not None else None
        if item_key is not None:
            if receipt is None:
                errors.append(
                    f"Evidence {evidence_id or '<missing>'} references an unknown verification binding"
                )
            else:
                receipt_subject = binding_subject(receipt)
                if receipt_subject is not None and (
                    str(item.get("project_id", "")) != receipt_subject[0]
                    or str(item.get("candidate_commit", "")) != receipt_subject[1]
                ):
                    errors.append(
                        f"Evidence {evidence_id or '<missing>'} subject does not match its verification binding"
                    )
        elif item_binding_id or item_generation not in (None, ""):
            errors.append(
                f"Evidence {evidence_id or '<missing>'} has an incomplete verification binding reference"
            )
        current_era = bool(
            current_binding_key
            and isinstance(current_ledger_start, int)
            and evidence_index >= current_ledger_start
        )
        if current_era:
            current_evidence_ids.add(evidence_id)
            if item_key != current_binding_key:
                errors.append(
                    f"Evidence {evidence_id or '<missing>'} created after the current binding must reference that binding"
                )
        if strict_integrity:
            if item.get("kind") == "MACHINE":
                errors.extend(_machine_errors(item))
            elif item.get("kind") == "ARTIFACT":
                errors.extend(_artifact_evidence_errors(item))
            elif item.get("result") == "PASS" and (
                not current_binding_key or current_era
            ):
                errors.append(
                    f"Evidence {evidence_id or '<missing>'} PASS must be MACHINE or ARTIFACT evidence"
                )

    try:
        gates = gate_map(acceptance)
    except OneShottedError as exc:
        errors.append(str(exc))
        gates = {}
    current_ledger_by_gate: dict[str, list[dict[str, Any]]] = {
        gate_id: [] for gate_id in gates
    }
    for item in evidence:
        evidence_id = str(item.get("id", "<missing>"))
        gate_id = str(item.get("gate_id", ""))
        gate = gates.get(gate_id)
        if gate is None:
            errors.append(f"Evidence {evidence_id} references unknown gate {gate_id!r}")
            continue
        if str(item.get("actor", "")) != str(gate.get("verifier", "")):
            errors.append(f"Evidence {evidence_id} actor does not match gate {gate_id} verifier")
        if current_binding_id:
            if evidence_id in current_evidence_ids:
                current_ledger_by_gate[gate_id].append(item)
        else:
            current_ledger_by_gate[gate_id].append(item)
    policy = acceptance.get("policy", {})
    for gate_id, gate in gates.items():
        gate_status = str(gate.get("status", "PENDING")).upper()
        if gate_status not in VALID_GATE_STATUSES:
            errors.append(f"Gate {gate_id} has invalid status {gate_status!r}")
        owner = str(gate.get("owner", "")).strip()
        verifier = str(gate.get("verifier", "")).strip()
        if not isinstance(gate.get("required"), bool):
            errors.append(f"Gate {gate_id} required must be boolean")
        if not isinstance(gate.get("requires_machine_evidence", False), bool):
            errors.append(f"Gate {gate_id} requires_machine_evidence must be boolean")
        if not owner or not verifier:
            errors.append(f"Gate {gate_id} requires owner and verifier")
        if policy.get("worker_self_approval_forbidden", True) and owner == verifier:
            errors.append(f"Gate {gate_id} has the same owner and verifier")
        ids = gate.get("evidence_ids", [])
        if not isinstance(ids, list):
            errors.append(f"Gate {gate_id} evidence_ids must be an array")
            ids = []
        if len(ids) != len(set(ids)):
            errors.append(f"Gate {gate_id} contains duplicate evidence ids")
        missing = [item for item in ids if item not in evidence_by_id]
        if missing:
            errors.append(f"Gate {gate_id} references missing evidence: {', '.join(missing)}")
        misbound = [
            item
            for item in ids
            if item in evidence_by_id
            and str(evidence_by_id[item].get("gate_id", "")) != gate_id
        ]
        if misbound:
            errors.append(
                f"Gate {gate_id} references evidence assigned to another gate: {', '.join(misbound)}"
            )
        current_ledger = current_ledger_by_gate.get(gate_id, [])
        current_ledger_ids = [str(item.get("id", "")) for item in current_ledger]
        if ids != current_ledger_ids:
            errors.append(
                f"Gate {gate_id} evidence_ids must exactly match its current binding evidence ledger in ledger order"
            )
        if current_ledger:
            latest_result = str(current_ledger[-1].get("result", "")).upper()
            if latest_result != gate_status:
                errors.append(
                    f"Gate {gate_id} status does not match its latest evidence result"
                )
        elif gate_status in {"PASS", "FAIL"}:
            errors.append(f"Gate {gate_id} has status {gate_status} without current evidence")
        if gate_status == "PASS":
            pass_items = [
                item
                for item in current_ledger[-1:]
                if item.get("result") == "PASS"
                and item.get("actor") == verifier
                and item.get("gate_id") == gate_id
            ]
            if not pass_items:
                errors.append(f"Gate {gate_id} is PASS without verifier-authored PASS evidence")
                continue
            if strict_integrity:
                if binding_identity is None:
                    errors.append(f"Gate {gate_id} PASS requires a current verification binding")
                    continue
                current_items = [
                    item
                    for item in pass_items
                    if str(item.get("binding_id", "")) == current_binding_id
                    and item.get("generation") == current_generation
                    and str(item.get("project_id", "")) == binding_identity[0]
                    and str(item.get("candidate_commit", "")) == binding_identity[1]
                ]
                if not current_items:
                    errors.append(
                        f"Gate {gate_id} PASS evidence does not match the current verification binding generation"
                    )
                    continue
                machine_items = [
                    item
                    for item in current_items
                    if item.get("kind") == "MACHINE"
                    and item.get("producer") == PRODUCER
                    and item.get("exit_code") == 0
                    and item.get("timed_out") is False
                    and item.get("integrity_stable") is True
                    and artifact_subject(item.get("expected_artifact")) == binding_identity[2]
                    and artifact_subject(item.get("artifact_before")) == binding_identity[2]
                    and artifact_subject(item.get("artifact_after")) == binding_identity[2]
                ]
                artifact_items = [
                    item
                    for item in current_items
                    if item.get("kind") == "ARTIFACT"
                    and item.get("producer") == ARTIFACT_PRODUCER
                    and isinstance(item.get("artifacts"), list)
                    and bool(item.get("artifacts"))
                    and item.get("git_repository_detected") is True
                    and str(item.get("actual_candidate_commit", "")) == binding_identity[1]
                ]
                for item in artifact_items:
                    errors.extend(_current_artifact_evidence_errors(root, item))
                if gate.get("requires_machine_evidence", False):
                    if not machine_items:
                        errors.append(
                            f"Gate {gate_id} requires machine-executed integrity-stable PASS evidence"
                        )
                elif not machine_items and not artifact_items:
                    errors.append(
                        f"Gate {gate_id} requires machine evidence or verifier-authored hashed artifact evidence"
                    )

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
        "evidence_by_id": evidence_by_id,
        "defects": defects,
        "blocking_open_defects": blocking_open,
        "creative_brief": creative_brief,
        "dialogue": dialogue,
        "dialogue_rounds": dialogue_rounds,
        "project_domain": project_domain,
        "production_mode": production_mode,
        "calibration_status": calibration_status,
        "task_graph": task_graph,
        "scheduler": scheduler,
        "verification_binding": verification_binding,
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
        "runnable_task_ids": scheduler.get("runnable_task_ids", []),
        "running_task_ids": scheduler.get("running_task_ids", []),
    }, data
