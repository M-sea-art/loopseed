# LoopSeed v0.5 Runtime Evidence Patch

## Purpose

This experiment upgrades LoopSeed from contract-bound autonomous execution to evidence-governed execution.

The goal is not to add more agents. The goal is to make completion decisions depend on verifiable reality.

## Core additions

### 1. Project Binding Receipt

Before execution, freeze:

- canonical project
- repository
- branch
- commit baseline
- target artifact
- stage
- protected invariants

Purpose: prevent high-quality execution on the wrong target.

### 2. Executable Evidence Runner

Evidence must connect:

command -> result -> artifact -> runtime state -> capture -> verdict

A summary is not evidence.

### 3. Production Frontier

Maintain the current decision state:

- champion build
- largest material gap
- next repair bundle
- preservation gates
- rollback target

The loop decides from state, not from memory.

### 4. Strong Verdict Model

Separate:

- execution status
- evidence status
- quality status
- terminal reason

Never convert build success into product verification.

## Non-goals

- no permanent new agent taxonomy
- no giant framework rewrite
- no vendor-specific lock-in
- no replacement of existing One-Shotted flow

## Experiment question

Does evidence-governed looping reduce false completion and improve autonomous product quality compared with existing One-Shotted execution?
