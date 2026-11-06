#!/usr/bin/env bash
# After a push to main: wait for Cloudflare's "Workers Builds: <worker>" check on this
# commit, then confirm https://fellowsurvivor.com serves this commit's files.
# Any problem exits non-zero, so the GitHub Actions run fails and GitHub emails a notice.
#
# Usage: scripts/check-cloudflare-deploy.sh <worker-name>
# Needs: gh (GH_TOKEN with checks:read), git, curl, sha256sum, GNU cp.
set -euo pipefail
cd "$(dirname "$0")/.."

worker="$1"
sha="${GITHUB_SHA:-$(git rev-parse HEAD)}"
repo="${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is required}"
site="https://fellowsurvivor.com"
check="Workers Builds: $worker"

# 1) Wait up to 15 minutes for the Cloudflare build of this commit.
state=""
for _ in $(seq 1 60); do
  state=$(gh api "repos/$repo/commits/$sha/check-runs" \
    --jq "[.check_runs[] | select(.name == \"$check\")][0] | if . == null then \"missing\" else .status + \"/\" + (.conclusion // \"\") end")
  case "$state" in
    completed/success) break ;;
    completed/*) echo "::error::Cloudflare build failed for $sha ($check: $state)"; exit 1 ;;
  esac
  sleep 15
done
if [ "$state" != "completed/success" ]; then
  echo "::error::Cloudflare build did not finish within 15 minutes ($check: $state)"
  exit 1
fi
echo "Cloudflare build succeeded: $check"

# 2) Build the same file set Cloudflare published and compare it with the live site.
sh scripts/cloudflare-build.sh >/dev/null
sleep 20  # let the new version reach every edge location
failures=0
checked=0
while IFS= read -r -d '' file; do
  rel="${file#.cf-dist/}"
  [ "$rel" = "_redirects" ] && continue
  case "$rel" in
    index.html) url_path="" ;;
    */index.html) url_path="${rel%index.html}" ;;
    *) url_path="$rel" ;;
  esac
  want=$(sha256sum "$file" | cut -d' ' -f1)
  got=$(curl -sfL --retry 3 --max-time 30 "$site/$url_path" | sha256sum | cut -d' ' -f1) || got="fetch-failed"
  checked=$((checked + 1))
  if [ "$want" != "$got" ]; then
    echo "::error::Live file differs from $sha: $site/$url_path"
    failures=$((failures + 1))
  fi
done < <(find .cf-dist -type f -print0)

echo "Compared $checked files on $site: $failures different"
[ "$failures" -eq 0 ]
