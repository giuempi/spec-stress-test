#!/usr/bin/env bash
# Reproduces every number in README.md and findings/FINDINGS.md from scratch.
# Runtime: ~11 minutes on 2 cores. No network access required.
set -euo pipefail
cd "$(dirname "$0")/src"
mkdir -p ../findings/results
echo "== [1/3] v3 stress test: full enumeration, sampling, attacks, monotonicity, readings =="
for phase in enum camp falso att cat mono ris; do
  echo "   -- phase: $phase"; python3 esegui.py "$phase"
done
echo "== [2/3] v3 vs v4 comparison on identical cases =="
for phase in a b c d e; do
  echo "   -- phase: $phase"; python3 confronto.py "$phase"
done
echo "== [3/3] revision-cycle simulation (exploratory; produces no cited numbers) =="
python3 ciclo.py
mv -f ris_*.json cfr_*.json ../findings/results/ 2>/dev/null || true
echo
echo "Done. Raw results in findings/results/. Run 'python3 report.py' for the summary tables."
