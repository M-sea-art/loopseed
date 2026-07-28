(() => {
  "use strict";

  const TRAVELERS = {
    poet: {
      name: "沈砚",
      role: "失声诗人",
      costs: [2, 2, 3],
      requests: [
        "“借两分灯，我想把最后一句写完。”",
        "“墨迹快干了，可那一句仍不肯来。”",
        "“若天亮前写成，就把它留在这间客栈。”",
      ],
      consequences: [
        "沈砚把冻僵的手拢在灯旁。墨重新流动，他写下：雨替赶路的人记住了来处。",
        "诗人没有开口，只把新写的一行贴在门上。风从缝里穿过，纸却没有颤。",
        "最后一笔落下时，他忽然轻声念出了整首诗。原来失去的不是声音，只是愿意听的人。",
      ],
    },
    healer: {
      name: "阿葵",
      role: "抱药女孩",
      costs: [3, 2, 2],
      requests: [
        "“药不能受潮，山下还有人在等。”",
        "“再烘一刻，药香就能穿过这场雨。”",
        "“最后一包药干了，我就能赶在天亮前下山。”",
      ],
      consequences: [
        "阿葵摊开药包，苦香盖过湿木气。她说这束光，也许能替山下的人多守一个清晨。",
        "药叶在火边卷起绿边。阿葵分出一小包留给你：守灯的人，也要记得照顾自己。",
        "她把干透的药紧紧抱好。门外雨势未歇，她眼里却已经有了下山的路。",
      ],
    },
    courier: {
      name: "无名",
      role: "黑伞信使",
      costs: [1, 3, 3],
      requests: [
        "“只借一线光，让我看清信上的名字。”",
        "“封蜡裂了。我得知道这封信是否还该送。”",
        "“信写给一个等了十年的人。请让我读完。”",
      ],
      consequences: [
        "信使只照了一眼，便把信收回怀中。你看见收信人的名字，竟与客栈旧匾后的落款相同。",
        "封蜡在热气里显出暗纹。信使沉默许久，第一次把黑伞放在了门边。",
        "他终于读完，把信投入灯焰。灰烬向上飘，却在梁间聚成一只朝家的鸟。",
      ],
    },
  };

  const NIGHTS = ["壹 / 叁", "贰 / 叁", "叁 / 叁"];
  const WEATHER = [
    "戌时三刻，山雨封路。门外传来三声叩门。",
    "子夜，河水漫过石桥。三位旅客仍未睡去。",
    "寅时，灯油见底。天亮前只剩最后一次取舍。",
  ];

  const initialState = () => ({
    night: 0,
    light: 9,
    phase: "night",
    pendingChoice: null,
    decisions: [],
    ending: null,
  });

  let state = initialState();

  const dom = {
    game: document.querySelector("#game"),
    night: document.querySelector("#night-display"),
    weather: document.querySelector("#weather-line"),
    light: document.querySelector("#light-count"),
    pips: document.querySelector("#light-pips"),
    warning: document.querySelector("#light-warning"),
    title: document.querySelector("#prompt-title"),
    travelers: [...document.querySelectorAll(".traveler")],
    consequence: document.querySelector("#consequence"),
    consequenceText: document.querySelector("#consequence-text"),
    advance: document.querySelector("#advance-button"),
    ledger: document.querySelector("#decision-ledger"),
    restart: document.querySelector("#restart-button"),
  };

  function snapshot() {
    return JSON.parse(JSON.stringify(state));
  }

  function getEnding() {
    const counts = state.decisions.reduce((all, decision) => {
      all[decision.choice] = (all[decision.choice] || 0) + 1;
      return all;
    }, {});
    const unique = Object.keys(counts).length;

    if (unique === 3) {
      return {
        id: "shared-dawn",
        title: "结局 · 众灯相承",
        text: "天亮时，诗贴在门上，药香留在炉边，黑伞替门槛挡住最后一阵雨。你没能照亮谁的整夜，却让三个人各自带走一小束光。从此客栈多了一条规矩：借出去的灯，会沿着山路回来。",
      };
    }

    const favored = Object.entries(counts).sort((a, b) => b[1] - a[1])[0][0];
    const endings = {
      poet: {
        id: "poem",
        title: "结局 · 雨声成诗",
        text: "天亮时，沈砚把写满三夜的纸钉在门上。路人念起它，客栈从此不再无名。你耗去的灯油变成一句句传远的话，连最深的雨夜也有人循声而来。",
      },
      healer: {
        id: "medicine",
        title: "结局 · 百草回春",
        text: "天亮时，阿葵带药下山。数月后，她在客栈门前种满驱寒的药草。你曾偏给一人的暖意，最后被熬成许多碗热汤，送给每个淋雨的人。",
      },
      courier: {
        id: "letter",
        title: "结局 · 旧信归途",
        text: "天亮时，黑伞信使把最后一封信留给了你。信中写着客栈最初的名字：归灯。你守住的并不是一处落脚地，而是一条让旧事终于抵达的路。",
      },
    };
    return endings[favored];
  }

  function choose(choice) {
    if (state.phase !== "night") return;
    const traveler = TRAVELERS[choice];
    const cost = traveler.costs[state.night];
    if (!traveler || state.light < cost) return;

    state.light -= cost;
    state.pendingChoice = choice;
    state.phase = "consequence";
    state.decisions.push({
      night: state.night + 1,
      choice,
      traveler: traveler.name,
      role: traveler.role,
      cost,
      lightAfter: state.light,
    });
    render();
  }

  function advance() {
    if (state.phase !== "consequence") return;
    if (state.night === 2) {
      state.phase = "ending";
      state.ending = getEnding();
    } else {
      state.night += 1;
      state.pendingChoice = null;
      state.phase = "night";
    }
    render();
  }

  function reset() {
    state = initialState();
    render();
  }

  function renderLamp() {
    dom.light.textContent = String(state.light);
    dom.pips.innerHTML = Array.from(
      { length: 9 },
      (_, index) => `<i class="${index >= state.light ? "spent" : ""}"></i>`
    ).join("");
    dom.warning.textContent =
      state.light >= 6
        ? "灯芯尚长，但雨没有停。"
        : state.light >= 3
          ? "灯影渐薄，每一次取舍都更沉。"
          : "只剩微火。门外仍有人在等。";
    dom.game.style.setProperty("--light-level", String(state.light / 9));
  }

  function renderTravelers() {
    dom.travelers.forEach((button) => {
      const id = button.dataset.choice;
      const traveler = TRAVELERS[id];
      const cost = traveler.costs[state.night];
      button.disabled = state.phase !== "night" || cost > state.light;
      button.classList.toggle("chosen", state.pendingChoice === id);
      document.querySelector(`[data-cost="${id}"]`).textContent = String(cost);
      document.querySelector(`[data-request="${id}"]`).textContent = traveler.requests[state.night];
    });
  }

  function renderLedger() {
    if (!state.decisions.length) {
      dom.ledger.innerHTML = '<li class="empty">尚未落笔</li>';
      return;
    }
    dom.ledger.innerHTML = state.decisions
      .map(
        (decision) =>
          `<li data-night="${decision.night}">第${["一", "二", "三"][decision.night - 1]}夜 · ${decision.traveler} −${decision.cost}，余 ${decision.lightAfter}</li>`
      )
      .join("");
  }

  function render() {
    dom.game.dataset.phase = state.phase === "ending" ? "ending" : "night";
    dom.night.textContent = state.phase === "ending" ? "晓" : NIGHTS[state.night];
    dom.weather.textContent =
      state.phase === "ending" ? "卯时，雨停了。屋檐滴下今夜最后一滴水。" : WEATHER[state.night];
    renderLamp();
    renderTravelers();
    renderLedger();

    if (state.phase === "consequence") {
      const traveler = TRAVELERS[state.pendingChoice];
      dom.consequence.hidden = false;
      dom.consequenceText.textContent = traveler.consequences[state.night];
      dom.advance.innerHTML =
        state.night === 2 ? "推门迎接黎明 <span>→</span>" : `迎来第${["二", "三"][state.night]}夜 <span>→</span>`;
      dom.title.textContent = `${traveler.name}靠近了灯火`;
    } else if (state.phase === "ending") {
      dom.consequence.hidden = false;
      dom.consequenceText.textContent = `${state.ending.title}\n${state.ending.text}`;
      dom.title.textContent = state.ending.title;
    } else {
      dom.consequence.hidden = true;
      dom.title.textContent = state.night === 0 ? "三位旅客，一次选择" : "雨更急了，灯更短了";
    }

    dom.restart.hidden = state.phase !== "ending";
    window.__keeperState = snapshot();
    window.dispatchEvent(new CustomEvent("keeper-state", { detail: snapshot() }));
  }

  dom.travelers.forEach((button) => button.addEventListener("click", () => choose(button.dataset.choice)));
  dom.advance.addEventListener("click", advance);
  dom.restart.addEventListener("click", reset);
  window.__keeper = Object.freeze({ choose, advance, reset, getState: snapshot });
  render();
})();
