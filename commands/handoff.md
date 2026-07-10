---
description: "產出 self-contained 交接 prompt：把當前工作（進度 + 決策脈絡 + 下一步）打包給另一個 session/repo/provider。與 /at（usage resume）分工 — handoff 交別人，/at 自己續"
when_to_use: "Hand off work to another Claude Code session, another repo's session, or a cross-provider web LLM (ChatGPT/Gemini). Package current progress + decision rationale + next step into a self-contained prompt. Not for usage-limit resume (use /at)."
usage: "/handoff [同repo|跨repo|跨provider] [任務描述] [--save]"
argument-hint: "[接手方] [任務] [--save]"
allowed-tools:
  - Bash
  - Read
  - Write
---

# /handoff — Self-Contained 交接 Prompt 產生器

把當前工作結晶成 self-contained prompt，交給另一個 session / repo / provider。解決「每次口語『給個 prompt』+ 手工湊 + 決策脈絡帶不過去」的反覆動作。

委託 Skills：
- [self-contained-prompt](../skills/self-contained-prompt/SKILL.md) — 交接 prompt 設計原則（**接手方三層、標準 schema、drift 防護、跨 provider 機密**）；本 command 是薄 adapter，原則不在這重複
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則

## 與 /at 的邊界（執行前確認）

| 命令 | 解什麼 | 觸發 |
|------|--------|------|
| `/at` | **時間接續**：usage 用盡，自己 resume | 5h usage limit |
| `/handoff` | **空間分工**：交另一個 session/provider | 主 session 在忙 / 要第二意見 / 跨 repo |

要「自己之後繼續」→ `/at`；要「別人現在接」→ `/handoff`。

> **STATE.md 非交接選項**：STATE.md（Last session 觀察，每 session 覆寫）不是命令、非 `/at`/`/handoff` 替代。`/at` resume 時讀它補 observation（寫入步驟見 [state-md-write](./instruction/_common/state-md-write.md)）；交接決策仍是 `/at` vs `/handoff` 二選一。

---

## 執行流程

### Phase 0：判斷接手方 + 收集進度

**接手方**（決定 self-contained 程度，三層判定見 [self-contained-prompt](../skills/self-contained-prompt/SKILL.md)「接手方三層」）：`同repo`（= 同 repo 的新 session，預設）/ `跨repo` / `跨provider`。arg 未指定 → 從對話偵測（「問 ChatGPT/Gemini」= 跨 provider、「給 `<other-repo>` 那邊」= 跨 repo、其餘預設同repo），不確定就問一句。

**收集進度**（機械）：

```bash
git log --oneline -5          # 近期 commit（baseline + 已完成）
git status --porcelain        # 未 commit 變更
git rev-parse HEAD            # baseline commit hash
```

+ 從當前對話摘「已交代的決策（為何選 X 不選 Y）+ 下一步 + 待決項」（用戶交代過的才帶，見 skill「決策脈絡原則」）。
+ 識別當前 EP（有 → 引用段落）。

### Phase 1：套標準 schema

依 [self-contained-prompt](../skills/self-contained-prompt/SKILL.md)「標準 schema」八欄（任務一句話 / baseline commit / 來源 EP / 已完成清單 / 已決策 / 下一步 / 驗收 / 承接 commit 不重做）。

有 EP → 引用段落 + 補這次對話剛定的決策；無 EP → 現擠 brief（完整 schema）。

### Phase 2：按接手方調嵌入程度

依 skill「接手方三層」：同repo 引用路徑（對方讀得到 repo）/ 跨 repo 加跨 repo 背景 + 嵌源 repo 相關片段 / 跨 provider 嵌**最小必要**片段。

### Phase 3：跨 provider 機密檢查（僅跨 provider）

依 skill「跨 provider 機密檢查」，flag 敏感內容（帳號/金鑰/真實持倉/未公開策略/客戶資料）並提醒 redact（代稱/抽象化）。

### Phase 4：產出

預設印 markdown code block（複製貼到目標 session/provider）。

帶 `--save` → 額外寫 `.at-contexts/handoff-{ts}.md`（沿用既有 context 檔機制）。

---

## 參數

| 參數 | 說明 |
|------|------|
| 接手方（可選）| `同repo` / `跨repo` / `跨provider`；省略則偵測或問 |
| 任務描述（可選）| 交接的工作；省略則從當前對話推導 |
| `--save` | 額外寫 `.at-contexts/handoff-{ts}.md` |

## 執行約束

### 強制

- 必須套 skill 標準 schema
- **已決策（為何選 X 不選 Y）必含**（決策脈絡是最常漏的）
- 嵌 code 必須讀回 commit 版本（drift 防護）
- 跨 provider 必須跑機密檢查

### 禁止

- ❌ 嵌整檔（只嵌回答問題必要的最小片段）
- ❌ 把用戶沒交代的決策硬擠進去
- ❌ 跨 provider 未跑機密檢查就產出
- ❌ 處理 usage resume（那是 `/at`）

## 流程位置

```
（主 session 在忙 / 要第二意見 / 跨 repo）→ /handoff [接手方] → 貼到目標 session/provider
```

接手方給建議 → 貼回原 session → `/judge-review` 評估採納。
