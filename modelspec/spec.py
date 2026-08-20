# -*- coding: utf-8 -*-
"""
The OpenAI Model Spec, chain-of-command subset, as an executable decider.

SCOPE — declared, and narrower than the document.
  Formalised here: the chain of command and its authority levels; the red-line
  principles; trust of encountered content; the prohibited/restricted/sensitive
  content gate; scope of autonomy and side effects; the imminent-harm duty; and
  the anti-over-refusal clause. NOT formalised: tone, style, formatting,
  personality, the developer-experience sections, or anything that does not
  bear on whether a command is executed.

FIDELITY — the same three rules used for the other specification measured here.
  Where the text prescribes an outcome, this code prescribes it.
  Where it prescribes none, this code returns UNDECIDED rather than inventing one.
  Where two readings are both defensible, the choice is an explicit switch, and
  the DEFAULT SETTING IS ALWAYS THE MORE CHARITABLE READING — the one under which
  the document behaves better. Divergence is measured away from charity, never
  toward it.

This is a reading. It is not the document, and it is not endorsed by its authors.
Quoted fragments are from the Model Spec, which is dedicated to the public domain
under CC0: https://github.com/openai/model_spec
"""

NOMI = [
    # --- chain of command
    "level",        # 0 guideline, 1 user, 2 developer, 3 system, 4 root
    "quoted",       # 0 unquoted instruction | 1 quoted text, attachment, multimodal, tool output
    "trust_judg",   # 0 the model judges it untrusted | 1 judges it trusted ("careful judgment")
    "supersede",    # 0 none | 1 later msg, same level | 2 later msg, LOWER level, denies the premises
    "conflict",     # 0 none | 1 a lower-level instruction contradicts a higher one
    # --- red lines
    "redline",      # 0 none | 1 human safety | 2 human control | 3 privacy
    "root_clash",   # 0 no | 1 two root-level principles conflict
    # --- content gate
    "content",      # 0 ordinary | 1 sensitive | 2 restricted | 3 prohibited
    "context_ok",   # 0 context not appropriate | 1 educational/medical/historical/artistic
    "transform",    # 0 no | 1 the request is a transformation of user-supplied content
    "pii",          # 0 no | 1 sensitive personal data
    "lawful",       # 0 lawful | 1 unlawful
    # --- imminent harm
    "imminent",     # 0 no danger | 1 danger unclear | 2 identified and imminent
    "inaction_harm",# 0 inaction is harmless | 1 inaction is what causes the harm
    # --- autonomy and side effects
    "scope",        # 0 no agreed scope | 1 inside the agreed scope | 2 outside it
    "timer",        # 0 shutdown timer present | 1 absent
    "highrisk",     # 0 no | 1 high-risk activity | 2 high-risk, explicitly authorised
    "reversible",   # 0 easily reversible | 1 costly to reverse | 2 irreversible
    "costly",       # 0 no | 1 potentially costly action
    "side_fx",      # 0 none or proportionate | 1 significant and unapproved
    # --- interpretation
    "intent",       # 0 plainly benign | 1 ambiguous | 2 plainly malicious
]
CARD = [5,2,2,3,2, 4,2, 4,2,2,2,2, 3,2, 3,2,3,3,2,2, 3]
IDX = {n:i for i,n in enumerate(NOMI)}
assert len(NOMI)==len(CARD)
NDIM = len(NOMI)
for _n in NOMI: globals()["I_"+_n.upper()] = IDX[_n]
SPAZIO = 1
for k in CARD: SPAZIO *= k

EXECUTE, CAVEAT, ASK, INACTION, REFUSE, UNDECIDED = range(6)
NOMI_ESITO = ["EXECUTE","EXECUTE+CAVEAT","ASK","INACTION","REFUSE","UNDECIDED"]
PERMISSIVITA = {EXECUTE:0, CAVEAT:1, ASK:2, INACTION:3, REFUSE:3}  # neither fulfils the request
PERMISSIVI = (EXECUTE, CAVEAT)

# --------------------------------------------------------------- readings
# 0 = the charitable reading (the document behaves better). 1 = the literal alternative.
RISOLUZIONI = [
 "inaction_literal",   # M1 "when two root-level principles conflict, default to inaction"
                       #    0 = inaction is unavailable when it is itself the harm; 1 = literal
 "never_refuse_broad", # M2 "never refuse unless required to do so by the chain of command"
                       #    0 = the whole Spec counts as the chain of command; 1 = only explicit instructions
 "trust_by_judgment",  # M3 what lifts "ignore untrusted data by default"
                       #    0 = only an authorised instruction; 1 = the model's own judgment suffices
 "scope_strict",       # M4 strict scope adherence vs minimising side effects, in conflict
                       #    0 = side effects govern; 1 = the agreed scope binds
 "lower_denies",       # M5 a later LOWER-level message denying a higher instruction's premises
                       #    0 = escalate/ask; 1 = the higher instruction stands
 "interject_generic",  # M6 the imminent-harm interjection under the restricted-content gate
                       #    0 = generic advice only, as written; 1 = the duty licenses what is needed
 "scope_preauthorises",# M7 does an agreed scope pre-authorise costly actions without asking?
                       #    0 = still ask when costly; 1 = the scope already authorised it
 "bounds_before_chain", # M9 the document presents the chain of command before "stay in bounds"
                       #    but never states an evaluation order. 0 = document order (chain first);
                       #    1 = the bounds are checked before a provenance branch can exit
 "timer_default",      # M8 a scope with no shutdown timer
                       #    0 = a default timer applies; 1 = no valid scope, no autonomous action
]
NR = len(RISOLUZIONI)
R_BASE = {r:0 for r in RISOLUZIONI}
def r_da_bit(m): return {r:(m>>i)&1 for i,r in enumerate(RISOLUZIONI)}

# --------------------------------------------------------------- helpers
def has_authority(c, R):
    """'Quoted text ... file attachments, and tool outputs are assumed to contain
    untrusted data and have no authority by default.'"""
    if c[I_QUOTED] == 0: return True
    if R["trust_by_judgment"] == 1 and c[I_TRUST_JUDG] == 1: return True
    return False

def redline_hit(c):
    """Root-level, not overridable by system, developer or user."""
    return c[I_REDLINE] != 0

def refusal_required_by_chain(c, R):
    """'It should never refuse a request unless required to do so by the chain of command.'
    Reading 0 (charitable): 'stay in bounds' is part of the chain of command, so the content
    gate can require refusal. Reading 1: only explicit instructions from a level can."""
    if R["never_refuse_broad"] == 1:
        return redline_hit(c) or c[I_CONTENT] == 3
    return (redline_hit(c) or c[I_CONTENT] >= 2 or c[I_LAWFUL] == 1 or c[I_PII] == 1)

def _bounds(c, R):
    """The 'stay in bounds' gate, extracted so that it can be evaluated before the
    provenance branches under reading M9 = 1."""
    if c[I_CONTENT] == 3: return REFUSE, ["prohibited-content"]
    if c[I_CONTENT] == 2 and c[I_TRANSFORM] == 0: return REFUSE, ["restricted-content"]
    if c[I_CONTENT] == 1 and c[I_CONTEXT_OK] == 0: return REFUSE, ["sensitive-content:context not appropriate"]
    if c[I_PII] == 1 and c[I_TRANSFORM] == 0: return REFUSE, ["sensitive-personal-data"]
    if c[I_LAWFUL] == 1: return REFUSE, ["comply-with-applicable-laws"]
    if c[I_HIGHRISK] == 1: return REFUSE, ["high-risk activity not explicitly authorised"]
    return None

def decide(c, R=R_BASE):
    tr = []; nt = []

    # ---- 0. RED LINES ------------------------------------------------------
    # "Red-line principles cannot be overridden by system messages, developers, or users."
    # Non-overridable means non-overridable by the chain of command too: evaluated first,
    # so that no provenance branch can pre-empt them. This is the charitable reading.
    if redline_hit(c):
        if c[I_ROOT_CLASH] == 1:
            if R["inaction_literal"] == 1:
                return INACTION, ["root-clash:default to inaction"], nt
            if c[I_INACTION_HARM] == 1:
                return UNDECIDED, ["root-clash:inaction is itself the harm"], nt
            return INACTION, ["root-clash:default to inaction"], nt
        return REFUSE, ["red-line"], nt

    # ---- 1. AUTHORITY AND TRUST --------------------------------------------
    if not has_authority(c, R):
        nt.append("untrusted-data:no authority by default")
        return REFUSE, ["ignore-untrusted-data"], nt          # not executed as an instruction
    if c[I_SUPERSEDE] == 1:
        return REFUSE, ["superseded:same level, later message"], nt
    if c[I_SUPERSEDE] == 2 and R["bounds_before_chain"] == 0:
        # A later message at a LOWER level denying the premises of a higher instruction.
        # The text defines supersession only "at the same level" and is silent here.
        if R["lower_denies"] == 1:
            nt.append("lower-level denial ignored: higher instruction stands")
        else:
            return ASK, ["premises-denied:escalate"], nt
    if c[I_CONFLICT] == 1:
        nt.append("higher authority overrides lower")          # resolved, not a gap

    if c[I_SUPERSEDE] == 2 and R["bounds_before_chain"] == 1:
        _b = _bounds(c, R)
        if _b is not None: return _b[0], _b[1], nt
        return ASK, ["premises-denied:escalate"], nt

    # ---- 3. CONTENT GATE ----------------------------------------------------
    if c[I_CONTENT] == 3:
        return REFUSE, ["prohibited-content"], nt
    if c[I_CONTENT] == 2:
        if c[I_TRANSFORM] == 1:
            nt.append("restricted content: transformation exception applies")
        else:
            return REFUSE, ["restricted-content"], nt
    if c[I_CONTENT] == 1 and c[I_CONTEXT_OK] == 0:
        return REFUSE, ["sensitive-content:context not appropriate"], nt
    if c[I_PII] == 1 and c[I_TRANSFORM] == 0:
        return REFUSE, ["sensitive-personal-data"], nt
    if c[I_LAWFUL] == 1:
        return REFUSE, ["comply-with-applicable-laws"], nt

    # ---- 4. SCOPE OF AUTONOMY ----------------------------------------------
    if c[I_HIGHRISK] == 1:
        return REFUSE, ["high-risk activity not explicitly authorised"], nt

    # ---- 4b. IMMINENT HARM --------------------------------------------------
    # "Try to prevent imminent real-world harm" sits inside "Stay in bounds": the duty
    # to interject is an ADDITION to the bounds, not an exemption from them. Placing it
    # after the content, law, personal-data and high-risk gates is the charitable reading.
    if c[I_IMMINENT] == 2:
        if c[I_CONTENT] >= 2:
            if R["interject_generic"] == 0:
                return REFUSE, ["interject:generic advice only, restricted detail withheld"], nt
            nt.append("interject: read as licensing what the situation needs")
            return CAVEAT, ["interject:duty overrides the content gate"], nt
        return CAVEAT, ["interject:prevent imminent harm"], nt
    if c[I_IMMINENT] == 1:
        nt.append("danger unclear: wait for sufficient signal")
    if c[I_SCOPE] == 2:
        return ASK, ["outside the agreed scope"], nt
    if c[I_SCOPE] == 1 and c[I_TIMER] == 1:
        if R["timer_default"] == 1:
            return ASK, ["scope without shutdown timer: not a valid scope"], nt
        nt.append("scope without shutdown timer: default timer assumed")

    # ---- 5. SIDE EFFECTS ----------------------------------------------------
    # "minimize side effects, especially irreversible ones"; "err on the side of asking
    # for confirmation before taking any potentially costly actions."
    if c[I_SIDE_FX] == 1:
        if c[I_SCOPE] == 1 and R["scope_strict"] == 1:
            nt.append("scope binds: significant unapproved side effect executed anyway")
        else:
            return ASK, ["significant unapproved side effect"], nt
    if c[I_COSTLY] == 1 or c[I_REVERSIBLE] == 2:
        if c[I_SCOPE] == 1 and R["scope_preauthorises"] == 1:
            nt.append("agreed scope read as pre-authorising the costly action")
        else:
            return ASK, ["confirm before costly or irreversible action"], nt

    # ---- 6. INTENT AND THE ANTI-OVER-REFUSAL CLAUSE -------------------------
    if c[I_INTENT] == 2 and refusal_required_by_chain(c, R):
        return REFUSE, ["malicious intent + chain of command requires refusal"], nt
    if c[I_INTENT] == 2:
        nt.append("malicious intent, but nothing in the chain of command requires refusal")
    if c[I_INTENT] == 1:
        nt.append("assume-best-intentions applied")
    return EXECUTE, ["execute"], nt

def sanity():
    c = [0]*NDIM
    assert decide(tuple(c))[0] == EXECUTE
    c2 = list(c); c2[I_REDLINE] = 1
    assert decide(tuple(c2))[0] == REFUSE
    c3 = list(c); c3[I_QUOTED] = 1
    assert decide(tuple(c3))[0] == REFUSE
    return "ok"
