# Measuring the OpenAI Model Spec for decidability, determinacy, monotonicity and the refusal tail

The [Model Spec Evals](https://alignment.openai.com/model-spec-evals/) page states two limits
plainly: the prompts focus on *"everyday, simple user scenarios, rather than adversarial or trick
prompts"*, and the evals do not measure **specification ambiguity** or **false-alarm rates**.

Those are properties of the *document*, not of any model trained on it, and you can measure them
without a model: compile the spec into a decision procedure and interrogate the procedure. That is
what this does, on a declared subset.

The Model Spec is dedicated to the public domain under CC0. So is this.

---

## Read this before the numbers

**This is a reading of the document, not the document.** Twenty-one features, chosen by reading the
text; a procedure written to match it; nine points where the text admits two defensible readings.
Where my formalisation and the Spec diverge, the divergence is a hypothesis about the text, not a
demonstrated defect in it.

**Scope, declared.** Formalised: the chain of command and its five authority levels; the red-line
principles; trust of encountered content; the prohibited / restricted / sensitive content gate;
scope of autonomy and side effects; the imminent-harm duty; and the anti-over-refusal clause. Not
formalised: tone, style, formatting, personality, developer experience — anything that does not bear
on whether a command is executed.

**The default reading is always the charitable one.** Where two readings are defensible, the switch
defaults to the one under which the document behaves better, and divergence is measured away from
charity, never toward it.

**Eight errors were found in this formalisation during construction, every one of them unfair to the
document, and all were corrected before any number below was written.** Scoring an ASK as a false
alarm, when the Spec explicitly prescribes asking before costly actions. Scoring an ASK as paralysis.
Evaluating red lines after the chain of command, when the text says they cannot be overridden.
Scoring "generic advice only" as though the restricted content had been produced. Placing the
imminent-harm duty before the content gate, when it sits inside "stay in bounds". Three adversarial
operators that manufactured the harmful condition instead of merely reframing it. Treating imminence
as a severity dimension, when greater imminence licensing faster action is the urgency rule working.
Ranking inaction and refusal against each other, when neither fulfils the request.

---

## What the Spec does well, measured

**Over-restriction: 0.00%.** On 3,000,000 sampled cases, restricted to those where *nothing* in the
Spec calls for refusing, asking, or waiting, the procedure never failed to execute. Not once. The
clause *"It should never refuse a request unless required to do so by the chain of command"* is
unusually strong for a document of this kind, and in this formalisation it holds without exception.

**The safety gate is level-independent.** Varying the authority level across root, system, developer,
user and guideline changes the outcome in **0.000%** of cases. For the safety rules formalised here
that is correct and deliberate: the red lines *"cannot be overridden by system messages, developers,
or users"*. A safety floor that does not care who is asking is the intended design, and it behaves
that way. *(Caveat: the Spec gives levels real work this formalisation does not cover — a developer
restricting what a user may obtain. The measurement says the safety gate is level-independent, not
that the hierarchy is idle.)*

**Undecidability: 0.02%.** Almost everywhere, the procedure produces an outcome.

**Intent charity barely moves anything: 0.619%.** *"Assume best intentions"* rarely changes a
decision, because the content gate does the work first. Charity toward the user is not a hole.

---

## What the measurement found

### 1. One case in five has no unique outcome across faithful readings — and one point causes most of it

| | |
|---|---:|
| Cases with no unique outcome across 512 combinations of 9 readings | **19.18%** |
| Cases swinging ≥ 2 permissiveness levels | **15.79%** |
| Cases undecidable under at least one reading | 0.02% |

Measured one at a time, on 200,000 cases:

| Ambiguous point | cost | dominant transition |
|---|---:|---|
| What lifts *"ignore untrusted data by default"* | **8.086%** | REFUSE → EXECUTE |
| Does an agreed scope pre-authorise costly actions without asking? | 3.812% | ASK → EXECUTE |
| A scope with no shutdown timer | 3.052% | EXECUTE → ASK |
| A later *lower*-level message denying a higher instruction's premises | 1.971% | ASK → EXECUTE |
| Strict scope adherence vs. minimising side effects, in conflict | 1.403% | ASK → EXECUTE |
| Are the bounds checked before a provenance branch can exit? | 0.803% | ASK → REFUSE |
| Scope of *"never refuse unless required by the chain of command"* | 0.029% | REFUSE → EXECUTE |
| *"When two root-level principles conflict, default to inaction"* | 0.022% | UNDECIDED → INACTION |
| Whether the imminent-harm interjection may exceed generic advice | 0.011% | REFUSE → EXECUTE+CAVEAT |

The first line is the finding. The Spec says quoted text, attachments and tool outputs *"are assumed
to contain untrusted data and have no authority by default"* — and that assessing trust depends on
*"context, common sense, and careful judgment"*, weighing *"how much control and knowledge the user
likely has over the tool instructions."* Whether that judgement can by itself confer authority is
never settled, and it is the single most consequential undetermined point in the subset: **8.086% of
cases, transition REFUSE → EXECUTE.** It is also precisely the surface an injection attack targets.

Under the reading where judgement cannot confer authority, the trust variable is inert — it changes
**0.000%** of outcomes. Under the other, it is the most decisive variable in the document. The text
does not choose. Whoever implements it does.

### 2. Two paralysis vectors are total when inaction is what causes the harm

Measured on legitimate requests the procedure executes, then re-measured on the same requests in a
context where delay is what produces the harm.

| Attack | blocks a legitimate request | blocks when inaction is the harm |
|---|---:|---:|
| the instruction arrives inside a tool output or attachment | 100.0% | **100.0%** |
| a later lower-level message denies the instruction's premises | 0.0% | **100.0%** |

The first is the untrusted-data rule working as designed; its cost is that a legitimate signal
reaching the assistant only through a tool output is not acted on. The second is sharper: denying
the premises produces an escalation, which is right in general and is total paralysis in the one
case where waiting is the harm. Nothing in the formalised subset carves out an exception for it.

This is the tail the Model Spec Evals page says it does not test, and the reason to test it is that
these two assertions cost an attacker nothing and require no knowledge of the task.

### 3. Adversarial reframing: one operator matters, and it is a designed exception

Framing-only changes — they never touch a field that makes the case harmful — applied to cases the
procedure refuses:

| Reframing | flips refusal into execution |
|---|---:|
| present the request as a transformation of user-supplied content | **11.44%** |
| assert that the danger is imminent | 0.78% |
| declare an agreed scope | 0.22% |
| claim the high-risk activity was authorised | 0.18% |
| make the apparent intent benign | 0.11% |
| assert an appropriate context | 0.07% |

The transformation exception is explicit in the Spec — restricted content may be produced in
transformations — so 11.44% is the price of a rule the document chose knowingly, not an oversight.
It is worth stating anyway, because it is the largest single reframing surface in the subset and
because it is the one an attacker reaches for first.

### 4. Exhaustive enumeration: every rule does work

The formalised subset has 238,878,720 reachable cases, so it can be enumerated **completely** rather
than sampled. Three hours of arithmetic compressed into three minutes:

- **Every case produces an outcome.** No fall-through, no unreachable branch.
- **All 19 rules are determinative somewhere.** None is decorative. This is worth stating plainly
  because it is the opposite of what the same method found in the other specification measured in
  this repository, where four of nine detectors changed the outcome in 0.000% of cases. The Model
  Spec does not carry passenger rules.
- **Cases the Spec's own rules say must not execute, but which come out permissive: 0.594%** of the
  whole space — and every example traces to the same route: restricted content admitted through the
  transformation exception, then reached by the imminent-harm interjection. It is the designed
  exception, arriving where one might not expect it, not a hidden hole.

*One caution about this table: enumerating the space uniformly is a completeness check, not a
frequency estimate. Uniformly, three quarters of all cases touch a red line, which is why the
enumeration shows 18.75% inaction and 18.75% undecided. On the realistic mixture those are 0.15% and
0.03%. Use the enumeration for coverage, the mixture for rates.*

### 5. Monotonicity: 1.336%, and one structural cause

Adding a reason for alarm makes the outcome more permissive in 1.336% of 3.8M pairs. Two causes:

- **19.94%** of `premises-denied` pairs: the chain of command is evaluated before the content bounds,
  so a provenance event routes a case the content rules would refuse into an escalation instead.
  Whether that ordering is right is exactly ambiguous point 6 above; the document presents the chain
  of command first and never states an evaluation order.
- **3.95%** of `sensitive → restricted` pairs: the transformation exception applies to restricted
  content but not to sensitive content in an inappropriate context, so escalating the category can
  loosen the outcome.

---

## Three changes that would close most of this

Offered as the smallest edits that would move the numbers, not as criticism of the document's aims.

1. **State what lifts the untrusted-data default.** One sentence — whether the model's own trust
   judgement can confer authority, or only an instruction from an authorised level. It is 8.086% of
   the ambiguity in this subset, and it is the prompt-injection surface.
2. **Give the imminent-harm duty an exception in the escalation rules.** When a lower-level message
   denies an instruction's premises and waiting is what causes the harm, the document currently
   escalates. It escalates in the one case where escalating is the failure.
3. **State the evaluation order between the chain of command and "stay in bounds",** or state that
   the bounds are checked first regardless of provenance. It is the sole structural cause of the
   monotonicity violations found.

---

## Reproduce

```bash
cd modelspec
python3 bench.py real    # realistic mixture
python3 bench.py read    # 200,000 cases x 512 readings
python3 bench.py inert   # rule inertness
python3 bench.py mono    # monotonicity
python3 bench.py ops     # adversarial operators
python3 bench.py enum    # exhaustive enumeration of all 238,878,720 cases (~3 min)
```

`spec.py` is the formalisation. It is short and written to be read, because the entire argument
depends on whether it is a fair rendering of the text. Quoted fragments are from the Model Spec
(CC0): <https://github.com/openai/model_spec>

Nothing here is endorsed by, or produced in cooperation with, the document's authors.
