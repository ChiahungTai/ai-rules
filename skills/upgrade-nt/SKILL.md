---
name: upgrade-nt

description: "升級 NautilusTrader 版本，含 breaking changes 影響掃描與跨 worktree 一致性驗證"
when_to_use: "升級 NautilusTrader 時使用。必須在收盤後執行（需跑 SJ external API 測試）。觸發詞：升級 NT、update nautilus、NT 升級。"
argument-hint: "預設升級到最新 release，可指定版本如 1.228.0"
allowed-tools: ["Bash", "Read", "Edit", "Grep", "WebSearch"]
---

# Upgrade NT — NautilusTrader 升級流程

NautilusTrader 升級指揮官。版本差距分析、掃描分級、雙 worktree 升級、DEPTH 驗證、commit、語音通知的**流程骨架見 [upgrade-flow.md](../_common/upgrade-flow.md)**（佔位符代入：`<REPO>`=nautechsystems/nautilus_trader、`<PACKAGE>`=nautilus_trader、`<SPEC>`=nautilus-trader、`<NAME>`=NT）；本檔只承載 NT 專屬內容。

NT 佔位符代入值：

- `<IMPORT_CHECK>`：`from nautilus_trader.config import BacktestEngineConfig; print('NT import OK')`

## NT 專屬掃描項目（Phase: 影響掃描）

> 表中搜尋指令是掃描模式範本。「API 改名/移除」列的 `"舊名"` 是佔位符，依 release notes 的具體 breaking changes 替換；其餘列可直接執行。

| 掃描項目 | 搜尋指令 | 關注對象 |
|---------|---------|---------|
| API 改名/移除 | `rg "<release_notes中的舊名>" mosaic_alpha/ --type py` | 參數名、方法名、類別名 |
| order 相關改動 | `rg "order_factory\|submit_order\|cancel_order\|modify_order" mosaic_alpha/ --type py` | 策略中的訂單操作 |
| Config 改動 | `rg "Config\|EngineConfig" mosaic_alpha/ --type py` | 配置中的參數名變更 |
| OMS 改動 | `rg "OMS\|NETTING\|HEDGING\|position_id" mosaic_alpha/ --type py` | 倉位管理模式 |
| 傳輸層改動 | `rg "TransportBackend\|Tungstenite\|Sockudo" mosaic_alpha/` | WebSocket 傳輸 |
| Log 改動 | `rg "LoggerConfig\|from_spec\|\.json\b" mosaic_alpha/ --type py` | 日誌配置 |
| Arrow 改動 | `rg "arrow\|Arrow\|pyarrow" mosaic_alpha/ --type py` | 序列化相關 |

## NT 專屬：Sync Stubs（升級後、commit 前）

**LSP stub 重新同步**（`uv sync` 會清除 venv 內的 `.pyi`）：
```bash
bash scripts/sync_nt_stubs.sh
```

**檢查 API 變更是否影響 stub**：
- NT 改了 `Bar`、`Price`、`Quantity` 等 class 的公開 API → 更新 `stubs/nautilus_trader/` 對應 `.pyi` 後重新 sync
- 模組路徑重組 → 更新 `stubs/` 目錄結構 + `pyrightconfig.json`

提交 `pyproject.toml` + stub 變更（commit 範本見 upgrade-flow）。

## 輸出報告

依 [upgrade-flow.md](../_common/upgrade-flow.md) 骨架，抬頭「NT 升級報告」。

## 約束

共用約束見 upgrade-flow。NT 無額外約束。
