# AIR-86 批次一：5.3 側實施規格底稿（與 codex 規格合成前）

> 2026-09-13。5.3 主 session 逐檔現況盤點。**關鍵修正發現**：三檔的現況比 codex §C 目標態表的削減預期**小很多**——部分 body 已被既有機制承接。

## 檔 1：design-thinking.md（1,510B；目標態 0.7-0.95K）

現況逐段：
- L7-13 兩層思考：C 核心（「本質對但後果壞仍不可接受」＋⑤兩層連鎖強制＋禁憑記憶）——**留**；已帶 deep-thinking pointer
- L15-17 決策分級：A 基底（單向門通用概念）＋C（機械工作用程式）——**A 句壓縮，C 句留**
- L19-27 架構三視角：A 基底（CA/DDD 教條）＋B（禁跨域存取 _private）——**壓兩行**（視角名＋_private 禁令），詳情已在 arch-thinking
- L29-31 觸發情境：B 路由——留一行

**5.3 裁定**：slim 後約 ~0.9K（codex band 內）。**注意**：codex D 節說它「升成明確 bootstrap core ↔ methodology body」——本檔 L13/27 pointer 已在場，動作主要是 L17/L21-25 壓縮。

## 檔 2：acceptance-evidence.md（3,527B；目標態 1.0-1.3K）——**重大修正**

現況結構：
- L7-13 核心原則＋Claim→Evidence→Trust：**C 核心，留**（已帶 skill pointer）
- **L15-21：`bundle: skip-start/end` 區塊**——claim 細則五條（數字核對/死碼全消費端/silent-failure/review 雙向/自報元資料）**已存在 skill 承接形態：bundle 部署時整段剝除，只有 CC rules-dir 與 repo source 讀到**
- L23-34 證據階層表＋禁低層冒充：B 本專案框架＋C——**留**

**5.3 裁定（byte 修正後）**：deployed 1,615B（skip 已剝除部署——CC 端 repo source 讀者仍見全量）→ 剩餘工作 −315~600B（對 band 1.0-1.3K）。§C 以 source 3,527 當基線是重複計帳；真正可做＝L7-13 核心句壓縮＋review 雙向條（L19）與 code-review-and-quality 職責邊界核對＋skip 區塊的 AIR-85 條件投影候選評估。

## 檔 3：model-routing.md（3,019B；目標態 1.4-1.8K）

現況逐段：
- L7-11 兩跳解析＋tier 定義＋model 詞彙（user 裁定＋invariant）：**bootstrap 核心，全留**
- L13-24 角色→tier 表（8 行）：**user 裁定密集**——每行都有拍板語義（lite 預設/full 不可降/內建型別陷阱）——**留**（這是「特殊裁定」資格，非 A）
- L26 尾註：留
- L28-32 external-runtime 段：family/profile 詞彙定義（權威）＋必載 skill 指針——**留**（已是 pointer 形）

**5.3 裁定**：本檔**已接近目標態**（3.0K vs band 1.4-1.8K 上緣+）——codex「委派細節/resume/fork/rate-limit 收 skill」**在現況檔內沒有對應可刪段落**（那些細節本來就只在 skill）。實際可動＝角色表兩行壓縮（L17/L19 的論證括號），約 −300~500B。

## 對 codex 規格 round 的修正要求（byte 精度修正後）

> ⚠️ 初版底稿犯單位錯（char 當 byte，CJK ~1.7×）——已修正。**deployed per-rule 基線已實測**（見下表）。

1. **§C 以 source bytes 為基準的部分重複計帳需修正**——最顯著：acceptance-evidence deployed 1,615B（skip 機制已剝 claim 細則 ~1.9KB；source 3,527 是假基線）→ 剩餘工作僅 −315~600B。其餘檔無 skip 區塊者 source≈deployed，§C 基線成立。
2. **實測 deployed 基線**（B，vs §C band 上緣＝剩餘工作）：tool-discipline 3,676（−976）/model-routing 3,058（−1,258，但檔內 lookup 本就 pointer 化，實際可動＝角色表論證括號壓縮 −500~800）/collaboration 2,539（−739）/outward 2,414（−214）/quality 2,386（−686）/python 2,095（−595）/context 1,710（−510）/acceptance 1,615（−315~600）/symbol 1,595（−645）/design 1,551（−601）/edit 1,306（−356）/must 1,209（−359）/llm+IW+_ai+modern ≈3,190（−711 合計）＋非 rules 段 4,491（−1.3~1.9K）。
3. **真實 headroom ≈ 10KB**（落點 ~23KB，codex 19-23.5K 估計的下緣區）——原 9-14K 估計成立但偏樂觀端。
4. **批次一修正**：design-thinking −601 / acceptance-evidence −315~600（非 −2.2K） / model-routing −500~800（角色表壓縮，非整段遷移）→ 批一實際 ≈ −1.4~2.0KB（非 §C 的 3.4-4.4K）。
5. AIR-86 卡驗收對照加「deployed 現值」欄（上表數字）作為機械起點。
