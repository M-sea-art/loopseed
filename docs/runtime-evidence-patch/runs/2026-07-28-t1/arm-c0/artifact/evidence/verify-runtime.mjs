import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const source = fs.readFileSync(new URL("../game.js", import.meta.url), "utf8");

function element(extra = {}) {
  return {
    textContent: "",
    innerHTML: "",
    hidden: false,
    disabled: false,
    dataset: {},
    style: { setProperty() {} },
    classList: { toggle() {} },
    addEventListener() {},
    ...extra,
  };
}

function boot() {
  const travelers = ["poet", "healer", "courier"].map((choice) =>
    element({ dataset: { choice } })
  );
  const bySelector = new Map([
    ["#game", element({ dataset: {} })],
    ["#night-display", element()],
    ["#weather-line", element()],
    ["#light-count", element()],
    ["#light-pips", element()],
    ["#light-warning", element()],
    ["#prompt-title", element()],
    ["#consequence", element({ hidden: true })],
    ["#consequence-text", element()],
    ["#advance-button", element()],
    ["#decision-ledger", element()],
    ["#restart-button", element({ hidden: true })],
    ...["poet", "healer", "courier"].flatMap((id) => [
      [`[data-cost="${id}"]`, element()],
      [`[data-request="${id}"]`, element()],
    ]),
  ]);
  const window = {
    addEventListener() {},
    dispatchEvent() {},
  };
  const context = vm.createContext({
    console,
    window,
    document: {
      querySelector(selector) {
        return bySelector.get(selector);
      },
      querySelectorAll(selector) {
        return selector === ".traveler" ? travelers : [];
      },
    },
    CustomEvent: class {
      constructor(type, options) {
        this.type = type;
        this.detail = options?.detail;
      }
    },
  });
  vm.runInContext(source, context, { filename: "game.js" });
  return window.__keeper;
}

function play(path) {
  const keeper = boot();
  const captures = [keeper.getState()];
  for (const choice of path) {
    keeper.choose(choice);
    captures.push(keeper.getState());
    keeper.advance();
    captures.push(keeper.getState());
  }
  return captures;
}

const shared = play(["poet", "healer", "courier"]);
const focused = play(["healer", "healer", "healer"]);
const sharedChoices = shared.filter((_, index) => index % 2 === 1);
const focusedChoices = focused.filter((_, index) => index % 2 === 1);

assert.deepEqual(sharedChoices.map((s) => s.light), [7, 5, 2]);
assert.deepEqual(focusedChoices.map((s) => s.light), [6, 4, 2]);
assert.equal(shared.at(-1).decisions.map((d) => d.choice).join(","), "poet,healer,courier");
assert.equal(focused.at(-1).decisions.map((d) => d.choice).join(","), "healer,healer,healer");
assert.equal(shared.at(-1).phase, "ending");
assert.equal(focused.at(-1).phase, "ending");
assert.equal(shared.at(-1).ending.id, "shared-dawn");
assert.equal(focused.at(-1).ending.id, "medicine");
assert.notEqual(shared.at(-1).ending.id, focused.at(-1).ending.id);

process.stdout.write(
  JSON.stringify(
    {
      protocol: "C0 PROTOCOL_ONLY",
      runner: "node-vm deterministic DOM harness",
      execution: "PASS",
      browserEvidence: "BLOCKED",
      paths: [
        {
          choices: ["poet", "healer", "courier"],
          lightAfterEachChoice: sharedChoices.map((s) => s.light),
          ending: shared.at(-1).ending,
          ledger: shared.at(-1).decisions,
        },
        {
          choices: ["healer", "healer", "healer"],
          lightAfterEachChoice: focusedChoices.map((s) => s.light),
          ending: focused.at(-1).ending,
          ledger: focused.at(-1).decisions,
        },
      ],
      assertions: 9,
      verdict: "STATIC_BEHAVIOR_PASS_BROWSER_CAPTURE_PENDING",
    },
    null,
    2
  ) + "\n"
);
