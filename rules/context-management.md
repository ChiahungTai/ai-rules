---
harness-scope: neutral
---

# Context 管理

> **載入機制**: 本檔 source 在 ai-rules repo `rules/`；各家 harness 經全域 guide 部署載入（Claude 端另有 `~/.claude/rules/` symlink auto-load）

## Session 管理

### Context 保護

- **任務切換時重置 context**：不同任務之間重置 context（Claude: `/clear`），避免不相關資訊累積
- **研究用 subagent**：大範圍探索交給 Agent 在獨立 context 中完成，結果摘要回主 session
- **Writer/Reviewer 分離**：審查自己剛寫的 code 有 bias，開新 session 審查品質更好

### 糾正策略

- 同一問題連續糾正 2 次仍失敗 → 重置 context（Claude: `/clear`），用更好的 prompt 重來（累積的失敗嘗試比乾淨 context 更糟）
- 糾正超過 2 次 → 說明 prompt 不夠好，不是 AI 不夠努力

## STATE.md（Last session 觀察層）

STATE.md 定義（定位 / 觀察層 vs 事實層邊界 / 職責矩陣 / 生命週期 / 路徑 / 觸發）與寫入步驟見 state-md-write 共用子範本（Claude: `../skills/_common/state-md-write.md`）（寫入由 at/deep-work 觸發；Open failures 走 kanban 不進 STATE）。

## Memory 生命周期規範（cluster-first＋索引機械投影）

harness auto memory 預設「one file = one fact」的「fact」操作定義 = **一個主題的教訓群（cluster）**，非一個事故；「check for an existing file — update rather than duplicate」的 update 目標 = 既有主題檔**加段**（非開新檔）。

### 單一寫入點：條目檔 frontmatter

**條目檔（frontmatter `name`/`description`/`type`）是唯一寫入點；`MEMORY.md` 索引是其機械投影，禁手寫**。索引載入上限＝200 行或 25,000 字元（UTF-16，兩端同語義）先到為準，超限截斷（附 WARNING，尾端條目不載）——手維護索引必漂移（截斷 → 查重漏同主題 → 近重複寫入 → 更肥 → 更截斷，正回授；2026-08-30 mosaic 56.6KB 實證）。

- 裝有 generator（`memory/_generate_index.py`）的專案：寫/改條目檔後跑 `python3 <memory-dir>/_generate_index.py`（Stop hook 亦自動重生成；手寫 MEMORY.md 被 PreToolUse hook 擋）。資產源與部署操作見 memory-audit skill（單一敘述處；rule 只立紀律）
- 未裝 generator 的專案：手維護索引，cluster-first 沿用

### 寫入四問（新教訓產生時依序）

1. **repo 可推導 or 通用原則？** → git log / instruction 檔 / 程式碼 / **進行中 EP 的進度與狀態（住 EP 檔）**可推導 → 不寫；**LLM 通用做事原則/方法論**（與 user 個人化無關、任何 session 都適用）屬 rules/skills 知識——rule 缺就補 rule，不開 memory 條目。memory 收與 user／專案綁定的事實（偏好、糾正、專案約束、外部資源參照）——通用工程原則不收
2. **同主題已有？** → `rg -i <關鍵詞> <memory-dir>/` 全檔掃（**不信 MEMORY.md 索引**——載入截斷下尾部條目不可見）；命中 → 既有檔加段（段標題保留原始 name、標 original type）；**進行中弧線條目禁加段**——弧線進度每 session 追加是膨脹主因（實證：單檔 98 次 Edit 養到 84KB），等弧線收案一次性蒸餾；無 → 才開新檔
3. **project-\* 已完結？** → 任務閉環先收斂既有 project 條目（刪現況細節、留決策教訓）再開新檔
4. **尺寸預算？** → frontmatter `description` ≤100 chars（索引行原料；>100 被 PreToolUse hook 硬擋——hook 僅攔主 session，subagent 寫入不觸發）；條目檔（含 frontmatter）≤12,000 chars（膨脹超限被 hook 擋；收斂方向＝改後比原檔短，放行）——超額 = 內容該住 EP 檔/repo 的訊號；索引軟上限 150 行，逼近 = cluster merge／收斂觸發

量化清理（同主題散檔合併、收斂執行、audit）由 memory-audit skill 承載（Claude: `../skills/memory-audit/SKILL.md`），寫入端只管四問。
