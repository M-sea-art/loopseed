#!/usr/bin/env node

import { chromium } from 'playwright';
import { mkdirSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const SHOTS = [
  {
    id: 'town_reveal',
    pos: [0, 0, 16],
    yaw: 0,
    pitch: -0.02,
    description: "South of town looking north up the path to Oak's lab.",
  },
  {
    id: 'lab_door',
    pos: [0, 0, -4.5],
    yaw: 0,
    pitch: 0.1,
    description: "Oak's lab entrance at close range.",
  },
  {
    id: 'starters_out',
    pos: [0, -60, -11.4],
    yaw: 0,
    pitch: -0.1,
    description: 'All three starters released on the lab table.',
    stage: 'all_released',
  },
];

function parseArgs(argv) {
  const args = {
    url: 'http://127.0.0.1:4173/',
    out: 'evidence/shots',
    width: 800,
    height: 450,
  };

  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--url') args.url = argv[++i];
    else if (arg === '--out') args.out = argv[++i];
    else if (arg === '--width') args.width = Number(argv[++i]);
    else if (arg === '--height') args.height = Number(argv[++i]);
  }

  return args;
}

const args = parseArgs(process.argv);
const outDir = resolve(args.out);
mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch({
  headless: true,
  args: [
    '--use-gl=angle',
    '--use-angle=swiftshader',
    '--enable-unsafe-swiftshader',
    '--enable-gpu',
    '--ignore-gpu-blocklist',
    '--enable-webgl',
    '--disable-frame-rate-limit',
    '--force-device-scale-factor=1',
  ],
});

const page = await browser.newPage({
  viewport: { width: args.width, height: args.height },
  deviceScaleFactor: 1,
});
page.setDefaultTimeout(300_000);

const consoleMessages = [];
const pageErrors = [];
page.on('console', (message) => {
  consoleMessages.push({ type: message.type(), text: message.text() });
});
page.on('pageerror', (error) => pageErrors.push(error.message));

const startedAt = new Date().toISOString();
const readyStart = performance.now();

try {
  console.log(`> ${args.url}`);
  await page.goto(args.url, { waitUntil: 'domcontentloaded', timeout: 60_000 });
  await page.waitForFunction(
    () => window.__GAME__ !== undefined || document.querySelector('#app pre') !== null,
    undefined,
    { timeout: 300_000 },
  );

  const bootError = await page.evaluate(() => {
    const pre = document.querySelector('#app pre');
    return pre ? pre.textContent : null;
  });
  if (bootError) throw new Error(`Application boot error: ${bootError}`);

  const readyMs = performance.now() - readyStart;

  const runtime = await page.evaluate(() => {
    const game = window.__GAME__;
    const renderer = game.engine.renderer;
    const gl = renderer.getContext();
    const debug = gl.getExtension('WEBGL_debug_renderer_info');
    const actualVendor = debug
      ? gl.getParameter(debug.UNMASKED_VENDOR_WEBGL)
      : gl.getParameter(gl.VENDOR);
    const actualRenderer = debug
      ? gl.getParameter(debug.UNMASKED_RENDERER_WEBGL)
      : gl.getParameter(gl.RENDERER);

    // This is a deliberately degraded CI observation tier, not the subject's
    // claimed high-quality performance tier. It keeps the one-shot scene
    // observable on a software renderer without changing subject source files.
    game.engine.setQuality('low');
    renderer.setPixelRatio(1);
    renderer.setSize(window.innerWidth, window.innerHeight);
    game.engine.postfx.setSize(window.innerWidth, window.innerHeight);

    game.engine.scene.traverse((node) => {
      const light = node;
      if (light.shadow?.mapSize) {
        light.shadow.mapSize.set(1024, 1024);
        light.shadow.map?.dispose?.();
        light.shadow.map = null;
        light.shadow.needsUpdate = true;
      }
    });

    const buildTimings = Array.isArray(game.world.buildTimings)
      ? game.world.buildTimings.map(([label, ms]) => ({ label, ms }))
      : [];

    return {
      requestedBackend: 'swiftshader',
      actualVendor,
      actualRenderer,
      viewport: [window.innerWidth, window.innerHeight],
      qualityTier: 'low',
      pixelRatio: renderer.getPixelRatio(),
      shadowMapSizeCap: 1024,
      buildTimings,
      buildTotalMs: buildTimings.reduce((sum, step) => sum + step.ms, 0),
      seed: game.world.ctx?.seed ?? null,
    };
  });

  // Allow the new quality and target sizes to settle before the first pose.
  await page.waitForTimeout(1_000);

  const manifest = [];

  for (const shot of SHOTS) {
    console.log(`  staging ${shot.id}`);

    await page.evaluate((currentShot) => {
      const game = window.__GAME__;
      if (!game.engine.running) game.engine.start();
      const position = new game.THREE.Vector3(...currentShot.pos);
      game.player.teleport(position, currentShot.yaw);
      game.player.state.pitch = currentShot.pitch;
      game.player.update(1 / 60);
      game.player.update(1 / 60);
    }, shot);

    // The interior transition and creature presentation are driven by ticks.
    // Keep the game's own loop alive briefly, then freeze it only for readback.
    await page.evaluate(
      () =>
        new Promise((resolveFrame) => {
          let frames = 0;
          const tick = () => {
            frames += 1;
            if (frames >= 18) resolveFrame();
            else requestAnimationFrame(tick);
          };
          requestAnimationFrame(tick);
        }),
    );

    if (shot.stage === 'all_released') {
      const stageResult = await page.evaluate(() => {
        const debug = window.__GAME__.world.root.userData.starterDebug;
        if (!debug) return 'missing starterDebug';
        for (let i = 0; i < 3; i++) debug.setRelease(i, 1);
        return 'released 3';
      });
      if (stageResult !== 'released 3') throw new Error(stageResult);

      await page.evaluate(
        () =>
          new Promise((resolveFrame) => {
            let frames = 0;
            const tick = () => {
              frames += 1;
              if (frames >= 14) resolveFrame();
              else requestAnimationFrame(tick);
            };
            requestAnimationFrame(tick);
          }),
      );
    }

    const captured = await page.evaluate((shotId) => {
      const game = window.__GAME__;
      if (game.hud?.dialogue?.isOpen) game.hud.dialogue.close();

      // Stop continuous rendering so browser compositing cannot contend with
      // this one deterministic readback. Then render once and read the WebGL
      // canvas synchronously in the same task.
      game.engine.renderer.setAnimationLoop(null);
      game.engine.running = false;

      const elapsed = game.engine.clock.elapsedTime;
      game.player.update(1 / 60);
      game.world.update(1 / 60, elapsed);
      game.hud?.update?.(1 / 60);
      game.engine.postfx.render(0);

      const canvas = game.engine.renderer.domElement;
      const sampleCanvas = document.createElement('canvas');
      sampleCanvas.width = 64;
      sampleCanvas.height = 36;
      const context = sampleCanvas.getContext('2d', { willReadFrequently: true });
      context.drawImage(canvas, 0, 0, sampleCanvas.width, sampleCanvas.height);
      const pixels = context.getImageData(0, 0, sampleCanvas.width, sampleCanvas.height).data;

      let sum = 0;
      let sumSquares = 0;
      let nonDark = 0;
      const values = pixels.length / 4;
      for (let i = 0; i < pixels.length; i += 4) {
        const luminance = 0.2126 * pixels[i] + 0.7152 * pixels[i + 1] + 0.0722 * pixels[i + 2];
        sum += luminance;
        sumSquares += luminance * luminance;
        if (luminance > 8) nonDark += 1;
      }
      const mean = sum / values;
      const variance = Math.max(0, sumSquares / values - mean * mean);

      const info = game.engine.renderer.info;
      const gl = game.engine.renderer.getContext();
      const debug = gl.getExtension('WEBGL_debug_renderer_info');
      const actualRenderer = debug
        ? gl.getParameter(debug.UNMASKED_RENDERER_WEBGL)
        : gl.getParameter(gl.RENDERER);

      return {
        shotId,
        dataUrl: canvas.toDataURL('image/png'),
        sample: {
          meanLuminance: mean,
          luminanceVariance: variance,
          nonDarkFraction: nonDark / values,
        },
        stats: {
          fpsBeforeFreeze: Math.round(game.engine.fps),
          drawCalls: info.render.calls,
          triangles: info.render.triangles,
          textures: info.memory.textures,
          geometries: info.memory.geometries,
          programs: info.programs ? info.programs.length : 0,
          actualRenderer,
        },
      };
    }, shot.id);

    if (!captured.dataUrl.startsWith('data:image/png;base64,')) {
      throw new Error(`${shot.id}: direct canvas capture did not return PNG data`);
    }

    const buffer = Buffer.from(captured.dataUrl.split(',', 2)[1], 'base64');
    if (buffer.length < 4_096) {
      throw new Error(`${shot.id}: PNG is implausibly small (${buffer.length} bytes)`);
    }
    if (captured.sample.nonDarkFraction < 0.05 || captured.sample.luminanceVariance < 2) {
      throw new Error(
        `${shot.id}: canvas readback appears blank (${JSON.stringify(captured.sample)})`,
      );
    }

    const file = `${shot.id}.png`;
    writeFileSync(resolve(outDir, file), buffer);
    manifest.push({
      id: shot.id,
      description: shot.description,
      file,
      bytes: buffer.length,
      sample: captured.sample,
      stats: captured.stats,
    });

    console.log(
      `  ${shot.id.padEnd(14)} ${(buffer.length / 1024).toFixed(0)} KiB  ` +
        `${captured.stats.drawCalls} calls  ` +
        `${Math.round(captured.stats.triangles / 1000)}k tris`,
    );
  }

  const payload = {
    status: 'PASS',
    captureMode: 'direct-webgl-canvas-swiftshader-low-800x450',
    startedAt,
    completedAt: new Date().toISOString(),
    readyMs,
    runtime,
    shots: manifest,
    consoleMessages,
    pageErrors,
  };
  writeFileSync(resolve(outDir, 'manifest.json'), JSON.stringify(payload, null, 2));
} catch (error) {
  const payload = {
    status: 'FAIL',
    captureMode: 'direct-webgl-canvas-swiftshader-low-800x450',
    startedAt,
    completedAt: new Date().toISOString(),
    error: error instanceof Error ? error.stack || error.message : String(error),
    consoleMessages,
    pageErrors,
  };
  writeFileSync(resolve(outDir, 'manifest.json'), JSON.stringify(payload, null, 2));
  console.error(payload.error);
  process.exitCode = 1;
} finally {
  await browser.close();
}
