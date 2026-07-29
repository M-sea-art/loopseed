#!/usr/bin/env python3
"""Validate the durable artifact produced by the minimal C1 rerun."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--approval", type=Path, required=True)
    args = parser.parse_args()

    payload = json.loads(args.artifact.read_text(encoding="utf-8"))
    expected = {
        "artifact_type": "loopseed-c1-delivery-receipt",
        "schema_version": 1,
        "test_id": "2026-07-29-c1-minimal-rerun",
        "repository": "M-sea-art/loopseed",
        "source_commit": "09a279f",
        "delivery_status": "ready",
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            raise SystemExit(f"{key}: expected {value!r}, got {payload.get(key)!r}")

    approval = args.approval.read_text(encoding="utf-8").strip()
    if approval != "C1-INDEPENDENT-VERIFY-READY":
        raise SystemExit("independent verification approval is invalid")

    print(
        json.dumps(
            {
                "ok": True,
                "test_id": payload["test_id"],
                "artifact": str(args.artifact),
                "approval": str(args.approval),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
