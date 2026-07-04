---
harness-scope: claude-specific
---

# 搜尋工具分工

> **載入機制**: source `~/Github/ai-rules/rules/`；Claude 端 `~/.claude/rules/` symlink auto-load；其他 harness 靠全域 guide on-demand 讀

---

## 核心原則

**語義查詢用 LSP，文字搜尋用 rg，檔案搜尋用 fd。**

- LSP：符號定義、引用、型別、呼叫鏈（~50ms，100% 準確）
- rg：註解、字串、config、文件內容（文字匹配）
- fd：檔案/目錄名稱搜尋

詳細 LSP 決策樹見 `@~/Github/ai-rules/rules/lsp-navigation.md`

---

## Why

- `find -exec`、`grep -r` 是 Claude Code 系統層級的硬限制，**無法被任何 allow 規則覆蓋**，每次都需手動批准
- `fd` / `rg` 語法更簡潔，預設可被 auto-allow
- `rg` 預設排除 `.gitignore` 中的檔案，減少噪音

---

## fd 常用語法

```
fd <pattern>              # 搜尋檔名（當前目錄遞迴）
fd -e py                  # 搜尋所有 .py 檔案
fd -e py . src/           # 搜尋 src/ 下的 .py 檔案
fd "test_" -e py          # 搜尋 test_ 開頭的 .py
fd -t d                   # 只搜尋目錄
fd -t f                   # 只搜尋檔案（預設）
fd -e py -x wc -l         # 對每個結果執行指令
fd -E test -E vendor      # 排除 test/ 和 vendor/
fd --max-depth 3          # 限制深度
```

- `fd <pattern> <path>` 中 pattern 匹配**檔名**，不是路徑
- 搜尋特定目錄：`fd . <dir>`（`.` 表示匹配所有檔名，第二個參數是路徑）
- **常見錯誤**：`fd src/` 是搜尋檔名包含 `src/` 的檔案，不是搜尋 src/ 目錄
- **隱藏檔陷阱**：`fd` 預設跳過 dotfiles（`.` 開頭）與 `.gitignore` 內檔案。查 `.project-snapshot.json`、`.gitignore`、`.env`、`.claude/` 等必須加 `-H`（`fd -H "project-snapshot"`），否則 false negative 誤判「不存在」。`rg` 同理用 `--hidden` 或 `-uu`

---

## rg 常用語法

```
rg "pattern"              # 遞迴搜尋（當前目錄）
rg "pattern" src/         # 限定搜尋 src/ 目錄
rg "pattern" file.py      # 搜尋單一檔案（路徑已知時直接指定）
rg -t py "pattern"        # 只搜 .py 檔案
rg -g "*.pyx" "pattern"   # glob 搜尋（--type py 不含 .pyx/.rs）
rg -g "!test*" "pattern"  # 排除匹配 test* 的檔案
rg -l "pattern"           # 只印檔名
rg -F "exact string"      # 固定字串（不走正則）
rg --no-filename "pat"    # 不印檔名（用於提取內容）
rg -o -r '$1' "(\w+)\.py" # 捕獲群組替換輸出（$1 是 rg 語法，非 shell expansion）
```

- **alternation 陷阱**：`rg "a\|b"` 搜尋的是 literal `a|b`（`\|` 是 regex literal pipe），**不是**「a 或 b」。多選一用 `rg "a|b"`（雙引號內 `|` 不被 shell 當 pipe，直傳 rg 作 alternation）或 `rg -e a -e b`
- **gitignored 檔盲點**（如 `settings.json`）：rg/fd 預設跳過 `.gitignore` 內檔案 —— 殘留檢查若漏了這點會 false-negative 誤判「全綠」（本 session 真實案例：settings.json 殘留被 rg 跳過）。查 gitignored 檔用 `rg --no-ignore` / `-uu` 或顯式指定檔名（详见上「隱藏檔陷阱」）

## 搜尋策略

- **找檔案**：`fd` 或 `rg -l "pattern"` — 只需檔名
- **看內容**：`rg --heading -A 3 "pattern" src/` — 多檔搜尋省 token
- **單檔搜尋**：`rg "pattern" file.py` — 路徑已知時直接指定，不需遞迴
- **跨語言搜尋**：`rg -g "*.py" -g "*.pyx" -g "*.rs" "pattern"` — 補足 `--type` 不涵蓋的副檔名

## --heading 省 token

多檔搜尋時加 `--heading`，檔名只在開頭印一次（預設每行重複完整路徑，浪費 token）：

```
rg --heading -A 2 "fn name" src/
```

- `rg` 預設正則匹配，固定字串用 `-F`
- 預設遵守 `.gitignore`，搜尋被忽略的檔案加 `--no-ignore`
- `-g` glob 比 `--type` 更靈活，支援任意副檔名和排除模式
