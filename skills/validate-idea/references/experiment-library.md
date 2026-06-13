# Experiment Library and Interview Question Bank

Read when designing a validation test (workflow step 2) or writing an interview script (step 3). Pick the method that matches the riskiest assumption, set its metric and threshold before running, and measure the action, not the opinion.

## Contents

- [Choosing the method](#choosing-the-method)
- [The experiment catalog](#the-experiment-catalog)
- [Setting a defensible threshold](#setting-a-defensible-threshold)
- [Interview question bank](#interview-question-bank)
- [Deflecting the three kinds of bad data](#deflecting-the-three-kinds-of-bad-data)
- [Commitment currencies](#commitment-currencies)

## Choosing the method

Match the method to what is actually uncertain. Running an expensive test on a question a cheap one answers is the common waste.

- The problem itself is unproven, you do not yet know if the pain exists: start with **interviews**. They are the only method that surfaces a problem you have not already framed.
- The problem is real but you do not know if your framing of the solution appeals: **smoke-test landing page** or **fake-door**.
- You can deliver the value by hand to a handful of people: **concierge / Wizard-of-Oz**, the highest-signal early test because people experience real value and you watch real behavior.
- The open question is willingness to pay, not interest: **pre-order, deposit, or letter of intent**. Nothing else tests viability honestly.

Escalate within one study: interviews that surface real pain should end in a concierge or pre-order ask, so the same conversation tests desirability and then willingness to commit.

## The experiment catalog

| Method | Tests | Metric | Rough pass bar | Cost / effort |
|---|---|---|---|---|
| Customer interviews (Mom Test) | Problem exists and matters | Share who describe the pain unprompted with a recent concrete instance | Majority of a 10-15 sample | Low; days |
| Smoke-test landing page | Interest and message-market fit | Click-through on a real "buy / sign up" CTA (not "learn more") | Context-dependent; set vs a known baseline | Low-medium |
| Fake-door / feature stub | Demand for a specific feature | Click-through on the not-yet-built option, then an honest "coming soon" | Set vs sibling features | Low |
| Explainer video | Comprehension + appeal of a complex idea | Watch-through and sign-up after | Set before running | Medium |
| Concierge / Wizard-of-Oz | Real value delivery + viability | Acceptance, repeat use, willingness to pay for the manual service | A few paying or returning | Medium; manual labor |
| Pre-order / deposit / LOI | Willingness to pay | Money or signed commitment up front | Any real commitment beats any number of "yes" | Medium |
| Concierge-to-paid conversion | Viability of the model | Share of hand-served users who pay to continue | Set before running | Medium |

Two principles govern all of them:

- **Skin-in-the-game.** Weight signals by what the yes costs the person: money > reputation (a public intro, a testimonial) > time (a trial) > a free verbal yes (worthless). A free "yes" predicts nothing because saying no felt rude.
- **YODA (Your Own Data beats Others' Data).** Run your own small experiment rather than reasoning from market reports, competitor traction, or analogies. The market for someone else's idea does not care about yours.

## Setting a defensible threshold

Commit these three numbers before running, in writing, so the result cannot be reinterpreted to fit hope:

1. **The XYZ hypothesis:** "At least X% of Y will do Z," where Z is an observable action.
2. **The sample or traffic size** that makes the result meaningful (a 30% pass on 3 people is noise).
3. **The decision rule:** what result is a Go, what is a Pivot, what is a Kill.

If you cannot state a result that would make you abandon the idea, you are not running an experiment, you are seeking reassurance.

## Interview question bank

Good questions anchor to specific past behavior. Bad questions ask for predictions, hypotheticals, or approval, all of which default to a meaningless yes.

| Bad (predicts nothing) | Good (anchors to behavior) |
|---|---|
| "Do you think this is a good idea?" | "Tell me about the last time you ran into this." |
| "Would you use a tool that does X?" | "How are you handling that today?" |
| "Would you pay $X for this?" | "What are you currently paying or spending time on to solve it?" |
| "Would you want feature Y?" | "Walk me through what you did the last time you needed that." |
| "How often do you think you'd use it?" | "How many times did this come up in the last month?" |

Reliable probes:
- "Tell me about the last time you..." then "What happened next?"
- "What's the hardest part about [the task]?" then "Why was that hard?"
- "What have you already tried, and why did you stop?"
- "Where does the budget for solutions like this come from?"
- "Who else deals with this? How do they handle it?"

Ask the scary question, the one whose answer could destroy the idea. Safe questions confirm what you already believe and teach nothing. A question that gets a yes no matter what is not worth asking.

## Deflecting the three kinds of bad data

| Bad data | What it sounds like | Deflect with |
|---|---|---|
| Compliments | "That's a great idea! You're onto something." | "Thanks, but to not waste your time, what does your current process actually look like?" |
| Fluff (generics, hypotheticals, futures) | "I always...", "I would never...", "I'd definitely buy that." | "When did that last happen? Walk me through that specific time." |
| Ideas (feature requests) | "You should add Z." | "Interesting, what would Z let you do that you can't today? Tell me about the last time you needed it." |

A conversation you walk away from feeling great about but with no concrete facts or commitment was a pitch, not a test.

## Commitment currencies

End every promising conversation with an ask calibrated to test real interest. Know the ask before the meeting.

- **Time:** "Would you try a prototype for 15 minutes next week?"
- **Reputation:** "Who else should I talk to about this?" / "Could you introduce me to whoever owns the budget?"
- **Money:** "We launch in 8 weeks, want the first cohort at 40% off?" / a deposit / a letter of intent.

If they will not give you their time, they will never give you their money. A clear "no" is data you can act on; a "maybe" is a zombie lead that wastes weeks.
