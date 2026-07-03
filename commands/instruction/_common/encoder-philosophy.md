# Encoder Philosophy — CLAUDE.md 品質標準

> **載入時機**: 僅在 `/instruction:*` 命令執行時載入，不放入 `rules/` 避免每個 session 浪費 context。

---

## 核心概念：CLAUDE.md 是 Encoder

CLAUDE.md 是模組知識的**壓縮表示**（Encoder）。品質的終極驗證是 **Decoder Test**：

給一個 LLM 讀取 CLAUDE.md，然後問它關於這個模組的設計決策、架構約束、非顯而易見的選擇。如果它能正確回答，說明 Encoder 成功捕獲了本質知識。

**Decoder Test 是 dry run**，不是每個 session 都執行。它在文檔維護時用來驗證品質，不是日常操作。

---

## Signal / Noise 框架

### High Signal — 必須保留

從程式碼**猜不到**的知識：

| 類型 | 說明 | 範例 |
|------|------|------|
| 設計理由 | 為什麼這樣做，而非那樣做 | 「選擇 Polars 而非 pandas，因為向量化計算在 40+ 指標場景下效能差異 10x」 |
| 架構約束 | 不可妥協的設計限制 | 「StateManager 雙向綁定必須用 Guard Clause 防止無限迴圈」 |
| 非顯而易見的選擇 | 看起來反直覺但有意義的決策 | 「stdout 預設 OFF，全由 print() 控制 — Logger 不輸出到 stdout」 |
| 模組邊界 | 這個模組不做什麼 | 「rate_limiter 不處理重試邏輯，只做速率限制」 |
| 失敗教訓 | 從實際 debugging 經驗得到的規則 | 「Panel Tabs 重建後非 active tab 的 Tabulator 點擊無反應 — 用 in-place update 解決」 |
| 型別關係 | 相似型別的用途區別和使用場景 | 「ConditionFilter 是純聲明式（YAML→Filter Tree），ObservationFilter 是 runtime 條件（tags→Polars）— 兩者語義不同，前者是設計意圖，後者是執行表示」 |
| Pipeline 編排 | 多步驟流程的順序和數據銜接 | 「PerStockDataPipeline.build(): load OHLCV → features → structure → setup classify → filter tree — 數據在 steps 間以 MLDataset 傳遞」 |
| 慣例映射 | 專案特定的約定，無法從名稱推導 | 「STATE_DIRECTIONS 將 trajectory state 映射為 signal direction，如 oversold→bullish — 語義映射，非 enum 對齊」 |
| 負空間指導 | **不要做什麼** — LLM 無法自行推導「不做」 | 「API 內部函數之間不要加驗證 — 共用型別合約已保證型別安全」 |
| 行為校準 | 判斷尺度 — LLM 不會自行產生校準原則 | 「拒絕≠錯誤：reviewer 拒絕建議不代表建議有問題，可能是 reviewer 過度吹毛求疵」 |

### Low Noise — 應該移除

從程式碼**可直接推導**的內容：

| 類型 | 說明 | 範例 |
|------|------|------|
| API 簽名 | 函數參數和回傳值型別 | `def process(data: pl.DataFrame, config: Config) -> pl.DataFrame` |
| 參數表 | 完整的參數列表和預設值 | `period: int = 14, method: str = "ema"` |
| 欄位列表 | DataFrame 的所有 column 名稱 | `open, high, low, close, volume` |
| 完整範例 | 超過 5 行的程式碼範例 | 30 行的 end-to-end 使用流程 |
| 通用知識 | LLM 訓練資料已有的知識 | 「Polars 比 pandas 更快」 |

### 程式碼範例限制

- **<= 5 行**: 可接受，展示關鍵用法
- **>5 行**: 應精簡為一句話描述 + 源碼引用（`檔案:行號`）

---

## 常見誤解

| 誤解 | 事實 |
|------|------|
| Decoder Test = 讓 LLM 重寫程式碼 | Decoder Test 是理解力驗證，不是系統重建 |
| 越短越好 | 長度不是目標，signal/noise ratio 才是 |
| 所有程式碼範例都該移除 | <= 5 行的關鍵用法範例有保留價值 |
| 架構圖是 noise | 高層級架構圖是 high signal（展示模組關係） |
| 完整 API 文檔是 signal | API 簽名是 noise，設計理由才是 signal |
| 負空間可以推導所以能刪 | 「不做什麼」LLM 無法自行推導 — 蒸餾時必須保留負空間指導和行為校準 |
