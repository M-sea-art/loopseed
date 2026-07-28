# 雨夜客栈：守灯人

`C0 PROTOCOL_ONLY`

一个无外部依赖的单屏浏览器游戏垂直切片。玩家在三夜之间，将仅有的九格灯火分给三位旅客。每次选择都会消耗真实灯火、留下后果，并改变黎明结局。

## 运行

在本目录执行：

```bash
python -m http.server 4173
```

然后打开 `http://127.0.0.1:4173/`。

## 操作

1. 每夜选择一位旅客。
2. 阅读即时后果后进入下一夜。
3. 第三夜选择后迎接黎明。
4. 使用“再守三夜”尝试另一条结局。

## 证据边界

本产物应用冻结的 v0.5 Evidence-Governed overlay 来组织 Project Binding Receipt、Evidence chain、Production Frontier 和分离状态。它只代表 `C0 PROTOCOL_ONLY` 实验产物，不声称验证了可执行的 LoopSeed v0.5 Runtime。
