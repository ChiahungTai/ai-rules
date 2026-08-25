# docs mode 適配：2a 語義反向撈 + code-review 軸裁剪

docs mode 適配真實缺口只有兩件小事（非系統性盤點）：

1. **2a ripple 語義反向撈**（`execution-plan` docs mode 段）：涉及格式/術語統一類變更，ripple 補 `rg "共用規範|與.*共用"`。dry-run 證實會**漏改**（真實錯誤）。
2. **code-review 軸裁剪**：docs mode（純文檔）跳過 Security/Performance 軸（N/A），避免文檔審查噪音。

**為何不系統化**（flow-review 2026-06-17 否決）：沒適配的損害多是「浪費/噪音」非「錯誤」——audit-test 自然跳過、commit 已隱式通過、ep-review 已有文檔維度。為「浪費幾句廢話」搞 UC matrix + 共用 skill + UC 數字標記 = over-engineering。原則：**先問「損害是錯誤還是浪費」再決定要不要設計**。

**來源**：flow-feedback `docs-mode-ep-ripple-gaps`（2a）+ `review-commit-workflow-mismatch` 觀察點 3（code-review）
