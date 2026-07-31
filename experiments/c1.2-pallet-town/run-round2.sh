#!/usr/bin/env bash

# Final bounded C1.2 observation attempt. Failures are recorded as evidence
# instead of aborting before summary generation.
set +e
set -u -o pipefail

LOOPSEED_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SUBJECT="${1:-$LOOPSEED_ROOT/subject}"
EVIDENCE="${2:-$LOOPSEED_ROOT/evidence}"
SUBJECT_EXPECTED_COMMIT="d49e0c0de836892133b3b21f50c9d29749879db5"
PREVIEW_URL="http://127.0.0.1:4173/"
RESULTS_TSV="$EVIDENCE/command-results.tsv"
BASELINE_RUN_ID="30622497022"
TIMEOUT_REPAIR_RUN_ID="30622840618"

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
  echo "experiment_round=3-final"
  echo "baseline_run_id=$BASELINE_RUN_ID"
  echo "timeout_repair_run_id=$TIMEOUT_REPAIR_RUN_ID"
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
  record_skipped "direct_canvas_capture" "subject checkout missing"
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
    record_skipped "direct_canvas_capture" "npm ci failed"
  elif [[ $CHECK_CODE -ne 0 || $TEST_CODE -ne 0 || $BUILD_CODE -ne 0 ]]; then
    FINAL_STATUS="FAIL"
    FINAL_REASON="one or more engineering gates failed"
    record_skipped "playwright_browser" "engineering gate failed"
    record_skipped "preview_ready" "engineering gate failed"
    record_skipped "direct_canvas_capture" "engineering gate failed"
  else
    run_step "playwright_browser" "playwright-install.log" "npx playwright install --with-deps chromium"
    BROWSER_CODE=$?

    if [[ $BROWSER_CODE -ne 0 ]]; then
      FINAL_STATUS="BLOCKED"
      FINAL_REASON="Chromium installation failed"
      record_skipped "preview_ready" "Chromium installation failed"
      record_skipped "direct_canvas_capture" "Chromium installation failed"
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
        record_skipped "direct_canvas_capture" "preview server did not become ready"
        FINAL_STATUS="FAIL"
        FINAL_REASON="production build passed, but preview did not become ready"
      else
        record_result "preview_ready" "PASS" 0 "$((preview_end - preview_start))" "preview.log"

        cp "$LOOPSEED_ROOT/experiments/c1.2-pallet-town/capture-ci-final.mjs" \
          "$SUBJECT/tools/capture-loopseed-final.mjs"

        run_step \
          "direct_canvas_capture" \
          "capture-final.log" \
          "node tools/capture-loopseed-final.mjs --url '$PREVIEW_URL' --out '$EVIDENCE/shots' --width 800 --height 450"
        CAPTURE_CODE=$?

        if [[ $CAPTURE_CODE -eq 0 ]]; then
          SHOT_COUNT="$(find "$EVIDENCE/shots" -maxdepth 1 -name '*.png' -type f | wc -l | tr -d ' ')"
          if [[ "$SHOT_COUNT" == "3" ]]; then
            CAPTURE_MODE="direct-webgl-canvas-swiftshader-low-800x450"
            FINAL_STATUS="PARTIAL"
            FINAL_REASON="all engineering gates passed and all three fixed shots were produced by the declared degraded CI observation adapter; native high-quality performance and visual parity remain unverified"
            sha256sum "$EVIDENCE"/shots/*.png > "$EVIDENCE/shot-sha256.txt"
            file "$EVIDENCE"/shots/*.png > "$EVIDENCE/shot-files.txt"
          else
            FINAL_STATUS="BLOCKED"
            FINAL_REASON="capture command returned success but did not produce exactly three PNG files"
          fi
        else
          FINAL_STATUS="BLOCKED"
          FINAL_REASON="final bounded direct-canvas adapter could not produce the three required screenshots"
        fi
      fi
    fi
  fi
fi

python3 - "$RESULTS_TSV" "$EVIDENCE/command-results.json" <<'PY'
import csv, json, sys
from pathlib import Path
rows = []
source = Path(sys.argv[1])
if source.exists():
    with source.open(encoding="utf-8") as handle:
        for row in csv.reader(handle, delimiter="\t"):
            if len(row) != 5:
                continue
            name, state, exit_code, elapsed_ms, log_file = row
            rows.append({
                "name": name,
                "state": state,
                "exitCode": int(exit_code),
                "elapsedMs": int(elapsed_ms),
                "logFile": log_file,
            })
Path(sys.argv[2]).write_text(json.dumps(rows, indent=2), encoding="utf-8")
PY

python3 - "$EVIDENCE" "$SUBJECT_EXPECTED_COMMIT" "$SUBJECT_COMMIT" "$CAPTURE_MODE" "$FINAL_STATUS" "$FINAL_REASON" "$BASELINE_RUN_ID" "$TIMEOUT_REPAIR_RUN_ID" <<'PY'
import json, sys
from pathlib import Path

root = Path(sys.argv[1])
expected, actual, mode, status, reason, baseline, repair = sys.argv[2:]
commands = json.loads((root / "command-results.json").read_text(encoding="utf-8"))
manifest_path = root / "shots" / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else None
produced = sorted(path.name for path in (root / "shots").glob("*.png")) if (root / "shots").exists() else []
required = ["town_reveal.png", "lab_door.png", "starters_out.png"]
missing = [name for name in required if name not in produced]

summary = {
    "experiment": "LOOPSEED C1.2 Pallet Town external evidence run",
    "round": "3-final",
    "priorRuns": [int(baseline), int(repair)],
    "status": status,
    "reason": reason,
    "subject": {
        "repository": "PauliusOS/pallet-town-3d",
        "expectedCommit": expected,
        "actualCommit": actual,
        "commitMatches": expected == actual,
    },
    "captureMode": mode,
    "adapterScope": {
        "renderer": "SwiftShader",
        "viewport": "800x450",
        "qualityTier": "low",
        "readback": "direct WebGL canvas, not browser page screenshot",
        "externalSourceModified": False,
    },
    "requiredShots": required,
    "producedShots": produced,
    "missingShots": missing,
    "visualCriticVerdict": "PENDING_INDEPENDENT_REVIEW" if not missing else "NOT_REVIEWABLE",
    "commands": commands,
    "captureManifest": manifest,
}
(root / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

lines = [
    "# LOOPSEED C1.2 final bounded run",
    "",
    f"- Status: **{status}**",
    f"- Reason: {reason}",
    f"- Prior runs: `{baseline}`, `{repair}`",
    f"- Subject commit: `{actual}`",
    f"- Frozen commit matched: **{'yes' if expected == actual else 'no'}**",
    f"- Capture mode: `{mode}`",
    f"- Required screenshots produced: **{len(required) - len(missing)}/{len(required)}**",
    "- Visual critic verdict: **PENDING_INDEPENDENT_REVIEW**" if not missing else "- Visual critic verdict: **NOT_REVIEWABLE**",
    "",
    "## Commands",
    "",
    "| Gate | State | Exit | Elapsed ms | Log |",
    "|---|---:|---:|---:|---|",
]
for item in commands:
    lines.append(
        f"| {item['name']} | {item['state']} | {item['exitCode']} | {item['elapsedMs']} | `{item['logFile']}` |"
    )

if manifest and manifest.get("status") == "PASS":
    runtime = manifest.get("runtime", {})
    lines.extend([
        "",
        "## Degraded observation runtime",
        "",
        f"- Page ready: `{manifest.get('readyMs', 0):.0f} ms`",
        f"- World build total: `{runtime.get('buildTotalMs', 0):.0f} ms`",
        f"- Actual renderer: `{runtime.get('actualRenderer')}`",
        f"- Actual vendor: `{runtime.get('actualVendor')}`",
        f"- Viewport: `{runtime.get('viewport')}`",
        f"- Quality tier: `{runtime.get('qualityTier')}`",
        "",
        "## Fixed shots",
        "",
        "| Shot | KiB | FPS before freeze | Draw calls | Triangles | Mean luminance | Variance |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for shot in manifest.get("shots", []):
        stats = shot.get("stats", {})
        sample = shot.get("sample", {})
        lines.append(
            f"| {shot.get('id')} | {shot.get('bytes', 0) / 1024:.0f} | "
            f"{stats.get('fpsBeforeFreeze')} | {stats.get('drawCalls')} | {stats.get('triangles')} | "
            f"{sample.get('meanLuminance', 0):.1f} | {sample.get('luminanceVariance', 0):.1f} |"
        )

lines.extend([
    "",
    "## Evidence boundary",
    "",
    "This is the final bounded CI adapter attempt. The subject source stayed unchanged. SwiftShader, low quality, 800×450 rendering, and direct-canvas readback are diagnostic evidence only; their FPS and appearance cannot establish native high-quality performance or AAA parity.",
])
(root / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
PY

cat "$EVIDENCE/summary.md"

if [[ "$FINAL_STATUS" == "FAIL" ]]; then
  exit 1
fi
exit 0
