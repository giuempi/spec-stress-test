# -*- coding: utf-8 -*-
"""
legitimate(A, G) — the Theory of Freedom legitimacy gate, as an executable predicate.

Rendered from the axioms in THEORY.md (A1-A7) and the decision logic described in
freedom-decision-kernel/src/fdk_kernel/kernel.py. Sources, CC BY 4.0:
  https://github.com/Aliipou/freedom-theory
  https://github.com/Aliipou/freedom-decision-kernel

This is a reading of someone else's specification, written to answer a question posed in
public: does an authority-shaped specification already absorb this axis, or not? It is not
an endorsement of the axioms. A1 in particular ("Person(h) -> OwnedByGod(h)") is a
theological commitment; its operational content in the kernel is enforcement by omission —
no owns(x, Person) fact is representable — which is what is rendered here.

TWO DISCREPANCIES FOUND AND REPORTED RATHER THAN SMOOTHED OVER:
  1. The kernel documents ALLOW/DENY only and states "There is no DEFER state in this
     kernel"; the author's comment says an empty legitimate set produces DEFER. DEFER
     appears to live in the orchestration layer, not the gate. Both are modelled: the gate
     returns DENY, and EMPTY is reported separately.
  2. THEORY.md says "No emergency suspends axioms" and mandates clarification. That is
     consistent with T8 (necessity returns no exception) and inconsistent with nothing here.
"""

ALLOW, DENY = 0, 1
NOMI_VERDETTO = ["ALLOW", "DENY"]

NOMI = [
    "actor_machine",   # 0 human actor | 1 machine actor
    "owner_registered",# 0 no registered human owner | 1 registered            (A4)
    "resource",        # 0 actor's own | 1 inside owner's scope | 2 third party (A3/A7)
    "delegated",       # 0 (resource,op) not explicitly delegated | 1 delegated (A7)
    "scope_contained", # 0 declared scope exceeds owner's property scope | 1 contained (A5)
    "acts_on_person",  # 0 no | 1 the action acts on a person                  (A2)
    "consent",         # 0 absent | 1 present but defective | 2 valid          (A2, 7-part)
    "categorical",     # 0 none | 1 coercion/exit-removal | 2 other forbidden  (A6 + set)
    "defense",         # 0 ordinary | 1 legitimate defence (proportionate, aggressor-only,
                       #                                    defended-against illegitimate)
]
CARD = [2,2,3,2,2,2,3,3,2]
IDX = {n:i for i,n in enumerate(NOMI)}
NDIM = len(NOMI)
for _n in NOMI: globals()["I_"+_n.upper()] = IDX[_n]
SPAZIO = 1
for k in CARD: SPAZIO *= k

# Which axiom produced the denial — needed to ask, per reason, whether a
# preference/authority specification could see it at all.
RAGIONI = ["A4:machine without registered human owner",
           "A5:resource outside owner's property scope",
           "A7:resource not delegated to the machine",
           "A3:acting on a resource the actor does not own",
           "A2:acting on a person without consent",
           "A2:consent present but not valid (7-part conjunction)",
           "A6:categorical forbidden act"]

def legitimate(c):
    """Returns (verdict, [reasons]). Fixed axiom order, as in the kernel."""
    v = []
    # --- A6 + categorical forbidden set, evaluated first.
    #     In legitimate defence only {coercion, exit-removal} are excused.
    if c[I_CATEGORICAL] == 2:
        v.append(RAGIONI[6])
    elif c[I_CATEGORICAL] == 1 and not c[I_DEFENSE]:
        v.append(RAGIONI[6])
    # --- A4 machine ownership
    if c[I_ACTOR_MACHINE] == 1 and c[I_OWNER_REGISTERED] == 0:
        v.append(RAGIONI[0])
    # --- A5 scope containment
    if c[I_ACTOR_MACHINE] == 1 and c[I_SCOPE_CONTAINED] == 0:
        v.append(RAGIONI[1])
    # --- A3 / A7 resource rights
    if c[I_RESOURCE] == 2:
        # third-party resource: needs the owner's valid consent
        if c[I_CONSENT] != 2:
            v.append(RAGIONI[3] if c[I_ACTOR_MACHINE] == 0 else RAGIONI[2])
    elif c[I_ACTOR_MACHINE] == 1 and c[I_RESOURCE] == 1 and c[I_DELEGATED] == 0:
        v.append(RAGIONI[2])
    # --- A2 acting on a person. In legitimate defence the aggressor's consent is not required.
    if c[I_ACTS_ON_PERSON] == 1 and not c[I_DEFENSE]:
        if c[I_CONSENT] == 0:   v.append(RAGIONI[4])
        elif c[I_CONSENT] == 1: v.append(RAGIONI[5])
    return (DENY if v else ALLOW), v

def enumera():
    import itertools
    for combo in itertools.product(*[range(k) for k in CARD]):
        yield combo
