# User-level AGENTS.md（bundle）內容定稿——整理草案（討論用）

> 2026-09-13，user 發起：「先定稿 Agents.md User level 的內容，這也包含 rules 要包含啥」。輸入＝v3 載體表判準（剛回填）＋腿 3 形態標註＋AIR-86 逐檔裁定＋structure.md 載體地圖＋guide 本體。本檔＝5.3 整理，待 codex 討論後報 user。

## 一、現況盤點（bundle＝什麼）

部署形態：`deploy_agents.py` 把 **guide（ai-development-guide.md）＋16 支 neutral rules** 串接成單檔 bundle → 四家 user-level 位置（ZCode/Codex/Muse/CC 經 rules-dir）。claude-specific 兩檔（bash-hard-rules/code-edit-constraints）只進 CC rules-dir；rules/AGENTS.md（治理檔）不進 bundle（CC 端除外——目錄掃描不限檔名，這是待修的受眾錯置）。現值 32,835B；最緊 target Muse gate ~36KiB（headroom ~4KB）。

## 二、依 v3 判準逐組件的目標態（5.3 初判）

### Guide（bundle 主體，七節）
| 節 | 判準判定 | 目標態 |
|---|---|---|
| 演化性思維 | C 校準（反保守傾向）＋pointer | 留（已短） |
| 驗證約束（風險分級表） | B/C | 留 |
| UC-Driven Development | B（跨 repo 方法論，層級閘過） | 留 |
| Solo+AI 工作流 | B（user 工作形態） | 留 |
| 架構設計紀律 | 已是 pointer 形 | 留 |
| 量化交易專屬鐵律 | B 領域特殊——**bundle 存在理由之一** | 留（核心） |
| Summary Instructions | C（compact 保護） | 留 |
→ **guide 大致健康**；逐句 A 段落（如「測試保護下持續重構」的共識論述）批次二清。

### Rules（bundle 內 16 支）
- **C 大宗 10 支**（tool-discipline/collaboration/quality-constraints/acceptance-evidence/outward-action-consent/must-execute/context-management/modern-cli/_ai-behavior/instruction-writing 骨架）：留——資格公式核心收件人；個別 A 殼句清。
- **slim 三支**：design-thinking（刪 ~60% 共識論述，留兩層強制＋模板 pointer）、edit-discipline（SOLID 展開壓一行）、python-standards（禁舊 typing 共識壓一行；留反主流裁定＋re-export 案例；Write 洞處置）。
- **B 拆分兩支**：model-routing、symbol-query-routing——bootstrap core（兩跳規則/啟動 gate/禁 0-hit 斷言）留；lookup body 沉 skill。
- **條件載入層三支**（AIR-85 後）：instruction-writing、llm-output-convention、（補 carrier 後）python-standards——非 CC bundle body→指針行。

### structure.md 的角色
「引用邊 9 對 rule↔skill 配對表」＝bundle 目標結構的現成地圖——定稿應**追認或修訂**該表（哪些配對再加強、哪些已完成）。斷鏈清單兩項相關：skills/CLAUDE.md 手維護索引；AGENTS.md 家族命名不對稱。

## 三、設計問題（codex 討論焦點）

1. **骨架化程度**：每 rule 終極形＝「一行判準＋pointer」vs 現「核心段落＋pointer」？激進版可再省多少 bytes？代價（脈絡連貫性/新 session 冷啟動理解）？
2. **guide 定位**：保持敘事主體 vs thin 化成索引層（每節一行＋pointer）？guide 的上下文連貫價值（七節互相定義工作形態）值得多少 bytes？
3. **檔案聚合**：16 支維持 vs 合併同性質（如編輯類三支）？合併利（清單短）弊（single-source 邊變粗、CCR/invariant 面重接）。
4. **部署形態**：guide 唯一入口＋rules 全 pointer 化的形態值得評估嗎？
5. **順序**：定稿收斂後 AIR-86 吃目標態；AIR-85 vertical slice 先行與否影響條件載入三支的目標態寫法。
