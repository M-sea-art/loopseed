#!/usr/bin/env bash

set -u -o pipefail

LOOPSEED_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SUBJECT="${1:-$LOOPSEED_ROOT/subject}"
EVIDENCE="${2:-$LOOPSEED_ROOT/evidence}"
SUBJECT_URL="https://github.com/PauliusOS/pallet-town-3d"
SUBJECT_EXPECTED_COMMIT="d49e0c0de836892133b3b21f50c9d29749879db5"
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

now_ms() {
  date +%s%3N
}

record_result() {
  local name="$1"
  local state="$2"
  local exit_code="$3"
  local elapsed_ms="$4"
  local log_file="$5"
  printf '%s\t%s\t%s\t%s\t%s\n' "$name" "$state" "$exit_code" "$elapsed_ms" "$log_file" >> "$RESULTS_TSV"
}

record_skipped() {
  local name="$1"
  local reason="$2"
  local log_file="$EVIDENCE/${name}.log"
  printf 'SKIPPED: %s\n' "$reason" > "$log_file"
  record_result "$name" "SKIPPED" 125 0 "$(basename "$log_file")"
}

run_step() {
  local name="$1"
  local log_name="$2"
  local command="$3"
  local start end code state
  start="$(now_ms)"
  (
    cd "$SUBJECT"
    bash -lc "$command"
  ) > "$EVIDENCE/$log_name" 2>&1
  code=$?
  end="$(now_ms)"
  state="PASS"
  if [[ $code -ne 0 ]]; then state="FAIL"; fi
  record_result "$name" "$state" "$code" "$((end - start))" "$log_name"
  return "$code"
}

if [[ ! -d "$SUBJECT/.git" ]]; then
  echo "Subject checkout missing: $SUBJECT" | tee "$EVIDENCE/fatal.log"
  record_skipped "npm_ci" "subject checkout missing"
  SUBJECT_COMMIT="missing"
else
  SUBJECT_COMMIT="$(git -C "$SUBJECT" rev-parse HEAD)"
fi

{
  echo "date_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "runner_os=${RUNNER_OS:-unknown}"
  echo "runner_arch=${RUNNER_ARCH:-unknown}"
  echo "github_repository=${GITHUB_REPOSITORY:-unknown}"
  echo "github_ref=${GITHUB_REF:-unknown}"
  echo "github_sha=${GITHUB_SHA:-unknown}"
  echo "subject_url=$SUBJECT_URL"
  echo "subject_expected_commit=$SUBJECT_EXPECTED_COMMIT"
  echo "subject_actual_commit=${SUBJECT_COMMIT:-missing}"
  echo "node=$(node --version 2>&1 || true)"
  echo "npm=$(npm --version 2>&1 || true)"
  echo "python=$(python3 --version 2>&1 || true)"
  uname -a
} > "$EVIDENCE/environment.txt"

INSTALL_CODE=125
CHECK_CODE=125
TEST_CODE=125
BUILD_CODE=125
BROWSER_CODE=125
PREVIEW_CODE=125
EXACT_CODE=125
FALLBACK_CODE=125
PROBE_CODE=125
CAPTURE_MODE="none"
FINAL_STATUS="BLOCKED"
FINAL_REASON="subject checkout unavailable"

if [[ "${SUBJECT_COMMIT:-missing}" != "missing" ]]; then
  run_step "npm_ci" "install.log" "npm ci"
  INSTALL_CODE=$?

  if [[ $INSTALL_CODE -eq 0 ]]; then
    run_step "typecheck" "check.log" "npm run check"
    CHECK_CODE=$?
    run_step "unit_tests" "test.log" "npm test"
    TEST_CODE=$?
    run_step "production_build" "build.log" "npm run build"
    BUILD_CODE=$?
  else
    record_skipped "typecheck" "npm ci failed"
    record_skipped "unit_tests" "npm ci failed"
    record_skipped "production_build" "npm ci failed"
  fi

  if [[ $INSTALL_CODE -ne 0 ]]; then
    FINAL_STATUS="BLOCKED"
    FINAL_REASON="dependency installation failed"
  elif [[ $CHECK_CODE -ne 0 || $TEST_CODE -ne 0 || $BUILD_CODE -ne 0 ]]; then
    FINAL_STATUS="FAIL"
    FINAL_REASON="one or more engineering gates failed"
  else
    run_step "playwright_browser" "playwright-install.log" "npx playwright install --with-deps chromium"
    BROWSER_CODE=$?

    if [[ $BROWSER_CODE -ne 0 ]]; then
      FINAL_STATUS="BLOCKED"
      FINAL_REASON="Chromium installation failed"
    else
      preview_start="$(now_ms)"
      (
        cd "$SUBJECT"
        npm run preview
      ) > "$EVIDENCE/preview.log" 2>&1 &
      PREVIEW_PID=$!

      preview_ready=0
      for _ in $(seq 1 90); do
        if curl --silent --fail "$PREVIEW_URL" >/dev/null 2>&1; then
          preview_ready=1
          break
        fi
        if ! kill -0 "$PREVIEW_PID" 2>/dev/null; then
          break
        fi
        sleep 1
      done
      preview_end="$(now_ms)"

      if [[ $preview_ready -eq 1 ]]; then
        PREVIEW_CODE=0
        record_result "preview_ready" "PASS" 0 "$((preview_end - preview_start))" "preview.log"

        run_step \
          "capture_exact" \
          "capture-exact.log" \
          "node tools/capture.mjs --url '$PREVIEW_URL' --out '$EVIDENCE/shots-exact' --shots town_reveal,lab_door,starters_out"
        EXACT_CODE=$?

        if [[ $EXACT_CODE -eq 0 ]]; then
          rm -rf "$EVIDENCE/shots"
          cp -a "$EVIDENCE/shots-exact" "$EVIDENCE/shots"
          CAPTURE_MODE="exact-metal-request"
          FINAL_STATUS="PASS"
          FINAL_REASON="all engineering gates and the unmodified three-shot capture passed"
        else
          cp "$SUBJECT/tools/capture.mjs" "$SUBJECT/tools/capture-loopseed-ci.mjs"
          python3 - "$SUBJECT/tools/capture-loopseed-ci.mjs" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
text = text.replace("'--use-angle=metal',", "'--use-angle=swiftshader',")
text = "\n".join(
    line for line in text.splitlines()
    if "--enable-unsafe-webgpu" not in line
) + "\n"
path.write_text(text, encoding="utf-8")
PY

          run_step \
            "capture_fallback" \
            "capture-fallback.log" \
            "node tools/capture-loopseed-ci.mjs --url '$PREVIEW_URL' --out '$EVIDENCE/shots-fallback' --shots town_reveal,lab_door,starters_out"
          FALLBACK_CODE=$?

          if [[ $FALLBACK_CODE -eq 0 ]]; then
            rm -rf "$EVIDENCE/shots"
            cp -a "$EVIDENCE/shots-fallback" "$EVIDENCE/shots"
            CAPTURE_MODE="swiftshader-fallback"
            FINAL_STATUS="PARTIAL"
            FINAL_REASON="engineering gates passed; exact Metal request failed on the Linux runner; all screenshots were produced by the declared SwiftShader fallback"
          else
            CAPTURE_MODE="none"
            FINAL_STATUS="BLOCKED"
            FINAL_REASON="both exact and declared fallback capture attempts failed"
          fi
        fi

        if [[ "$CAPTURE_MODE" != "none" ]]; then
          cp "$LOOPSEED_ROOT/experiments/c1.2-pallet-town/probe.mjs" "$SUBJECT/tools/c1-probe.mjs"
          PROBE_BACKEND="metal"
          if [[ "$CAPTURE_MODE" == "swiftshader-fallback" ]]; then PROBE_BACKEND="swiftshader"; fi
          run_step \
            "runtime_probe" \
            "probe.log" \
            "node tools/c1-probe.mjs --url '$PREVIEW_URL' --out '$EVIDENCE/probe.json' --backend '$PROBE_BACKEND'"
          PROBE_CODE=$?
          if [[ $PROBE_CODE -ne 0 && "$FINAL_STATUS" == "PASS" ]]; then
            FINAL_STATUS="PARTIAL"
            FINAL_REASON="visual capture passed, but the supplementary runtime-timing probe failed"
          fi
        else
          record_skipped "runtime_probe" "no successful capture backend"
        fi
      else
        PREVIEW_CODE=1
        record_result "preview_ready" "FAIL" 1 "$((preview_end - preview_start))" "preview.log"
        record_skipped "capture_exact" "preview server did not become ready"
        record_skipped "capture_fallback" "preview server did not become ready"
        record_skipped "runtime_probe" "preview server did not become ready"
        FINAL_STATUS="FAIL"
        FINAL_REASON="production build passed, but the preview server did not become ready"
      fi
    fi
  fi
fi

python3 - "$RESULTS_TSV" "$EVIDENCE/command-results.json" <<'PY'
import csv
import json
import sys
from pathlib import Path

source = Path(sys.argv[1])
target = Path(sys.argv[2])
rows = []
with source.open(encoding="utf-8") as handle:
    for name, state, exit_code, elapsed_ms, log_file in csv.reader(handle, delimiter="\t"):
        rows.append({
            "name": name,
            "state": state,
            "exitCode": int(exit_code),
            "elapsedMs": int(elapsed_ms),
            "logFile": log_file,
        })
target.write_text(json.dumps(rows, indent=2), encoding="utf-8")
PY

python3 - "$EVIDENCE" "$SUBJECT_EXPECTED_COMMIT" "${SUBJECT_COMMIT:-missing}" "$CAPTURE_MODE" "$FINAL_STATUS" "$FINAL_REASON" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
expected_commit = sys.argv[2]
actual_commit = sys.argv[3]
capture_mode = sys.argv[4]
status = sys.argv[5]
reason = sys.argv[6]

commands_path = root / "command-results.json"
commands = json.loads(commands_path.read_text(encoding="utf-8")) if commands_path.exists() else []
probe_path = root / "probe.json"
probe = json.loads(probe_path.read_text(encoding="utf-8")) if probe_path.exists() else None
manifest_path = root / "shots" / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else None
shot_files = sorted(path.name for path in (root / "shots").glob("*.png")) if (root / "shots").exists() else []
required_shots = ["town_reveal.png", "lab_door.png", "starters_out.png"]
missing_shots = [name for name in required_shots if name not in shot_files]

summary = {
    "experiment": "LOOPSEED C1.2 Pallet Town external evidence run",
    "status": status,
    "reason": reason,
    "subject": {
        "repository": "PauliusOS/pallet-town-3d",
        "expectedCommit": expected_commit,
        "actualCommit": actual_commit,
        "commitMatches": expected_commit == actual_commit,
    },
    "captureMode": capture_mode,
    "requiredShots": required_shots,
    "producedShots": shot_files,
    "missingShots": missing_shots,
    "visualCriticVerdict": "PENDING_INDEPENDENT_REVIEW" if not missing_shots else "NOT_REVIEWABLE",
    "commands": commands,
    "probe": probe,
    "captureManifest": manifest,
}

(root / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

lines = [
    "# LOOPSEED C1.2 run summary",
    "",
    f"- Status: **{status}**",
    f"- Reason: {reason}",
    f"- Subject commit: `{actual_commit}`",
    f"- Frozen commit matched: **{'yes' if expected_commit == actual_commit else 'no'}**",
    f"- Capture mode: `{capture_mode}`",
    f"- Required screenshots produced: **{len(required_shots) - len(missing_shots)}/{len(required_shots)}**",
    "- Visual critic verdict: **PENDING_INDEPENDENT_REVIEW**" if not missing_shots else "- Visual critic verdict: **NOT_REVIEWABLE**",
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

if probe and probe.get("status") == "PASS":
    runtime = probe.get("runtime", {})
    renderer = runtime.get("renderer", {})
    lines.extend([
        "",
        "## Runtime probe",
        "",
        f"- Page ready: `{probe.get('readyMs', 0):.0f} ms`",
        f"- World build steps total: `{runtime.get('buildTotalMs', 0):.0f} ms`",
        f"- Requested backend: `{renderer.get('requestedBackend')}`",
        f"- Actual renderer: `{renderer.get('actualRenderer')}`",
        f"- Actual vendor: `{renderer.get('actualVendor')}`",
        f"- Probe FPS: `{runtime.get('fps')}`",
        f"- Probe draw calls: `{runtime.get('render', {}).get('drawCalls')}`",
        f"- Probe triangles: `{runtime.get('render', {}).get('triangles')}`",
    ])

if manifest:
    lines.extend(["", "## Fixed shots", "", "| Shot | FPS | Draw calls | Triangles |", "|---|---:|---:|---:|"])
    for shot in manifest.get("shots", []):
        stats = shot.get("stats", {})
        lines.append(
            f"| {shot.get('id')} | {stats.get('fps')} | {stats.get('drawCalls')} | {stats.get('triangles')} |"
        )

lines.extend([
    "",
    "## Evidence boundary",
    "",
    "Engineering and capture status are machine-recorded. Visual quality remains unjudged until an independent critic inspects the three PNG files. SwiftShader FPS, when used, is not native-GPU performance evidence.",
])
(root / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
PY

cat "$EVIDENCE/summary.md"

if [[ "$FINAL_STATUS" == "FAIL" ]]; then
  exit 1
fi

# BLOCKED and PARTIAL are valid evidence outcomes; preserve and upload their receipts.
exit 0
