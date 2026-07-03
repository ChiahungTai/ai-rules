# 遞歸發現與處理流程

## 步驟 1: 發現 instruction 檔

```bash
# 單檔案模式
Read <target-instruction-file>

# 遞歸模式（用 fd，預設排除隱藏檔與 .gitignore；AGENTS.md 為主、CLAUDE.md legacy）
fd "(AGENTS|CLAUDE)\.md" <target-dir>
```

## 步驟 2: 分類與優先級

```python
def categorize_instruction_files(files: list) -> dict:
    """將發現的 instruction 檔（AGENTS.md/CLAUDE.md）按重要性分類"""

    categories = {
        "critical": [],    # 專案根目錄
        "high": [],        # 主要模組 (src/, core/, lib/)
        "medium": [],      # 子模組
        "low": []          # 測試、範例、文檔
    }

    for file_path in files:
        if "/" not in file_path.replace(target_dir, ""):
            categories["critical"].append(file_path)
        elif any(x in file_path for x in ["/src/", "/core/", "/lib/"]):
            if file_path.count("/") > 3:  # 深層目錄
                categories["medium"].append(file_path)
            else:
                categories["high"].append(file_path)
        elif any(x in file_path for x in ["/tests/", "/examples/", "/docs/"]):
            categories["low"].append(file_path)
        else:
            categories["medium"].append(file_path)

    return categories
```

## 步驟 3: 處理順序

```
1. Critical（根目錄）
   ↓
2. High（主要模組）
   ↓
3. Medium（子模組）
   ↓
4. Low（測試、範例）
```
