# Solo Developer + AI 開發流程圖

> 基於 2026-06-07 討論整理。描述 mosaic_alpha 專案的實際開發模式。

---

## 核心模式：預設一個 EP = 一個 Session

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'primaryBorderColor': '#4a9eff', 'lineColor': '#6a9fff', 'fontFamily': 'system-ui'}}}%%
flowchart LR
    classDef good fill:#1a3e2e,stroke:#27ae60,color:#e0e0e0,stroke-width:2px
    classDef ok fill:#3e3a1a,stroke:#f1c40f,color:#e0e0e0,stroke-width:2px
    classDef bad fill:#3e1a1a,stroke:#e74c3c,color:#ffcccc,stroke-width:3px
    classDef decision fill:#1a1a3e,stroke:#4a9eff,color:#e0e0e0,stroke-width:2px

    SESSION["Session N<br/>新鮮 context"]:::good
    PLAN["/execution-plan<br/>產生 EP"]:::decision
    BUILD["/build<br/>逐段實作"]:::decision
    REVIEW["/code-review<br/>獨立 session"]:::decision
    COMMIT["/commit<br/>等待確認"]:::good
    DONE["✅ EP 完成<br/>Archive"]:::good

    SESSION -->|"新 EP"| PLAN --> BUILD -->|"EP 完成"| REVIEW --> COMMIT --> DONE

    %% Compact 發生在任何階段
    PLAN -.->|"/compact"| PLAN
    BUILD -.->|"/compact"| BUILD
    REVIEW -.->|"/compact"| REVIEW

    %% Model 退化 → 更新 EP → 新 session
    BUILD -.->|"Model 變怪"| SAVE["📝 更新 EP 進度"]:::ok
    SAVE -->|"開新 session"| SESSION2["Session N+1<br/>新鮮 context"]:::good
    SESSION2 -->|"繼續同一 EP<br/>或開新 EP"| PLAN

    style SAVE fill:#3e3a1a,stroke:#f1c40f,stroke-width:2px
```

---

## 全景流程

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'primaryBorderColor': '#4a9eff', 'lineColor': '#6a9fff', 'fontFamily': 'system-ui'}}}%%
flowchart TD
    classDef decision fill:#1a1a3e,stroke:#4a9eff,color:#e0e0e0,stroke-width:2px
    classDef session fill:#16213e,stroke:#2ecc71,color:#e0e0e0,stroke-width:2px
    classDef warning fill:#3e1a1a,stroke:#e74c3c,color:#ffcccc,stroke-width:2px
    classDef archive fill:#1a3e2e,stroke:#27ae60,color:#e0e0e0,stroke-width:2px
    classDef human fill:#3e3a1a,stroke:#f1c40f,color:#e0e0e0,stroke-width:2px

    %% ── 決策 ──
    subgraph DEC["🎯 決策：下一個做什麼"]
        BL["UC-BACKLOG.md<br/>Track P: P0→P3<br/>Track A: A0→A4"]:::decision
    end

    BL --> HUMAN["👤 人類判斷<br/>看三個 VSCode worktree"]:::human
    HUMAN -->|"選定 item"| NEWSession

    %% ── 新 Session ──
    NEWSession["🔄 開新 Session<br/>（新 EP = 新 Session）"]:::session

    %% ── EP 規劃 ──
    subgraph PLAN["📐 EP 規劃"]
        SPEC["/spec<br/>掃描 USE-CASES.md<br/>定義或更新 UC"]:::decision
        EP["/execution-plan<br/>產生 EP，引用 UC ID"]:::decision
    end

    NEWSession --> SPEC --> EP

    %% ── Build ──
    subgraph BUILD_LOOP["🔨 Build"]
        BUILD["/build<br/>按 segment 逐段實作"]:::session
        UPDATE["更新 USE-CASES.md<br/>📋→✅"]:::session
    end

    EP --> BUILD --> UPDATE

    %% ── Review & Commit ──
    UPDATE -->|"EP 全段完成"| CR["/code-review<br/>平行 session"]:::archive
    CR --> CM["/commit<br/>展示變更摘要<br/>等待人類確認"]:::archive

    %% ── 歸檔 ──
    CM --> EPARC["EP → _done/"]:::archive
    CM --> BLUP["更新 UC-BACKLOG"]:::archive
    BLUP --> BL

    %% ── Model 退化（隨時發生）──
    EP -.->|"context 變怪"| DEGRADE["⚠️ 更新 EP 進度<br/>開新 Session"]:::warning
    BUILD -.->|"context 變怪"| DEGRADE
    DEGRADE --> NEWSession
```

---

## 三個 Worktree + Trunk 模型

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
    classDef trunk fill:#1a3e2e,stroke:#27ae60,color:#e0e0e0,stroke-width:2px
    classDef feature fill:#3e2e1a,stroke:#e67e22,color:#e0e0e0,stroke-width:2px

    subgraph WT0["🖥️ main repo — main（trunk）"]
        T0["唯一整合線<br/>只往前、永不被 rebase"]:::trunk
    end

    subgraph WT1["🖥️ trading_lab — replay（feature）"]
        F1["replay 開發軌"]:::feature
    end

    subgraph WT2["🖥️ offline_backtesting — backbone（feature）"]
        F2["backbone 開發軌"]:::feature
    end

    WT1 -->|"rebase main（單向）"| WT0
    WT2 -->|"rebase main（單向）"| WT0
```

> **單向 rebase，不交互**：feature（replay / backbone）只 rebase onto trunk（`main`）；feature 之間不直接 rebase（要對方的東西走 trunk 中轉）。Trunk 只用 `git merge --ff-only` 吸收「已 rebase 過 main」的 feature —— 不是 fast-forward 就拒絕（安全欄杆，避免靜默改寫已 push 的 trunk）。`rerere` 開啟，相同衝突自動套用前次解析。詳見 [/rebase](../../commands/rebase.md)。

---

## UC-BACKLOG ↔ EP ↔ Session 關係

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart TD
    classDef backlog fill:#1a1a3e,stroke:#4a9eff,color:#e0e0e0
    classDef ep fill:#16213e,stroke:#2ecc71,color:#e0e0e0
    classDef uc fill:#1a3e2e,stroke:#27ae60,color:#e0e0e0

    subgraph BACKLOG["📋 UC-BACKLOG.md"]
        P0["P0: Paper Trading 穩定化"]:::backlog
        P1["P1: Swappable Architecture"]:::backlog
        P2["P2: Monitoring & Safety"]:::backlog
    end

    P0 -->|"人類選定"| EP1["EP<br/>Session A<br/>Backlog: P0-1, P0-2<br/>UCs: 🆕, TD-01"]:::ep
    P0 -->|"人類選定"| EP2["EP<br/>Session B<br/>Backlog: P0-3<br/>UCs: RP-04"]:::ep

    EP1 -->|"完成"| UC1["USE-CASES.md 更新<br/>🆕→✅, TD-01 擴展"]:::uc
    EP2 -->|"完成"| UC2["USE-CASES.md 更新<br/>RP-04 📋→✅"]:::uc

    UC1 -->|"backlog 狀態連動"| BACKLOG
    UC2 -->|"backlog 狀態連動"| BACKLOG

    P1 -.->|"P0 Phase Gate"| EP3["EP<br/>Session C"]:::ep
```

---

## Session 內的 Compact 分佈

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
    classDef phase fill:#16213e,stroke:#2ecc71,color:#e0e0e0,stroke-width:2px
    classDef compact fill:#3e3a1a,stroke:#f1c40f,color:#e0e0e0,stroke-width:2px

    subgraph SESSION["Session 時間線"]
        direction LR
        P1["/execution-plan"]:::phase
        C1["/compact"]:::compact
        P2["/build<br/>seg 1-2"]:::phase
        C2["/compact"]:::compact
        P3["/build<br/>seg 3-4"]:::phase
        C3["/compact"]:::compact
        P4["/code-review"]:::phase
    end

    P1 --> C1 --> P2 --> C2 --> P3 --> C3 --> P4

    C3 -.->|"或：context 變怪"| STOP["🛑 更新 EP<br/>開新 Session"]:::phase
```

---

## ⚠️ 問題點 & ✅ 運作良好的部分

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart TD
    classDef pain fill:#3e1a1a,stroke:#e74c3c,color:#ffcccc,stroke-width:2px
    classDef ok fill:#1a3e2e,stroke:#27ae60,color:#e0e0e0,stroke-width:2px

    PAIN1["⚠️ EP ↔ UC-BACKLOG 未綁定<br/>無法查詢「P0-1 做了幾個 EP」"]:::pain
    PAIN2["⚠️ 跨 Session 接續<br/>依賴人類記憶口述進度"]:::pain

    OK1["✅ 預設一個 EP = 一個 Session<br/>model 退化可跨 Session 接續"]:::ok
    OK2["✅ Worktree 三 slot + trunk rebase<br/>單向 onto main，ff-only 吸收"]:::ok
    OK3["✅ Review 用平行 session<br/>Writer/Reviewer 分離"]:::ok
    OK4["✅ Model 變怪就更新 EP 重開<br/>不硬撐，務實"]:::ok
    OK5["✅ UC-BACKLOG + UC-Driven<br/>Local-first，無外部依賴"]:::ok
```
