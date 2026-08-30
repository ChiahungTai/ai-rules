# [tag:skills] 條目重複機械防護（池衛生）

## 目標
memory 索引事故的正回授鏈中「同主題重複條目檔」目前只有 prose 紀律（寫入四問 #2 rg 查重）——重複條目帶合法 frontmatter 時 generator 來者不拒照樣投影。評估機械防護形態（寫入前 hook 查重建議？audit 層自動 near-dup 偵測？）。

## 相關
- `rules/context-management.md`「Memory 生命周期規範」寫入四問
- `skills/memory-audit/SKILL.md` cluster merge 機械觸發（同主題散檔 ≥3）

## 驗收標準
- 提案評估（YAGNI 檢驗：重複率數據支撐才建；先量測兩池 near-dup 現況）
- 若建：併發安全（勿在寫入熱路徑加重量）；若不建：記錄數據與理由關卡

## 備註
hardening EP（memory-lifecycle-hardening-ep）明確不做項——防 scope creep 拆卡追蹤。audit skill 的 cluster merge 觸發已是半機械防線，先看它夠不夠。
