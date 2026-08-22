# Copyright: (c) 2026 mosaic_alpha contributors
# Licensed under GNU Affero General Public License v3.0+
"""code_reality — code reality 薄層工具鏈（dev-only）。

三源證據（LSP／CRG graph／VizTracer runtime）的可消費機械產物：
runtime_edges（viztracer trace → runtime 呼叫邊表）、snapshot（CRG
module-edge 集 → commit 錨定 sidecar）、transition（兩 snapshot 邊集
差異＋EP 宣稱對照）、hub_refs（CRG callers 按檔聚合）、boundary_build
＋boundary（NT pyo3 宣告 ↔ .pyi 合約對照 sidecar——python 符號 → Rust
真身查詢；跨語言縫，評估報告 §8 薄層 #6）。

加 __init__.py 是為了 `python -m code_reality.<mod>` 顯式子套件
import（PEP 420 namespace package 在顯式 import 時不可靠——tools/lsp_mcp
前例）。禁 re-export——消費端用完整路徑 import。
"""
