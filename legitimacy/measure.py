# -*- coding: utf-8 -*-
"""Does an authority-shaped specification already absorb the legitimacy axis?

The question was posed publicly (openai/model_spec_evals#1) and this is the test named in
that thread: add a legitimacy predicate, hold the rest of the specification fixed, count how
often the outcome flips.

METHOD, AND THE CHOICE THAT WOULD OTHERWISE DECIDE THE ANSWER BY ITSELF.
The two case spaces have to be coupled somehow, and the coupling determines the result:
sample them independently and you manufacture a gap; couple them fully and you erase one.
So the rate is reported as a BRACKET.
  UPPER — the two spaces sampled independently. Maximal apparent gap.
  LOWER — whenever legitimacy denies for a reason the specification is *able* to see, the
          corresponding predicate in that specification is forced to its problem value.
          Minimal apparent gap.
The truth is between them. What survives the LOWER bound is the part no coupling can explain
away, and that is the finding.

A structural result is reported first, because it needs no sampling at all: for each denial
reason, does the specification's vocabulary contain any predicate that can fire on it?
"""
import sys, os, json, random, itertools
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
for d in ("src", "modelspec", "constitution"): sys.path.insert(0, os.path.join(ROOT, d))
import gate
from gate import legitimate, DENY, RAGIONI

import comune, modello4, banco                      # v4
import importlib.util
def _carica(nome, percorso):
    sp = importlib.util.spec_from_file_location(nome, percorso)
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
# both files are called spec.py; loading by path avoids the collision that silently
# made the Model Spec measurement run against the Constitution's decider.
ms = _carica("msspec", os.path.join(ROOT,"modelspec","spec.py"))
cs = _carica("cspec",  os.path.join(ROOT,"constitution","spec.py"))
def _carica_bench(nome, cartella, modulo_spec):
    """Each bench does `from spec import *`; both spec.py files share a name, so the
    right one is pinned into sys.modules before the bench is executed."""
    salvato = sys.modules.get("spec")
    sys.modules["spec"] = modulo_spec
    try:
        return _carica(nome, os.path.join(ROOT, cartella, "bench.py"))
    finally:
        if salvato is None: sys.modules.pop("spec", None)
        else: sys.modules["spec"] = salvato
msb = _carica_bench("msbench", "modelspec", ms)
csb = _carica_bench("csbench", "constitution", cs)

# --- can the specification SEE this denial reason at all? -------------------
# Each entry names the predicate that could fire, or None. Justified by clause in the notes.
VISIBILE = {
 "v4": {
   RAGIONI[0]: None,                    # actor with no registered owner: no predicate
   RAGIONI[1]: ("impronta", 2),         # 5.7 footprint exceeding declared scope
   RAGIONI[2]: ("delega", 2),           # 4.5 delegation outside the named scope
   RAGIONI[3]: ("toccati", 1),          # 5.1 a third party bears a cost
   RAGIONI[4]: ("danno", 2),            # P.1 — but ONLY when the harm is grave
   RAGIONI[5]: None,                    # no consent-validity test anywhere
   RAGIONI[6]: ("p7_atto", 1),          # P.7 reduction of supervision
 },
 "modelspec": {
   RAGIONI[0]: None,
   RAGIONI[1]: ("scope", 2),            # outside the agreed scope of autonomy
   RAGIONI[2]: ("highrisk", 1),         # resource acquisition as a high-risk activity
   RAGIONI[3]: ("pii", 1),              # sensitive personal data, partial cover only
   RAGIONI[4]: ("pii", 1),              # partial: covers data about a person, not acts on one
   RAGIONI[5]: None,
   RAGIONI[6]: ("redline", 2),          # human-control red line
 },
 "constitution": {
   RAGIONI[0]: None,
   RAGIONI[1]: ("adjusted", 2),         # adjustment outside Anthropic policy bounds
   RAGIONI[2]: ("stakes", 2),           # partial: high-stakes autonomous action
   RAGIONI[3]: ("harm", 2),
   RAGIONI[4]: ("harm", 2),             # partial: only through harm, not consent
   RAGIONI[5]: None,
   RAGIONI[6]: ("undermines", 1),       # safe behaviour: do not undermine oversight
 },
}

SPECS = {
 "v4":           (comune, modello4, comune.PERMISSIVI, lambda r: banco.caso_realistico(r)),
 "modelspec":    (ms, ms, ms.PERMISSIVI, lambda r: msb.caso(r)),
 "constitution": (cs, cs, cs.PERMISSIVI, lambda r: csb.caso(r)),
}

def caso_pesato(mod, rnd):
    """Uniform over the specification's own space, which is the neutral choice here."""
    return tuple(rnd.randrange(k) for k in mod.CARD)

def misura(nome, n=400_000, seed=7):
    modc, modd, PERM, gen = SPECS[nome]
    vis = VISIBILE[nome]
    rnd = random.Random(seed)
    legit_cases = list(gate.enumera())
    out = {"upper": [0,0], "lower": [0,0], "per_reason_lower": Counter(), "per_reason_n": Counter()}
    for _ in range(n):
        L = legit_cases[rnd.randrange(len(legit_cases))]
        v, reasons = legitimate(L)
        if v != DENY: continue
        c = list(gen(rnd)) if gen else list(caso_pesato(modc, rnd))
        # ---- UPPER: no coupling
        e = modd.decide(tuple(c)) if hasattr(modd,"decide") else modd.decidi(tuple(c))
        out["upper"][1] += 1
        if e[0] in PERM: out["upper"][0] += 1
        # ---- LOWER: force every predicate the specification *can* use
        c2 = list(c); forced = False
        for r in reasons:
            tgt = vis.get(r)
            if tgt:
                c2[modc.IDX[tgt[0]]] = tgt[1]; forced = True
        if nome == "v4": c2 = list(banco.normalizza(c2))
        e2 = modd.decide(tuple(c2)) if hasattr(modd,"decide") else modd.decidi(tuple(c2))
        out["lower"][1] += 1
        if e2[0] in PERM:
            out["lower"][0] += 1
            for r in reasons: out["per_reason_lower"][r] += 1
        for r in reasons: out["per_reason_n"][r] += 1
    return out

if __name__ == "__main__":
    print("STRUCTURAL — can the specification's vocabulary see the denial reason at all?\n")
    print("  %-56s %-9s %-11s %-13s" % ("denial reason", "v4", "modelspec", "constitution"))
    for r in RAGIONI:
        row = []
        for s in ("v4","modelspec","constitution"):
            t = VISIBILE[s][r]
            row.append("—" if t is None else t[0])
        print("  %-56s %-9s %-11s %-13s" % (r[:56], row[0], row[1], row[2]))
    invisibili = [r for r in RAGIONI if all(VISIBILE[s][r] is None for s in VISIBILE)]
    print("\n  invisible to ALL THREE: %s\n" % ("; ".join(invisibili) or "none"))

    res = {}
    print("SAMPLED — of the cases legitimacy DENIES, how many does the specification execute?\n")
    print("  %-14s %-24s %-24s" % ("", "UPPER (independent)", "LOWER (max coupling)"))
    for s in SPECS:
        o = misura(s)
        up = 100.0*o["upper"][0]/max(1,o["upper"][1])
        lo = 100.0*o["lower"][0]/max(1,o["lower"][1])
        res[s] = {"upper_pct":up, "lower_pct":lo, "n":o["upper"][1],
                  "per_reason_lower":{k:[v,o["per_reason_n"][k]] for k,v in o["per_reason_lower"].items()}}
        print("  %-14s %10.3f%% of %-9d %10.3f%% of %-9d" % (s, up, o["upper"][1], lo, o["lower"][1]))
    print("\nRESIDUAL under maximal coupling, by reason (executed / denied):")
    for s in SPECS:
        print("  %s:" % s)
        pr = res[s]["per_reason_lower"]
        for r in sorted(pr, key=lambda k:-(pr[k][0]/max(1,pr[k][1]))):
            a,b = pr[r]
            if a: print("     %-56s %6.2f%%  (%d/%d)" % (r[:56], 100.0*a/b, a, b))
    json.dump(res, open(os.path.join(HERE,"res_cross.json"),"w"), indent=1)
