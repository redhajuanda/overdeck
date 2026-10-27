#!/usr/bin/env bash
# repo-context.sh <repo-dir> — print the "Repo context" block for an implementer brief.
#
# Lists the repo's AGENTS.md (path + size) and every repo skill as name + description
# + SKILL.md path — descriptions only, never the skill body. Paste the output verbatim
# into subagent-prompt.md § Step 0. Works on a clone or a worktree.
# No dependencies beyond bash + awk.
set -euo pipefail

dir="${1:?usage: repo-context.sh <repo-dir>}"
dir="$(cd "$dir" && pwd)"

echo "### Repo context — \`$(basename "$dir")\` at \`$dir\`"
echo
if [ -f "$dir/AGENTS.md" ]; then
  echo "- AGENTS.md: \`$dir/AGENTS.md\` ($(wc -l < "$dir/AGENTS.md") lines) — **read in full before anything else**"
else
  echo "- AGENTS.md: none in this repo"
fi
if [ -f "$dir/CLAUDE.md" ] && ! grep -qx '@AGENTS.md' "$dir/CLAUDE.md"; then
  echo "- CLAUDE.md: \`$dir/CLAUDE.md\` has its own content — read it too"
fi
echo

seen=" "
rows=""
for base in "$dir/.agents/skills" "$dir/.claude/skills" "$dir/.codex/skills"; do
  [ -d "$base" ] || continue
  for f in "$base"/*/SKILL.md; do
    [ -f "$f" ] || continue
    real="$(readlink -f "$f")"
    case "$seen" in *" $real "*) continue ;; esac
    seen="$seen$real "
    row="$(awk -v path="$f" '
      NR == 1 && $0 != "---" { exit }
      NR > 1 && $0 == "---" { done = 1 }
      done { exit }
      NR > 1 {
        if (folding) {
          if ($0 ~ /^[ \t]+/) { sub(/^[ \t]+/, ""); desc = desc (desc ? " " : "") $0; next }
          folding = 0
        }
        if ($0 ~ /^name:/)        { name = $0; sub(/^name:[ \t]*/, "", name) }
        if ($0 ~ /^description:/) {
          d = $0; sub(/^description:[ \t]*/, "", d)
          if (d ~ /^[>|][-+]?$/) { folding = 1; desc = "" } else desc = d
        }
      }
      END {
        gsub(/^["\x27]|["\x27]$/, "", name); gsub(/^["\x27]|["\x27]$/, "", desc)
        gsub(/\|/, "\\|", desc)
        if (name != "") printf "| %s | %s | `%s` |\n", name, desc, path
      }' "$f")"
    [ -n "$row" ] && rows="$rows$row"$'\n'
  done
done

if [ -n "$rows" ]; then
  echo "Repo skills — descriptions only. Open a SKILL.md only when its description matches the task in hand."
  echo
  echo "| Skill | Description | SKILL.md |"
  echo "|---|---|---|"
  printf '%s' "$rows"
else
  echo "Repo skills: none"
fi
