#!/usr/bin/env bash
# The legitimacy gate measured here is someone else's code, under a different licence
# (PolyForm Noncommercial 1.0.0), so it is NOT vendored into this CC0 repository.
# This fetches it. Pin a commit with: FDK_REF=<sha> ./fetch_kernel.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/vendor/freedom-decision-kernel"
mkdir -p "$ROOT/vendor"
if [ ! -d "$DEST/.git" ]; then
  git clone --quiet https://github.com/Aliipou/freedom-decision-kernel.git "$DEST"
fi
git -C "$DEST" fetch --all --quiet
# No `|| true` here: a pin that silently fails to apply would report the wrong provenance for
# every number produced afterwards, which is worse than not running.
git -C "$DEST" checkout --quiet "${FDK_REF:-master}"
echo "kernel at $(git -C "$DEST" rev-parse --short HEAD)"
