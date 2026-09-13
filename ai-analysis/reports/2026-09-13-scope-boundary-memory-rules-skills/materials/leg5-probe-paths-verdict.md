# 腿 5（probe）：CC user-level `paths:` 條件載入——L4 實證判決

> 產出者：spec-miner（glm-5.3-flash），2026-09-13。隔離實驗（CLAUDE_CONFIG_DIR 重定位）＋對照組設計。完整原始輸出在 agent output；本檔為判決摘要（materials 用）。

## 判決

**成立**（Claude Code 2.1.263）。有 `paths:` 的 user-level rule 不在 session start 載入；Claude 以 **Read tool 讀到 glob 匹配檔**後，以 attachment（`nested_memory`）lazy 注入——`load_reason:"path_glob_match"`、`memory_type:"User"`。

## 證據鏈

- **實驗組**（Read `target.probe-py`）：`loaded-exp2.jsonl` 有 probe-scoped.md 事件（`globs:["**/*.probe-py"]`、`trigger_file_path` 記錄觸發檔）；transcript 有 MARKER 命中（attachment 注入內容）
- **對照組**（Read `target.probe-md`）：probe-scoped.md **零事件**（rg 無命中）；僅 always rule＋CLAUDE.md 以 `session_start` 載入
- **無效實驗自曝**：第一輪實驗組模型未呼叫 tool（幻覺答案），該輪不具證據力，已棄用
- **binary 佐證**：launch 掃描鏈 `conditionalRule:!1`（eager 掃描模式）＋ lazy 路徑 `conditionalRule:!0`——兩者串接，非能力缺席（推翻腿 1 unverified 的悲觀解讀）

## 機制細節

- 載入時點＝Read tool 回傳後、下一個 model turn 前（attachment 注入，非同步、非 session start）
- 觸發條件＝Read tool 實際讀取匹配檔（與官方 memory.md:220 一致）
- 匹配語義＝glob 對被讀檔路徑（絕對 vs cwd-relative 匹配未設對照，不過度宣稱）

## 附帶發現

1. **CLAUDE_CONFIG_DIR 重定位失 auth 根因**：live 認證在 `~/.claude/settings.json` 的 `.env`（`ANTHROPIC_AUTH_TOKEN`＋`ANTHROPIC_BASE_URL`=api.z.ai）非 Keychain；Keychain `Claude Code-credentials` accessToken 已過期（2026-03-02）＝殘留。
2. 異常觀察（unexplained）：config-dir 重定位下 `~/.claude/CLAUDE.md` 被載入且標 `memory_type:"Project"`——scope 歸屬偏差，真實部署不受影響。

## 紀律舉證

- `~/.claude/` 唯讀不變（`find -newermt 2026-09-13 08:00` 零命中）；實驗產物全在 `.agent-tmp/scope-research/cc-probe/`；secret 未落盤未印出。
