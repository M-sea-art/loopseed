#!/usr/bin/env python3
"""Command-line interface for the LoopSeed One-Shotted control plane."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from one_shotted_core import (  # noqa: E402
    OneShottedError,
    add_gate,
    finalize,
    initialize,
    record_defect,
    record_gate_result,
    resume,
    run_evidence,
    status,
    transition,
    validate,
)


def print_json(value: dict[str, object]) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def add_root(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", default=".", help="Target project root; default: current directory")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Initialize and enforce a LoopSeed One-Shotted evidence loop"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Create a project-local One-Shotted control plane")
    add_root(init)
    init.add_argument("--goal", required=True, help="The single human-authorized root goal")
    init.add_argument("--force", action="store_true", help="Replace an existing One-Shotted run")

    gate = subparsers.add_parser("add-gate", help="Add an observable acceptance gate")
    add_root(gate)
    gate.add_argument("--id", required=True)
    gate.add_argument("--title", required=True)
    gate.add_argument("--criterion", required=True)
    gate.add_argument("--owner", required=True, help="Implementation owner")
    gate.add_argument("--verifier", required=True, help="Independent verifier")
    gate.add_argument("--optional", action="store_true")
    gate.add_argument(
        "--machine",
        action="store_true",
        help="Require machine-executed evidence; manual record entries cannot satisfy this gate",
    )

    record = subparsers.add_parser("record", help="Record an independent gate verdict")
    add_root(record)
    record.add_argument("--gate", required=True)
    record.add_argument("--result", required=True, choices=("PASS", "FAIL", "pass", "fail"))
    record.add_argument("--actor", required=True)
    record.add_argument("--summary", required=True)
    record.add_argument("--command", dest="commands", action="append", default=[])
    record.add_argument("--artifact", action="append", default=[])

    machine = subparsers.add_parser(
        "run-evidence", help="Execute a command and bind its exit status to a gate or blocker"
    )
    add_root(machine)
    target_group = machine.add_mutually_exclusive_group(required=True)
    target_group.add_argument("--gate", help="Acceptance gate to update from machine evidence")
    target_group.add_argument("--blocker", help="Active blocker to produce unblock evidence for")
    machine.add_argument("--actor", required=True)
    machine.add_argument("--command", dest="exec_command", required=True)
    machine.add_argument("--project", required=True)
    machine.add_argument("--candidate", required=True)
    machine.add_argument("--artifact", required=True)
    machine.add_argument("--timeout", type=int, default=120)

    defect = subparsers.add_parser("defect", help="Append an OPEN or RESOLVED defect event")
    add_root(defect)
    defect.add_argument("--id", required=True)
    defect.add_argument("--severity", required=True, choices=("P0", "P1", "P2", "P3"))
    defect.add_argument("--status", default="OPEN", choices=("OPEN", "RESOLVED"))
    defect.add_argument("--summary", required=True)
    defect.add_argument("--actor", required=True)
    defect.add_argument("--evidence-id")

    move = subparsers.add_parser("transition", help="Advance, reroute, block, or abort the run")
    add_root(move)
    move.add_argument("--phase", choices=("BIND", "PLAN", "IMPLEMENT", "VERIFY", "REPAIR"))
    move.add_argument("--next", dest="next_action")
    move.add_argument("--no-progress", action="store_true")
    move.add_argument("--blocker")
    move.add_argument("--unblock")
    move.add_argument("--project")
    move.add_argument("--candidate")
    move.add_argument("--artifact")
    move.add_argument("--abort", action="store_true")

    recover = subparsers.add_parser(
        "resume", help="Resume BLOCKED to VERIFY only with fresh machine unblock evidence"
    )
    add_root(recover)
    recover.add_argument("--evidence", required=True)
    recover.add_argument("--actor", required=True)

    check = subparsers.add_parser("validate", help="Validate contracts, ledgers, and evidence references")
    add_root(check)
    check.add_argument("--require-final", action="store_true")

    finish = subparsers.add_parser("finalize", help="Write VERIFIED only after every hard gate passes")
    add_root(finish)

    show = subparsers.add_parser("status", help="Print a compact run summary")
    add_root(show)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root)
    try:
        if args.command == "init":
            result = initialize(root, args.goal, force=args.force)
        elif args.command == "add-gate":
            result = add_gate(
                root,
                args.id,
                args.title,
                args.criterion,
                args.owner,
                args.verifier,
                required=not args.optional,
                requires_machine_evidence=args.machine,
            )
        elif args.command == "record":
            result = record_gate_result(
                root,
                args.gate,
                args.result,
                args.actor,
                args.summary,
                commands=args.commands,
                artifacts=args.artifact,
            )
        elif args.command == "run-evidence":
            result = run_evidence(
                root,
                args.actor,
                args.exec_command,
                args.project,
                args.candidate,
                args.artifact,
                gate_id=args.gate,
                blocker_id=args.blocker,
                timeout_seconds=args.timeout,
            )
        elif args.command == "defect":
            result = record_defect(
                root,
                args.id,
                args.severity,
                args.status,
                args.summary,
                args.actor,
                evidence_id=args.evidence_id,
            )
        elif args.command == "transition":
            result = transition(
                root,
                phase=args.phase,
                next_action=args.next_action,
                no_progress=args.no_progress,
                blocked_reason=args.blocker,
                unblock_condition=args.unblock,
                abort=args.abort,
                project_id=args.project,
                candidate_commit=args.candidate,
                artifact=args.artifact,
            )
        elif args.command == "resume":
            result = resume(root, args.evidence, args.actor)
        elif args.command == "validate":
            result = validate(root, require_final=args.require_final)
        elif args.command == "finalize":
            result = finalize(root)
        elif args.command == "status":
            result = status(root)
        else:  # pragma: no cover
            parser.error(f"Unknown command: {args.command}")
            return 2
    except OneShottedError as exc:
        print_json({"ok": False, "error": str(exc)})
        return 2
    print_json(result)
    return 0 if result.get("ok", False) else 1


if __name__ == "__main__":
    raise SystemExit(main())
