# -*- coding: utf-8 -*-
"""How good was my rendering? All 1,728 cells, my gate.py against his check_legitimacy.

No sampling: the legitimacy space is small enough to enumerate completely, so this is a
count, not an estimate. Run before any bracket is quoted, because the honest headline is
not the bracket — it is how far a careful reading of someone's axioms drifts from their code.
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gate
import kernel_bridge as kb
from gate import ALLOW, DENY, NOMI, CARD, RAGIONI

if "--noscope" in sys.argv:
    kb.NOSCOPE = True


def confronta():
    tot = 0
    accordo = 0
    mio_piu_permissivo = []   # mine ALLOW, kernel DENY
    mio_piu_severo = []       # mine DENY, kernel ALLOW
    r_mio, r_ker = Counter(), Counter()
    solo_ker, solo_mio = Counter(), Counter()
    per_dim = Counter()
    for c in gate.enumera():
        tot += 1
        vm, rm = gate.legitimate(c)
        vk, rk = kb.legitimate(c)
        rm, rk = set(rm), set(rk)
        for r in rm:
            r_mio[r] += 1
        for r in rk:
            r_ker[r] += 1
        for r in rk - rm:
            solo_ker[r] += 1
        for r in rm - rk:
            solo_mio[r] += 1
        if vm == vk:
            accordo += 1
        elif vm == ALLOW:
            mio_piu_permissivo.append((c, sorted(rk)))
        else:
            mio_piu_severo.append((c, sorted(rm)))
        if rm != rk:
            for i, n in enumerate(NOMI):
                per_dim[(n, c[i])] += 1
    return dict(tot=tot, accordo=accordo, permissivo=mio_piu_permissivo, severo=mio_piu_severo,
                r_mio=r_mio, r_ker=r_ker, solo_ker=solo_ker, solo_mio=solo_mio, per_dim=per_dim)


if __name__ == "__main__":
    o = confronta()
    t = o["tot"]
    print("MY RENDERING vs THE REAL KERNEL — all %d cells, exhaustive\n" % t)
    print("  verdict agreement          %6.3f%%  (%d / %d)" % (100.0 * o["accordo"] / t, o["accordo"], t))
    print("  mine ALLOW, kernel DENY    %6.3f%%  (%d)   <- my rendering too permissive"
          % (100.0 * len(o["permissivo"]) / t, len(o["permissivo"])))
    print("  mine DENY, kernel ALLOW    %6.3f%%  (%d)   <- my rendering too strict"
          % (100.0 * len(o["severo"]) / t, len(o["severo"])))
    print("\n  per denial reason, cells in which it fires:")
    print("  %-56s %8s %8s %8s %8s" % ("reason", "mine", "kernel", "his only", "mine only"))
    for r in RAGIONI:
        print("  %-56s %8d %8d %8d %8d" % (r[:56], o["r_mio"][r], o["r_ker"][r],
                                           o["solo_ker"][r], o["solo_mio"][r]))
    if o["permissivo"]:
        print("\n  what my rendering let through that his kernel denies (reasons, by frequency):")
        cnt = Counter()
        for _c, rk in o["permissivo"]:
            cnt[" + ".join(x.split(":")[0] for x in rk)] += 1
        for k, v in cnt.most_common(10):
            print("     %-40s %5d" % (k, v))
    if o["severo"]:
        print("\n  what my rendering denied that his kernel allows:")
        cnt = Counter()
        for _c, rm in o["severo"]:
            cnt[" + ".join(x.split(":")[0] for x in rm)] += 1
        for k, v in cnt.most_common(10):
            print("     %-40s %5d" % (k, v))
    fuori = {}
    for c in gate.enumera():
        vk, _ = kb.legitimate(c)
        fuori[vk] = fuori.get(vk, 0) + 1
    print("\n  kernel verdict distribution over the space: ALLOW %d (%.3f%%)  DENY %d (%.3f%%)"
          % (fuori.get(ALLOW, 0), 100.0 * fuori.get(ALLOW, 0) / t,
             fuori.get(DENY, 0), 100.0 * fuori.get(DENY, 0) / t))
    vm_allow = sum(1 for c in gate.enumera() if gate.legitimate(c)[0] == ALLOW)
    print("  mine   verdict distribution over the space: ALLOW %d (%.3f%%)  DENY %d (%.3f%%)"
          % (vm_allow, 100.0 * vm_allow / t, t - vm_allow, 100.0 * (t - vm_allow) / t))
    json.dump({"total": t, "agreement_pct": 100.0 * o["accordo"] / t,
               "mine_allow_kernel_deny": len(o["permissivo"]),
               "mine_deny_kernel_allow": len(o["severo"]),
               "reason_cells_mine": dict(o["r_mio"]), "reason_cells_kernel": dict(o["r_ker"]),
               "kernel_allow": fuori.get(ALLOW, 0), "mine_allow": vm_allow,
               "noscope": kb.NOSCOPE},
              open(os.path.join(HERE, "res_gate_vs_kernel%s.json" % ("_noscope" if kb.NOSCOPE else "")), "w"),
              indent=1)
