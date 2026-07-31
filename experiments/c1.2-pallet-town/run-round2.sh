#!/usr/bin/env bash

# Final bounded C1.2 run. Every non-zero result is converted into an evidence
# receipt; the external subject remains read-only.
set +e
set -u -o pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SUBJECT="${1:-$ROOT/subject}"
EVIDENCE="${2:-$ROOT/evidence}"
EXPECTED_SHA="d49e0c0de836892133b3b21f50c9d29749879db5"
PREVIEW_URL="http://127.0.0.1:4173/"
TSV="$EVIDENCE/command-results.tsv"
mkdir -p "$EVIDENCE"
: > "$TSV"

PREVIEW_PID=""
cleanup() {
  if [[ -n "$PREVIEW_PID" ]] && kill -0 "$PREVIEW_PID" 2>/dev/null; then
    kill "$PREVIEW_PID" 2>/dev/null || true
    wait "$PREVIEW_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

now_ms() { date +%s%3N; }
record() { printf '%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$5" >> "$TSV"; }
skip() {
  local name="$1" reason="$2" log="$EVIDENCE/$1.log"
  printf 'SKIPPED: %s\n' "$reason" > "$log"
  record "$name" "SKIPPED" 125 0 "$(basename "$log")"
}
run_step() {
  local name="$1" log="$2" command="$3" start end code state
  start="$(now_ms)"
  (cd "$SUBJECT" && bash -lc "$command") > "$EVIDENCE/$log" 2>&1
  code=$?
  end="$(now_ms)"
  state="PASS"; [[ $code -ne 0 ]] && state="FAIL"
  record "$name" "$state" "$code" "$((end-start))" "$log"
  return "$code"
}

ACTUAL_SHA="missing"
[[ -d "$SUBJECT/.git" ]] && ACTUAL_SHA="$(git -C "$SUBJECT" rev-parse HEAD)"

{
  echo "experiment_round=final-diagnostic"
  echo "prior_run_1=30622497022"
  echo "prior_run_2=30622840618"
  echo "cancelled_postfx_run=30624140799"
  echo "date_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "github_sha=${GITHUB_SHA:-unknown}"
  echo "runner_os=${RUNNER_OS:-unknown}"
  echo "runner_arch=${RUNNER_ARCH:-unknown}"
  echo "subject_expected_commit=$EXPECTED_SHA"
  echo "subject_actual_commit=$ACTUAL_SHA"
  echo "node=$(node --version 2>&1 || true)"
  echo "npm=$(npm --version 2>&1 || true)"
  uname -a
} > "$EVIDENCE/environment.txt"

STATUS="BLOCKED"
REASON="subject checkout unavailable"
MODE="none"

if [[ "$ACTUAL_SHA" == "missing" ]]; then
  for gate in npm_ci typecheck unit_tests production_build playwright_browser preview_ready diagnostic_capture; do
    skip "$gate" "subject checkout missing"
  done
else
  run_step npm_ci install.log "npm ci"; INSTALL=$?
  if [[ $INSTALL -eq 0 ]]; then
    run_step typecheck check.log "npm run check"; CHECK=$?
    run_step unit_tests test.log "npm test"; TEST=$?
    run_step production_build build.log "npm run build"; BUILD=$?
  else
    CHECK=125; TEST=125; BUILD=125
    skip typecheck "npm ci failed"; skip unit_tests "npm ci failed"; skip production_build "npm ci failed"
  fi

  if [[ $INSTALL -ne 0 ]]; then
    REASON="dependency installation failed"
    skip playwright_browser "npm ci failed"; skip preview_ready "npm ci failed"; skip diagnostic_capture "npm ci failed"
  elif [[ $CHECK -ne 0 || $TEST -ne 0 || $BUILD -ne 0 ]]; then
    STATUS="FAIL"; REASON="one or more engineering gates failed"
    skip playwright_browser "engineering gate failed"; skip preview_ready "engineering gate failed"; skip diagnostic_capture "engineering gate failed"
  else
    run_step playwright_browser playwright-install.log "npx playwright install --with-deps chromium"; BROWSER=$?
    if [[ $BROWSER -ne 0 ]]; then
      REASON="Chromium installation failed"
      skip preview_ready "Chromium installation failed"; skip diagnostic_capture "Chromium installation failed"
    else
      start="$(now_ms)"
      (cd "$SUBJECT" && npm run preview) > "$EVIDENCE/preview.log" 2>&1 &
      PREVIEW_PID=$!
      ready=0
      for _ in $(seq 1 90); do
        curl --silent --fail "$PREVIEW_URL" >/dev/null 2>&1 && { ready=1; break; }
        kill -0 "$PREVIEW_PID" 2>/dev/null || break
        sleep 1
      done
      end="$(now_ms)"

      if [[ $ready -ne 1 ]]; then
        record preview_ready FAIL 1 "$((end-start))" preview.log
        skip diagnostic_capture "preview server did not become ready"
        STATUS="FAIL"; REASON="production build passed, but preview did not become ready"
      else
        record preview_ready PASS 0 "$((end-start))" preview.log
        cp "$ROOT/experiments/c1.2-pallet-town/capture-ci-final.mjs" "$SUBJECT/tools/capture-loopseed-final.mjs"
        run_step diagnostic_capture capture-final.log \
          "timeout --signal=TERM --kill-after=15s 420s node tools/capture-loopseed-final.mjs --url '$PREVIEW_URL' --out '$EVIDENCE/shots' --width 800 --height 450"
        CAPTURE=$?
        COUNT="$(find "$EVIDENCE/shots" -maxdepth 1 -name '*.png' -type f 2>/dev/null | wc -l | tr -d ' ')"

        if [[ $CAPTURE -eq 0 && "$COUNT" == "3" ]]; then
          STATUS="PARTIAL"
          MODE="direct-webgl-base-render-swiftshader-800x450"
          REASON="engineering gates passed and all three fixed scenes were captured through the declared base-render diagnostic adapter; production post-processing, native GPU performance, and AAA parity remain unverified"
          sha256sum "$EVIDENCE"/shots/*.png > "$EVIDENCE/shot-sha256.txt"
          file "$EVIDENCE"/shots/*.png > "$EVIDENCE/shot-files.txt"
        elif [[ $CAPTURE -eq 124 || $CAPTURE -eq 137 ]]; then
          REASON="final diagnostic capture hit its 420-second hard stop"
        elif [[ $CAPTURE -eq 0 ]]; then
          REASON="capture command returned success but did not produce exactly three PNG files"
        else
          REASON="final base-render diagnostic adapter failed; see capture-final.log and manifest.json"
        fi
      fi
    fi
  fi
fi

python3 - "$TSV" "$EVIDENCE/command-results.json" <<'PY'
import csv, json, sys
from pathlib import Path
rows=[]
with Path(sys.argv[1]).open(encoding='utf-8') as f:
    for row in csv.reader(f, delimiter='\t'):
        if len(row)==5:
            n,s,c,m,l=row
            rows.append({'name':n,'state':s,'exitCode':int(c),'elapsedMs':int(m),'logFile':l})
Path(sys.argv[2]).write_text(json.dumps(rows,indent=2),encoding='utf-8')
PY

python3 - "$EVIDENCE" "$EXPECTED_SHA" "$ACTUAL_SHA" "$MODE" "$STATUS" "$REASON" <<'PY'
import json, sys
from pathlib import Path
root=Path(sys.argv[1]); expected,actual,mode,status,reason=sys.argv[2:]
commands=json.loads((root/'command-results.json').read_text())
manifest_path=root/'shots'/'manifest.json'
manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else None
produced=sorted(p.name for p in (root/'shots').glob('*.png')) if (root/'shots').exists() else []
required=['town_reveal.png','lab_door.png','starters_out.png']
missing=[x for x in required if x not in produced]
summary={
 'experiment':'LOOPSEED C1.2 Pallet Town external evidence run',
 'round':'final-diagnostic',
 'priorRuns':[30622497022,30622840618,30624140799],
 'status':status,'reason':reason,
 'subject':{'repository':'PauliusOS/pallet-town-3d','expectedCommit':expected,'actualCommit':actual,'commitMatches':expected==actual},
 'captureMode':mode,
 'adapterScope':{'renderer':'SwiftShader','viewport':'800x450','renderPath':'base Three.js renderer; no project post-processing','shadows':False,'externalSourceModified':False,'hardStopSeconds':420},
 'requiredShots':required,'producedShots':produced,'missingShots':missing,
 'visualCriticVerdict':'PENDING_DIAGNOSTIC_REVIEW' if not missing else 'NOT_REVIEWABLE',
 'commands':commands,'captureManifest':manifest,
}
(root/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
lines=[
 '# LOOPSEED C1.2 final diagnostic run','',f'- Status: **{status}**',f'- Reason: {reason}',
 f'- Subject commit: `{actual}`',f"- Frozen commit matched: **{'yes' if expected==actual else 'no'}**",
 f'- Capture mode: `{mode}`',f'- Required screenshots produced: **{len(required)-len(missing)}/{len(required)}**',
 '- Visual critic verdict: **PENDING_DIAGNOSTIC_REVIEW**' if not missing else '- Visual critic verdict: **NOT_REVIEWABLE**',
 '', '## Commands','', '| Gate | State | Exit | Elapsed ms | Log |','|---|---:|---:|---:|---|'
]
for x in commands:
 lines.append(f"| {x['name']} | {x['state']} | {x['exitCode']} | {x['elapsedMs']} | `{x['logFile']}` |")
if manifest and manifest.get('status')=='PASS':
 r=manifest.get('runtime',{})
 lines += ['', '## Diagnostic runtime','',f"- Page ready: `{manifest.get('readyMs',0):.0f} ms`",f"- World build total: `{r.get('buildTotalMs',0):.0f} ms`",f"- Actual renderer: `{r.get('actualRenderer')}`",f"- Viewport: `{r.get('viewport')}`",f"- Render path: `{r.get('qualityTier')}`",'', '## Fixed scenes','', '| Scene | KiB | Draw calls | Triangles | Mean luminance | Variance |','|---|---:|---:|---:|---:|---:|']
 for shot in manifest.get('shots',[]):
  st=shot.get('stats',{}); sm=shot.get('sample',{})
  lines.append(f"| {shot.get('id')} | {shot.get('bytes',0)/1024:.0f} | {st.get('drawCalls')} | {st.get('triangles')} | {sm.get('meanLuminance',0):.1f} | {sm.get('luminanceVariance',0):.1f} |")
lines += ['', '## Evidence boundary','', 'This diagnostic deliberately bypasses the production post-processing chain, disables shadows, and uses SwiftShader at 800×450. It may establish scene observability only. It cannot establish native high-quality performance or AAA visual parity.']
(root/'summary.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
PY

cat "$EVIDENCE/summary.md"
[[ "$STATUS" == "FAIL" ]] && exit 1
exit 0
