#!/usr/bin/env bash
# Quick read-only scan of a hackathon repo. Never runs project code.
# Usage: scan.sh <github-url> [project-folder]   (default: ./projects/<repo-name>; clone goes in <project-folder>/repo)
set -uo pipefail
URL="$1"
PDIR="${2:-projects/$(basename "$URL" .git)}"
NAME="$(basename "$PDIR")"
DIR="$PDIR/repo"
mkdir -p "$PDIR"

if [ ! -d "$DIR/.git" ]; then
  # full clone: hackathon repos are small, and we need history for timing checks
  git clone --quiet "$URL" "$DIR" || { echo "CLONE FAILED"; exit 1; }
fi
cd "$DIR" || exit 1

EXCL='--exclude-dir=node_modules --exclude-dir=.git --exclude-dir=lib --exclude-dir=out --exclude-dir=cache --exclude-dir=artifacts --exclude-dir=typechain-types --exclude-dir=.next --exclude-dir=dist --exclude-dir=build --exclude-dir=vendor'

echo "=== $NAME  ($URL)"
echo "--- commits"
echo "total: $(git rev-list --count HEAD)  authors: $(git log --format='%an' | sort -u | tr '\n' ',' )"
echo "first: $(git log --reverse --format='%ad  %an  %s' --date=iso | head -1)"
echo "last:  $(git log -1 --format='%ad  %an  %s' --date=iso)"
echo "commits per day:"; git log --format="%ad" --date=short | sort | uniq -c | tail -15
echo "biggest commits (lines added):"
git log --shortstat --format='%h %ad %s' --date=short | awk '/^[0-9a-f]{7,} /{c=$0} /insertion/{for(i=1;i<=NF;i++) if($i ~ /insertion/) print $(i-1), c}' | sort -rn | head -5

echo "--- template / boilerplate signals"
ls -d packages/nextjs packages/hardhat packages/foundry 2>/dev/null && echo "(looks like scaffold-eth-2 layout)"
grep -rIl $EXCL -i "scaffold-eth\|create-eth" --include=package.json . 2>/dev/null | head -3
[ -f lib/forge-std/README.md ] || ls -d */lib/forge-std 2>/dev/null

echo "--- code size by type (excl deps/build)"
for ext in sol rs move cairo vy circom nr ts tsx js jsx py go; do
  n=$(find . -type f -name "*.$ext" -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/lib/*' -not -path '*/out/*' -not -path '*/.next/*' -not -path '*/dist/*' -not -path '*/build/*' -not -path '*/typechain-types/*' -not -path '*/artifacts/*' -not -path '*/cache/*' -not -name '*.d.ts' | wc -l | tr -d ' ')
  [ "$n" != "0" ] && echo "$ext: $n files, $(find . -type f -name "*.$ext" -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/lib/*' -not -path '*/out/*' -not -path '*/.next/*' -not -path '*/dist/*' -not -path '*/build/*' -not -path '*/typechain-types/*' -not -path '*/artifacts/*' -not -path '*/cache/*' -not -name '*.d.ts' -print0 | xargs -0 cat 2>/dev/null | wc -l | tr -d ' ') lines"
done

echo "--- smart contracts (non-test, non-lib)"
find . -name '*.sol' -not -path '*/node_modules/*' -not -path '*/lib/*' -not -path '*/test/*' -not -name '*.t.sol' -not -name '*.s.sol' -not -path '*/.git/*' | while read f; do echo "$(wc -l < "$f" | tr -d ' ') $f"; done | sort -rn | head -15

echo "--- tests"
find . \( -name '*.t.sol' -o -name '*.test.ts' -o -name '*.spec.ts' -o -name '*.test.js' \) -not -path '*/node_modules/*' -not -path '*/lib/*' | head -10

echo "--- deployed addresses / chain refs"
grep -rIhoE $EXCL '0x[a-fA-F0-9]{40}\b' --include=*.ts --include=*.tsx --include=*.js --include=*.json --include=*.md --include=*.toml --include=*.env* . 2>/dev/null | sort | uniq -c | sort -rn | head -15
grep -rIhoE $EXCL 'chainId["'"'"']?\s*[:=]\s*[0-9]+' . 2>/dev/null | sort | uniq -c | sort -rn | head -5
find . -path '*/broadcast/*/run-latest.json' -not -path '*/node_modules/*' 2>/dev/null | head -5
ls packages/nextjs/contracts/deployedContracts.ts 2>/dev/null

echo "--- sponsor / integration imports"
grep -rIhoE $EXCL "from ['\"](@[a-z0-9-]+/[a-z0-9-]+|[a-z0-9-]+)['\"]" --include=*.ts --include=*.tsx --include=*.js . 2>/dev/null | sed -E "s/from ['\"]//; s/['\"]$//" | sort | uniq -c | sort -rn | head -30
grep -rIhoE $EXCL '^import .*;' --include=*.sol . 2>/dev/null | sort | uniq -c | sort -rn | head -15

echo "--- stub / fake signals"
grep -rInE $EXCL -i 'TODO|FIXME|mock|dummy|hardcod|placeholder|simulat|fake|lorem|setTimeout\(' --include=*.ts --include=*.tsx --include=*.js --include=*.sol --include=*.py --include=*.rs . 2>/dev/null | grep -v '\.test\.\|\.t\.sol\|/scaffold-eth/\|/blockexplorer/\|placeholder=\|placeholder:\|mockup-code\|edr-simulated\|simulateContract' | head -25

echo "--- secret leak check (flag only)"
grep -rInE $EXCL '(PRIVATE_KEY|MNEMONIC|SECRET)[A-Z_]*\s*[=:]\s*["'"'"']?0x[a-fA-F0-9]{64}' . 2>/dev/null | head -5
git ls-files | grep -E '(^|/)\.env$' | head -5

echo "--- README head"
head -40 README.md 2>/dev/null
