#!/usr/bin/env python3
"""
Unified Project Knowledge Scanner.

Produces three things (no full registries — LLM reads files directly):
1. dep_graph — AST-parsed Python import relationships
2. findings — mechanical cross-validation issues (X-cap-path, X-tag-module, etc.)
3. fingerprint — lightweight change detection (counts + hashes)

Internal parsing of instruction files (AGENTS.md preferred, CLAUDE.md legacy) and .kanban/ is kept for computing findings,
but registries are NOT included in output.

Designed for the /scan-project skill + /daily-maintain or /project-review workflow.

Usage:
    uv run python scan_project.py --project-root . --output .project-snapshot.json
    uv run python scan_project.py --init --project-root /path/to/project
"""

import argparse
from collections import defaultdict
from datetime import datetime
from datetime import timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import tomllib


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SKIP_DIRS_SCAN = {
    ".venv",
    "venv",
    "__pycache__",
    ".git",
    "node_modules",
    ".mypy_cache",
    ".ruff_cache",
    ".idea",
    "_archive",
    ".claude",
    "build",
    "dist",
    "ref-docs",  # external harness mirrors — not this repo's instructions
}

# Top-level dirs that may carry __init__.py but are never the importable
# package root. Used only by the _find_package_root fallback to avoid picking
# tests/ (which often has more .py files than the real package).
NON_PACKAGE_DIRS = {"tests", "test", "docs", "examples", "stubs"}

KANBAN_LANES = {"Backlog", "Next-Up", "In-Progress", "Done"}
ACTIVE_KANBAN_LANES = KANBAN_LANES - {"Done"}

# [tag:module] on first line of kanban cards
TAG_RE = re.compile(r"\[tag:([^\]]+)\]")

# EP reference in ## 相關 section
EP_REF_RE = re.compile(r"^- EP:\s*`?([^`*\n]+)`?", re.MULTILINE)

# Capabilities table header detection
CAPABILITIES_HEADER_RE = re.compile(r"^##\s+Capabilities", re.MULTILINE)

# Markdown table row detection: starts and ends with |
TABLE_ROW_START = re.compile(r"^\|.*\|\s*$")

# Note: UC ID pattern removed — Capabilities tables now use 3-column format
# (能力 | 入口 | 狀態) without UC ID numbering.


# ---------------------------------------------------------------------------
# Import scan_imports if available (graceful degradation)
# ---------------------------------------------------------------------------


def _load_scan_imports(project_root: Path) -> dict | None:
    """Try to import and run scan_imports.scan_project from the target project."""
    candidates = [
        project_root / "tools" / "scan_imports.py",
        project_root.parent / "tools" / "scan_imports.py",
    ]
    for path in candidates:
        if path.exists():
            try:
                spec = importlib.util.spec_from_file_location("scan_imports", path)
                if spec is None or spec.loader is None:
                    continue
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                package_root = _find_package_root(project_root)
                if package_root:
                    return mod.scan_project(package_root, package_root.name)
            except Exception:
                pass
    return None


def _find_package_root(project_root: Path) -> Path | None:
    """Find the project's main Python package root, deterministically.

    Selection never depends on filesystem iterdir() order. Unsorted iterdir()
    previously caused a regression: adding a dev utility's __init__.py flipped
    the iteration order and resolved package_root to that utility dir instead
    of the real package, which made every path/tag check resolve against the
    wrong base and produced 236 false-positive findings in a single run.

    Priority (each step deterministic):
    1. project_root itself is a package (has __init__.py).
    2. pyproject.toml declaration — [tool.setuptools.packages.find] include /
       [tool.setuptools] packages / [[tool.poetry.packages]] include. This is
       the authoritative source of "what is this project's package".
    3. Dir whose name matches [project] name or the repo dir name
       (PEP 503 normalization: '-' -> '_').
    4. Deterministic fallback: largest candidate by .py file count, excluding
       obvious non-package dirs (tests/ etc.); candidates are pre-sorted by
       name so ties resolve deterministically.

    Limitation: src-layout (packages under src/) is not handled — the scanner's
    scope is top-level packages. Add where=["src"] resolution if ever needed.
    """
    if (project_root / "__init__.py").exists():
        return project_root

    candidates = _sorted_package_candidates(project_root)
    if not candidates:
        return None

    by_name = {c.name: c for c in candidates}

    # 2. Authoritative: pyproject.toml package declaration
    pyproject = project_root / "pyproject.toml"
    if pyproject.exists():
        for pkg_name in _declared_package_names(pyproject):
            root_name = pkg_name.split(".")[0].rstrip("*")
            if root_name in by_name:
                return by_name[root_name]

    # 3. Name match: [project] name or repo dir name (normalized)
    for proj_name in _project_name_candidates(project_root):
        if proj_name in by_name:
            return by_name[proj_name]

    # 4. Deterministic fallback: largest code candidate; ties -> sorted name
    code_candidates = [c for c in candidates if c.name not in NON_PACKAGE_DIRS]
    pool = code_candidates or candidates
    return max(pool, key=_count_py_files)


def _sorted_package_candidates(project_root: Path) -> list[Path]:
    """Deterministic list of top-level dirs that look like a package root."""
    result: list[Path] = []
    for child in sorted(project_root.iterdir(), key=lambda p: p.name):
        if (
            child.is_dir()
            and (child / "__init__.py").exists()
            and not child.name.startswith(".")
            and child.name not in SKIP_DIRS_SCAN
        ):
            result.append(child)
    return result


def _declared_package_names(pyproject: Path) -> list[str]:
    """Extract declared package names from pyproject.toml (setuptools/poetry).

    Names may be glob patterns ("my_package*") or dotted paths
    ("pkg.sub"); callers take the first dot segment and strip the glob star.
    """
    try:
        with pyproject.open("rb") as f:
            data = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError):
        return []

    tool = data.get("tool", {})
    names: list[str] = []

    # setuptools packages field is overloaded:
    #   [tool.setuptools] packages = ["pkg_a", "pkg_b"]   -> list
    #   [tool.setuptools.packages.find] include = [...]   -> dict with .find
    packages_field = tool.get("setuptools", {}).get("packages", {})
    if isinstance(packages_field, list):
        names.extend(packages_field)
    elif isinstance(packages_field, dict):
        find_cfg = packages_field.get("find", {})
        names.extend(find_cfg.get("include", []))

    # poetry: [[tool.poetry.packages]] include = "..."
    for pkg in tool.get("poetry", {}).get("packages", []):
        if isinstance(pkg, dict) and "include" in pkg:
            names.append(pkg["include"])

    return names


def _project_name_candidates(project_root: Path) -> list[str]:
    """Candidate project names (normalized '-' -> '_') for dir matching."""
    names: list[str] = []
    pyproject = project_root / "pyproject.toml"
    if pyproject.exists():
        try:
            with pyproject.open("rb") as f:
                data = tomllib.load(f)
            proj_name = data.get("project", {}).get("name")
            if proj_name:
                names.append(proj_name.replace("-", "_"))
        except (OSError, tomllib.TOMLDecodeError):
            pass
    # Repo dir name (commonly matches the package name)
    names.append(project_root.name.replace("-", "_"))
    return names


def _count_py_files(path: Path) -> int:
    """Count .py files in a directory tree (fallback sizing signal only)."""
    try:
        return sum(1 for _ in path.rglob("*.py"))
    except OSError:
        return 0


# ---------------------------------------------------------------------------
# Instruction-file parsing (AGENTS.md preferred, CLAUDE.md legacy)
# ---------------------------------------------------------------------------


def _find_instruction_files(project_root: Path) -> list[Path]:
    """Find each directory's instruction-content file (dual-file aware).

    Per instruction-writing.md dual-file mode: content lives in AGENTS.md
    (CLAUDE.md is a thin @AGENTS.md wrapper for Claude). Prefer AGENTS.md;
    fall back to CLAUDE.md for legacy single-file repos. Returns one file
    per directory.
    """
    by_dir: dict[Path, Path] = {}
    for path in project_root.rglob("CLAUDE.md"):
        parts = path.relative_to(project_root).parts
        if any(part in SKIP_DIRS_SCAN for part in parts):
            continue
        if ".claude" in parts:
            continue
        by_dir[path.parent] = path
    for path in project_root.rglob("AGENTS.md"):
        parts = path.relative_to(project_root).parts
        if any(part in SKIP_DIRS_SCAN for part in parts):
            continue
        if ".claude" in parts:
            continue
        by_dir[path.parent] = path  # AGENTS.md preferred (overwrites CLAUDE.md)
    return sorted(by_dir.values())


def parse_claude_md_registry(
    project_root: Path,
) -> tuple[list[dict], list[dict]]:
    """Parse all CLAUDE.md files.

    Returns (claude_md_registry, capabilities_registry).
    """
    claude_md_registry = []
    capabilities_registry = []
    for md_file in _find_instruction_files(project_root):
        md_entry, caps_entries = _parse_single_claude_md(md_file, project_root)
        claude_md_registry.append(md_entry)
        capabilities_registry.extend(caps_entries)
    return claude_md_registry, capabilities_registry


def _parse_capabilities_table(
    content: str, source_claude_md: str, module: str
) -> list[dict]:
    """Parse Capabilities table from instruction-file content.

    Expected table format (3 columns, no UC ID):
        | 能力 | 入口 | 狀態 |
    """
    entries: list[dict] = []

    header_match = CAPABILITIES_HEADER_RE.search(content)
    if not header_match:
        return entries

    # Get text after the header until next ## heading
    start = header_match.end()
    next_section = re.search(r"\n## ", content[start:])
    section_text = (
        content[start : start + next_section.start()]
        if next_section
        else content[start:]
    )

    for line in section_text.splitlines():
        # Parse table row using split-by-| instead of regex.
        # This handles | inside backtick content (e.g. CLI `sync [revenue|income|all]`)
        # by taking col1 from the left and status from the right, then
        # reconstructing entry_point from the middle fragments.
        if not TABLE_ROW_START.match(line):
            continue
        parts = line.split("|")
        # parts: ['', col1, col2, ..., colN, ''] (leading/trailing |)
        if len(parts) < 5:  # need at least: '' capability entry_point status ''
            continue
        col1 = parts[1].strip()  # capability/能力 (never contains |)
        col_last = parts[-2].strip()  # status/狀態 (never contains |)
        # Reconstruct entry_point by rejoining fragments — restores | inside backticks
        entry_point = "|".join(parts[2:-2]).strip()

        # Skip separator rows (---)
        if all(set(c.strip()) <= {"-", ":"} for c in parts[1:-1]):
            continue
        # Skip header rows
        if col1 in ("能力", "Capability"):
            continue

        # Skip empty rows
        if not col1:
            continue

        # Extract status emoji
        status = ""
        for ch in col_last:
            if ch in "✅📋🔧❌🟡🟢":
                status = ch
                break
        if not status:
            status = "✅"  # Default for Capabilities table entries

        entries.append(
            {
                "module": module,
                "capability": col1,
                "entry_point": entry_point,
                "status": status,
                "source_claude_md": source_claude_md,
            }
        )

    return entries


def _parse_single_claude_md(
    md_file: Path, project_root: Path
) -> tuple[dict, list[dict]]:
    """Parse a single CLAUDE.md file.

    Returns (metadata_dict, capabilities_entries).
    """
    content = md_file.read_text(encoding="utf-8")
    path_rel = str(md_file.relative_to(project_root))

    parent = md_file.parent
    module = parent.name if parent != project_root else "(root)"

    has_boundaries = bool(
        re.search(r"Module Boundaries|模組邊界|Does NOT depend on", content)
    )

    has_capabilities = bool(CAPABILITIES_HEADER_RE.search(content))

    not_depend_on = []
    for m in re.finditer(r"Does NOT depend on[：:]*\s*(.+?)(?:\n|$)", content):
        for mod_match in re.finditer(r"\b([a-z][a-z0-9_]*)\b", m.group(1)):
            not_depend_on.append(mod_match.group(1))

    # Parse Capabilities table
    capabilities_entries = _parse_capabilities_table(content, path_rel, module)

    md_entry = {
        "path": path_rel,
        "module": module,
        "exists": True,
        "has_module_boundaries": has_boundaries,
        "has_capabilities_table": has_capabilities,
        "capabilities_count": len(capabilities_entries),
        "declared_not_depend_on": sorted(set(not_depend_on)),
    }

    return md_entry, capabilities_entries


# ---------------------------------------------------------------------------
# .kanban/ card parsing (tag-based identity)
# ---------------------------------------------------------------------------


def parse_kanban_registry(project_root: Path) -> list[dict]:
    """Parse all .kanban/ cards."""
    kanban_dir = project_root / ".kanban"
    if not kanban_dir.is_dir():
        return []

    registry = []
    for lane_dir in sorted(kanban_dir.iterdir()):
        if not lane_dir.is_dir():
            continue
        if lane_dir.name not in KANBAN_LANES:
            continue
        lane = lane_dir.name
        for card_file in sorted(lane_dir.glob("*.md")):
            entry = _parse_kanban_card(card_file, lane, project_root)
            registry.append(entry)
    return registry


def _parse_kanban_card(card_file: Path, lane: str, project_root: Path) -> dict:
    """Parse a single Kanban card.

    Card identity: title (= filename stem) + [tag:module] on line 1.
    No YAML frontmatter, no UC ID as primary key.
    """
    content = card_file.read_text(encoding="utf-8")
    source_rel = str(card_file.relative_to(project_root))

    # Title: filename stem (Chinese name, e.g. "騰落線指標")
    title = card_file.stem

    # Tags: [tag:xxx] on first line (space-separated for multiple)
    tags = TAG_RE.findall(content.split("\n", 1)[0]) if content else []

    # EP reference from ## 相關 section
    ep_match = EP_REF_RE.search(content)
    ep_ref = ""
    has_ep = False
    if ep_match:
        ep_ref = ep_match.group(1).strip()
        has_ep = ep_ref not in ("待定", "")

    # Has spec: check for spec references in body
    has_spec = bool(re.search(r"spec[：:]", content, re.IGNORECASE))

    return {
        "title": title,
        "tags": tags,
        "lane": lane,
        "has_ep": has_ep,
        "ep_ref": ep_ref,
        "has_spec": has_spec,
        "source_file": source_rel,
    }


# ---------------------------------------------------------------------------
# Cross-validation (mechanical checks)
# ---------------------------------------------------------------------------


def _find_valid_tag_names(project_root: Path) -> set[str]:
    """Find valid tag names from package root subdirectories + top-level dirs.

    Tag convention: tag name = a real directory in the repo.
    Sources (combined, both generic — no project-specific hardcoding):
      1. Package root (e.g. my_package/) subdirectories — the library modules.
         Shorthand: adapters/sj → sj (nested package with __init__.py).
      2. Project root top-level dirs — cross-cutting domains that live outside
         the importable package (tools/, deploy/, scripts/, tests/). These host
         real product-adjacent work (dev utilities, launchd ops, CLI entries)
         and carry kanban cards, so their names are valid tags.

    Excluded: SKIP_DIRS_SCAN + dotdirs + transient/experimental top-level dirs
    (poc/, lab/) — temporary or deprecated, not stable tag targets.
    """
    valid_tags: set[str] = set()

    # Source 1: package root subdirectories (library modules)
    pkg_root = _find_package_root(project_root)
    if pkg_root:
        for child in sorted(pkg_root.iterdir()):
            if not child.is_dir():
                continue
            if child.name.startswith((".", "_")):
                continue
            if child.name in SKIP_DIRS_SCAN:
                continue
            valid_tags.add(child.name)
            # Add shorthand for nested modules (e.g. adapters/sj → sj)
            for nested in sorted(child.iterdir()):
                if nested.is_dir() and (nested / "__init__.py").exists():
                    valid_tags.add(nested.name)

    # Source 2: project root top-level dirs (cross-cutting domains outside package)
    transient_top_dirs = {"poc", "lab"}  # temporary / deprecated — not stable tags
    for child in sorted(project_root.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith((".", "_")):
            continue
        if child.name in SKIP_DIRS_SCAN or child.name in transient_top_dirs:
            continue
        if pkg_root is not None and child == pkg_root:
            continue  # package root itself (already covered by source 1)
        valid_tags.add(child.name)

    return valid_tags


def run_cross_validation(
    modules: dict,
    capabilities_registry: list[dict],
    kanban_registry: list[dict],
    claude_md_registry: list[dict],
    project_root: Path,
) -> list[dict]:
    """Run mechanical cross-validation checks."""
    findings = []

    claude_md_modules = {e["module"] for e in claude_md_registry}

    # --- Capabilities checks ---

    # X-cap-path: Capabilities entry_point path does not exist
    # Entry paths may be relative to: project root, package root, or
    # the CLAUDE.md's own directory.  Check all three before reporting.
    pkg_root = _find_package_root(project_root)
    for e in capabilities_registry:
        entry = e.get("entry_point", "")
        if not entry:
            continue
        # Extract first path-like segment (before any description)
        # e.g. "CLI `mycli data daily-close`" → skip (CLI commands)
        # e.g. "`indicators/engine.py:apply_indicators()`" → extract path
        path_match = re.search(r"`?([a-z_][a-z0-9_./]+\.pyi?)", entry)
        if path_match:
            rel_path = path_match.group(1).split(":")[0]
            # Candidate locations to check
            candidates = [
                project_root / rel_path,  # absolute from project root
            ]
            if pkg_root:
                candidates.append(pkg_root / rel_path)  # under package root
            # Relative to the CLAUDE.md's own directory
            claude_md_dir = (
                project_root / e["source_claude_md"].rsplit("/", 1)[0]
                if "/" in e["source_claude_md"]
                else project_root
            )
            candidates.append(claude_md_dir / rel_path)
            if not any(p.exists() for p in candidates):
                findings.append(
                    {
                        "check_id": "X-cap-path",
                        "severity": "important",
                        "detail": (
                            f"Capabilities entry path '{rel_path}' "
                            f"does not exist (in {e['source_claude_md']})"
                        ),
                        "capability": e["capability"],
                        "source_claude_md": e["source_claude_md"],
                    }
                )

    # X6: Module in dep-graph but no instruction file (AGENTS.md/CLAUDE.md)
    for mod_name, mod_data in modules.items():
        if mod_name in claude_md_modules:
            continue
        file_count = mod_data.get("file_count", 0)
        if file_count < 3:
            continue
        mod_dir = project_root / mod_name
        if mod_dir.is_dir() and not (
            (mod_dir / "CLAUDE.md").exists() or (mod_dir / "AGENTS.md").exists()
        ):
            pkg_dir = _find_package_root(project_root)
            if pkg_dir:
                actual_dir = pkg_dir / mod_name
                if actual_dir.is_dir() and (
                    (actual_dir / "CLAUDE.md").exists()
                    or (actual_dir / "AGENTS.md").exists()
                ):
                    continue
            findings.append(
                {
                    "check_id": "X6",
                    "severity": "important",
                    "detail": (
                        f"Module '{mod_name}' has {file_count} files but no instruction file (AGENTS.md/CLAUDE.md)"
                    ),
                    "module": mod_name,
                }
            )

    # --- Kanban checks ---

    # X-tag-module: tag does not correspond to any valid module/domain directory
    valid_tags = _find_valid_tag_names(project_root)
    if valid_tags:
        for e in kanban_registry:
            for tag in e.get("tags", []):
                if tag not in valid_tags:
                    findings.append(
                        {
                            "check_id": "X-tag-module",
                            "severity": "important",
                            "detail": (
                                f"Card '{e['title']}' has tag '{tag}' "
                                f"which does not match any package "
                                f"subdirectory or top-level dir"
                            ),
                            "kanban_source": e["source_file"],
                        }
                    )

    # X-ep-ready: Next-Up/In-Progress card has EP ref but file missing
    for e in kanban_registry:
        if e["lane"] not in ("Next-Up", "In-Progress"):
            continue
        if not e.get("has_ep") or not e.get("ep_ref"):
            continue
        ep_ref = e["ep_ref"]
        # EP files live under ai-analysis/ or similar directories
        # Check common locations
        ep_candidates = [
            project_root / "ai-analysis" / "execution-plans" / ep_ref,
            project_root / "ai-analysis" / "done_plans" / ep_ref,
            project_root / ep_ref,
        ]
        ep_exists = any(p.exists() for p in ep_candidates)
        if not ep_exists:
            findings.append(
                {
                    "check_id": "X-ep-ready",
                    "severity": "important",
                    "detail": (
                        f"Card '{e['title']}' in {e['lane']} references "
                        f"EP '{ep_ref}' but file not found"
                    ),
                    "kanban_source": e["source_file"],
                }
            )

    return findings


# ---------------------------------------------------------------------------
# Main scan function
# ---------------------------------------------------------------------------


def _compute_fingerprint(
    capabilities_registry: list[dict],
    kanban_registry: list[dict],
    claude_md_registry: list[dict],
) -> dict:
    """Compute lightweight fingerprint for change detection.

    LLM reads CLAUDE.md and .kanban/ directly when it needs details.
    The fingerprint only answers: "did something change since last scan?"
    """

    # Capabilities hash: sorted capability + module + status
    cap_keys = sorted(
        f"{e['capability']}:{e['module']}:{e['status']}" for e in capabilities_registry
    )
    cap_hash = hashlib.md5("|".join(cap_keys).encode()).hexdigest()[:12]

    # Kanban hash: sorted title + lane + tags
    kanban_keys = sorted(
        f"{e['title']}:{e['lane']}:{','.join(sorted(e['tags']))}"
        for e in kanban_registry
    )
    kanban_hash = hashlib.md5("|".join(kanban_keys).encode()).hexdigest()[:12]

    # Kanban by lane
    kanban_by_lane: dict[str, int] = defaultdict(int)
    for e in kanban_registry:
        kanban_by_lane[e["lane"]] += 1

    return {
        "capabilities_total": len(capabilities_registry),
        "capabilities_hash": cap_hash,
        "kanban_total": len(kanban_registry),
        "kanban_by_lane": dict(kanban_by_lane),
        "kanban_hash": kanban_hash,
        "instruction_file_total": len(claude_md_registry),
    }


def scan_project(project_root: Path) -> dict:
    """Run the full unified scan.

    Produces three things:
    1. dep_graph — AST-parsed import relationships (LLM can't do this)
    2. findings — mechanical cross-validation issues (LLM can but expensive)
    3. fingerprint — lightweight change detection (counts + hashes)

    Internal parsing (registries) is kept for computing findings,
    but NOT included in output. LLM reads CLAUDE.md and .kanban/
    directly when it needs details.
    """
    project_root = project_root.resolve()

    # Phase 1: Import scan (from scan_imports.py if available)
    import_data = _load_scan_imports(project_root)
    if import_data:
        modules = import_data.get("modules", {})
        edges = import_data.get("edges", [])
        hotspots = import_data.get("hotspots", [])
        project_name = import_data.get("project", project_root.name)
    else:
        modules = {}
        edges = []
        hotspots = []
        project_name = project_root.name

    # Phase 2: Parse CLAUDE.md files (internal — not in output)
    claude_md_registry, capabilities_registry = parse_claude_md_registry(project_root)

    # Phase 3: Parse .kanban/ cards (internal — not in output)
    kanban_registry = parse_kanban_registry(project_root)

    # Phase 4: Run mechanical cross-validation → findings
    findings = run_cross_validation(
        modules,
        capabilities_registry,
        kanban_registry,
        claude_md_registry,
        project_root,
    )

    # Phase 5: Compute fingerprint for change detection
    fingerprint = _compute_fingerprint(
        capabilities_registry, kanban_registry, claude_md_registry
    )

    return {
        "project": project_name,
        "scan_timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "schema_version": 5,
        "dep_graph": {
            "modules": modules,
            "edges": edges,
            "hotspots": hotspots,
        },
        "findings": findings,
        "fingerprint": fingerprint,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Unified project knowledge scanner")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path("."),
        help="Path to the project root (default: current directory)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON file path (default: stdout)",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initial generation mode (no diff, just produce full snapshot)",
    )
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    result = scan_project(project_root)

    output_json = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        args.output.write_text(output_json, encoding="utf-8")
        fp = result["fingerprint"]
        findings_count = len(result["findings"])
        dep_modules = len(result["dep_graph"]["modules"])
        print(
            f"Written to {args.output} "
            f"(dep_graph: {dep_modules} modules, "
            f"findings: {findings_count}, "
            f"fingerprint: {fp['capabilities_total']} caps / "
            f"{fp['kanban_total']} cards)"
        )
    else:
        print(output_json)


if __name__ == "__main__":
    main()
