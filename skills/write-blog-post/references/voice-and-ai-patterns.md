Brandon's blog voice and the full AI-writing-pattern checklist. Read before drafting and again during revision; this is the load-bearing quality bar for the post. The SKILL.md workflow covers structure; this file covers voice and the patterns to strip.

## Contents

- [Tone and Voice](#tone-and-voice)
- [AI Pattern Detection](#ai-pattern-detection)

## Tone and Voice

These rules apply throughout the entire post.

**Person and address:**
- Second person ("you", "your") throughout: speak directly to the reader
- First person ("I") is appropriate in opinion and lessons posts, and sparingly in others when sharing a personal experience that illustrates the point
- "We" is not appropriate: this is a personal blog, not a team publication

**Register:**
- Conversational but not casual; contractions are used freely ("you'll", "it's", "don't", "that's")
- Peer-to-peer, not authority-to-student; assume the reader is capable, not that they need hand-holding
- Direct declarative sentences preferred over hedged constructions ("This approach solves X" not "This approach can potentially help you to solve X")

**What to avoid:**
- Exclamation points (rare exceptions only)
- Emojis (never)
- Em dashes (never: rewrite the sentence instead)
- Hype and inflated language (see AI vocabulary watch list in the AI Pattern Detection section below)
- Filler openers ("In this article, we will...", "Today I'm going to show you...")
- Signposting phrases ("Let's dive in", "Let's explore", "Here's what you need to know", "Without further ado")
- Persuasive framing ("The real question is", "At its core", "What really matters", "Fundamentally")
- Chatbot artifacts ("I hope this helps", "Great question", "Let me know if you'd like me to expand on any section")
- Repeating what a heading already said in the first sentence of the section
- Vague closings that say nothing ("I hope you found this helpful")

**What to include:**
- Honest acknowledgment of difficulty, tradeoffs, or limitations when they exist
- Specific examples: concrete over abstract whenever possible
- Links to primary sources (official docs, proposals, relevant prior art) where they add value

**Rhythm and voice:**
- Vary sentence length deliberately. Short declarative statements, then longer explanatory ones. Uniform sentence length produces flat prose.
- Vary paragraph length too. A one-sentence paragraph works for emphasis. A five-sentence paragraph works for explanation. Uniformly-sized paragraphs feel generated.
- Have opinions and state them directly. Brandon's posts take positions: "Concepts are more important to master than writing code is." Don't hedge into neutral territory.
- Acknowledge difficulty honestly. "Learning to write code is hard, time-consuming, and mentally exhausting" is more credible than a generic list of challenges.
- Avoid the clean-contrast trap. Not every paragraph needs a tidy thesis-antithesis structure. Sometimes the answer is messy or uncertain; saying so is more human than resolving it artificially.
- Be specific about experiences. "I spent days reading documentation, only for it to click the moment I actually wrote the code" beats "practice is important."

---

## AI Pattern Detection

These patterns are the most common signs of AI-generated prose. Check for them throughout drafting and revision.

### AI vocabulary watch list

The words and phrases below are strongly associated with AI output. They're not always wrong; "key" in a database context or "enhance" describing a specific API improvement are fine. The test: would a person say this in conversation, or does it only appear because you've read it in AI output a thousand times?

> additionally, align with, at its core, boasts, breathtaking, catalyst, commitment to, comprehensive, crucial, cultivating, cutting-edge, deeply rooted, delve, elevate, emphasizing, encompassing, enduring, enhance, evolving landscape, exemplifies, explore (as a call to action), focal point, fostering, fundamentally, furthermore, garner, groundbreaking, harness, highlight (as a verb), holistic, indelible mark, innovative, interplay, intricate / intricacies, it's worth noting, key (as a hollow intensifier), landscape (abstract), lasting, leverage, moreover, multifaceted, navigate (abstract), nestled, notably, nuanced (when meaning nothing specific), paramount, pivotal, plethora, profound, realm, renowned, reshaping, robust, seamless, serves as / stands as / functions as / marks / represents (replacing "is"), setting the stage, showcase, streamline, stunning, supercharge, tapestry (abstract), testament, transformative, underscore (as a verb), unique (when meaning "notable"), unlocking, valuable, vibrant, vital

### Structural patterns to avoid

1. **Rule-of-three forcing**: Don't pack ideas into groups of three for rhetorical effect. If there are two things, say two. If there are four, say four.
2. **Superficial -ing phrases**: Don't tack participial phrases onto sentences for fake depth ("highlighting the importance of...", "showcasing how..."). If the point matters, give it its own sentence.
3. **Synonym cycling**: If you mean the same thing, use the same word. Don't rotate through synonyms to avoid repetition ("the tool / the solution / the platform / the system").
4. **Negative parallelisms**: Avoid "It's not just X; it's Y" and "Not only X, but Y." State what it *is* directly.
5. **Filler phrases**: Cut wordy constructions to their core:

   | Instead of                   | Write                            |
   | ---------------------------- | -------------------------------- |
   | In order to                  | To                               |
   | Due to the fact that         | Because                          |
   | At this point in time        | Now                              |
   | In the event that            | If                               |
   | Has the ability to           | Can                              |
   | It is important to note that | *(delete, just state the thing)* |
   | Prior to                     | Before                           |
   | A wide variety of            | Many / various                   |

6. **Excessive hedging**: Don't stack qualifiers. "The policy may affect outcomes" not "It could potentially possibly be argued that the policy might have some effect."
7. **Persuasive authority tropes**: Don't use "The real question is", "At its core", "What really matters", "Fundamentally", "The heart of the matter." These pretend to cut through noise but just add ceremony to an ordinary point.
8. **Signposting and announcements**: Don't narrate what you're about to do. No "Let's dive in", "Let's explore", "Let's break this down", "Here's what you need to know", "Without further ado." Just start.
9. **Copula avoidance**: Prefer "is", "are", "has" over "serves as", "stands as", "functions as", "boasts", "features", "offers" when a simple copula is accurate.
10. **Passive voice**: Use active voice when the actor is known. "The compiler catches the error" not "The error is caught."
