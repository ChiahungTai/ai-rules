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

## fd 語法對照（取代 find）

| 用途 | find | fd |
|------|------|-----|
| 搜尋副檔名 | `find . -name "*.py"` | `fd -e py` |
| 排除目錄 | `-not -path "*/test*"` | `-E test` |
| 搜尋子目錄 | `find path -name "*.py"` | `fd -e py . path` |
| 只取檔名 | `-exec basename {} \;` | `-x basename` |
| 全路徑匹配 | 預設行為 | `--full-path` |

### fd 注意事項

- `fd <pattern> <path>` 中 pattern 匹配檔名，不是路徑
- 搜尋特定目錄用 `fd . <dir>`，不是 `fd <dir>`

---

## rg 語法對照（取代 grep）

| 用途 | grep | rg |
|------|------|-----|
| 遞迴搜尋 | `grep -r "pattern" .` | `rg "pattern"` |
| 限定副檔名 | `grep -r --include="*.py"` | `rg -t py` |
| 排除目錄 | `grep -r --exclude-dir=node_modules` | 預設遵守 `.gitignore` |
| 只印檔名 | `grep -rl "pattern"` | `rg -l "pattern"` |
| 顯示行號 | `grep -rn "pattern"` | 預設顯示 |
| 固定字串 | `grep -rF "exact"` | `rg -F "exact"` |
| 正則匹配 | `grep -rE "pat.*tern"` | `rg "pat.*tern"`（預設） |

### rg 注意事項

- `rg` 預設使用正則表達式，固定字串用 `-F`
- 預設遵守 `.gitignore`，搜尋被忽略的檔案需加 `--no-ignore`
- 輸出格式比 grep 更豐富，通常不需要額外格式化
