#!/usr/bin/env python3
"""Fail closed when the production usage guide is stale for a release version."""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_PATH = ROOT / ".codex-plugin" / "plugin.json"
GUIDE_PATH = ROOT / "docs" / "usage-guide.zh-CN.md"


def fail(message: str) -> None:
    print(f"USAGE_GUIDE_VERSION_FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def front_matter_value(text: str, key: str) -> str:
    pattern = rf"(?m)^{re.escape(key)}:\s*[\"']?([^\"'\n]+)[\"']?\s*$"
    match = re.search(pattern, text)
    if not match:
        fail(f"missing front matter field: {key}")
    return match.group(1).strip()


def main() -> None:
    if not PLUGIN_PATH.is_file():
        fail(f"plugin manifest not found: {PLUGIN_PATH.relative_to(ROOT)}")
    if not GUIDE_PATH.is_file():
        fail(f"usage guide not found: {GUIDE_PATH.relative_to(ROOT)}")

    plugin = json.loads(PLUGIN_PATH.read_text(encoding="utf-8"))
    plugin_version = str(plugin.get("version", "")).strip()
    if not plugin_version:
        fail("plugin version is missing")

    guide = GUIDE_PATH.read_text(encoding="utf-8")
    guide_version = front_matter_value(guide, "loopseed_version")
    update_policy = front_matter_value(guide, "update_policy")
    updated = front_matter_value(guide, "last_updated")

    if guide_version != plugin_version:
        fail(
            "guide version does not match plugin version: "
            f"guide={guide_version!r}, plugin={plugin_version!r}. "
            "Update docs/usage-guide.zh-CN.md in the same upgrade."
        )

    if update_policy != "required-on-every-version-upgrade":
        fail("usage guide update_policy must remain required-on-every-version-upgrade")

    try:
        date.fromisoformat(updated)
    except ValueError as exc:
        fail(f"last_updated must be an ISO date: {updated!r} ({exc})")

    required_sections = (
        "## 1. 先选最轻的模式",
        "## 2. 当前版本怎么选",
        "## 9. 成本纪律",
        "## 11. 每次升级必须同步更新本文",
    )
    missing = [section for section in required_sections if section not in guide]
    if missing:
        fail(f"required usage sections are missing: {', '.join(missing)}")

    print(
        "USAGE_GUIDE_VERSION_PASS: "
        f"version={plugin_version} guide={GUIDE_PATH.relative_to(ROOT)} updated={updated}"
    )


if __name__ == "__main__":
    main()
