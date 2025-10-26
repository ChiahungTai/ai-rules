# Design Plan Command - SD結構化設計計畫書生成器

為軟體開發專案生成**SD結構化設計計畫書**，執行 Phase 2 的系統設計與架構規劃，專為系統架構設計、技術方案制定和用戶故事細化設計。

**🚨 重要**: 此命令生成SD設計專精計畫書，專注於Phase 2的結構化設計方法論。系統分析請使用 `/analysis-plan`，實作執行請使用 `/execution-plan`。

## 使用方式
```bash
/design-plan "設計任務描述" [可選：PROMPT檔案路徑]
```

## 🎯 Design Plan SD結構化設計計畫書定位

### **核心受眾** (雙重受眾設計)
- **AI (Claude)**: 執行Phase 2 SD結構化設計的主要執行者
  - 需要：基於SA分析的具體設計步驟和Pseudo Code模板
  - 目標：生成完整的設計藍圖文檔和函數調用Call Stack
  - 約束：必須基於SA分析結果，保持SA-SD一致性
- **User (你) Review**: SD設計結果的審核者和架構決策者
  - 需要：清晰的設計藍圖和技術架構方案
  - 目標：理解系統設計，評估技術方案可行性
  - 價值：獲得可執行的技術設計和Phase 3實作指導

### **核心價值**
- **系統架構藍圖**: 基於SA分析結果設計完整的系統架構
- **技術方案制定**: 制定具體可執行的技術實作方案
- **用戶故事細化**: 將業務需求轉化為可執行的技術故事
- **SD設計文檔輸出**: 生成完整的結構化設計文檔作為Phase 3基礎

### **🚨 SD設計特色功能：SA空殼Class補完**

#### **📋 從SA到SD的自然延續**
- **SA階段輸出**: 檔案結構ERD + 空殼class定義
- **SD階段補完**: 空殼class → Pseudo Code設計藍圖
- **設計藍圖**: 方法簽名 + 詳細註釋 + 調用關係，不做具體實現
- **架構意圖**: 讓開發者理解設計思路和技術決策

#### **🎯 Pseudo Code設計標準**
1. **方法簽名設計**: 完整的參數類型、返回值定義
2. **設計意圖註釋**: 詳細說明業務邏輯和架構考量
3. **Call Stack展示**: 展示函數調用關係和執行路徑
4. **架構決策記錄**: 設計原因和技術考量說明

## 📚 專業知識庫 (強制自動載入)

🚨 **必須按順序載入以下核心文檔：**
1. CLAUDE.md - 基礎行為準則與環境約束
2. session_notes.md - 當前任務狀態

## 🏗️ SD結構化設計方法論核心

### **SD設計的戰略地位**
SD (Structured Design) 在故事驅動開發中是**架構設計的藍圖**：

- **系統架構藍圖**: 系統架構圖定義整體技術架構
- **模組組織設計**: 模組結構圖設計清晰的模組關係
- **程式結構設計**: 類別圖和互動圖指導程式設計
- **介面標準制定**: 介面設計規範確保一致性

### **🔄 Call Stack設計核心方法**

**Call Stack設計價值**: 通過實際函數調用展示系統執行順序，用調用關係替代抽象的模組依賴圖，提供Phase 3實作的具體調用模板。

### **基於SA分析的設計原則**
- **SA-SD一致性**: SD設計必須完全基於SA分析結果
- **數據流導向**: 系統架構設計遵循DFD分析的數據流向
- **實體關係對應**: 模組設計對應ERD分析的實體關係
- **狀態驅動**: 程式邏輯設計符合狀態轉換圖的行為定義

## 🏗️ SD結構化設計計畫書標準結構

### **1. 設計任務概要**
- **設計目標**: 明確的SD設計目標和交付標準
- **SA分析基礎**: 基於哪些SA分析結果進行設計
- **設計範圍**: SD設計的範圍和邊界條件
- **技術約束**: 專案的技術約束和設計限制

### **2. 系統架構圖設計規劃**

#### **分層架構設計範例** (可根據專案調整)
**典型軟體系統架構**：
- **應用層 (Application Layer)**:
  - Web UI (視覺化應用)
  - CLI工具
  - API Gateway
- **業務邏輯層 (Business Logic Layer)**:
  - 策略引擎 (Strategy Engine)
  - 實驗管理器 (Experiment Manager)
  - 模型管理器 (Model Manager)
  - 風控引擎 (Risk Engine)
- **服務層 (Service Layer)**:
  - 數據閘道器 (Data Gateway)
  - 特徵管理器 (Feature Manager)
  - 快取管理器 (Cache Manager)
  - 訊號處理器 (Signal Processor)
- **基礎設施層 (Infrastructure Layer)**:
  - 數據提供者 (Data Provider)
  - 日誌系統 (Logger)
  - 配置管理 (Config)
  - 工具函數 (Utilities)

#### **依賴管理原則**
- 單向依賴: 上層依賴下層，下層不依賴上層
- 依賴注入: 通過配置注入依賴，避免硬編碼
- 介面隔離: 模組間通過標準介面通信

### **3. 模組結構圖設計規劃**

#### **模組介面設計規範**
- **統一配置注入**: 所有模組通過config字典初始化
- **標準生命週期**: initialize() → process() → cleanup()
- **錯誤處理統一**: 使用專案定義的驗證策略
- **日誌記錄統一**: 使用模組級logger，統一日誌格式

### **4. 程式結構圖設計規劃** <!-- ai-tag: #Pseudo Code設計核心 -->

#### **🚨 從SA空殼Class到SD設計藍圖**

##### **📁 檔案結構展示方式 (取代mermaid ERD)**
使用類似檔案樹的方式展示，而非抽象的mermaid圖表：

```
[project_name]/
├── [data_module]/
│   └── [sub_module]/
│       └── core_class.py              # 重構後的核心系統
├── [business_module]/
│   ├── components/
│   │   ├── main_component.py          # 主要組件，已有核心機制
│   │   ├── feature_a.py                # 受益於優化的組件
│   │   └── feature_b.py                # 最小影響的組件
│   └── processors/
│       └── data_processor.py           # 需要適配的高風險組件
```

**檔案結構展示原則**：
- **清楚標註**: 每個檔案的作用和重構重點
- **影響評估**: 標明哪些是高風險、中風險、低風險組件
- **實際路徑**: 使用真實的檔案路徑，便於開發者定位

##### **🏗️ 空殼class定義方式 (可直接讀懂的code大綱)**
提供詳細註解的class結構，讓人掃讀就能理解設計意圖：

```python
# [project_name]/[module]/core_component.py

class ComponentFactory:
    """
    統一組件創建入口，解決SA分析發現的重複載入問題
    設計目標：提供高性能的資源管理策略
    """
    def __init__(self, config: Dict[str, Any]):
        """配置驅動初始化，支援策略設定"""
        pass

    def create_component(self, name: str, data: pd.DataFrame,
                        strategy: str = 'optimized') -> Component:
        """創建組件，內建性能優化策略"""
        pass

class CoreComponent:
    """
    核心組件，改進機制解決性能問題
    關鍵改進：智能處理、快速復原、向後相容
    """
    def __init__(self, name: str, data: pd.DataFrame,
                 strategy: str = 'optimized'):
        """strategy控制處理方式：optimized或standard"""
        pass

    def to_dict(self, include_data: bool = None) -> Dict[str, Any]:
        """智能序列化，根據strategy自動決定是否包含大數據"""
        pass

    @classmethod
    def from_dict(cls, data: Dict[str, Any],
                  fallback_loader: Optional[Callable] = None) -> 'CoreComponent':
        """智能反序列化，支援直接復原和外部載入兩種策略"""
        pass
```

**空殼class設計原則**：
- **詳細註解**: 說明設計意圖、解決的問題、預期效益
- **實際參數**: 使用真實的參數類型和名稱
- **關聯標註**: 標明影響的具體檔案和行號
- **API保持**: 明確哪些API保持不變，降低風險

##### **Pseudo Code設計範例模板**
```python
# SD階段：Pseudo Code設計藍圖
class DataProcessor:
    """
    設計意圖: 統一數據處理入口，支援批次和單筆處理
    架構角色: Service Layer核心組件，依賴: DataGateway, CacheManager
    """
    def __init__(self, config: Dict[str, Any]):
        """Call Stack: __init__ -> _validate_config -> _setup_dependencies"""
        assert isinstance(config, dict), "Config must be dictionary"
        self.config = config
        self._setup_dependencies()

    def process_batch(self, instruments: List[str], time_range: TimeRange) -> ProcessResult:
        """
        批次數據處理主流程，Pipeline模式支援中斷恢復
        Call Stack: process_batch -> _load_data -> _validate_data -> _transform_data
        """
        raw_data = self._load_data(instruments, time_range)
        validated_data = self._validate_data(raw_data)
        return self._transform_data(validated_data)

    def _load_data(self, instruments: List[str], time_range: TimeRange) -> RawData:
        """Call Stack: _load_data -> DataGateway.load_bars -> CacheManager.get"""
        pass
```

#### **設計模式應用** (具體調用展示)
```python
# Strategy Pattern 實際調用範例
class StrategyEngine:
    def execute_strategy(self, strategy_name: str, data: MarketData) -> SignalResult:
        """
        Call Stack: execute_strategy -> StrategyFactory.create -> strategy.apply -> SignalProcessor.process
        """
        strategy = StrategyFactory.create(strategy_name)  # Factory Pattern調用
        signals = strategy.apply(data)                    # Strategy Pattern調用
        return SignalProcessor.process(signals)           # 後續處理調用
```

### **5. 介面設計規範規劃**

#### **API介面設計標準**
- **輸入驗證統一**: 使用專案定義的驗證機制進行類型和範圍檢查
- **輸出格式標準**: 統一的回應格式和錯誤處理
- **版本管理**: API版本化策略和向後相容性
- **文檔標準**: API文檔的格式和維護標準

#### **UI介面設計標準** (如適用)
- **組件化設計**: 基於選定UI框架的組件化設計
- **響應式設計**: 適應不同螢幕尺寸的佈局
- **互動模式**: 使用者互動的標準模式和流程
- **視覺一致性**: 統一的視覺風格和元件庫

## 🎯 用戶故事設計標準 (Phase 2核心活動)

### **故事細化方法論**
- **SA分析對應**: 每個用戶故事對應特定的SA分析元素
- **驗收標準設計**: 具體可測試的驗收條件
- **Examples設計**: 每個故事對應的Examples驗證方案
- **優先級分級**: P0-P4的優先級分級策略

### **用戶故事標準格式**
```markdown
**故事ID**: US-001
**作為** [用戶角色] **我希望** [功能描述] **以便** [業務價值]

**驗收標準**: [具體操作和期望結果]
**SA/SD設計關聯**: [對應DFD流程、ERD實體、系統架構位置]
**Examples設計**: basic_usage.py、integration.py、error_handling.py

**定義完成**: Examples可執行、API驗證通過、系統整合無衝突、設計一致性確認
```

## 🏗️ SD 結構化設計標準

### **🎯 2段式漸進設計文檔產出**
**design-plan 在同一設計文檔中分2段漸進完成，確保設計整體性：**

#### **設計段落 1: 整體架構設計**
- **🎯 目標**: 基於SA分析設計整體系統架構和技術選型
- **📋 交付**: 分層架構圖 + 技術架構圖 + 技術選型決策
- **🔍 USER REVIEW**: 架構方向確認，技術選型正確性
- **⚠️ 在同一設計文檔中完成，Review通過後繼續詳細設計**

#### **設計段落 2: 詳細設計完成**
- **🎯 目標**: 基於確認的架構完成所有詳細設計組件
- **📋 交付**:
  - **模組結構圖設計**: 詳細的模組劃分、依賴關係和模組介面定義
  - **Pseudo Code 設計藍圖**: 將SA空殼class補完為具體設計藍圖，包含Call Stack展示
  - **介面規範設計**: 完整的API介面規範、數據格式定義和錯誤處理策略
  - **架構決策記錄**: 詳細的設計原因、技術考量和整合方案
- **🔍 USER REVIEW**: 詳細設計完整性，與架構一致性

#### **設計文檔特色**
- **2段式漸進**: 先確認架構方向，再完成詳細設計，降低返工風險
- **同文檔完整性**: 雖分2段執行，但在同一設計文檔中保持整體一致性
- **實作導向**: 提供可直接用於 execution-plan 智能分析的完整設計基礎
- **SA-SD延續**: 完全基於SA分析結果，保持分析設計一致性

## 📊 SD設計文檔輸出標準

### **Analysis & Design書 (SD部分)標準結構**
```markdown
# Analysis & Design - [專案名稱]

## 🏗️ SD結構化設計 (Phase 2)

### 系統架構圖
[插入整體架構圖 - 使用mermaid graph/C4Context]

### 模組結構圖
[插入模組結構圖 - 使用mermaid graph]

### 🚨 Pseudo Code設計藍圖 (核心交付物)
#### 從SA空殼Class到SD設計藍圖
```python
# 基於SA分析的檔案結構ERD，補完每個類別的Pseudo Code設計

class [EntityName]:
    """
    設計意圖: [業務功能和架構角色]
    架構位置: [在分層架構中的位置]
    依賴模組: [具體依賴的其他模組]
    """

    def __init__(self, config: Dict[str, Any]):
        """
        設計意圖: [初始化邏輯和依賴注入]
        Call Stack: __init__ -> _validate_config -> _setup_dependencies
        """
        # 初始化 pseudo code
        pass

    def main_method(self, params: ParamType) -> ResultType:
        """
        設計意圖: [主要業務功能描述]
        Call Stack: main_method -> step1 -> step2 -> step3
        架構考量: [設計決策和技術原因]
        整合說明: [與其他模組的整合方式]
        """
        # 主要邏輯 pseudo code，展示調用關係
        result1 = self._step1(params)      # 步驟1調用
        result2 = self._step2(result1)     # 步驟2調用
        return self._step3(result2)        # 步驟3調用

    def _step1(self, data: InputType) -> IntermediateType:
        """
        Call Stack: _step1 -> ExternalModule.method -> Helper.function
        """
        # pseudo code展示調用鏈
        pass
```

#### 模組間調用關係展示
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

### API介面規範 (Pseudo Code形式)
```python
# API設計展示具體的介面定義和調用方式
class APIController:
    def endpoint_method(self, request: RequestType) -> ResponseType:
        """
        Call Stack: endpoint_method -> validate -> business_logic -> format_response
        """
        # API邏輯 pseudo code
        pass
```

## 🔗 SA/SD一致性驗證
- **檔案結構ERD對應**: SA的檔案結構如何轉化為SD的Pseudo Code
- **數據流與Call Stack一致**: DFD數據流與函數調用鏈的對應關係
- **實體關係與模組調用**: ERD實體關係與實際模組調用的一致性
- **功能分解與設計實現**: 功能分解如何體現在類別設計和調用關係中

## 🎯 用戶故事與設計關聯
[完整的用戶故事集，包含SA/SD設計關聯和Pseudo Code實現思路]
```

### **🚨 SD設計必須交付的核心內容**
1. **📁 檔案結構展示**: 使用檔案樹方式展示，標註重構重點和風險評估
2. **🏗️ 空殼class定義**: 可直接讀懂的code大綱，詳細註解設計意圖
3. **💻 Pseudo Code設計藍圖**: 基於空殼class的完整設計補完
4. **🔄 Call Stack展示**: 每個主要方法的函數調用鏈和執行路徑
5. **📋 架構決策記錄**: 詳細的設計原因和技術考量說明
6. **🔗 模組整合方案**: 具體的模組間調用關係和整合方式
7. **✅ SA-SD一致性**: 與SA分析結果的完整對應和延續關係

**🎯 設計展示優勢**：
- **code可讀性**: 直接看class結構理解設計，不需要解讀抽象圖表
- **設計意圖清晰**: 註解說明為什麼這樣設計，解決什麼問題
- **實作指導性**: 開發者可以直接按照空殼class的結構進行實作
- **風險可控**: 明確標註哪些組件受影響，評估重構風險

## 🚨 專案特定約束模板

### **通用設計約束**
- **分層依賴原則**: 嚴格的單向依賴，下層不得依賴上層
- **早期錯誤檢測**: 使用適當的驗證機制進行激進檢查
- **配置驅動設計**: 核心行為通過配置控制，避免硬編碼
- **介面隔離原則**: 模組間通過定義的介面通信

### **技術架構約束範例**
> **注意**: 以下約束需要根據實際專案的 CLAUDE.md 進行客製化

- **數據存取層**: 定義統一的數據存取介面和實作標準
- **業務邏輯層**: 建立領域物件的繼承體系和行為規範
- **服務協調層**: 設計統一的服務管理和生命週期管理機制
- **展示介面層**: 確立UI框架選型和組件化設計標準

### **Mermaid圖表規範**
- **系統架構**: `graph TD/LR` 或 `C4Context`
- **模組結構**: `graph TD/LR`
- **類別設計**: `classDiagram`
- **流程互動**: `sequenceDiagram`
- **狀態機制**: `stateDiagram-v2`

## 📋 Design Plan計畫書品質檢查

### **SD設計規劃完整性**
- [ ] 系統架構設計包含分層架構和技術棧
- [ ] 模組結構設計有明確的依賴關係和介面定義
- [ ] **🚨 Pseudo Code設計藍圖**：基於SA空殼class的完整設計補完
- [ ] **🚨 Call Stack展示**：每個主要方法的函數調用鏈和執行路徑
- [ ] **🚨 架構決策記錄**：詳細的設計原因和技術考量說明
- [ ] 介面規範設計涵蓋API和UI標準

### **SA-SD一致性檢查**
- [ ] 架構設計基於SA分析的DFD結果
- [ ] 模組設計對應ERD分析的實體關係
- [ ] 程式設計符合狀態轉換圖的邏輯
- [ ] 介面設計滿足功能分解的需求

### **用戶故事設計品質**
- [ ] 每個故事有明確的SA/SD設計關聯
- [ ] 驗收標準具體可測試
- [ ] Examples設計完整可執行
- [ ] Definition of Done包含設計一致性檢查

## 🔧 輸出和後續行動

Design Plan生成完成後：

### **直接輸出**
1. **計畫書路徑**: 提供完整的Design Plan檔案位置
2. **設計範圍摘要**: SD設計的核心範圍和重點
3. **SA-SD關聯說明**: 與Phase 1 SA分析的對應關係
4. **execution-plan 銜接準備**: 說明設計結果如何適合智能分析

### **後續行動建議**
- **開始執行**: 使用 `/sasd` + Module Expert基於此計畫書執行Phase 2 SD設計
- **SA基礎確認**: 確認SA分析結果完整且準確
- **完整設計產出**: 一次性完成所有核心設計組件，產出完整設計文檔
- **⚡ Phase 3智能銜接**: SD設計完成後直接使用 `/execution-plan` 智能分析和實作規劃

### **session_notes更新**
- 記錄Design Plan生成結果和SD設計規劃
- 更新分段執行計劃和Review檢查點
- 記錄SD設計重點和SA-SD關聯關係

---

**重要**: 此命令專注於SD結構化設計計畫書生成，為Phase 2執行提供詳細指導。SA分析規劃請使用 `/analysis-plan`，實作執行規劃請使用 `/execution-plan`。

**🚨 強制要求**:
- SD設計必須完全基於SA分析結果
- **🏗️ 必須產出完整 SD 設計文檔**：一次性包含所有核心設計組件
- **🚨 Pseudo Code設計藍圖為核心交付物**：必須將SA空殼class補完為設計藍圖
- **🚨 Call Stack函數調用展示**：必須展示主要方法的調用鏈和執行路徑
- **🚨 架構決策記錄**：必須包含詳細的設計原因和技術考量
- **SA-SD延續性**：必須基於SA分析的檔案結構ERD進行設計補完
- **⚡ execution-plan 銜接準備**：設計結果必須適合 execution-plan 智能分析
- 必須包含完整的用戶故事設計標準
- 使用mermaid圖表時需確保Dark Theme相容性
