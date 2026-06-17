# /consistency 經 Skill tool + context:fork 調用時 $ARGUMENTS 不傳入 fork context → 自檢 consistency.md（非目標檔）

> 來源：為 nt-query skill 改動的 `SKILL.md` 跑 `/consistency` 驗證時發現。互動式 `/consistency <path>`（user 直接打）正常；程式化 `Skill(consistency, args=...)` 走 `context: fork` 時 args 丟失，subagent 自檢了 `consistency.md` 自己的定義檔。type-2（命令/harness 互動設計缺陷），記錄供 /flow-review。

## 情境

為驗證改動過的 `skills/nt-query/SKILL.md`，程式化調用：

`Skill(skill="consistency", args="/Users/.../skills/nt-query/SKILL.md")`

回傳報告的「受檢文檔」竟是 `/Users/ctai/Github/ai-rules/commands/consistency.md`（consistency 命令**自己的定義檔**，自評 78/100），而非目標 SKILL.md。報告開頭 subagent 自承：

> 「我注意到注入的 prompt 主體…在步驟 0 寫著 `…/skills/nt-query/SKILL.md`，但 `commands/consistency.md` 的實際檔案內容卻是 `$ARGUMENTS`。」

即：consistency.md 命令體裡的 `$ARGUMENTS` **沒被替換**成路徑（字面殘留 `$ARGUMENTS`）。subagent 在 wrapper 訊息看得到目標是 SKILL.md，但命令體說「read `$ARGUMENTS`」（字面）→ 無法解析目標 → 轉而自檢 consistency.md。

## 為何發生

`$ARGUMENTS` 替換的兩條調用路徑行為不一致：

| 調用方式 | `$ARGUMENTS` 是否替換進命令體 | 結果 |
|---|---|---|
| 互動式 `/consistency <path>`（user 鍵入） | ✅ 是（harness 執行前替換） | 正確檢查目標檔 |
| 程式化 `Skill(consistency, args=...)` + `context: fork` | ❌ 否（fork context 拿到 args 但未替換進命令體的 `$ARGUMENTS`） | 命令體殘留字面 `$ARGUMENTS` → subagent 無目標 → 自檢 |

subagent 在 wrapper 看得到 args（所以它「知道」目標是 SKILL.md），但一致性檢查的**執行邏輯**寫在命令體裡（讀 `$ARGUMENTS`），命令體沒被替換 → 執行邏輯拿不到目標 → 退化成自檢。這是「args 傳到了 wrapper、卻沒傳到執行邏輯」的斷層。

## type-2 建議（設計）

**根因修復（harness 層，正解）**：`Skill` tool 對 `context: fork` 命令，fork 前應與互動式一樣把 `$ARGUMENTS` 替換進命令體。否則任何 `$ARGUMENTS` + `context: fork` 的命令經程式化調用都會斷層。

**防禦性加固（命令層，belt-and-suspenders）**：consistency.md（及所有用 `$ARGUMENTS` 的命令）在步驟 0 偵測「目標是否為字面 `$ARGUMENTS` 或空」→ fail-fast：

```
若目標 == "$ARGUMENTS" 或空 → 停止，回「未收到目標路徑；請以 /consistency <path> 調用」，不要自檢。
```

避免「拿不到目標就自檢自己」這種誤導性輸出——78/100 自評看起來像真跑了一次驗證，其實跑錯檔，比「沒跑」更危險（虛假信心）。

**本次降級處置（已採用）**：spawn 獨立 `Agent`，把目標路徑直接寫進 prompt（不靠 `$ARGUMENTS`）。副作用反而是正面——獨立 agent 的驗證獨立性高於「AI 自驗自己」（符合 acceptance-evidence：A 軸自驗天花板是 AI 內部自洽），所以這個 workaround 不只繞過 bug，還提升了證據強度。

## 影響範圍

非 consistency 獨有——**任何用 `$ARGUMENTS` + `context: fork` 的命令/skill，經 `Skill` tool 程式化調用都會中招**。建議 /flow-review 時機械掃描：

```
rg "context:\s*fork" commands/ skills/     # 撈所有 fork 命令
rg "\$ARGUMENTS" commands/ skills/          # 交叉用 $ARGUMENTS 的
```

兩者交集 = 潛在受害命令，逐一想「程式化調用會斷層嗎」。

## 本次處置

未修根因（harness `$ARGUMENTS`-in-fork 注入機制，需更深確認；留 /flow-review 討論修在 harness 層還是命令層 fail-fast）。本次用獨立 agent workaround 完成驗證。

## tags

`consistency` `context:fork` `$ARGUMENTS` `Skill-tool` `harness` `forked-execution`
