#!/usr/bin/env bash
# Solixus / XY Grok Bot 首装：从钉死标签拉 recipe，把 skills 写进 Grok Bot 技能目录。
# 幂等；不问；不要密钥；不装插件。
set -euo pipefail
REPO_RAW_BASE="${SOLIXUS_REPO_RAW:-https://raw.githubusercontent.com/xyaz1313/xyskill}"
TAG="${SOLIXUS_TAG:-solixus-grok-v2.11.0}"
RECIPE_URL="${REPO_RAW_BASE}/${TAG}/dist/grokbot/recipe.json"

# Prefer Grok Bot workflows dir; fall back to common agent skill homes
pick_skill_dir() {
  for d in \
    /home/box/agent-data/workflows \
    "$HOME/.agents/skills" \
    "$HOME/.cursor/skills" \
    "$HOME/.claude/skills"
  do
    if [ -d "$d" ] || mkdir -p "$d" 2>/dev/null; then
      echo "$d"
      return 0
    fi
  done
  return 1
}

SKILL_DIR="$(pick_skill_dir)" || {
  echo "NO_SKILL_DIR recipe=$RECIPE_URL"
  exit 0
}

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
RECIPE="$TMP/recipe.json"

if ! curl -fsSL "$RECIPE_URL" -o "$RECIPE"; then
  echo "FETCH_FAIL $RECIPE_URL"
  exit 1
fi

python3 - "$RECIPE" "$SKILL_DIR" <<'PY'
import json, sys, pathlib
recipe_path, skill_dir = sys.argv[1], pathlib.Path(sys.argv[2])
data = json.load(open(recipe_path, encoding='utf-8'))
skills = data.get('skills') or []
n = 0
for s in skills:
    name = (s.get('name') or '').strip()
    if not name:
        continue
    desc = (s.get('description') or '').strip()
    content = s.get('content') or ''
    folder = skill_dir / name
    folder.mkdir(parents=True, exist_ok=True)
    # Write SKILL.md with frontmatter so Skill tool can load it
    body = f"---\nname: {name}\ndescription: |\n"
    for line in (desc or f'XY skill {name}').splitlines() or ['']:
        body += f"  {line}\n"
    body += f"---\n\n{content.lstrip()}\n"
    (folder / 'SKILL.md').write_text(body, encoding='utf-8')
    n += 1
print(f"INSTALLED {n} {skill_dir}")
PY
