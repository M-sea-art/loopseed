# Evidence Chain

**Arm:** `C0 PROTOCOL_ONLY`

This chain applies the fixed v0.5 Evidence-Governed overlay as a protocol. It does not claim an executable v0.5 Runtime.

| Link | Command / action | Result | Artifact / runtime state | Capture | Verdict |
|---|---|---|---|---|---|
| Binding | `git rev-parse`, branch inspection, target freeze | repository, branch, and baseline resolved | `PROJECT_BINDING_RECEIPT.md` | receipt SHA-256 `77bef6…12b4` | PASS |
| Source validity | `node --check game.js` | exit 0 | `game.js` SHA-256 `b975e8…59c6` | terminal result | PASS |
| Local serve | `python -m http.server 4173` + `curl` | HTTP 200, `text/html`, 5613 bytes | `index.html` SHA-256 `2865cf…976` | terminal result | PASS |
| State transitions | `node evidence/verify-runtime.mjs` | 9 assertions pass across two full paths | visible light sequences `7→5→2` and `6→4→2` | `evidence/runner-output.json` | PASS for deterministic static behavior |
| Ending branch | same deterministic runner | endings `shared-dawn` and `medicine` differ | two decision ledgers, each with exactly 3 nights | `evidence/runner-output.json` | PASS for deterministic static behavior |
| Browser boot | Cloud browser opens `http://127.0.0.1:4173/` | `ERR_BLOCKED_BY_CLIENT` | no browser runtime state available | `evidence/browser-block.txt` | BLOCKED |
| File fallback | Cloud browser opens synchronized local file | rejected by browser URL policy | no browser runtime state available | `evidence/browser-block.txt` | BLOCKED |
| Runtime visual | actual browser screenshot review | not executable on this surface | 0 screenshots captured of maximum 3 | `evidence/browser-block.txt` | PENDING unified test bench |
| Harness recovery | shared internal Agent Preview loads the frozen artifact | page title and meaningful first screen present; no preview-originated console warning/error | actual browser runtime state | `evidence/lead-verification.md` | PASS |
| Runtime paths | fixed path and alternate path completed in the Cloud Browser | lamp sequences `7→5→2` and `6→4→2`; endings `雨声成诗` and `百草回春` | two terminal ledgers with three nights each | `evidence/lead-verification.md` | PASS |
| Runtime visual | initial, post-choice, and terminal captures | all required visual and state elements legible | 3 screenshots captured of maximum 3 | `evidence/screenshots/` | PASS |

## Artifact hashes

- `index.html`: `2865cf98bf490ac800d6434a676d99f5f5535ed7c23937753d9fa9a44c316976`
- `styles.css`: `5b6bd0d90f369b83c39c6bccf468b46bf4868d58aa82cf32b2948330aaabbfff`
- `game.js`: `b975e8ce26a4189519cd21bfef019771a75894077bca04477eb3d9facb9e59c6`

## Evidence boundary

The deterministic harness executes the shipped `game.js` against a minimal DOM
contract. It proves state transitions, lamp expenditure, the three-night
terminal transition, and choice-dependent endings. The later lead verification
adds the required actual browser interaction and visual screenshot evidence.
This completes the T1 product chain without claiming that v0.5 itself is an
executable runtime.
