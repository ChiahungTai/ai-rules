# 腿 3：rules/ 19 檔逐檔形態標註（A 共識／B 特殊／C 校準／D 機械）

> 產出者：lite-verify（glm-5.3-flash），2026-09-13。19 檔全部完整 Read。形態判準：A=模型已內建通用工程共識；B=領域/專案特定（離開 context 模型不知道）；C=反直覺行為校準（模型不做就會犯錯，非專案特定）；D=具體工具/命令/命名慣例。

## 盤點勘誤
派單稱 20 檔；實測 `ls rules/*.md | wc -l`＝**19 檔、696 行**（證據 wc -l 合計 696）。以下按實際 19 檔。

## 逐檔標註

### rules/AGENTS.md（151 行）
| 條目/小節 | 形態 | 一句理由 |
|---|---|---|
| Claude vs 非 Claude 載入架構（dir symlink vs deploy bundle）| B | 「rules auto-load 是 Claude 獨有」屬 ai-rules 部署拓撲 |
| 部署紀律（`uv run python scripts/deploy_agents.py`）| B/D | 專案流程與具體命令一體 |
| 尺寸 gate 與截斷線（ZCode 100KiB 硬編碼、Muse 65,536 bytes）| B | 特定 harness 實測事實「hIn=100*1024 無 config 可調」 |
| 部署驗證義務（deploy exit 0 ≠ 部署完成）| C/B | 扳「只看 [OK] 宣稱完成」；逐端驗法專案特定 |
| harness-scope 分類表＋default=neutral | B | 本 repo frontmatter 機制與逐 rule 歸類 |
| Rule 寫作原則（可驗證／signal 導向）| B 註 A | 「保留從程式碼猜不到的知識」為 AI instruction 特有治理 |
| Neutral 中性化規範＋括號註模式＋rg 機械檢查清單 | B/D | 跨 harness 寫作規範；末段 rg 清單屬機械 |

### _ai-behavior-constraints.md（9 行）
| 條目 | 形態 | 一句理由 |
|---|---|---|
| single-source drift 防護（rg 掃引用逐檔同步）| C/B | 扳「改定義源忘了掃引用」；sync-sources invariant 屬專案機制 |

### acceptance-evidence.md（34 行）
| 條目 | 形態 | 一句理由 |
|---|---|---|
| 證據獨立性（「綠燈只證明自洽」）| C | 扳 AI 同寫 test＋impl 的自洽陷阱 |
| Claim→Evidence→Trust no-impact 校驗 | C | 「self-report 不能取代查證」防自述無影響 |
| claim 細則群（數字核對／死碼全消費端／禁標 silent／自報元資料）| C | 六條全防憶印象與靜態推論，附真實案例（41 誤寫 20）|
| L1–L6 證據階層表＋禁低層冒充高層 | B 註 A | 測試金字塔是共識基底；六層＋A/B 軸為本專案自訂框架 |

### bash-hard-rules.md（24 行，claude-specific）
| 條目 | 形態 | 一句理由 |
|---|---|---|
| 權限偵測限制（「`#` 是毒藥、`$` 是禁區、陣列是禁區」）| B/D | Claude CLI 靜態分析器行為屬工具事實；替代寫法屬機械 |
| 例外與降級（寫 .py 再 uv run）| D | 具體替代路徑 |

### code-edit-constraints.md（60 行，claude-specific）
| 條目 | 形態 | 一句理由 |
|---|---|---|
| Edit 前必 Read／重讀／old_string 精確 | C | 扳「憑記憶拼湊」——不做就 Error 的校準 |
| replace_all 子串陷阱（SyncSyncRateLimiter 案例）| B 註 C | 「無整詞邊界選項」是 Edit API 工具事實 |
| 連續 3 次同類錯誤停下驗證、禁盲目重試 | C | 扳不改策略的反覆嘗試 |

### collaboration-constraints.md（36 行）
| 條目 | 形態 | 一句理由 |
|---|---|---|
| 理解優先實作（禁猜測實作、疑問一次彙整）| C | 扳需求不明就動手 |
| 事實查證原則（path:line、AGPL 禁搬碼、fork 查 .venv）| C/B | 查證義務屬校準；AGPL/fork 條款屬領域特定 |
| 破壞性選擇的查證觸發（刪檔查 README/backlog）| C | 扳「憑檔名選」，附 standup 卡誤刪案例 |
| 具體明確表達（禁「大概/可能/應該可以」）| C | 扳 hedging 語言 |
| 反 Sycophancy（VERIFY→EVALUATE→附理由反對）| C | 扳盲從建議、盲改指標污染回測 |
| 工作目錄紀律＋Agent 派發與產出回收 | C/B | 多 WT 協作校準＋本 repo 卡/worktree 拓撲 |

### context-management.md（27 行）
| 條目 | 形態 | 一句理由 |
|---|---|---|
| Session 管理（重置、兩次糾正失敗換 prompt）| C/B | 扳「同題硬撐」；Writer/Reviewer 載體屬專案慣例 |
| 想法即時落盤（durable checkpoint）| C/B | 扳「findings 留 transcript 後 session 死亡」；EP/卡/journal 載體專案特定 |
| STATE.md pointer | B | 專案 Last session 觀察層機制 |
| Memory 生命周期 pointer | B | MEMORY.md 投影禁手寫、條目檔唯一寫入點——專案池規範 |

### design-thinking.md（31 行）
| 條目 | 形態 | 一句理由 |
|---|---|---|
| 兩層思考（第一性原理＋「至少兩層連鎖後果」）| A/C | 第一性原理是共識；強制兩層深度屬校準 |
| 決策分級（單向門/雙向門）| A 註 C | one-way door 為通用概念；「機械工作用程式，不用 LLM 當萬用工具」偏校準 |
| 架構三視角（依賴向內/bounded context/use case 驅動）| A 註 B | Clean Architecture＋DDD 教條原型；「禁跨域直接存取 _private」屬專案慣例 |
| 觸發情境（載 trading-analysis skill）| B | 專案 skill 路由 |

### edit-discipline.md（27 行）
| 條目 | 形態 | 一句理由 |
|---|---|---|
| 核心原則（「預設不保留向後相容」）| C 註 A | 測試保護下重構屬共識；反相容保守預設屬校準 |
| SOLID＋validation 禁投機＋scripts 層級 | A 註 B | SOLID 為共識原型；「scripts 不反向侵入 library」偏專案分層 |
| 衝突寫法處理（禁默默混合）| C | 扳「矛盾各取一半」妥協傾向 |
| 向後相容確認機制 | C/B | 扳預設加相容層；觸發條件含專案部署情境 |
| 變更範圍紀律（「刪除不留 tombstone，歷史交 git log」）| A/C | 最小變更屬共識；反墓碑註解習慣屬校準 |

### instruction-writing.md（17 行）
| 條目 | 形態 | 一句理由 |
|---|---|---|
| 雙檔架構（AGENTS.md source／CLAUDE.md thin wrapper）| B | 跨 harness instruction 拓撲 |
| Signal/Noise 準則（可推導＝噪音、真實案例標記）| B 註 A | 本專案治理準則；「不寫可推導內容」有共識成分 |
| 禁統計/版本號/更新日期/Changelog | B | 本專案元資訊禁令 |
| 導航＝概念→symbol 種子，位置交 LSP | B | 依賴 LSP 工具鏈的分工立場 |

### llm-output-convention.md（21 行）
| 條目 | 形態 | 一句理由 |
|---|---|---|
| print=索引 Logger=資料庫（state transition, not computation trace）| B 註 C | 專案發明慣例；扳 print debug trace 傾向 |
| Namespace 強制 module-path（`Logger(__name__)`）| D 註 A | 具體命名慣例；__name__ 有 Python 生態共識基底 |
| status tag 禁 [INFO]、`action_name:` 前綴 | D | 具體輸出格式 |

### model-routing.md（32 行）
| 條目 | 形態 | 一句理由 |
|---|---|---|
| 兩跳解析＋tier 定義（full/vision/lite）| B | 本專案角色分層體系 |
| model 詞彙（native ID only、alias fail-closed）| B | user 裁定詞彙約束，離開 context 無從得知 |
| 角色→tier 表＋external-runtime family/profile／bridge 拓撲 | B | 逐角色拍板裁決＋GLM/muse/codex bridge 事實 |

### modern-cli-preference.md（9 行）
| 條目 | 形態 | 一句理由 |
|---|---|---|
| 「文字→rg、檔案→fd」 | C 註 D | 扳 grep/ls 舊習（C 原型）；工具映射屬機械 |

### must-execute-before-complete.md（23 行）
| 條目 | 形態 | 一句理由 |
|---|---|---|
| 核心原則（必須實跑，ast.parse 不算）| C | 扳「說理論可行就報完成」——C 原型 |
| 強制規則（RED 先行、綠後確認測到聲稱行為）| C 註 A | TDD 是共識；「確認確實測到」扳形式化跑測 |
| POC 生命週期（EP build＋commit 為止）＋例外清單 | B | 本 repo 工作流節點（build 提煉正式測試、commit 2.7 承接）|

### outward-action-consent.md（50 行）
| 條目 | 形態 | 一句理由 |
|---|---|---|
| 核心原則＋Reversibility test（outward 需授權）| C 註 B | 扳自主 commit/deploy——C 原型；live order/broker write 屬量化場景 |
| AUTH line 模板＋quote scope 判準（逐字引用禁意譯擴張）| C/D | 防邏輯跳躍擴權；模板格式具體 |
| documentation ≠ authorization | C | 扳「README 有寫就當授權」 |
| Commit 專屬段（最嚴格等級）＋kanban 四例外 | C/B | 確認 gate 屬校準；①–④ 例外屬本 repo 卡簿流程 |
| Autonomous shortcut＋Source of truth 邊界 | B | deep-work 紅線枚舉與治理宣告屬專案體系 |

### python-standards.md（37 行）
| 條目 | 形態 | 一句理由 |
|---|---|---|
| demo_/test_ 命名約定 | D 註 B | 命名慣例原型；「demo commit 時移 scripts/」屬專案流程 |
| `__init__.py` 禁 re-export＋Facade 論證 | B/C | 反 Python 社群常見實踐的專案立場，附 import 變秒真實案例；防 facade 傾向屬 C |
| 遷移既有 re-export（先查全消費者，禁先刪）| C | 程序校準 |
| 型別註解（禁 `__future__`/TYPE_CHECKING、禁舊 typing、Any 先查 py.typed）| C 註 A | 禁舊 typing 是共識；禁 `__future__`/TYPE_CHECKING 反主流風格＝校準 |
| Python 命令執行 pointer | D | 單一源指針（tool-discipline）|

### quality-constraints.md（37 行）
| 條目 | 形態 | 一句理由 |
|---|---|---|
| 完整交付標準（核心功能＋文檔同步）| A 註 B | 可用交付是共識；「檢查上層 AGENTS.md」屬專案結構 |
| Crash-Only Design（「損壞數據比缺失更危險」）| B 註 A | 量化交易鐵律＋適用/不適用表；fail fast 有共識基底 |
| 誤用警告（crash-only 非 graceful 不修藉口）| C/B | 扳規則濫用；ReplayHost SIGTERM 案例專案特定 |
| Fail Loud＋消費端驗證模式 | C | 扳「隔離綠燈報完成」「憑目錄直覺選測試集」 |
| 漸進式驗證（DEPTH-MIN→SAMPLE→FULL）＋多步驟檢查點 | C | 扳「改後直跑 FULL」「不確定仍盲續」 |

### symbol-query-routing.md（21 行）
| 條目 | 形態 | 一句理由 |
|---|---|---|
| cr-first 路由（符號→code-reality）| B 註 C | code-reality 屬專屬工具鏈；扳「rg 查符號」 |
| code-reality 分工（SCIP/pyrefly/lsp-bridge/harvest）| B | 工具鏈內部事實，模型離開不會知道 |
| 任務啟動 gate＋rg 漏符號警告（勿宣稱零消費者）| B/C | 專案 gate 機制；「禁把未查到斷言為不存在」屬校準 |

### tool-discipline.md（50 行）
| 條目 | 形態 | 一句理由 |
|---|---|---|
| 工具選擇＋視覺判讀路由（禁主 session Read 圖）| C/B | 扳讀圖佔滿 context；agent 路由屬專案架構 |
| Skill 調用紀律（先讀再派）| C | 扳裸派跳過 skill，附真實案例 |
| Python 命令執行（uv run 強制、禁 timeout/gtimeout）| D | 命令前綴原型；macOS 無 timeout 屬平台事實 |
| zsh 動態 flag 陣列（`args=(...)`＋`"${args[@]}"`）| D | 具體 shell recipe 原型 |
| 檔案修改禁令（禁 sed 改檔、Edit/Write 前先 Read）| C | C 原型雙入 |
| Edit 失敗處置階梯（第二次 not found 停止盲試）| C | 扳第三次盲試；repr 唯讀診斷程序化 |
| 背景執行（run_in_background、`[fg]` 逃生口）| B/D | ZCode 前台預設與 rewrite gate 屬 harness 機制事實＋具體參數 |
| 閘門命令禁 pipe 到 tail/grep | C | 扳 pipe 把失敗偽裝綠燈 |
| Read 紀律＋獨立呼叫批次化 | C | 扳重複全讀（86KB×19 案例）與序列呼叫 |
| 輸出慣例（繁體中文＋英文術語）| B | 用戶語言偏好 |

## 彙總

### 19 檔形態分佈統計

| 檔 | 主要形態 | A 類佔比估計 |
|---|---|---|
| AGENTS.md | B | ~5% |
| _ai-behavior-constraints.md | C | 0% |
| acceptance-evidence.md | C | ~10% |
| bash-hard-rules.md | B | 0% |
| code-edit-constraints.md | C | ~5% |
| collaboration-constraints.md | C | ~10% |
| context-management.md | C（B 成分重）| ~5% |
| design-thinking.md | **A** | ~60% |
| edit-discipline.md | C/A | ~35% |
| instruction-writing.md | B | ~10% |
| llm-output-convention.md | B/D | ~15% |
| model-routing.md | B | 0% |
| modern-cli-preference.md | C | 0% |
| must-execute-before-complete.md | C | ~15% |
| outward-action-consent.md | C | ~5% |
| python-standards.md | C/D | ~25% |
| quality-constraints.md | C | ~10% |
| symbol-query-routing.md | B | ~5% |
| tool-discipline.md | C | ~5% |

主要形態計數：**B 6 檔、C 12 檔、A 1 檔**。全庫加權 A 類密度約 **10%**（design-thinking 與 edit-discipline 貢獻大半）；C 類為最大宗（校準密集：宣稱完成前實跑、commit consent、禁 sed、rg 優先、不憑記憶編輯）；B 類集中在專案拓撲（部署/model-routing/symbol-query/memory/kanban）。

### A 類密度最高 top 5
1. design-thinking.md（~60%——Clean Architecture/DDD/單向門皆共識基底）
2. edit-discipline.md（~35%——SOLID＋最小變更）
3. python-standards.md（~25%——禁舊 typing、命名基底）
4. llm-output-convention.md ＝ must-execute-before-complete.md（~15%——`__name__` 慣例／TDD）

### B/C 密度最高 top 5（A 近零、專案特定知識純度最高）
1. model-routing.md（B 幾乎 100%——角色裁決＋bridge 拓撲）
2. bash-hard-rules.md（B/D 100%——Claude CLI 靜態分析器行為）
3. _ai-behavior-constraints.md（C/B 100%——drift 防護機制）
4. AGENTS.md（~95%——部署拓撲＋scope 治理）
5. symbol-query-routing.md（~95%——code-reality 工具鏈事實）
（modern-cli-preference.md 9 行小檔亦近全 C/D，因篇幅未列入）
