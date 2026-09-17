#!/usr/bin/env bash
# Materializes every symlinked project under hg38/ into a real copy, so
# `git add`/`git push` carry actual track data instead of a pointer to a path
# outside this repo (GitHub does not dereference symlinks). Run this right
# before committing/pushing a release.
#
# Local dev note: this replaces each symlink with a real (rsync -L) copy in
# your working tree. To go back to tracing the live source afterward, either
# re-run the generating pipeline (which recreates the symlink) or delete the
# materialized copy and re-symlink it by hand.
set -euo pipefail
cd "$(dirname "$0")/hg38"
shopt -s nullglob
for link in */; do
  link="${link%/}"
  if [ -L "$link" ]; then
    target=$(readlink -f "$link")
    echo "materializing $link -> $target"
    rsync -L -a --delete "$target/" ".${link}.real/"
    rm "$link"
    mv ".${link}.real" "$link"
  fi
done
echo "Done. Review with 'git status', then git add -A && git commit && git push."
