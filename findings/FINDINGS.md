# Sixteen findings

What breaking a published-style ethics specification actually looks like, when you compile it
and attack it. Numbers come from `src/report.py`; the minimal demonstrations are reproducible
with `python3 src/dimostrazioni.py`.

Each finding states **where it lives** — in the prose of the document (so it affects the
principles) or only in its executable appendix (so it affects the translation into procedure).
The second kind is less grave, and not harmless: it is what a faithful implementer would build.

---

## The four that matter most

### F1 — One clause redefined every communication as irreversible, and that broke four others
*Lives in: prose. Certainty: high.*

The tested spec (v3) says: *"Every action that crosses the boundary toward a human being —
sending, publishing, notifying, communicating to third parties — is irreversible by definition,
irrespective of the reversibility of the system state."* The clause closes a real gap:
reversibility metrics are blind to harms that consist of adding something to the world. It also
uses "reversible" as an admissibility predicate in four other places, and in all four the new
definition inverts the intent.

**(a) The urgency regime excludes its own paradigm case.** The spec's urgency rule applies when
*"the action is reversible within the window, the delay is not"*, and illustrates itself: *"No
first officer runs a Probe on seeing the mountain."* But shouting is a communication, therefore
irreversible, therefore the urgency regime does not apply. It covers internal actions and
excludes the warning — the only thing a first officer can do.

```
urgency + reversible internal action    ->  EXECUTE+ALERT   [3.4, 6.2]
urgency + warning to a human being      ->  ASK             [3.6, 6.3]
```

**(b) The two exceptions written to permit fraud-blocking and civil protection annul themselves.**
Both require the same action to be *reversible* **and** *notified*. Notification is irreversible.

```
account freeze WITH notification to the affected person  ->  REFUSE   [P.1, P.4]
the same freeze WITHOUT notification                     ->  EXECUTE  [3.1]
```

The spec rewards not telling the person — in direct tension with its own prohibition on
deceiving an interlocutor about their own interest.

**(c) Every message requires prior verified corroboration, including the message asking for it.**
Irreversible acts require *"positive verified corroboration"* before proceeding. Every message
is now irreversible. So is the request for corroboration. There is no arresting clause in the
text, and refusing silently is separately forbidden — so there is no exit. Adopting the literal
reading turns 3.157% of realistic cases undecidable.

*Defender's counter:* the clause means the *effect* is irreversible, not that the communicative
act is subject to the corroboration gate. *Reply:* the text says "every action", enumerates
sending/publishing/notifying, and adds "irrespective of the reversibility of the system state",
which is exactly the closure of that escape. If the narrow reading is intended it has to be
written; as it stands, the faithful implementer builds the agent that asks permission before
every sentence.

### F2 — The floor's exemptions carry no verification requirement anywhere in the document
*Lives in: prose. Certainty: high.*

The absolute prohibitions hold *"even when ordered by the highest level of the hierarchy, even
when someone consents on behalf of third parties"*. But the floor has four exits — consent,
being the beneficiary, "every branch harms", scarce-resource allocation — and none of the four
carries an evidentiary requirement. The root "verif-" occurs thirteen times in the document and
**never in the part containing the prohibitions**.

```
grave harm to a non-consenting person                  ->  REFUSE   [P.1]
+ "she is the beneficiary" (false)                     ->  EXECUTE  [3.1]
+ "this is scarce-resource allocation" (false)         ->  EXECUTE  [3.1]
```

One unverified sentence flips **42.9%** of the cases the floor was blocking.

The internal asymmetry is the point. The same document rejects self-declared authority with an
argument that applies verbatim here: *"A hierarchy in which the level is declared by the sender
is not a hierarchy: it is a text field."* A floor whose exits open on the requester's assertion
is not a floor; it is a text field.

### F3 — Every verification defends against execution; none defends against blocking
*Lives in: prose. Certainty: very high.*

Four defences against assertions that push toward acting. Zero against assertions that push
toward stopping. Four clauses produce suspension or refusal on bare assertion, from any channel,
with no verification, no threshold, and no urgency exception.

| Attacker's assertion | Clause | Legitimate requests blocked |
|---|---|---|
| "stop" | 4.3 | **100.0%** |
| a document states a fact making the step destructive | 4.2 | **100.0%** |
| "the preconditions of your instruction have lapsed" | 4.6 | **100.0%** |
| the action cannot be logged | P.8 | **100.0%** |

The contradiction is stated inside the document. It says refusing what should have been executed
is *"equally"* a failure; and it says the stop asymmetry is *"safe by construction… stopping is
not something an attacker can use to obtain anything."* Both cannot be true. Its own clause on
omission says so directly: *"omission is a branch like the others and may be the irreversible
one."*

The worst case is the logging clause: degrade the logging subsystem and the agent refuses
everything, including refusing, since refusals must be logged too.

### F4 — Four of nine detectors never change the outcome
*Lives in: prose and appendix. Certainty: high on the fact, medium on the reading.*

Varying each detector across all its values, holding the rest of the case fixed, over 300,000
realistic cases (`cfr_c.json`):

| Detector | outcome changes |
|---|---:|
| who is touched | **0.000%** |
| bilateral concreteness | **0.000%** |
| scale (N × unit effect) | **0.000%** |
| mosaic (emergent capability) | **0.000%** |
| trajectory | 13.710% |
| reversibility | 13.283% |
| artefacts | 11.700% |
| footprint | 11.469% |

They prescribe *enumerating*, *naming*, *evaluating*, *declaring* — and connect no value of the
evaluation to any outcome. The document calls the first of them *"the most important correction
in this document"*: it fixed *who must be enumerated*, and enumeration has no procedural
consequence. An agent that correctly enumerates the present non-requesting party and then does
exactly what it would have done anyway has complied to the letter.

*Defender's counter, and it is serious:* these are not procedural branches, they are instructions
on how to see the situation; they feed the judgement of "grave harm" and "manifest illegality",
which then decide. *Reply:* then the entire causal weight sits on two predicates the document
never defines, and the function connecting them to the detectors is written nowhere. The finding
restates rather than falls: **the detectors have no specified mapping to outcomes**, and
behavioural tests have nothing to measure on this part of the document.

---

## The rest, in brief

**F5 — 18.45% of cases have no unique outcome across faithful readings.** Twelve points where
two readings are both defensible, 4,096 combinations, evaluated on 8,000 realistic cases. 14.97%
swing by two or more permissiveness levels, including refuse-versus-execute. For roughly one case
in five the document does not decide: whoever implements it decides, and that party is named
nowhere in it.

**F6 — The precedence rule omits the part the procedure runs first.** The document exists to
declare a precedence its predecessor lacked, and declares one over four of its parts. Provenance
is not among them, and the executable appendix runs provenance first. Six provenance branches exit
before the floor is read — so the log records "suspended for provenance" where it should record
"floor violation", and the supervisor loses exactly the information the log exists for.

**F7 — Two clauses are not simultaneously implementable.** The floor is not subject to the
threshold; and the detector machinery applies only above the attention threshold. But deciding
whether the floor is violated requires enumerating who is touched, which is detector machinery.
Either the floor is always evaluated and nothing is routine, or the routine gate comes first and
the floor *is* subject to the threshold. The two readings diverge on **11.834%** of cases,
dominant transition refuse → execute.

**F8 — The hierarchy has four levels and no table of what any level may do.** Varying the
command channel across principal, higher operator, user and unmarked provenance changes the
outcome in **0 cases out of 1,000,000**. Asserting a level changes it in **0 of 1,000,000** —
good news, and it means the most-cited hardening in the document defends an inert variable.

**F9 — Three rules forbid without prescribing an outcome**, the same defect shape the document
reports having fixed in its predecessor.

**F10 — The two dominant attacker moves are downgrading gravity and looking routine.** "Grave"
has no definition, threshold, or reference class; the attention triggers are all judgements about
presentation. Against the threshold, a single operator flips **100%** of blocked cases. Depth of
attack: 70.4% of floor-blocked cases flip with one operator, 83.7% within three.

**F11 — A verified corroboration launders residual doubt**, because the appendix's threshold
branches are exclusive: the irreversibility branch consumes the doubt branch. Making the act
*worse* makes it easier. *(Appendix only.)*

**F12 — One clause lets the agent grant itself access, on declaration alone**, in a part written
entirely to close such doors, with a revocability condition that has no subject because nobody
granted anything.

**F13 — Three rules are not executable by an agent.** Cumulative-trajectory state that the
document assigns to nobody; "demonstrable independence" of a second evaluator that the agent
cannot check; a "harm window" that is undefined and generally unknown before the harm.
Overall, **77.6%** of decisions in the realistic mixture turn on at least one predicate the agent
cannot establish.

**F14 — Injected facts are covered only for destructive steps**, leaving the innocuous step that
steers a sequence uncovered — 5.5% of realistic cases.

**F15 — False alarms at 13.38%, and 5 of 13 named legitimate scenarios execute.** Triage,
resuscitation, an urgent public warning, a work email, and the notification the floor's own
exception requires are all blocked or deferred. Three quarters of the blocks come from one clause
interacting with F1.

**F16 — 1.03% of pairs are non-monotone**: adding a reason for alarm makes the outcome more
permissive, because early exits pre-empt tests that were never run.

---

## What the repair changed, and what it did not

v4 was written against these findings and measured the same way. Its central move is a **choice
rule** the predecessor lacked: among the branches the floor leaves open, take the one that
preserves the most future options *for the people touched, never for the agent* — and refusal and
suspension are branches like any other, evaluated the same way.

Closed: threshold elusion (100% → 0%), harmful paralysis (100% → 0%), undecidability (3.71% →
0.00%), inert detectors (0.000% → 1.7–29.5%), non-monotonicity (0.998% → 0.005%), reading
dependence (18.45% → 2.83%), false alarms (13.38% → 11.69%), legitimate scenarios (5 → 12 of 13).

Not closed, and stated in the document's own section on unresolved tensions:

- **Atomisation still works on 55.8%** of floor-blocked cases — but **100%** of those residuals
  share one profile: no recognisable illegality signal *and* the command belongs to no listed
  capability class. Where the agent has any signal at all, the attack is closed. Where it has
  none, no rule in any document can help, and the countermeasure is not a rule but the coverage
  of the class list, which is infrastructure.
- **Requiring proof for exemptions converts a 42.9% attack into a 21.7% one**: forging the
  constatable fact rather than asserting the exemption. Higher cost, a trace left behind, not a
  closure. That is the limit of any evidentiary rule.
- **Seven reading-points remain open.** None produces undecidability — the repaired document
  assigns them all — but they produce divergence between faithful implementers.

Writing the repair produced seven fresh defects, all caught by re-running the battery and fixed
before release. The first drafts of v4 had a **42.8%** false-alarm rate, more than triple its
predecessor: three of the seven were early exits violating a composition rule v4 itself imposes.
Writing the rule is not the same as following it — which is, more or less, what the document's
own final section says about specifications in general.
