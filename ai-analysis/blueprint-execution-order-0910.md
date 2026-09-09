# 執行順序完整藍圖（2026-09-10 triage 後定版）

> 依據：A 軸卡面宣告矩陣＋B 軸工作項反推實測矩陣（`.agent-tmp/blueprint-{A,B}-matrix.md`）交叉合成。六線＝L1(AIR-58)/L2(AIR-67)/L3(AIR-70)/L4(AIR-60)/L5(AIR-63)/L6(AIR-68)。

## 一、衝突矩陣（A∩B 交叉確認）

| ID | 檔案 | 衝突線 | 消解機制 |
|---|---|---|---|
| O1 | `skills/_common/work-order.md` | L2 段三×L3 段二⑦×L4 | **三線同檔**——波次分離（L3→L2→L4） |
| O2 | `skills/handoff/SKILL.md` | L4×L5（互為約束：64「本地軌不動」vs L4 改引用） | L4→L5 序列 |
| O3 | `rules/context-management.md` | L3 段一 S2×L4 段一 | 波次分離 |
| O4 | `skills/model-routing/SKILL.md` | L1（codex row）×L3 段二①（❔pointer 源）×L4（:163 定向接續節） | 弱衝突（不同節）；L1∥L3 可行，L4 後置 |
| O5 | `review-engine`/`judge-review` | L2 改定義源×L4 驗收掃描 | L2 先於 L4（驗收有效性） |
| O6 | `skills/implement/SKILL.md` | L3 S5×L4 段三 | 弱；波次分離 |
| O7 | MEMORY.md 投影鏈 | L3 段二條目刪改×L5 件一 pointer 行 | 弱；波次分離 |
| O8 | `skills/memory-audit/SKILL.md` | L3 確定改×L1❔×L5❔ | unknown 落點在 L3 段二執行時定 |

**中心結論：L4（AIR-60）是衝突中心**——與 L2/L3/L5 全有面，且 O1 三線同檔——**L4 後置是硬排程約束**。

## 二、執行波次（序列＋唯一真平行）

| 波次 | 線 | 平行性 | 理由 |
|---|---|---|---|
| **0（隨時）** | **L6＝AIR-68** | **真平行**（跨 repo delegate-bridge——與 ai-rules 波次零衝突，B 實測） | 跨 repo 不受共享 WT 約束 |
| 1 | L1＝AIR-58 | 序列首位 | 時效（銜接 57 鏡像 grounding）；觸及面最小（model-routing 系＋agents toml＋mosaic 路由） |
| 2 | L3＝AIR-70 | 序列 | 最重弧兩段連續（13 中級→washed-out 重驗→v2 判準×先鋒 8 條→雙池 audit） |
| 3 | L2＝AIR-67 | 序列 | 三段連續；**O1 與 L3 的 work-order 面已收斂**；registry 連動：改 roles/ 必重跑 sync_agents.py |
| 4 | L4＝AIR-60 | 序列（衝突中心後置） | O1/O2/O3/O5 全部前置收斂後獨占 |
| 5 | L5＝AIR-63 | 序列 | 視圖雙件（O2 與 L4 已序列） |

**共享 WT 約束**：同 repo 同時只宜一條主動弧（單 branch checkout）——「平行」僅跨 repo 成立（L6）。同弧內多段=同 session 連續做。

## 三、連動面與易錯點（兩軸貢獻）

- **Registry 連動**（B）：`agents/roles/` 改動必重跑 `sync_agents.py`（生成 zcode/claude 兩份）——L2 段一 R2 觸發
- **同名分家**（A）：`rules/model-routing` ≠ `skills/model-routing/SKILL`；`rules/symbol-query-routing` ≠ skill 同名——驗收 rg 勿混
- **L6 的 ai-rules 側殘留**（B）：根 `AGENTS.md:107` delegate-rescue 消費描述——AIR-68 驗收「零殘留」會掃到，卡 scope 需含此處
- **路徑糾錯**（B）：mosaic 實路徑 `mosaic_alpha`（下底線）；先鋒 8 條⑥＝雙檔落點（instruction-clean＋edit-discipline，6 檔 7 落點）
- **draft-5 已 wash**（B 實測不在場——triage 清除生效）

## 四、unknown 待定項（執行時裁）

L4：rehydration 單一源落點／receipt 生成器路徑／followup 與 post-build 二擇一；L5 件一：豁免落點／gitignore；L2 段三：注入塊與 R7 落點；O8 memory-audit 落點歸屬——共 18 項詳 A 軸 §3，各線 handoff 時逐項帶入。

## 五、handoff 順序

L6 handoff（已備）隨時可開；L1 handoff 即刻可備；各波收斂→ ff main → 下一波 handoff。每波 handoff 帶：本藍圖衝突格＋該線卡（自足）＋unknown 項。
