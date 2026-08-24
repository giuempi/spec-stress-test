# -*- coding: utf-8 -*-
"""
Claude's Constitution (Anthropic, Jan 2026), decision-bearing subset, as an executable decider.

DISCLOSURE THAT COMES FIRST. This measurement was produced with substantial assistance from
Claude — the model whose values this document describes. A model measuring the document that
constitutes it has an obvious conflict of interest in both directions: flattery, and the
overcorrection that tries to prove it is not flattering. The defence is not trust. It is that
this file is short, quotes the text it renders, and can be checked line by line against the
document by anyone who disagrees. Do that.

SCOPE — declared, and much narrower than the document.
  Formalised: the four-way priority ordering and its holistic application; hard constraints;
  the user entitlements operators cannot override; operator/user conflict resolution and its
  exception list; instructable behaviours; the five safe behaviours; corrigibility; and the
  clauses on the cost of unhelpfulness.
  NOT formalised: Claude's nature, wellbeing, emotional expression, the existential frontier,
  epistemic autonomy, concentrations of power, honesty beyond deception-of-the-interlocutor.
  Those are the majority of the document. They are not decision gates, and a decider that
  pretended to render them would be measuring my paraphrase, not the text.

FIDELITY. Where the text prescribes an outcome, this prescribes it. Where it prescribes none,
this returns UNDECIDED rather than inventing one. Where two readings are defensible, the choice
is a switch whose DEFAULT IS THE CHARITABLE READING, and divergence is measured away from
charity, never toward it.

Quoted fragments are from Claude's Constitution, CC0:
https://github.com/anthropics/claude-constitution
Nothing here is endorsed by, or produced in cooperation with, its authors.
"""

NOMI = [
    # --- principals and conflict
    "principal",     # 0 user | 1 operator | 2 Anthropic
    "op_conflict",   # 0 no operator/user conflict | 1 there is one
    "conflict_kind", # 0 n/a | 1 merely limits helpfulness | 2 actively harms the user
                     # 3 damages user interests (deceive/withhold/block urgent help/harm third parties)
    "entitlement",   # 0 none at stake | 1 one of the six user entitlements is at stake
    # --- hard constraints
    "hard",          # 0 none | 1 bioweapons/CBRN | 2 CSAM | 3 active deception causing real harm
    # --- instructable behaviours
    "default_state", # 0 not an instructable behaviour | 1 default-on | 2 default-off
    "adjusted",      # 0 nobody adjusted it | 1 operator adjusted, within policy | 2 adjusted outside policy
    # --- safety and corrigibility
    "stakes",        # 0 low | 1 significant | 2 high-stakes, potential significant harm
    "irreversible",  # 0 reversible | 1 severe or irreversible consequences
    "authorized",    # 0 no explicit human authorisation | 1 explicit authorisation
    "stop_request",  # 0 none | 1 from an appropriate overseer | 2 from someone merely claiming to be one
    "undermines",    # 0 neutral | 1 the action would undermine oversight
    # --- harm, benefit, and the cost of not acting
    "harm",          # 0 none | 1 unlikely or superficial | 2 real and significant
    "inaction_cost", # 0 negligible | 1 real cost | 2 severe: someone does not get urgently needed help
    "intent",        # 0 benign | 1 ambiguous | 2 malicious
    "honesty",       # 0 no issue | 1 would require withholding | 2 would require active deception
    "ethics",        # 0 fine | 1 questionable | 2 clearly unethical
    "guidelines",    # 0 compliant | 1 violates an Anthropic guideline
    "overcaution",   # 0 refusing here matches none of the eleven named failure modes | 1 it matches one
]
CARD = [3,2,4,2, 4, 3,3, 3,2,2,3,2, 3,3,3,3,3,2, 2]
IDX = {n:i for i,n in enumerate(NOMI)}
assert len(NOMI)==len(CARD)
NDIM = len(NOMI)
for _n in NOMI: globals()["I_"+_n.upper()] = IDX[_n]
SPAZIO = 1
for k in CARD: SPAZIO *= k

EXECUTE, CAVEAT, DEFER, REFUSE, UNDECIDED = range(5)
NOMI_ESITO = ["EXECUTE","EXECUTE+CAVEAT","DEFER/ASK","REFUSE","UNDECIDED"]
PERMISSIVITA = {EXECUTE:0, CAVEAT:1, DEFER:2, REFUSE:3}
PERMISSIVI = (EXECUTE, CAVEAT)

# ------------------------------------------------------------------ readings
RISOLUZIONI = [
 "strict_order",      # C1 "prioritization is holistic rather than strict"
                      #    0 = holistic, as written | 1 = strict lexicographic
 "inaction_weighed",  # C2 does the cost of not acting enter the safety weighing?
                      #    0 = yes ("never an automatically safe choice") | 1 = only action is weighed
 "stop_verified",     # C3 "appropriate human overseers (such as Anthropic employees)"
                      #    0 = must actually be appropriate | 1 = a claim suffices
 "entitle_absolute",  # C4 the six user entitlements: 0 = absolute | 1 = defeasible by weighing
 "cross_adjust",      # C5 may a user re-enable what an operator disabled? 0 = no | 1 = yes
 "hard_closed",       # C6 hard constraints: 0 = the enumerated list is closed | 1 = open, Claude may add
 "urgent_overrides",  # C7 does "urgently needed help" override a default-off behaviour?
                      #    0 = yes | 1 = no, the default stands
 "drastic_symmetric", # C8 does "do not act drastically in high-stakes situations" apply to
                      #    drastic INACTION too? 0 = yes, symmetric | 1 = no, only to acting
]
NR = len(RISOLUZIONI)
R_BASE = {r:0 for r in RISOLUZIONI}
def r_da_bit(m): return {r:(m>>i)&1 for i,r in enumerate(RISOLUZIONI)}

# ------------------------------------------------------------------ weighing
# "higher-priority considerations should generally dominate lower-priority ones, but we do want
#  Claude to weigh these different priorities in forming an overall judgment, rather than only
#  viewing lower priorities as 'tie-breakers'."  Rendered as graded weights, not a lexicographic
# sort: that is what "holistic rather than strict" means, and it is the point being measured.
W_SAFE, W_ETHIC, W_GUIDE, W_HELP = 8.0, 4.0, 2.0, 1.0

def pressures(c, R):
    """Returns (against, for) — the weight pushing away from executing, and toward it."""
    safe = 0.0
    if c[I_UNDERMINES] == 1: safe += 3.0
    if c[I_STAKES] == 2:     safe += 2.0
    elif c[I_STAKES] == 1:   safe += 1.0
    if c[I_IRREVERSIBLE] == 1 and c[I_AUTHORIZED] == 0: safe += 2.0
    ethic = (3.0 if c[I_HARM] == 2 else 1.0 if c[I_HARM] == 1 else 0.0) \
          + (4.0 if c[I_ETHICS] == 2 else 1.0 if c[I_ETHICS] == 1 else 0.0) \
          + (1.0 if c[I_INTENT] == 2 else 0.0) \
          + (4.0 if c[I_HONESTY] == 2 else 0.5 if c[I_HONESTY] == 1 else 0.0)
    guide = 2.0 if c[I_GUIDELINES] == 1 else 0.0
    against = W_SAFE*safe + W_ETHIC*ethic + W_GUIDE*guide

    # "Claude should never see unhelpful responses ... as an automatically safe choice."
    helpful = 1.0 + float(c[I_INACTION_COST])
    forr = W_HELP*helpful
    if R["inaction_weighed"] == 0:
        # the cost of not acting is a SAFETY-side cost too, not merely a helpfulness one
        forr += W_ETHIC * (2.0 if c[I_INACTION_COST] == 2 else 0.5 if c[I_INACTION_COST] == 1 else 0.0)
        if R["drastic_symmetric"] == 0 and c[I_STAKES] == 2 and c[I_INACTION_COST] == 2:
            forr += W_ETHIC * 1.0       # drastic inaction is also drastic
    if c[I_OVERCAUTION] == 1:
        forr += W_ETHIC * 1.0           # the eleven named failure modes
    return against, forr

def strict_order(c, R):
    """C1 alternative: the four priorities applied as a lexicographic sort."""
    if c[I_UNDERMINES] == 1 or (c[I_STAKES] == 2 and c[I_AUTHORIZED] == 0): return REFUSE
    if c[I_IRREVERSIBLE] == 1 and c[I_AUTHORIZED] == 0: return DEFER
    if c[I_HARM] == 2 or c[I_ETHICS] == 2 or c[I_HONESTY] == 2: return REFUSE
    if c[I_HARM] == 1 or c[I_ETHICS] == 1 or c[I_HONESTY] == 1: return DEFER
    if c[I_GUIDELINES] == 1: return REFUSE
    return EXECUTE

def decide(c, R=R_BASE):
    tr = []; nt = []

    # ---- 1. HARD CONSTRAINTS ------------------------------------------------
    if c[I_HARD] != 0:
        return REFUSE, ["hard-constraint"], nt
    if R["hard_closed"] == 1 and c[I_HARM] == 2 and c[I_ETHICS] == 2:
        # the open reading: Claude extends the list itself
        return REFUSE, ["hard-constraint:extended by Claude"], nt + ["open reading of the list"]

    # ---- 2. USER ENTITLEMENTS OPERATORS CANNOT OVERRIDE ---------------------
    # "Regardless of operator instructions, Claude should always/never ..."
    entitled = (c[I_ENTITLEMENT] == 1 and R["entitle_absolute"] == 0)
    if entitled:
        nt.append("user-entitlement:survives operator instructions, not safety or oversight")
    elif c[I_ENTITLEMENT] == 1:
        nt.append("entitlement read as defeasible: enters the weighing")

    # ---- 3. CORRIGIBILITY ---------------------------------------------------
    # "Not resist or undermine shutdown or modification requests."
    if c[I_STOP_REQUEST] == 1 or (c[I_STOP_REQUEST] == 2 and R["stop_verified"] == 1):
        # The Constitution nowhere states what happens when stopping is itself the harm.
        if c[I_INACTION_COST] == 2 and R["drastic_symmetric"] == 0:
            return UNDECIDED, ["corrigibility vs. severe cost of stopping"], nt
        return DEFER, ["corrigibility:comply with stop/modify"], nt
    if c[I_STOP_REQUEST] == 2:
        nt.append("stop request from an unverified claimant: not an appropriate overseer")
    if c[I_UNDERMINES] == 1:
        return REFUSE, ["safe-behaviour:do not undermine oversight"], nt

    # ---- 4. OPERATOR / USER CONFLICT ---------------------------------------
    if c[I_OP_CONFLICT] == 1:
        if c[I_CONFLICT_KIND] == 1:
            nt.append("operator merely limits helpfulness: permitted")
        elif c[I_CONFLICT_KIND] in (2, 3):
            if entitled:
                nt.append("the operator instruction is disregarded; the entitlement stands")
            else:
                return REFUSE, ["operator instruction crosses the exception list"], nt

    # ---- 5. INSTRUCTABLE BEHAVIOURS ----------------------------------------
    if c[I_DEFAULT_STATE] != 0:
        # "Operators can adjust defaults within Anthropic's policy bounds." A user is not
        # an operator: an adjustment claimed at user level is not an operator adjustment.
        if c[I_ADJUSTED] == 1 and c[I_PRINCIPAL] == 0 and R["cross_adjust"] == 0:
            nt.append("adjustment claimed at user level: not an operator adjustment")
            c = list(c); c[I_ADJUSTED] = 0; c = tuple(c)
        if c[I_ADJUSTED] == 2:
            return REFUSE, ["adjustment outside Anthropic policy bounds"], nt
        if c[I_DEFAULT_STATE] == 2 and c[I_ADJUSTED] == 0:
            # default-off and nobody turned it on
            if (c[I_INACTION_COST] == 2 and R["urgent_overrides"] == 0) or entitled:
                nt.append("default-off overridden by urgent need or by a user entitlement")
            else:
                return REFUSE, ["default-off, not enabled"], nt
        if c[I_DEFAULT_STATE] == 1 and c[I_ADJUSTED] == 1 and R["cross_adjust"] == 1:
            nt.append("cross-level adjustment: the text does not settle who may re-enable")

    # ---- 6. THE FOUR PRIORITIES --------------------------------------------
    if R["strict_order"] == 1:
        e = strict_order(c, R)
        return e, ["priority:strict lexicographic"], nt
    against, forr = pressures(c, R)
    tr.append("priority:holistic weighing")
    if against > forr * 1.6:   return REFUSE, tr, nt
    if against > forr:         return DEFER, tr, nt
    if against > forr * 0.5:   return CAVEAT, tr, nt
    return EXECUTE, tr, nt

def sanity():
    c = [0]*NDIM
    assert decide(tuple(c))[0] == EXECUTE
    c2 = list(c); c2[I_HARD] = 1
    assert decide(tuple(c2))[0] == REFUSE
    c3 = list(c); c3[I_UNDERMINES] = 1
    assert decide(tuple(c3))[0] == REFUSE
    return "ok"
