---
harness-scope: neutral
---

# 搜尋工具分工

> **載入機制**: 本檔 source 在 ai-rules repo `rules/`；各家 harness 經全域 guide 部署載入（Claude 端另有 `~/.claude/rules/` symlink auto-load）

---

## 核心原則

**符號/圖譜查詢用 code-reality（index 在場；型別面〔hover/diagnostics〕雙語言用 code-reality-lsp-bridge——.py/.rs 副檔路由），文字搜尋用 rg，檔案搜尋用 fd。** `fd`/`rg` 預設遵守 `.gitignore`（減少噪音）。詳細 LSP×rg/fd 工具對照速查見 [lsp-navigation.md](lsp-navigation.md)。

(Claude: `find -exec`、`grep -r` 是 Claude Code 系統層級硬限制；`fd`/`rg` 預設可 auto-allow。其他 harness 無此限制，fd/rg 語法優勢通用)

---

## fd/rg 陷阱（基礎語法是原生知識，此處只列會誤導的）

- **fd pattern 匹配檔名不是路徑**：搜尋特定目錄用 `fd . <dir>`；`fd src/` 是搜尋檔名含 `src/` 的檔案非搜尋 src/ 目錄
- **隱藏檔/gitignored 檔陷阱**：fd/rg 預設跳過 dotfiles 與 ignore 檔，**旗標跨工具不同義**——fd：`-H` hidden、`-u` 全解；rg：`--hidden`/`--no-ignore`（`-H` 是 with-filename 非 hidden）；dot+ignore 疊加態（如 `.code-review-graph/` 自帶 `*` ignore）兩旗標併用（NT graph.db 1.4G 誤判不存在實案）
- **rg alternation 陷阱**：`rg "a\|b"` 搜尋 literal `a|b`，**不是**「a 或 b」。多選一用 `rg "a|b"`（雙引號內 `|` 直傳 rg）或 `rg -e a -e b`（markdown 表格 cell 內一律用 `-e` 多 pattern，避開 `\|` 轉義歧義）
- **固定字串用 `-F`**（預設走正則）；**glob `-g` 比 `--type` 靈活**（`--type py` 不含 `.pyx`/`.rs`）
- **多檔搜尋加 `--heading`**：檔名只印一次（預設每行重複完整路徑）；路徑已知時直接指定檔案不遞迴
- **grep 旗標不可遷移到 rg**：grep `-h`（抑制檔名）rg 是 help——免檔名用 `-I`；`-r` grep=遞迴、rg=--replace（複合旗標 `-rn` 拆開讀，`-r` 會替換 match 污染輸出）。真實案例：`rg -h pattern` 印整份 help、`rg -rn pattern` match 全成 "n"（grep 慣性遷移）
- **rg `-g` glob 錨定路徑 arg 形態**：`-g '!dir/**'` 對絕對路徑 root arg 靜默失效——要生效用 cwd＋arg `.` 或 `!**/dir/**`（hazard runner 實案：mock 全繞過、真 rg 測試才抓到）

---

## 統計/計數用途禁用 head 截斷

> **核心原則**：rg「展示用途」（看有哪些檔）與「統計用途」（得數字寫進文檔/claim）命令不同。統計用途禁 `| head -N` 截斷後人工數。

| 用途 | 命令 |
|------|------|
| 展示（看範例） | `rg -l "pattern" \| head -N` |
| **統計:檔案數**（寫進文檔/claim） | `rg -l "pattern" \| wc -l`（**禁 head 截斷**） |
| 統計:per-file match 數 | `rg -c "pattern"`（輸出 `file:count` 多行，語境不同於檔案數） |

**真實案例**：`rg -l "from <pkg>" | head -20` 截斷 → consumers **41 誤寫 20**（head 只列前段），多處文檔寫錯，**自審抓不到**（claim 與截斷證據共享盲點，需獨立第三方 rg 才揭露）。同類陷阱不同載體：符號查詢的 truncation/masking 見 [lsp-navigation.md](lsp-navigation.md)。

---

## 盤點執行點：間接層與直呼層雙掃

盤點執行點雙掃（間接層 make target/wrapper 引用＋直呼層 raw command——CI 跑哪些測試、哪些入口呼叫某工具、cutover 影響域的完整性盤點）見 acceptance-evidence skill「盤點執行點雙掃」章。
