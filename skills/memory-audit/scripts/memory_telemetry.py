"""Read-only memory telemetry collector (AIR-40 S1: events + coverage).

Drives normalized write/read events out of ZCode db.sqlite part rows and
Claude transcript JSONL without touching sources. Scope is S1 only:
event/identity/coverage JSON. Ranking projection is S2 and consumes this
output. See ai-analysis/_tasks/09-07-memory-governance/write-attribution/ep.md.
"""

import argparse
import hashlib
import json
import sqlite3
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

SCHEMA = 1
TOOLS = ("Read", "Write", "Edit")


@dataclass
class Event:
    source: str  # zcode | claude
    id: str
    session: str
    parent: str | None
    task_type: str | None
    tool: str
    status: str  # completed | error | unmatched | unknown
    operation_start: str | None
    operation_end: str | None
    record_time: str
    time_source: str  # operation | record_fallback
    raw_path: str
    canonical_path: str | None
    entry: str
    payload_chars: int
    input_sha256: str
    call_id: str | None
    prior_known: bool = False
    net_delta: int | None = None
    copy_of: str | None = None
    actor: str = "unknown"
    source_ref: dict = field(default_factory=dict)
    read_range: dict | None = None


@dataclass
class Coverage:
    zcode: dict = field(default_factory=dict)
    claude: dict = field(default_factory=dict)
    pools: list = field(default_factory=list)


def parse_ts(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000, UTC)
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def iso(dt):
    return dt.astimezone(UTC).isoformat() if dt else None


def in_window(dt, since, until):
    return dt is not None and since <= dt < until


def resolve_pool_entry(pools, raw, cwd=None):
    """Return (canonical_path, entry) or (None, None) when outside pools."""
    if not raw:
        return None, None
    p = Path(raw).expanduser()
    if not p.is_absolute():
        if not cwd:
            return None, None
        p = Path(cwd) / p
    try:
        rp = p.resolve()
    except OSError:
        return None, None
    for pool in pools:
        try:
            if (
                rp.parent == pool
                and rp.name != "MEMORY.md"
                and not rp.name.startswith("_")
            ):
                return str(rp), rp.name
        except OSError:
            continue
    return None, None


def read_zcode(db_path, pools, since, until):
    events, coverage = [], {"readable": False}
    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    except sqlite3.Error as exc:
        coverage.update(readable=False, error=str(exc))
        return events, coverage
    try:
        con.execute("BEGIN")
        bounds = con.execute(
            "select min(time_created), max(time_created), count(*) from part"
        ).fetchone()
        coverage["bounds"] = {
            "first": iso(parse_ts(bounds[0])),
            "last": iso(parse_ts(bounds[1])),
            "global_parts": bounds[2],
        }
        sessions = {
            r[0]: (r[1], r[2])
            for r in con.execute("select id, parent_id, task_type from session")
        }
        rows = con.execute(
            """select p.id, p.session_id, p.time_created, p.data
            from part p where p.time_created >= ? and p.time_created < ?
            and json_extract(p.data, '$.type') = 'tool'
            order by p.time_created, p.id""",
            (int(since.timestamp() * 1000), int(until.timestamp() * 1000)),
        ).fetchall()
    finally:
        con.close()
    coverage["readable"] = True
    coverage["rows_scanned"] = len(rows)
    coverage["unknown_shapes"] = 0
    for pid, sid, ts_ms, raw in rows:
        try:
            d = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            coverage["unknown_shapes"] += 1
            continue
        if not isinstance(d, dict) or d.get("tool") not in TOOLS:
            coverage["unknown_shapes"] += 1
            continue
        state = d.get("state") or {}
        if not isinstance(state, dict):
            coverage["unknown_shapes"] += 1
            continue
        inp = state.get("input") or {}
        canon, entry = resolve_pool_entry(pools, inp.get("file_path"))
        if canon is None:
            continue
        op = state.get("time") or {}
        op_start = parse_ts(op.get("start")) if isinstance(op, dict) else None
        op_end = parse_ts(op.get("end")) if isinstance(op, dict) else None
        record = parse_ts(ts_ms)
        if op_start is not None and in_window(op_start, since, until):
            flag = "operation"
        else:
            flag = "record_fallback"
        status = state.get("status")
        status = status if status in ("completed", "error") else "unknown"
        parent, task = sessions.get(sid, (None, None))
        payload = inp.get("content", inp.get("new_string", ""))
        events.append(
            Event(
                source="zcode",
                id=pid,
                session=sid,
                parent=parent,
                task_type=task,
                tool=d["tool"],
                status=status,
                operation_start=iso(op_start),
                operation_end=iso(op_end),
                record_time=iso(record),
                time_source=flag,
                raw_path=str(inp.get("file_path")),
                canonical_path=canon,
                entry=entry,
                payload_chars=len(payload) if isinstance(payload, str) else 0,
                input_sha256=hashlib.sha256(
                    json.dumps(inp, sort_keys=True).encode()
                ).hexdigest(),
                call_id=d.get("callID"),
                actor=sid if sid in sessions else "unknown",
                source_ref={"db": str(db_path), "row": pid},
                read_range=(
                    {k: inp[k] for k in ("offset", "limit") if k in inp} or None
                )
                if d["tool"] == "Read"
                else None,
            )
        )
    return events, coverage


def read_claude(roots, pools, since, until):
    events = []
    coverage = {
        "requested": True,
        "readable": True,
        "files": 0,
        "malformed": 0,
        "bounds": {"first": None, "last": None},
        "scope": "explicit --cc-root only; removed worktree dirs not enumerated unless passed",
    }
    seen_ts = []
    for root in roots:
        root = Path(root)
        if not root.is_dir():
            coverage["readable"] = False
            coverage.setdefault("missing", []).append(str(root))
            continue
        for path in sorted(root.rglob("*.jsonl")):
            coverage["files"] += 1
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                coverage.setdefault("unreadable", []).append(str(path))
                continue
            pending, results = {}, {}
            for line_no, line in enumerate(text.splitlines(), 1):
                if not line.strip():
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    coverage["malformed"] += 1
                    continue
                if not isinstance(d, dict):
                    coverage["malformed"] += 1
                    continue
                ts = parse_ts(d.get("timestamp"))
                if ts is not None:
                    seen_ts.append(ts)
                blocks = (d.get("message") or {}).get("content", [])
                if not isinstance(blocks, list):
                    continue
                sid = d.get("sessionId", path.stem)
                for block in blocks:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "tool_result" and block.get("tool_use_id"):
                        results[(str(path), sid, block["tool_use_id"])] = (
                            "error" if block.get("is_error") else "completed"
                        )
                    if block.get("type") != "tool_use":
                        continue
                    if block.get("name") not in TOOLS:
                        continue
                    inp = block.get("input") or {}
                    canon, entry = resolve_pool_entry(
                        pools, inp.get("file_path"), d.get("cwd")
                    )
                    if canon is None or ts is None or not in_window(ts, since, until):
                        continue
                    payload = inp.get("content", inp.get("new_string", ""))
                    pending[(str(path), sid, block.get("id"))] = Event(
                        source="claude",
                        id=str(block.get("id")),
                        session=sid,
                        parent=None,
                        task_type=None,
                        tool=block["name"],
                        status="unmatched",
                        operation_start=iso(ts),
                        operation_end=iso(ts),
                        record_time=iso(ts),
                        time_source="operation",
                        raw_path=str(inp.get("file_path")),
                        canonical_path=canon,
                        entry=entry,
                        payload_chars=len(payload) if isinstance(payload, str) else 0,
                        input_sha256=hashlib.sha256(
                            json.dumps(inp, sort_keys=True).encode()
                        ).hexdigest(),
                        call_id=str(block.get("id")),
                        source_ref={
                            "file": str(path),
                            "line": line_no,
                        },
                        read_range=(
                            {k: inp[k] for k in ("offset", "limit") if k in inp} or None
                        )
                        if block["name"] == "Read"
                        else None,
                    )
            for key, event in pending.items():
                event.status = results.get(key, "unmatched")
                events.append(event)
    if seen_ts:
        coverage["bounds"] = {"first": iso(min(seen_ts)), "last": iso(max(seen_ts))}
    return events, coverage


def resolve_lineage(events, sessions):
    """Fold fork/side-chat copies. Returns (canonical, aliases, ambiguous)."""

    def ancestors(sid):
        chain, seen = [], set()
        while sid and sid not in seen:
            seen.add(sid)
            parent, _ = sessions.get(sid, (None, None))
            if not parent:
                break
            chain.append(parent)
            sid = parent
        return set(chain)

    groups = {}
    for e in events:
        if e.tool not in ("Write", "Edit") or e.status != "completed":
            continue
        key = (
            e.tool,
            e.canonical_path,
            e.input_sha256,
            e.operation_start,
            e.operation_end,
        )
        groups.setdefault(key, []).append(e)
    aliases, ambiguous = [], []
    for members in groups.values():
        by_session = {m.session for m in members}
        if len(by_session) < 2:
            continue
        folded = False
        for m in members:
            older = [
                o for o in members if o is not m and o.session in ancestors(m.session)
            ]
            if older:
                first = min(older, key=lambda o: (o.record_time, o.id))
                m.copy_of = first.id
                aliases.append(
                    {"copy": m.id, "canonical": first.id, "basis": "lineage+time+hash"}
                )
                folded = True
        if not folded:
            ambiguous.append(
                {
                    "members": [m.id for m in members],
                    "reason": "multi-session same content without ancestor link",
                }
            )
    canonical = [e for e in events if e.copy_of is None]
    return canonical, aliases, ambiguous


def generator_identity(pool: Path) -> str:
    g = pool / "_generate_index.py"
    if not g.is_file():
        return "absent"
    return hashlib.sha256(g.read_bytes()).hexdigest()[:12]


def snapshot_index(pools) -> dict:
    snaps = {}
    for pool in pools:
        mem = pool / "MEMORY.md"
        text = mem.read_text(encoding="utf-8") if mem.is_file() else ""
        entry_names = sorted(
            p.name
            for p in pool.glob("*.md")
            if p.name != "MEMORY.md" and not p.name.startswith("_")
        )
        snaps[str(pool)] = {
            "generator_schema": generator_identity(pool),
            "index_chars": len(text),
            "index_lines": text.count("\n"),
            "entry_count": len(entry_names),
            "entries": entry_names,
        }
    return snaps


def index_delta_with_baseline(pools, baseline_dir: Path):
    if baseline_dir is None:
        return {
            "value": None,
            "reason": "index baseline disabled (pass --baseline-dir to enable)",
            "baseline_written": [],
            "incomparable": None,
        }
    written, reasons, pool_deltas, incomparable = [], [], {}, []
    now = snapshot_index(pools)
    for pool_key, snap in now.items():
        key = pool_key.replace("/", "_")
        bfile = baseline_dir / f"{key}.json"
        if not bfile.is_file():
            reasons.append(f"no prior baseline for {pool_key}; baseline created")
        else:
            try:
                prev = json.loads(bfile.read_text(encoding="utf-8"))
            except (ValueError, OSError):
                reasons.append(f"unreadable baseline for {pool_key}")
                incomparable.append(pool_key)
                prev = None
            if prev is not None:
                if prev.get("generator_schema") != snap["generator_schema"]:
                    reasons.append(f"incomparable generator identity for {pool_key}")
                    incomparable.append(pool_key)
                else:
                    pool_deltas[pool_key] = {
                        k: snap[k] - prev.get(k, 0)
                        for k in ("index_chars", "index_lines", "entry_count")
                    }
        baseline_dir.mkdir(parents=True, exist_ok=True)
        bfile.write_text(
            json.dumps(snap, ensure_ascii=False, sort_keys=True), encoding="utf-8"
        )
        written.append(str(bfile))
    # partial semantics: with multiple pools, value sums only comparable pools
    # — consumers must check "partial" before reading it as a total.
    if pool_deltas:
        value = {
            k: sum(d[k] for d in pool_deltas.values())
            for k in ("index_chars", "index_lines", "entry_count")
        }
        value["pools"] = pool_deltas
        value["partial"] = len(pool_deltas) < len(now)
    else:
        value = None
    return {
        "value": value,
        "reason": "; ".join(reasons) or None,
        "baseline_written": written,
        "incomparable": incomparable or None,
    }


def project_writes(canonical, aliases, ambiguous, pools, baseline_dir):
    successful = [
        e for e in canonical if e.status == "completed" and e.tool in ("Write", "Edit")
    ]
    # errors share the Write/Edit scope with successful; CC unmatched pairs are
    # in-flight, not failures — counted separately, never as write errors.
    errors = [
        e for e in canonical if e.status == "error" and e.tool in ("Write", "Edit")
    ]
    unmatched = [
        e for e in canonical if e.status == "unmatched" and e.tool in ("Write", "Edit")
    ]
    by_entry, by_actor = {}, {}
    for e in successful:
        ent = by_entry.setdefault(
            e.entry, {"entry": e.entry, "successful_writes": 0, "payload_chars": 0}
        )
        ent["successful_writes"] += 1
        ent["payload_chars"] += e.payload_chars
        act = by_actor.setdefault(
            e.actor, {"actor": e.actor, "successful_writes": 0, "payload_chars": 0}
        )
        act["successful_writes"] += 1
        act["payload_chars"] += e.payload_chars
    top_entries = sorted(
        by_entry.values(), key=lambda r: (-r["payload_chars"], r["entry"])
    )
    top_actors = sorted(
        by_actor.values(), key=lambda r: (-r["payload_chars"], r["actor"])
    )
    snaps = snapshot_index(pools)
    inventory_entries = [
        {"entry": name, "pool": pk}
        for pk, snap in snaps.items()
        for name in snap["entries"]
    ]
    return {
        "schema": SCHEMA,
        "inventory_timestamp": max(
            (e.record_time for e in successful if e.record_time),
            default=None,
        ),
        "counts": {
            "events_total": len(canonical),
            "successful": len(successful),
            "errors": len(errors),
            "unmatched": len(unmatched),
            "copies_folded": len(aliases),
            "ambiguous": len(ambiguous),
        },
        "top_actors": top_actors,
        "top_entries": top_entries,
        "net_file_delta": {
            "value": None,
            "reason": (
                "no proven before-image for Write/Edit; payload_chars is flow, "
                "not stock"
            ),
        },
        "index_delta": index_delta_with_baseline(pools, baseline_dir),
        "current_inventory": {"entries": inventory_entries},
    }


RANKS = ("hot", "core", "cold")


def _frontmatter_rank(text):
    """Behavioral mirror of the pool generator's parse_frontmatter+parse_rank.

    Equivalence contract (pinned by test_i1/test_i1b): requires a leading
    '---' fence, the frontmatter block ends at the first closing '\\n---'
    (body fences never leak in), only 'metadata:' indented children (not
    other parents) feed the nested placement, a top-level rank with a value
    wins over metadata.rank. Normalization mirrors the generator's two
    layers: parse_frontmatter unquotes TOP-LEVEL values only, then
    parse_rank strips+unquotes+lowercases once — so a quoted top-level
    ' hot ' ends up hot (double-pass) while the same nested value stays
    core (single-pass leaves inner whitespace). Invalid or missing -> core.
    The per-pool generator hash rides along as generator_schema (report
    "generators" map), so consumers can detect mirror drift.
    """
    if not text.startswith(("---\n", "---\r\n")):
        return "core"
    end = text.find("\n---", 4)
    if end < 0:
        return "core"
    top = meta = None
    parent = None
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            k, _, v = line.strip().partition(":")
            if parent == "metadata" and k.strip() == "rank" and v.strip():
                meta = v.strip()  # generator keeps nested values raw
            continue
        k, _, v = line.partition(":")
        parent = k.strip() if not v.strip() else None
        if k.strip() == "rank" and v.strip():
            top = v.strip().strip("'\"")  # generator unquotes top-level
    raw = top or meta
    val = str(raw).strip().strip("'\"").lower() if raw is not None else ""
    return val if val in RANKS else "core"


def snapshot_entries(pools):
    """Inventory with content hash / rank / mtime (AIR-41 S1)."""
    inv = []
    for pool in pools:
        for p in sorted(pool.glob("*.md")):
            if p.name == "MEMORY.md" or p.name.startswith("_"):
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except OSError:
                continue
            inv.append(
                {
                    "entry": p.name,
                    "pool": str(pool),
                    "sha256": hashlib.sha256(text.encode()).hexdigest(),
                    "rank": _frontmatter_rank(text),
                    "mtime": iso(datetime.fromtimestamp(p.stat().st_mtime, tz=UTC)),
                }
            )
    return inv


def project_reads(canonical, inventory, coverages, since, until):
    """AIR-41 S1/S2: body-Read observation + coverage-limited candidates."""
    reads_by_entry = {}
    read_errors = 0
    unpaired = 0
    for e in canonical:
        if e.tool != "Read":
            continue
        if e.status == "error":
            read_errors += 1
            continue
        if e.entry == "MEMORY.md":
            continue  # index file, not an entry (EP S1)
        # unmatched (CC result missing) / unknown (zcode state absent) Reads
        # still count as contact — dropping them would flip genuinely read
        # entries into zero-body-read candidates (directional error).
        if e.status != "completed":
            unpaired += 1
        reads_by_entry.setdefault(e.entry, []).append(
            {
                "source": e.source,
                "session": e.session,
                "actor": e.actor,
                "ts": e.operation_start or e.record_time,
                "status": e.status,
                "partial": e.read_range is not None,
                "range": e.read_range,
                "source_ref": e.source_ref,
            }
        )
    cutoff = until - timedelta(days=30)
    observations, no_body = [], []
    for item in inventory:
        name = item["entry"]
        body = reads_by_entry.get(name, [])
        mtime = parse_ts(item["mtime"])
        exemptions = {
            "hot": item["rank"] == "hot",
            "recent_30d": mtime is not None and mtime >= cutoff,
        }
        observations.append(
            {
                "entry": name,
                "body_reads": body,
                "zero_body_read": not body,
            }
        )
        if not body:
            no_body.append(
                {
                    "entry": name,
                    "rank": item["rank"],
                    "mtime": item["mtime"],
                    "exemptions": exemptions,
                }
            )
    inventory_names = {item["entry"] for item in inventory}
    reads_without_entry = sorted(set(reads_by_entry) - inventory_names)
    firsts = []
    for db_cov in coverages.get("zcode_dbs", []):
        if db_cov.get("readable"):
            first = parse_ts((db_cov.get("bounds") or {}).get("first"))
            if first:
                firsts.append(first)
    cc_first = parse_ts((coverages.get("claude", {}).get("bounds") or {}).get("first"))
    if cc_first:
        firsts.append(cc_first)
    # window_shortfall: a source whose earliest record post-dates --since
    # cannot testify about the start of the window — zero-read conclusions
    # there are coverage-limited, not evidence of disuse.
    coverages["window_shortfall"] = any(first > since for first in firsts)
    coverages["unpaired_reads"] = unpaired
    partial = (
        not (
            coverages.get("zcode", {}).get("readable")
            and coverages.get("claude", {}).get("requested")
        )
        or coverages["window_shortfall"]
    )
    coverages["partial"] = partial
    coverages["read_errors"] = read_errors
    coverages["instrumented"] = [
        s
        for s in ("zcode", "claude")
        if coverages.get(s, {}).get("readable") or coverages.get(s, {}).get("requested")
    ]
    # static manifest — not probed at runtime; extend only when a harness
    # gains a readable telemetry source
    coverages["uninstrumented"] = ["codex", "muse", "bash-rg"]
    return {
        "inventory": inventory,
        "observations": observations,
        "candidates": {
            "no_body_read": no_body,
            "coverage_limited": partial,
            # reads of entries absent from inventory: rename/delete identity
            # clue (EP R6) — HOLD material for LLM adjudication, never
            # auto-merged. maintenance-only / purpose classification stays
            # LLM-side (skill); the collector emits no fake empty slot.
            "reads_without_entry": reads_without_entry,
        },
    }


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Read-only memory telemetry (AIR-40 S1)"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    w = sub.add_parser("writes", help="emit normalized events + coverage JSON")
    w.add_argument("--pool", action="append", required=True)
    w.add_argument("--zcode-db", action="append", default=[])
    w.add_argument("--cc-root", action="append", default=[])
    w.add_argument("--since", default=None)
    w.add_argument("--until", default=None)
    w.add_argument("--output", required=True)
    w.add_argument(
        "--baseline-dir",
        default=None,
        help="enable index-delta snapshots in this directory (default: disabled)",
    )
    rd = sub.add_parser("reads", help="body-Read observation (AIR-41)")
    rd.add_argument("--pool", action="append", required=True)
    rd.add_argument("--zcode-db", action="append", default=[])
    rd.add_argument("--cc-root", action="append", default=[])
    rd.add_argument("--since", default=None)
    rd.add_argument("--until", default=None)
    rd.add_argument("--output", required=True)
    return parser.parse_args(argv)


def fail(message, code=2):
    sys.stderr.write(json.dumps({"schema": SCHEMA, "error": message}) + "\n")
    return code


def main(argv=None):
    args = parse_args(argv)
    pools = []
    for raw in args.pool:
        p = Path(raw).expanduser()
        if not p.is_dir():
            return fail(f"pool not a directory: {raw}")
        pools.append(p.resolve())
    out = Path(args.output).expanduser()
    try:
        out_resolved = out.resolve()
    except OSError:
        out_resolved = out.absolute()
    for protected in pools + [
        Path(p).expanduser() for p in args.zcode_db + args.cc_root
    ]:
        try:
            if out_resolved == protected or protected in out_resolved.parents:
                return fail(f"output inside sources refused: {args.output}")
        except OSError:
            continue
    until = (
        parse_ts(args.until) if args.until else datetime.now(UTC).replace(microsecond=0)
    )
    default_days = 90 if args.command == "reads" else 7
    since = parse_ts(args.since) if args.since else until - timedelta(days=default_days)
    if since is None or until is None or since >= until:
        return fail("invalid --since/--until window")
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return fail(f"cannot create output dir: {exc}")
    events, coverages, sessions = [], {}, {}
    if args.zcode_db:
        for db_path in args.zcode_db:
            if not Path(db_path).is_file():
                return fail(f"zcode db unreadable: {db_path}")
        for db_path in args.zcode_db:
            z_events, z_cov = read_zcode(db_path, pools, since, until)
            events.extend(z_events)
            coverages.setdefault("zcode_dbs", []).append(
                {"path": str(db_path), **z_cov}
            )
    else:
        coverages["zcode_dbs"] = [{"requested": False}]
    zcovs = [c for c in coverages.get("zcode_dbs", []) if c.get("readable")]
    coverages["zcode"] = {
        "readable": bool(zcovs) if args.zcode_db else False,
        "rows_scanned": sum(c.get("rows_scanned", 0) for c in zcovs),
        "unknown_shapes": sum(c.get("unknown_shapes", 0) for c in zcovs),
    }
    if args.cc_root:
        c_events, c_cov = read_claude(args.cc_root, pools, since, until)
        events.extend(c_events)
        coverages["claude"] = c_cov
        if c_cov.get("missing"):
            return fail(f"cc roots missing: {c_cov['missing']}")
    else:
        coverages["claude"] = {"requested": False}
    coverages["pools"] = [str(p) for p in pools]
    for db_path in args.zcode_db:
        try:
            con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            for sid, parent, task in con.execute(
                "select id, parent_id, task_type from session"
            ):
                sessions[sid] = (parent, task)
            con.close()
        except sqlite3.Error:
            pass
    canonical, aliases, ambiguous = resolve_lineage(events, sessions)
    unknown = sorted(
        {e.session for e in events if e.actor == "unknown" and e.session != "unknown"}
    )
    events.sort(key=lambda e: (e.record_time or "", e.id))
    if args.command == "reads":
        inventory = snapshot_entries(pools)
        projection = project_reads(canonical, inventory, coverages, since, until)
        report = {
            "schema": SCHEMA,
            "window": {"start": iso(since), "end": iso(until)},
            "coverage": coverages,
            # the rank mirror above is a behavioral copy of the per-pool
            # generator; its hash rides along so consumers can detect drift
            "generators": {str(p): generator_identity(p) for p in pools},
            "aliases": aliases,
            "ambiguous": ambiguous,
            "unknown": unknown,
            **projection,
        }
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        obs = projection["observations"]
        zero = len(projection["candidates"]["no_body_read"])
        print(
            f"[OK] entries={len(inventory)} body_read_entries="
            f"{sum(1 for o in obs if o['body_reads'])} zero_body_read={zero} "
            f"read_errors={coverages.get('read_errors', 0)} "
            f"unpaired_reads={coverages.get('unpaired_reads', 0)} "
            f"window_shortfall={coverages.get('window_shortfall')} "
            f"partial={coverages.get('partial')}"
        )
        return 0
    baseline_dir = Path(args.baseline_dir).expanduser() if args.baseline_dir else None
    projection = project_writes(canonical, aliases, ambiguous, pools, baseline_dir)
    report = {
        "schema": SCHEMA,
        "window": {"start": iso(since), "end": iso(until)},
        "coverage": coverages,
        "events": [asdict(e) for e in canonical]
        + [{**asdict(e), "folded": True} for e in events if e.copy_of is not None],
        "aliases": aliases,
        "ambiguous": ambiguous,
        "unknown": unknown,
        "report": projection,
    }
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(
        f"[OK] events={len(report['events'])} aliases={len(aliases)} "
        f"ambiguous={len(ambiguous)} unknown_actors={len(unknown)} "
        f"successful={projection['counts']['successful']} "
        f"errors={projection['counts']['errors']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
