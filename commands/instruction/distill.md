---
description: "蒸餾 Markdown 文檔，提煉核心精華，移除可推導內容"
when_to_use: "Distill instruction files (根 AGENTS.md source + CLAUDE.md wrapper/模組 nav) by separating signal from noise: keep design rationale and constraints, remove API signatures and derivable content. 雙檔模式見 instruction-writing.md。"
usage: "/instruction:distill [目錄路徑] [選項]"
argument-hint: "/instruction:distill [目錄路徑] [--recursive] — 預設處理當前目錄，可指定目錄或 .md 檔案"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
---

# /instruction:distill — 蒸餾精簡工具

> **instruction file 雙檔模式**：蒸餾對象含根 `AGENTS.md`（source）+ `CLAUDE.md`（wrapper + 模組導航）——遞迴發現時兩者皆納入。見 [instruction-writing.md](../../rules/instruction-writing.md)。

Markdown 文檔 signal/noise 分離，提煉高 signal 核心知識。

Signal/noise framework: [encoder-philosophy.md](./_common/encoder-philosophy.md)

## 適用文檔

- **AGENTS.md（source）/ CLAUDE.md（wrapper）**：AI 協作指南，保留核心原則和約束
- **說明文檔**：描述現有系統運作的技術文檔，保留關鍵行為描述和架構
- **不適用**：設計文檔（描述概念、提案）— 設計演進過程可能需要保留歷史脈絡

---

## Signal/Noise 分類

#### ✅ High Signal — 必須保留

從程式碼**猜不到**的知識：設計理由、架構約束、非顯而易見的選擇、模組邊界、失敗教訓、核心原則/約束

#### ❌ Low Noise — 應該蒸餾

從程式碼**可直接推導**：API 簽名、參數表、欄位列表、完整範例（>5 行）、過時範例、重複說明、通用知識

#### ⚠️ 灰色地帶（預設保留）

| 內容類型 | 保留條件 | 移除條件 |
|---------|---------|---------|
| 範例程式碼 | ≤ 5 行，展示關鍵用法 | > 5 行或過時、重複 |
| 檢查清單 | 行為約束、決策要點 | 顯而易見的項目 |
| 配置參數 | 影響行為的關鍵參數 | 很少修改的環境參數 |

---

## 執行流程

1. **掃描文件**：識別 High Signal、Low Noise、灰色地帶
2. **顯示預覽**：列出三類內容數量及預估結果
3. **用戶確認**：詢問是否執行
4. **執行蒸餾**：備份原檔（`.backup`），寫入蒸餾結果
5. **Decoder Test（dry run）**：驗證蒸餾後的 Encoder 品質 — 回答職責、設計決策、約束、邊界四個核心問題。有失敗 → 從 `.backup` 還原

### Low Noise 處理策略

蒸餾不是「直接刪除」，而是 signal/noise 分離：
- ❌ 直接移除：詳細程式碼步驟、過多配置參數列表、版本變更歷史
- ✅ 簡潔描述替代：一句話總結 + 源碼引用（`config.py:15-30`）

遞歸發現邏輯: [recursive-discovery.md](./_common/recursive-discovery.md)

---

## 參數

| 參數 | 說明 |
|------|------|
| **無參數** | 蒸餾當前目錄的 instruction files（根 AGENTS.md + CLAUDE.md） |
| **檔案/目錄路徑** | 蒸餾指定檔案或目錄 |
| **--recursive, -r** | 遞歸處理所有子目錄的 instruction files（AGENTS.md + CLAUDE.md） |
| **--dry-run** | 預覽模式，不實際修改 |
| **--aggressive** | 高純度蒸餾，只保留絕對核心原則 |
| **--moderate** | 標準蒸餾（預設） |
| **--conservative** | 輕度蒸餾，只去除明顯冗餘 |

---

## 執行約束

- **謹慎原則**：有疑問就保留。寧可少刪也不要誤刪
- **備份優先**：蒸餾前必須建立 `.backup` 檔案
- **AI 導航價值優先**：架構圖、核心表格、使用範例、引用來源必須特別謹慎

遞歸處理約束: [recursive-constraints.md](./_common/recursive-constraints.md)

---

> **蒸餾哲學**: signal/noise 分離。保留從程式碼猜不到的設計知識，移除可推導的冗餘內容。目標不是越短越好，而是提升 signal/noise ratio。
