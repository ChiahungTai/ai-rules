# Claude／Codex VSCode Extension 用法（仿造標的）

日期 2026-09-11。立場：**ext 的用法就是 ground truth——仿造它大概率不會錯**。本報告主體是 ext 側實測行為（同 repo 接手可直接讀檔驗證；版本均為本機實測），bridge 設計意見只在末段衍生。

## Codex extension 實際用法（`openai.chatgpt-26.908`）

- **進程模型**：spawn 自帶 `bin/macos-aarch64/codex`（0.154.0-alpha.6.1），argv `-c features.code_mode_host=true app-server`，stdout JSONL 解析。常駐單一 App Server process，多 threads 共用一條 Code Mode host connection；另有 `codex-code-mode-host` helper（gRPC/stdio strings 取證）。
- **thread 操作面**（`out/extension.js` 方法名字典）：`thread/start・started・list・fork・inject_items・deleted・unsubscribe・unarchived・unarchive・stop・reverted・resume`；`turn/start・completed・steer・started・interrupt`。
- **turn 起手參數**：`cwd`（可 null）、`approvalPolicy`、`permissions`（見過 `":read-only"`）、`runtimeWorkspaceRoots`、`model`／`reasoning_effort`、`serviceTier`。
- **thread 生命周期**：start→steer→interrupt/stop→archive；平行工作走 `fork`；`inject_items` 插物料；`list` 預設 `sourceKinds=[cli, vscode]` 雙面同庫。
- **binary 選擇**：`chatgpt.cliExecutable` 有值就用，否則自帶 binary（`package.json:114-115`）。

## Claude extension 實際用法（`anthropic.claude-code-2.1.267`）

- **進程模型**：spawn 自帶 `resources/native-binary/claude`（2.1.267，existsSync 回退），CLI 子行程＋雙向 stream-json（stdin `input-format` in／stdout `output-format` out）。無 ACP、無常駐 server。
- **起手參數**：`--session-id=` 定錨、`--resume-session-at=` 續點、`--session-mirror` 鏡像、`--add-dir` 加目錄；`permissionMode`／`allowDangerouslySkipPermissions`／`sessionKey` 直通 CLI（passthrough，非 extension 自判）。
- **會話本體**：`~/.claude/projects/<project>/<session-id>.jsonl`；resume 跨專案搜尋（v2.1.223 起）。
- **override 口**：無（package.json 無對應設定；兩端版本各自前進）。

## TL;DR 對照

| 面 | Codex（openai.chatgpt） | Claude（anthropic.claude-code） |
|---|---|---|
| extension 調用形態 | spawn 自帶 binary 跑 **App Server**（JSON-RPC over stdio，stdout JSONL） | spawn 自帶 binary 跑 **CLI 子行程**（`--input-format stream-json` stdin in、`--output-format stream-json --verbose` stdout out） |
| 關鍵證據 | `out/extension.js`：`Spawning codex app-server`，argv `-c features.code_mode_host=true app-server` | `extension.js`：argv 含 `--output-format stream-json --verbose --input-format stream-json`、`--session-id=`、`--resume-session-at=`、`--session-mirror`、`--add-dir` |
| 自帶 binary | `bin/macos-aarch64/codex`＝0.154.0-alpha.6.1（另有 `codex-code-mode-host` helper） | `resources/native-binary/claude`＝2.1.267（existsSync 回退邏輯） |
| 用戶 PATH 版 | 0.153.4（較舊） | 2.1.263（較舊） |
| override 口 | 有：`chatgpt.cliExecutable`（`package.json:114-115`） | 無（package.json 無對應設定） |
| 會話本體 | `~/.codex/sessions/` rollout JSONL（globalState 只存 UI metadata／pinning） | `~/.claude/projects/<project>/<session-id>.jsonl`（官方 sessions.md:222） |
| 跨面接續 key | `thread.sessionId`（≠`thread.id`，app-server.md:533-536 明確警告） | `session-id`（`claude --resume <id>` 跨專案搜尋，sessions.md:27） |
| Auth／計費 | 共用 `~/.codex/auth.json`（ChatGPT 登入）；同訂閱額度（pricing.md:327-328）；翻 API 計費只兩種（改共享登入／單次 `CODEX_API_KEY`） | 同產品 OAuth 登入流（extension 內無獨立 credential store；`oauth/authorize`＋`claude_cli` key 流程）；同訂閱 |
| 版本差風險 | 有（schema／defaults／methods 可能漂） | 有（同理；另 extension 無 override 口，兩端版本各自前進） |

## Codex 各種用法（本機＋官方文件已驗）

1. **`codex exec "…"（one-shot）**：bridge 日常派工形態。`--json` 結構輸出；配額走 ChatGPT 訂閱（本機 `auth_mode=chatgpt`）。
2. **`codex exec resume <SESSION_ID>`**：接續 persisted session。用 `thread.sessionId`，**不是** App Server `thread.id`（過去兩者多為同 UUID 是 coincidence，不可固化）。
3. **App Server 生命周期**：`thread/list`（`sourceKinds=["cli","vscode"]` 預設雙面同庫，app-server.md:688-689）→ `thread/read` → `thread/resume`（用 `thread.id`）→ `thread/fork`（平行工作用 fork 語義，別雙寫同卷——同時 resume 同卷的 lock contract UNVERIFIED）。
4. **`code_mode_host`**：Code Mode execution host infrastructure（模型在其中跑 JS 再發 nested tool calls），≠`code_mode` feature；plain app-server 預設已 true，extension 顯式 `-c` 是鎖死。
5. **計費邊界**：auth／provider／model routing，不是 app-server vs exec（codex 討論 job-mtwg0cvj 全文）。
6. **版本釘選**：bridge 派工固定 `--model chatgpt-web/high`（與 `~/.codex/config.toml:5` 預設一致，實測）。

## Claude 各種用法（本機＋官方鏡像已驗）

1. **interactive（終端／IDE 內）**：`claude`，session 進 picker；`--continue`、`--resume <id|name>`、`--fork-session`、`--add-dir`。
2. **headless（`-p`）**：`claude -p "…" --output-format json|stream-json` 取結構結果（含 session ID、usage、cost 估計）；`claude -p --resume <id>` 追問既有 session（sessions.md:209-217）。
3. **extension 內部**：同上 CLI 子行程＋雙向 stream-json；`--session-id` 定錨同 store、`--resume-session-at` 續點、`--session-mirror` 鏡像。
4. **resume 互通（構造確認，未做 live 跨面實驗）**：同 binary 家族＋同 store＋`--session-id` 定錨 ⇒ extension thread 可用 CLI `claude --resume` 接（跨專案搜尋會找到）；反之同理。live roundtrip 未測，標 capped。
5. **bridge 姿勢**：一律走 CLI（`exec`／`-p`／`--resume`），不碰 extension 內部行程；記 `session_id` 單一 key（Claude 無雙 identity 問題）；平行工作用 `--fork-session`。

## Bridge 仿造衍生（意見段，非實測）

仿造原則：調用形態照抄 ext（codex 學 App Server 常駐＋thread 操作面；claude 學 CLI 子行程＋stream-json 雙向）；identity 與版本策略照抄 ext 的選擇（codex 雙 key＋`cliExecutable` 釘版口；claude 單 key 無口）。以下四條由此直接導出：

- **調用面統一，identity 面分家**：兩家都是「自帶 binary＋共享 store」，bridge 只需會兩套調用（codex：`exec`／App Server；claude：CLI＋stream-json），identity 規則各記各的（codex 雙 key `app_server_thread_id`＋`codex_session_id`；claude 單 key `session_id`）。
- **接續一律用跨面 key**：codex 用 `sessionId`（禁拿 `thread.id` 跨面）；claude 用 `session-id`。fork 語義做平行，禁雙寫同卷（兩家 lock contract 皆 UNVERIFIED）。
- **版本差當一等風險**：兩家 extension 都比用戶 CLI 新（codex .154a6.1 vs .153.4；claude 2.1.267 vs 2.1.263）且各自前進；codex 有 `cliExecutable` 可釘，claude 無——bridge 側對 codex 可考慮跟隨釘版，claude 側只能接受漂移並在 vermismatch 時回報。
- **計費觀測**：兩家同訂閱額度內不分池；`CODEX_API_KEY` 單次注入（codex）是唯一的靜默翻轉點，bridge 應剝除或顯式標記（delegate-bridge 現行已剝，維持）。

## 取證清單與未驗項

- 取證：codex extension `out/extension.js`（spawn 行）、`bin/macos-aarch64/codex --version`、globalState UUID→`~/.codex/sessions/` 對應×2、claude `extension.js`（argv／native-binary／OAuth 流）、`~/.claude/projects/` 目錄、官方鏡像 `ref-docs/harness/{codex/app-server.md,claude-code/docs/en/{sessions,headless}.md}`、codex 討論 `job-mtwg0cvj-6u0bwg`（completed）。
- 未驗：Claude 跨面 live resume roundtrip（唯讀限制未做）；codex 雙寫同卷 lock 行為；`codex-code-mode-host` spawn argv／IPC 細節（無 source-level 證據不腦補）。
- 方法註：Context7 skill 已載但本 harness 無 MCP face，改用 repo 官方鏡像＋本機實檔取證替代。
