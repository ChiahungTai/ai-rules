---
harness-scope: neutral
paths:
  - "**/*.md"
---

# Instruction File 撰寫規範

修改任何 instruction 檔前必載入 **instruction-writing skill**；frontmatter、章節、引用、導航/Decoder Test、映射 drift、自洽五維與元資訊禁令以該 skill 為單一源。

## Always-on 核心

- 雙檔：每層 `AGENTS.md` 是 harness-neutral source，body 禁 Claude 專屬散文；`CLAUDE.md` 是 `@AGENTS.md` thin wrapper。全域 guide 獨立於專案 root；`@` 僅 Claude 展開，AGENTS.md 禁 transclude。
- Signal/Noise：保留設計理由、約束/邊界、失敗教訓、型別區別、Pipeline/慣例映射、共用基建、負空間、行為校準；易被合理化動搖的規則保留「補充論證／第一性原理」。
- 可推導簽名/參數/欄位、Class→檔案表、重複導航、>5 行完整範例屬噪音；泛用 rule 用 placeholder，真實失敗案例可保留專案實例但須標「真實案例」。
- **禁統計（行數/字數）、版本號、更新日期、Changelog**。
- 導航只負責概念→symbol 種子；symbol→位置交 LSP；Decoder Test 見 instruction-writing skill。
