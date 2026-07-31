#!/usr/bin/env node

import { chromium } from 'playwright';
import { mkdirSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const EYE_HEIGHT = 1.62;
const SHOTS = [
  {
    id: 'town_reveal',
    feet: [0, 0, 16],
    yaw: 0,
    pitch: -0.02,
    description: "South of town looking north up the path to Oak's lab.",
  },
  {
    id: 'lab_door',
    feet: [0, 0, -4.5],
    yaw: 0,
    pitch: 0.1,
    description: "Oak's lab entrance at close range.",
  },
  {
    id: 'starters_out',
    feet: [0, -60, -11.4],
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

    // Freeze the production loop. This adapter renders the underlying Three.js
    // scene once per fixed camera without the project's heavy post-processing.
    game.engine.renderer.setAnimationLoop(null);
    game.engine.running = false;
    game.engine.setQuality('low');
    renderer.setPixelRatio(1);
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = false;
    renderer.toneMapping = game.THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1;

    const buildTimings = Array.isArray(game.world.buildTimings)
      ? game.world.buildTimings.map(([label, ms]) => ({ label, ms }))
      : [];

    return {
      requestedBackend: 'swiftshader',
      actualVendor,
      actualRenderer,
      viewport: [window.innerWidth, window.innerHeight],
      qualityTier: 'diagnostic-base-render',
      pixelRatio: renderer.getPixelRatio(),
      shadows: false,
      postProcessing: false,
      buildTimings,
      buildTotalMs: buildTimings.reduce((sum, step) => sum + step.ms, 0),
      seed: game.world.ctx?.seed ?? null,
    };
  });

  const manifest = [];

  for (const shot of SHOTS) {
    console.log(`  rendering ${shot.id}`);

    const captured = await page.evaluate(
      ({ currentShot, eyeHeight }) => {
        const game = window.__GAME__;
        const { renderer, scene, camera } = game.engine;

        camera.position.set(
          currentShot.feet[0],
          currentShot.feet[1] + eyeHeight,
          currentShot.feet[2],
        );
        camera.rotation.order = 'YXZ';
        camera.rotation.set(currentShot.pitch, currentShot.yaw, 0);
        camera.updateMatrixWorld(true);

        if (currentShot.stage === 'all_released') {
          const starterDebug = game.world.root.userData.starterDebug;
          if (!starterDebug) throw new Error('missing starterDebug');
          for (let i = 0; i < 3; i++) starterDebug.setRelease(i, 1);
          for (let i = 0; i < 3; i++) {
            game.world.update(1 / 60, game.engine.clock.elapsedTime + i / 60);
          }
        }

        if (game.hud?.dialogue?.isOpen) game.hud.dialogue.close();

        renderer.info.reset();
        renderer.setRenderTarget(null);
        renderer.clear(true, true, true);
        renderer.render(scene, camera);

        const canvas = renderer.domElement;
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
          const luminance =
            0.2126 * pixels[i] + 0.7152 * pixels[i + 1] + 0.0722 * pixels[i + 2];
          sum += luminance;
          sumSquares += luminance * luminance;
          if (luminance > 8) nonDark += 1;
        }
        const mean = sum / values;
        const variance = Math.max(0, sumSquares / values - mean * mean);
        const info = renderer.info;

        return {
          dataUrl: canvas.toDataURL('image/png'),
          sample: {
            meanLuminance: mean,
            luminanceVariance: variance,
            nonDarkFraction: nonDark / values,
          },
          stats: {
            drawCalls: info.render.calls,
            triangles: info.render.triangles,
            textures: info.memory.textures,
            geometries: info.memory.geometries,
            programs: info.programs ? info.programs.length : 0,
          },
        };
      },
      { currentShot: shot, eyeHeight: EYE_HEIGHT },
    );

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
    captureMode: 'direct-webgl-base-render-swiftshader-800x450',
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
    captureMode: 'direct-webgl-base-render-swiftshader-800x450',
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
