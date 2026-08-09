from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / ".codex-plugin" / "plugin.json"
GUIDE = ROOT / "docs" / "usage-guide.zh-CN.md"


def fail(message: str) -> int:
    print(f"usage-guide-version: FAIL: {message}", file=sys.stderr)
    return 1


def main() -> int:
    try:
        plugin = json.loads(PLUGIN.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return fail(f"cannot read plugin metadata: {exc}")

    try:
        guide = GUIDE.read_text(encoding="utf-8")
    except OSError as exc:
        return fail(f"cannot read production usage guide: {exc}")

    plugin_version = str(plugin.get("version", "")).strip()
    if not plugin_version:
        return fail("plugin version is empty")

    match = re.search(
        r'^loopseed_version:\s*["\']?([^"\'\s]+)["\']?\s*$',
        guide,
        flags=re.MULTILINE,
    )
    if match is None:
        return fail("docs/usage-guide.zh-CN.md lacks loopseed_version front matter")

    guide_version = match.group(1)
    if guide_version != plugin_version:
        return fail(
            f"guide declares {guide_version}, plugin declares {plugin_version}; "
            "update the production truth page with every version upgrade"
        )

    if 'update_policy: "required-on-every-version-upgrade"' not in guide:
        return fail("usage guide must retain required-on-every-version-upgrade policy")

    print(f"usage-guide-version: PASS: {plugin_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
