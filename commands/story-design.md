# Story Design Command - 整合式專案設計系統

為軟體開發專案提供**從專案啟動到技術設計的完整解決方案**，整合專案規劃、User Story 挖掘、系統分析與架構設計，採用**漸進式發現**方法，確保專案目標與技術方案完全一致。

**🚨 重要**: 此命令提供一站式服務，從專案啟動到技術實作的完整流程。純技術優化請使用 `/analysis-plan` 和 `/design-plan`。

## 📖 OpenSpec 完整指導 (AI 必讀)

### **什麼是 OpenSpec？**

OpenSpec 是一個結構化規範格式系統，用於標準化技術文檔的編寫。**即使您從未聽說過 OpenSpec，本命令也提供完整的使用指導**。

#### **OpenSpec 核心特點**
- **結構化格式**: 使用固定的標題結構確保一致性
- **可解析性**: 工具可以自動解析和驗證
- **明確性**: 使用 SHALL 語言明確陳述需求
- **驗證機制**: 內建驗證和錯誤修復指導

### **🚨 OpenSpec 結構化格式 (強制要求)**

本命令**必須**遵循以下 OpenSpec 結構化格式：

#### **基本結構模式**
```markdown
### Requirement: [需求名稱]

[需求描述 SHALL 陳述]

#### Scenario: [場景描述]

- **GIVEN** [初始狀態] (可選)
- **WHEN** [條件或觸發]
- **THEN** [預期結果]
- **AND** [額外結果或條件]
```

#### **📝 撰寫規範 (必須遵守)**

**1. Requirement 標題規範**
```markdown
# ✅ 正確格式
### Requirement: User Story Analysis

# ❌ 錯誤格式
### User Story Analysis
## Requirement: User Story Analysis
#### Requirement: User Story Analysis
```

**2. SHALL 語言規範**
```markdown
# ✅ 正確：使用 SHALL 明確陳述
系統 SHALL 提供清晰的 Executive Summary，明確專案目標、核心價值和成功標準。

# ❌ 錯誤：避免使用模糊語言
系統應該提供清晰的 Executive Summary...
系統需要提供清晰的 Executive Summary...
系統可以提供清晰的 Executive Summary...
```

**3. Scenario 結構規範**
```markdown
# ✅ 正確：使用 WHEN/THEN/AND 結構
#### Scenario: Defining project scope and value
- **GIVEN** a clear understanding of the business problem
- **WHEN** defining the project scope
- **THEN** the Executive Summary SHALL include:
  - **專案目標**: 明確可衡量的目標陳述
  - **核心價值**: 為用戶和業務創造的具體價值
- **AND** each goal SHALL be measurable and time-bound

# ❌ 錯誤：不使用結構化格式
#### Scenario: Defining project scope and value
定義專案範圍時，應包含專案目標和核心價值。
```

### **🔍 OpenSpec 驗證機制**

#### **預驗證檢查清單**
每個完成的需求都必須通過以下檢查：

```markdown
# ✅ 檢查清單範例
## 預驗證檢查清單
- [ ] 使用 `### Requirement:` 標題格式
- [ ] Requirement 描述包含 SHALL 陳述
- [ ] 每個 Requirement 都有對應的 Scenario
- [ ] Scenario 使用 `#### Scenario:` 標題
- [ ] Scenario 包含 WHEN/THEN/AND 結構
- [ ] 沒有語法錯誤或格式問題
```

#### **錯誤修復指導**
當驗證失敗時，提供具體修復步驟：

```markdown
# ✅ 錯誤修復指導範例
## 錯誤修復指導

**問題**: 缺少 SHALL 陳述
**修復步驟**:
1. 在 Requirement 描述中添加 SHALL 陳述
2. 範例：`系統 SHALL 提供用戶驗證機制`
3. 避免使用「應該」、「需要」等模糊詞語

**問題**: Scenario 結構不正確
**修復步驟**:
1. 使用 `#### Scenario:` 標題
2. 採用 WHEN/THEN/AND 結構
3. 每個步驟使用粗體關鍵字
```

### **📋 OpenSpec 最佳實踐**

#### **需求編寫最佳實踐**
```markdown
# ✅ 好的範例
### Requirement: Comprehensive User Analysis

系統 SHALL 進行全面的用戶分析，確保深度理解用戶需求和使用場景。

#### Scenario: Analyzing user requirements

- **GIVEN** access to user requirements and business context
- **WHEN** performing comprehensive user analysis
- **THEN** the analysis SHALL include:
  - **使用者背景**: 詳細的用戶角色和背景分析
  - **核心痛點**: 具體問題描述和影響分析
  - **期望目標**: 理想解決方案的完整描述
- **AND** each component SHALL be based on actual user feedback and data
```

#### **常見錯誤避免**
```markdown
# ❌ 避免的錯誤
1. 混用標題級別 (### 和 #### 混亂使用)
2. 不使用 SHALL 語言
3. Scenario 缺少 WHEN/THEN/AND 結構
4. Requirement 和 Scenario 之間缺少對應關係
5. 描述過於模糊或主觀
```

### **🎯 本命令的 OpenSpec 應用**

本命令將 OpenSpec 格式應用於：
- **SD1-SD4 設計階段**: 每個階段都有結構化的 Requirements 和 Scenarios
- **驗證機制**: 確保設計品質和一致性
- **錯誤修復**: 提供具體的問題解決方案
- **交付物標準**: 明確的完成檢查清單

**🔥 重要提醒**: 即使您完全不熟悉 OpenSpec，只要遵循本命令提供的範例和模板，就能產出符合 OpenSpec 標準的高品質設計文檔。

## 使用方式
```bash
/story-design "專案描述或需求"
```

## 🎯 Story Design 整合式設計定位

### **核心受眾** (整合設計)
- **AI (Claude)**: 執行整合式專案規劃與技術設計的主要執行者
  - 需要：專案管理能力 + User Story 挖掘技巧 + SA/SD 分析能力 + 互動協作機制
  - 目標：從專案啟動到技術實作的完整解決方案
  - 約束：每個關鍵節點必須確認，確保專案目標與技術方案一致
- **User (你) 專案協作者**: 專案決策者和最終驗證者
  - 需要：清晰的專案目標、業務需求、成功標準定義
  - 目標：獲得從規劃到實作的完整解決方案
  - 價值：參與整個專案生命週期，確保成果符合實際需求

### **核心價值**
- **一站式服務**: 從專案總體規劃到技術設計的完整流程
- **專案總體規劃**: Executive Summary、目標定義、價值主張
- **User Story 深度挖掘**: 結構化方法深度理解用戶真實需求
- **漸進式發現**: 4階段確認，確保每個決策點都正確
- **SA/SD 完整整合**: 一次性完成從需求到技術的完整設計
- **互動式協作**: AI-User 深度協作，共同打造最佳方案
- **SDE 執行規劃**: 完整的專案執行策略和里程碑規劃

### **🎭 4-Stage 設計流程 (基於 OpenSpec 清晰命名)**

**執行流程**: SD1 (專案探索) → SD2 (系統分析) → SD3 (架構設計) → SD4 (最終確認)

#### **階段設計原則**
- **SD 專業導向**: 每個階段都體現系統設計師的專業價值
- **漸進式發現**: 分階段確認，避免一次性分析造成方向偏差
- **User Story 核心**: 所有技術決策都回歸到用戶故事
- **完整交付**: 每個階段都有具體的交付成果

#### **適用情境**
- ✅ **新專案啟動**: 需要完整規劃和技術設計的新專案
- ✅ **複雜功能開發**: 需要深度規劃和技術實現的複雜功能
- ✅ **系統重構**: 需要全面評估和重新設計的系統重構
- ✅ **業務轉型**: 需要技術支援的業務變革項目

**不適用於**：
- ❌ **純技術優化**: 沒有明確專案目標的技術改進
- ❌ **緊急修復**: 需要快速解決的技術問題
- ❌ **小型功能**: 簡單功能可直接使用其他命令

---

## 📚 專業知識庫 (強制自動載入)

🚨 **必須按順序載入以下核心文檔：**
1. CLAUDE.md - 專案約束和環境配置
2. session_notes.md - 當前任務狀態和歷史記錄
3. docs/ai_support/core/architect_comprehensive_guide.md - SA/SD 方法論指導

## 🎯 專案整合式發現方法論核心

### **專案總體規劃的戰略地位**
專案總體規劃在整合式發展中是**所有決策的基礎**：

- **專案目標基礎**: 深度定義專案目標、範圍、成功標準
- **User Story 指導**: 所有 User Story 都必須支援專案總體目標
- **技術方向導向**: 技術方案必須回歸到專案戰略目標
- **資源配置基準**: 所有決策都必須考慮專案資源約束

### **🚨 4-Stage 漸進式發現機制** (基於 OpenSpec 設計)

**執行流程**: SD1 (專案探索) → SD2 (系統分析) → SD3 (架構設計) → SD4 (最終確認)

#### **階段定義原則**
- **SD 專業導向**: 每個階段體現系統設計師的專業價值
- **漸進式發現**: 分階段確認，避免一次性分析造成方向偏差
- **User Story 核心**: 所有技術決策都回歸到用戶故事
- **完整交付**: 每個階段都有具體的交付成果

## 🎭 User Story 挖掘方法論

### **User Story 的戰略地位**
User Story 在專案執行中是**技術決策的基礎**：

- **需求理解基礎**: 深度挖掘用戶背景、痛點、期望
- **方案設計導向**: 所有技術方案都必須回歸到 User Story
- **成功標準定義**: 明確什麼是「成功的解決方案」
- **驗證基準**: 所有設計决策都必須能夠解決具體的用戶問題

## 🏗️ 4-Stage Story Design 標準結構

### **SD1: 專案探索 (Project Discovery)**

#### **🎯 專案啟動與總體規劃**
基於 AI-User 互動協作，建立專案的整體框架：

##### **Executive Summary (專案概覽)**
- **專案目標**: 明確的專案目標和成功標準
- **核心價值**: 專案為用戶和業務帶來的主要價值
- **技術創新點**: 專案的技術亮點和創新之處
- **複雜度評估**: Simple/Medium/Complex，決定後續執行策略

##### **User Story 深度挖掘**
- **用戶背景分析**: 誰是使用者？他們的角色和職責是什麼？
- **痛點深度挖掘**: 具體遇到什麼問題？為什麼這是個問題？
- **期望目標定義**: 理想的解決方案應該是什麼樣？
- **業務場景分析**: 在什麼情況下會遇到這個問題？
- **成功標準確認**: 怎樣才算問題被成功解決？

##### **執行策略規劃**
- **SD2 (系統分析)**: 系統理解、需求分析、技術可行性評估
- **SD3 (架構設計)**: 系統架構設計、技術方案制定
- **段落式實作**: 功能分段實作、Examples驗證、品質保證

#### **🔍 關鍵確認點 SD1: 專案探索確認**
```
基於我們的討論，這是專案的整體規劃：

**專案目標**: [明確的專案目標]
**核心價值**: [為用戶和業務帶來的價值]
**User Story**: [深度挖掘的用戶故事]
**執行策略**: [SD2 → SD3 → 實作規劃]
**複雜度評估**: [Simple/Medium/Complex]

請確認：
1. 這個專案總體規劃是否符合您的期望？
2. User Story 理解是否正確？
3. 可以繼續進行 SD2 系統分析嗎？
```

### **SD2: 系統分析 (System Analysis)**

#### **🔍 現有系統理解**
基於 User Story 進行系統現況分析：

##### **預查證清單設計**
- **User Story 導向**: 根據具體需求制定查證範圍
- **現有資源評估**: 評估現有系統的可用性和限制
- **技術約束識別**: 識別可能影響方案的技術約束
- **批量讀取計劃**: 優化 context 使用效率

##### **DFD 數據流分析**
- **業務流程映射**: 將 User Story 轉化為數據流圖
- **系統邊界定義**: 明確什麼需要新開發，什麼可以重用
- **外部實體識別**: 識別與系統互動的外部角色
- **數據流向分析**: 理解數據在系統中的流動路徑

#### **🗂️ 數據結構設計**

##### **概念 ERD (業務理解)**
基於 User Story 識別核心業務實體：
- **主要實體**: 用戶、數據、策略、結果等
- **實體關係**: 1:N、N:M 等業務關係
- **業務規則**: 實體間的約束和規則

##### **實作 ERD - 檔案結構設計**
```
[project_name]/
├── entities/                           # 數據實體定義層
│   ├── __init__.py
│   ├── [entity1].py                    # 核心業務實體
│   │   └── class [Entity1]:            # 基於 User Story 的屬性設計
│   │       ├── [field1]: [Type]        # 解決痛點的關鍵屬性
│   │       └── [field2]: [Type]        # 支援業務場景的屬性
│   └── [entity2].py                    # 相關實體
├── repositories/                       # 數據存取層
│   ├── [entity1]_repository.py         # 實體 CRUD 操作
│   └── [entity2]_repository.py
└── services/                          # 業務邏輯層
    ├── [core_business]_service.py      # User Story 核心邏輯
    └── [integration]_service.py        # 系統整合邏輯
```

#### **🔍 關鍵確認點 SD2: 系統分析確認**
```
基於對系統的分析，我發現：

**可重用組件**: [現有可用組件]
**需要開發部分**: [必須新開發的功能]
**技術約束**: [主要技術限制]
**數據結構**: [ERD 設計結果]
**整合點**: [與現有系統的整合方式]

這個系統分析是否符合您的預期？需要調整分析範圍嗎？
```

### **SD3: 架構設計 (Architecture Design)**

#### **🏗️ 系統架構設計**
基於 User Story 和系統分析結果：

##### **分層架構設計**
- **應用層**: 直接支援 User Story 的介面層
- **業務邏輯層**: 實現核心業務邏輯的服務層
- **數據服務層**: 處理數據存取和整合的服務層
- **基礎設施層**: 支援系統運行的基礎組件

##### **🚨 Pseudo Code 設計藍圖** (核心交付物)
```python
# [project_name]/[module]/[business_component].py

class [BusinessComponent]:
    """
    User Story: [對應的用戶故事描述]
    設計意圖: [解決什麼痛點，支援什麼業務場景]
    架構位置: [在分層架構中的位置和職責]
    依賴模組: [具體依賴的其他模組]
    """

    def __init__(self, config: Dict[str, Any]):
        """
        設計意圖: [初始化邏輯和依賴注入]
        Call Stack: __init__ -> _validate_config -> _setup_dependencies
        User Story 支援: [如何支援用戶故事]
        """
        # 基於 User Story 的初始化邏輯
        pass

    def core_business_method(self, params: ParamType) -> ResultType:
        """
        設計意圖: [核心業務功能，直接解決用戶痛點]
        Call Stack: core_business_method -> _step1 -> _step2 -> _validate_result
        User Story 支援: [具體支援用戶故事的哪個部分]
        業務價值: [為用戶創造什麼價值]
        架構考量: [設計決策和技術原因]
        整合說明: [與其他模組的整合方式]
        """
        # 核心業務邏輯的 pseudo code
        result1 = self._step1(params)      # 步驟1：處理用戶輸入
        result2 = self._step2(result1)     # 步驟2：核心業務邏輯
        return self._validate_result(result2)  # 步驟3：結果驗證

    def _step1(self, data: InputType) -> IntermediateType:
        """
        Call Stack: _step1 -> DataService.process -> Validation.check
        User Story 支援: [支援用戶故事的哪個子場景]
        """
        # 具體實現邏輯的 pseudo code
        pass
```

##### **模組間調用關係展示**
```python
# 展示不同模組間的實際調用關係
# 替代抽象的模組依賴圖

# UI Layer調用Business Layer
ui_result = StrategyEngine.execute_strategy(strategy_config)

# Business Layer調用Service Layer
data = DataGateway.load_bars(instruments, time_range)

# Service Layer調用Infrastructure Layer
cached_data = CacheManager.get(cache_key)
```

#### **🔗 用戶故事與技術方案關聯**

##### **技術故事分解**
- **US-001**: [用戶故事 1 的技術實現方案]
  - 實作複雜度: [高/中/低]
  - 依賴模組: [相關依賴]
  - 驗證方式: [Examples 設計]
- **US-002**: [用戶故事 2 的技術實現方案]
  - 實作複雜度: [高/中/低]
  - 依賴模組: [相關依賴]
  - 驗證方式: [Examples 設計]

##### **Examples 設計**
- **basic_usage.py**: 基本使用場景驗證 (P0)
- **integration.py**: 系統整合驗證 (P1)
- **error_handling.py**: 錯誤處理驗證 (P1)

#### **🔍 關鍵確認點 SD3: 架構設計確認**
```
基於 User Story 和前面的分析，我設計了以下技術架構：

**系統架構**: [分層架構設計]
**核心組件**: [解決痛點的核心組件設計]
**技術選型**: [基於需求的技术選擇]
**整合方案**: [與現有系統的整合方式]
**Pseudo Code**: [完整的實作藍圖]

這個技術架構是否能有效解決您的問題？
```

### **SD4: 最終確認 (Final Confirmation)**

#### **✅ 完整設計方案確認**
整合前面所有階段的結果：

##### **技術方案總結**
- **User Story 完整支援**: [如何完整解決用戶問題]
- **技術方案優勢**: [相比其他方案的優勢]
- **實作可行性**: [技術實作的可行性評估]

##### **段落式實作規劃**
- **開發優先級**: [P0-P2 的優先級分級]
- **段落策略**: [如何將技術故事分解為獨立段落]
- **驗證計劃**: [每個段落的驗證方式]
- **整合時機**: [段落間的整合時機]

#### **🔍 關鍵確認點 SD4: 最終設計方案確認**
```
這是完整的解決方案設計：

**技術方案總結**: [簡潔的方案概述]
**User Story 支援**: [如何完整解決用戶問題]
**實作計劃**: [段落式實作建議]
**成功標準**: [如何驗證方案成功]

請確認：
1. 這個方案是否完全解決了您的問題？
2. 有沒有需要調整的地方？
3. 可以開始段落式實作了嗎？
```

## 🔄 4-Stage 執行指導 (基於 OpenSpec 最佳實踐)

### **🚨 強制關鍵確認點機制**
**禁止跳過任何確認點，每個階段完成後必須獲得用戶確認才能繼續：**

#### **SD1: 專案探索** (必須確認)
- **🎯 目標**: 專案總體規劃、User Story 深度挖掘、執行策略制定
- **📋 交付**: Executive Summary + User Story 分析 + SD2-SD4 規劃
- **🔍 USER REVIEW**: 專案目標正確性，User Story 理解正確性
- **⚠️ 必須確認才能進入 SD2**

#### **SD2: 系統分析** (必須確認)
- **🎯 目標**: 現有系統理解、DFD 分析、數據結構設計
- **📋 交付**: 系統分析報告 + DFD 圖 + ERD 設計 + 查證清單結果
- **🔍 USER REVIEW**: 系統理解正確性，分析範圍適當性，數據設計合理性
- **⚠️ 必須確認才能進入 SD3**

#### **SD3: 架構設計** (必須確認)
- **🎯 目標**: 系統架構設計、Pseudo Code 藍圖、技術選型
- **📋 交付**: 系統架構圖 + Pseudo Code 設計 + 技術故事分解
- **🔍 USER REVIEW**: 技術方案可行性，架構設計正確性
- **⚠️ 必須確認才能進入 SD4**

#### **SD4: 最終確認** (最終確認)
- **🎯 目標**: 完整方案確認、段落式實作規劃
- **📋 交付**: 完整設計文檔 + 實作計劃 + Examples 設計
- **🔍 USER REVIEW**: 方案完整性，實作可行性
- **✅ 全部完成標準**: 所有 4 個確認點都通過

## 📊 Story Design 輸出標準

### **🚨 強制要求：單一 Story Design 文檔**

**核心原則**:
- ✅ **必須產生單一 Story Design 文檔**，不得分散成多個文檔
- ✅ **文檔命名**: `[project_name]_story_design.md`
- ✅ **文檔位置**: `docs/design/` 目錄
- ✅ **包含完整 SA+SD 內容**: 從 User Story 到技術方案的完整鏈路
- ❌ **禁止產出**: 多個分散的分析、設計文檔

**執行彈性**:
- ⚠️ **允許中介思考**: 過程中可以產生臨時筆記幫助組織思路
- ✅ **最終必須整合**: 最後必須整合為單一完整文檔
- ✅ **清理臨時文檔**: 整合完成後清理所有臨時文檔

### **Story Design 標準結構 (基於 OpenSpec 結構化格式)**

**🚨 重要**: 此文檔格式採用 OpenSpec 結構化規格式，確保解析一致性和工具相容性。

```markdown
# Story Design - [專案名稱]

## Purpose

本 Story Design 文檔定義了 [專案簡要描述] 的完整技術解決方案，基於 4-Stage 設計流程 (SD1-SD4)，為 execution-plan 提供實作所需的完整資訊。

## SD1: 專案探索 Requirements

### Requirement: Executive Summary Definition

專案 SHALL 提供清晰的 Executive Summary，明確專案目標、核心價值和成功標準。

#### Scenario: Defining project scope and value

- **GIVEN** a clear understanding of the business problem
- **WHEN** defining the project scope
- **THEN** the Executive Summary SHALL include:
  - **專案目標**: 明確可衡量的目標陳述
  - **核心價值**: 為用戶和業務創造的具體價值
  - **技術創新點**: 專案的技術亮點和創新之處
  - **複雜度評估**: Simple/Medium/Complex 等級決定
  - **成功標準**: 可驗證的成功條件

### Requirement: User Story Deep Analysis

系統 SHALL 深度分析 User Story，確保完全理解用戶背景、痛點和期望。

#### Scenario: Conducting User Story analysis

- **GIVEN** access to user requirements and context
- **WHEN** performing User Story analysis
- **THEN** the analysis SHALL include:
  - **使用者背景**: 詳細的用戶角色和背景分析
  - **核心痛點**: 具體問題描述和影響分析
  - **期望目標**: 理想解決方案的完整描述
  - **成功標準**: 可測量的成功標準定義
  - **業務場景**: 具體使用場景和工作流程

### Requirement: Execution Strategy Planning

系統 SHALL 制定明確的執行策略，規劃 SD2-SD4 的具體實施路徑。

#### Scenario: Planning execution strategy

- **GIVEN** completed project analysis and User Story understanding
- **WHEN** defining execution strategy
- **THEN** the strategy SHALL include:
  - **SD2 (系統分析)**: 系統理解、需求分析、技術可行性評估計劃
  - **SD3 (架構設計)**: 系統架構設計、技術方案制定計劃
  - **段落式實作**: 功能分段實作、Examples驗證、品質保證計劃

## SD2: 系統分析 Requirements

### Requirement: System Analysis and DFD Design

系統 SHALL 進行全面的系統分析，生成清晰的數據流圖和現狀評估。

#### Scenario: Analyzing current system architecture

- **GIVEN** access to existing system documentation and codebase
- **WHEN** performing system analysis
- **THEN** the analysis SHALL produce:
  - **DFD 數據流圖**: 展示數據在系統中的流動路徑
  - **現有系統分析**: 可重用組件、需要開發部分、技術約束評估
  - **整合點識別**: 與現有系統的整合方式和介面定義

### Requirement: Entity Relationship Design

系統 SHALL 基於 User Story 設計完整的實體關係模型和檔案結構。

#### Scenario: Creating ERD and file structure

- **GIVEN** defined User Story and system requirements
- **WHEN** designing data structures
- **THEN** the ERD design SHALL include:
  - **概念 ERD**: 核心業務實體和關係定義
  - **實作 ERD**: 完整的檔案目錄結構設計
  - **類別空殼**: 基礎 class 定義和屬性設計

## SD3: 架構設計 Requirements

### Requirement: System Architecture Design

系統 SHALL 設計完整的系統架構，包括分層結構和組件互動。

#### Scenario: Designing technical architecture

- **GIVEN** completed system analysis and ERD design
- **WHEN** creating system architecture
- **THEN** the architecture SHALL include:
  - **系統架構圖**: 完整的分層架構設計
  - **Pseudo Code 藍圖**: 詳細的實作設計藍圖
  - **模組調用關係**: 具體的組件間互動方式

### Requirement: Technical Story Decomposition

系統 SHALL 將 User Story 分解為可執行的技術故事，為段落式實作奠定基礎。

#### Scenario: Breaking down implementation tasks

- **GIVEN** complete architecture design and User Story requirements
- **WHEN** creating technical stories
- **THEN** each technical story SHALL include:
  - **US-ID**: 唯一識別符和描述
  - **實作複雜度**: 高/中/低複雜度評估
  - **依賴模組**: 相關依賴和整合需求
  - **驗證方式**: Examples 設計和測試策略

## SD4: 最終確認 Requirements

### Requirement: Final Design Validation

系統 SHALL 進行最終設計確認，確保方案的完整性和可行性。

#### Scenario: Validating complete solution

- **GIVEN** completed SD1-SD3 design work
- **WHEN** performing final validation
- **THEN** the validation SHALL confirm:
  - **User Story 完整支援**: 如何完整解決用戶問題
  - **技術方案優勢**: 相比其他方案的比較優勢
  - **實作可行性**: 技術實作的可行性評估
  - **execution-plan 就緒**: 確認包含實作所需所有資訊

### Requirement: Implementation Planning

系統 SHALL 制定詳細的段落式實作計劃，為 execution-plan 提供完整指導。

#### Scenario: Planning phased implementation

- **GIVEN** validated technical design
- **WHEN** creating implementation plan
- **THEN** the plan SHALL include:
  - **開發優先級**: P0-P2 的優先級分級
  - **段落策略**: 技術故事分解為獨立段落的方式
  - **驗證計劃**: 每個段落的具體驗證方式
  - **整合時機**: 段落間的整合和測試時機

## Execution Plan 智能分析資訊

### Requirement: File Impact Analysis

系統 SHALL 提供完整的檔案影響分析，支援 execution-plan 的智能分析。

#### Scenario: Analyzing implementation impact

- **GIVEN** complete technical design
- **WHEN** performing file impact analysis
- **THEN** the analysis SHALL include:
  - **關鍵檔案**: 需要修改的主要檔案清單 (3-5個)
  - **新增檔案**: 需要新建的檔案列表
  - **依賴關係**: 檔案間的依賴和調用關係
  - **向後相容性**: 現有 API 的相容性考量

### Requirement: Implementation Template Generation

系統 SHALL 提供實作模板生成基礎，支援 execution-plan 的自動化實作。

#### Scenario: Creating implementation templates

- **GIVEN** complete Pseudo Code and architecture design
- **WHEN** generating implementation templates
- **THEN** the templates SHALL include:
  - **核心類別**: 主要實作類別的設計藍圖
  - **API 介面**: 需要實現的方法簽名
  - **Call Stack**: 完整的函數調用鏈
  - **錯誤處理**: 驗證策略和錯誤處理設計
```

### **🚨 OpenSpec 結構化格式要求**
**Story Design 必須遵循 OpenSpec 結構化格式**：

1. **使用 `### Requirement:` 和 `#### Scenario:` 結構**
2. **採用 SHALL 語言明確陳述需求**
3. **使用 WHEN/THEN/AND 結構化場景步驟**
4. **確保每個需求都有對應的驗證場景**

### **🚨 execution-plan 相容性要求**
**Story Design 必須確保 execution-plan 能夠進行智能分析：**

1. **完整的 Pseudo Code**: 提供足夠詳細的程式碼設計藍圖
2. **明確的 Call Stack**: 展示完整的函數調用關係
3. **檔案結構清晰**: 明確的新建/修改檔案清單
4. **技術故事分解**: 便於 execution-plan 進行功能段落規劃
5. **Examples 設計**: 為 execution-plan 的驗證機制提供基礎
6. **整合資訊**: 與現有專案架構的整合方式
7. **驗證策略**: 明確的錯誤處理和驗證方式

## 🚨 專案特定約束模板

### **Story Design 專用約束**
- **User Story 優先**: 所有技術決策必須回歸到 User Story
- **漸進式確認**: 每個關鍵節點都必須獲得用戶確認
- **實際代碼驗證**: SA 分析必須基於實際代碼查證
- **整合導向**: 設計必須考慮與現有專案架構的整合

### **通用架構約束**
- **遵循現有架構**: 必須符合專案的架構設計原則
- **使用統一組件**: 優先重用現有模組和組件
- **遵循日誌規範**: 使用專案標準的日誌系統
- **符合測試標準**: 使用專案指定的測試框架

### **互動式確認約束**
- **禁止跳過確認**: 任何情況下都不得跳過關鍵確認點
- **清晰表達**: 確認問題必須清晰易懂，避免技術術語
- **耐心等待**: 給用戶足夠時間思考和回饋
- **及時調整**: 根據用戶回饋立即調整分析方向

## 📋 Story Design 品質檢查

### **User Story 分析完整性**
- [ ] User Story 描述清晰具體
- [ ] 痛點分析深入準確
- [ ] 成功標準可測量
- [ ] 業務場景覆蓋完整

### **SA 分析品質**
- [ ] 預查證清單基於 User Story 制定
- [ ] DFD 分析完整展示數據流動
- [ ] 現有系統分析準確
- [ ] 整合方案可行

### **SD 設計品質**
- [ ] 系統架構符合 User Story 需求
- [ ] Pseudo Code 設計清晰可執行
- [ ] Call Stack 展示完整
- [ ] 技術選型合理

### **整體一致性**
- [ ] SA-SD 設計一致性
- [ ] User Story 貫穿整個設計
- [ ] 技術方案能有效解決痛點
- [ ] 實作計劃清晰可行

## 🔧 輸出和後續行動

Story Design 完成後：

### **直接輸出**
1. **設計文檔路徑**: 完整的 Story Design 文檔位置 (`docs/design/[project_name]_story_design.md`)
2. **User Story 支援總結**: 如何完整解決用戶問題
3. **技術方案概述**: 核心技術方案和架構設計
4. **execution-plan 就緒確認**: 確認文檔包含 execution-plan 所需的所有資訊

### **後續行動建議**
- **🚀 立即實作**: 使用 `/execution-plan` 基於 Story Design 進行智能分析和段落式實作規劃
- **Module Expert 協作**: 與相關領域專家討論具體實作細節
- **迭代優化**: 根據實作過程中的發現進行設計調整

### **session_notes更新**
- 記錄 Story Design 的關鍵決策和 User Story 分析
- 更新 4 個關鍵確認點的結果
- 記錄 User Story 到技術方案的完整映射關係
- 標註為 execution-plan 準備的設計文檔

### **與其他命令的整合**
- **execution-plan**: Story Design 的直接下游，基於設計文檔進行實作規劃
- **/impl**: execution-plan 生成後，由 /impl 執行具體的 Examples 驅動實作
- **/sasd**: 在複雜情況下，可回溯使用 /sasd 進行更深入的架構分析

---

**重要提醒**:
- 此命令專注於**故事驅動的系統架構設計**，通過漸進式發現確保方案正確性
- **🚨 輸出文檔專為 `/execution-plan` 智能分析設計**，確保包含實作所需的所有關鍵資訊
- **純技術分析**請繼續使用 `/analysis-plan` 和 `/design-plan`
- **執行鏈路**: `/story-design` → `/execution-plan` → `/impl`

**🚨 強制要求**:
- 必須完成所有 4 個關鍵確認點才能完成設計
- **🚨 User Story 必須貫穿整個設計過程**，所有技術決策都必須回歸到 User Story
- **🚨 輸出必須符合 execution-plan 格式要求**，包含智能分析所需的所有資訊
- **🚨 檔案結構 ERD 和 Pseudo Code 設計藍圖為核心交付物**
- **🚨 必須產生單一 Story Design 文檔**，包含完整的 SD1-SD4 設計內容
- 必須基於實際代碼查證進行 SD2 系統分析
- 必須使用 mermaid 圖表並確保 Dark Theme 相容性
- 必須遵循 4-Stage 漸進式發現方法，不得跳過任何確認點

**🔄 推薦工作流程**:
1. **4-Stage 設計**: 使用 `/story-design` 進行 SD1→SD2→SD3→SD4 完整設計
2. **智能實作規劃**: 使用 `/execution-plan` 基於 Story Design 文檔進行段落式實作規劃
3. **Examples 驅動實作**: 使用 `/impl` 執行具體的功能實作