# Claude Code Sub-Agents 系統完整視覺化解釋

## 1. 系統架構圖

```mermaid
graph TB
    subgraph "Claude Code 生態系統"
        A[使用者 User] -->|輸入指令| B[Claude Code 主系統]
        B -->|任務分析| C{任務類型判斷}
    end

    subgraph "預設 Agents"
        D[general-purpose]
        E[Explore]
        F[Plan]
        G[test-generator]
        H[claude-code-guide]
    end

    subgraph "專業化 Sub-Agents"
        I[content-analyzer<br/>內容分析師]
        J[content-processor<br/>內容處理器]
        K[context-analyzer<br/>上下文分析師]
        L[structure-analyzer<br/>結構分析師]
        M[verification-expert<br/>驗證專家]
        N[visualization-specialist<br/>視覺化專家]
        O[report-coordinator<br/>報告協調器]
    end

    subgraph "工具生態"
        P[Read 工具]
        Q[Write 工具]
        R[Edit 工具]
        S[Grep 工具]
        T[Glob 工具]
        U[Bash 工具]
        V[WebFetch 工具]
    end

    C -->|一般程式開發| D
    C -->|代碼搜索分析| E
    C -->|規劃設計| F
    C -->|測試生成| G
    C -->|功能指導| H

    C -->|內容深度分析| I
    C -->|內容處理優化| J
    C -->|背景上下文理解| K
    C -->|架構結構分析| L
    C -->|驗證檢查| M
    C -->|視覺化設計| N
    C -->|多Agent協調| O

    I --> P
    I --> S
    I --> T

    J --> P
    J --> Q
    J --> R
    J --> T

    K --> P
    K --> S
    K --> U
    K --> V

    L --> P
    L --> S
    L --> T
    L --> U

    M --> P
    M --> S
    M --> T
    M --> U

    N --> P
    N --> Q
    N --> R

    O --> P
    O --> Q
    O --> R
    O --> T

    O -->|協調整合| I
    O -->|協調整合| J
    O -->|協調整合| K
    O -->|協調整合| L
    O -->|協調整合| M
```

## 2. Sub-Agent 創建流程圖

```mermaid
flowchart TD
    Start([開始]) --> A{需求分析}
    A -->|具體分析需求| B[定義 Agent 功能]
    A -->|複雜任務| C[拆解為多個 Agents]

    B --> D[設計工具配置]
    C --> D

    D --> E{選擇工具組合}
    E -->|讀取為主| F[Read + Grep + Glob]
    E -->|處理為主| G[Read + Write + Edit]
    E -->|系統操作| H[Bash + WebFetch]
    E -->|混合需求| I[完整工具集]

    F --> J[撰寫 Agent 規格]
    G --> J
    H --> J
    I --> J

    J --> K[定義使用場景]
    K --> L[設定工具限制]
    L --> M[建立輸出格式]
    M --> N[設定最佳實踐]
    N --> O{測試驗證}

    O -->|通過| P[部署 Agent]
    O -->|失敗| Q[調整規格]
    Q --> J

    P --> R[建立使用文檔]
    R --> End([完成])

    style Start fill:#4caf50,color:#fff
    style End fill:#2196f3,color:#fff
    style P fill:#ff9800,color:#fff
    style Q fill:#f44336,color:#fff
```

## 3. 代理類型對照表

### 專業化 Sub-Agents 功能對比

```mermaid
quadrantChart
    title Sub-Agents 功能定位分析
    x-axis "分析導向" --> "處理導向"
    y-axis "獨立運作" --> "協調整合"

    "content-analyzer": [0.8, 0.2]
    "content-processor": [0.3, 0.2]
    "context-analyzer": [0.7, 0.3]
    "structure-analyzer": [0.8, 0.2]
    "verification-expert": [0.6, 0.3]
    "visualization-specialist": [0.2, 0.4]
    "report-coordinator": [0.1, 0.9]
```

### 工具權限矩陣

```mermaid
graph LR
    subgraph "工具權限分配"
        Read[Read<br/>📖 讀取]
        Write[Write<br/>✍️ 寫入]
        Edit[Edit<br/>✏️ 編輯]
        Grep[Grep<br/>🔍 搜索]
        Glob[Glob<br/>📁 檔案匹配]
        Bash[Bash<br/>⚡ 命令執行]
        WebFetch[WebFetch<br/>🌐 網路獲取]
    end

    subgraph "分析型 Agents"
        CA[content-analyzer]
        CONA[context-analyzer]
        SA[structure-analyzer]
        VE[verification-expert]
    end

    subgraph "處理型 Agents"
        CP[content-processor]
        VS[visualization-specialist]
        RC[report-coordinator]
    end

    CA --> Read
    CA --> Grep
    CA --> Glob

    CONA --> Read
    CONA --> Grep
    CONA --> Bash
    CONA --> WebFetch

    SA --> Read
    SA --> Grep
    SA --> Glob
    SA --> Bash

    VE --> Read
    VE --> Grep
    VE --> Glob
    VE --> Bash

    CP --> Read
    CP --> Write
    CP --> Edit
    CP --> Glob

    VS --> Read
    VS --> Write
    VS --> Edit

    RC --> Read
    RC --> Write
    RC --> Edit
    RC --> Glob

    style CA fill:#e3f2fd
    style CONA fill:#e3f2fd
    style SA fill:#e3f2fd
    style VE fill:#e3f2fd
    style CP fill:#f3e5f5
    style VS fill:#f3e5f5
    style RC fill:#f3e5f5
```

## 4. 使用場景實例

### 場景一：文檔品質提升專案

```mermaid
sequenceDiagram
    participant U as 使用者
    participant M as Claude Code
    participant CA as content-analyzer
    participant CP as content-processor
    participant VE as verification-expert
    participant RC as report-coordinator
    participant VS as visualization-specialist

    U->>M: 執行文檔品質提升專案
    M->>CA: 分析現有文檔內容品質
    M->>CONA: 理解項目背景和歷史
    M->>SA: 檢查文檔結構組織

    par 並行分析
        CA->>CA: 深度內容分析
        CONA->>CONA: 背景上下文分析
        SA->>SA: 結構架構分析
    end

    CA->>RC: 提交內容分析報告
    CONA->>RC: 提交背景分析報告
    SA->>RC: 提交結構分析報告

    RC->>CP: 基於分析結果，啟動內容處理
    RC->>VE: 同時啟動驗證檢查

    par 處理與驗證
        CP->>CP: 內容蒸餾與優化
        VE->>VE: 語法與連結驗證
    end

    CP->>RC: 提交優化後內容
    VE->>RC: 提交驗證報告

    RC->>VS: 請求視覺化報告設計
    VS->>VS: 創建結構化報告
    VS->>RC: 提交視覺化報告

    RC->>M: 最終整合報告
    M->>U: 提供完整的品質提升方案
```

### 場景二：系統架構評估

```mermaid
graph TD
    A[系統架構評估需求] --> B{選擇適合的 Agents}

    B --> C[context-analyzer<br/>分析歷史演進]
    B --> D[structure-analyzer<br/>檢查當前架構]
    B --> E[content-analyzer<br/>評估文檔品質]

    C --> F[Git 歷史分析]
    C --> G[技術決策背景]

    D --> H[模組依賴分析]
    D --> I[架構模式識別]

    E --> J[技術文檔檢查]
    E --> K[程式碼一致性]

    F --> L[report-coordinator]
    G --> L
    H --> L
    I --> L
    J --> L
    K --> L

    L --> M[整合分析結果]
    M --> N[visualization-specialist]
    N --> O[架構視覺化報告]

    style A fill:#ff5722,color:#fff
    style O fill:#4caf50,color:#fff
    style L fill:#2196f3,color:#fff
```

## 5. 最佳實踐建議

### Sub-Agents 使用決策樹

```mermaid
flowchart TD
    Start([任務需求]) --> A{分析類型?}

    A -->|內容分析| B[content-analyzer]
    A -->|內容處理| C[content-processor]
    A -->|背景理解| D[context-analyzer]
    A -->|結構檢查| E[structure-analyzer]
    A -->|品質驗證| F[verification-expert]
    A -->|視覺化| G[visualization-specialist]
    A -->|多任務整合| H[report-coordinator]

    B --> I{需要深入處理?}
    C --> I
    D --> I
    E --> I
    F --> I
    G --> I

    I -->|是| J[啟動多 Agent 協作]
    I -->|否| K[單獨 Agent 完成]

    J --> L[report-coordinator 協調]
    L --> M[並行執行多 Agents]
    M --> N[整合結果]

    K --> O[直接輸出結果]
    N --> P[最終報告]
    O --> P
    P --> End([完成])

    style Start fill:#4caf50,color:#fff
    style End fill:#2196f3,color:#fff
    style J fill:#ff9800,color:#fff
    style L fill:#ff5722,color:#fff
```

### Agent 協作模式

```mermaid
graph TB
    subgraph "單獨執行模式"
        A1[單一任務] --> B1[選擇對應 Agent]
        B1 --> C1[獨立執行]
        C1 --> D1[直接輸出]
    end

    subgraph "序列協作模式"
        A2[複雜任務] --> B2[按順序啟動 Agents]
        B2 --> C2[Agent 1 輸出]
        C2 --> D2[Agent 2 處理]
        D2 --> E2[Agent 3 驗證]
        E2 --> F2[最終結果]
    end

    subgraph "並行協作模式"
        A3[大型專案] --> B3[同時啟動多 Agents]
        B3 --> C3[並行分析階段]
        C3 --> D3[report-coordinator 整合]
        D3 --> E3[綜合報告輸出]
    end
```

## 6. 效能優化建議

### 資源使用策略

```mermaid
pie
    title Sub-Agents 資源使用分布
    "Read 操作" : 40
    "Grep 搜索" : 25
    "Write/Edit" : 20
    "系統命令" : 10
    "網路請求" : 5
```

### 最佳實踐清單

```mermaid
mindmap
  root((Sub-Agents 最佳實踐))
    任務設計
      明確目標範圍
      選擇適當 Agent
      定義清晰輸出
    工具配置
      最小權限原則
      功能需求匹配
      安全性考量
    協作策略
      並行執行優化
      依賴關係管理
      結果整合規劃
    品質保證
      驗證機制建立
      錯誤處理流程
      效能監控指標
```

---

## 總結

Claude Code Sub-Agents 系統提供了一個專業化、模組化的 AI 協作框架。透過適當選擇和組合不同的專業化 agents，可以大幅提升複雜任務的執行效率和品質。關鍵在於理解每個 agent 的專長領域、工具限制，以及如何有效地協調它們的協作關係。