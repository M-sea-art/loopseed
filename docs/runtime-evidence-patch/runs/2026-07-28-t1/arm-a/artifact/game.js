const GAME_DATA = {
  nights: [
    {
      label: "第一夜",
      chapter: "夜一",
      weather: "风雨初至",
      title: "雨追着三双脚进了门。",
      copy: "屋檐漏水，炉火将熄。三名旅客都在等你抬起那盏灯——可灯油只够撑过三个夜晚。",
      options: {
        courier: {
          icon: "羽",
          name: "照亮马厩 · 林雁",
          hint: "让负伤信使连夜换马",
          cost: 3,
          resultTitle: "一封信越过了山口",
          result: "林雁咬紧绷带，借灯换好马掌。她将一枚赤蜡印放在柜台：若有急事，折断它。",
        },
        child: {
          icon: "纸",
          name: "照亮账房 · 乔乔",
          hint: "替迷路学徒描下归途",
          cost: 2,
          resultTitle: "地图上多了一条小路",
          result: "乔乔烘干地图，用炭笔补全被雨水冲淡的岔口。她折下一只纸鸟留给你。",
        },
        storyteller: {
          icon: "弦",
          name: "照亮偏堂 · 莫伯",
          hint: "让盲眼琴师温暖双手",
          cost: 2,
          resultTitle: "旧琴记起了山的声音",
          result: "莫伯在灯下调好断弦。他听见远雷，告诉你：第二夜，北窗千万要拴紧。",
        },
      },
    },
    {
      label: "第二夜",
      chapter: "夜二",
      weather: "寒潮压境",
      title: "河水涨上台阶，北窗开始作响。",
      copy: "寒气钻进每一道木缝。你必须决定，今夜哪一段旅程值得由灯火继续托住。",
      options: {
        courier: {
          icon: "羽",
          name: "点亮信鸽塔 · 林雁",
          hint: "把水患消息送往下游",
          cost: 2,
          resultTitle: "三只灰鸽穿入暴雨",
          result: "借着窗口的灯，林雁放飞警报。远处村落逐盏亮起回应，河岸不再一片漆黑。",
        },
        child: {
          icon: "纸",
          name: "点亮旧仓 · 乔乔",
          hint: "寻找封堵决口的麻袋",
          cost: 3,
          resultTitle: "小手找到了被遗忘的粮袋",
          result: "乔乔从旧仓拖出麻袋，旅客们合力堵住后门。客栈保住了最后一袋米。",
        },
        storyteller: {
          icon: "弦",
          name: "点亮门廊 · 莫伯",
          hint: "用琴声召回迷途船夫",
          cost: 2,
          resultTitle: "琴音在黑水上架起一座桥",
          result: "莫伯迎着雨弹奏。失去航标的小舟循声靠岸，船夫带来一捆干柴。",
        },
      },
    },
    {
      label: "第三夜",
      chapter: "夜三",
      weather: "破晓之前",
      title: "最后的黑暗，比前两夜都长。",
      copy: "灯壶已经见底。门外有人呼救，而你只能把最后一簇暖光交给一双手。",
      options: {
        courier: {
          icon: "羽",
          name: "高悬路灯 · 林雁",
          hint: "为山口的救援队标出客栈",
          cost: 3,
          resultTitle: "路灯刺破了最深的雨幕",
          result: "林雁把灯挂上屋脊。救援队看见它，带着药箱和绳索赶到。灯油随雨熄尽。",
        },
        child: {
          icon: "纸",
          name: "守住灶火 · 乔乔",
          hint: "熬一锅让所有人醒来的热粥",
          cost: 2,
          resultTitle: "米香赶走了最后一层寒意",
          result: "乔乔守着细火搅动米粥。最虚弱的旅客睁开眼，众人有了等到天亮的力气。",
        },
        storyteller: {
          icon: "弦",
          name: "照亮渡口 · 莫伯",
          hint: "让琴声与灯影一同引航",
          cost: 3,
          resultTitle: "渡口回应了三声船铃",
          result: "莫伯抱琴坐在灯旁。最后一艘渡船靠岸，载走了被洪水困住的人。",
        },
      },
    },
  ],
  travelers: {
    courier: { label: "信使之路", color: "#d86a58" },
    child: { label: "学徒之路", color: "#77b7cf" },
    storyteller: { label: "琴师之路", color: "#a9b58b" },
  },
  endings: {
    all: {
      emblem: "☀",
      title: "百灯同明",
      copy: "你没有只看见一个人的风雨。信鸽带来援军，地图指出高地，琴声领船靠岸。天亮时，三名旅客把各自的一盏灯挂回客栈。",
      path: "三路成环",
      quote: "“被分出去的光，最后都找到了回来的路。”",
    },
    courier: {
      emblem: "羽",
      title: "长路有信",
      copy: "你一次次把灯交给林雁。第三日清晨，官道上的每座驿站都收到水患警报，山谷因此比洪峰更早醒来。",
      path: "信使之路",
      quote: "“灯没有走远，它只是变成了远方的消息。”",
    },
    child: {
      emblem: "纸",
      title: "新任守灯人",
      copy: "乔乔用你给的灯火记路、找粮、守灶。雨停后，她没有离开，而是在门前重新挂起一盏写着‘有人等你’的灯。",
      path: "学徒之路",
      quote: "“有些归途，是从学会替别人留灯开始的。”",
    },
    storyteller: {
      emblem: "弦",
      title: "雨声成歌",
      copy: "莫伯的琴救回迷路的人与船。后来，这三个夜晚被唱遍沿河村落，每个听过歌的人都会在暴雨时点亮窗灯。",
      path: "琴师之路",
      quote: "“一盏灯会熄，一首记得灯的歌不会。”",
    },
  },
};

const state = {
  night: 0,
  flame: 9,
  choices: [],
  locked: false,
  sound: false,
};

const $ = (selector) => document.querySelector(selector);
const elements = {
  nightLabel: $("#night-label"),
  weatherLabel: $("#weather-label"),
  flameValue: $("#flame-value"),
  flamePips: $("#flame-pips"),
  chapterNumber: $("#chapter-number"),
  promptTitle: $("#prompt-title"),
  promptCopy: $("#prompt-copy"),
  choices: $("#choices"),
  consequence: $("#consequence"),
  consequenceTitle: $("#consequence-title"),
  consequenceCopy: $("#consequence-copy"),
  continueButton: $("#continue-button"),
  ending: $("#ending"),
  endingTitle: $("#ending-title"),
  endingCopy: $("#ending-copy"),
  endingEmblem: $("#ending-emblem"),
  endingFlame: $("#ending-flame"),
  endingPath: $("#ending-path"),
  endingQuote: $("#ending-quote"),
  restartButton: $("#restart-button"),
  soundToggle: $("#sound-toggle"),
  lightFlash: $("#light-flash"),
};

let audio = null;

function buildPips() {
  elements.flamePips.innerHTML = "";
  for (let i = 0; i < 9; i += 1) {
    const pip = document.createElement("i");
    if (i < state.flame) pip.className = "full";
    elements.flamePips.appendChild(pip);
  }
}

function renderNight() {
  const night = GAME_DATA.nights[state.night];
  state.locked = false;
  elements.nightLabel.textContent = night.label;
  elements.weatherLabel.textContent = night.weather;
  elements.chapterNumber.textContent = night.chapter;
  elements.promptTitle.textContent = night.title;
  elements.promptCopy.textContent = night.copy;
  elements.flameValue.textContent = state.flame;
  elements.consequence.hidden = true;
  elements.continueButton.hidden = true;
  elements.continueButton.textContent = state.night === 2 ? "守到天明 →" : "推门迎接下一夜 →";
  document.querySelectorAll(".traveler").forEach((traveler) => traveler.classList.remove("chosen"));
  document.querySelectorAll(".journey li").forEach((item, index) => {
    item.classList.toggle("active", index === state.night);
    item.classList.toggle("done", index < state.night);
  });

  elements.choices.innerHTML = "";
  Object.entries(night.options).forEach(([key, option]) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "choice";
    button.dataset.traveler = key;
    button.style.setProperty("--traveler-color", GAME_DATA.travelers[key].color);
    button.disabled = option.cost > state.flame;
    button.innerHTML = `
      <span class="sigil" aria-hidden="true">${option.icon}</span>
      <span class="choice-copy">
        <strong>${option.name}</strong>
        <small>${option.hint}</small>
      </span>
      <span class="cost"><b>−${option.cost}</b> 灯火</span>
    `;
    button.addEventListener("click", () => chooseTraveler(key, button));
    elements.choices.appendChild(button);
  });
  buildPips();
}

function chooseTraveler(key, button) {
  if (state.locked) return;
  const option = GAME_DATA.nights[state.night].options[key];
  if (option.cost > state.flame) return;

  state.locked = true;
  state.flame -= option.cost;
  state.choices.push(key);
  elements.flameValue.textContent = state.flame;
  buildPips();
  document.querySelectorAll(".choice").forEach((choice) => {
    choice.disabled = true;
    choice.classList.toggle("selected", choice === button);
  });
  const traveler = document.querySelector(`#traveler-${key}`);
  if (traveler) traveler.classList.add("chosen");
  elements.consequenceTitle.textContent = option.resultTitle;
  elements.consequenceCopy.textContent = option.result;
  elements.consequence.hidden = false;
  elements.continueButton.hidden = false;
  elements.continueButton.focus({ preventScroll: true });
  flareLight();
  playChime();
}

function continueJourney() {
  if (!state.locked) return;
  if (state.night < 2) {
    state.night += 1;
    flareLightning();
    renderNight();
    return;
  }
  showEnding();
}

function getEnding() {
  const unique = new Set(state.choices);
  if (unique.size === 3) return GAME_DATA.endings.all;
  const counts = state.choices.reduce(
    (sum, key) => ({ ...sum, [key]: (sum[key] || 0) + 1 }),
    {},
  );
  const winner = Object.keys(counts).sort((a, b) => counts[b] - counts[a])[0];
  return GAME_DATA.endings[winner];
}

function showEnding() {
  const ending = getEnding();
  elements.endingEmblem.textContent = ending.emblem;
  elements.endingTitle.textContent = ending.title;
  elements.endingCopy.textContent = ending.copy;
  elements.endingPath.textContent = ending.path;
  elements.endingFlame.textContent = state.flame;
  elements.endingQuote.textContent = ending.quote;
  elements.ending.hidden = false;
  elements.restartButton.focus({ preventScroll: true });
  playChime(true);
}

function restart() {
  state.night = 0;
  state.flame = 9;
  state.choices = [];
  state.locked = false;
  elements.ending.hidden = true;
  renderNight();
}

function flareLight() {
  document.querySelectorAll(".ambient-glow").forEach((glow, index) => {
    glow.style.opacity = Math.max(0.22, state.flame / 9 - index * 0.08);
  });
}

function flareLightning() {
  elements.lightFlash.classList.remove("flash");
  requestAnimationFrame(() => elements.lightFlash.classList.add("flash"));
}

function createRainAudio() {
  const AudioContext = window.AudioContext || window.webkitAudioContext;
  if (!AudioContext) return null;
  const context = new AudioContext();
  const seconds = 2;
  const buffer = context.createBuffer(1, context.sampleRate * seconds, context.sampleRate);
  const data = buffer.getChannelData(0);
  let previous = 0;
  for (let i = 0; i < data.length; i += 1) {
    const white = Math.random() * 2 - 1;
    previous = previous * 0.965 + white * 0.035;
    data[i] = previous * 0.85;
  }
  const source = context.createBufferSource();
  const filter = context.createBiquadFilter();
  const gain = context.createGain();
  source.buffer = buffer;
  source.loop = true;
  filter.type = "lowpass";
  filter.frequency.value = 1500;
  gain.gain.value = 0.12;
  source.connect(filter).connect(gain).connect(context.destination);
  source.start();
  return { context, source, gain };
}

function toggleSound() {
  if (!audio) audio = createRainAudio();
  if (!audio) return;
  state.sound = !state.sound;
  audio.gain.gain.setTargetAtTime(state.sound ? 0.12 : 0, audio.context.currentTime, 0.12);
  elements.soundToggle.setAttribute("aria-pressed", String(state.sound));
  elements.soundToggle.lastElementChild.textContent = `雨声：${state.sound ? "开" : "关"}`;
}

function playChime(final = false) {
  if (!state.sound || !audio) return;
  const oscillator = audio.context.createOscillator();
  const gain = audio.context.createGain();
  oscillator.type = "sine";
  oscillator.frequency.value = final ? 523.25 : 392;
  gain.gain.setValueAtTime(0.0001, audio.context.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.08, audio.context.currentTime + 0.02);
  gain.gain.exponentialRampToValueAtTime(0.0001, audio.context.currentTime + 0.7);
  oscillator.connect(gain).connect(audio.context.destination);
  oscillator.start();
  oscillator.stop(audio.context.currentTime + 0.72);
}

elements.continueButton.addEventListener("click", continueJourney);
elements.restartButton.addEventListener("click", restart);
elements.soundToggle.addEventListener("click", toggleSound);

document.addEventListener("keydown", (event) => {
  if (event.key.toLowerCase() === "r" && !elements.ending.hidden) restart();
});

renderNight();
