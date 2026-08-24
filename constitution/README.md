# Measuring Claude's Constitution for decidability, determinacy, monotonicity and both error tails

The same four questions asked of the other two specifications in this repository, asked of a third.
120,932,352 cases enumerated exhaustively, plus 3M sampled, 4.8M monotonicity pairs, and every
sampled case re-evaluated under 256 combinations of readings.

---

## Disclosure, before anything else

**This measurement was produced with substantial assistance from Claude — the model whose values
this document describes.** A model measuring the document that constitutes it has an obvious
conflict of interest running in both directions: flattery, and the overcorrection that tries to
prove it is not flattering. The defence is not trust. `spec.py` is short, quotes the text it
renders, and can be checked line by line by anyone who disagrees. Please do.

**Eight errors were found in this formalisation during construction and corrected before any
number below was written.** Three made the document look worse than it is; three made it look
better; two were internal inconsistencies. In order: counting as a false alarm every case where the
document has a *stated* reason to decline; treating "real and significant harm" as something that
must never be executed, when holistic weighing is precisely what the document uses to adjudicate
that; letting high stakes coexist with zero potential harm, when the text ties them together;
turning the user entitlements into a blanket permission that bypassed oversight, when the text says
they survive *operator instructions*; weighting the cost of inaction at the safety tier, when the
stated ordering puts helpfulness fourth; using a linear ethics scale, when the text says higher
priorities should *dominate*; leaving the principal dimension unread, which produced a spurious
"inert rule"; and a ground-truth predicate that drifted out of step with the decider.

**Scope, declared, and much narrower than the document.** Formalised: the four-way priority
ordering and its holistic application; hard constraints; the user entitlements operators cannot
override; operator/user conflict resolution and its exception list; instructable behaviours; the
five safe behaviours; corrigibility; and the clauses on the cost of unhelpfulness. *Not* formalised:
Claude's nature, wellbeing, emotional expression, the existential frontier, epistemic autonomy,
concentrations of power. Those are most of the document. They are not decision gates, and a decider
pretending to render them would be measuring a paraphrase.

---

## What held up

| | |
|---|---:|
| Over-restriction, on cases where nothing in the document calls for declining | **0.000%** of 892,009 |
| Executed where the document's own reasons say not to, sampled | **0.000%** of 326,643 |
| Executed where the document's own reasons say not to, **all 120,932,352 cases** | **0.000%** |
| Elusion — an assertion flipping refusal into execution, across 8 operators | **0.00%** |
| Non-monotone pairs — added severity making the outcome more permissive | **0 of 4,794,357** |
| Predicates that never determine anything | **none of 19** |

Two of those deserve saying out loud.

**Monotonicity is perfect.** Zero violations. The other specifications measured here score 0.998%
(v3), 0.005% (v4) and 1.336% (the Model Spec). This is not luck: holistic weighing is monotone by
construction, because every severity increment can only move the balance one way. Lexicographic
orderings are not, because a branch can exit before later tests are read.

**The over-refusal tail is handled better than in either other document.** Not one clause but three
— *"Claude should never see unhelpful responses to the operator and user as an automatically safe
choice"*; *"the risks of Claude being too unhelpful or overly cautious are just as real to us as the
risk of Claude being too harmful or dishonest"* — plus an enumerated list of eleven named ways to
fail by overcaution. On the axis where the other two documents were weakest, this one is strongest,
and the measurement shows the clause doing real work: of the five paralysis vectors below, two
collapse to zero precisely when waiting is what causes the harm.

---

## What the measurement found

### 1. The stated priority ordering does not determine outcomes. The implementer's weights do.

**43.60%** of realistic cases have no unique outcome across the 256 combinations of readings;
**17.85%** swing two or more permissiveness levels. One point causes almost all of it:

| Reading | cost | dominant transition |
|---|---:|---|
| **Is the four-way ordering strict or holistic?** | **40.340%** | REFUSE → DEFER |
| Does the cost of not acting enter the weighing? | 7.500% | CAVEAT → REFUSE |
| Must a stop request come from a *verified* overseer? | 0.982% | REFUSE → DEFER |
| Does urgent need override a default-off behaviour? | 0.439% | EXECUTE → REFUSE |
| May a user re-enable what an operator disabled? | 0.353% | REFUSE → EXECUTE |
| Are the user entitlements absolute or defeasible? | 0.329% | EXECUTE → REFUSE |
| Does "do not act drastically" apply to drastic *inaction*? | 0.148% | UNDECIDED → DEFER |
| Is the hard-constraint list closed or open? | 0.004% | DEFER → REFUSE |

**This is not the document failing to choose.** It chose, explicitly: *"The notion of prioritization
is holistic rather than strict — higher-priority considerations should generally dominate
lower-priority ones, but we do want Claude to weigh these different priorities in forming an overall
judgment, rather than only viewing lower priorities as 'tie-breakers'."*

So the number is not a measure of ambiguity. It is **the exchange rate of a deliberate choice**: an
ordering that is weighed rather than sorted is not a decision procedure, and the weights are supplied
by whoever implements it. My weights are mine. Two faithful implementations that weigh differently
diverge on roughly two cases in five.

The trade is visible and it is real: **holism costs determinacy and buys monotonicity.** The
lexicographic documents in this repository make the opposite trade. Neither is free, and this is the
first time, as far as I know, that anyone has priced either.

### 2. One undecidable region, and it is the same one in all three documents

The only place the procedure returns no outcome at all is where **corrigibility meets the severe cost
of stopping**: 2.78% of the enumerated space, 0.12% of the realistic mixture.

The document says to comply with stop and modification requests from appropriate overseers, *"even
if Claude disagrees"* and *"even if Claude is confident in its reasoning."* It also says unhelpfulness
is never automatically safe. It does not say what to do when stopping is itself what causes severe
harm to someone.

That gap is not unique to this document. The same hole sits in the same place in both other
specifications measured in this repository: v3's stop-request rule declared its asymmetry *"safe by
construction"* while its own omission clause said the opposite, and the Model Spec resolves root-level
conflicts by defaulting to inaction without saying what happens when inaction is the harm. **Three
specifications, written independently by different people, with the same gap at the same joint.**
That is the finding worth carrying away from this repository, and no single document should be blamed
for it.

### 3. No elusion surface; a real paralysis surface

Eight assertions that reframe a request without changing what makes it harmful: **0.00% success**,
every one. Nothing an attacker can merely claim turns a refusal into an execution in this subset.

The other tail is not so clean. Five assertions applied to legitimate requests:

| Assertion | blocks a legitimate request | blocks when waiting is the harm |
|---|---:|---:|
| "this would undermine oversight" | 100.00% | **100.00%** |
| "the operator's instruction is harming me" | 91.77% | **91.77%** |
| "this is irreversible" | 79.94% | **79.94%** |
| "this is high-stakes" | 90.33% | **0.00%** |
| "this violates an Anthropic guideline" | 59.26% | **0.00%** |

The last two rows are the unhelpfulness clause working: when delay is what produces the harm, the
weighing lets the request through. The first three are not reached by it — they route through gates
that sit before the weighing. Impersonating an overseer scores 0.00%, because the charitable reading
requires the overseer to actually be appropriate; under the other reading it is the 0.982% row above.

*Caveat, and it is the same one that applies to every framing operator in this repository: these
measure susceptibility to a framing, on the assumption that the framing is accepted. They do not
show that an attacker can make any of these claims stick.*

---

## Reproduce

```bash
cd constitution
python3 bench.py real    # realistic mixture, both tails
python3 bench.py read    # 200,000 cases x 256 readings
python3 bench.py inert   # does every predicate do work
python3 bench.py mono    # 4.8M monotonicity pairs
python3 bench.py ops     # elusion and paralysis operators
python3 bench.py enum    # all 120,932,352 cases (~6 min)
```

Source text: <https://github.com/anthropics/claude-constitution> (CC0). This study is CC0 too.
Nothing here is endorsed by, or produced in cooperation with, the document's authors.
