# [tag:rules,skills] memory 生命周期治理 hardening EP

## 目標
吸收 arch-thinking 審查修正：generator 併發安全（unique tmp）＋雙單位 gate（chars+bytes）、config 回滾路徑文件化、zcode live parity invariant（F8 形狀防線）、memory-audit 層 3 邊界掃描、部署收尾（deploy＋check_single_source＋兩池冪等）。

## 相關
- EP：`ai-analysis/execution-plans/ep-memory-lifecycle-hardening.md`
- 主任務（同 working tree）：generator 資產化＋雙 hook＋三處接線＋rule「Memory 生命周期規範」

## 驗收標準
- pytest tests/ 全綠（含併發 smoke／byte-gate／parity 三態新測試）
- check_single_source 全綠（含新 zcode_live_parity）
- deploy 三端 byte-identical＋rg spot check 含新 rule 段落
- 兩池 `_generate_index.py --check` 過＋資產/部署副本三方 cmp identical

## 備註
新 session live 驗證（gate 擋寫＋Stop regen＋stderr 回饋）為 deferred 驗收——config snapshot 語義本 session 無法執行；失敗回滾按 `hooks/memory-hooks-rollback.md`。
