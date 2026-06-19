# EP: S6 commit 顯式收尾三件 + 子目錄 EP 歸檔（task #10）

> **parent**: [ep-dev-process-redesign.md](./ep-dev-process-redesign.md)（master 整脊綱要 S6 段展開）
> **本 EP**: commit 收尾 SYSTEM-MAP 升格**顯式三件**（Capabilities + Kanban + SYSTEM-MAP）。補子目錄 EP（如 `dev-process/`）歸檔邏輯（跨目錄 mv 到 `execution-plans/_done/`）。**task #10**：commit message 雙重定義單一真相源化（`code-review.md` Commit Message 產生 ↔ `commit.md` 階段 4）。過渡期手動衍生，標 parent。

## 動機（self-contained 背景）

commit 收尾現「Capabilities + Kanban（大型/中型）」。SYSTEM-MAP 升格**顯式三件**（對齊 ai-development-guide 三層文件體系：CLAUDE.md Capabilities / SYSTEM-MAP / .kanban）。**子目錄 EP 歸檔**（F3）：整脊 EP 在 `dev-process/` 子目錄，歸檔要跨目錄 mv 到 `execution-plans/_done/`（統一歸檔區，不另開子目錄 _done/）。

**task #10**：commit message 雙重定義（`code-review.md:170-194` Commit Message 產生段 ↔ `commit.md` 階段 4 生成 Commit Message）= 兩處定義 commit message 格式/語言規範，drift 風險。單一真相源化。

## 範圍
- **S6a**：commit 階段 3 改「顯式收尾三件」（Capabilities + Kanban + SYSTEM-MAP）+ SYSTEM-MAP 升格（適用對象明文）+ 子目錄 EP 歸檔
- **S6b**：task #10 commit message 單一真相源化（code-review 引流 commit，或定義沉一處）

## 依賴
無

---

## S6a: 顯式收尾三件 + 子目錄 EP 歸檔

### 成功標準
- [ ] commit 階段 3 標題/內容改「顯式收尾三件」：Capabilities ✅ + Kanban Done + **SYSTEM-MAP 狀態更新**（原子操作）
- [ ] SYSTEM-MAP 從「如果存在」改「**消費專案有就顯式更新；ai-rules 元專案正當跳過**」
- [ ] **子目錄 EP 歸檔**：commit 階段 6 補「EP 可能在子目錄（如 dev-process/），歸檔跨目錄 mv 到 `execution-plans/_done/`（統一歸檔區，不另開子目錄 _done/）」
- [ ] 對齊 ai-development-guide 三層文件體系

### 驗證
- `rg "顯式收尾|三件|子目錄.*歸檔|跨目錄|_done|消費專案" commands/commit.md`

---

## S6b: task #10 commit message 單一真相源化

### 成功標準
- [ ] commit message 格式/語言規範單一真相源：定義沉一處（commit.md 階段 4 或 code-review.md），另一處引流
- [ ] 消除 code-review.md:170-194 ↔ commit.md 階段 4 雙重定義 drift

### 驗證
- `rg "commit message 格式|引流|單一真相源" commands/code-review.md commands/commit.md`

---

## 收尾
- 回母 EP：S6 build+commit 後，master S6 段標 ✅；**task #10 關閉**
- 風險：SYSTEM-MAP 升格可能讓元專案（無 SYSTEM-MAP）困惑 → 明文「元專案正當跳過」
