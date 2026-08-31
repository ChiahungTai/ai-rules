# [tag:hooks] CRG hook 死碼清理＋matcher no-op 修復

## 目標
memory audit（2026-08-31）發現的兩個 repo 側殘留：①`hooks/require-crg-repo-root.py`＋`hooks/zcode-registration.json:28` 註冊在 CRG 08-30 全清後成死碼；②live ZCode config 的 PreToolUse matcher `mcp__code-review-graph__` 對現行 CR plugin 工具名（`mcp__plugin_code-reality_code-reality__*`）substring 不命中＝靜默 no-op。

## 相關
- memory：`project_crg-shared-server`（弧全記錄＋殘留發現）
- 先例：zcode-hooks-porting 記的 matcher 靜默失效陷阱

## 驗收標準
- 決策：hook 刪除（CRG 已亡、repo_root 防護隨之無對象）或改 matcher 指向 CR plugin 工具名（若 repo_root 防護對 CR graph 查詢仍有價值——查 cr-query skill 是否需要）
- live config `~/.zcode/cli/config.json` 的 matcher 同步清理
- 刪除前 rg 全 repo 引用（hooks/AGENTS.md、zcode-registration、測試）

## 備註
另一個順手項：settings.json sandbox disabled 下的 dead config（autoAllowBashIfSandboxed/filesystem）清理——feedback_no-sandbox-layer 條目早建議過。
