---
harness-scope: neutral
---

# 驗收證據階層

> **載入機制**: 本檔 source 在 ai-rules repo `rules/`；各家 harness 經全域 guide 部署載入（Claude 端另有 `~/.claude/rules/` symlink auto-load）。**深層理論**（認知誤差與 EP 預見極限、Intent Drift 兩型、filter trap 重構查證、L3 整合實例、Runtime Invariant Assurance、B 軸演進）見 **acceptance-evidence skill**（on-demand）

## 核心原則:證據獨立性

傳統 TDD 的權威性建立在一個從未被明說的前提:測試的「意圖」與實作的「理解」分屬不同認知主體。**AI 同時寫實作與測試時,這個獨立性塌縮。** 測試從「人類意圖的權威表達」降級為「AI 對自己理解的描述」,綠燈只證明「AI 自洽地重複了自己的錯」。最危險的不是測試太弱,而是測試與實作共享同一個錯誤前提 — AI 誤解問題時,它寫的測試忠實反映誤解,實作忠實滿足誤解。

**判斷準則**:驗收證據的強度,取決於「證據來源是否獨立於被驗證物」。AI 同寫 test + impl = 零獨立性 = 證據強度低。

### Claim→Evidence→Trust(no-impact claim 校驗)

當 AI/producer 宣稱「不影響 X」(accounting/risk/invariant)時,這個 claim 須有**獨立機械證據**反證(git diff / rg 殘留 / LSP findReferences),否則 claim 退化為 self-report — AI 同時產 code 與 claim,受同一 mental model drift 污染。**AI 誠實說「沒影響」時最危險** — 獨立性塌縮點。任何「沒影響 X」的 claim 都須獨立證據,不接受自述。

同型 claim 群（均須獨立機械證據，詳案例見 acceptance-evidence skill）：

- **數字/清單類 claim**（計數、規模、盤點）:寫進文檔前用獨立計數命令（`rg | wc -l` / `rg -c`）核對完整輸出，不靠印象或截斷結果人工數——AI 寫盤點清單易憑印象混入/漏掉成員（真實案例：consumers 數 41 誤寫 20，因 `rg | head -20` 截斷）。
- **刪除/死碼自述**（zero caller /「沒人用」）:證據須涵蓋**全消費端**——靜態 import（LSP `findReferences`）+ 字串引用（rg 跨 .py/.yaml/.json）+ **非函式庫消費者**（scripts/、lab/、demo、saved config）+ 動態派發（getattr/importlib/registry auto-discovery/StrEnum 字串值）。只跑 LSP 宣稱「zero hits = 確認」**不足**。最低門檻：刪整檔/整 class 前，rg 符號名跨全專案 + 實際執行 import 測試（L4）受影響消費者——靜態 zero-hit ≠ runtime 無消費者（真實案例：自述「雙工具驗證零 caller」，實際 scripts/ 有 hard-import caller → runtime `ModuleNotFoundError`）。
- **silent-failure claim**（silent drift / 靜默失效）:宣稱「行為 silent」須附**執行證據**（跑了該輸入、觀察到靜默通過），非靜態推論。**silent vs loud 不對稱風險**——誤判 loud（實為 silent）以為會炸卻靜默腐敗（危險）；誤判 silent（實為 loud）虛驚、跑測試推翻（安全）。無執行證據時**預設標 'inferred loud'，禁標 'silent'**。
- **Review 雙向應用**：審查 diff 時看到 `raise`→`return None`、新增/拓寬 `try/except`、crash→filter、validation 緩步化 → 視為潛在 silent-corruption **引入**（loud→silent regression 檢查見 code-review-and-quality skill）。

## 證據階層

「功能完成」不是布林值,是證據債券 — 不同驗證手段產生不同強度的證據,覆蓋不同 bug 類別:

| 層 | 證據形式 | 抓什麼 bug | AI 造假風險 | 風險映射 |
|--|--|--|--|--|
| L1 靜態 | type check / ruff / ast.parse | 語法、型別契約 | 不能(機械執行) | 🟢 低 |
| L2 單元 | unit test(含 mock) | 函式內部邏輯 | **最易**(同義反覆、mock 假設即 bug、測試反映實作) | 🟡 中 |
| L3 整合 | integration(真實 DB / 跨模組 fixture) | 組合契約、跨檔擴散、FK 約束 | 可能 mock 掉關鍵邊界 | 🟡 中 |
| L4 可執行 demo | 真實跑腳本 / 資料片段 | **AI 幻覺 API、第三方程式庫真實行為** | 不能(程式真的跑了),但會選擇性跑 happy path | 🔴 高(外部依賴) |
| L5 對抗性 POC | 刻意用髒資料 / 邊界 / 已知陷阱 | **AI 對邊界的盲區**(除權息、減資、NaN、時區、溢出) | 若 POC 標的也是 AI 挑,會潛意識避開自己盲區 | 🔴 高(數據完整性) |
| L6 人類觀察 | 人在迴圈看真實輸出 / 畫面 / log | **需求誤解**(AI 正確實作了錯誤的理解) | 不會誤信 PASS,但會「看一眼就夠」 | 單向門決策 |

**根本禁令**:用低層證據冒充高層驗收是核心錯誤 — 不是「測不夠多」,而是「用錯層的證據」。現有零散禁令統一解釋為這個原則的不同表現:

| 既有禁令 | 冒充關係 |
|--|--|
| [must-execute](./must-execute-before-complete.md) 禁 ast.parse 取代執行 | L1 冒充 L4+ |
| [quality-constraints](./quality-constraints.md) 禁隔離 unit test 宣稱功能完成 | L2 冒充 L3+ |
| test-driven-development skill 警告過度 mock | L2 的獨立性被掏空 |
| 消費端驗證模式(見 quality-constraints) | L3 的具體化 |

L3 整合層正向實例（mock 抓不到的 source bug）、filter trap 重構查證義務：見 acceptance-evidence skill。

### 證據時效性

證據階層談「強度」,但證據還有「時效」— 測試通過的證據會隨系統演化而**腐化**。重構改變行為後,測試可能:過時但仍通過（死測試:測試被改成迎合新實作,從「驗證意圖」降級為「反映實作」）、或驗證的行為已無關。過時測試比沒測試更危險 — 它給虛假信心。**重構後必須重新確認證據有效**,否則 L2 證據 silently 貶值。

## A / B 雙軸分工

| 軸 | 職責 | 證據層 | 天花板 |
|--|--|--|--|
| **A 機器自驗** | 內部實作細節的正確性 | L1-L3 | **AI 內部自洽** — 機器斷言跳不出 AI 信念體系 |
| **B 人類驗收** | 跨越「自洽 → 對外部正確」的鴻溝 | L4-L6 | 部分落地:debrief + illustrate + smell-detector = 人類 viewport(三層介入);完整 L4-L6 執行驗收仍為設計方向(見 skill) |

**鐵律**:A 是必要不充分,B 是充分性的來源。A 軸深化有邊際效益遞減 — 天花板是 AI 自洽,真正的驗收鴻溝在 B 軸。Agent Review 的「獨立 context」≠「獨立智能」:同家族 LLM 共享系統性偏誤,quorum 對共同盲點無效,A 軸的深層防線最終仍由 B 軸兜底。人審亦有結構上限（疲勞/注意力/確認偏差，經驗無關）→ P0 invariant 需 Runtime Invariant Assurance 補（A 機械、B 人審、runtime assurance 三層守衛,詳見 skill）。

## 與既有規則的關係

風險分級（ai-development-guide「驗證約束」段）決定爬到第幾層（🟢 低風險不需六層——避免過度工程是內建約束）；漸進驗證（[progressive-validation](./progressive-validation.md)）是 L1→L3 爬坡順序（DEPTH-MIN→SAMPLE→FULL）；消費端驗證模式（[quality-constraints](./quality-constraints.md)）是 L3 的具體化，本階層為它提供「為什麼」。階層降低風險、**不消除風險**——每一層都值得懷疑，包括最頂層（L6 人類觀察會疲勞漏見；L5 POC 可能打自己畫的靶）。
