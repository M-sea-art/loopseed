"""Contracts and primitive helpers for LoopSeed One-Shotted mode."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.8.1"
RUN_RELATIVE = Path(".loopseed") / "one-shotted"
VALID_STATUSES = {"ACTIVE", "VERIFIED", "BLOCKED", "ABORTED"}
VALID_PHASES = {"CALIBRATE", "BIND", "PLAN", "IMPLEMENT", "VERIFY", "REPAIR", "FINALIZE"}
VALID_GATE_STATUSES = {"PENDING", "PASS", "FAIL", "BLOCKED"}
VALID_RESULTS = {"PASS", "FAIL"}
VALID_SEVERITIES = {"P0", "P1", "P2", "P3"}
VALID_DEFECT_STATUSES = {"OPEN", "RESOLVED"}
PROJECT_DOMAINS = {"game", "general"}
PRODUCTION_MODES = {"focused", "studio", "moonshot"}
GATE_ROLES = {"hard", "bar"}
DIALOGUE_KINDS = {"seed", "synthesis", "question", "answer", "decision"}
DIALOGUE_EFFECTS = {
    "preserve",
    "clarify",
    "correct",
    "amplify",
    "complete",
    "continue",
    "offer_options",
}
REQUIRED_FILES = (
    "project-identity.md",
    "architecture-contract.md",
    "goal-contract.json",
    "acceptance.json",
    "expert-registry.json",
    "state.json",
    "evidence.jsonl",
    "defects.jsonl",
)
CALIBRATION_FILES = (
    "creative-brief.json",
    "dialogue.jsonl",
)
SCHEDULER_FILE = "task-graph.json"
ALLOWED_TRANSITIONS = {
    "CALIBRATE": set(),
    "BIND": {"PLAN"},
    "PLAN": {"IMPLEMENT"},
    "IMPLEMENT": {"VERIFY", "PLAN"},
    "VERIFY": {"REPAIR", "FINALIZE", "PLAN"},
    "REPAIR": {"IMPLEMENT", "VERIFY", "PLAN"},
    "FINALIZE": set(),
}


class OneShottedError(RuntimeError):
    """User-actionable contract or transition error."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_id(prefix: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}-{stamp}-{uuid.uuid4().hex[:8]}"


def clean_line(value: str, *, name: str) -> str:
    normalized = " ".join(str(value).split())
    if not normalized:
        raise OneShottedError(f"{name} must not be empty")
    return normalized


def run_dir(root: Path) -> Path:
    return root.expanduser().resolve() / RUN_RELATIVE


def template_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "templates" / "one-shotted"


def schema_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "schemas" / "one-shotted"
