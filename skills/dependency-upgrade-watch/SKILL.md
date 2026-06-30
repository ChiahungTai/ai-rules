---
name: dependency-upgrade-watch
description: 偵測 nautilus_trader / shioaji 版本漂移並建議升級。讀取 pyproject.toml / uv.lock / poetry.lock / requirements.txt 相依清單、或討論 NT/SJ 版本/升級時使用 — 比對 pinned 與 PyPI 最新版，漂移時主動建議 /upgrade-nt 或 /upgrade-sj。
paths: ["**/pyproject.toml", "**/uv.lock", "**/poetry.lock", "**/requirements*.txt"]
allowed-tools: ["Bash(uv pip *)", "WebSearch"]
---

# Dependency Upgrade Watch

讀取或編輯相依清單（pyproject.toml / uv.lock / poetry.lock / requirements.txt）遇到 `nautilus_trader` 或 `shioaji` 時：

1. 記下 pinned 版本
2. 查最新版（PyPI — `uv pip index versions <pkg>`）
3. **pinned < latest** → 點出漂移（X → Y）+ 建議對應命令：
   - `nautilus_trader` → `/upgrade-nt`
   - `shioaji` → `/upgrade-sj`
   - 提醒：兩命令必須**收盤後**執行（需跑 SJ external API 測試）
4. **pinned == latest** → **靜默不輸出**（不報「已是最新」，避免噪音）
5. **離線 / PyPI 不可達** → 記「無法查最新版」，**不建議升級**（防幻覺版本號），可選提示 user 手動確認
6. **scope 限制**：僅處理 `nautilus_trader` 與 `shioaji`；其他 nautilus 套件（`nautilus_pyo3` 等）不建議對應命令（超出 upgrade-nt scope），可選提示 user 手動處理
7. **不自動執行** — 只建議，時機由 user 決定
