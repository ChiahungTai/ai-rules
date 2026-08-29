---
harness-scope: neutral
---

# AI 行為約束

> **載入機制**: 本檔 source 在 ai-rules repo `rules/`；各家 harness 經全域 guide 部署載入（Claude 端另有 `~/.claude/rules/` symlink auto-load）

## single-source drift 防護（修改紀律）

改「定義源」（review-engine 共通邏輯 / 跨命令引用的 rule / 模式判定表——**含 code 定義源**）時，**強制 `rg "<單一關鍵詞>"` 掃所有引用該定義的命令/skill，逐檔同步**——否則「定義改了，引用沒跟」（drift regression）。細節（rg alternation 陷阱、案例、sync-sources 的 invariant 登記）見 instruction-writing skill「文檔自洽五維檢查」。

## 撰寫/修改 instruction 檔約束（pointer）

- **元資訊禁止**（❌ 行為表、執行約束、自檢清單）與 **文檔自洽五維檢查**：見 instruction-writing skill（on-demand）——撰寫或修改任何 instruction 檔時載入
