#!/usr/bin/env bash

set -u -o pipefail

LOOPSEED_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SUBJECT="${1:-$LOOPSEED_ROOT/subject}"
EVIDENCE="${2:-$LOOPSEED_ROOT/evidence}"
SUBJECT_EXPECTED_COMMIT="d49e0c0de836892133b3b21f50c9d29749879db5"
BASELINE_RUN_ID="30622497022"
PREVIEW_URL="http://127.0.0.1:4173/"
RESULTS_TSV="$EVIDENCE/command-results.tsv"

mkdir -p "$EVIDENCE"
: > "$RESULTS_TSV"

PREVIEW_PID=""
cleanup() {
  if [[ -n "$PREVIEW_PID" ]] && kill -0 "$PREVIEW_PID" 2>/dev/null; then
    kill "$PREVIEW_PID" 2>/dev/null || true
    wait "$PREVIEW_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

now_ms() { date +%s%3N; }

record_result() {
  printf '%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$5" >> "$RESULTS_TSV"
}

record_skipped() {
  local name="$1" reason="$2" log_file="$EVIDENCE/${name}.log"
  printf 'SKIPPED: %s\n' "$reason" > "$log_file"
  record_result "$name" "SKIPPED" 125 0 "$(basename "$log_file")"
}

run_step() {
  local name="$1" log_name="$2" command="$3"
  local start end code state
  start="$(now_ms)"
  (cd "$SUBJECT" && bash -lc "$command") > "$EVIDENCE/$log_name" 2>&1
  code=$?
  end="$(now_ms)"
  state="PASS"
  [[ $code -ne 0 ]] && state="FAIL"
  record_result "$name" "$state" "$code" "$((end - start))" "$log_name"
  return "$code"
}

SUBJECT_COMMIT="missing"
if [[ -d "$SUBJECT/.git" ]]; then
  SUBJECT_COMMIT="$(git -C "$SUBJECT" rev-parse HEAD)"
fi

{
  echo "experiment_round=2"
  echo "baseline_run_id=$BASELINE_RUN_ID"
  echo "date_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "runner_os=${RUNNER_OS:-unknown}"
  echo "runner_arch=${RUNNER_ARCH:-unknown}"
  echo "github_repository=${GITHUB_REPOSITORY:-unknown}"
  echo "github_ref=${GITHUB_REF:-unknown}"
  echo "github_sha=${GITHUB_SHA:-unknown}"
  echo "subject_expected_commit=$SUBJECT_EXPECTED_COMMIT"
  echo "subject_actual_commit=$SUBJECT_COMMIT"
  echo "node=$(node --version 2>&1 || true)"
  echo "npm=$(npm --version 2>&1 || true)"
  echo "python=$(python3 --version 2>&1 || true)"
  uname -a
} > "$EVIDENCE/environment.txt"

FINAL_STATUS="BLOCKED"
FINAL_REASON="subject checkout unavailable"
CAPTURE_MODE="none"

if [[ "$SUBJECT_COMMIT" == "missing" ]]; then
  record_skipped "npm_ci" "subject checkout missing"
  record_skipped "typecheck" "subject checkout missing"
  record_skipped "unit_tests" "subject checkout missing"
  record_skipped "production_build" "subject checkout missing"
  record_skipped "playwright_browser" "subject checkout missing"
  record_skipped "preview_ready" "subject checkout missing"
  record_skipped "capture_harness_repair" "subject checkout missing"
  record_skipped "runtime_probe" "subject checkout missing"
else
  run_step "npm_ci" "install.log" "npm ci"
  INSTALL_CODE=$?

  if [[ $INSTALL_CODE -eq 0 ]]; then
    run_step "typecheck" "check.log" "npm run check"; CHECK_CODE=$?
    run_step "unit_tests" "test.log" "npm test"; TEST_CODE=$?
    run_step "production_build" "build.log" "npm run build"; BUILD_CODE=$?
  else
    CHECK_CODE=125; TEST_CODE=125; BUILD_CODE=125
    record_skipped "typecheck" "npm ci failed"
    record_skipped "unit_tests" "npm ci failed"
    record_skipped "production_build" "npm ci failed"
  fi

  if [[ $INSTALL_CODE -ne 0 ]]; then
    FINAL_STATUS="BLOCKED"
    FINAL_REASON="dependency installation failed"
    record_skipped "playwright_browser" "npm ci failed"
    record_skipped "preview_ready" "npm ci failed"
    record_skipped "capture_harness_repair" "npm ci failed"
    record_skipped "runtime_probe" "npm ci failed"
  elif [[ $CHECK_CODE -ne 0 || $TEST_CODE -ne 0 || $BUILD_CODE -ne 0 ]]; then
    FINAL_STATUS="FAIL"
    FINAL_REASON="one or more engineering gates failed"
    record_skipped "playwright_browser" "engineering gate failed"
    record_skipped "preview_ready" "engineering gate failed"
    record_skipped "capture_harness_repair" "engineering gate failed"
    record_skipped "runtime_probe" "engineering gate failed"
  else
    run_step "playwright_browser" "playwright-install.log" "npx playwright install --with-deps chromium"
    BROWSER_CODE=$?

    if [[ $BROWSER_CODE -ne 0 ]]; then
      FINAL_STATUS="BLOCKED"
      FINAL_REASON="Chromium installation failed"
      record_skipped "preview_ready" "Chromium installation failed"
      record_skipped "capture_harness_repair" "Chromium installation failed"
      record_skipped "runtime_probe" "Chromium installation failed"
    else
      preview_start="$(now_ms)"
      (cd "$SUBJECT" && npm run preview) > "$EVIDENCE/preview.log" 2>&1 &
      PREVIEW_PID=$!
      preview_ready=0
      for _ in $(seq 1 90); do
        if curl --silent --fail "$PREVIEW_URL" >/dev/null 2>&1; then
          preview_ready=1
          break
        fi
        if ! kill -0 "$PREVIEW_PID" 2>/dev/null; then break; fi
        sleep 1
      done
      preview_end="$(now_ms)"

      if [[ $preview_ready -ne 1 ]]; then
        record_result "preview_ready" "FAIL" 1 "$((preview_end - preview_start))" "preview.log"
        record_skipped "capture_harness_repair" "preview server did not become ready"
        record_skipped "runtime_probe" "preview server did not become ready"
        FINAL_STATUS="FAIL"
        FINAL_REASON="production build passed, but preview did not become ready"
      else
        record_result "preview_ready" "PASS" 0 "$((preview_end - preview_start))" "preview.log"

        cp "$SUBJECT/tools/capture.mjs" "$SUBJECT/tools/capture-loopseed-repair.mjs"
        python3 - "$SUBJECT/tools/capture-loopseed-repair.mjs" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
text = text.replace("'--use-angle=metal',", "'--use-angle=swiftshader',")
text = "\n".join(line for line in text.splitlines() if "--enable-unsafe-webgpu" not in line) + "\n"
needle = "const consoleErrors = [];"
replacement = "// LOOPSEED CI adapter: the original waitForFunction call passes its timeout object as arg.\n// Set the page default explicitly so the procedural world may finish on software rendering.\npage.setDefaultTimeout(240000);\n\nconst consoleErrors = [];"
if needle not in text:
    raise SystemExit("capture adapter insertion point not found")
text = text.replace(needle, replacement, 1)
path.write_text(text, encoding="utf-8")
PY
        diff -u "$SUBJECT/tools/capture.mjs" "$SUBJECT/tools/capture-loopseed-repair.mjs" > "$EVIDENCE/capture-adapter.diff" || true

        run_step \
          "capture_harness_repair" \
          "capture-repair.log" \
          "node tools/capture-loopseed-repair.mjs --url '$PREVIEW_URL' --out '$EVIDENCE/shots' --shots town_reveal,lab_door,starters_out"
        CAPTURE_CODE=$?

        if [[ $CAPTURE_CODE -eq 0 ]]; then
          CAPTURE_MODE="ci-timeout-repair-swiftshader"
          FINAL_STATUS="PARTIAL"
          FINAL_REASON="engineering gates passed and all fixed shots were produced through a declared CI adapter that corrected the capture timeout behavior and requested SwiftShader"

          cp "$LOOPSEED_ROOT/experiments/c1.2-pallet-town/probe.mjs" "$SUBJECT/tools/c1-probe.mjs"
          run_step \
            "runtime_probe" \
            "probe.log" \
            "node tools/c1-probe.mjs --url '$PREVIEW_URL' --out '$EVIDENCE/probe.json' --backend swiftshader"
          PROBE_CODE=$?
          if [[ $PROBE_CODE -ne 0 ]]; then
            FINAL_REASON="$FINAL_REASON; supplementary runtime probe failed"
          fi
        else
          record_skipped "runtime_probe" "repaired capture failed"
          FINAL_STATUS="BLOCKED"
          FINAL_REASON="the bounded timeout/backend CI adapter still could not produce the required screenshots"
        fi
      fi
    fi
  fi
fi

python3 - "$RESULTS_TSV" "$EVIDENCE/command-results.json" <<'PY'
import csv, json, sys
from pathlib import Path
rows = []
with Path(sys.argv[1]).open(encoding="utf-8") as handle:
    for name, state, exit_code, elapsed_ms, log_file in csv.reader(handle, delimiter="\t"):
        rows.append({"name": name, "state": state, "exitCode": int(exit_code), "elapsedMs": int(elapsed_ms), "logFile": log_file})
Path(sys.argv[2]).write_text(json.dumps(rows, indent=2), encoding="utf-8")
PY

python3 - "$EVIDENCE" "$SUBJECT_EXPECTED_COMMIT" "$SUBJECT_COMMIT" "$CAPTURE_MODE" "$FINAL_STATUS" "$FINAL_REASON" "$BASELINE_RUN_ID" <<'PY'
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
expected, actual, mode, status, reason, baseline = sys.argv[2:]
commands = json.loads((root / "command-results.json").read_text(encoding="utf-8"))
probe = json.loads((root / "probe.json").read_text(encoding="utf-8")) if (root / "probe.json").exists() else None
manifest = json.loads((root / "shots" / "manifest.json").read_text(encoding="utf-8")) if (root / "shots" / "manifest.json").exists() else None
produced = sorted(p.name for p in (root / "shots").glob("*.png")) if (root / "shots").exists() else []
required = ["town_reveal.png", "lab_door.png", "starters_out.png"]
missing = [name for name in required if name not in produced]
summary = {
  "experiment": "LOOPSEED C1.2 Pallet Town external evidence run",
  "round": 2,
  "baselineRunId": int(baseline),
  "status": status,
  "reason": reason,
  "subject": {"repository": "PauliusOS/pallet-town-3d", "expectedCommit": expected, "actualCommit": actual, "commitMatches": expected == actual},
  "captureMode": mode,
  "adapterScope": ["request SwiftShader on Linux", "set Playwright page default timeout to 240000 ms"],
  "requiredShots": required,
  "producedShots": produced,
  "missingShots": missing,
  "visualCriticVerdict": "PENDING_INDEPENDENT_REVIEW" if not missing else "NOT_REVIEWABLE",
  "commands": commands,
  "probe": probe,
  "captureManifest": manifest,
}
(root / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

lines = [
  "# LOOPSEED C1.2 repair verification",
  "",
  f"- Status: **{status}**",
  f"- Reason: {reason}",
  f"- Baseline run: `{baseline}`",
  f"- Subject commit: `{actual}`",
  f"- Frozen commit matched: **{'yes' if expected == actual else 'no'}**",
  f"- Capture mode: `{mode}`",
  f"- Required screenshots produced: **{len(required)-len(missing)}/{len(required)}**",
  "- Visual critic verdict: **PENDING_INDEPENDENT_REVIEW**" if not missing else "- Visual critic verdict: **NOT_REVIEWABLE**",
  "",
  "## Commands",
  "",
  "| Gate | State | Exit | Elapsed ms | Log |",
  "|---|---:|---:|---:|---|",
]
for item in commands:
    lines.append(f"| {item['name']} | {item['state']} | {item['exitCode']} | {item['elapsedMs']} | `{item['logFile']}` |")
if probe and probe.get("status") == "PASS":
    runtime = probe.get("runtime", {})
    renderer = runtime.get("renderer", {})
    lines += [
      "", "## Runtime probe", "",
      f"- Page ready: `{probe.get('readyMs', 0):.0f} ms`",
      f"- World build total: `{runtime.get('buildTotalMs', 0):.0f} ms`",
      f"- Actual renderer: `{renderer.get('actualRenderer')}`",
      f"- Actual vendor: `{renderer.get('actualVendor')}`",
      f"- Probe FPS: `{runtime.get('fps')}`",
      f"- Probe draw calls: `{runtime.get('render', {}).get('drawCalls')}`",
      f"- Probe triangles: `{runtime.get('render', {}).get('triangles')}`",
    ]
if manifest:
    lines += ["", "## Fixed shots", "", "| Shot | FPS | Draw calls | Triangles |", "|---|---:|---:|---:|"]
    for shot in manifest.get("shots", []):
        stats = shot.get("stats", {})
        lines.append(f"| {shot.get('id')} | {stats.get('fps')} | {stats.get('drawCalls')} | {stats.get('triangles')} |")
lines += [
  "", "## Evidence boundary", "",
  "The external source is unchanged. This round repairs only the CI observation adapter. SwiftShader FPS is not native-GPU performance evidence. Visual quality remains pending until an independent critic inspects the three PNG files.",
]
(root / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
PY

cat "$EVIDENCE/summary.md"
[[ "$FINAL_STATUS" == "FAIL" ]] && exit 1
exit 0
