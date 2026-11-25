#!/usr/bin/env python3
"""Minimal Agent-Native Game Development Stack v1 state helper.

This is intentionally a thin control helper. It does not implement engine,
geometry, asset, Gauntlet, or finalization behavior. Those remain separate
capabilities coordinated by LoopSeed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STACK_VERSION = "1.0"
CAPABILITY_ID = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
DOMAINS = {
    "orchestration",
    "quality",
    "engine",
    "world",
    "asset",
    "qa",
    "performance",
    "knowledge",
    "memory",
    "other",
}
OWNERSHIP = {"isolated", "shared-read", "integration-owner", "global-coupled"}
COST_CLASSES = {"low", "medium", "high", "external"}
STATUSES = {"experimental", "verified", "deprecated"}
HARVEST_KINDS = {
    "one_off_defect",
    "invariant",
    "skill",
    "geometry_macro",
    "template_gap",
    "tool_gap",
    "test_gap",
    "knowledge_gap",
    "architecture_gap",
    "structural_reset",
}


def _stack_dir(root: str | os.PathLike[str]) -> Path:
    return Path(root).resolve() / ".loopseed" / "agent-native-stack-v1"


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    temp.replace(path)


def _dedupe(values: list[str] | None) -> list[str]:
    return list(dict.fromkeys(values or []))


def init_state(root: str, world_id: str) -> dict[str, str]:
    base = _stack_dir(root)
    base.mkdir(parents=True, exist_ok=True)

    registry = base / "capability-registry.json"
    world_plan = base / "world-plan.json"
    harvest = base / "harvest.jsonl"

    if not registry.exists():
        _write_json(registry, {"stack_version": STACK_VERSION, "capabilities": []})

    if not world_plan.exists():
        _write_json(
            world_plan,
            {
                "stack_version": STACK_VERSION,
                "world_id": world_id,
                "units": "meters",
                "coordinate_system": {"up_axis": "Y", "handedness": "right"},
                "camera_contracts": [],
                "semantic_nodes": [],
                "routes": [],
                "build_slots": [],
                "gameplay_proxies": [],
                "invariants": [],
                "engine_adapters": {},
            },
        )

    harvest.touch(exist_ok=True)
    return {
        "registry": str(registry),
        "world_plan": str(world_plan),
        "harvest": str(harvest),
    }


def register_capability(args: argparse.Namespace) -> dict[str, Any]:
    if not CAPABILITY_ID.fullmatch(args.id):
        raise ValueError(f"invalid capability id: {args.id}")
    if args.domain not in DOMAINS:
        raise ValueError(f"invalid domain: {args.domain}")
    if args.ownership not in OWNERSHIP:
        raise ValueError(f"invalid ownership scope: {args.ownership}")
    if args.cost not in COST_CLASSES:
        raise ValueError(f"invalid cost class: {args.cost}")
    if args.status not in STATUSES:
        raise ValueError(f"invalid status: {args.status}")

    paths = init_state(args.root, args.world_id)
    registry_path = Path(paths["registry"])
    registry = _read_json(registry_path)
    capabilities = registry.setdefault("capabilities", [])
    if any(item.get("id") == args.id for item in capabilities):
        raise ValueError(f"capability already registered: {args.id}")

    record: dict[str, Any] = {
        "id": args.id,
        "domain": args.domain,
        "provider": args.provider,
        "description": args.description,
        "engine_support": _dedupe(args.engine),
        "inputs": args.input or [],
        "outputs": args.output or [],
        "tools_required": _dedupe(args.tool),
        "evidence_required": args.evidence or [],
        "ownership_scope": args.ownership,
        "cost_class": args.cost,
        "fallback": args.fallback or "",
        "status": args.status,
    }
    if args.source_repo or args.source_reference or args.source_evidence:
        record["source"] = {
            "repository": args.source_repo or "",
            "reference": args.source_reference or "",
            "evidence": args.source_evidence or [],
        }

    capabilities.append(record)
    capabilities.sort(key=lambda item: item["id"])
    _write_json(registry_path, registry)
    return record


def harvest(args: argparse.Namespace) -> dict[str, Any]:
    if args.kind not in HARVEST_KINDS:
        raise ValueError(f"invalid harvest kind: {args.kind}")
    if args.capability_id and not CAPABILITY_ID.fullmatch(args.capability_id):
        raise ValueError(f"invalid proposed capability id: {args.capability_id}")

    paths = init_state(args.root, args.world_id)
    event: dict[str, Any] = {
        "stack_version": STACK_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": args.actor,
        "source": args.source,
        "kind": args.kind,
        "summary": args.summary,
        "evidence": args.evidence or [],
        "next_action": args.next_action,
        "promoted": False,
    }
    if args.capability_id:
        event["proposed_capability_id"] = args.capability_id

    path = Path(paths["harvest"])
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return event


def list_capabilities(args: argparse.Namespace) -> list[dict[str, Any]]:
    paths = init_state(args.root, args.world_id)
    registry = _read_json(Path(paths["registry"]))
    return list(registry.get("capabilities", []))


def _print(data: Any) -> None:
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="initialize local Stack v1 state")
    init.add_argument("--root", default=".")
    init.add_argument("--world-id", default="game")

    register = sub.add_parser("register-capability", help="add a capability registry entry")
    register.add_argument("--root", default=".")
    register.add_argument("--world-id", default="game")
    register.add_argument("--id", required=True)
    register.add_argument("--domain", required=True, choices=sorted(DOMAINS))
    register.add_argument("--provider", required=True)
    register.add_argument("--description", required=True)
    register.add_argument("--engine", action="append")
    register.add_argument("--input", action="append")
    register.add_argument("--output", action="append")
    register.add_argument("--tool", action="append")
    register.add_argument("--evidence", action="append")
    register.add_argument("--ownership", default="isolated", choices=sorted(OWNERSHIP))
    register.add_argument("--cost", default="low", choices=sorted(COST_CLASSES))
    register.add_argument("--status", default="experimental", choices=sorted(STATUSES))
    register.add_argument("--fallback")
    register.add_argument("--source-repo")
    register.add_argument("--source-reference")
    register.add_argument("--source-evidence", action="append")

    harvest_cmd = sub.add_parser("harvest", help="record a reusable lesson or gap")
    harvest_cmd.add_argument("--root", default=".")
    harvest_cmd.add_argument("--world-id", default="game")
    harvest_cmd.add_argument("--actor", default="lead")
    harvest_cmd.add_argument("--source", required=True)
    harvest_cmd.add_argument("--kind", required=True, choices=sorted(HARVEST_KINDS))
    harvest_cmd.add_argument("--summary", required=True)
    harvest_cmd.add_argument("--evidence", action="append")
    harvest_cmd.add_argument("--capability-id")
    harvest_cmd.add_argument("--next-action", required=True)

    listing = sub.add_parser("list-capabilities", help="print registered capabilities")
    listing.add_argument("--root", default=".")
    listing.add_argument("--world-id", default="game")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            _print(init_state(args.root, args.world_id))
        elif args.command == "register-capability":
            _print(register_capability(args))
        elif args.command == "harvest":
            _print(harvest(args))
        elif args.command == "list-capabilities":
            _print(list_capabilities(args))
        else:
            parser.error(f"unknown command: {args.command}")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
