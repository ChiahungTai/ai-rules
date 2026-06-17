---
description: "定期讀 ai-analysis/flow-feedback/ 累積回饋，找重複摩擦 + 聚合 type-2 設計缺陷，跟 user 討論怎改善 skills/commands。/flow-review [--since <date>]"
when_to_use: "Periodic review of accumulated flow-feedback. User fires when they have time. LLM globs all feedback files, finds recurring friction (systemic) + aggregates type-2 design-flaw candidates, then discusses improvement directions with the user. B-axis: human judgment drives the improvement decisions. Output → /spec (big change) or kanban card (small change) → /build."
usage: "/flow-review [--since <date>]"
argument-hint: "無參數讀全部 / --since YYYY-MM-DD 限定日期後"
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
---

# /flow-review — 摩擦回顧 + 改善討論

> **核心理念**：演化迴圈的**討論端**。讀累積 flow-feedback → 找 pattern → 跟你討論 → 改善決策。深度反思在這裡（human-in-loop, B 軸），不在 `/flow-feedback`。

委託 Skills：
- [rules-reminder](../skills/rules-reminder/SKILL.md) — Bash 規則

---

## 流程

### 1. glob 回饋
`ai-analysis/flow-feedback/*.md`（或 `--since <date>` 限定）。若空 → 提示「尚無 feedback，先跑 `/flow-feedback`」。

### 2. 聚合分析
- **重複摩擦**：同一 command/skill 跨多筆反覆出現 → **系統性問題**（單次 = 偶然，重複 = 該改）
- **type-2 聚合**：跨筆的設計缺陷候選合併、強化
- **摩擦 heatmap**：哪個 command/skill 最多摩擦（tags 聚合）

### 3. 討論（互動，B 軸）
- 報告聚合發現（重複 + heatmap + type-2 候選）
- **挑戰 type-1**：這真的是時機問題，還是 type-2 設計問題被誤判成時機？（防 type-1 掩蓋 type-2）
- **深 type-2**：設計缺陷確認 + 改善方向探討
- 開放討論，不急結論（可多次 review 才定案）

### 4. 決策 → 落地

| 共識類型 | 去向 |
|---------|------|
| 大改（重寫 command、新命令） | `/spec` → kanban |
| 小改（措辭、流程微調） | kanban card |
| 還沒想清楚 | 留在 feedback，下次 review 再議 |

> **歸檔生命週期**：決策且對應變更經 `/commit` 落地 → /commit 自動把該 feedback 歸檔到 `ai-analysis/flow-feedback/_done/`（同 EP `_done/` 哲學，見 /commit 階段 2.8）；「還沒想清楚」留 root 供下次 review。active inbox（root）= 未結案項。

---

## 討論方法論（防退化成閒聊）

- **找重複**：單次摩擦可能是個案，重複才是系統性
- **聚 type-2**：高價值，主動追
- **挑戰 type-1**：type-1 最容易產但最淺，逐一問「這真的只是時機？」
- **不替人決定**：LLM 提素材 + 挑戰，改善決策是你的判斷

---

## 邊界

- **B 軸**：討論品質取決於你的領域判斷 + 反覆詰問（像挖 `/deliverable-review` 設計缺陷那樣）。LLM 是素材提供者 + 挑戰者，不是決策者。
- **不急**：累積不夠或沒想清楚，就留著下次。寧可慢，別誤改。

---

## 與其他命令

- ← [`/flow-feedback`](./flow-feedback.md)：素材源（每筆 feedback）
- → `/spec` / kanban card / `/build`：改善落地
- 相關：`/project-review`（專案健康）；本命令聚焦 **session 摩擦驅動的系統演化**
