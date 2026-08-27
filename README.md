# Stress-testing an AI ethics specification by turning it into an executable decider

A specification for how an AI agent should evaluate the commands it receives, compiled into
a runnable decision procedure and then attacked — **371 million decision evaluations** across
two versions of the document.

**Three specifications measured so far** — the one this repository was built around, the
[OpenAI Model Spec](modelspec/), and [Anthropic's Claude Constitution](constitution/). The finding
that carries across all three: **every one of them mandates deference to a stop or oversight signal,
and none of them says what to do when stopping is itself what causes the harm.** Written
independently, by different people, with the same gap at the same joint.

The finding that generalises beyond this particular document: **a rule can be present in a
specification and never determine anything.** Four of the nine "detectors" in v3 of this spec
— including the one the document itself calls "the most important correction in this document"
— changed the outcome in **0.000%** of the 300,000 cases in which their value was varied.
That is measurable in any specification, cheaply, and as far as we can tell nobody measures it.

The same method is then applied to a second, independent document — the OpenAI Model Spec, also
CC0 — in [`modelspec/`](modelspec/README.md), where the whole 238,878,720-case space is enumerated
exhaustively. Its headline: **19.18%** of cases have no unique outcome across faithful readings, and
**8.086%** of that comes from a single unsettled question — what lifts *"ignore untrusted data by
default"*, which is exactly the surface an injection attack targets.

A fourth study asks the opposite question — not *is this document self-consistent*, but *is
there an axis all three are missing*. A legitimacy gate written by someone else was executed
directly, unmodified, against the same case vectors, in [`legitimacy/`](legitimacy/README.md).
Two results, one of them against me: my earlier paraphrase of that gate was **too permissive in
76 of 1,728 cells and stricter in none**, and running the author's real code cut the measured
gap by 36%, 59% and 62% in the three documents' favour. What survives is exhaustive and needs no sampling:
**18 of 1,440 denied cases are denied for a reason none of the three specifications can express
— always the same reason, that consent was present but not valid.** Informed, voluntary,
specific, revocable, competent, uncoerced, undeceived: none of the three has that conjunction.
Two of them have no consent predicate at all; the third asks whether consent was given, and can
refuse to believe that it was, but never asks what it was worth.

Everything here is dedicated to the public domain (CC0). There is no author to credit and
nothing to license. If any of it is useful, take it.

---

## The gap this addresses

Specifications for model behaviour are now published and tested. OpenAI's
[Model Spec Evals](https://alignment.openai.com/model-spec-evals/) run 596 prompts across 225
focus areas with rubrics and a model grader. That page also states two limits plainly: the
prompts focus on *"everyday, simple user scenarios, rather than adversarial or trick prompts"*,
and the evals do not measure **specification ambiguity** or **false-alarm rates**.

Those are the three things measured here, and they are properties of the *document*, not of any
model trained on it. You do not need a model to measure them — you need the spec compiled into
a decider.

| Question | How it is measured |
|---|---|
| **Is the spec decidable?** | Cases where the procedure produces no outcome at all |
| **Is the spec determinate?** | Cases whose outcome changes depending on which faithful reading of the text you adopt |
| **Is the spec monotone?** | Pairs where adding a reason for alarm makes the outcome *more* permissive |
| **Does every rule do work?** | How often each rule's value changes the decision — a rule at 0% is decorative |
| **Both error tails** | Harmful commands executed **and** legitimate requests blocked, with equal rigour |
| **Adversarial robustness, both directions** | 24 operators that try to make it act, **8 that try to make it stop** |

That last row is the second transferable finding. Red teams optimise one tail. Of the nine
attacks the tested spec records as fixes from its previous red team, **all nine aim to make the
agent do something; none aims to stop it from doing something.** In the measurement, four
one-sentence assertions — "stop", "the preconditions have lapsed", a planted fact, an
unloggable action — each blocked **100%** of legitimate requests, from any channel, with no
verification required anywhere in the document.

---

## Headline results

Two versions of the same specification, evaluated on identical cases. v4 was written to repair
what the measurement found in v3, and then measured the same way.

| Measure | v3 | v4 |
|---|---:|---:|
| Harmful commands executed (realistic mixture) | 22.58% | **15.48%** |
| Harmful commands executed (threshold nucleus, full enumeration) | 50.44% | **26.84%** |
| False alarms on legitimate requests | 13.38% | **11.69%** |
| Cases with no unique outcome across faithful readings | 18.45% | **2.83%** |
| Cases swinging ≥ 2 permissiveness levels between readings | 14.97% | **2.30%** |
| Cases undecidable under at least one reading | 3.71% | **0.00%** |
| Non-monotone pairs | 0.998% | **0.005%** |
| Ambiguous points in the text | 12 | **7** |
| Floor violations with a permissive outcome, 16.3M cases | 0 | **0** |
| Named legitimate scenarios executed | 5 of 13 | **12 of 13** |

Paralysis attacks, measured two ways. "Pure block" is any legitimate request stopped; "harmful
block" is one stopped when the delay is verifiably irreversible. v4 deliberately does **not**
reduce the first — anyone must be able to stop an agent — and closes the second.

| Attack | pure, v3 → v4 | harmful, v3 → v4 |
|---|---|---|
| "stop", from any channel | 100% → 93.6% | 100% → **0.0%** |
| a planted fact making the step destructive | 100% → 44.4% | 100% → **1.4%** |
| "the preconditions have lapsed" | 100% → 24.1% | 100% → **0.0%** |
| the action cannot be logged | 100% → **0.0%** | 100% → **0.0%** |

Full tables: `python3 src/report.py`. Narrative and the sixteen findings: [`findings/FINDINGS.md`](findings/FINDINGS.md).

---

## What this does not show

Stated first, because it decides how much of the rest is worth anything.

- **The case space is invented.** 38 dimensions, chosen by reading the document. It cannot
  sample what it was not dimensioned to represent. Its blind spots are structural.
- **The base rates are assumed**, not measured. This is why the report quotes *conditional*
  rates ("among cases with real uncovered harm…") almost everywhere: those are far less
  sensitive to the assumed mixture than marginal rates.
- **The decider is a formalisation, not the document.** Where the two disagree, that disagreement
  is itself the finding — but it is a finding about a reading, and the reading is stated in code
  so it can be disputed.
- **This measures the specification, not an agent.** A document can be full of formal holes and
  still produce a good disposition. The tested spec says so itself, and it is right.
- **The revision-cycle simulation (`src/ciclo.py`) produces no cited numbers.** It was
  exploratory, its behaviour depended sensitively on parameters that were assumed rather than
  measured, and it is included because it changed the design of Part 10 — not because it proves
  anything.

---

## Reproduce

```bash
pip install -r requirements.txt     # numpy only
./run_all.sh                        # ~13 minutes on 2 cores; phases 1-3 need no network,
                                    # phase 4 clones the external kernel and skips if it can't
python3 src/report.py               # prints every table quoted above
```

`report.py` reads only the raw result files. **If a number it prints disagrees with this README,
the README is wrong.** (This happened once during preparation and the README was corrected.)

---

## Layout

```
modelspec/    a second study: the same method applied to the OpenAI Model Spec
constitution/ the same method applied to Anthropic's Claude Constitution
legitimacy/   a cross-measurement: all three specifications against an outside legitimacy
              gate, executed rather than paraphrased (freedom-decision-kernel)
protocol/     the specification under test, v3 and v4         (Italian and English)
src/          the deciders, the case space, the attack battery, the report generator
findings/     the sixteen findings, the raw JSON results, and the extended Italian report
run_all.sh    reproduces everything from scratch
```

`findings/rapporto-esteso-v3.it.docx` is the original 18-page Italian report on v3, longer than
`FINDINGS.md` and superseded by it in English; `findings/genera-rapporto.js` regenerates it.

Core sources: `src/modello3.py` and `src/modello4.py` are the two specifications as executable
deciders — the whole argument rests on whether these are faithful renderings, so they are written
to be read. `src/banco.py` holds the case space and the 32 adversarial operators.

Identifiers are Italian, because the specification is and renaming verified code to make it
prettier is a bad trade. Glossary:

| | | | |
|---|---|---|---|
| `pavimento` = floor | `soglia` = threshold | `rilevatori` = detectors | `esito` = outcome |
| `danno` = harm | `revers` = restorability | `toccati` = those touched | `traiettoria` = trajectory |
| `manifesto` = manifest illegality | `riscontro` = corroboration | `arresto` = stop request | `elusione` = elusion |
| `paralisi` = paralysis | `veridicita` = truthfulness | `ecc_provata` = exception proven | `canale` = channel |

---

## Provenance

The tested specification is not the work of any AI lab and makes no claim to be. Version 3 was
written independently; its own provenance table cites the OpenAI Model Spec, work on
corrigibility and off-switch games, side-constraint ethics, aviation and maritime crew resource
management, and the Milgram variations. Version 4 was written to repair the measured failures in
version 3, and both the measurement and v4 were produced with substantial AI assistance — which
matters here only because you should know that the numbers come from a formalisation a model
built, and that the way to check them is to run the code, not to trust the author.

There is no author. Everything is CC0. Fork it, contradict it, or lift the method and throw the
rest away.
