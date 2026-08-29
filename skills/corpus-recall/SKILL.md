---
name: corpus-recall
description: "開新功能/修 bug 前找前因後果 / 這功能之前怎麼做的 / 相關 tours / prior art / corpus 檢索——topic（symbol｜模組路徑｜關鍵詞）→ 前因後果卡片：相關鏈文檔＋tour 走讀入口（職責一句＋為何相關＋confidence）。與 smell-detector 對仗＝行動前偵察雙軸（code 壞味道／敘事脈絡）。"
when_to_use: "Before starting a feature/bugfix/refactor: recall prior narrative context (callstack chains, tours, delta tours) —「之前怎麼做的、有沒有既有鏈」. Also AI self-use at execution-plan 階段 0 全域研究. NOT for: code structure viewport (/illustrate), symbol navigation (LSP/cr-query/hub_refs), post-action understanding (/debrief)."
argument-hint: "<topic> [--repo PATH]"
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
---

# /corpus-recall — 行動前敘事脈絡檢索（topic → 前因後果卡片）

> **受眾**：人類判讀為主（開工前確認前因後果）＋AI 自用（EP 階段 0 素材盤點——LLM 缺 whole picture 會重造既有，檢索是被動觸發不了的，要成為流程一步）。
> 與 `/smell-detector` 對仗＝行動前偵察雙軸：code 壞味道／corpus 敘事脈絡。存在的理由：corpus 超過瀏覽閾值後，「一個個看」不會發生——瀏覽＝找不到＝等於沒寫，本命令是檢索前門。

## 前置偵測（無素材即誠實停）

| 偵測 | 命中 | 未命中 |
|------|------|--------|
| `ai-analysis/blueprint/callstack-plan.md` | 鏈菜單（錨點×職責×優先序）——主索引 | 回「本 repo 無 callstack 語料」＋指向 blueprint-bootstrap 生成路徑，**不硬湊** |
| `.tours/manifest.toml`＋`.tours/**/*.tour` | tour 走讀入口＋sources 交叉 | chain md 可獨立存在——跳過 tour 層續查 |
| `.tours/delta/*.tour` | 近期弧 delta（7 天窗） | 跳過該層 |

`--repo` 省略＝cwd；跨 repo 消費用 `--repo <repo-root>`。

## 檢索食譜（機械層——rg 求全，LLM 不做記憶檢索）

topic 三形態（symbol／模組路徑／關鍵詞）統一跑以下層，機械命中集先求全再判讀：

1. **plan 行匹配**：symbol／路徑 → rg 錨點欄；關鍵詞 → rg 職責行（中文直接 rg；同義詞 LLM 先擴展再 rg——「下單」→order/submit/entry）
2. **tour 檔案面**：`rg <topic> <repo>/.tours/ --glob '*.tour'`——景點 file/pattern 鍵是鏈的實際落點（plan 錨點沒列的模組靠這層）
3. **manifest 交叉**：命中鏈 → `manifest.toml` sources 行 → 對應 callstack md
4. **md 內文**：`rg -l <topic> <repo>/ai-analysis/blueprint/callstack/`——標題／入口總表／UC 映射表
5. **delta 層**：`.tours/delta/` 檔名（日期-task）＋內容命中＝近期弧直接脈絡
6. **（repo 有 code-reality 時）影響域擴展**：topic 是 symbol → `hub_refs <symbol> --repo <repo>` 取 callers/callees 目錄面 → 反查哪些鏈錨在那些目錄——撈「topic 沒直接提到但會被波及」的鏈

## LLM 判讀層（機械命中 ≠ 語義相關）

- 逐條寫「為何相關」一句（同模組／上下游邊／同 UC 場景／歷史決策）——寫不出理由的命中淘汰
- confidence 三級：**高**＝plan 錨點或 tour 景點直接命中／**中**＝影響域或 md 內文命中／**低**＝僅關鍵詞共振（標明保留——人判，不靜默刪）
- 模糊 topic（多義）→ 澄清一次問完（「X 指下單流程還是回測引擎的 X？」），不猜方向

## 輸出合約（前因後果卡片）

```
## 前因後果卡片：<topic>
- 相關鏈 N 條（高 x／中 y／低 z）：
  - [高] <鏈名>（<軌>）：<plan 職責一句>——為何相關：<理由>；
    走讀 .tours/<路徑>／深讀 callstack/<md>
- 近期 delta（7 天窗命中時）：<task> @ <date>——一句摘要
- 空手誠實：無命中 → 「無相關鏈」＋一句建議（生成候選走
  blueprint-bootstrap plan 枚舉；或該 topic 尚無語料）——不硬湊
```

## 邊界

- 卡片是**索引非內容**：不代讀完整鏈——每條帶走讀＋深讀雙入口，深讀由人/AI 按需
- YAGNI：rg＋LLM 判讀，不上向量/嵌入索引——corpus 百篇級再議
- 語料時效：plan/tour 是快照（drift 治理歸 tour-bootstrap 的 validate/upgrade）——卡片引用鏈名與檔案路徑，不引行號

## 與其他命令協作

| 想問的問題 | 命令 |
|-----------|------|
| 開工前：之前怎麼做的、有哪些既有鏈（本命令） | `/corpus-recall` |
| 開工前：code 有沒有壞味道 | `/smell-detector` |
| 結構長怎樣（whole picture） | `/illustrate` |
| 改完後：改了啥 | `/debrief` |
| corpus 建置與治理 | [tour-bootstrap](../tour-bootstrap/SKILL.md)／[blueprint-bootstrap](../blueprint-bootstrap/SKILL.md) |

## 流程位置

```
行動前偵察：/smell-detector（code 面）＋/corpus-recall（敘事面）
→ EP（階段 0 全域研究可自用本命令）→ /implement → /debrief → /post-build → /commit
```
