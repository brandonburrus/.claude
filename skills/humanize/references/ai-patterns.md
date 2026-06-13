# AI writing pattern catalog

Check the text against every pattern below. Grounded in Wikipedia's "Signs of AI writing" (WikiProject AI Cleanup), observed across thousands of instances of AI-generated text. Remember the cluster rule from SKILL.md: isolated hits are weak evidence, co-occurring hits are strong.

## Contents

- Content patterns (1-6)
- Language and grammar patterns (7-13)
- Style patterns (14-19)
- Communication patterns (20-22)
- Filler, hedging, and framing (23-30)
- Vocabulary and false agency (31-32)

## Content patterns

### 1. Inflated significance and legacy

Watch for: stands as, serves as, is a testament, vital/pivotal/crucial/key role or moment, underscores its importance, reflects broader, symbolizing its enduring, setting the stage for, marking a shift, key turning point, evolving landscape, indelible mark, deeply rooted.

The model puffs up importance by claiming arbitrary facts represent or contribute to broader trends. Fix: state the fact and what it concretely did.

> Before: The Statistical Institute of Catalonia was officially established in 1989, marking a pivotal moment in the evolution of regional statistics in Spain.
> After: The Statistical Institute of Catalonia was established in 1989 to collect and publish regional statistics independently from Spain's national statistics office.

### 2. Notability name-dropping

Watch for: independent coverage, national media outlets, written by a leading expert, active social media presence, lists of publications with no content.

Fix: replace the list of venues with one concrete, contentful citation.

> Before: Her views have been cited in The New York Times, BBC, Financial Times, and The Hindu.
> After: In a 2024 New York Times interview, she argued that AI regulation should focus on outcomes rather than methods.

### 3. Superficial -ing analyses

Watch for: trailing present-participle phrases: highlighting..., ensuring..., reflecting..., symbolizing..., fostering..., showcasing..., encompassing...

Tacked-on -ing phrases add fake depth. Fix: cut the phrase, or convert it to a separate sentence with a real source or actor.

> Before: The color palette resonates with the region's natural beauty, symbolizing Texas bluebonnets, reflecting the community's deep connection to the land.
> After: The temple uses blue, green, and gold. The architect said these reference local bluebonnets and the Gulf coast.

### 4. Promotional language

Watch for: boasts, vibrant, rich (figurative), profound, showcasing, exemplifies, commitment to, natural beauty, nestled, in the heart of, groundbreaking (figurative), renowned, breathtaking, must-visit, stunning.

> Before: Nestled within the breathtaking region of Gonder, Alamata Raya Kobo stands as a vibrant town with a rich cultural heritage.
> After: Alamata Raya Kobo is a town in the Gonder region of Ethiopia, known for its weekly market and 18th-century church.

### 5. Vague attributions and weasel words

Watch for: industry reports, observers have cited, experts argue, some critics argue, several publications.

Opinions get attributed to vague authorities. Fix: name the source, or drop the claim.

> Before: Experts believe it plays a crucial role in the regional ecosystem.
> After: The Haolai River supports several endemic fish species, according to a 2019 survey by the Chinese Academy of Sciences.

### 6. Formulaic "challenges and future prospects" sections

Watch for: Despite its X, it faces several challenges..., Despite these challenges..., Challenges and Legacy, Future Outlook.

Fix: replace the formula with specific events, causes, and responses.

> Before: Despite its industrial prosperity, Korattur faces challenges typical of urban areas. Despite these challenges, Korattur continues to thrive.
> After: Traffic congestion increased after 2015 when three new IT parks opened. The municipal corporation began a stormwater drainage project in 2022.

## Language and grammar patterns

### 7. AI vocabulary words

High-frequency tells, especially when co-occurring: actually, additionally, align with, crucial, delve, emphasizing, enduring, enhance, fostering, garner, highlight (verb), interplay, intricate, intricacies, key (adjective), landscape (abstract), pivotal, showcase, tapestry (abstract), testament, underscore (verb), valuable, vibrant.

These words exploded in frequency in post-2023 text. Replace with plain alternatives; do not flatten all formal vocabulary, only these.

### 8. Copula avoidance

Watch for: serves as, stands as, marks, represents, boasts, features, offers, where "is", "are", or "has" would do.

> Before: Gallery 825 serves as LAAA's exhibition space and boasts over 3,000 square feet.
> After: Gallery 825 is LAAA's exhibition space. It has four rooms totaling 3,000 square feet.

### 9. Negative parallelisms and tailing negations

Watch for: not only... but..., it's not just about X, it's Y, and clipped tailing fragments like "no guessing" or "no wasted motion" tacked onto sentence ends.

> Before: It's not just about the beat riding under the vocals; it's part of the aggression. It's not merely a song, it's a statement.
> After: The heavy beat adds to the aggressive tone.

> Before: The options come from the selected item, no guessing.
> After: The options come from the selected item without forcing the user to guess.

### 10. Rule of three overuse

Models force ideas into triplets to appear comprehensive ("innovation, inspiration, and industry insights"). Fix: break the triplet; use one item, two, or four, whatever the facts support.

> Before: The event features keynote sessions, panel discussions, and networking opportunities.
> After: The event includes talks and panels. There's also time for informal networking between sessions.

### 11. Elegant variation (synonym cycling)

Repetition penalties make models cycle synonyms: the protagonist, the main character, the central figure, the hero, all in one paragraph. Humans repeat the same word; do that instead.

### 12. False ranges

"From X to Y" where X and Y are not on a meaningful scale.

> Before: From the singularity of the Big Bang to the enigmatic dance of dark matter.
> After: The book covers the Big Bang, star formation, and current theories about dark matter.

### 13. Passive voice and subjectless fragments

Watch for: hidden actors and dropped subjects: "No configuration file needed", "The results are preserved automatically".

> Before: No configuration file needed. The results are preserved automatically.
> After: You do not need a configuration file. The system preserves the results automatically.

## Style patterns

### 14. Em dashes and en dashes

The most reliable single tell. The final rewrite contains none, including spaced dashes and double hyphens used the same way. Replace, in rough preference order: period (new sentence), comma (tight aside), colon (introducing an explanation), parentheses (true aside), or restructure.

> Before: The new policy — announced without warning — affects thousands of workers.
> After: The new policy, announced without warning, affects thousands of workers.

### 15. Mechanical boldface

Bolding every key term mid-prose. Fix: unbold; if a term deserves emphasis, the sentence structure should provide it.

### 16. Inline-header vertical lists

Bullets shaped "**Header:** sentence restating the header". Fix: merge into prose, or use a plain list without the bolded label.

> Before: **Performance:** Performance has been enhanced through optimized algorithms.
> After: The update speeds up load times through optimized algorithms.

### 17. Title Case in headings

Capitalize the first word and proper nouns only; AI title-cases every main word.

### 18. Emojis

Decorating headings or bullets with emojis is a tell, and this library bans them everywhere regardless.

### 19. Curly quotation marks

Replace curly quotes with straight ones. Weak evidence alone (most editors auto-curl); strong alongside other tells.

## Communication patterns

### 20. Chatbot correspondence artifacts

Watch for: I hope this helps, Of course!, Certainly!, You're absolutely right, Would you like, let me know, here is a...

Chat framing pasted as content. Cut entirely; the content starts at the first substantive sentence.

### 21. Knowledge-cutoff disclaimers and speculative gap-filling

Watch for: as of [date], up to my last training update, while specific details are limited, based on available information, maintains a low profile, keeps personal details private, likely grew up, it is believed that.

Two tells: hard cutoff disclaimers, and inventing plausible filler to paper over a missing source. Say what is not known, or cut the sentence; never dress a guess as fact.

> Before: Information about her early life is not publicly available, suggesting she maintains a low profile. She likely grew up in a middle-class household.
> After: Her early life is not documented in the available sources.

### 22. Sycophantic tone

Watch for: Great question!, You're absolutely right that, That's an excellent point.

Cut the flattery; keep whatever substantive content follows it.

## Filler, hedging, and framing

### 23. Filler phrases

- "In order to achieve this goal" becomes "To achieve this"
- "Due to the fact that it was raining" becomes "Because it was raining"
- "At this point in time" becomes "Now"
- "In the event that you need help" becomes "If you need help"
- "The system has the ability to process" becomes "The system can process"
- "It is important to note that the data shows" becomes "The data shows"

### 24. Excessive hedging

Stacked qualifiers: "It could potentially possibly be argued that the policy might have some effect." Fix: one qualifier maximum: "The policy may affect outcomes."

### 25. Generic positive conclusions

Watch for: the future looks bright, exciting times lie ahead, journey toward excellence, a major step in the right direction.

Fix: end on a concrete fact or plan, or just end.

> Before: The future looks bright for the company as they continue their journey toward excellence.
> After: The company plans to open two more locations next year.

### 26. Uniform hyphenation of word pairs

Watch for: third-party, cross-functional, data-driven, high-quality, real-time, long-term, end-to-end hyphenated everywhere.

Humans hyphenate attributively and drop the hyphen in predicate position. Keep "a high-quality report"; write "the report is high quality".

### 27. Persuasive authority tropes

Watch for: the real question is, at its core, in reality, what really matters, fundamentally, the deeper issue, the heart of the matter.

These announce depth and then restate an ordinary point with ceremony. Cut the frame; keep the point.

### 28. Signposting and announcements

Watch for: let's dive in, let's explore, let's break this down, here's what you need to know, without further ado.

Announcing what the text is about to do instead of doing it. Cut; start with the content.

> Before: Let's dive into how caching works in Next.js. Here's what you need to know.
> After: Next.js caches data at multiple layers, including request memoization, the data cache, and the router cache.

### 29. Heading warm-up sentences

A heading followed by a one-liner restating the heading before the real content. Cut the warm-up; the first sentence after a heading carries information.

### 30. Diff-anchored writing

Documentation or comments narrating a change ("This function was added to replace the previous approach") instead of describing the thing as it is. Outside changelogs, release notes, and migration guides, text should read coherently without knowing what changed last commit.

> Before: This function was added to replace the previous approach of iterating through all items.
> After: This function uses a hash map for O(1) lookups, avoiding the O(n squared) cost of naive iteration.

## Vocabulary and false agency

### 31. Business jargon verbs

Watch for the consultant register standing in for a plain verb. Replace with the plain word; the jargon adds register, not meaning.

| Avoid | Use instead |
|---|---|
| navigate (a challenge) | handle, address |
| unpack (an analysis) | explain, examine |
| lean into | accept, commit to |
| deep dive | analysis, examination |
| double down | commit, increase |
| circle back | return to, revisit |
| moving forward | next, from now on |
| take a step back | reconsider |
| on the same page | aligned, agreed |
| game-changer | significant, important |

> Before: Moving forward, we need to lean into the discomfort and navigate these challenges as a team.
> After: Next, the team needs to accept the discomfort and handle the funding shortfall.

### 32. False agency verbs

Watch for inanimate things performing human actions: the decision emerges, the data tells us, the market rewards, the culture shifts, a complaint becomes a fix, the conversation moves toward.

This is distinct from copula avoidance (pattern 8, where the verb dresses up a plain "is") and passive voice (pattern 13, where the actor is hidden): here an abstraction is handed a verb only a person can do, which lets the sentence skip naming who acted. Fix: name the human; if no specific person fits, use "you" to put the reader in the seat.

> Before: Over time the decision emerges, and the data tells us the market rewards speed.
> After: After a week the team decided, having read in the usage logs that buyers paid more for the faster tier.
