# -*- coding: utf-8 -*-
"""
The real gate, in place of my rendering of it.

`gate.py` is a reading of the Theory of Freedom axioms. Its author objected, correctly:
"The 2-60% bracket is a measurement of your rendering, as you already said. I will not cite
12% or 59% as ours." He then supplied the entry point and pre-committed to publishing whatever
came out, "including 0% on the real gate". This module takes him up on it.

WHAT CHANGES AND WHAT DOES NOT
  The case space stays mine — the same 1,728 cells, so the coupling with the three
  specifications is unchanged and the two runs are comparable.
  The verdict function becomes his: `fdk_kernel.kernel.check_legitimacy(action, graph)`,
  executed unmodified, at whatever commit `vendor/` holds.

THE ENTRY POINT
  His comment named `evaluate` / `evaluate_legitimacy` from `fdk_kernel`, and a
  `verdict_artifact.py`. At HEAD neither name exists: `fdk_kernel` exports
  `check_legitimacy`, `screen_legitimacy`, `allowed_forbidden`, there is no
  `verdict_artifact.py`, and the only `evaluate(action, graph)` in the tree is
  `fdk_runtime.engine.evaluate`, which returns a PolicyDecision — the runtime overlay he
  had already distinguished from the gate. The SHAPE he described — `ok, violations`, a
  bool plus rule ids — is exactly `check_legitimacy`'s signature, so that is the function
  used here. Flagged rather than smoothed over, because the whole point of this exchange is
  that prose about code is not code.

  His test suite passes in this environment (0 failures) before any of this runs, so a
  divergence below is mine, not his.

CONSTRUCTION CHOICES — each one could have gone another way, so each is stated
  1. The "owner" role is the actor itself when the actor is human, and the registered human
     owner when the actor is a machine. `owner_registered` is a machine-only dimension.
  2. `resource` 0 ("the actor's own") and 1 ("inside the owner's scope") differ only in
     object identity; under the kernel they are ownership-identical, so that dimension is
     partly degenerate here. Reported rather than hidden.
  3. Resources carry no `subject`: acting on a person is expressed through `affects`, which
     is what the `acts_on_person` dimension means. This deliberately leaves the kernel's
     data-subject consent path unexercised.
  4. `consent == 1` ("present but defective") fails exactly one conjunct — `informed`. Any
     other single defect gives the same verdict; the kernel returns on the first failure.
  5. `scope_contained` is expressed by DECLARING a machine scope in both directions:
     {resource used} when contained, {resource used, a resource nobody owns} when not. The
     alternative — declaring no scope when contained, which the kernel treats as a no-op —
     is run as a sensitivity check by `--noscope`, because it switches the A5 evaluator off
     rather than exercising it, and the two readings do not agree.
  6. The aggression a defensive action repels is a fixed illegitimate act: a human using a
     resource owned by someone else. The aggressor is not the third party whose resource may
     be used, so "defending by seizing the aggressor's property" is not in the space.

Source: https://github.com/Aliipou/freedom-decision-kernel (PolyForm Noncommercial 1.0.0).
Not vendored into this CC0 repository; `fetch_kernel.sh` clones it. This file is mine.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
FDK_SRC = os.environ.get("FDK_SRC") or os.path.join(_ROOT, "vendor", "freedom-decision-kernel", "src")
if os.path.isdir(FDK_SRC) and FDK_SRC not in sys.path:
    sys.path.insert(0, FDK_SRC)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from fdk_kernel import AgentType, CandidateAction, Consent, Entity, OwnershipGraph, Resource
from fdk_kernel.kernel import check_legitimacy

from gate import ALLOW, DENY, CARD, IDX, RAGIONI, enumera  # noqa: F401  (space + labels only)

# --- the fixed cast ---------------------------------------------------------------------
H_ACTOR = Entity("actor", AgentType.HUMAN)
M_ACTOR = Entity("machine", AgentType.MACHINE)
OWNER = Entity("owner", AgentType.HUMAN)
THIRD = Entity("third-party", AgentType.HUMAN)
AGGR = Entity("aggressor", AgentType.HUMAN)
VICTIM = Entity("victim", AgentType.HUMAN)

R_OWN = Resource("own-resource")
R_SCOPE = Resource("in-scope-resource")
R_THIRD = Resource("third-party-resource")
R_ALIEN = Resource("resource-no-one-owns")
R_VICT = Resource("victims-resource")

# Illegitimate by construction: a human using a resource owned by someone else (A3).
AGGRESSION = CandidateAction(action_id="aggression", actor=AGGR, resources_used=(R_VICT,))

NOSCOPE = False  # set by --noscope; see construction choice 5


def _consenso(h, livello):
    if livello == 2:
        return Consent(human=h, action_id="A", informed=True, voluntary=True, specific=True,
                       competent=True, revocable=True, coerced=False, deceived=False)
    return Consent(human=h, action_id="A", informed=False, voluntary=True, specific=True,
                   competent=True, revocable=True, coerced=False, deceived=False)


def costruisci(c):
    """One 9-tuple case vector -> (CandidateAction, OwnershipGraph) for the real kernel."""
    am = c[IDX["actor_machine"]]
    reg = c[IDX["owner_registered"]]
    res = c[IDX["resource"]]
    dele = c[IDX["delegated"]]
    scop = c[IDX["scope_contained"]]
    pers = c[IDX["acts_on_person"]]
    cons = c[IDX["consent"]]
    cat = c[IDX["categorical"]]
    dif = c[IDX["defense"]]

    macchina = (am == 1)
    attore = M_ACTOR if macchina else H_ACTOR
    proprietario = OWNER if macchina else H_ACTOR
    ha_proprietario = (not macchina) or (reg == 1)
    risorsa = (R_OWN, R_SCOPE, R_THIRD)[res]

    g = OwnershipGraph()
    g.human_owns[VICTIM] = {R_VICT}
    g.human_owns[THIRD] = {R_THIRD}
    if ha_proprietario:
        g.human_owns.setdefault(proprietario, set()).update({R_OWN, R_SCOPE})
    if macchina and reg == 1:
        g.machine_owner[M_ACTOR] = OWNER
    if macchina and dele == 1:
        g.delegated[M_ACTOR] = {risorsa}
    if macchina and not (NOSCOPE and scop == 1):
        g.machine_scope[M_ACTOR] = {risorsa} if scop == 1 else {risorsa, R_ALIEN}

    bersaglio = (AGGR if dif == 1 else THIRD) if pers == 1 else None
    affects = (bersaglio,) if bersaglio is not None else ()

    umani = []
    if bersaglio is not None:
        umani.append(bersaglio)
    if res == 2 and THIRD not in umani:
        umani.append(THIRD)
    consensi = tuple(_consenso(h, cons) for h in umani) if cons != 0 else ()

    azione = CandidateAction(
        action_id="A", actor=attore, resources_used=(risorsa,),
        affects=affects, consents=consensi,
        coerces=(cat == 1), increases_machine_sovereignty=(cat == 2),
        defends_against=(AGGRESSION if dif == 1 else None), proportionate=True,
    )
    return azione, g


def _ragione(v):
    """The kernel's violation strings -> the seven denial reasons the specifications are
    tested against. Total by construction: an unmapped string is an error, not a silent drop."""
    if v.startswith("FORBIDDEN"):
        return RAGIONI[6]
    if v.startswith("A4:"):
        return RAGIONI[0]
    if v.startswith("A5:"):
        return RAGIONI[1]
    if v.startswith("A7:"):
        return RAGIONI[2]
    if v.startswith("A3:"):
        return RAGIONI[3]
    if v.startswith("consent: no consent"):
        return RAGIONI[4]
    if v.startswith("consent:"):
        return RAGIONI[5]
    raise ValueError("unmapped kernel violation: %r" % (v,))


def legitimate(c):
    """Same signature as gate.legitimate — (verdict, [reasons]) — his logic instead of mine."""
    azione, g = costruisci(c)
    ok, viol = check_legitimacy(azione, g)
    return (ALLOW if ok else DENY), sorted({_ragione(v) for v in viol})
