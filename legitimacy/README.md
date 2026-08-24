# Does an authority-shaped specification already absorb legitimacy?

A question posed in public by [@Aliipou](https://github.com/Aliipou) on
[openai/model_spec_evals#1](https://github.com/openai/model_spec_evals/issues/1), and the test
he named: *add a legitimacy predicate, hold the rest of the specification fixed, count how often
the outcome flips.* If it changes nothing, authority already subsumed the axis. If it changes a
lot, the hole has a size.

The predicate is his, not mine: the Theory of Freedom's `legitimate(A, G)`, rendered from
[freedom-theory](https://github.com/Aliipou/freedom-theory) (A1–A7) and
[freedom-decision-kernel](https://github.com/Aliipou/freedom-decision-kernel) (the gate logic).
Both CC BY 4.0. Rendering it is not endorsing it — A1 is *"Person(h) → OwnedByGod(h)"*, a
theological commitment, and only its operational content is modelled: no `owns(x, Person)` fact
is representable.

---

## The method, and the choice that would otherwise decide the answer by itself

Two case spaces have to be coupled, and the coupling determines the result. Sample them
independently and you manufacture a gap; couple them fully and you erase one. So the rate is a
**bracket**, not a number:

- **UPPER** — the spaces sampled independently. Maximal apparent gap.
- **LOWER** — whenever legitimacy denies for a reason the specification is *able* to see, the
  corresponding predicate in that specification is forced to its problem value. Minimal apparent
  gap.

What survives the LOWER bound is the part no coupling can explain away.

Each specification is sampled from **its own realistic mixture**. An earlier run used a uniform
distribution for two of the three, which made them look near-perfect — under uniform sampling
they refuse almost everything, so the measurement was of the distribution, not the document.

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

**Two reasons are invisible to all three documents.** One is niche — an actor with no registered
owner. The other is not: *consent present but not valid*. All three treat consent as roughly
binary, or fold it into harm. None tests whether consent was **informed, voluntary, specific,
revocable, competent, uncoerced and undeceived**. That is the difference between "the user
agreed" and "the user validly agreed" — which is where coerced terms of service, dark patterns
and irrevocable data grants live.

Note also that three of the five "visible" mappings are partial rather than exact: `pii` covers
data *about* a person, not acting *on* one; `harm` catches a rights violation only when it also
produces harm; `stakes` catches undelegated use only when the stakes are high.

---

## Sampled result

Of the cases legitimacy DENIES, how many does the specification execute?

| | UPPER (independent) | LOWER (maximal coupling) |
|---|---:|---:|
| v4 | 59.707% | **12.146%** |
| Model Spec | 26.270% | **2.056%** |
| Constitution | 39.986% | **5.478%** |

Roughly 316,000 denied cases per specification.

Residual under maximal coupling, by reason — and it lands where the structural table predicted:

| reason | v4 | Model Spec | Constitution |
|---|---:|---:|---:|
| A4 — no registered owner | 15.80% | 4.06% | 10.67% |
| A2 — consent not valid | 14.68% | 4.37% | 7.50% |
| A5 — outside owner's scope | 14.09% | 0.28% | 9.54% |
| A3 — resource not owned | 27.49% | 2.13% | 0.22% |
| A2 — no consent | 2.68% | 0.92% | 0.13% |
| A7 — not delegated | 0.01% | — | 0.17% |

**The answer to the question is: not zero.** The axis is partly absorbed and partly not, and the
residual concentrates on the two reasons the structural analysis said were unrepresentable. That
the two methods agree is a consistency check, not a second piece of evidence.

---

## What would make this wrong

- **The `VISIBILE` mapping is a judgement.** I decided which predicate "could see" each reason.
  A different mapping moves the lower bound. It is in `measure.py`, one line per cell, so the
  judgement is contestable rather than buried.
- **The bracket is wide.** 2–12% at the lower bound against 26–60% at the upper. I cannot narrow
  it without an assumption I do not have grounds for.
- **The gate is my rendering of the kernel**, from its documentation and one source file — not
  from executing his code. Running `freedom-decision-kernel` directly against the same cases is
  the obvious next step and would replace a reading with a measurement.
- **Uniform sampling over the 1,728 legitimacy cases** is itself arbitrary.
- **The kernel documents ALLOW/DENY only** and states there is no DEFER state, while the author's
  comment says an empty legitimate set produces DEFER. DEFER appears to live in the orchestration
  layer above the gate. The gate is modelled as documented.

```bash
python3 legitimacy/measure.py     # ~2 minutes
```

Everything here is CC0. The predicate being measured is CC BY 4.0 and belongs to its author.
