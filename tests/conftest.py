"""治理工具鏈測試共用載入器（hooks/scripts 非 package，走 importlib）。"""

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_module(rel: str):
    """以檔案路徑載入 repo 內非 package 腳本為 module（每呼叫一個新 instance）。"""
    spec = importlib.util.spec_from_file_location(
        rel.replace("/", "_").removesuffix(".py"), REPO_ROOT / rel
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
