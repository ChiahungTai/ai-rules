#!/usr/bin/env python3
# MEMORY.md 索引 generator——條目檔 frontmatter 是單一 source，索引是其機械投影。
# 用法: python3 _generate_index.py [--check]（--check 只驗證不寫入、零檔案系統副作用）
# Gate 分級（2026-09-03 裁決「zcode 優先」——ZCode 為主力 harness）：
#   硬 gate（fail-loud exit 1＋行動訊息；超限時**索引照寫出**〔--check 除外〕——
#     2026-09-05 S1/AIR-25 改 CC 式，官方 memory.md:401-403「write still succeeds +
#     error telling Claude to rewrite」；size gate 拒寫會停滯索引＝新條目不可見＝
#     召回斷裂。**errs 路徑（frontmatter 違規）同 CC 式（AIR-27）**：壞條目跳過、
#     合法條目照常寫出＋exit 1 列名壞檔——一個壞檔不擋全部條目投影：
#     >22,500 字元 或 >190 行——守兩端共同截斷線（200 行／25,000 字元）
#   bytes info（照常寫入、exit 0）：>24,000 bytes 印 [INFO] 一行——縱深預警
#     （非任何 harness 的實際截斷線：兩端皆量 chars；CJK 一字 3B，bytes 提前折射）
# 載入上限實證（2026-09-03 雙端源碼反組譯、CLI 三版同構；共用池＝ZCode symlink→Claude 實體）：
#   兩端同語義＝200 行 或 25,000 字元（UTF-16 code units，CJK 一字計 1）：
#     ZCode zcode.cjs：Vut=200／mre=25e3（Wut()：o=t.length 比較）
#     Claude versions/<v>：YD=200／GF=25000（mLe() 回傳 byteCount:t.length——
#       欄位名叫 byteCount、計量是 .length＝chars；TextEncoder 在另一 scope 屬
#       crypto——欄位名≠計量方式，minified 跨 scope 撞名勿再誤讀）
#   兩端超限皆截斷＋附 WARNING（非靜默）；「25KB」假象＝警告以 25000/1024 顯示 "24.4KB"
#   重跑驗證（drift 防護——量詞須彈性：常數前綴不足 100 字元，.{100} 會 0 hits）：
#     rg -a -o '.{30}mre=[0-9*]+.{30}' /Applications/ZCode.app/Contents/Resources/glm/zcode.cjs
#     rg -a -o '.{0,100}YD=200,GF=25000.{0,60}' ~/.local/share/claude/versions/<最新版>
#     計量實作：perl -0777 -ne 'if (/(function mLe\(e\)\{.{0,300})/s){my $x=$1;$x=~s/\n/\\n/g;print "$x\n"}' <該版檔>
# 2026-09-06 輸出行附 gate 值（OK 兩路徑＋size FAIL 附超限比值）：nightly-watch 假警——
#   輸出不含 gate 值時，消費 session 轉引 _audit-state.md prose 舊值（18,500 vs 真值
#   22,500）＝輸出真空由 prose 填補（09-02 同型第二次）。輸出自足＝就地校驗。
# 寫入用 unique tmp（os.getpid()）＋只清 aged（>60s）殘檔——並行 process 的 in-flight
# tmp 不被誤殺。
# 2026-09-01 chars gate 17,000→18,500（harness 線內 ~25% 餘裕）：寫入治理
# hook 上線（block-memory-index-write.py 擋 desc>120/膨脹>12,000）後流入率
# 下降，原 17,000 餘裕（~700）只撐一天（08-31 晚 16,308 → 隔晨 17,269 撞線）。
# （hook 僅攔主 session——subagent 寫入不觸發；「流入率下降」以主 session 寫入為主）
# 2026-09-03 晚 chars gate 18,500→22,500（真線 90%）：寫入原則配套＋每日夜間收斂
# cron 承接流出（user 裁定「有進有出」）——gate 即時閥語義下餘裕＝收斂反應時間，
# 夜間收斂前置清理使 jam 罕見，放寬安全。
# description 截斷線隨 hook DESC_LIMIT：140→120（09-01）→100（09-03 P1：硬限對齊
# 紀律值）——寫入端已擋，此為存量縱深。
# 條目 frontmatter 必含 name / description / type（頂層 `type:` 或 `metadata.type:` 皆可）。
# 語言層約束：跑在 hook runtime 系統 python3 3.9——禁 PEP 604（X | None）等 3.10+ 語法。
import os
import pathlib
import sys
import time

GATE_CHARS = 22_500
TRUNCATE_DESC = 100  # desc 截斷線——須 == hooks/block-memory-index-write.py DESC_LIMIT（tests cross-layer 錨）
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


def write_index(here: pathlib.Path, content: str) -> None:
    """aged 殘檔清理＋tmp+replace 原子寫（只清 >60s 殘檔——並行 in-flight tmp 不誤殺）。"""
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
    info = (
        f"[INFO] bytes {n_bytes} > {GATE_BYTES} — 縱深預警（兩端截斷線皆 25,000 chars；CJK 一字 3B，bytes 提前折射）\n"
        if n_bytes > GATE_BYTES
        else ""
    )
    if errs:
        print(
            info
            + "[FAIL] frontmatter 違規（需 name/description/type∈user|feedback|project|reference）"
            f"——{len(errs)} 檔跳過、未進索引：\n"
            + "\n".join(errs)
            + "\n[提示] 索引已以合法條目照常寫出（CC 式——壞條目不擋投影，AIR-27）；修好後重跑"
        )
        if not check_only:  # --check 零副作用（與 size gate 同 guard）
            write_index(here, content)
        return 1
    if n_chars > GATE_CHARS or n_lines > GATE_LINES:
        wrote = ""
        if not check_only:  # --check 零副作用語義不變（SM-2 guard）
            write_index(here, content)
            wrote = "——索引已寫出（不停滯）"
        print(
            info
            + f"[FAIL] gate 超限: {n_chars} chars (>{GATE_CHARS}, {n_chars / GATE_CHARS:.1%})"
            f" / {n_lines} lines (>{GATE_LINES}, {n_lines / GATE_LINES:.1%}){wrote}。當下 session 需縮：merge or drop stale 條目"
            "（可推導內容歸 repo/git——skip-derivable），縮後重跑"
        )
        return 1
    if check_only:
        print(
            info
            + f"[OK] {len(entries)} entries, {n_chars} chars, {n_bytes} bytes, {n_lines} lines"
            f"（gate: {GATE_CHARS} chars／{GATE_BYTES} bytes／{GATE_LINES} 行；--check 未寫入）"
        )
        return 0
    write_index(here, content)
    print(
        info
        + f"[OK] MEMORY.md 已重生成: {len(entries)} entries, {n_chars} chars, {n_bytes} bytes, {n_lines} lines"
        f"（gate: {GATE_CHARS} chars／{GATE_BYTES} bytes／{GATE_LINES} 行）"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
