# UC-5：單一 MCP 接口（code-reality 薄殼）

[tag:code-reality] [mcp]

## 目標
FastMCP HTTP 薄殼（:8200）＋launchd 常駐＋ZCode user-level 掛接——LLM 單一接口完成 refs/callers/closure/audit，每回應帶 [SRC]。工具呼叫＝subprocess spawn（保鮮免 kickstart）。

## 相關
- EP 段 3：`ai-analysis/execution-plans/ep-code-reality-repo-mcp.md`
- 套路前例：`com.user.crg-mcp.plist`（launchd）、lsp-python entry（ZCode user-level http）
- v1 擴面：impact/communities/hub（S6 圖層後）

## 驗收標準
- 四工具可用：refs/callers/closure/audit（repo_root 必填，缺→loud error 帶修正指引）
- [SRC] 逐字透傳＋exit codes 不偽裝＋stderr WARN 以 [STDERR] 段可見
- freshness probe：工作樹改碼→下一呼叫反映（SM-10）
- 新 session 見 `mcp__code-reality__*` 工具

## 備註
v0 工具面＝SCIP 家族四工具；snapshot/transition/hub_refs/tour 維持 CLI（YAGNI）。Claude 端掛接 optional。不做 repo-root hook（server 端自己 loud）

> 2026-08-26 註記：ownership＝code-reality repo Rust 軌（ai-rules 側無動作）；R4 graph family EP 之後評估 MCP 形態。卡留作跨 repo 可見度——屆時若由 Rust 統一介面交付，收案比照 caller-edges 卡。
