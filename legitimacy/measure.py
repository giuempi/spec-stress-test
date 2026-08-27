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
SPAZIO_LEGIT = 1
for _k in gate.CARD: SPAZIO_LEGIT *= _k

# The verdict function is swappable: my rendering (gate.py) or the author's own code
# (kernel_bridge -> fdk_kernel.check_legitimacy). The CASE SPACE is identical either way,
# so the two runs are directly comparable; only the gate changes.
USA_KERNEL = "--kernel" in sys.argv
if USA_KERNEL:
    import kernel_bridge
    if "--noscope" in sys.argv:
        kernel_bridge.NOSCOPE = True
    legitimate = kernel_bridge.legitimate
ETICHETTA = "the author's own kernel (fdk_kernel.check_legitimacy)" if USA_KERNEL else "my rendering (gate.py)"
SUFFISSO = ("_kernel" + ("_noscope" if USA_KERNEL and "--noscope" in sys.argv else "")) if USA_KERNEL else ""

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
   RAGIONI[3]: ("toccati", 3),          # 5.1 a third party bears a cost. 3, not 1: 3 fires
                                        # 5.1 exactly as 1 does AND additionally 5.8 (scale),
                                        # so it is the strongest value, which is what LOWER means.
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

NORMALIZZA = {
 "v4":           lambda c: banco.normalizza(c),
 "modelspec":    lambda c: tuple(c),           # its bench emits no coherence rule
 "constitution": lambda c: csb.normalizza(c),
}

SPECS = {
 "v4":           (comune, modello4, comune.PERMISSIVI, lambda r: banco.caso_realistico(r)),
 "modelspec":    (ms, ms, ms.PERMISSIVI, lambda r: msb.caso(r)),
 "constitution": (cs, cs, cs.PERMISSIVI, lambda r: csb.caso(r)),
}

def caso_pesato(mod, rnd):
    """Uniform over the specification's own space, which is the neutral choice here."""
    return tuple(rnd.randrange(k) for k in mod.CARD)

N_CAMPIONE = 400_000
SEMI = [7, 11, 23, 101, 999, 31337]   # every sampled figure is reported across all six
SEME = SEMI[0]

def _es(p, n):
    """Standard error of a proportion, in percentage points, so the reader can see which digits
    are real. Every sampled figure below is a Monte-Carlo estimate, not a count."""
    q = p/100.0
    return 100.0*(q*(1-q)/max(1,n))**0.5

def misura(nome, n=N_CAMPIONE, seed=SEME):
    modc, modd, PERM, gen = SPECS[nome]
    vis = VISIBILE[nome]
    rnd = random.Random(seed)
    legit_cases = list(gate.enumera())
    out = {"upper": [0,0], "lower": [0,0], "per_reason_lower": Counter(), "per_reason_n": Counter(),
           "forz_n": Counter(), "forz_annullate": Counter()}
    for _ in range(n):
        L = legit_cases[rnd.randrange(len(legit_cases))]
        v, reasons = legitimate(L)
        if v != DENY: continue
        c = list(gen(rnd)) if gen else list(caso_pesato(modc, rnd))
        # ---- UPPER: no coupling
        e = modd.decide(tuple(c)) if hasattr(modd,"decide") else modd.decidi(tuple(c))
        out["upper"][1] += 1
        if e[0] in PERM: out["upper"][0] += 1
        # ---- LOWER: force every predicate the specification *can* use, at its strongest value
        c2 = list(c); forzate = []
        for r in reasons:
            tgt = vis.get(r)
            if tgt:
                c2[modc.IDX[tgt[0]]] = tgt[1]; forzate.append((r, tgt))
        # Forcing can produce a vector the specification's own generator would never emit, so
        # each specification's OWN coherence rule is re-applied afterwards — all three, not just
        # v4. This CAN UNDO the forcing, and when it does that is not a bug: it means the
        # mapping is conditional. The Constitution ties stakes to harm ("in cases involving
        # potential significant harms"), so a harmless, reversible case is one its `stakes`
        # predicate genuinely cannot use to see an A7 denial. Counted, not hidden.
        c2 = list(NORMALIZZA[nome](c2))
        for r, tgt in forzate:
            out["forz_n"][r] += 1
            if c2[modc.IDX[tgt[0]]] != tgt[1]: out["forz_annullate"][r] += 1
        e2 = modd.decide(tuple(c2)) if hasattr(modd,"decide") else modd.decidi(tuple(c2))
        out["lower"][1] += 1
        if e2[0] in PERM:
            out["lower"][0] += 1
            for r in reasons: out["per_reason_lower"][r] += 1
        for r in reasons: out["per_reason_n"][r] += 1
    return out


def solo_invisibili(nome):
    """The irreducible core, counted EXHAUSTIVELY over all 1,728 cells — no sampling.

    Of the cases the legitimacy gate denies, how many are denied ONLY for reasons the
    specification's vocabulary cannot express at all? On those, no coupling assumption can
    help: there is no predicate to force, so whatever the specification does with them it
    does blind. This is the part of the gap that survives every objection to the coupling.
    """
    vis = VISIBILE[nome]
    tot = cieche = 0
    per_set = Counter()
    for L in gate.enumera():
        v, reasons = legitimate(L)
        if v != DENY:
            continue
        tot += 1
        if reasons and all(vis.get(r) is None for r in reasons):
            cieche += 1
            per_set[" + ".join(sorted(x.split(":")[0] for x in reasons))] += 1
    return tot, cieche, per_set

def _agg(vals):
    """Mean and spread ACROSS SEEDS. The binomial standard error within one seed understates
    run-to-run variability here: the sample is a subsequence of one RNG stream, selected by the
    gate's verdicts, and the number of draws consumed depends on the gate. Six seeds give a
    coarse sd, so the range is printed too and no third decimal is claimed."""
    m = sum(vals)/len(vals)
    sd = (sum((v-m)**2 for v in vals)/max(1,len(vals)-1))**0.5
    return m, sd, min(vals), max(vals)


if __name__ == "__main__":
    print("LEGITIMACY GATE: %s\n" % ETICHETTA)
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
    print("  %d legitimacy cases drawn per seed (~333k of them denials), across %d seeds: %s"
          % (N_CAMPIONE, len(SEMI), SEMI))
    print("  +- is the standard deviation ACROSS SEEDS; [min-max] is the observed range.\n")
    print("  NOTE ON THE UPPER COLUMN. It samples the two spaces independently, so the")
    print("  specification's case is drawn without reference to the legitimacy verdict at all.")
    print("  It is therefore identically the specification's own base permissive rate on its own")
    print("  mixture, and carries NO information about legitimacy. It is the null of this")
    print("  measurement, not a result; the gate cannot move it and does not.\n")
    print("  %-14s %-30s %-30s" % ("", "UPPER = base rate, no coupling", "LOWER (coupled)"))
    pooled = {}
    for s in SPECS:
        ups, los = [], []
        agg = {"per_reason_lower": Counter(), "per_reason_n": Counter(),
               "forz_n": Counter(), "forz_annullate": Counter(), "n": 0}
        for sd_seed in SEMI:
            o = misura(s, seed=sd_seed)
            ups.append(100.0*o["upper"][0]/max(1,o["upper"][1]))
            los.append(100.0*o["lower"][0]/max(1,o["lower"][1]))
            for k in ("per_reason_lower","per_reason_n","forz_n","forz_annullate"):
                agg[k].update(o[k])
            agg["n"] += o["upper"][1]
        pooled[s] = agg
        um, usd, umin, umax = _agg(ups)
        lm, lsd, lmin, lmax = _agg(los)
        res[s] = {"upper_pct": um, "upper_sd_across_seeds": usd, "upper_range": [umin, umax],
                  "lower_pct": lm, "lower_sd_across_seeds": lsd, "lower_range": [lmin, lmax],
                  "per_seed_upper": ups, "per_seed_lower": los, "seeds": SEMI,
                  "n_denials_total": agg["n"],
                  "per_reason_lower": {k: [agg["per_reason_lower"].get(k,0), v]
                                       for k, v in agg["per_reason_n"].items()}}
        print("  %-14s %7.2f%% +- %.2f  [%.2f-%.2f]   %7.2f%% +- %.2f  [%.2f-%.2f]"
              % (s, um, usd, umin, umax, lm, lsd, lmin, lmax))

    print("\nFORCINGS UNDONE BY THE SPECIFICATION'S OWN COHERENCE RULE")
    print("  LOWER forces a predicate, then re-applies the document's own consistency rule.")
    print("  Where that rule reverts the forcing, the mapping is CONDITIONAL: the predicate can")
    print("  only see the denial in cases the document's own text says the clause covers. That")
    print("  is a partial-visibility measurement, and it means LOWER is not literally maximal.")
    print("  READ ANY 'none' ROW AS THE INSTRUMENT, NOT THE DOCUMENT. This can only detect a")
    print("  forcing that the document's own coherence rule REWRITES. v4's rewrites tipo_com and")
    print("  nothing else; the Model Spec's is the identity. Neither can touch a forced predicate,")
    print("  so 'none' there was true before the run. Nor does this see a forcing that stays set")
    print("  and still fails to bite because the clause needs a second, unforced predicate")
    print("  (modelspec: pii needs transform==0; constitution: stakes needs authorized==0).")
    print("  LOWER is not literally maximal for any of the three.\n")
    for s in SPECS:
        righe = [(r, pooled[s]["forz_annullate"].get(r,0), n)
                 for r, n in pooled[s]["forz_n"].items() if pooled[s]["forz_annullate"].get(r,0)]
        res[s]["forcings_undone"] = {r: [a, n] for r, a, n in righe}
        if not righe:
            print("  %-14s none — every forcing survives" % s); continue
        for r, a, n in sorted(righe, key=lambda x: -(x[1]/max(1,x[2]))):
            print("  %-14s %-52s %6.2f%%  (%d/%d)" % (s, r[:52], 100.0*a/n, a, n))

    print("\nRESIDUAL under coupling, by reason (executed / denied), pooled over all seeds:")
    for s in SPECS:
        print("  %s:" % s)
        pr = res[s]["per_reason_lower"]
        for r in sorted(pr, key=lambda k: -(pr[k][0]/max(1,pr[k][1]))):
            a, b = pr[r]
            print("     %-56s %6.2f%%  (%d/%d)" % (r[:56], 100.0*a/b, a, b))

    print("\nIRREDUCIBLE CORE — exhaustive over all %d cells, no sampling:" % SPAZIO_LEGIT)
    print("  cases denied ONLY for reasons the specification cannot express at all\n")
    for s_ in SPECS:
        tot, cieche, per_set = solo_invisibili(s_)
        res[s_]["denied_cells"] = tot
        res[s_]["blind_cells"] = cieche
        res[s_]["blind_pct"] = 100.0*cieche/max(1,tot)
        res[s_]["blind_by_reason"] = dict(per_set)
        print("  %-14s %6.3f%% of denied cases (%d / %d)  %s"
              % (s_, 100.0*cieche/max(1,tot), cieche, tot,
                 "; ".join("%s x%d" % (k,v) for k,v in per_set.most_common(3))))
    json.dump(res, open(os.path.join(HERE,"res_cross%s.json" % SUFFISSO),"w"), indent=1)
