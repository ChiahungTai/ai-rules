---
harness-scope: neutral
paths:
  - "**/*.md"
---

# Instruction File 撰寫規範

修改任何 instruction 檔前載入 **instruction-writing skill**：frontmatter、章節、引用、導航/Decoder Test、映射 drift、自洽五維與元資訊禁令的單一源。

## 檔案命名（雙檔模式）

每層 `AGENTS.md` 是 harness-neutral source，body 不放 Claude 專屬散文；Claude 端 `CLAUDE.md` 是 `@AGENTS.md` thin wrapper。全域 guide 獨立於專案 root AGENTS。**@ transclusion 僅 Claude 展開，AGENTS.md 禁用 @ 拉內容**。

## 內容分類（精簡版）

以 AI 可執行性與 Signal/Noise 為準。

- 保留：設計理由、約束、邊界、失敗教訓、型別區別、Pipeline 編排、慣例映射、共用基建、負空間與行為校準。why 預設一句；易被合理化動搖的規則保留「補充論證／第一性原理」。
- 避免：可推導簽名/參數/欄位、Class→檔案表、重複導航、超過五行完整範例。泛用 rules 用 placeholder；真實失敗案例例外，須標「真實案例」。
- **禁止加入統計（行數/字數）、版本號、更新日期、Changelog**；專注當前知識與執行約束。

## 導航優先原則

導航提供概念→symbol 種子；符號→位置由 LSP 查。兩者分工與 Decoder Test 見 instruction-writing skill。
