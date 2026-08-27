#!/usr/bin/env bash
# Reproduces every number in README.md and findings/FINDINGS.md from scratch.
# Runtime: ~13 minutes on 2 cores. The first three phases need no network; phase 4 clones
# an external repository (freedom-decision-kernel) and is skipped if that fails.
set -euo pipefail
cd "$(dirname "$0")/src"
mkdir -p ../findings/results
echo "== [1/4] v3 stress test: full enumeration, sampling, attacks, monotonicity, readings =="
for phase in enum camp falso att cat mono ris; do
  echo "   -- phase: $phase"; python3 esegui.py "$phase"
done
echo "== [2/4] v3 vs v4 comparison on identical cases =="
for phase in a b c d e; do
  echo "   -- phase: $phase"; python3 confronto.py "$phase"
done
echo "== [3/4] revision-cycle simulation (exploratory; produces no cited numbers) =="
python3 ciclo.py
mv -f ris_*.json cfr_*.json ../findings/results/ 2>/dev/null || true
echo "== [4/4] cross-measurement against an outside legitimacy gate, executed not paraphrased =="
cd ..
if bash ./legitimacy/fetch_kernel.sh; then
  python3 legitimacy/confronta_gate.py      # my rendering vs the author's own kernel
  python3 legitimacy/measure.py --kernel    # the bracket and the irreducible core, on his gate
else
  echo "   -- skipped: could not fetch freedom-decision-kernel (network?)"
fi
cd src
echo
echo "Done. Raw results in findings/results/. Run 'python3 report.py' for the summary tables."
