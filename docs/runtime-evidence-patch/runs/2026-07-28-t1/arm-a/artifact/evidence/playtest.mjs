import { spawn } from "node:child_process";
import { writeFile } from "node:fs/promises";
import { createRequire } from "node:module";
import process from "node:process";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const baseURL = "http://127.0.0.1:4173/";
const screenshots = {
  opening: "evidence/01-opening-night.jpg",
  courierEnding: "evidence/02-courier-ending.jpg",
  sharedEnding: "evidence/03-shared-ending.jpg",
};

const server = spawn(
  "python3",
  ["-m", "http.server", "4173", "--bind", "127.0.0.1"],
  { cwd: process.cwd(), stdio: ["ignore", "pipe", "pipe"] },
);

let serverOutput = "";
server.stdout.on("data", (chunk) => {
  serverOutput += chunk.toString();
});
server.stderr.on("data", (chunk) => {
  serverOutput += chunk.toString();
});

async function waitForServer() {
  for (let attempt = 0; attempt < 40; attempt += 1) {
    try {
      const response = await fetch(baseURL);
      if (response.ok) return;
    } catch {
      // Server is still starting.
    }
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  throw new Error(`Server did not become ready.\n${serverOutput}`);
}

function expectEqual(actual, expected, label) {
  if (actual !== expected) {
    throw new Error(`${label}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
  }
}

async function readState(page) {
  return page.evaluate(() => ({
    title: document.title,
    night: document.querySelector("#night-label")?.textContent?.trim(),
    flame: document.querySelector("#flame-value")?.textContent?.trim(),
    prompt: document.querySelector("#prompt-title")?.textContent?.trim(),
    consequence: document.querySelector("#consequence-title")?.textContent?.trim() || null,
    endingHidden: document.querySelector("#ending")?.hidden,
    ending: document.querySelector("#ending-title")?.textContent?.trim() || null,
    path: document.querySelector("#ending-path")?.textContent?.trim() || null,
    bodyScroll: {
      width: document.documentElement.scrollWidth,
      height: document.documentElement.scrollHeight,
      viewportWidth: window.innerWidth,
      viewportHeight: window.innerHeight,
    },
  }));
}

async function choose(page, traveler, expectedFlame, expectedNight) {
  const choice = page.locator(`[data-traveler="${traveler}"]`);
  expectEqual(await choice.count(), 1, `unique ${traveler} choice`);
  await choice.click();
  await page.locator("#consequence:not([hidden])").waitFor({ state: "visible" });
  const after = await readState(page);
  expectEqual(after.flame, String(expectedFlame), `${expectedNight} flame`);
  expectEqual(after.night, expectedNight, `${expectedNight} label`);
  if (!after.consequence) throw new Error(`${expectedNight} consequence is missing`);
  return after;
}

async function continueNight(page, expectedNight) {
  const button = page.locator("#continue-button");
  expectEqual(await button.count(), 1, "unique continue button");
  await button.click();
  if (expectedNight) {
    await page.locator("#night-label").filter({ hasText: expectedNight }).waitFor({ state: "visible" });
    expectEqual((await readState(page)).night, expectedNight, "advanced night");
  } else {
    await page.locator("#ending:not([hidden])").waitFor({ state: "visible" });
  }
}

async function runPath(page, choices, expectedEnding, expectedPath, expectedFlames) {
  const steps = [];
  for (let index = 0; index < choices.length; index += 1) {
    const nightLabel = ["第一夜", "第二夜", "第三夜"][index];
    steps.push(await choose(page, choices[index], expectedFlames[index], nightLabel));
    await continueNight(page, index < 2 ? ["第二夜", "第三夜"][index] : null);
  }
  const ending = await readState(page);
  expectEqual(ending.endingHidden, false, "ending visibility");
  expectEqual(ending.ending, expectedEnding, "ending title");
  expectEqual(ending.path, expectedPath, "ending path");
  return { steps, ending };
}

let browser;
let exitCode = 0;
try {
  await waitForServer();
  browser = await chromium.launch({
    headless: true,
    executablePath: chromium.executablePath(),
  });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 1,
    locale: "zh-CN",
  });
  const page = await context.newPage();
  const consoleMessages = [];
  const pageErrors = [];
  page.on("console", (message) => {
    if (message.type() === "error" || message.type() === "warning") {
      consoleMessages.push({ type: message.type(), text: message.text() });
    }
  });
  page.on("pageerror", (error) => pageErrors.push(error.message));

  const response = await page.goto(baseURL, { waitUntil: "networkidle" });
  expectEqual(response?.status(), 200, "HTTP status");
  const opening = await readState(page);
  expectEqual(opening.title, "雨夜客栈：守灯人", "page title");
  expectEqual(opening.night, "第一夜", "opening night");
  expectEqual(opening.flame, "9", "opening flame");
  expectEqual(opening.endingHidden, true, "opening ending hidden");
  expectEqual(opening.bodyScroll.width, opening.bodyScroll.viewportWidth, "desktop horizontal fit");
  expectEqual(opening.bodyScroll.height, opening.bodyScroll.viewportHeight, "desktop vertical fit");

  const travelerVisibility = {};
  for (const traveler of ["courier", "child", "storyteller"]) {
    travelerVisibility[traveler] = await page.locator(`#traveler-${traveler}`).isVisible();
    expectEqual(travelerVisibility[traveler], true, `${traveler} visible`);
  }

  await page.screenshot({ path: screenshots.opening, type: "jpeg", quality: 90 });

  const courierPath = await runPath(
    page,
    ["courier", "courier", "courier"],
    "长路有信",
    "信使之路",
    [6, 4, 1],
  );
  await page.screenshot({ path: screenshots.courierEnding, type: "jpeg", quality: 90 });

  const restart = page.locator("#restart-button");
  expectEqual(await restart.count(), 1, "unique restart button");
  await restart.click();
  const restarted = await readState(page);
  expectEqual(restarted.night, "第一夜", "restart night");
  expectEqual(restarted.flame, "9", "restart flame");
  expectEqual(restarted.endingHidden, true, "restart ending hidden");

  const sharedPath = await runPath(
    page,
    ["child", "storyteller", "courier"],
    "百灯同明",
    "三路成环",
    [7, 5, 2],
  );
  await page.screenshot({ path: screenshots.sharedEnding, type: "jpeg", quality: 90 });

  const report = {
    status: "PASS",
    environment: {
      url: baseURL,
      browser: await browser.version(),
      playwright: "1.61.1",
      viewport: "1440x900",
      fallback:
        "Cloud Browser failed on localhost with net::ERR_BLOCKED_BY_CLIENT; user explicitly allowed regular Playwright fallback.",
    },
    opening,
    travelerVisibility,
    paths: {
      courier: courierPath,
      shared: sharedPath,
    },
    console: {
      warningsAndErrors: consoleMessages,
      pageErrors,
      clean: consoleMessages.length === 0 && pageErrors.length === 0,
    },
    screenshots,
  };

  if (!report.console.clean) {
    throw new Error(`Console is not clean: ${JSON.stringify(report.console)}`);
  }
  await writeFile("evidence/playtest-results.json", `${JSON.stringify(report, null, 2)}\n`);
  console.log(JSON.stringify(report, null, 2));
  await context.close();
} catch (error) {
  exitCode = 1;
  console.error(error.stack || error.message);
} finally {
  if (browser) await browser.close();
  server.kill("SIGTERM");
}

process.exitCode = exitCode;
