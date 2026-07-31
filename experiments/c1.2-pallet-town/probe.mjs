#!/usr/bin/env node

import { chromium } from 'playwright';
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

function parseArgs(argv) {
  const args = {
    url: 'http://127.0.0.1:4173/',
    out: 'evidence/probe.json',
    backend: 'swiftshader',
    settle: 1400,
  };

  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--url') args.url = argv[++i];
    else if (arg === '--out') args.out = argv[++i];
    else if (arg === '--backend') args.backend = argv[++i];
    else if (arg === '--settle') args.settle = Number(argv[++i]);
  }

  return args;
}

const args = parseArgs(process.argv);
const outputPath = resolve(args.out);
mkdirSync(dirname(outputPath), { recursive: true });

const launchArgs = [
  '--use-gl=angle',
  `--use-angle=${args.backend}`,
  '--enable-gpu',
  '--ignore-gpu-blocklist',
  '--enable-webgl',
  '--disable-frame-rate-limit',
  '--force-device-scale-factor=1',
];

if (args.backend === 'metal') launchArgs.push('--enable-unsafe-webgpu');

const consoleMessages = [];
const pageErrors = [];
const startedAt = new Date().toISOString();
const monotonicStart = performance.now();
let browser;

try {
  browser = await chromium.launch({ headless: true, args: launchArgs });
  const page = await browser.newPage({
    viewport: { width: 1600, height: 900 },
    deviceScaleFactor: 1,
  });

  page.on('console', (message) => {
    consoleMessages.push({ type: message.type(), text: message.text() });
  });
  page.on('pageerror', (error) => pageErrors.push(error.message));

  await page.goto(args.url, { waitUntil: 'domcontentloaded', timeout: 60_000 });

  await page.waitForFunction(
    () => window.__GAME__ !== undefined || document.querySelector('#app pre') !== null,
    { timeout: 90_000 },
  );

  const bootError = await page.evaluate(() => {
    const pre = document.querySelector('#app pre');
    return pre ? pre.textContent : null;
  });
  if (bootError) throw new Error(`Application boot error: ${bootError}`);

  const readyMs = performance.now() - monotonicStart;
  await page.waitForTimeout(args.settle);

  const runtime = await page.evaluate(() => {
    const game = window.__GAME__;
    const renderer = game.engine.renderer;
    const info = renderer.info;
    const buildTimings = Array.isArray(game.world.buildTimings)
      ? game.world.buildTimings.map(([label, ms]) => ({ label, ms }))
      : [];

    return {
      buildTimings,
      buildTotalMs: buildTimings.reduce((sum, step) => sum + step.ms, 0),
      fps: Math.round(game.engine.fps),
      render: {
        drawCalls: info.render.calls,
        triangles: info.render.triangles,
        points: info.render.points,
        lines: info.render.lines,
      },
      memory: {
        textures: info.memory.textures,
        geometries: info.memory.geometries,
      },
      programs: info.programs ? info.programs.length : 0,
      renderer: {
        webgl2: renderer.capabilities.isWebGL2,
        maxTextureSize: renderer.capabilities.maxTextureSize,
        maxSamples: renderer.capabilities.maxSamples,
        precision: renderer.capabilities.precision,
      },
      seed: game.world.ctx?.seed ?? null,
    };
  });

  const payload = {
    status: 'PASS',
    startedAt,
    completedAt: new Date().toISOString(),
    url: args.url,
    backend: args.backend,
    readyMs,
    runtime,
    consoleMessages,
    pageErrors,
  };

  writeFileSync(outputPath, JSON.stringify(payload, null, 2));
  await browser.close();
} catch (error) {
  const payload = {
    status: 'FAIL',
    startedAt,
    completedAt: new Date().toISOString(),
    url: args.url,
    backend: args.backend,
    error: error instanceof Error ? error.stack || error.message : String(error),
    consoleMessages,
    pageErrors,
  };
  writeFileSync(outputPath, JSON.stringify(payload, null, 2));
  if (browser) await browser.close();
  process.exitCode = 1;
}
