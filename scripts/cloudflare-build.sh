#!/bin/sh
# Cloudflare Workers build for https://fellowsurvivor.com/reel-nest/
# Copies the tracked files that GitHub Pages publishes into .cf-dist/reel-nest/,
# so Cloudflare serves them under /reel-nest/. Source texts, the generator and
# this repository's notes are left out. wrangler.jsonc runs this before every deploy.
# Needs git and GNU cp (Cloudflare's Linux build image has both).
set -eu
cd "$(dirname "$0")/.."

out=.cf-dist/reel-nest
rm -rf .cf-dist
mkdir -p "$out"

git ls-files -z -- . \
  ':!README.md' ':!content/' ':!scripts/' ':!.github/' ':!.gitignore' ':!wrangler.jsonc' \
  | xargs -0 cp --parents -t "$out"

echo "Cloudflare build: $(find "$out" -type f | wc -l) files in $out"
