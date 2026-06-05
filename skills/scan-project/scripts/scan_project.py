#!/usr/bin/env python3
"""
Unified Project Knowledge Scanner.

Extends scan_imports.py with USE-CASES.md and CLAUDE.md parsing,
producing a unified snapshot for cross-artifact validation.

Designed for the /scan-project skill + /claude:daily-maintain workflow.

Usage:
    uv run python scan_project.py --project-root . --output .project-snapshot.json
    uv run python scan_project.py --init --project-root /path/to/project
"""

import argparse
import importlib.util
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from datetime import timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Import scan_imports if available (graceful degradation)
# ---------------------------------------------------------------------------

def _load_scan_imports(project_root: Path) -> dict | None:
    """Try to import and run scan_imports.scan_project from the target project."""
    candidates = [
        project_root / "scripts" / "scan_imports.py",
        project_root.parent / "scripts" / "scan_imports.py",
    ]
    for path in candidates:
        if path.exists():
            try:
                spec = importlib.util.spec_from_file_location("scan_imports", path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                package_root = _find_package_root(project_root)
                if package_root:
                    return mod.scan_project(package_root, package_root.name)
            except Exception:
                pass
    return None


def _find_package_root(project_root: Path) -> Path | None:
    """Find the Python package root (directory with __init__.py)."""
    # Check if project_root itself is the package
    if (project_root / "__init__.py").exists():
        return project_root
    # Check single subdirectory (e.g., project_root/mosaic_alpha/)
    for child in project_root.iterdir():
        if child.is_dir() and (child / "__init__.py").exists() and not child.name.startswith("."):
            return child
    return None


# ---------------------------------------------------------------------------
# USE-CASES.md parsing
# ---------------------------------------------------------------------------

STATUS_EMOJIS = {"✅", "📋", "🔧", "❌", "🟡", "🟢"}

# Match: ### ✅ D-14: 每日收盤完整流程 Pipeline — mosaic_alpha/data/daily_close/
UC_TITLE_RE = re.compile(
    r"^###\s+([✅📋🔧❌🟡🟢])\s+([A-Za-z]+-\d+):\s+(.+?)\s*(?:[—–-]\s*(.+))?$"
)

# Match UC IDs in cross-reference fields
UC_ID_RE = re.compile(r"\b([A-Z]+-\d+)\b")

SKIP_DIRS_SCAN = {
    ".venv", "venv", "__pycache__", ".git", "node_modules",
    ".mypy_cache", ".ruff_cache", ".idea", "_archive",
    ".claude", "build", "dist",
}


def _find_use_cases_files(project_root: Path) -> list[Path]:
    """Find all USE-CASES.md files in library module directories."""
    results = []
    for path in project_root.rglob("USE-CASES.md"):
        parts = path.relative_to(project_root).parts
        if any(part in SKIP_DIRS_SCAN for part in parts):
            continue
        if "scripts" in parts:
            continue
        results.append(path)
    return sorted(results)


def parse_uc_registry(project_root: Path) -> list[dict]:
    """Parse all USE-CASES.md files and extract UC entries."""
    registry = []
    for uc_file in _find_use_cases_files(project_root):
        entries = _parse_single_uc_file(uc_file, project_root)
        registry.extend(entries)
    return registry


def _parse_single_uc_file(uc_file: Path, project_root: Path) -> list[dict]:
    """Parse a single USE-CASES.md file."""
    entries = []
    lines = uc_file.read_text(encoding="utf-8").splitlines()
    source_rel = str(uc_file.relative_to(project_root))
    current_section = ""
    current_entry = None

    for i, line in enumerate(lines, 1):
        # Track current section (## headings)
        if line.startswith("## "):
            current_section = line.lstrip("#").strip()
            continue

        # Match UC title line
        m = UC_TITLE_RE.match(line)
        if m:
            # Save previous entry
            if current_entry:
                entries.append(current_entry)

            status, uc_id, title, path_str = m.groups()
            # Collect cross-refs from remaining lines until next ### or end
            current_entry = {
                "uc_id": uc_id,
                "status": status,
                "title": title.strip(),
                "path": path_str.strip() if path_str else "",
                "source_file": source_rel,
                "section": current_section,
                "line_number": i,
                "cross_refs": [],
                "domain_deps": [],
                "downstream_consumers": [],
            }
            continue

        # Extract cross-references from entry body
        if current_entry and line.strip().startswith("- "):
            stripped = line.strip()
            if any(
                key in stripped
                for key in ("跨領域依賴", "領域依賴", "domain_dep")
            ):
                refs = UC_ID_RE.findall(stripped)
                current_entry["domain_deps"].extend(refs)
                current_entry["cross_refs"].extend(refs)
            elif any(
                key in stripped
                for key in ("下游消費者", "consumed_by", "消費者")
            ):
                refs = UC_ID_RE.findall(stripped)
                current_entry["downstream_consumers"].extend(refs)
                current_entry["cross_refs"].extend(refs)
            elif any(
                key in stripped
                for key in ("編排流程", "跨領域依賴", "orchestrat")
            ):
                refs = UC_ID_RE.findall(stripped)
                current_entry["cross_refs"].extend(refs)

    # Don't forget the last entry
    if current_entry:
        entries.append(current_entry)

    # Deduplicate cross_refs
    for entry in entries:
        entry["cross_refs"] = sorted(set(entry["cross_refs"]))
        entry["domain_deps"] = sorted(set(entry["domain_deps"]))
        entry["downstream_consumers"] = sorted(set(entry["downstream_consumers"]))

    return entries


# ---------------------------------------------------------------------------
# CLAUDE.md parsing
# ---------------------------------------------------------------------------


def _find_claude_md_files(project_root: Path) -> list[Path]:
    """Find all CLAUDE.md files."""
    results = []
    for path in project_root.rglob("CLAUDE.md"):
        parts = path.relative_to(project_root).parts
        if any(part in SKIP_DIRS_SCAN for part in parts):
            continue
        if ".claude" in parts:
            continue
        results.append(path)
    return sorted(results)


def parse_claude_md_registry(project_root: Path) -> list[dict]:
    """Parse all CLAUDE.md files and extract metadata."""
    registry = []
    for md_file in _find_claude_md_files(project_root):
        entry = _parse_single_claude_md(md_file, project_root)
        registry.append(entry)
    return registry


def _parse_single_claude_md(md_file: Path, project_root: Path) -> dict:
    """Parse a single CLAUDE.md file."""
    content = md_file.read_text(encoding="utf-8")
    path_rel = str(md_file.relative_to(project_root))

    # Infer module name from directory
    parent = md_file.parent
    module = parent.name if parent != project_root else "(root)"

    # Check for Module Boundaries section
    has_boundaries = bool(
        re.search(r"Module Boundaries|模組邊界|Does NOT depend on", content)
    )

    # Extract declared "Does NOT depend on" modules
    not_depend_on = []
    for m in re.finditer(
        r"Does NOT depend on[：:]*\s*(.+?)(?:\n|$)", content
    ):
        # Extract module names from the line
        for mod_match in re.finditer(r"\b([a-z][a-z0-9_]*)\b", m.group(1)):
            not_depend_on.append(mod_match.group(1))

    # Extract UC IDs referenced in content
    uc_ids = sorted(set(UC_ID_RE.findall(content)))

    return {
        "path": path_rel,
        "module": module,
        "exists": True,
        "has_module_boundaries": has_boundaries,
        "referenced_uc_ids": uc_ids,
        "declared_not_depend_on": sorted(set(not_depend_on)),
    }


# ---------------------------------------------------------------------------
# UC Edge building
# ---------------------------------------------------------------------------


def build_uc_edges(uc_registry: list[dict]) -> list[dict]:
    """Build UC-to-UC dependency edges from registry cross_refs."""
    edges = []
    seen = set()

    for entry in uc_registry:
        source = entry["uc_id"]
        source_file = entry["source_file"]

        # Domain deps
        for target in entry.get("domain_deps", []):
            key = (source, target, "domain_dep")
            if key not in seen:
                seen.add(key)
                edges.append({
                    "source": source,
                    "target": target,
                    "type": "domain_dep",
                    "source_file": source_file,
                })

        # Downstream consumers (reverse direction)
        for consumer in entry.get("downstream_consumers", []):
            key = (consumer, source, "consumed_by")
            if key not in seen:
                seen.add(key)
                edges.append({
                    "source": consumer,
                    "target": source,
                    "type": "consumed_by",
                    "source_file": source_file,
                })

        # Cross-refs that aren't already captured
        for ref in entry.get("cross_refs", []):
            if ref in entry.get("domain_deps", []) or ref in entry.get(
                "downstream_consumers", []
            ):
                continue
            key = (source, ref, "cross_ref")
            if key not in seen:
                seen.add(key)
                edges.append({
                    "source": source,
                    "target": ref,
                    "type": "cross_ref",
                    "source_file": source_file,
                })

    return edges


# ---------------------------------------------------------------------------
# Cross-validation (mechanical checks)
# ---------------------------------------------------------------------------


def run_cross_validation(
    modules: dict,
    uc_registry: list[dict],
    claude_md_registry: list[dict],
    project_root: Path,
) -> list[dict]:
    """Run mechanical cross-validation checks."""
    findings = []

    # Build lookup sets
    all_uc_ids = {e["uc_id"] for e in uc_registry}
    uc_by_id = defaultdict(list)
    for e in uc_registry:
        uc_by_id[e["uc_id"]].append(e)

    claude_md_modules = {e["module"] for e in claude_md_registry}

    # X-path: UC code_path does not exist
    for entry in uc_registry:
        if not entry["path"]:
            continue
        full_path = project_root / entry["path"]
        if not full_path.exists():
            findings.append({
                "check_id": "X-path",
                "severity": "critical",
                "detail": (
                    f"UC {entry['uc_id']} path {entry['path']} "
                    f"does not exist (defined in {entry['source_file']})"
                ),
                "uc_id": entry["uc_id"],
                "path": entry["path"],
            })

    # X6: Module in dep-graph but no CLAUDE.md
    for mod_name, mod_data in modules.items():
        if mod_name in claude_md_modules:
            continue
        file_count = mod_data.get("file_count", 0)
        if file_count < 3:
            continue  # Skip tiny modules
        # Check if directory actually has CLAUDE.md (might be nested)
        mod_dir = project_root / mod_name
        if mod_dir.is_dir() and not (mod_dir / "CLAUDE.md").exists():
            # Also check for package subdirectory pattern
            pkg_dir = _find_package_root(project_root)
            if pkg_dir:
                actual_dir = pkg_dir / mod_name
                if actual_dir.is_dir() and (actual_dir / "CLAUDE.md").exists():
                    continue
            findings.append({
                "check_id": "X6",
                "severity": "important",
                "detail": f"Module '{mod_name}' has {file_count} files but no CLAUDE.md",
                "module": mod_name,
            })

    # X7: UC cross-reference to non-existent ID
    for entry in uc_registry:
        for ref in entry.get("cross_refs", []):
            if ref not in all_uc_ids:
                findings.append({
                    "check_id": "X7",
                    "severity": "critical",
                    "detail": (
                        f"UC {entry['uc_id']} cross-references {ref} "
                        f"which does not exist in any USE-CASES.md"
                    ),
                    "source_uc": entry["uc_id"],
                    "broken_ref": ref,
                })

    # X-unique: Same UC ID defined in multiple files
    for uc_id, entries in uc_by_id.items():
        if len(entries) > 1:
            source_files = [e["source_file"] for e in entries]
            findings.append({
                "check_id": "X-unique",
                "severity": "critical",
                "detail": (
                    f"UC ID {uc_id} defined in {len(entries)} files: "
                    f"{', '.join(source_files)}"
                ),
                "uc_id": uc_id,
                "source_files": source_files,
            })

    return findings


# ---------------------------------------------------------------------------
# Main scan function
# ---------------------------------------------------------------------------


def scan_project(project_root: Path) -> dict:
    """Run the full unified scan."""
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

    # Phase 2: Parse USE-CASES.md files
    uc_registry = parse_uc_registry(project_root)

    # Phase 3: Parse CLAUDE.md files
    claude_md_registry = parse_claude_md_registry(project_root)

    # Phase 4: Build UC edges
    uc_edges = build_uc_edges(uc_registry)

    # Phase 5: Run mechanical cross-validation
    cross_validation = run_cross_validation(
        modules, uc_registry, claude_md_registry, project_root
    )

    return {
        "project": project_name,
        "scan_timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "schema_version": 2,
        "modules": modules,
        "edges": edges,
        "hotspots": hotspots,
        "uc_registry": uc_registry,
        "claude_md_registry": claude_md_registry,
        "uc_edges": uc_edges,
        "cross_validation": cross_validation,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Unified project knowledge scanner"
    )
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
        total_uc = len(result["uc_registry"])
        total_issues = len(result["cross_validation"])
        print(
            f"Written to {args.output} "
            f"({total_uc} UCs, {total_issues} cross-validation issues)"
        )
    else:
        print(output_json)


if __name__ == "__main__":
    main()
