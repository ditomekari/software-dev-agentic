#!/usr/bin/env bash
# setup-symlinks.sh
# Wires all agents/skills/hooks/reference for the chosen platform into .claude/.
# Safe to re-run — link_if_absent never overwrites existing files.
# Also used by sync.sh to re-link after a submodule update.
#
# Usage:
#   software-dev-agentic/scripts/setup-symlinks.sh --platform=web
#   software-dev-agentic/scripts/setup-symlinks.sh --platform=ios
#   software-dev-agentic/scripts/setup-symlinks.sh --platform=android
#   software-dev-agentic/scripts/setup-symlinks.sh --platform=flutter
#
# Priority order: agents.local > platform > core  (first link wins)

set -euo pipefail

SUBMODULE="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_ROOT="$(cd "$SUBMODULE/.." && pwd)"
CLAUDE_DIR="$PROJECT_ROOT/.claude"

# ── Parse --platform ─────────────────────────────────────────────────────────

PLATFORM=""
APP_NAME=""
for arg in "$@"; do
  case "$arg" in
    --platform=*) PLATFORM="${arg#--platform=}" ;;
    --app-name=*) APP_NAME="${arg#--app-name=}" ;;
  esac
done

if [ -z "$PLATFORM" ]; then
  echo "Error: --platform is required."
  echo "Usage: $0 --platform=web|ios|android|flutter"
  exit 1
fi

PLATFORM_DIR="$SUBMODULE/lib/platforms/$PLATFORM"
if [ ! -d "$PLATFORM_DIR" ]; then
  echo "Error: platform '$PLATFORM' not found at $PLATFORM_DIR"
  exit 1
fi

echo "Setting up software-dev-agentic (platform: $PLATFORM)..."

# ── Helpers ───────────────────────────────────────────────────────────────────

link_if_absent() {
  local target="$1"
  local link="$2"
  if [ -e "$link" ] || [ -L "$link" ]; then
    echo "  skip  $link"
  else
    ln -s "$target" "$link"
    echo "  link  $(basename $link)"
  fi
}

convert_dir_symlink() {
  local dir="$1"
  if [ -L "$dir" ]; then
    echo "  convert  $dir (directory symlink → real directory)"
    rm "$dir"
    mkdir -p "$dir"
  fi
}

# ── Directories ───────────────────────────────────────────────────────────────

echo ""
echo "Preparing .claude/ directories..."
convert_dir_symlink "$CLAUDE_DIR/agents"
convert_dir_symlink "$CLAUDE_DIR/skills"
convert_dir_symlink "$CLAUDE_DIR/reference"
mkdir -p \
  "$CLAUDE_DIR/agents" \
  "$CLAUDE_DIR/skills" \
  "$CLAUDE_DIR/reference" \
  "$CLAUDE_DIR/agents.local/extensions" \
  "$CLAUDE_DIR/skills.local/extensions" \
  "$CLAUDE_DIR/reference.local" \
  "$CLAUDE_DIR/agentic-state/runs"

# ── Link function (local > platform > core) ───────────────────────────────────

link_agents() {
  local src_dir="$1"
  local rel_prefix="$2"
  [ -d "$src_dir" ] || return 0
  while IFS= read -r agent; do
    [ -f "$agent" ] || continue
    name="$(basename "$agent")"
    rel_path="${agent#$src_dir/}"
    link_if_absent "$rel_prefix/$rel_path" "$CLAUDE_DIR/agents/$name"
  done < <(find "$src_dir" -name "*.md" -type f)
}

link_skills() {
  local src_dir="$1"
  local rel_prefix="$2"
  [ -d "$src_dir" ] || return 0
  for skill_dir in "$src_dir"/*/; do
    [ -d "$skill_dir" ] || continue
    name="$(basename "$skill_dir")"
    [ "$name" = "contract" ] && continue
    [ "$name" = "extensions" ] && continue
    link_if_absent "$rel_prefix/$name" "$CLAUDE_DIR/skills/$name"
  done
  if [ -d "$src_dir/contract" ]; then
    for skill_dir in "$src_dir/contract"/*/; do
      [ -d "$skill_dir" ] || continue
      name="$(basename "$skill_dir")"
      link_if_absent "$rel_prefix/contract/$name" "$CLAUDE_DIR/skills/$name"
    done
  fi
}

link_reference() {
  local src_dir="$1"
  local rel_prefix="$2"
  local dest_base="${3:-$CLAUDE_DIR/reference}"
  [ -d "$src_dir" ] || return 0
  for ref in "$src_dir"/*.md; do
    [ -f "$ref" ] || continue
    name="$(basename "$ref")"
    link_if_absent "$rel_prefix/$name" "$dest_base/$name"
  done
  for subdir in "$src_dir"/*/; do
    [ -d "$subdir" ] || continue
    subname="$(basename "$subdir")"
    mkdir -p "$dest_base/$subname"
    link_reference "$subdir" "../$rel_prefix/$subname" "$dest_base/$subname"
  done
}

# Relative paths from .claude/agents/ or .claude/skills/ to submodule
REL_CORE="../../software-dev-agentic/lib/core"
REL_PLATFORM="../../software-dev-agentic/lib/platforms/$PLATFORM"

# ── 1. Local overrides (highest priority) ────────────────────────────────────

echo ""
echo "1/3 Linking local overrides..."
link_agents "$CLAUDE_DIR/agents.local" "../agents.local"
link_skills "$CLAUDE_DIR/skills.local" "../skills.local"
link_reference "$CLAUDE_DIR/reference.local" "../reference.local"

# ── 2. Platform agents/skills/reference ──────────────────────────────────────

echo ""
echo "2/3 Linking platform: $PLATFORM..."
link_agents "$PLATFORM_DIR/agents" "$REL_PLATFORM/agents"
link_skills "$PLATFORM_DIR/skills" "$REL_PLATFORM/skills"
link_reference "$PLATFORM_DIR/reference" "$REL_PLATFORM/reference"

# ── 3. Core agents/skills/reference (fallback) ───────────────────────────────

echo ""
echo "3/3 Linking core..."
link_agents "$SUBMODULE/lib/core/agents" "$REL_CORE/agents"
link_skills "$SUBMODULE/lib/core/skills" "$REL_CORE/skills"
link_reference "$SUBMODULE/lib/core/reference" "$REL_CORE/reference"

# ── Prune dangling symlinks ───────────────────────────────────────────────────

echo ""
echo "Pruning dangling symlinks..."
_pruned=0
for _dir in "$CLAUDE_DIR/agents" "$CLAUDE_DIR/skills" "$CLAUDE_DIR/hooks"; do
  [ -d "$_dir" ] || continue
  while IFS= read -r _link; do
    if [ ! -e "$_link" ]; then
      rm "$_link"
      echo "  remove  $(basename "$_link") (dangling)"
      _pruned=$((_pruned + 1))
    fi
  done < <(find "$_dir" -maxdepth 1 -type l)
done
# reference/ may be nested — prune recursively
if [ -d "$CLAUDE_DIR/reference" ]; then
  while IFS= read -r _link; do
    if [ ! -e "$_link" ]; then
      rm "$_link"
      echo "  remove  ${_link#$CLAUDE_DIR/} (dangling)"
      _pruned=$((_pruned + 1))
    fi
  done < <(find "$CLAUDE_DIR/reference" -type l)
fi
[ "$_pruned" -eq 0 ] && echo "  clean"
unset _pruned _dir _link

# ── .gitignore ────────────────────────────────────────────────────────────────

echo ""
GITIGNORE="$PROJECT_ROOT/.gitignore"
if grep -qs 'agentic-state' "$GITIGNORE" 2>/dev/null; then
  echo "skip  .gitignore (agentic-state/ already present)"
else
  printf '\n# Claude Code — agentic state (delegation flags, session state, run artifacts)\n.claude/agentic-state/\n' >> "$GITIGNORE"
  echo "patch .gitignore (added agentic-state/)"
fi

# ── Hooks ─────────────────────────────────────────────────────────────────────

echo ""
echo "Linking hooks..."
if [ -d "$PLATFORM_DIR/hooks" ]; then
  mkdir -p "$CLAUDE_DIR/hooks"
  for hook in "$PLATFORM_DIR/hooks/"*.sh; do
    [ -f "$hook" ] || continue
    chmod +x "$hook"
    name="$(basename "$hook")"
    link_if_absent "$REL_PLATFORM/hooks/$name" "$CLAUDE_DIR/hooks/$name"
  done
fi

CORE_HOOKS_DIR="$SUBMODULE/lib/core/hooks"
if [ -d "$CORE_HOOKS_DIR" ]; then
  mkdir -p "$CLAUDE_DIR/hooks"
  for hook in "$CORE_HOOKS_DIR/"*.sh; do
    [ -f "$hook" ] || continue
    chmod +x "$hook"
    name="$(basename "$hook")"
    link_if_absent "$REL_CORE/hooks/$name" "$CLAUDE_DIR/hooks/$name"
  done
fi

# ── Settings ──────────────────────────────────────────────────────────────────

echo ""
SHARED_SETTINGS="$CLAUDE_DIR/settings.json"
if grep -q 'require-builder-feature-orchestrator' "$SHARED_SETTINGS" 2>/dev/null; then
  RESULT=$(python3 - "$SHARED_SETTINGS" <<'EOF'
import sys, re
f = sys.argv[1]
content = open(f).read()
cleaned = re.sub(r',?\s*\{\s*"type"\s*:\s*"command"\s*,\s*"command"\s*:\s*"[^"]*require-builder-feature-orchestrator[^"]*"\s*\}', '', content)
if cleaned != content:
    open(f, 'w').write(cleaned)
    print("removed")
else:
    print("warn")
EOF
  )
  if [ "$RESULT" = "removed" ]; then
    echo "patch settings.json (removed require-builder-feature-orchestrator hook)"
  else
    echo "warn  settings.json — could not auto-remove hook, remove manually"
  fi
else
  echo "skip  settings.json (require-builder-feature-orchestrator not present)"
fi

LOCAL_SETTINGS="$CLAUDE_DIR/settings.local.json"
if [ ! -f "$LOCAL_SETTINGS" ] && [ -f "$PLATFORM_DIR/settings-template.jsonc" ]; then
  cp "$PLATFORM_DIR/settings-template.jsonc" "$LOCAL_SETTINGS"
  echo "copy  .claude/settings.local.json"
elif [ -f "$LOCAL_SETTINGS" ] && grep -q 'PROJECT_ROOT/hooks/' "$LOCAL_SETTINGS"; then
  # Migrate: old template used literal PROJECT_ROOT placeholder — replace with correct relative path
  python3 - "$LOCAL_SETTINGS" <<'PYEOF'
import sys, re
f = sys.argv[1]
content = open(f).read()
fixed = re.sub(r'PROJECT_ROOT/hooks/', '.claude/hooks/', content)
if fixed != content:
    open(f, 'w').write(fixed)
    print("  migrate  settings.local.json (PROJECT_ROOT/hooks/ → .claude/hooks/)")
PYEOF
fi

# ── CLAUDE.md ─────────────────────────────────────────────────────────────────

TEMPLATE="$PLATFORM_DIR/CLAUDE-template.md"
BEGIN_MARKER="<!-- BEGIN software-dev-agentic:$PLATFORM -->"
END_MARKER="<!-- END software-dev-agentic:$PLATFORM -->"

echo ""
if [ ! -f "$TEMPLATE" ]; then
  echo "skip  CLAUDE.md (no template for $PLATFORM)"
elif [ ! -f "$PROJECT_ROOT/CLAUDE.md" ]; then
  cp "$TEMPLATE" "$PROJECT_ROOT/CLAUDE.md"
  echo "copy  CLAUDE.md (from $PLATFORM CLAUDE-template.md)"
elif grep -qF "$BEGIN_MARKER" "$PROJECT_ROOT/CLAUDE.md"; then
  managed_tmp="$(mktemp)"
  awk "/^${BEGIN_MARKER}$/{found=1} found{print} /^${END_MARKER}$/{found=0}" "$TEMPLATE" > "$managed_tmp"
  awk -v begin="$BEGIN_MARKER" -v end="$END_MARKER" -v src="$managed_tmp" '
    $0 == begin { while ((getline line < src) > 0) print line; skip=1; next }
    $0 == end   { skip=0; next }
    !skip        { print }
  ' "$PROJECT_ROOT/CLAUDE.md" > "$PROJECT_ROOT/CLAUDE.md.tmp" && mv "$PROJECT_ROOT/CLAUDE.md.tmp" "$PROJECT_ROOT/CLAUDE.md"
  rm -f "$managed_tmp"
  echo "sync  CLAUDE.md (managed section updated)"
else
  BLOCK=$(sed -n "/<!-- BEGIN software-dev-agentic:$PLATFORM -->/,/<!-- END software-dev-agentic:$PLATFORM -->/p" "$TEMPLATE")
  printf '\n%s\n' "$BLOCK" >> "$PROJECT_ROOT/CLAUDE.md"
  echo "append CLAUDE.md ($PLATFORM block)"
fi

if [ -f "$PROJECT_ROOT/CLAUDE.md" ] && grep -q '\[AppName\]' "$PROJECT_ROOT/CLAUDE.md"; then
  if [ -z "$APP_NAME" ]; then
    printf "  App name (replaces [AppName] in CLAUDE.md): "
    read -r APP_NAME
  fi
  if [ -n "$APP_NAME" ]; then
    sed -i.bak "s/\[AppName\]/$APP_NAME/g" "$PROJECT_ROOT/CLAUDE.md" && rm "$PROJECT_ROOT/CLAUDE.md.bak"
    echo "  ✓  Replaced [AppName] with '$APP_NAME'"
  else
    echo "  ⚠  Fill in [AppName] placeholders in CLAUDE.md"
  fi
fi

# ── Done ──────────────────────────────────────────────────────────────────────

echo ""
echo "Done. software-dev-agentic ($PLATFORM) is wired."
echo ""
echo "Next steps:"
echo "  1. Fill in CLAUDE.md placeholders"
echo "  2. git add .claude/ && git commit -m 'chore: wire software-dev-agentic ($PLATFORM)'"
