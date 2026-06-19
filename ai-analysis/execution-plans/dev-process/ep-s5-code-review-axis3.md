# EP: S5 code-review axis3 接線 + 六軸單一真相源化（task #9）

> **parent**: [ep-dev-process-redesign.md](./ep-dev-process-redesign.md)（master 整脊綱要 S5 段展開）
> **本 EP**: code-review axis 3（Architecture）調用 [architecture-viewport](../../../skills/architecture-viewport/SKILL.md) skill（吸收原 arch-review 機器結構職責，A 軸）+ top-down 審查順序。**task #9 核心**（judge-review 已定決策 (a)）：六軸定義單一真相源化（沉 [code-review-and-quality](../../../skills/code-review-and-quality/SKILL.md) skill，command 引流）。review 鏈合併（code review 含 arch → judge 一次）。過渡期手動衍生，標 parent。

## 動機（self-contained 背景）

code-review axis 3（[code-review.md](../../../commands/code-review.md) `:106-107`）吸收原 arch-review 職責 B（機器結構符合度）。調用 S1 skill。**top-down**（B7）：axis 3 結構先於其他軸正確性 — 結構錯了正確性審白費。

**task #9 核心**（judge-review 查證 + 決策 (a)）：六軸雙重真相源 — `code-review.md:98-121` 六軸摘要 ↔ `code-review-and-quality/SKILL.md:12-57` 六軸詳解，且 `:15` 已「委託 code-review-and-quality — 六軸方法論」卻又在 `:98-121` 自寫 = **「委託又自寫」矛盾**。名稱也不一致（command「Readability/UC Coverage」vs skill「Readability & Simplicity/Capability Coverage」）。

**決策 (a)**：六軸**定義**單一真相源化（沉 skill，command 引流）。理由：`/code-review` 觸發時 skill 已委託載入（`:15`），command 摘要移除不增加 context 切換成本，卻消除「委託又自寫」矛盾 + drift 根因。**範圍邊界**：只單一化六軸「定義」；command **保留特有段**（深層思考 `:123-130`、docs mode `:74`、UC Coverage 審查細節 `:114-121`、審查模式 Workflow `:52-86`）。

**review 鏈合併**（B5/SM-10）：code review 含結構（axis 3）→ 不再分開 arch review + judge，**judge 一次**。

## 範圍
- **S5a**：六軸定義單一化（command `:98-121` 引流 skill）+ axis 3 接線（`:106-107` 調用 skill + top-down + 受眾明文）+ 軸表名稱統一（`:63-73`）
- **S5b**：agent prompt（`:76-82` Architecture 軸引用 skill）+ 流程位置（`:200-206` review 鏈合併 judge 一次）

## 依賴
S1（architecture-viewport，已完成 ✅）

---

## S5a: 六軸單一化 + axis 3 接線 + top-down

### 成功標準
- [ ] 六軸**定義**引流 skill（command `:98-121` 摘要移除，改「六軸定義見 code-review-and-quality skill — 單一真相源」）；保留深層思考 + UC Coverage 細節（command 特有）
- [ ] **axis 3**（`:106-107`）：調用 architecture-viewport skill（city map/dep weight/重用/LSP 查證 → 機器 finding A 軸）+ top-down（結構先於正確性）+ **受眾明文**（axis 3 與 illustrate 用同一 skill；axis 3 產機器 finding A 軸 / illustrate 渲染給人 B 軸）
- [ ] **軸表**（`:63-73`）名稱統一 skill：Readability → Readability & Simplicity；UC Coverage → Capability Coverage

### 驗證
- `rg "architecture-viewport|top-down|單一真相源|Readability & Simplicity|Capability Coverage|axis 3.*機器 finding" commands/code-review.md`

---

## S5b: agent prompt + 流程位置 review 鏈合併

### 成功標準
- [ ] agent prompt（`:76-82`）：Architecture 軸引用 architecture-viewport + architecture-thinking
- [ ] 流程位置（`:200-206`）：review 鏈合併（code review 含 axis 3 結構 → judge **一次**；不再 arch→judge→code→judge 兩次 judge）

### 驗證
- `rg "review 鏈|judge.*一次|architecture-viewport|architecture-thinking" commands/code-review.md`

---

## 收尾
- 回母 EP：S5 build+commit 後，master S5 段標 ✅；**task #9 關閉**（六軸單一化落地）
- 風險：六軸定義移除可能讓 command 失自包含 → skill 已委託載入（`:15`），引流不增加成本；保留 command 特有段（深層思考/UC Coverage 細節）維持執行指引
