# 运行证据记录

日期：2026-07-28
状态：`EVIDENCE_BLOCKED`

## 交付物

- `index.html`：单屏场景、SVG 客栈与三名旅客、HUD、三夜进度、结局页
- `styles.css`：雨夜动效、冷暖光、响应式界面、动效降级
- `game.js`：三夜状态机、每夜一次选择、真实灯火扣减、即时后果、组合结局、本地 Web Audio
- `README.md`：本地运行方法

## 原始命令与退出状态

### 1. JavaScript 语法检查

```text
$ node --check game.js
[无标准输出]
exit: 0
```

结果：通过。

### 2. 交付文件枚举

```text
$ rg --files . | sort
./README.md
./game.js
./index.html
./styles.css
exit: 0
```

结果：实现文件均在本 artifact 目录内。

### 3. 启动本地服务（首次）

```text
$ python3 -m http.server 4173 --bind 0.0.0.0
Serving HTTP on 0.0.0.0 port 4173 (http://0.0.0.0:4173/) ...
^C
exit: 1
```

结果：服务成功进入监听；在浏览器访问受阻后手动中断。

### 4. 启动本地服务（隔离验证）

```text
$ python3 -m http.server 4173 --bind 127.0.0.1
Serving HTTP on 127.0.0.1 port 4173 (http://127.0.0.1:4173/) ...
^C
exit: 1
```

结果：服务成功进入监听；验证结束后手动中断。

### 5. 跨执行单元 HTTP 取回

```text
$ curl --fail --silent --show-error --head http://127.0.0.1:4173/ && curl --fail --silent --show-error http://127.0.0.1:4173/game.js | node --check
curl: (7) Failed to connect to 127.0.0.1 port 4173 after 0 ms: Couldn't connect to server
exit: 7
```

结果：执行单元之间不共享回环网络；不能把这一结果归因于游戏。

### 6. 主循环不变量检查

```text
$ rg -n "state\.flame -= option\.cost|state\.choices\.push|state\.night < 2|showEnding\(|traveler-courier|traveler-child|traveler-storyteller" index.html game.js
game.js:231:  state.flame -= option.cost;
game.js:232:  state.choices.push(key);
game.js:252:  if (state.night < 2) {
game.js:258:  showEnding();
game.js:272:function showEnding() {
index.html:120:            <g id="traveler-courier" class="traveler" transform="translate(508 418)">
index.html:134:            <g id="traveler-child" class="traveler" transform="translate(702 447)">
index.html:147:            <g id="traveler-storyteller" class="traveler" transform="translate(866 414)">
exit: 0
```

结果：静态证实灯火扣减、选择记录、三夜推进、结局调用与三名旅客节点均存在。

### 7. 外部资源禁用检查

```text
$ if rg -n "https?://|@import|<img[[:space:]]" index.html styles.css game.js; then exit 1; else exit 0; fi
[无标准输出]
exit: 0
```

结果：没有远程 URL、CSS 导入或外部图片引用。

## 浏览器尝试

使用同一获准 Cloud Browser：

1. 打开 `http://127.0.0.1:4173/`
   - 结果：`net::ERR_BLOCKED_BY_CLIENT`
2. 打开同步目录中的 `file:///home/oai/share/.../artifact/index.html`
   - 结果：被 Cloud Browser URL 安全策略拒绝
   - 策略明确禁止为同一目标继续使用间接执行、原始 CDP、其他浏览器表面或绕过方式

因此没有合规途径让获准浏览器加载本地产物。未尝试公共部署，也未改用其他浏览器表面。

## 要求项状态

| 要求 | 状态 | 证据 |
|---|---|---|
| 可直接运行产品 | 已完成 | `README.md` 与四个零依赖实现文件 |
| 三夜、每夜一次有后果选择 | 静态通过，浏览器未实测 | `game.js` 三夜状态机 |
| 灯火真实减少 | 静态通过，浏览器未实测 | `state.flame -= option.cost` |
| 选择决定结局 | 静态通过，浏览器未实测 | `getEnding()` / `showEnding()` |
| 雨夜、客栈、冷暖光 | 已实现，截图未取得 | 本地 SVG/CSS 场景 |
| 三名可辨旅客 | 静态通过，截图未取得 | 三个具名 SVG 旅客节点 |
| 两条完整选择路径 | **阻塞** | 浏览器未获准加载页面 |
| 控制台错误检查 | **阻塞** | 页面未进入游戏 JS 上下文 |
| 运行截图路径 | **无** | 未伪造非运行截图 |

## 截图

截图数量：0 / 3。
截图路径：无。
原因：获准浏览器无法加载本地 HTTP 或同步文件 URL；未使用替代渲染器冒充运行截图。

## 后续授权的常规 Playwright 回退

后续收到明确授权：Cloud Browser 的 localhost 导航失败后，可使用同一云端环境中的常规 Playwright 回退。已按 `frontend-testing-debugging` 的 fallback 分支创建 `evidence/playtest.mjs`，测试脚本会：

- 自行启动 `127.0.0.1:4173` 本地服务；
- 使用 1440×900 视口；
- 走完 `林雁 → 林雁 → 林雁` 与 `乔乔 → 莫伯 → 林雁` 两条三夜路径；
- 逐夜断言灯火、夜数和即时后果；
- 断言两个不同结局；
- 收集 `console warning/error` 与 `pageerror`；
- 最多生成三张 JPEG 截图。

### Playwright 环境预检

```text
$ node -e "const p=require('playwright/package.json'); console.log('playwright',p.version)" && node -e "const {chromium}=require('playwright'); console.log(chromium.executablePath())"
playwright 1.61.1
/root/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome
exit: 0
```

### 测试脚本首次运行

```text
$ node evidence/playtest.mjs
Error [ERR_MODULE_NOT_FOUND]: Cannot find package 'playwright' imported from .../evidence/playtest.mjs
exit: 1
```

结果：预装包可由 CommonJS 解析，但 ESM 裸导入不读取同一模块搜索路径。只修正测试夹具为 `createRequire`，未修改产品。

### 测试脚本第二次运行

```text
$ node evidence/playtest.mjs
browserType.launch: Executable doesn't exist at /root/.cache/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-linux64/chrome-headless-shell
exit: 1
```

结果：Playwright 默认无头壳不存在。只让测试夹具显式使用 `chromium.executablePath()`，未修改产品。

### 测试脚本第三次运行

```text
$ node evidence/playtest.mjs
browserType.launch: Failed to launch chromium because executable doesn't exist at /root/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome
exit: 1
```

结果：Playwright API 返回的完整 Chromium 路径同样不存在。

### 浏览器可执行文件实存检查

```text
$ node -e "const fs=require('fs'); const p=require('playwright'); for(const n of ['chromium','firefox','webkit']){const x=p[n].executablePath(); console.log(n,x,fs.existsSync(x))}"
chromium /root/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome false
firefox /root/.cache/ms-playwright/firefox-1532/firefox/firefox false
webkit /root/.cache/ms-playwright/webkit-2311/pw_run.sh false
exit: 0
```

```text
$ command -v chromium || command -v chromium-browser || command -v google-chrome || true
[无标准输出]
exit: 0
```

在 `/root/.cache/ms-playwright`、`/usr/bin`、`/usr/local`、`/usr/lib`、`/opt`、`/nix`、`/ms-playwright` 和 `/home/oai` 的受限可执行文件搜索也没有找到 `chrome`、`chromium` 或 `chrome-headless-shell`。

### 回退结论

常规 Playwright 库存在，但没有任何实存浏览器可执行文件。按任务约束未执行 `playwright install`，也未下载依赖。因此测试脚本没能启动产品页面，截图和控制台结果仍为空；状态保持 `EVIDENCE_BLOCKED`。
