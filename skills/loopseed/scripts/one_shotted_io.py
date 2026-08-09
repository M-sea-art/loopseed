"""Project-local JSON and JSONL persistence for One-Shotted mode."""

from __future__ import annotations

import json
import os
import time
import uuid
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Iterator, TypeVar

from one_shotted_types import OneShottedError, run_dir, template_dir

ResultT = TypeVar("ResultT")


@contextmanager
def run_lock(root: Path) -> Iterator[None]:
    """Serialize project-local control-plane mutations across CLI processes."""

    # Keep the lock beside, not inside, the run directory. A failed command in
    # an uninitialized project must not create a partial run, and `init
    # --force` may safely replace the run directory while holding this lock.
    control_root = run_dir(root).parent
    control_root.mkdir(parents=True, exist_ok=True)
    path = control_root / ".one-shotted.runtime.lock"
    with path.open("a+b") as handle:
        if os.name == "nt":  # pragma: no cover - exercised on Windows CI only
            import msvcrt

            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"\0")
                handle.flush()
            handle.seek(0)
            while True:
                try:
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    time.sleep(0.05)
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


@contextmanager
def verification_activity_lock(root: Path, *, exclusive: bool) -> Iterator[None]:
    """Coordinate long verifier execution without blocking ordinary state updates."""

    control_root = run_dir(root).parent
    control_root.mkdir(parents=True, exist_ok=True)
    path = control_root / ".one-shotted.verification.lock"
    with path.open("a+b") as handle:
        if os.name == "nt":  # pragma: no cover - exercised on Windows CI only
            import msvcrt

            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"\0")
                handle.flush()
            handle.seek(0)
            mode = msvcrt.LK_NBLCK if exclusive else msvcrt.LK_NBRLCK
            while True:
                try:
                    msvcrt.locking(handle.fileno(), mode, 1)
                    break
                except OSError:
                    time.sleep(0.05)
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            mode = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
            fcntl.flock(handle.fileno(), mode)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def locked_mutation(function: Callable[..., ResultT]) -> Callable[..., ResultT]:
    """Decorate a public mutation whose first argument is the project root."""

    @wraps(function)
    def wrapped(root: Path, *args: Any, **kwargs: Any) -> ResultT:
        with run_lock(root):
            return function(root, *args, **kwargs)

    return wrapped


def exclusive_verification_mutation(
    function: Callable[..., ResultT],
) -> Callable[..., ResultT]:
    """Serialize a mutation after all active verifier commands have committed."""

    @wraps(function)
    def wrapped(root: Path, *args: Any, **kwargs: Any) -> ResultT:
        with verification_activity_lock(root, exclusive=True):
            with run_lock(root):
                return function(root, *args, **kwargs)

    return wrapped

def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise OneShottedError(f"Missing required file: {path}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise OneShottedError(f"Cannot read valid JSON from {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise OneShottedError(f"Expected a JSON object in {path}")
    return value


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        os.replace(temporary, path)
    except (OSError, UnicodeError) as exc:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        raise OneShottedError(f"Cannot write JSON atomically to {path}: {exc}") from exc


def append_jsonl(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
    except (OSError, UnicodeError) as exc:
        raise OneShottedError(f"Cannot append evidence to {path}: {exc}") from exc


def current_gate_evidence_ids(
    target: Path,
    gate_id: str,
    binding: dict[str, Any] | None,
) -> list[str]:
    """Derive gate references from the ledger, including a prior partial commit."""

    values, errors = read_jsonl(target / "evidence.jsonl")
    if errors:
        raise OneShottedError("Cannot synchronize an invalid evidence ledger: " + "; ".join(errors))
    binding_id = str(binding.get("binding_id", "")) if isinstance(binding, dict) else ""
    generation = binding.get("generation") if isinstance(binding, dict) else None
    result: list[str] = []
    for item in values:
        if str(item.get("gate_id", "")) != gate_id:
            continue
        if binding_id:
            if (
                str(item.get("binding_id", "")) != binding_id
                or item.get("generation") != generation
            ):
                continue
        elif item.get("binding_id") not in (None, ""):
            continue
        evidence_id = str(item.get("id", "")).strip()
        if evidence_id:
            result.append(evidence_id)
    return result


def current_artifact_evidence_receipts(
    target: Path,
    acceptance: dict[str, Any],
    binding: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Return still-current latest PASS artifact receipts for current gates."""

    latest_ids = {
        str(ids[-1])
        for gate in acceptance.get("gates", [])
        if isinstance(gate, dict)
        for ids in [gate.get("evidence_ids", [])]
        if isinstance(ids, list) and ids
    }
    values, errors = read_jsonl(target / "evidence.jsonl")
    if errors:
        raise OneShottedError("Cannot inspect an invalid evidence ledger: " + "; ".join(errors))
    binding_id = str(binding.get("binding_id", "")) if isinstance(binding, dict) else ""
    generation = binding.get("generation") if isinstance(binding, dict) else None
    receipts: list[dict[str, Any]] = []
    for item in values:
        if (
            str(item.get("id", "")) not in latest_ids
            or item.get("kind") != "ARTIFACT"
            or item.get("result") != "PASS"
            or item.get("producer") != "loopseed.artifact-evidence-recorder"
        ):
            continue
        if (
            str(item.get("binding_id", "")) != binding_id
            or item.get("generation") != generation
        ):
            continue
        # An allowlisted untracked artifact must still have the bytes that the
        # verifier hashed. Otherwise it could become an unbound source input.
        from one_shotted_integrity import artifact_identity, artifact_subject

        project_root = target.parent.parent
        for artifact in item.get("artifacts", []):
            if not isinstance(artifact, dict) or artifact_subject(artifact) is None:
                continue
            try:
                current = artifact_identity(project_root, str(artifact.get("path", "")))
            except OneShottedError:
                continue
            if artifact_subject(current) == artifact_subject(artifact):
                receipts.append(dict(artifact))
    return sorted(receipts, key=lambda item: str(item.get("path", "")))


def current_artifact_evidence_paths(
    target: Path,
    acceptance: dict[str, Any],
    binding: dict[str, Any] | None,
) -> list[str]:
    """Return paths from still-current latest PASS artifact receipts."""

    return sorted(
        {
            str(item["path"])
            for item in current_artifact_evidence_receipts(target, acceptance, binding)
        }
    )


def read_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    values: list[dict[str, Any]] = []
    errors: list[str] = []
    if not path.exists():
        return values, [f"Missing required file: {path}"]
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return values, [f"Cannot read {path}: {exc}"]
    for line_number, raw in enumerate(lines, start=1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{line_number}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{path}:{line_number}: expected an object")
            continue
        values.append(value)
    return values, errors


def load_template_json(name: str) -> dict[str, Any]:
    return read_json(template_dir() / name)


def load_template_text(name: str) -> str:
    path = template_dir() / name
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError, UnicodeError) as exc:
        raise OneShottedError(f"Cannot read bundled template {path}: {exc}") from exc


def load_run(root: Path) -> tuple[Path, dict[str, Any], dict[str, Any], dict[str, Any]]:
    target = run_dir(root)
    return (
        target,
        read_json(target / "goal-contract.json"),
        read_json(target / "acceptance.json"),
        read_json(target / "state.json"),
    )
