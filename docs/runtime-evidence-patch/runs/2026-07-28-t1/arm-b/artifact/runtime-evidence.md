# Runtime evidence

## Local artifact checks

- Static server: `GET /` returned `HTTP 200`, `text/html`, 34,953 bytes.
- JavaScript: the inline game script passed `node --check`.
- HTML contract: exactly three traveler choice buttons were found (`healer`, `guard`, `child`), with three inline SVG portraits and all seven required game-state UI targets.
- The runtime exposes a read-only snapshot for testing as `window.__RAIN_INN_STATE__`; the document body also mirrors `data-night`, `data-flame`, and `data-ending`.

## Browser access boundary

The configured generic cloud browser could not reach the local static server:

```text
Browser Use cannot open http://127.0.0.1:4173/
net::ERR_BLOCKED_BY_CLIENT
```

The browser security policy also rejected opening the synchronized local `file://` path and explicitly prohibited alternate browser surfaces or workarounds.

Per the experiment constraint, the artifact was not publicly deployed and no dependency was installed. No runtime screenshots were fabricated. The browser gates remain pending for the experiment Lead's unified internal test bench.

## Unified bench flow

1. Serve this directory with `python -m http.server 4173`.
2. Open `http://127.0.0.1:4173/` at a desktop viewport.
3. Capture initial state: `data-night="1"`, `data-flame="9"`, three distinct travelers visible.
4. Choose 桑婆 (cost 2): expect `data-flame="7"` and the consequence text; continue.
5. Choose 陆七 (night-two cost 2): expect `data-night="2"`, then `data-flame="5"`; continue.
6. Choose 阿棠 (night-three cost 1): expect `data-flame="4"`, `data-ending="shared-dawn"`, and ending title “众灯成家”.
7. Confirm the ending ledger reads `桑婆 × 1`, `陆七 × 1`, `阿棠 × 1`, `余火 4 / 9`.

This route proves one consequential choice per night, real light consumption `9 → 7 → 5 → 4`, and a choice-dependent third-night ending.
