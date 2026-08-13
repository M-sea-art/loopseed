"""Public control-plane API for LoopSeed One-Shotted mode."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from one_shotted_bind import bind_project
from one_shotted_calibration import (
    lock_creative_brief as _lock_creative_brief,
    record_dialogue_turn as _record_dialogue_turn,
)
from one_shotted_context import (
    assert_project_context_ready,
    initialize,
    lock_project_context,
    lock_project_context_file,
)
from one_shotted_defects import record_defect
from one_shotted_evidence import record_gate_result
from one_shotted_finalize import finalize
from one_shotted_gates import add_gate
from one_shotted_io import read_json
from one_shotted_runner import run_evidence
from one_shotted_status import status
from one_shotted_tasks import (
    add_task,
    declare_wait,
    schedule_tasks,
    set_task_required,
    set_task_status,
)
from one_shotted_transition import transition
from one_shotted_types import OneShottedError
from one_shotted_validate import validate


def record_dialogue_turn(root: Path, *args: Any, **kwargs: Any) -> dict[str, Any]:
    assert_project_context_ready(root)
    return _record_dialogue_turn(root, *args, **kwargs)


def lock_creative_brief(
    root: Path,
    brief: dict[str, Any],
    *,
    actor: str = "lead",
) -> dict[str, Any]:
    context = assert_project_context_ready(root)
    compiled = dict(brief)
    if context is not None:
        compiled.setdefault("project_context_id", context.get("context_id"))
    return _lock_creative_brief(root, compiled, actor=actor)


def lock_creative_brief_file(
    root: Path,
    file_path: Path,
    *,
    actor: str = "lead",
) -> dict[str, Any]:
    source = file_path.expanduser()
    if not source.is_absolute():
        source = root.expanduser().resolve() / source
    return lock_creative_brief(root, read_json(source), actor=actor)


__all__ = [
    "OneShottedError",
    "add_gate",
    "add_task",
    "assert_project_context_ready",
    "bind_project",
    "declare_wait",
    "finalize",
    "initialize",
    "lock_creative_brief",
    "lock_creative_brief_file",
    "lock_project_context",
    "lock_project_context_file",
    "record_defect",
    "record_dialogue_turn",
    "record_gate_result",
    "run_evidence",
    "schedule_tasks",
    "set_task_required",
    "set_task_status",
    "status",
    "transition",
    "validate",
]
