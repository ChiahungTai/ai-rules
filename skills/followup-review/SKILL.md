---
name: followup-review

description: "審查者回頭驗收實作結果，確認修改合理性和不修改的合理性。/followup-review [審查報告]（無參數則從 git 變更推斷）"
when_to_use: "Verify that code changes from a previous review were implemented correctly. Use after /judge-review decisions have been applied."
argument-hint: "可選：貼上原始審查報告和 judge-review 的決策結果；無參數時自動從 git 變更推斷"
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Write", "Edit"]
---

# /followup-review — 審查者驗收實作結果

你是原始 Code Reviewer，回頭驗收實作 AI 的處理結果。確認修改是否合理、不修改是否合理。

委託 Skills：
- [rules-reminder](../rules-reminder/SKILL.md) — Bash 規則

## 核心目標

**「對照原始審查 → 查證實際變更 → 判斷合理性 → 輸出驗收報告」**

### 角色定位

你是**原始審查者**：確認你的問題被正確解決、被拒絕的建議有合理理由、發現新引入的問題。

### 驗收標準

**修改合理性**：確實解決原始問題？未引入新問題？解法合理（不需完美）？
**不修改合理性**：拒絕理由基於事實？原始問題確實不存在？

---

## 執行流程

### 無參數模式（推薦）

1. **優先讀持久化 finding**：讀 caller 指定帳本（鏈上預設 `.review/<branch>.md` 工作帳本；EP Review Cycle 規劃期＝EP review 區段）的 finding 清單；或 `/smell-detector` zoom 報告（`ai-analysis/smell-detector/<dir>/<scope>.md`，finding 帶 ID F1/F2/T1...）— 兩者皆可作為驗收 baseline（zoom 報告是 read-only 偵測器產出，finding + 建議 + 查證誠信，可直接對照驗收）
2. finding 存在 → 逐項驗收(讀修改後程式碼對照原始問題)
3. **無持久化檔才 fallback** `git diff` + `git status` 推斷(舊行為)
4. 變更範圍超出可推斷範圍 → 向用戶確認

### 有參數模式

提供持久化 finding(`/judge-review` 已標 `decision`)→ 按標準流程對照驗收。

### 逐項驗收

- **採納的建議**：讀取修改後程式碼 → 對照原始問題 → 檢查是否引入新問題 → 通過標 `verified`
- **拒絕的建議**：讀取相關程式碼 → 對照拒絕理由 → 重新評估原始問題 → 拒絕合理標 `closed`
- **整體品質檢查**：新引入問題掃描 + 一致性 + 完整性

驗收後更新 caller 指定帳本（鏈上預設 `.review/<branch>.md`；規劃期＝EP review 區段）finding 的 `status`(格式見 [workflow-review-pattern.md](../_common/workflow-review-pattern.md)):`verified`(採納且通過)/ `closed`(拒絕合理)/ 維持 `open`(未通過需再修)。新引入的 Critical / Important 問題,新增 finding(狀態 `open`)。驗收基準優先用 finding 自帶**驗證式**重跑（可機械複驗）——驗證式缺席時退 LLM 對照判讀。

### muse reviewer 續接驗收（委派形態；delegate-bridge ≥1.0.0——未實戰，首跑後回報修訂）

原始 review 若為 muse 委派（經 bridge——reviewer 交接契約的 jobId→ledger sessionId 即續接定址鍵），followup 可定向續接**同一 reviewer session**——帶完整審查記憶（findings 理由、讀過的檔案、考慮過又放過的 near-miss）逐項驗收，非讀檔扮演。

`delegate-bridge task --session-id <review sessionId> -- "<逐項驗收>＋fix commit range"`（family 預設 muse；跨 workspace 加 `--allow-workspace-switch`；語義矩陣與守衛處置見 [model-routing](../model-routing/SKILL.md)「session 定向接續」節）

- 語義＝**mutating 續寫**（append 進原 transcript）——多輪 followup 疊同一卷，reviewer 記得前輪驗收
- prompt 必帶 fix commit range＋明示**重讀當前檔案**（卷內檔案狀態是修前的 stale）
- caller 指定帳本（鏈上預設 `.review/<branch>.md`）仍是法定 findings 帳本（verified/closed/open 由主 session 更新）——session 記憶是保真度升級，非替代
- 簡單 findings 走 fresh session 讀檔較省（續接帶整包 review context，成本高——判準見 handoff skill 邊界表）

---

## 輸出格式

```markdown
## 📋 Followup Review 驗收報告

### 驗收總覽
| 審查建議 | 決策 | 驗收結果 | 說明 |
|----------|------|----------|------|

### 🟢 通過項目 / 🔴 未通過項目 / 拒絕合理性驗證
### 🆕 新發現問題（如有）

### 驗收結論
✅ 全部通過 / ⚠️ 部分需修正 / ❌ 需要重做
```

---

## 執行約束

- **必須查證實際程式碼**：用 git diff + Read 確認
- **必須逐項驗收**：每個建議都有驗收結論
- **合理不等於完美**：確實解決問題即可
- **拒絕不等於錯誤**：有合理依據的拒絕應被接受
- **聚焦實質問題**：不吹毛求疵，關注真正影響品質的問題
- **不重新展開完整 code review**（只驗收，不重審）

---

## 語音通知

遵循 [voice-notification skill](../voice-notification/SKILL.md)（隨機稱謂、sentinel 進度提醒、say 樣板見 skill）：

- **開始**（第一個動作前）：建進度提醒 sentinel + say 開始
  ```bash
  touch /tmp/.claude-voice-pending
  say -v Meijia -r 180 "開始追蹤驗收"
  ```
- **完成**（輸出結果後）：清 sentinel + 套 skill「任務完成」樣板 say（隨機稱謂，填「追蹤驗收完成」）
  ```bash
  rm -f /tmp/.claude-voice-pending
  ```

---

## 流程位置

前置：`/code-review` → `/judge-review` → 實作 AI 完成修改
後續：未通過 → 再次修正 → `/followup-review`；全部通過 → `/commit`

### review 驗收迴圈（canonical 全流程見 [code-review.md](../code-review/SKILL.md)）

```
/code-review（Review LLM）→ /judge-review（Implementation LLM）
→ 實作修改 → /followup-review（Review LLM 驗收）
```
