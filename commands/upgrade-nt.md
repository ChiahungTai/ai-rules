---
description: "升級 NautilusTrader 版本，含 breaking changes 影響掃描與跨 worktree 一致性驗證"
when_to_use: "升級 NautilusTrader 時使用。必須在收盤後執行（需跑 SJ external API 測試）。觸發詞：升級 NT、update nautilus、NT 升級。"
usage: "/upgrade-nt [目標版本]"
argument-hint: "預設升級到最新 release，可指定版本如 1.228.0"
allowed-tools: ["Bash", "Read", "Edit", "Grep", "WebSearch"]
---

# Upgrade NT — NautilusTrader 升級流程

NautilusTrader 升級指揮官。負責版本差距分析、breaking changes 影響掃描、跨 worktree 一致性驗證。

## 🔴 前置條件

**必須在收盤後執行**（15:30 以後）。升級後需要跑 `tests/external_api/sj/` 完整外部 API 測試，盤中執行會干擾 SJ quota 和即時交易。

## 🚀 執行流程

### Phase 1: 版本差距分析

1. **取得當前版本**：
   ```bash
   uv run python -c "import nautilus_trader; print(nautilus_trader.__version__)"
   ```

2. **取得最新 release**：
   ```bash
   gh api repos/nautechsystems/nautilus_trader/releases/latest --jq '.tag_name, .published_at, .name'
   ```
   如果使用者指定版本，改查該版本：
   ```bash
   gh api repos/nautechsystems/nautilus_trader/releases/tags/v<VERSION> --jq '.tag_name, .published_at'
   ```

3. **取得 release notes**：
   ```bash
   gh api repos/nautechsystems/nautilus_trader/releases/tags/v<VERSION> --jq '.body'
   ```

4. **產出版本差距報告**（表格格式）：
   - 當前版本 → 目標版本
   - 中間跳過的版本數
   - Breaking changes 列表

### Phase 2: Breaking Changes 影響掃描

逐一掃描 breaking changes 對專案的影響。掃描項目（按常見 breaking changes 分類）：

> **使用方式**：表格中的搜尋指令是掃描模式範本。第一列「API 改名/移除」的 `"舊名"` 是佔位符，執行時需根據 release notes 中的具體 breaking changes 替換為實際 API 名稱。其餘列為通用掃描，可直接執行。

| 掃描項目 | 搜尋指令 | 關注對象 |
|---------|---------|---------|
| API 改名/移除 | `rg "<release_notes中的舊名>" mosaic_alpha/ --type py` | 參數名、方法名、類別名 |
| order 相關改動 | `rg "order_factory\|submit_order\|cancel_order\|modify_order" mosaic_alpha/ --type py` | 策略中的訂單操作 |
| Config 改動 | `rg "Config\|EngineConfig" mosaic_alpha/ --type py` | 配置中的參數名變更 |
| OMS 改動 | `rg "OMS\|NETTING\|HEDGING\|position_id" mosaic_alpha/ --type py` | 倉位管理模式 |
| 傳輸層改動 | `rg "TransportBackend\|Tungstenite\|Sockudo" mosaic_alpha/` | WebSocket 傳輸 |
| Log 改動 | `rg "LoggerConfig\|from_spec\|\.json\b" mosaic_alpha/ --type py` | 日誌配置 |
| Arrow 改動 | `rg "arrow\|Arrow\|pyarrow" mosaic_alpha/ --type py` | 序列化相關 |

**掃描結果分級**：

| 分級 | 定義 | 行動 |
|------|------|------|
| 🔴 直接命中 | 專案程式碼使用了被移除/改名的 API | 必須修改後才能升級 |
| 🟡 間接影響 | 使用的 API 行為改變（如 panic → ValueError） | 需評估，通常不需改 |
| 🟢 無影響 | 專案未使用受影響的 API | 可安全升級 |

### Phase 3: 執行升級

1. **更新 `pyproject.toml` 下限**（兩個 worktree 都要更新）：
   - `mosaic_alpha_offline_backtesting/pyproject.toml`
   - `mosaic_alpha/pyproject.toml`
   - 格式：`"nautilus-trader>=<TARGET_VERSION>"`

2. **驗證 TOML 合法**：
   ```bash
   uv run python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb')); print('OK')"
   ```

3. **同步兩個 worktree 的依賴**：
   ```bash
   uv sync
   ```
   在兩個 worktree 都要執行。

4. **確認兩邊版本一致**：
   ```bash
   uv run python -c "import nautilus_trader; print(nautilus_trader.__version__)"
   ```

### Phase 4: 驗證（漸進式）

遵循專案的漸進式驗證策略（QUICK → REPRESENTATIVE → ALL）：

**QUICK（秒級）**：
```bash
uv run python -c "import nautilus_trader; print(nautilus_trader.__version__)"
uv run python -c "from nautilus_trader.config import BacktestEngineConfig; print('NT import OK')"
```

**REPRESENTATIVE（分鐘級）**：
```bash
uv run pytest tests/ -x -q --timeout=60 -k "not external_api"
```
跑內部測試，排除外部 API 測試（需收盤後才跑）。

**ALL（完整驗證，收盤後執行）**：
```bash
uv run pytest tests/external_api/sj/ -x -q
```
SJ 外部 API 完整測試，驗證 NT 升級不影響 Shioaji 整合。

### Phase 5: Commit

提交 `pyproject.toml` 變更，commit message 格式：

```
chore(deps): upgrade nautilus-trader >=X.Y.Z

- Breaking changes impact scan: [結果摘要]
- Internal tests: [PASS/FAIL]
- External API tests: [PASS/PENDING]
```

## 📋 輸出格式

```
## NT 升級報告

**版本變更**: 當前 → 目標
**升級風險**: 🟢 低 / 🟡 中 / 🔴 高

### Breaking Changes 影響掃描
| 掃描項目 | 命中 | 分級 | 說明 |
|---------|------|------|------|

### 驗證結果
| 階段 | 結果 |
|------|------|
| QUICK | ✅/❌ |
| REPRESENTATIVE | ✅/❌/⏳ 待收盤 |
| ALL (SJ external) | ⏳ 待收盤 / ✅/❌ |

### 跨 Worktree 一致性
| Worktree | 版本 |
|----------|------|
```

## 🔧 約束

- **收盤後才能跑完整驗證**：SJ external API 測試需收盤後（15:30+）
- **兩個 worktree 都要更新**：`mosaic_alpha/` 和 `mosaic_alpha_offline_backtesting/`
- **pyproject.toml 下限反映實際最低相容版本**：不只反映歷史安裝版本
