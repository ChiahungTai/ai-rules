# Upgrade Flow — 套件升級共同骨架（upgrade-nt / upgrade-sj 共用）

> 佔位符：`<REPO>`（GitHub repo）、`<PACKAGE>`（Python 套件名）、`<SPEC>`（pyproject 相依 spec）、`<IMPORT_CHECK>`（升級後 import 驗證語句）、`<NAME>`（語音通知用簡稱）、`<VERSION>`（目標版號）、`<TARGET_VERSION>`（pyproject 下限版號）。各 skill 定義自己的掃描項目表（與風險區域，如有），流程骨架一律引用本檔。

## 前置條件（共用）

**必須在收盤後執行**（15:30 以後）。理由：

1. 升級後需跑 `tests/external_api/sj/` 完整外部 API 測試
2. 盤中執行會消耗 SJ quota（每日重置 ~08:00）並干擾即時交易連線

## Phase: 版本差距分析

```bash
# 當前版本
uv run python -c "import <PACKAGE>; print(<PACKAGE>.__version__)"
# 最新 release
gh api repos/<REPO>/releases/latest --jq '.tag_name, .published_at, .name'
# 指定版本 / release notes
gh api repos/<REPO>/releases/tags/v<VERSION> --jq '.tag_name, .published_at'
gh api repos/<REPO>/releases/tags/v<VERSION> --jq '.body'
```

產出版本差距報告（表格）：當前 → 目標、中間跳過版本數、breaking changes 列表。

## Phase: Breaking Changes 影響掃描（方法論）

先用 LSP `workspaceSymbol` 搜尋 release notes 提到的 API 名稱，確認專案是否使用；再用 rg 做完整文字搜尋。掃描項目表由各 skill 自帶（套件特定）。

**掃描結果分級**：

| 分級 | 定義 | 行動 |
|------|------|------|
| 🔴 直接命中 | 專案程式碼使用了被移除/改名的 API | 必須修改後才能升級 |
| 🟡 間接影響 | 使用的 API 行為改變 | 需評估，通常不需改 |
| 🟢 無影響 | 專案未使用受影響的 API | 可安全升級 |

## Phase: 執行升級（雙 worktree）

1. **更新 `pyproject.toml` 下限**（兩個 worktree 都要）：
   - `mosaic_alpha_offline_backtesting/pyproject.toml`
   - `mosaic_alpha/pyproject.toml`
   - 格式：`"<SPEC>>=<TARGET_VERSION>"`
2. **驗證 TOML 合法**：
   ```bash
   uv run python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb')); print('OK')"
   ```
3. **同步依賴**：兩個 worktree 各跑 `uv sync`
4. **確認兩邊版本一致**：重跑版本查詢指令

## Phase: 驗證（漸進式：DEPTH-MIN → DEPTH-SAMPLE → DEPTH-FULL）

遵循專案漸進式驗證策略：

```bash
# DEPTH-MIN（秒級）：import + <IMPORT_CHECK>
uv run python -c "<IMPORT_CHECK>"

# DEPTH-SAMPLE（分鐘級）：內部測試，排除外部 API
uv run pytest tests/ -x -q --timeout=60 -k "not external_api"

# DEPTH-FULL（完整驗證，收盤後執行）：SJ 外部 API
uv run pytest tests/external_api/sj/ -x -q
```

## Phase: Commit

```
chore(deps): upgrade <SPEC> >=X.Y.Z

- Breaking changes impact scan: [結果摘要]
- Internal tests: [PASS/FAIL]
- External API tests: [PASS/PENDING]
```

## 輸出報告骨架

```
## <NAME> 升級報告

**版本變更**: 當前 → 目標
**升級風險**: 🟢 低 / 🟡 中 / 🔴 高

### Breaking Changes 影響掃描
| 掃描項目 | 命中 | 分級 | 說明 |
|---------|------|------|------|

### 驗證結果
| 階段 | 結果 |
|------|------|
| DEPTH-MIN | ✅/❌ |
| DEPTH-SAMPLE | ✅/❌/⏳ 待收盤 |
| DEPTH-FULL (SJ external) | ⏳ 待收盤 / ✅/❌ |

### 跨 Worktree 一致性
| Worktree | 版本 |
|----------|------|
```

## 語音通知

遵循 [voice-notification skill](../voice-notification/SKILL.md)（隨機稱謂、sentinel 進度提醒、say 樣板見 skill）：

- **開始**（第一個動作前）：建進度提醒 sentinel + say 開始
  ```bash
  touch /tmp/.claude-voice-pending
  say -v Meijia -r 180 "開始升級 <NAME>"
  ```
- **完成**（輸出結果後）：清 sentinel + 套 skill「任務完成」樣板 say（隨機稱謂，填「<NAME> 升級完成」）
  ```bash
  rm -f /tmp/.claude-voice-pending
  ```

## 共用約束

- 收盤後才能跑完整驗證（SJ external API 測試需收盤後 15:30+）
- 兩個 worktree 都要更新
- `pyproject.toml` 下限反映實際最低相容版本，非歷史安裝版本
