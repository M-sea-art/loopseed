"""Minimal task scheduling and no-idle enforcement for One-Shotted mode."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from one_shotted_io import load_run, read_json, write_json_atomic
from one_shotted_types import OneShottedError, clean_line, utc_now


TASK_GRAPH_FILE = "task-graph.json"
TASK_STATUSES = {"PENDING", "RUNNING", "SUCCEEDED", "FAILED", "BLOCKED", "CANCELLED"}
RELATION_KINDS = {"HARD_DEPENDENCY", "SOFT_ADVICE", "INDEPENDENT"}
JOIN_STRATEGIES = {"ALL_REQUIRED", "FIRST_SUCCESS", "QUORUM"}
WAIT_REASONS = {"HARD_DEPENDENCY", "JOIN"}
TASK_TRANSITIONS = {
    "PENDING": {"RUNNING", "BLOCKED", "CANCELLED"},
    "RUNNING": {"SUCCEEDED", "FAILED", "BLOCKED", "CANCELLED"},
    "FAILED": {"PENDING", "CANCELLED"},
    "BLOCKED": {"PENDING", "CANCELLED"},
    "SUCCEEDED": set(),
    "CANCELLED": set(),
}


def _task_map_unchecked(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(task.get("id", "")).strip(): task
        for task in graph.get("tasks", [])
        if isinstance(task, dict) and str(task.get("id", "")).strip()
    }


def task_graph_errors(graph: dict[str, Any], expected_run_id: str | None = None) -> list[str]:
    """Return deterministic structural errors without mutating the graph."""

    errors: list[str] = []
    if expected_run_id and graph.get("run_id") != expected_run_id:
        errors.append("Task graph must share the One-Shotted run_id")
    policy = graph.get("policy")
    if not isinstance(policy, dict):
        errors.append("Task graph requires a policy object")
    else:
        for key in (
            "no_idle_while_runnable",
            "soft_advice_never_blocks",
            "main_agent_retains_scheduling",
        ):
            if policy.get(key) is not True:
                errors.append(f"Task graph must enable policy.{key}")

    tasks = graph.get("tasks")
    if not isinstance(tasks, list):
        return errors + ["task-graph.json field 'tasks' must be an array"]

    task_ids: list[str] = []
    for index, task in enumerate(tasks):
        label = f"Task at index {index}"
        if not isinstance(task, dict):
            errors.append(f"{label} must be an object")
            continue
        task_id = str(task.get("id", "")).strip()
        if not task_id or any(character.isspace() for character in task_id):
            errors.append(f"{label} requires a whitespace-free id")
            continue
        task_ids.append(task_id)
        if not str(task.get("purpose", "")).strip():
            errors.append(f"Task {task_id} requires a purpose")
        if not str(task.get("owner", "")).strip():
            errors.append(f"Task {task_id} requires an owner")
        status = str(task.get("status", "")).upper()
        if status not in TASK_STATUSES:
            errors.append(f"Task {task_id} has invalid status {status!r}")
        if status == "BLOCKED" and not str(task.get("unblock_condition", "")).strip():
            errors.append(f"Blocked task {task_id} requires an unblock_condition")
        if not isinstance(task.get("read_only"), bool):
            errors.append(f"Task {task_id} read_only must be boolean")
        scopes = task.get("write_scope")
        if not isinstance(scopes, list) or any(not str(scope).strip() for scope in scopes):
            errors.append(f"Task {task_id} write_scope must be an array of non-empty strings")
        elif task.get("read_only") and scopes:
            errors.append(f"Read-only task {task_id} cannot declare write_scope")
        elif not task.get("read_only") and not scopes:
            errors.append(f"Writing task {task_id} requires write_scope")
        if not str(task.get("isolation", "")).strip():
            errors.append(f"Task {task_id} requires an isolation boundary")
        if not isinstance(task.get("relations", []), list):
            errors.append(f"Task {task_id} relations must be an array")
        join = task.get("join")
        if not isinstance(join, dict):
            errors.append(f"Task {task_id} requires a join object")
        else:
            strategy = str(join.get("strategy", "")).upper()
            if strategy not in JOIN_STRATEGIES:
                errors.append(f"Task {task_id} has invalid join strategy {strategy!r}")

    duplicates = sorted({task_id for task_id in task_ids if task_ids.count(task_id) > 1})
    if duplicates:
        errors.append("Duplicate task ids: " + ", ".join(duplicates))

    known = set(task_ids)
    graph_map = _task_map_unchecked(graph)
    hard_edges: dict[str, list[str]] = {task_id: [] for task_id in known}
    for task_id, task in graph_map.items():
        seen_relations: set[tuple[str, str]] = set()
        hard_count = 0
        for relation in task.get("relations", []):
            if not isinstance(relation, dict):
                errors.append(f"Task {task_id} has a non-object relation")
                continue
            source = str(relation.get("task_id", "")).strip()
            kind = str(relation.get("kind", "")).upper()
            if source not in known:
                errors.append(f"Task {task_id} references unknown task {source!r}")
            if source == task_id:
                errors.append(f"Task {task_id} cannot relate to itself")
            if kind not in RELATION_KINDS:
                errors.append(f"Task {task_id} has invalid relation kind {kind!r}")
            key = (source, kind)
            if key in seen_relations:
                errors.append(f"Task {task_id} repeats relation {source}:{kind}")
            seen_relations.add(key)
            if source in known and kind == "HARD_DEPENDENCY":
                hard_count += 1
                hard_edges[task_id].append(source)

        join = task.get("join", {})
        if not isinstance(join, dict):
            continue
        strategy = str(join.get("strategy", "")).upper()
        quorum = join.get("quorum")
        if strategy == "FIRST_SUCCESS" and hard_count < 1:
            errors.append(f"Task {task_id} FIRST_SUCCESS requires a hard dependency")
        if strategy == "QUORUM":
            if not isinstance(quorum, int) or isinstance(quorum, bool):
                errors.append(f"Task {task_id} QUORUM requires an integer quorum")
            elif not 1 <= quorum <= hard_count:
                errors.append(f"Task {task_id} quorum must be between 1 and {hard_count}")
        elif quorum is not None:
            errors.append(f"Task {task_id} may set quorum only with QUORUM")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str, trail: list[str]) -> None:
        if task_id in visiting:
            cycle_start = trail.index(task_id) if task_id in trail else 0
            errors.append("Hard dependency cycle: " + " -> ".join(trail[cycle_start:] + [task_id]))
            return
        if task_id in visited:
            return
        visiting.add(task_id)
        for source in hard_edges.get(task_id, []):
            visit(source, trail + [task_id])
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in sorted(known):
        visit(task_id, [])
    return list(dict.fromkeys(errors))


def _validated_graph(root: Path) -> tuple[Path, dict[str, Any], dict[str, Any], dict[str, Any]]:
    target, goal, _, state = load_run(root)
    graph = read_json(target / TASK_GRAPH_FILE)
    errors = task_graph_errors(graph, str(goal.get("run_id", "")))
    if errors:
        raise OneShottedError("Invalid task graph: " + "; ".join(errors))
    return target, goal, state, graph


def _hard_sources(task: dict[str, Any], tasks: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        tasks[str(relation.get("task_id"))]
        for relation in task.get("relations", [])
        if isinstance(relation, dict)
        and str(relation.get("kind", "")).upper() == "HARD_DEPENDENCY"
        and str(relation.get("task_id")) in tasks
    ]


def _join_satisfied(task: dict[str, Any], tasks: dict[str, dict[str, Any]]) -> bool:
    sources = _hard_sources(task, tasks)
    if not sources:
        return True
    successes = sum(str(source.get("status", "")).upper() == "SUCCEEDED" for source in sources)
    strategy = str(task.get("join", {}).get("strategy", "ALL_REQUIRED")).upper()
    if strategy == "FIRST_SUCCESS":
        return successes >= 1
    if strategy == "QUORUM":
        return successes >= int(task.get("join", {}).get("quorum", len(sources)))
    return successes == len(sources)


def _scopes_overlap(first: str, second: str) -> bool:
    left = first.strip().strip("/") or "*"
    right = second.strip().strip("/") or "*"
    return (
        left == "*"
        or right == "*"
        or left == right
        or left.startswith(right + "/")
        or right.startswith(left + "/")
    )


def _write_conflict(first: dict[str, Any], second: dict[str, Any]) -> bool:
    if first.get("read_only") or second.get("read_only"):
        return False
    if str(first.get("isolation")) != str(second.get("isolation")):
        return False
    return any(
        _scopes_overlap(str(left), str(right))
        for left in first.get("write_scope", [])
        for right in second.get("write_scope", [])
    )


def scheduler_snapshot(graph: dict[str, Any], capacity: int | None = None) -> dict[str, Any]:
    """Derive the maximum safe dispatch batch without mutating task state."""

    if capacity is not None and (isinstance(capacity, bool) or capacity < 1):
        raise OneShottedError("capacity must be a positive integer")
    tasks = _task_map_unchecked(graph)
    running = sorted(
        task_id for task_id, task in tasks.items() if str(task.get("status", "")).upper() == "RUNNING"
    )
    ready = sorted(
        task_id
        for task_id, task in tasks.items()
        if str(task.get("status", "")).upper() == "PENDING" and _join_satisfied(task, tasks)
    )
    pending = sorted(
        task_id for task_id, task in tasks.items() if str(task.get("status", "")).upper() == "PENDING"
    )
    available = None if capacity is None else max(0, capacity - len(running))
    selected: list[str] = []
    held: dict[str, str] = {}
    for task_id in ready:
        task = tasks[task_id]
        if available is not None and len(selected) >= available:
            held[task_id] = "concurrency_capacity"
            continue
        conflicting = next(
            (
                other_id
                for other_id in running + selected
                if _write_conflict(task, tasks[other_id])
            ),
            None,
        )
        if conflicting:
            held[task_id] = f"write_conflict:{conflicting}"
            continue
        selected.append(task_id)

    cancellation_candidates: set[str] = set()
    for consumer_id, consumer in tasks.items():
        strategy = str(consumer.get("join", {}).get("strategy", "ALL_REQUIRED")).upper()
        if strategy not in {"FIRST_SUCCESS", "QUORUM"} or not _join_satisfied(consumer, tasks):
            continue
        for source in _hard_sources(consumer, tasks):
            source_id = str(source.get("id"))
            if str(source.get("status", "")).upper() not in {"PENDING", "RUNNING"}:
                continue
            needed_elsewhere = any(
                other_id != consumer_id
                and str(other.get("status", "")).upper() == "PENDING"
                and not _join_satisfied(other, tasks)
                and any(
                    isinstance(relation, dict)
                    and str(relation.get("task_id")) == source_id
                    and str(relation.get("kind", "")).upper() == "HARD_DEPENDENCY"
                    for relation in other.get("relations", [])
                )
                for other_id, other in tasks.items()
            )
            if not needed_elsewhere:
                cancellation_candidates.add(source_id)

    blocked_by = {
        task_id: [
            str(source.get("id"))
            for source in _hard_sources(tasks[task_id], tasks)
            if str(source.get("status", "")).upper() != "SUCCEEDED"
        ]
        for task_id in pending
        if task_id not in ready
    }
    failed = sorted(
        task_id for task_id, task in tasks.items() if str(task.get("status", "")).upper() == "FAILED"
    )
    blocked = sorted(
        task_id for task_id, task in tasks.items() if str(task.get("status", "")).upper() == "BLOCKED"
    )
    succeeded = sorted(
        task_id for task_id, task in tasks.items() if str(task.get("status", "")).upper() == "SUCCEEDED"
    )
    cancelled = sorted(
        task_id for task_id, task in tasks.items() if str(task.get("status", "")).upper() == "CANCELLED"
    )
    wait_allowed = not selected and bool(running)
    stalled = not selected and not running and bool(pending or failed or blocked)
    complete = bool(tasks) and len(succeeded) + len(cancelled) == len(tasks)
    if selected:
        next_action = "Dispatch all runnable tasks now: " + ", ".join(selected)
    elif running:
        next_action = "No safe runnable task remains; wait only at a declared dependency or join point."
    elif stalled:
        next_action = "No task is running or runnable; repair, unblock, cancel, or replan instead of waiting."
    elif complete:
        next_action = "Task graph is settled; continue to whole-product verification."
    else:
        next_action = "Declare the smallest independently judgeable production tasks."
    return {
        "ready_task_ids": ready,
        "runnable_task_ids": selected,
        "held_task_ids": held,
        "running_task_ids": running,
        "waiting_task_ids": sorted(set(pending) - set(ready)),
        "blocked_by": blocked_by,
        "succeeded_task_ids": succeeded,
        "failed_task_ids": failed,
        "blocked_task_ids": blocked,
        "cancelled_task_ids": cancelled,
        "cancellation_candidate_task_ids": sorted(cancellation_candidates),
        "wait_allowed": wait_allowed,
        "wait_forbidden": bool(selected),
        "stalled": stalled,
        "complete": complete,
        "next_action": next_action,
    }


def schedule_tasks(root: Path, capacity: int | None = None) -> dict[str, Any]:
    _, _, state, graph = _validated_graph(root)
    if str(state.get("status", "")).upper() != "ACTIVE":
        raise OneShottedError("Only an ACTIVE run can schedule tasks")
    return {"ok": True, **scheduler_snapshot(graph, capacity)}


def add_task(
    root: Path,
    task_id: str,
    purpose: str,
    owner: str,
    *,
    relations: list[tuple[str, str]] | None = None,
    join_strategy: str | None = None,
    quorum: int | None = None,
    write_scope: list[str] | None = None,
    read_only: bool = False,
    isolation: str = "shared",
    required: bool = True,
) -> dict[str, Any]:
    target, goal, state, graph = _validated_graph(root)
    if str(state.get("status", "")).upper() != "ACTIVE":
        raise OneShottedError("Only an ACTIVE run can add tasks")
    if str(state.get("phase", "")).upper() not in {"PLAN", "IMPLEMENT", "REPAIR"}:
        raise OneShottedError("Declare production tasks in PLAN, IMPLEMENT, or REPAIR")
    normalized_id = clean_line(task_id, name="task id")
    if any(character.isspace() for character in normalized_id):
        raise OneShottedError("task id must not contain whitespace")
    tasks = _task_map_unchecked(graph)
    if normalized_id in tasks:
        raise OneShottedError(f"Task already exists: {normalized_id}")

    normalized_relations: list[dict[str, str]] = []
    for source, raw_kind in relations or []:
        source_id = clean_line(source, name="relation task id")
        kind = clean_line(raw_kind, name="relation kind").upper()
        if source_id not in tasks:
            raise OneShottedError(f"Unknown relation task: {source_id}")
        if kind not in RELATION_KINDS:
            raise OneShottedError(f"relation kind must be one of {sorted(RELATION_KINDS)}")
        normalized_relations.append({"task_id": source_id, "kind": kind})

    hard_relation_count = sum(
        relation["kind"] == "HARD_DEPENDENCY" for relation in normalized_relations
    )
    if join_strategy is None:
        if hard_relation_count > 1:
            raise OneShottedError(
                "Tasks with multiple hard dependencies must explicitly choose ALL_REQUIRED, FIRST_SUCCESS, or QUORUM"
            )
        strategy = "ALL_REQUIRED"
    else:
        strategy = clean_line(join_strategy, name="join strategy").upper()
    if strategy not in JOIN_STRATEGIES:
        raise OneShottedError(f"join strategy must be one of {sorted(JOIN_STRATEGIES)}")
    if strategy != "QUORUM" and quorum is not None:
        raise OneShottedError("quorum is valid only with QUORUM")
    scopes = [clean_line(scope, name="write scope") for scope in (write_scope or [])]
    if read_only and scopes:
        raise OneShottedError("A read-only task cannot declare write scope")
    if not read_only and not scopes:
        scopes = ["*"]
    now = utc_now()
    graph.setdefault("tasks", []).append(
        {
            "id": normalized_id,
            "purpose": clean_line(purpose, name="task purpose"),
            "owner": clean_line(owner, name="task owner"),
            "required": bool(required),
            "status": "PENDING",
            "relations": normalized_relations,
            "join": {"strategy": strategy, "quorum": quorum},
            "read_only": bool(read_only),
            "write_scope": scopes,
            "isolation": clean_line(isolation, name="isolation boundary"),
            "created_at": now,
            "updated_at": now,
        }
    )
    graph["loopseed_version"] = goal.get("loopseed_version")
    errors = task_graph_errors(graph, str(goal.get("run_id", "")))
    if errors:
        raise OneShottedError("Cannot add invalid task: " + "; ".join(errors))
    snapshot = scheduler_snapshot(graph)
    state["scheduler_wait"] = None
    state["next_action"] = snapshot["next_action"]
    state["updated_at"] = now
    write_json_atomic(target / TASK_GRAPH_FILE, graph)
    write_json_atomic(target / "state.json", state)
    return {"ok": True, "task_id": normalized_id, **snapshot}


def set_task_status(
    root: Path,
    task_id: str,
    status: str,
    actor: str,
    summary: str,
    unblock_condition: str | None = None,
) -> dict[str, Any]:
    target, _, state, graph = _validated_graph(root)
    if str(state.get("status", "")).upper() != "ACTIVE":
        raise OneShottedError("Only an ACTIVE run can update tasks")
    tasks = _task_map_unchecked(graph)
    normalized_id = clean_line(task_id, name="task id")
    if normalized_id not in tasks:
        raise OneShottedError(f"Unknown task: {normalized_id}")
    task = tasks[normalized_id]
    current = str(task.get("status", "")).upper()
    desired = clean_line(status, name="task status").upper()
    if desired not in TASK_STATUSES:
        raise OneShottedError(f"task status must be one of {sorted(TASK_STATUSES)}")
    if desired not in TASK_TRANSITIONS.get(current, set()):
        raise OneShottedError(f"Invalid task transition: {current} -> {desired}")
    if desired == "BLOCKED" and not unblock_condition:
        raise OneShottedError("A BLOCKED task requires an unblock condition")
    if desired != "BLOCKED" and unblock_condition:
        raise OneShottedError("unblock_condition is valid only for a BLOCKED task")
    if desired == "RUNNING":
        if not _join_satisfied(task, tasks):
            raise OneShottedError(f"Task {normalized_id} still has an unsatisfied hard dependency join")
        conflict = next(
            (
                other_id
                for other_id, other in tasks.items()
                if other_id != normalized_id
                and str(other.get("status", "")).upper() == "RUNNING"
                and _write_conflict(task, other)
            ),
            None,
        )
        if conflict:
            raise OneShottedError(
                f"Task {normalized_id} conflicts with running writer {conflict}; isolate it or wait for that writer"
            )

    now = utc_now()
    task.update(
        {
            "status": desired,
            "last_actor": clean_line(actor, name="task actor"),
            "last_summary": clean_line(summary, name="task summary"),
            "updated_at": now,
        }
    )
    if desired == "BLOCKED":
        task["unblock_condition"] = clean_line(
            str(unblock_condition), name="task unblock condition"
        )
    elif desired == "PENDING":
        task.pop("unblock_condition", None)
    snapshot = scheduler_snapshot(graph)
    state["scheduler_wait"] = None
    state["next_action"] = snapshot["next_action"]
    state["updated_at"] = now
    write_json_atomic(target / TASK_GRAPH_FILE, graph)
    write_json_atomic(target / "state.json", state)
    return {"ok": True, "task_id": normalized_id, "task_status": desired, **snapshot}


def declare_wait(
    root: Path,
    task_ids: list[str],
    reason: str,
    fallback: str,
    *,
    capacity: int | None = None,
) -> dict[str, Any]:
    target, _, state, graph = _validated_graph(root)
    if str(state.get("status", "")).upper() != "ACTIVE":
        raise OneShottedError("Only an ACTIVE run can declare a wait")
    snapshot = scheduler_snapshot(graph, capacity)
    if snapshot["runnable_task_ids"]:
        raise OneShottedError(
            "NO_IDLE_WHILE_RUNNABLE: dispatch "
            + ", ".join(snapshot["runnable_task_ids"])
            + " before waiting"
        )
    normalized_ids = [clean_line(task_id, name="wait task id") for task_id in task_ids]
    if not normalized_ids:
        raise OneShottedError("wait requires at least one task id")
    running = set(snapshot["running_task_ids"])
    invalid = sorted(set(normalized_ids) - running)
    if invalid:
        raise OneShottedError("Wait targets must be RUNNING tasks: " + ", ".join(invalid))
    wait_reason = clean_line(reason, name="wait reason").upper()
    if wait_reason not in WAIT_REASONS:
        raise OneShottedError(f"wait reason must be one of {sorted(WAIT_REASONS)}")
    if wait_reason == "HARD_DEPENDENCY":
        tasks = _task_map_unchecked(graph)
        hard_targets = {
            str(relation.get("task_id"))
            for task in tasks.values()
            if str(task.get("status", "")).upper() == "PENDING"
            for relation in task.get("relations", [])
            if isinstance(relation, dict)
            and str(relation.get("kind", "")).upper() == "HARD_DEPENDENCY"
        }
        if not set(normalized_ids) <= hard_targets:
            raise OneShottedError("HARD_DEPENDENCY wait targets must block an unresolved consumer")
    now = utc_now()
    state["scheduler_wait"] = {
        "task_ids": normalized_ids,
        "reason": wait_reason,
        "fallback": clean_line(fallback, name="wait fallback"),
        "declared_at": now,
    }
    state["next_action"] = (
        "Wait only for declared tasks "
        + ", ".join(normalized_ids)
        + "; if they do not return, "
        + state["scheduler_wait"]["fallback"]
    )
    state["updated_at"] = now
    write_json_atomic(target / "state.json", state)
    return {"ok": True, "wait": state["scheduler_wait"], **snapshot}
