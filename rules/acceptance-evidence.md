---
harness-scope: neutral
---

# 驗收證據階層

## 核心原則:證據獨立性

證據強度取決於來源是否獨立於被驗證物。AI 同寫 test＋impl 共享理解，可能忠實實現同一錯誤前提；綠燈只證明自洽。認知誤差、Intent Drift、filter trap、L3 實例、證據時效性、A/B 軸限制及 runtime assurance 見 acceptance-evidence skill。

### Claim→Evidence→Trust(no-impact claim 校驗)

producer 宣稱「不影響 X」（accounting/risk/invariant）須有獨立機械證據（diff、rg 殘留、LSP references）；self-report 不能取代查證。其他 claim 類型見 acceptance-evidence skill。

<!-- bundle: skip-start -->
- **數字/清單類 claim**（計數、規模、盤點）:寫進文檔前用獨立計數命令（`rg | wc -l` / `rg -c`）核對完整輸出，不靠印象或截斷結果人工數——AI 寫盤點清單易憑印象混入/漏掉成員（真實案例：consumers 數 41 誤寫 20，因 `rg | head -20` 截斷）。
- **刪除/死碼自述**（zero caller /「沒人用」）:證據須涵蓋**全消費端**——靜態 import（LSP `findReferences`）+ 字串引用（rg 跨 .py/.yaml/.json）+ **非函式庫消費者**（scripts/、lab/、demo、saved config）+ 動態派發（getattr/importlib/registry auto-discovery/StrEnum 字串值）。只跑 LSP 宣稱「zero hits = 確認」**不足**。最低門檻：刪整檔/整 class 前，rg 符號名跨全專案 + 實際執行 import 測試（L4）受影響消費者——靜態 zero-hit ≠ runtime 無消費者（真實案例：自述「雙工具驗證零 caller」，實際 scripts/ 有 hard-import caller → runtime `ModuleNotFoundError`）。
- **silent-failure claim**（silent drift / 靜默失效）:宣稱「行為 silent」須附**執行證據**（跑了該輸入、觀察到靜默通過），非靜態推論。**silent vs loud 不對稱風險**——誤判 loud（實為 silent）以為會炸卻靜默腐敗（危險）；誤判 silent（實為 loud）虛驚、跑測試推翻（安全）。無執行證據時**預設標 'inferred loud'，禁標 'silent'**。
- **Review 雙向應用**：審查 diff 時看到 `raise`→`return None`、新增/拓寬 `try/except`、crash→filter、validation 緩步化 → 視為潛在 silent-corruption **引入**（loud→silent regression 檢查見 code-review-and-quality skill）。
- **自報元資料不可信**（自報分類／判讀元資料）：agent 對自己輸出的 label 統計禁當驗收統計源；正解＝llm_label vs 標準答案逐案機械比對，禁用自報欄位做統計。
<!-- bundle: skip-end -->

## 證據階層

| 層 | 證據與覆蓋 | 限制/風險 |
|---|---|---|
| L1 靜態 | type check/ruff/ast.parse；語法、型別 | 低風險 |
| L2 單元 | unit test（含 mock）；函式邏輯 | mock 假設可能即 bug |
| L3 整合 | 真 DB/跨模組 fixture；組合/FK/擴散 | 仍可能 mock 關鍵邊界 |
| L4 可執行 demo | 真腳本/資料；API/第三方真實行為 | 可能只挑 happy path |
| L5 對抗性 POC | 髒資料/已知陷阱：除權息、NaN、時區、溢出等 | AI 仍可能避開盲區 |
| L6 人類觀察 | 真輸出/畫面/log；需求理解 | 疲勞、確認偏差 |

**禁用低層證據冒充高層驗收**；低風險不必爬滿六層，風險分級決定深度。驗證順序/消費端模式見 [quality-constraints](quality-constraints.md)；證據時效、A（L1–L3）/B（L4–L6）分工、同家族共同盲點與 P0 三層守衛見 acceptance-evidence skill。
