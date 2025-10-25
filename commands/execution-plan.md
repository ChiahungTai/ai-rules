# Execution Plan Command - 段落式實作計畫書生成器

為軟體開發專案生成**段落式實作計畫書**，基於 Story Design 的 4-Stage 設計成果，執行分段實作與品質保證，專為功能實現、Examples驅動開發和品質保證設計。

**🚨 重要**: 此命令基於 `/story-design` 的 SD1-SD4 成果生成實作計畫書，專注於段落式實作方法論。

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
### Requirement: Self-Contained Segment Structure

# ❌ 錯誤格式
### Self-Contained Segment Structure
## Requirement: Self-Contained Segment Structure
#### Requirement: Self-Contained Segment Structure
```

**2. SHALL 語言規範**
```markdown
# ✅ 正確：使用 SHALL 明確陳述
每個實作段落 SHALL 是完全獨立的，AI 只需讀取該段落就能完成實作。

# ❌ 錯誤：避免使用模糊語言
每個實作段落應該是完全獨立的...
每個實作段落需要是完全獨立的...
每個實作段落可以是完全獨立的...
```

**3. Scenario 結構規範**
```markdown
# ✅ 正確：使用 WHEN/THEN/AND 結構
#### Scenario: Creating self-contained implementation segments
- **GIVEN** technical story decomposition and implementation requirements
- **WHEN** designing self-contained segments
- **THEN** each segment SHALL include:
  - **段落概要**: Context 獨立的基礎資訊
  - **核心實作要點**: 基於智能分析的實作指導
  - **程式碼指導**: 可直接使用的實作框架
- **AND** each segment SHALL be independently executable

# ❌ 錯誤：不使用結構化格式
#### Scenario: Creating self-contained implementation segments
設計段落時，應包含概要、實作要點和程式碼指導。
```

### **🔍 OpenSpec 驗證機制 (Execution Plan 專用)**

#### **預驗證檢查清單**
Execution Plan 完成後必須通過以下檢查：

```markdown
## Execution Plan 預驗證檢查清單
- [ ] 使用 `### Requirement:` 標題格式
- [ ] 所有 Requirement 描述包含 SHALL 陳述
- [ ] 每個 Requirement 都有對應的 Scenario
- [ ] Scenario 使用 `#### Scenario:` 標題
- [ ] Scenario 包含 WHEN/THEN/AND 結構
- [ ] 功能段落設計為 Self-Contained
- [ ] 包含完整的 Examples 驗證策略
- [ ] 提供明確的完成檢查清單
```

#### **錯誤修復指導**
當驗證失敗時，提供具體修復步驟：

```markdown
## Execution Plan 錯誤修復指導

**問題**: 功能段落不夠 Self-Contained
**修復步驟**:
1. 確保每個段落包含完整的實作資訊
2. 添加檔案路徑和依賴關係說明
3. 提供具體的程式碼框架
4. 包含驗證方法和完成標準

**問題**: Examples 驗證不完整
**修復步驟**:
1. 為每個段落設計對應的 Examples
2. 明確 Examples 檔案路徑和名稱
3. 提供具體的驗證場景
4. 標註執行命令和預期結果
```

### **📋 Execution Plan 專用最佳實踐**

#### **功能段落設計最佳實踐**
```markdown
# ✅ 好的範例
### Requirement: Self-Contained Segment Structure

每個實作段落 SHALL 是完全獨立的，AI 只需讀取該段落就能完成實作。

#### Scenario: Creating self-contained implementation segments

- **GIVEN** technical story decomposition and implementation requirements
- **WHEN** designing self-contained segments
- **THEN** each segment SHALL include:
  - **段落概要**: Context 獨立的基礎資訊
  - **核心實作要點**: 基於智能分析的實作指導
  - **程式碼指導**: 可直接使用的實作框架
  - **驗證機制**: Examples 和測試設計
  - **完成檢查**: 明確的驗收標準
- **AND** each segment SHALL be independently executable without additional context
```

#### **Examples 驅動設計最佳實踐**
```markdown
# ✅ 好的範例
### Requirement: Examples Design and Validation

系統 SHALL 設計完整的 Examples 驗證策略，確保實作品質。

#### Scenario: Creating Examples validation strategy

- **GIVEN** User Story requirements and implementation design
- **WHEN** designing Examples validation
- **THEN** the strategy SHALL include:
  - **basic_usage.py**: 基本使用場景驗證 (P0)
  - **integration.py**: 系統整合驗證 (P1)
  - **error_handling.py**: 錯誤處理驗證 (P1)
  - **測試覆蓋**: 涵蓋 90% 以上使用場景
- **AND** each Example SHALL be executable and provide clear validation results
```

### **🎯 本命令的 OpenSpec 應用**

本命令將 OpenSpec 格式應用於：
- **段落式實作設計**: 每個功能段落都有結構化的 Requirements 和 Scenarios
- **驗證機制**: 確保段落 Self-Contained 和 Examples 可執行
- **錯誤修復**: 提供具體的實作問題解決方案
- **品質保證**: 明確的完成檢查清單和驗收標準

### **🔄 與 Story Design 的整合**

Execution Plan **基於** Story Design 的 SD1-SD4 成果，並將其轉換為：
- **可執行的段落**: 將技術故事分解為獨立實作段落
- **具體的程式碼**: 將 Pseudo Code 轉換為實作框架
- **驗證機制**: 設計 Examples 和測試策略
- **品質標準**: 制定完成檢查清單

**🔥 重要提醒**: 即使您完全不熟悉 OpenSpec，只要遵循本命令提供的範例和模板，就能產出符合 OpenSpec 標準的高品質實作計畫書。

## 使用方式
```bash
/execution-plan "實作任務描述" [可選：PROMPT檔案路徑]
```

## 🎯 Execution Plan 段落式實作計畫書定位

### **主要受眾**
- **主要受眾**: AI執行段落式實作
- **次要受眾**: `/impl` + Module Expert協作、功能實作Review

### **核心價值**
- **Story Design 驅動**: 基於 SD1-SD4 設計成果，確保與用戶故事一致
- **Self-Contained分段實作**: 每個功能段落獨立完整，應對context限制
- **Examples驅動開發**: 以可執行範例驗證功能，確保用戶體驗
- **強制Review機制**: 每段落完成後USER REVIEW，確保品質
- **生產就緒交付**: 輸出可部署的功能實作、完整Examples、測試套件

## 📚 專業知識庫 (強制自動載入)

🚨 **必須按順序載入以下核心文檔：**
1. CLAUDE.md - 基礎行為準則與環境約束
2. session_notes.md - 當前任務狀態
3. Story Design 設計文檔 - SD1-SD4 完整設計成果
4. docs/ai_support/core/developer_comprehensive_guide.md - Examples驅動開發指導

## 🎯 段落式實作方法論核心

### **Execution Plan 的戰略地位**
Execution Plan 在 4-Stage 設計流程中是**功能實現的品質保證**：

- **Story Design 驅動**: 基於 SD1-SD4 設計成果，確保與用戶故事完全一致
- **Examples驅動驗證**: Examples是核心驗證機制，不只是輔助工具
- **Self-Contained執行**: 每個功能段落獨立執行，context效率最大化
- **強制Review品質**: 每段完成後USER REVIEW，避免累積品質債務
- **生產就緒標準**: 輸出可直接部署的高品質功能實作

### **🚨 強制分段實作原則**
**絕對禁止**: 一次完成複雜功能，必須按功能段落分段進行
**執行策略**: 功能段落1 → USER REVIEW → 功能段落2 → USER REVIEW → ...

## 🧠 智能設計分析與驗證機制 (基於 OpenSpec)

### **🔍 執行前強制 Story Design 分析**
**執行 /execution-plan 時，AI 基於完整 Story Design (SD1-SD4) 進行智能分析與驗證：**

#### **Step 1: Story Design 結構化驗證**
使用 OpenSpec 結構化格式驗證 Story Design 文檔：

**結構化格式驗證**:
- 確認使用 `### Requirement:` 和 `#### Scenario:` 結構
- 驗證每個需求都有 SHALL 語言陳述
- 檢查 WHEN/THEN/AND 場景步驟的完整性

**內容完整性檢查**:
- **SD1 專案探索**: Purpose、Requirements、Scenarios 完整性
- **SD2 系統分析**: 系統分析需求和驗證場景
- **SD3 架構設計**: 架構設計需求和技术故事分解
- **SD4 最終確認**: 最終驗證需求和實作計劃場景

#### **Step 2: 實作導向智能分析**
基於驗證過的 Story Design，進行實作導向分析：

**檔案影響分析**:
- 基於 SD3 架構設計分析實際修改檔案
- 評估依賴關係和整合複雜度
- 識別向後相容性風險

**實作模板生成**:
- 將 SD3 Pseudo Code 轉換為具體實作框架
- 補強實作細節和調用關係
- 生成可執行程式碼模板

**技術故事映射**:
- 將 SD4 技術故事分解映射到實作段落
- 計算段落優先級和依賴關係
- 設計驗證策略和 Examples 規劃

#### **Step 3: Self-Contained段落生成**
基於分析結果生成獨立完整的功能段落：
- **Context獨立**: 包含完整實作資訊
- **實作就緒**: 提供可直接使用的程式碼
- **驗證完整**: 整合 Examples 和 Review 機制

### **🚨 OpenSpec 驗證機制**

#### **Requirement: Pre-Validation Checklist**

Execution Plan SHALL 提供完整的預驗證檢查清單，確保實作前的品質保證。

#### **Scenario: Performing comprehensive validation**

- **GIVEN** generated execution plan and Story Design
- **WHEN** executing validation checklist
- **THEN** the validation SHALL include:
  - **Story Design 結構驗證**: 確認遵循 OpenSpec 格式
  - **需求完整性檢查**: 驗證每個 Requirement 都有對應 Scenario
  - **技術故事一致性**: 確認技術故事與 User Story 對應
  - **實作可行性評估**: 評估每個段落的實作可行性

#### **Requirement: Error Remediation Guidance**

系統 SHALL 提供具體的錯誤修復指導，幫助解決常見問題。

#### **Scenario: Providing actionable error fixes**

- **GIVEN** validation failures or implementation issues
- **WHEN** generating remediation guidance
- **THEN** the guidance SHALL include:
  - **具體修復步驟**: 詳細的問題解決方案
  - **預期結構範例**: 正確的格式模板
  - **調試建議**: 除錯和驗證的方法
  - **最佳實踐提醒**: 避免常見陷阱的建議

## 🏗️ Execution Plan 計畫書標準結構 (基於 OpenSpec)

### **Purpose**

本 Execution Plan 文檔定義了基於 Story Design (SD1-SD4) 的段落式實作計畫，採用 OpenSpec 結構化格式，確保實作過程的品質保證和可追溯性。

### **1. 實作任務概要 Requirements**

#### **Requirement: Implementation Task Definition**

Execution Plan SHALL 提供清晰的實作任務定義，基於 Story Design 各階段成果。

#### **Scenario: Defining implementation scope**

- **GIVEN** validated Story Design with SD1-SD4 outcomes
- **WHEN** creating implementation task summary
- **THEN** the task definition SHALL include:
  - **實作目標**: 基於 Story Design 的具體實作目標
  - **Story Design 基礎**: 明確引用的 SD1-SD4 階段成果
  - **智能補強摘要**: 自動分析發現的設計補強策略
  - **分段策略**: 基於技術故事的功能分段計劃
  - **品質標準**: 每個段落的驗收標準和完成條件

### **2. Self-Contained段落執行設計 Requirements**

#### **Requirement: Self-Contained Segment Structure**

每個實作段落 SHALL 是完全獨立的，AI 只需讀取該段落就能完成實作。

#### **Scenario: Creating self-contained implementation segments**

- **GIVEN** technical story decomposition and implementation requirements
- **WHEN** designing self-contained segments
- **THEN** each segment SHALL include:
  - **段落概要**: Context 獨立的基礎資訊
  - **核心實作要點**: 基於智能分析的實作指導
  - **程式碼指導**: 可直接使用的實作框架
  - **驗證機制**: Examples 和測試設計
  - **完成檢查**: 明確的驗收標準

### **3. 功能段落標準格式 Requirements**

#### **Requirement: Segment Template Standardization**

實作段落 SHALL 遵循標準化模板格式，確保一致性和可預測性。

#### **Scenario: Applying segment template**

- **GIVEN** validated Story Design and implementation requirements
- **WHEN** creating implementation segments
- **THEN** each segment SHALL follow this structure:

```markdown
## 功能段落X: [US-ID] [User Story 標題] 實作

### 📋 段落概要 (Context獨立性)
- **功能描述**: 基於 User Story 的具體功能描述
- **User Story 對應**: SD4 技術故事 US-ID 的實作
- **預期成果**: 可驗證的具體成果和輸出
- **前置條件**: SD3 架構設計完成，依賴存在
- **預估時間**: 實作預估時間

### 🎯 核心實作要點 (智能分析結果)
- **Story Design 依據**: SD1 User Story 和 SD3 Pseudo Code
- **關鍵檔案**: 基於檔案影響分析的修改清單
- **核心邏輯**: 基於 Pseudo Code 的實作邏輯
- **API設計**: 基於 SD3 設計的具體介面
- **錯誤處理**: 基於 Story Design 的錯誤策略

### 💻 程式碼指導 (實作模板)
- **初始化邏輯**: 基於 Pseudo Code 的實作框架
- **核心方法**: 主要業務功能的具體實作
- **輔助方法**: 支援功能的實作指導

### 🧪 Examples驗證 (功能驗證)
- **Examples檔案**: SD4 設計的驗證檔案
- **驗證場景**: 基於 User Story 的測試場景
- **執行命令**: 標準化的驗證命令

### ✅ 完成檢查清單 (明確驗收)
- **功能實作**: 核心功能完成且符合 User Story
- **Examples驗證**: Examples 可正常執行
- **錯誤處理**: 錯誤處理邏輯驗證通過
- **API規範**: 符合 SD3 設計規範
- **整合測試**: 與現有系統整合無衝突

### 🔗 下一段落銜接 (流程連貫)
- **交付物**: 本段落完成的具體交付
- **下段前置**: 下一段落開始前的準備
```

#### 💻 程式碼指導 (智能生成的實作模板)
```python
# 基於SD設計智能生成的實作框架
class EnhancedImplementation:
    def core_method(self, params: SpecificType) -> ResultType:
        """
        智能補強的實作指導
        Call Stack: [自動分析的調用鏈]
        設計依據: [來自SD設計的具體依據]
        """
        # Step 1: [具體實作步驟，基於設計分析]
        # Step 2: [整合策略，基於依賴分析]
        # Step 3: [錯誤處理，基於驗證原則]
        pass
```

#### 🧪 Examples驗證 (功能驗證)
- **Examples檔案**: [對應的examples檔案名稱]
- **驗證場景**: [需要驗證的使用場景，2-3個]
- **執行命令**: [驗證examples的具體命令]

#### ✅ 完成檢查清單 (明確驗收)
- [ ] 核心功能實作完成且可運行
- [ ] Examples可正常執行並展示功能
- [ ] 錯誤處理邏輯驗證通過
- [ ] API介面符合設計規範
- [ ] 與現有系統整合無衝突

#### 🔗 下一段落銜接 (流程連貫)
- **交付物**: [本段落完成後的交付物]
- **下段前置**: [下一段落開始前需要的準備]

#### **Context限制應對策略**
**🚨 資訊濃縮原則** (最關鍵的創新點):

1. **一段落一功能**: 每個段落只專注一個明確功能，避免複雜性
2. **關鍵資訊優先**: 實作必需的資訊優先，細節可後補
3. **檔案引用最小化**: 每段落引用檔案數量控制在3-5個
4. **模板化指導**: 提供程式碼框架，減少從零開始的context消耗

#### **功能段落優先級設計**
- **P0核心段落** (必須完成):
  - 核心API實作
  - 基礎Examples驗證
  - 關鍵錯誤處理

- **P1重要段落** (重要功能):
  - 進階功能實作
  - 整合測試驗證
  - 效能優化

- **P2增值段落** (可選功能):
  - 輔助工具
  - 詳細文檔
  - 額外Examples

### **3. Examples驅動開發策略**

#### **Examples核心價值重新定位**
Examples在故事驅動開發中是**核心驗證機制**，具備4個關鍵角色：

1. **設計驗證器**: Examples展示API設計是否直覺易用
2. **功能完整性檢查**: Examples必須涵蓋90%以上的實際使用場景
3. **用戶接受度測試**: Examples代表真實用戶的實際操作流程
4. **測試設計參考**: Examples內容可作為編寫自動化測試的設計參考

#### **Examples目錄結構標準**
**檔案命名規則**:
- `basic_{功能}_usage.py` - 基礎使用 (P0: 最重要)
- `advanced_{功能}.py` - 進階功能 (P1)
- `{功能}_integration.py` - 跨模組整合 (P1)
- `migration_from_{舊API}.py` - 遷移指南 (P2)
- `troubleshooting_{功能}.py` - 問題排解 (P2)

#### **Examples品質標準**
- ✅ **可執行性**: 所有examples在乾淨環境中可直接執行
- ✅ **完整性**: 涵蓋90%以上的實際使用場景
- ✅ **易學性**: 新用戶能通過examples在20分�內完成基本操作
- ✅ **實用性**: Examples直接解決真實世界的問題
- ✅ **維護性**: Examples程式碼簡潔清晰，註解充分

#### **Examples開發優先級**
1. **P0**: basic_usage.py - 最核心的使用方式
2. **P1**: integration.py - 與其他模組的整合使用
3. **P2**: advanced_features.py - 進階功能展示
4. **P3**: migration_guides.py - 遷移和升級指南
5. **P4**: troubleshooting.py - 問題排解和最佳實踐

### **4. 測試策略與品質保證**

#### **測試分工明確化**
- **Examples職責**: 展示使用方式、驗證用戶體驗、提供測試設計參考
- **Tests職責**: 自動化回歸測試、邊界條件測試、性能測試

#### **品質保證檢查清單**
- **功能正確性**: 核心功能符合設計規範
- **API易用性**: 通過Examples驗證API設計直覺性
- **錯誤處理**: 邊界條件和異常情況的處理
- **整合穩定性**: 與現有系統的整合測試
- **代碼品質**: 符合專案代碼規範和風格

### **5. 實作段落模板範例**

### **4. Examples 驅動開發策略 Requirements**

#### **Requirement: Examples Design and Validation**

系統 SHALL 設計完整的 Examples 驗證策略，確保實作品質。

#### **Scenario: Creating Examples validation strategy**

- **GIVEN** User Story requirements and implementation design
- **WHEN** designing Examples validation
- **THEN** the strategy SHALL include:
  - **basic_usage.py**: 基本使用場景驗證 (P0)
  - **integration.py**: 系統整合驗證 (P1)
  - **error_handling.py**: 錯誤處理驗證 (P1)
  - **測試覆蓋**: 涵蓋 90% 以上使用場景

### **5. 驗證與品質保證 Requirements**

#### **Requirement: Quality Assurance Framework**

系統 SHALL 提供完整的驗證框架，確保實作品質。

#### **Scenario: Implementing quality assurance**

- **GIVEN** implementation segments and Examples
- **WHEN** performing quality assurance
- **THEN** the framework SHALL include:
  - **強制 Review 機制**: 每段落完成後 USER REVIEW
  - **自動化測試**: 基於 Examples 的自動化驗證
  - **回歸測試**: 確保不破壞現有功能
  - **整合測試**: 跨模組整合驗證

## 📋 實作範例模板 (基於 OpenSpec 格式)

### **Requirement: Core Implementation Segment Template**

核心功能段落 SHALL 遵循標準化範本，確保一致性和可維護性。

#### **Scenario: Applying core segment template**

- **GIVEN** SD3 Pseudo Code and SD4 technical story
- **WHEN** creating core implementation segment
- **THEN** the segment SHALL follow this template:

```markdown
## 功能段落1: [US-001] [User Story 標題] 核心實作

### 📋 段落概要 (Context 獨立性)
- **功能描述**: 基於 SD1 User Story 的具體功能描述
- **User Story 對應**: SD4 技術故事 US-001 的實作
- **預期成果**: 可驗證的具體成果和功能輸出
- **前置條件**: SD3 架構設計已完成，相關依賴存在
- **預估時間**: 4-6小時

### 🎯 核心實作要點 (智能分析結果)
- **Story Design 依據**:
  - SD1 User Story: [對應的用戶故事描述]
  - SD3 Pseudo Code: [基於哪個 Pseudo Code 設計]
- **關鍵檔案**:
  - `[基於SD3 ERD的主要檔案]` (核心實作)
  - `[相關依賴檔案]` (基礎介面/工具)
  - `examples/[SD4設計的檔案]` (驗證範例)
- **核心邏輯**:
  1. [基於 Pseudo Code 的核心邏輯1]
  2. [基於 Pseudo Code 的核心邏輯2]
  3. [基於 Story Design 的驗證機制]
- **API設計**: [基於 SD3 設計的具體 API 介面]
- **錯誤處理**: [基於 Story Design 的錯誤處理策略]

### 💻 程式碼指導 (基於 SD3 Pseudo Code)
```python
# 基於 SD3 Pseudo Code 轉換的實作框架
class [ComponentName]:
    """
    User Story: [SD1 中的對應用戶故事]
    設計意圖: [解決什麼痛點，支援什麼業務場景]
    架構位置: [SD3 中的架構位置]
    依賴模組: [具體依賴的其他模組]
    """

    def __init__(self, config: Dict[str, Any]):
        """
        設計意圖: [初始化邏輯和依賴注入]
        Call Stack: __init__ -> _validate_config -> _setup_dependencies
        User Story 支援: [如何支援具體的用戶場景]
        """
        # 基於 Pseudo Code 的初始化邏輯
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
        # 基於 Pseudo Code 的核心邏輯
        result1 = self._step1(params)      # 步驟1：處理用戶輸入
        result2 = self._step2(result1)     # 步驟2：核心業務邏輯
        return self._validate_result(result2)  # 步驟3：結果驗證

    def _step1(self, data: InputType) -> IntermediateType:
        """
        Call Stack: _step1 -> DataService.process -> Validation.check
        User Story 支援: [支援用戶故事的哪個子場景]
        """
        # 基於 Pseudo Code 的具體實現邏輯
        pass
```

### 🧪 Examples驗證 (基於 SD4 設計)
- **Examples檔案**: `examples/[SD4設計的檔案名]`
- **驗證場景**:
  1. [基於 User Story 的主要使用場景]
  2. [錯誤處理驗證場景]
  3. [邊界條件測試場景]
- **執行命令**: [基於專案環境的標準執行命令]

### ✅ 完成檢查清單 (明確驗收)
- [ ] 核心功能實作完成且符合 User Story 需求
- [ ] Examples可正常執行並展示功能
- [ ] 錯誤處理邏輯驗證通過
- [ ] API介面符合 SD3 設計規範
- [ ] 與現有系統整合無衝突

### 🔗 下一段落銜接 (流程連貫)
- **交付物**: 可運行的核心功能和驗證範例
- **下段前置**: 核心功能驗證通過，準備整合其他模組
```

#### **範例2: 整合功能段落模板**
```markdown
## 功能段落3: DataGateway與Strategy系統整合

### 📋 段落概要 (Context獨立性)
- **功能描述**: 整合DataGateway到現有Strategy系統，實現策略回測數據來源統一
- **預期成果**: 所有Strategy類別可透過DataGateway取得統一格式數據
- **前置條件**: DataGateway核心功能完成，BaseStrategy類別存在
- **預估時間**: 3-4小時

### 🎯 核心實作要點 (濃縮精華)
- **關鍵檔案**:
  - `strategy/base_strategy.py` (修改基礎類別)
  - `strategy/trend_following.py` (範例策略更新)
  - `examples/strategy/integrated_backtest.py` (整合驗證)
- **核心邏輯**:
  1. BaseStrategy注入DataGateway依賴
  2. 統一數據介面替換現有分散數據載入
  3. 向後相容性確保 (暫時保留舊介面)
- **API設計**: `BaseStrategy.__init__(data_gateway: DataGateway)`
- **錯誤處理**: 數據載入失敗時的策略降級處理

### 💻 程式碼指導 (實作模板)
```python
class BaseStrategy:
    def __init__(self, data_gateway: DataGateway, config: Dict):
        self.data_gateway = data_gateway
        self.config = config

    def load_strategy_data(self, symbol: str, period: str) -> pd.DataFrame:
        # 統一透過DataGateway載入數據
        start_date, end_date = self._calculate_period_range(period)
        return self.data_gateway.load_data(symbol, start_date, end_date)

    def backtest(self, symbols: List[str]) -> Dict:
        # 整合回測邏輯，使用統一數據來源
        results = {}
        for symbol in symbols:
            data = self.load_strategy_data(symbol, self.config['backtest_period'])
            results[symbol] = self._run_strategy(data)
        return results
```

### 🧪 Examples驗證 (功能驗證)
- **Examples檔案**: `examples/strategy/integrated_backtest.py`
- **驗證場景**:
  1. 趨勢策略使用DataGateway執行回測
  2. 多商品組合策略驗證
  3. 與舊版本結果一致性檢查
- **執行命令**: `python examples/strategy/integrated_backtest.py`

### ✅ 完成檢查清單 (明確驗收)
- [ ] BaseStrategy成功整合DataGateway
- [ ] 現有策略 (trend_following) 遷移成功
- [ ] Examples執行結果與預期一致
- [ ] 向後相容性確認 (舊版本策略仍可運行)
- [ ] 整合測試涵蓋多種數據來源場景

### 🔗 下一段落銜接 (流程連貫)
- **交付物**: 完整整合的Strategy系統和驗證範例
- **下段前置**: 所有核心功能整合完成，準備進行系統效能優化
```

## 🚨 專案特定約束模板

### **實作執行專用約束範例**
> **注意**: 以下約束需要根據實際專案的 CLAUDE.md 進行客製化

- **驗證策略**: 定義專案的驗證機制（如：assert優先、fail fast策略）
- **向後相容性**: 定義專案的相容性政策（如：允許破壞性變更）
- **Examples優先**: 先讓examples能跑，再完善內部實作
- **實際運行驗證**: 修改代碼後必須立即執行相關測試或範例程式

### **執行環境約束範例**
> **注意**: 需根據專案實際環境配置

- **Python環境**: 專案使用的Python版本和虛擬環境路徑
- **環境變數**: 必要的環境變數設定（如：PYTHONPATH）
- **工作目錄**: 執行命令時的標準工作目錄
- **路徑管理**: 專案的統一路徑管理工具或模組

### **文檔輸出約束範例**
> **注意**: 需根據專案文檔結構定義

- **儲存路徑**: Execution Plan 文檔的標準儲存位置
- **Self-Contained要求**: 每個功能段落獨立完整
- **強制Review**: 每個段落完成後必須USER REVIEW

## 📋 Execution Plan 計畫書品質檢查

### **Self-Contained設計驗證**
- [ ] **獨立性**: 不讀取其他段落也能理解要做什麼
- [ ] **完整性**: 包含所有執行必需的資訊 (檔案、邏輯、驗證)
- [ ] **可驗證**: 有明確的完成標準和檢查方法
- [ ] **精華濃縮**: 資訊密度高，context使用最小化
- [ ] **實作導向**: 提供具體程式碼框架，而非抽象描述

### **Examples驅動設計品質**
- [ ] Examples涵蓋90%以上使用場景
- [ ] 基礎Examples (P0) 完整設計
- [ ] 整合Examples (P1) 跨模組驗證
- [ ] Examples可執行性和易學性保證

### **分段執行合理性**
- [ ] 功能段落劃分合理且相對獨立
- [ ] 每個段落有明確的目標和交付物
- [ ] Review檢查點設計清晰可執行
- [ ] 段落間的依賴關係和銜接明確

## 🔧 輸出和後續行動

Execution Plan生成完成後：

### **直接輸出**
1. **計畫書路徑**: 提供完整的Execution Plan檔案位置
2. **智能分析報告**: SD設計基礎確認和實作導向分析結果
3. **實作範圍摘要**: 分段實作的核心範圍和功能
4. **SD設計對應**: 與Phase 2 SD設計的對應關係說明
5. **分段執行提醒**: 強調功能段落分段執行和Review機制

### **後續行動建議**
- **開始執行**: 使用 `/impl` + Module Expert基於此計畫書執行Phase 3實作
- **SD設計基礎**: 確認SD設計文檔完整且準確
- **功能段落執行**: 按P0→P1→P2順序逐段執行，每段完成後USER REVIEW
- **Examples優先**: 每段都先實現Examples可執行，再完善內部實作

### **session_notes更新**
- 記錄Execution Plan生成結果和分段實作規劃
- 更新功能段落執行順序和Review檢查點
- 記錄Examples驅動開發策略和品質標準

---

**重要**: 此命令專注於段落式實作計畫書生成，基於 Story Design (SD1-SD4) 成果為實作提供詳細指導。完整專案設計請使用 `/story-design`。

**🚨 強制要求 (基於 OpenSpec 最佳實踐)**:
- **🧠 必須執行 Story Design 分析**: 基於完整 SD1-SD4 設計進行結構化驗證和分析
- **📁 必須進行檔案影響分析**: 基於 SD3 架構設計和現有代碼分析實際修改檔案
- **💻 必須生成實作模板**: 將 SD3 Pseudo Code 轉換為具體可執行的程式碼框架
- **🔗 必須展示 Call Stack**: 分析和展示基於 Story Design 的函數調用關係
- **🎭 必須基於 User Story**: 確保所有實作都回歸到 SD1 的用戶故事
- **📝 必須遵循 OpenSpec 格式**: 使用 `### Requirement:` 和 `#### Scenario:` 結構
- **📝 必須使用 SHALL 語言**: 明確陳述需求和預期行為
- **📝 必須包含驗證場景**: 每個需求都有對應的 WHEN/THEN/AND 場景
- 必須設計 Self-Contained 功能段落，應對 context 限制
- 必須設計強制 Review 機制，每段完成後 USER REVIEW
- 必須包含完整的 Examples 驅動開發策略
- Examples 必須可執行且涵蓋 90% 使用場景
- 實作必須基於 Story Design 和智能分析結果

### **📋 OpenSpec 相容性要求**
- **結構化格式**: 文檔必須遵循 OpenSpec 的 `### Requirement:` 和 `#### Scenario:` 格式
- **驗證機制**: 提供完整的預驗證檢查清單和錯誤修復指導
- **工具相容**: 確保與 OpenSpec 工具鏈的相容性