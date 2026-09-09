#!/usr/bin/env bash
# Verify the cross-harness memory topology (read-only; `--smoke` adds one
# hook round-trip with trap cleanup). Used after fresh-machine setup and
# as the shrunken E2E for the migration acceptance gate.
#
# Checks: pool is a real dir; CC path is a symlink onto the pool; ZCode
# path double-hops onto the pool; all three resolve to the same inode;
# deployed generator --check is green; hooks.json exists with an
# executable command.
set -euo pipefail

REPO=$(cd "$(dirname "$0")/.." && pwd)
POOL="$REPO/.agents/memory"
SMOKE=0
if [ "${1:-}" = "--smoke" ]; then SMOKE=1; fi

pass=0; failn=0
ok() { pass=$((pass + 1)); echo "OK   $1"; }
bad() { failn=$((failn + 1)); echo "FAIL $1"; }

ENCODED=$(printf '%s' "$REPO" | tr '/' '-')
HASH=$(printf '%s' "$REPO" | shasum -a 256 | cut -c1-16)
CC_MEM="$HOME/.claude/projects/$ENCODED/memory"
ZC_MEM="$HOME/.zcode/cli/memories/projects/$(basename "$REPO")-$HASH/memory"

[ -d "$POOL" ] && [ ! -L "$POOL" ] && ok "pool is a real dir" || bad "pool missing or symlink: $POOL"
[ -L "$CC_MEM" ] && [ "$(readlink "$CC_MEM")" = "$POOL" ] && ok "CC symlink -> pool" || bad "CC link wrong: $CC_MEM"
[ -L "$ZC_MEM" ] && [ "$(readlink "$ZC_MEM")" = "$CC_MEM" ] && ok "ZCode symlink -> CC" || bad "ZCode link wrong: $ZC_MEM"

if [ -f "$POOL/MEMORY.md" ] && [ -f "$CC_MEM/MEMORY.md" ] && [ -f "$ZC_MEM/MEMORY.md" ]; then
  A=$(python3 -c "import os;print(os.stat('$POOL/MEMORY.md').st_ino)")
  B=$(python3 -c "import os;print(os.stat('$CC_MEM/MEMORY.md').st_ino)")
  C=$(python3 -c "import os;print(os.stat('$ZC_MEM/MEMORY.md').st_ino)")
  [ "$A" = "$B" ] && [ "$B" = "$C" ] && ok "same inode ($A)" || bad "inode mismatch: $A $B $C"
else
  bad "MEMORY.md not reachable on all three legs"
fi

if [ -f "$POOL/_generate_index.py" ]; then
  GEN_LOG=$(mktemp /tmp/verify-topology-gen.XXXXXX.log)
  if python3 "$POOL/_generate_index.py" --check >"$GEN_LOG" 2>&1; then
    ok "generator --check green"
  else
    bad "generator --check failed (see $GEN_LOG)"
  fi
  rm -f "$GEN_LOG"
else
  bad "deployed generator missing: $POOL/_generate_index.py"
fi

HOOK_JSON="$REPO/.muse/hooks.json"
if [ -f "$HOOK_JSON" ]; then
  CMD=$(jq -r '.hooks.PreToolUse[0].hooks[0].command' "$HOOK_JSON" 2>/dev/null || true)
  [ -n "$CMD" ] && [ -x "$CMD" ] && ok "hooks.json command executable" || bad "hooks.json command not executable: $CMD"
else
  bad "hooks.json missing (run hooks/setup-muse-hooks.sh)"
fi

if [ "$SMOKE" = 1 ]; then
  INBOX="$REPO/.agents/memory-inbox"
  mkdir -p "$INBOX"
  SMOKE_OUT=""
  cleanup() { [ -n "$SMOKE_OUT" ] && rm -f "$SMOKE_OUT"; }
  trap cleanup EXIT
  IN='{"tool_name":"add_memory","tool_input":{"scope":"project","path":"smoke-probe.md","content":"smoke"}}'
  RESP=$(printf '%s' "$IN" | bash "$REPO/hooks/muse_memory_inbox.sh")
  # grep 抽取隱性依賴 hook deny reason 文案內含絕對路徑（"已代存 inbox: <path>"）——
  # 改 reason 措辭時須同步此 pattern（fail-loud：抽不到 = smoke FAIL）
  SMOKE_OUT=$(printf '%s' "$RESP" | jq -r '.hookSpecificOutput.permissionDecisionReason' | grep -o "$INBOX/[^']*\.json" | head -n 1 || true)
  if printf '%s' "$RESP" | jq -e '.hookSpecificOutput.permissionDecision == "deny"' >/dev/null && [ -n "$SMOKE_OUT" ] && [ -f "$SMOKE_OUT" ]; then
    ok "hook smoke: deny + inbox landed"
  else
    bad "hook smoke failed"
  fi
  cleanup
  trap - EXIT
fi

echo "--- $pass passed, $failn failed ---"
[ "$failn" = 0 ]
