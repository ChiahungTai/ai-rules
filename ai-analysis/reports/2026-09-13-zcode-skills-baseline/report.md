# ZCode Harness Skills 現況盤查（baseline）

> 2026-09-13，lite-verify 盤查（read-only）＋主 session 補查 model-routing 載入異常 root cause。用途＝skills corpus 治理弧的 baseline 材料（建卡依據）。所有數字機械覆核（wc -c／ls／rg）。

## 1. 拓撲

| 事實 | 證據 |
|---|---|
| `~/.zcode/skills` → symlink → `/Users/ctai/Github/ai-rules/skills`（`~/.agents/skills` 同指一實體） | `ls -ld` 兩條 symlink |
| 兩路徑內容逐 byte 一致 | `diff -rq` → identical |
| repo skills＝79（80 目錄扣 `_common/` 共用子範本，非 skill） | `ls */SKILL.md \| wc -l` |
| 專案層 `.zcode/skills/` 不存在 | `ls .zcode/` 僅 `plans/` |
| plugin 真相源＝`~/.zcode/cli/plugins/installed_plugins.json`（5 件）＋zcode-plugins-official 四件 bypass enabledPlugins 在場 | config 比對 |
| **active 總數＝97**（repo 79＋plugin 18）；cache 全量 110 SKILL.md（含歷史版本孤兒） | find/wc |

## 2. 來源×功能彙總

| 來源 | count | bytes |
|---|---|---|
| repo | 79 | 984,591 |
| plugin:official（browser-use/document-skills/skill-creator/zcode-guide） | 13 | 242,675 |
| plugin:code-reality | 1 | 19,532 |
| plugin:delegate | 3 | 11,028 |
| plugin:sinotrade | 1 | 18,908 |

| 功能 | count | bytes |
|---|---|---|
| A 開發工作流編排 | 12 | 225,549 |
| B 審查與驗證鏈 | 14 | 190,312 |
| C 治理與文檔生命週期 | 21 | 249,444 |
| D 方法論/深掘參考 | 17 | 213,320 |
| E 量化交易域 | 8 | 75,758 |
| F 人類 viewport/視覺 | 8 | 60,096 |
| G harness/外部工具操作 | 17 | 262,255 |

Top-10 最大：pdf 70,643／memory-audit 48,150／**model-routing 48,023（未載入，見 §4）**／implement 41,444／pptx 44,225／execution-plan 40,244／instruction-writing 31,065／audit-test 30,750／rebase 29,393／arch-thinking 25,781。

## 3. 觀察（機械事實）

1. **同名撞名**：`code-reality` repo 版（15,361B）與 plugin 版（19,532B）並存皆可載，內容不同——載入序 user > workspace > plugin，實際生效=repo 版；語義 drift 風險。
2. **雙路徑重複計**：harness 清單把 78 個 repo skill 各列兩次（`.zcode`/`.agents` 同實體）——統計勿以清單長度為準。
3. cache 殘留：code-reality 積 24 版本、browser-use 8 版；muse-market 6 版未安裝；official 的 android-emulator/ios-simulator/computer-use 等僅存 cache。
4. `mermaid/` 權限 0700（其餘 0755）。
5. frontmatter 變異：maintain/scan-project/pdf/shioaji 用 block scalar（`>`/`|`）——工具消費 desc 需支援。
6. ZCode 官方載入規則（zcode-guide/diagnosing-skills）：扁平 key:value 解析；desc 缺失或 **>1024 chars → skill 被 drop**；**觸發呈現只取 desc 前 ~250 chars**（觸發詞寫在 desc 尾=對 ZCode 無效）。

## 4. model-routing 未載入——root cause（主 session 補查定案）

- 現象：磁碟在場（48,023B、frontmatter name+description 齊）、YAML 合法（ruby safe_load OK、parsed desc 563 chars），但本 session harness skill 清單獨缺它（其餘 78 個 repo skill 皆在）。
- **Root cause：raw description 行 1,198 chars > 1024 上限 → ZCode flat parser 直接 drop**（官方文檔明文）。memory-audit 614/acceptance-evidence 465 皆低於限。
- 附帶陷阱：desc 是未引號 plain scalar 且含 ` #339/#306`——完整 YAML 解析器會剝註解（parsed 563），ZCode flat parser 不剝（raw 1,198）——**兩種解析器量到的長度不同，以 raw 為準**。
- 影響：model-routing（tier×provider 權威表、spawn 前必載）對 ZCode session **靜默不可見**——規則端 `rules/model-routing.md` 的「委派前必載 skill」指針在 ZCode 端指不到（silent failure 形態）。
- 修法方向（未執行，待拍板）：desc 收斂 ≤1024 raw chars 且觸發語義前置（前 250 chars）＋加引號；或拆 when_to_use。屬 skills 治理弧或獨立 hotfix。

## 5. 明細

完整 97 行明細表（name｜分類｜bytes｜desc 首句）見盤查 agent 原始回報（本檔 §1–4 為其彙總＋補查）；`?` 標註三項：ep-validate（B?）、standup（C?）、agent-workflow（A?）。
