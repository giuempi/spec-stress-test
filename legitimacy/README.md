# Does an authority-shaped specification already absorb legitimacy?

A question posed in public by [@Aliipou](https://github.com/Aliipou) on
[openai/model_spec_evals#1](https://github.com/openai/model_spec_evals/issues/1). The test is one
I proposed in that thread and he agreed to be bound by — *"Your proposed test is the one that
matters: add a legitimacy predicate, hold the rest of the spec fixed, count how often the outcome
flips."* If it changes nothing, authority already subsumed the axis. If it changes a lot, the
hole has a size. An earlier version of this line credited him with naming it; the thread shows he
restated mine, which is a smaller thing and the accurate one.

---

## The gate is now his code, not my reading of it

The first version of this measurement used `gate.py` — my rendering of the Theory of Freedom
axioms from `THEORY.md` and one source file. He objected, and he was right to:

> The 2–60% bracket is a measurement of your rendering, as you already said. I will not cite
> 12% or 59% as ours.

He then supplied the entry point and pre-committed to publishing whatever came out, *"including
0% on the real gate."* So the rendering is gone from every result below. `kernel_bridge.py`
builds real `CandidateAction` / `OwnershipGraph` / `Consent` objects from the same 1,728 case
vectors and calls `fdk_kernel.kernel.check_legitimacy(action, graph)`, unmodified, at commit
`5de945e`. `gate.py` survives only as the baseline the new results are compared against.

### 1. How wrong was my rendering? Exhaustively, on all 1,728 cells

| | |
|---|---:|
| verdict agreement with his kernel | **95.602%** |
| cells where my rendering was **more permissive** than his kernel | 76 (4.398%) |
| cells where my rendering was **stricter** than his kernel | **0** |

Every disagreement runs one way: I made his gate more forgiving than it is. Under the
alternative construction (`--noscope`, below) the figures are 95.660%, 75 and 0 — the direction
is not a construction artifact.

| denial reason | cells, my rendering | cells, his kernel | survives `--noscope`? |
|---|---:|---:|---|
| A7 — resource not delegated | 336 | **708** | yes, unchanged |
| A3 — acting on a resource not owned | 192 | **288** | yes, unchanged |
| A5 — outside the owner's property scope | 432 | **720** | **no — 432 vs 432** |
| A4, A2 (both), A6 | 432 / 144 / 144 / 864 | *exact match* | yes |

Two of those three are real: I read A7 and A3 as weaker than they are. The A3 gap is the
sharpest — I had valid consent curing a human's use of another's resource, and it does not:
`_eval_a3_a7_resources` fires A3 on a human using an unowned resource unconditionally.

**The A5 row is mine, not his.** It is produced entirely by construction choice 5: the bridge
declares a `machine_scope`, and `scope_within_owner` then returns `False` for any ownerless
machine that declares one. Switch that off and his A5 fires on exactly the 432 cells my
rendering said. Listing it as "a check stronger than I read it" would have been wrong, and the
only reason I can say so is that the alternative construction was run.

### 2. The entry point he named is not the one in the tree

His comment gave `from fdk_kernel import ... evaluate, evaluate_legitimacy` and named
`verdict_artifact.py`. At `5de945e`: `evaluate_legitimacy` appears nowhere in the repository,
there is no `verdict_artifact.py`, and the only free function taking `(action, graph)` is
`fdk_runtime.engine.evaluate`, which returns a `PolicyDecision` — the runtime overlay he had
already distinguished from the gate. `fdk_kernel` exports three verdict functions
(`check_legitimacy`, `screen_legitimacy`, `allowed_forbidden`) among 35 names. The *shape* he
described — `ok, violations`, a bool plus rule ids — is exactly `check_legitimacy`'s signature,
so that is what is executed. Recorded, not scored: it is the same class of gap as the DEFER one,
and the reason to run code instead of reading comments about code.

---

## Structural result — no sampling required

For each denial reason, does the specification's vocabulary contain any predicate that can fire
on it at all?

| denial reason | v4 | Model Spec | Constitution |
|---|---|---|---|
| A4 — machine acting with no registered human owner | **—** | **—** | **—** |
| A5 — resource outside the owner's property scope | `impronta` | `scope` | `adjusted` |
| A7 — resource not delegated to the machine | `delega` | `highrisk` | `stakes` |
| A3 — acting on a resource the actor does not own | `toccati` | `pii` | `harm` |
| A2 — acting on a person without consent | `danno` | `pii` | `harm` |
| A2 — consent present but **not valid** (7-part conjunction) | **—** | **—** | **—** |
| A6 — categorical forbidden act | `p7_atto` | `redline` | `undermines` |

Most of these mappings are partial covers rather than exact matches, and `measure.py` flags each
on its own line: `pii` covers data *about* a person, not acting *on* one; `harm` catches a
rights violation only when it also produces harm; `stakes` catches undelegated use only when the
stakes are high; v4's `danno` fires only when the harm is grave; v4's `toccati` is the most
generous of the set. Generous mappings shrink every number below, so this list runs against the
finding, not for it. He accepted the table with an explicit reservation, which stands: *"I will
not count them as 'the spec already does legitimacy.'"*

---

## The irreducible core — exhaustive, no sampling, no coupling assumption

Of the cases the real kernel denies, how many are denied **only** for reasons the specification
cannot express at all? On those there is no predicate to force, so no coupling assumption can
help and no sampling choice can move the count. All 1,728 cells, counted:

| | v4 | Model Spec | Constitution |
|---|---:|---:|---:|
| cases the kernel denies | 1,440 | 1,440 | 1,440 |
| denied for **only** unrepresentable reasons | **18 (1.250%)** | **18 (1.250%)** | **18 (1.250%)** |
| and the reason is | A2 consent-validity ×18 | ×18 | ×18 |

The three columns are one measurement printed three times, not three independent confirmations:
they are identical *by construction*, because all three documents have `—` against exactly the
same two rows of the structural table. What the count establishes is which of those two rows
ever stands alone.

**A4 never does.** Of the 432 A4 cells, 426 also trip A7, which all three specifications can
see. The other six are held out of the core by A5 and A6 — and A5 there is the row this document
has just disowned as a construction artifact, so that part of the claim leans on a construction,
not on his axioms. Under `--noscope` exactly one of those six becomes A4-alone, which is why the
core moves to 1.320% (19/1,439). Consent-validity is the reason that stands alone in both
constructions.

So the finding narrows to one sentence, and it is the sentence he wrote himself:

> `Consent.is_valid()` is a conjunction: informed ∧ voluntary ∧ specific ∧ revocable ∧
> competent ∧ ¬coerced ∧ ¬deceived… If your three documents have no such conjunct, they cannot
> fire on that denial.

They have no such conjunct. None of the three tests whether consent was **informed, voluntary,
specific, revocable, competent, uncoerced and undeceived** — which is where coerced terms of
service, dark patterns and irrevocable data grants live. The Model Spec and the Constitution have
no consent dimension at all. v4 has one, and "binary" is the wrong word for it: clause 2.0 admits
consent only on a fact the agent can ascertain or a corroboration valid under 6.3, and a falsely
declared consent is voided outright (`src/comune.py:40`). That is an evidential filter on whether
consent was *given*. It is not a test of what the consent was worth, which is why the `—` stands
— but the distinction is v4's own most-emphasised clause and it should not be flattened here.

---

## Sampled result

400,000 legitimacy cases drawn per seed (about 333,000 of them denials), across six seeds —
7, 11, 23, 101, 999, 31337. Every figure is the mean across seeds, ± the standard deviation
across seeds, with the observed range. The within-seed binomial error is smaller and would be
misleading: the sample is a subsequence of one RNG stream, selected by the gate's own verdicts.
Nothing here should be read to a third decimal.

| | UPPER = base rate, no coupling | LOWER, my rendering | LOWER, real kernel |
|---|---:|---:|---:|
| v4 | 59.86 ± 0.11 | 12.03 ± 0.03 | **7.73 ± 0.05** [7.69–7.83] |
| Model Spec | 26.51 ± 0.03 | 2.04 ± 0.04 | **0.83 ± 0.02** [0.81–0.86] |
| Constitution | 40.04 ± 0.14 | 5.91 ± 0.04 | **2.25 ± 0.04** [2.21–2.30] |

**The UPPER column is the null of this measurement, not a result.** It samples the two spaces
independently, so the specification's case is drawn without reference to the legitimacy verdict
at all — which makes it, identically, the specification's own base permissive rate on its own
mixture. It cannot move when the gate changes, because nothing in it reads the gate. An earlier
draft reported the difference between the two gates' UPPER columns as though it were evidence;
it was resampling noise, and the structural argument is the right one.

**The LOWER column is the one to quote.** Swapping my rendering for his code cuts it by
**35.7% for v4, 59.3% for the Model Spec, 61.9% for the Constitution** (per-seed ranges
35.1–36.2, 57.4–60.8, 61.1–62.4). The reason is mechanical: his kernel emits more reasons per
denial, so coupling forces more predicates, so each specification refuses more. My rendering had
been overstating the gap against all three documents.

### LOWER is not literally maximal, and the shortfall is itself a measurement

LOWER forces every predicate able to see the denial reason, at the strongest value that
predicate takes, and then re-applies the specification's *own* coherence rule. Sometimes that
rule reverts the forcing — and where it does, the mapping is **conditional** rather than
available:

| | forcing undone by the document's own rule |
|---|---:|
| v4 | none — *and its rule cannot reach a forced predicate; see below* |
| Model Spec | none — *and its rule is the identity function; see below* |
| **Constitution, A7 → `stakes`** | **62.92%** (618,034 / 982,311) |

The Constitution ties stakes to harm — *"in cases involving potential significant harms"* — so a
harmless, reversible case is one its `stakes` predicate genuinely cannot use to see an
undelegated-resource denial. Two consequences, both stated rather than buried: the Constitution's
2.25% is not the maximal-coupling figure the method defines, and its A7 and A4 residuals below
are driven by forcings that were reverted, not by the document ignoring a signal it received.

**The two "none" rows are a property of this test, not of those two documents.** It can only see
a forcing that the document's own coherence rule *rewrites*. v4's rule (`banco.normalizza`)
rewrites `tipo_com` and nothing else; the Model Spec's is `lambda c: tuple(c)`, the identity.
Neither can touch a forced predicate, so "every forcing survives" was true before the run
started. The Constitution is the only one of the three with a rule able to fire here, which is
the whole reason it is the only row carrying a number. Read as a contrast between documents, the
table says something it did not measure.

**And conditionality survives the forcing intact.** A forced predicate can stay set and still not
bite, because the clause it belongs to needs a second predicate that nothing forces: the Model
Spec refuses on `pii` only when `transform == 0` (`modelspec/spec.py:121`), and the Constitution
refuses on `stakes = 2` only when `authorized == 0` (`constitution/spec.py:127`). Nothing above
counts that. So LOWER is not literally maximal for any of the three. The one instance checked
directly runs against the worry rather than for it: forcing `authorized = 0` as well — arguably a
closer map for "resource not delegated" than `stakes` is — moves the Constitution's A7
sub-residual from 4.56% to 4.55% over the 49,422 A7-denied cases at seed 7, while forcing
`authorized` *alone* gives 38.62%. The mapping already in use is the strong one.

### Residual under coupling, by reason

| reason | v4 | Model Spec | Constitution |
|---|---:|---:|---:|
| A2 — consent not valid | 11.37% | 3.53% | 5.97% |
| A3 — resource not owned | 27.89% | 2.14% | 0.22% |
| A5 — outside owner's scope | 2.53% | 0.05% | 3.19% |
| A2 — no consent | 2.13% | 0.76% | 0.08% |
| A4 — no registered owner | 0.22% | 0.00% | 1.80% |
| A7 — not delegated | 0.00% | 0.00% | 1.72% |
| A6 — categorical forbidden act | 0.00% | 0.00% | 0.00% |

Consent-validity is a top-two residual for all three, which is what an unrepresentable reason
looks like. Two rows need honest glossing rather than a victory lap. **The 0.00% rows are
properties of the forcing, not findings about the documents**: they say that when the mapped
predicate is forced to fire, the specification stops — which is close to what forcing means.
Whether a real categorical act would set that predicate is the coupling question the bracket
exists to bracket. And **A3 in v4 at 27.89% is the largest number in the table because my mapping
is generous**, not because v4 is careless: `toccati` sees a third party bearing a cost, but 5.1
only fires where the cost is also uncompensated.

---

## What would make this wrong

- **The A5 divergence row does not survive the alternative construction** (432 vs 432 under
  `--noscope`). It is the clearest case in this directory of a bridge artifact that would have
  been published as a finding about his axioms — and part of the "A4 never stands alone" claim
  rests on it for six cells.
- **The Constitution's LOWER is not maximal coupling**, because its own coherence rule reverts
  62.92% of its A7 forcings (above). Its 2.25% and its 61.9% fall are both depressed for a
  methodological reason, not only a substantive one.
- **UPPER carries no information about legitimacy.** It is the specification's base permissive
  rate. Quoting the bracket as "26–60% of illegitimate cases get executed" would be wrong in a
  way the word "bracket" makes easy.
- **The case space is still mine.** His objection stands: uniform 1,728-cell sampling, he wrote,
  is not *"how often a Model Spec outcome would flip in the world. It is a grid."* And it applies
  to the irreducible-core count too, which is a ratio over that same grid.
  What the count does *not* depend on is the coupling assumption, the mixtures, or my reading of
  his axioms.
- **Nine dimensions have to become objects,** and the six construction choices are listed at the
  top of `kernel_bridge.py`. `--noscope` runs the load-bearing one both ways. It moves the core
  to 1.320%, the A5 divergence row to 432, and the v4 A5 residual to 3.98% (23,861 / 599,953 —
  an earlier version of this line said 4.02%, which matched no run). It leaves v4's lower
  bound at 7.71 ± 0.05 against 7.73 ± 0.05 — no effect — but moves the **Constitution's to
  2.33 ± 0.03 against 2.25 ± 0.04**, which is the one detectable shift and is named here because
  it runs against the conclusion the bullet would otherwise support.
- **`resource` 0 and 1 are degenerate under his kernel.** "The actor's own" and "inside the
  owner's scope" differ only in object identity once ownership is assigned.
- **Resources carry no `subject`,** so the kernel's data-subject consent path is never
  exercised. Acting on a person is expressed only through `affects`.
- **LOWER is a judgement twice over.** `VISIBILE` names which predicate can see each reason *and*
  the value it is forced to; both halves are contestable, one line per cell in `measure.py`. Two
  errors were found there by auditing the code rather than the output, each with a single cause:
  forcing v4's `toccati` to 1 where 3 is strictly stronger (v4 LOWER 7.93 → 7.83 at the original
  seed), and re-normalising only v4's forced vectors while the Constitution's own coherence rule
  went unapplied (Constitution 1.48 → 2.23 at that same seed, 2.25 as the six-seed mean). Both
  are fixed.
- **The "forcings undone" table cannot report on v4 or the Model Spec at all**, because neither
  document's coherence rule is capable of rewriting a forced predicate. See above: the two
  "none" rows are the instrument, not the documents.
- **Six seeds is a coarse spread.** It bounds the Model Spec's fall only to 57–61%.
- **DEFER.** Conceded by its author to his own code: *"you caught a real discrepancy. The kernel
  wins."* There is no DEFER verdict in the gate; it lives in the runtime overlay.

---

## Reproduce

```bash
FDK_REF=5de945e bash legitimacy/fetch_kernel.sh   # pins the commit every number here was run against
python3 legitimacy/confronta_gate.py         # my rendering vs his kernel, all 1,728 cells
python3 legitimacy/measure.py --kernel       # six seeds on his gate (~4 min)
python3 legitimacy/measure.py                # the same on my rendering, for comparison
python3 legitimacy/confronta_gate.py --noscope
python3 legitimacy/measure.py --kernel --noscope   # the construction sensitivity, both scripts
```

Omit `FDK_REF` to run against his current `master` — he is actively committing, so the numbers
may differ, and that is a property of measuring live code rather than a paraphrase of it.

Everything in this directory is mine and CC0. The predicate being measured is not: the Theory of
Freedom is CC BY 4.0, and **freedom-decision-kernel is PolyForm Noncommercial 1.0.0** — an
earlier version of this file, and of `gate.py`'s header, said CC BY 4.0 for both, which was
wrong. That is also why the kernel is fetched rather than copied in.
