---
name: validate-idea
description: >-
  Use this skill to test whether a product or business idea is worth building
  before committing to build it: identify the riskiest assumption, design the
  cheapest experiment that could falsify it, run it, and turn the evidence into a
  go/pivot/kill decision. Use when the user says "validate my idea", "should I
  build this", "is there real demand", "test this before I build it", "design an
  experiment to test X", "customer interviews", "user research questions",
  "the Mom Test", "users say they want it but don't buy", "smoke test", "concierge
  MVP", "pretotype", or "riskiest assumption". Do not use for sizing a market or
  reading the competitive landscape from desk research (use research-market), for
  refining a vague idea's intent before any test exists (use clarify-ambiguity),
  for choosing between solution approaches (use explore-solutions), or for writing
  the PRD once the idea is validated (use write-product-spec).
---

## Purpose

Run the cheapest test that could prove a product idea wrong, before any of it is built. The deliverable is an experiment plan with a pre-committed pass/fail threshold (and the interview script, landing-page copy, or concierge plan it needs), followed by a synthesis of the evidence into a Go, Pivot, or Kill verdict. This skill executes validation; `write-product-spec` step 8 only *names* the assumptions to test, and `research-market` reads the market from the outside. This one collects primary evidence from real people doing real things.

The one rule the whole skill defends: **validate by observing what people actually do, not by asking what they would do.** Stated intent ("yes I'd use that", "great idea") is the default output of a politeness reflex and carries zero signal. Past behavior and costly commitments are the only reliable data. Every step below exists to keep the test anchored to behavior.

## Workflow

- [ ] 1. Surface the assumptions and rank by risk; pick the single riskiest
- [ ] 2. Design the cheapest test that could falsify it, with a pass/fail threshold set *before* running
- [ ] 3. Run it (interviews by the Mom Test rules; demand tests by skin-in-the-game)
- [ ] 4. Synthesize evidence against the threshold into Go / Pivot / Kill

### 1. Surface and rank the assumptions

List the beliefs the idea silently rests on. If the user has a `write-product-spec` already, its "assumptions-to-test" are the input; otherwise elicit them. Sort each into one of three risk types:

| Type | The bet | Usual failure |
|---|---|---|
| Desirability | People want this enough to change behavior | Nobody actually has the pain, or not badly enough |
| Viability | The business works (they pay, the math closes) | They want it but won't pay what it costs to serve |
| Feasibility | We can actually build and deliver it | Almost never the fatal one early; defer it |

Rank by **risk = how uncertain it is x how fatal it is if wrong.** Validate the single riskiest first; a passing test on a safe assumption is wasted motion. For a brand-new idea the riskiest is almost always desirability, so start there unless evidence says otherwise. State which assumption you are testing and why it ranked highest before designing anything.

### 2. Design the cheapest falsifiable test

Write the assumption as an **XYZ hypothesis**: "At least X% of Y will do Z," where Z is an observable action, not a feeling. Set the success threshold (the X) and the sample size *now*, before you run, so the result cannot be rationalized after the fact. A test you cannot fail is not a test.

Pick the lightest method that produces behavioral signal for that assumption:

| Method | Tests | Signal measured | Use when |
|---|---|---|---|
| Customer interviews (Mom Test) | Desirability: does the pain exist | What they already do and spend about it | The problem itself is unproven |
| Landing / smoke-test page | Desirability + demand | Sign-ups, clicks-to-buy on a real CTA | The problem is real but appeal is unproven |
| Concierge / Wizard-of-Oz | Desirability + viability | They accept and value a manually delivered solution | You can deliver by hand to a few people |
| Pre-order / letter of intent / deposit | Viability | Money or a signed commitment up front | Willingness to pay is the open question |
| Fake-door / feature stub | Desirability of a specific feature | Click-through on a not-yet-built option | Prioritizing among features |

Bias toward the methods that cost money or reputation to say yes to (pre-orders, deposits, concierge), because **skin-in-the-game is the only reliable demand signal**; a free "yes" predicts nothing. Collect your own data from this experiment rather than leaning on market reports or analogies; the market for someone else's idea does not care about yours.

For the full catalog with metric and threshold guidance, and the good-vs-bad interview question bank, read `references/experiment-library.md`.

### 3. Run the test

For demand tests (landing page, pre-order, concierge): drive real traffic or real prospects, never friends-and-family, and record the action, not the reaction.

For interviews, follow the Mom Test rules; an interview that breaks them produces confident false positives, the worst outcome of all:

- **Talk about their life, not your idea.** Do not reveal what you are building until the end, if ever. The moment you pitch, they switch from truth to politeness.
- **Ask about specific past events, not hypotheticals.** "Tell me about the last time you hit this problem, what did you do?" not "Would you use a tool that...". Behavior already happened and cannot be wished into existence.
- **Talk less; aim for them speaking 80% of the time.** Let silences do the work.
- **Deflect compliments and dig past them.** "Great idea" is not data; respond "thanks, but what are you doing about this today?" and get back to facts.
- **End with a real ask for commitment.** Time (a trial), reputation (an intro), or money (a deposit). A pleasant chat with no commitment is a zombie lead, not validation. A clean "no" is more useful than a warm "maybe."

Anchor pricing questions to existing spend ("what do you pay for this now?"), never to a hypothetical ("would you pay $X?").

### 4. Synthesize into a verdict

Separate facts (what they did and said they did) from interpretations (what you think it means); report the facts first. Count signal across the sample: a pain mentioned unprompted by most participants is real; one mentioned by one person is noise. Compare the measured result against the threshold you fixed in step 2, then return one verdict:

| Verdict | Trigger | Next step |
|---|---|---|
| Go | Met the pre-set threshold with behavioral evidence | Proceed to `write-product-spec` / MVP; carry the evidence in |
| Pivot | The pain is real but the assumed segment, problem framing, or solution is wrong | Re-rank assumptions and re-test the new riskiest one |
| Kill | No demand: no existing workaround, no spend, no commitment | Stop; name the disconfirming evidence plainly |

Name the evidence behind the verdict. A verdict the data does not support is the failure this skill exists to prevent.

## Red and green flags

These let you read a result fast. Multiple red flags on a desirability test is a Kill or Pivot regardless of enthusiasm.

- **Green:** people already pay for an inferior workaround; they ask when they can have it or hand over money/time; they describe the pain in concrete recent detail unprompted; it is the user's own pain.
- **Red:** no existing workaround (the problem is not painful enough to act on); the only validation is "friends think it's cool"; you have to convince people they have the problem; every "yes" is hypothetical and free.

## Gotchas

- **The agent cannot run the test; it designs and synthesizes.** Interviews, traffic, and pre-orders happen in the real world over days. Produce the plan, the script, and the threshold; then process the results the user brings back. Do not fabricate or assume outcomes.
- **A threshold set after seeing results is not a threshold.** The pass/fail line must be committed in step 2. Moving it to match the data is the most common way a doomed idea survives validation.
- **Compliments and "I would" feel like progress and are not.** Enthusiasm with no behavioral evidence or commitment is a red flag, not a green one; weight it at zero.
- **Validation precedes the spec; it does not replace it.** A Go verdict feeds `write-product-spec`; it does not substitute for defining what gets built. Hand off, do not absorb its job.
- **This is not market research.** `research-market` answers "is the market big and reachable" from secondary sources. This answers "will these specific people actually act" from primary evidence. Run validation even when the market looks large on paper; a big market for an unwanted product is still zero.

## Example

Idea: a subscription app that auto-categorizes freelancers' business expenses for tax time.

1. **Riskiest assumption (desirability):** freelancers find expense categorization painful enough to pay to remove it. Feasibility (OCR, bank APIs) is well-trodden, so defer it.
2. **Hypothesis:** "At least 30% of freelancers I talk to who currently track expenses will, when asked, show me a real recent mess and agree to a paid 15-minute concierge run." Sample: 12 freelancers. Method: Mom Test interviews escalating to a concierge offer (skin-in-the-game).
3. **Run:** recruit from a freelancer Slack, not friends. Open with "walk me through how you handled expenses last tax season, what was the worst part?" Never mention the app until the end. Close with the concierge ask.
4. **Synthesize:** 9 of 12 described a specific recent scramble unprompted (real pain); but only 1 accepted the paid concierge, and 7 said "I just dump it on my accountant in March." Verdict: **Pivot.** The pain is real but the buyer is the accountant, not the freelancer; re-rank assumptions around an accountant-facing tool and re-test.
