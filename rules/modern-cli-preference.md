# 現代 CLI 工具偏好

> **自動載入**: 此檔案位於 `~/.claude/rules/`，會自動載入到所有會話

---

## 核心原則

**搜尋檔案用 `fd` 取代 `find`，搜尋內容用 `rg` 取代 `grep`。**

兩者皆為 BurntSushi 開發，已透過 Homebrew 安裝，預設可被 `Bash(fd:*)` / `Bash(rg:*)` auto-allow。

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

## 搜尋策略

- **找檔案**：`rg -l "pattern"` 或 `fd` — 只需檔名
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
