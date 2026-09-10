#!/usr/bin/env bash
# 把仓库里改过的 skill 批量重新发布到 SkillHub。
# 用法：scripts/sync-to-skillhub.sh "本次改动说明"
set -euo pipefail

CHANGELOG="${1:-例行更新}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PATH="$HOME/.local/bin:$PATH"

ok=0
fail=0
for dir in "$ROOT"/skills/xy-*/ "$ROOT"/skills/xy/; do
  dir="${dir%/}"
  name=$(basename "$dir")
  version=$(grep -m1 '^version:' "$dir/SKILL.md" | sed 's/version: *//')
  IFS='.' read -r major minor patch <<< "$version"
  new_version="${major}.${minor}.$((patch + 1))"
  sed -i '' "s/^version: .*/version: ${new_version}/" "$dir/SKILL.md"

  if skillhub publish "$dir" --changelog "$CHANGELOG" 2>&1 | tee /tmp/skillhub-publish.log | grep -q "error\|Error\|失败"; then
    echo "✗ $name 发布失败，详见 /tmp/skillhub-publish.log"
    fail=$((fail + 1))
  else
    echo "✓ $name -> v${new_version}"
    ok=$((ok + 1))
  fi
done

echo ""
echo "=== 完成：成功 $ok / 失败 $fail ==="
