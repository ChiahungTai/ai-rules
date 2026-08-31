#!/usr/bin/env python3
# MEMORY.md 索引 generator——條目檔 frontmatter 是單一 source，索引是其機械投影。
# 用法: python3 _generate_index.py [--check]（--check 只驗證不寫入、零檔案系統副作用）
# Gate: 產物 >18,500 字元、>24,000 bytes 或 >190 行 → fail-loud exit 1（不寫入）。
# 單位實證：harness 載入限「前 200 行或 25KB」（24.4KiB≈24,985，chars/bytes 兩讀同值），
# 雙 harness 實證以 chars 計（2026-08-30：42,110 chars/56,604 bytes 檔案報「41KB over
# 24.4KB」——41K 只能對上 chars；ZCode session 警示 26.4K chars 同口徑）；
# bytes 維度是對「以 bytes 計」讀法的縱深防禦。寫入用 unique tmp（os.getpid()）
# ＋只清 aged（>60s）殘檔——並行 process 的 in-flight tmp 不被誤殺。
# 2026-09-01 chars gate 17,000→18,500（harness 線內 ~25% 餘裕）：寫入治理
# hook 上線（block-memory-index-write.py 擋 desc>120/膨脹>12,000）後流入率
# 下降，原 17,000 餘裕（~700）只撐一天（08-31 晚 16,308 → 隔晨 17,269 撞線）。
# （hook 僅攔主 session——subagent 寫入不觸發；「流入率下降」以主 session 寫入為主）
# description 截斷 140→120 對齊 hook DESC_LIMIT（>120 在寫入端已擋，此為存量縱深）。
# 條目 frontmatter 必含 name / description / type（頂層 `type:` 或 `metadata.type:` 皆可）。
# 語言層約束：跑在 hook runtime 系統 python3 3.9——禁 PEP 604（X | None）等 3.10+ 語法。
import os
import pathlib
import sys
import time

GATE_CHARS = 18_500
TRUNCATE_DESC = 120  # desc 截斷線——須 == hooks/block-memory-index-write.py DESC_LIMIT（tests cross-layer 錨）
GATE_BYTES = 24_000
GATE_LINES = 190
ORDER = [
    ("user", "User"),
    ("feedback", "Feedback"),
    ("project", "Project"),
    ("reference", "Reference"),
]


def parse_frontmatter(text: str) -> dict:
    if not text.startswith(("---\n", "---\r\n")):
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        return {}
    out: dict = {}
    parent = None
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            k, _, v = line.strip().partition(":")
            if parent:
                out[f"{parent}.{k.strip()}"] = v.strip()
            continue
        k, _, v = line.partition(":")
        parent = k.strip() if not v.strip() else None
        out[k.strip()] = v.strip().strip("'\"")
    return out


def main() -> int:
    here = pathlib.Path(__file__).resolve().parent
    check_only = "--check" in sys.argv
    errs, entries = [], []
    for f in sorted(here.glob("*.md")):
        if f.name == "MEMORY.md" or f.name.startswith("_"):
            continue
        fm = parse_frontmatter(f.read_text(encoding="utf-8"))
        typ = fm.get("type") or fm.get("metadata.type")
        desc = " ".join((fm.get("description") or "").split())
        if not (fm.get("name") and desc and typ in dict(ORDER)):
            errs.append(f"  {f.name}: type={typ!r}")
            continue
        hook = desc if len(desc) <= TRUNCATE_DESC else desc[: TRUNCATE_DESC - 1] + "…"
        entries.append((typ, f.stem, f.name, hook))
    if errs:
        print(
            "[FAIL] frontmatter 違規（需 name/description/type∈user|feedback|project|reference）:"
        )
        print("\n".join(errs))
        return 1
    lines = [
        "# Memory Index",
        "",
        "本檔為 _generate_index.py 機械投影，禁手寫（PreToolUse gate）——改條目檔後重跑 generator。",
        "",
    ]
    for typ, title in ORDER:
        group = [e for e in entries if e[0] == typ]
        if not group:
            continue
        lines.append(f"## {title}")
        lines.append("")
        lines.extend(f"- [{stem}]({name}) - {hook}" for _, stem, name, hook in group)
        lines.append("")
    content = "\n".join(lines).rstrip() + "\n"
    n_chars, n_lines = len(content), content.count("\n")
    n_bytes = len(content.encode("utf-8"))
    if n_chars > GATE_CHARS or n_lines > GATE_LINES or n_bytes > GATE_BYTES:
        print(
            f"[FAIL] gate 超限: {n_chars} chars (>{GATE_CHARS}) / {n_bytes} bytes"
            f" (>{GATE_BYTES}) / {n_lines} lines (>{GATE_LINES})——先 cluster merge/收斂再生成"
        )
        return 1
    if check_only:
        print(
            f"[OK] {len(entries)} entries, {n_chars} chars, {n_bytes} bytes, {n_lines} lines（--check 未寫入）"
        )
        return 0
    # 只清 aged 殘檔（>60s）——不碰並行 process 的 in-flight tmp；--check 分支已 return
    now = time.time()
    for stale in here.glob("MEMORY.md.*.tmp"):
        try:
            if now - stale.stat().st_mtime > 60:
                stale.unlink()
        except OSError:
            pass
    tmp = here / f"MEMORY.md.{os.getpid()}.tmp"
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(here / "MEMORY.md")
    print(
        f"[OK] MEMORY.md 已重生成: {len(entries)} entries, {n_chars} chars, {n_bytes} bytes, {n_lines} lines"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
