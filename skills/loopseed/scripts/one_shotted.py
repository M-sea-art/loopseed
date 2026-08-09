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
    add_task,
    bind_project,
    declare_wait,
    finalize,
    initialize,
    lock_creative_brief_file,
    record_defect,
    record_dialogue_turn,
    record_gate_result,
    run_evidence,
    schedule_tasks,
    set_task_required,
    set_task_status,
    status,
    transition,
    validate,
)


def print_json(value: dict[str, object]) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def add_root(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", default=".", help="Target project root; default: current directory")


def parse_relation(value: str) -> tuple[str, str]:
    try:
        task_id, kind = value.rsplit(":", 1)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("relation must use TASK_ID:KIND") from exc
    if not task_id.strip() or not kind.strip():
        raise argparse.ArgumentTypeError("relation must use TASK_ID:KIND")
    return task_id.strip(), kind.strip().upper()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Initialize and enforce a LoopSeed One-Shotted evidence loop"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Create a project-local One-Shotted control plane")
    add_root(init)
    init.add_argument("--goal", required=True, help="The single human-authorized root goal")
    init.add_argument("--domain", default="auto", choices=("auto", "game", "general"))
    init.add_argument(
        "--production-mode",
        default="auto",
        choices=("auto", "focused", "studio", "moonshot"),
    )
    init.add_argument("--dialogue", default="auto", choices=("auto", "on", "off"))
    init.add_argument("--max-dialogue-rounds", type=int, default=5)
    init.add_argument("--force", action="store_true", help="Replace an existing One-Shotted run")

    bind = subparsers.add_parser(
        "bind",
        help="Freeze the built candidate's Git HEAD and primary artifact before verification",
    )
    add_root(bind)
    bind.add_argument("--project", required=True)
    bind.add_argument("--candidate", required=True)
    bind.add_argument("--artifact", required=True)

    dialogue = subparsers.add_parser(
        "dialogue-turn",
        help="Record a creative co-director turn before the One-Shot production lock",
    )
    add_root(dialogue)
    dialogue.add_argument("--actor", required=True, choices=("user", "model"))
    dialogue.add_argument(
        "--kind",
        required=True,
        choices=("seed", "synthesis", "question", "answer", "decision"),
    )
    dialogue.add_argument("--summary", required=True)
    dialogue.add_argument(
        "--effect",
        action="append",
        default=[],
        help="Model effect: preserve, clarify, correct, amplify, complete, continue, offer_options",
    )
    dialogue.add_argument(
        "--advance",
        action="append",
        default=[],
        help="Material decision surface advanced by this turn",
    )
    dialogue.add_argument(
        "--option",
        action="append",
        default=[],
        help="Question option in ID|label|consequence format; repeat 2-4 times",
    )
    dialogue.add_argument("--recommended", help="Recommended option ID")

    lock = subparsers.add_parser(
        "lock-brief",
        help="Validate and freeze a user-authorized creative brief, then enter BIND",
    )
    add_root(lock)
    lock.add_argument("--file", required=True, help="Path to the compiled creative brief JSON")
    lock.add_argument("--actor", default="lead", help="Actor performing the lock")

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
        help="Require a command executed by run-evidence; artifact-only PASS cannot satisfy this gate",
    )

    record = subparsers.add_parser("record", help="Record an independent gate verdict")
    add_root(record)
    record.add_argument("--gate", required=True)
    record.add_argument("--result", required=True, choices=("PASS", "FAIL", "pass", "fail"))
    record.add_argument("--actor", required=True)
    record.add_argument("--summary", required=True)
    record.add_argument(
        "--command",
        dest="commands",
        action="append",
        default=[],
        help="Rejected: record never executes commands; use run-evidence",
    )
    record.add_argument("--artifact", action="append", default=[])

    machine = subparsers.add_parser(
        "run-evidence",
        help="Execute a verifier command and bind its result to Git HEAD and artifact SHA-256",
    )
    add_root(machine)
    machine.add_argument("--gate", required=True)
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
    move.add_argument(
        "--phase",
        choices=("CALIBRATE", "BIND", "PLAN", "IMPLEMENT", "VERIFY", "REPAIR"),
    )
    move.add_argument("--next", dest="next_action")
    move.add_argument("--no-progress", action="store_true")
    move.add_argument("--blocker")
    move.add_argument("--unblock")
    move.add_argument("--abort", action="store_true")

    task = subparsers.add_parser("add-task", help="Add a bounded task to the no-idle scheduler")
    add_root(task)
    task.add_argument("--id", required=True)
    task.add_argument("--purpose", required=True)
    task.add_argument("--owner", required=True)
    task.add_argument(
        "--relation",
        action="append",
        type=parse_relation,
        default=[],
        help="TASK_ID:HARD_DEPENDENCY|SOFT_ADVICE|INDEPENDENT",
    )
    task.add_argument(
        "--join",
        choices=("ALL_REQUIRED", "FIRST_SUCCESS", "QUORUM"),
    )
    task.add_argument("--quorum", type=int)
    task.add_argument("--write-scope", action="append", default=[])
    task.add_argument("--read-only", action="store_true")
    task.add_argument("--isolation", default="shared")
    task.add_argument("--optional", action="store_true")

    task_state = subparsers.add_parser("task-status", help="Start, finish, fail, block, or cancel a task")
    add_root(task_state)
    task_state.add_argument("--task", required=True)
    task_state.add_argument(
        "--status",
        required=True,
        choices=("PENDING", "RUNNING", "SUCCEEDED", "FAILED", "BLOCKED", "CANCELLED"),
    )
    task_state.add_argument("--actor", required=True)
    task_state.add_argument("--summary", required=True)
    task_state.add_argument("--unblock")

    task_requirement = subparsers.add_parser(
        "task-requirement",
        help="Explicitly mark an existing task required or optional",
    )
    add_root(task_requirement)
    task_requirement.add_argument("--task", required=True)
    requirement = task_requirement.add_mutually_exclusive_group(required=True)
    requirement.add_argument("--required", action="store_true")
    requirement.add_argument("--optional", action="store_true")
    task_requirement.add_argument("--actor", required=True)
    task_requirement.add_argument("--summary", required=True)

    schedule = subparsers.add_parser("schedule", help="List the maximum safe runnable task batch")
    add_root(schedule)
    schedule.add_argument("--capacity", type=int)

    wait = subparsers.add_parser("wait", help="Declare a legal dependency or join wait")
    add_root(wait)
    wait.add_argument("--for", dest="task_ids", action="append", required=True)
    wait.add_argument("--reason", required=True, choices=("HARD_DEPENDENCY", "JOIN"))
    wait.add_argument("--fallback", required=True)
    wait.add_argument("--capacity", type=int)

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
            result = initialize(
                root,
                args.goal,
                force=args.force,
                domain=args.domain,
                production_mode=args.production_mode,
                dialogue=args.dialogue,
                max_dialogue_rounds=args.max_dialogue_rounds,
            )
        elif args.command == "bind":
            result = bind_project(root, args.project, args.candidate, args.artifact)
        elif args.command == "dialogue-turn":
            result = record_dialogue_turn(
                root,
                args.actor,
                args.kind,
                args.summary,
                effects=args.effect,
                advances=args.advance,
                options=args.option,
                recommended=args.recommended,
            )
        elif args.command == "lock-brief":
            result = lock_creative_brief_file(root, Path(args.file), actor=args.actor)
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
                args.gate,
                args.actor,
                args.exec_command,
                args.project,
                args.candidate,
                args.artifact,
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
            )
        elif args.command == "add-task":
            result = add_task(
                root,
                args.id,
                args.purpose,
                args.owner,
                relations=args.relation,
                join_strategy=args.join,
                quorum=args.quorum,
                write_scope=args.write_scope,
                read_only=args.read_only,
                isolation=args.isolation,
                required=not args.optional,
            )
        elif args.command == "task-status":
            result = set_task_status(
                root,
                args.task,
                args.status,
                args.actor,
                args.summary,
                unblock_condition=args.unblock,
            )
        elif args.command == "task-requirement":
            result = set_task_required(
                root,
                args.task,
                args.required and not args.optional,
                args.actor,
                args.summary,
            )
        elif args.command == "schedule":
            result = schedule_tasks(root, capacity=args.capacity)
        elif args.command == "wait":
            result = declare_wait(
                root,
                args.task_ids,
                args.reason,
                args.fallback,
                capacity=args.capacity,
            )
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
