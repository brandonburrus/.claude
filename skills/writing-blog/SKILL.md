---
name: writing-blog
description: Use this skill when drafting, editing, or writing blog posts for blog.brandonburrus.com.
  Do not use for Confluence docs, READMEs, internal technical writing, or any writing
  not destined for the blog.
---

## Purpose

Guide the agent to write blog posts that match Brandon's established voice, structure, and quality bar as demonstrated across his published posts at blog.brandonburrus.com. The output is a complete `.mdx` file ready to drop into `src/content/posts/`.

## Workflow

### 1. Understand the topic

Before writing, identify:

- The **target audience** — primarily developers early-to-mid career, curious and motivated but not experts yet
- The **post category** — one of: tutorial/guide, concept explainer, tooling or productivity, opinion/lessons learned, or reference list
- Any **code examples** that will be needed and what language or tool they target
- Whether the post should reference any existing posts or external resources

If the topic brief is vague, ask for the audience, the core takeaway, and one concrete example the post should include before proceeding.

### 2. Draft the frontmatter

Generate YAML frontmatter before writing the body. Required fields:

```yaml
---
title: "Post Title"
description: "One sentence. Describes what the post covers, not why someone should read it."
publishedAt: YYYY-MM-DD
tags: ["tag-one", "tag-two"]
---
```

**Title rules:**
- Descriptive and specific, not clickbait
- Often includes a number, a colon, or a clear noun phrase
- Examples from the corpus: "Bash for Beginners: Becoming a Terminal Ninja", "4 JavaScript Libraries to Learn in 2021", "What is 'Abstraction' in Programming?"
- Avoid: "The Ultimate Guide to X", "Why You Should Learn X", "X Will Change Your Life"

**Description rules:**
- One sentence, under 160 characters
- Describes the actual content, not the value proposition
- Examples: "A practical introduction to Bash covering navigation, file management, paths, arguments, and where to find help." — not "Learn everything you need to know about Bash!"

**Tag rules:**
- Lowercase, hyphenated (`software-engineering` not `SoftwareEngineering`)
- Topic-focused, 2–4 per post
- Use consistent tags across related posts (e.g., `vscode`, `productivity`, `fundamentals`, `javascript`)

**Filename slug** (for the user to use when saving the file):
- Derived from the title, lowercase, hyphenated, no special characters
- Matches the URL path the post will be served at

### 3. Write the opening

The opening is 1–2 paragraphs. It must:

- Frame **why this topic matters** before touching the substance
- Use relatable context — a common frustration, a moment of realization, or a situation the reader has been in
- Not open with a dictionary definition or "In this post, I will..."
- Not summarize the entire post

When the post is a structured list or tutorial, a short overview of what will be covered is acceptable after the contextual hook — but the hook comes first.

**Examples of strong openers from the corpus:**
- "Using the terminal for the first time can be really intimidating. We're creatures of habit, used to graphical interfaces that guide us through every action." *(bash-for-beginners)*
- "As a developer, I'm always looking for ways to make things more efficient. But it wasn't until I was introduced to Vim that I started thinking about not just writing efficient code, but *efficiently writing* efficient code." *(visual-studio-code-and-vim)*
- "Do you know what the top errors are in a JavaScript codebase?" *(optional-chaining-nullish-coalescing — opens with a question that immediately sets up the problem)*

### 4. Write the body

Use H2 (`##`) as the primary section heading level. H3 (`###`) for subsections within a section. Never skip levels.

**For each post category, follow the appropriate structure:**

**Tutorial / guide:**
Numbered steps or logically ordered H2 sections. Each section covers one discrete action. Include a quick-reference table or summary at the end when the post covers multiple commands, shortcuts, or items.

**Concept explainer:**
Start concrete ("here's a thing you already know"), build up to the abstraction, then show why the abstraction is useful. Analogies are welcome but should be brief. End with a practical takeaway — how does understanding this concept change what the reader writes or how they think?

**Tooling / productivity:**
Categorize items into logical groups. Each item gets a bold name followed by a one-to-three sentence description. Longer descriptions are reserved for less obvious tools. Always close with what the combined toolset accomplishes together.

**Opinion / lessons learned:**
Numbered takeaways work well. Each lesson gets a heading and 2–4 paragraphs. Open each lesson with the principle stated plainly, then support it with reasoning and personal experience. Avoid vague advice — every lesson should be actionable or give the reader a concrete way to think about something differently.

**Reference list:**
Similar to tooling, but often includes code snippets. Group by category. Include a brief intro sentence before each category explaining why those items belong together.

**Code examples:**
- Build complexity incrementally — simple example first, realistic example second
- One concept per block; do not combine unrelated ideas into one snippet
- Use the language appropriate to the topic; do not switch languages mid-post without explanation
- Comments in code blocks should be minimal — only when the code cannot speak for itself
- Inline code (backtick) for any command, function name, key shortcut, or value mentioned in prose

**Prose formatting:**
- Bold (`**`) only for key terms on first introduction and for strong emphasis on a specific word or phrase within a sentence — not for whole sentences or section summaries
- Italics (`*`) for emphasis within a sentence, or for titles of external resources
- Blockquotes for external quotes only — not for callouts or warnings (use a `> **Note:**` pattern for important caveats, as seen in the corpus)
- Tables for comparisons, shortcut references, or command references
- Horizontal rules (`---`) to separate major thematic breaks, not between every section

### 5. Write the closing

1–3 paragraphs. The closing must:

- Tie back to the broader principle behind the post, not just recap what was covered
- Be forward-looking — what should the reader do next, or what does mastering this unlock?
- End on a grounded, encouraging note — honest about effort required, clear about the payoff
- Not include a hard call to action ("subscribe", "share this post", "follow me")

Link to external resources (official docs, further reading) at the end of the closing or inline where they are first referenced — not in a separate "Resources" section unless the post is a reference list.

---

## Tone and Voice

These rules apply throughout the entire post.

**Person and address:**
- Second person ("you", "your") throughout — speak directly to the reader
- First person ("I") is appropriate in opinion and lessons posts, and sparingly in others when sharing a personal experience that illustrates the point
- "We" is not appropriate — this is a personal blog, not a team publication

**Register:**
- Conversational but not casual — contractions are used freely ("you'll", "it's", "don't", "that's")
- Peer-to-peer, not authority-to-student — assume the reader is capable, not that they need hand-holding
- Direct declarative sentences preferred over hedged constructions ("This approach solves X" not "This approach can potentially help you to solve X")

**What to avoid:**
- Exclamation points (rare exceptions only)
- Emojis (never)
- Em dashes (never — rewrite the sentence instead)
- Hype and inflated language (see AI vocabulary watch list in the AI Pattern Detection section below)
- Filler openers ("In this article, we will...", "Today I'm going to show you...")
- Signposting phrases ("Let's dive in", "Let's explore", "Here's what you need to know", "Without further ado")
- Persuasive framing ("The real question is", "At its core", "What really matters", "Fundamentally")
- Chatbot artifacts ("I hope this helps", "Great question", "Let me know if you'd like me to expand on any section")
- Repeating what a heading already said in the first sentence of the section
- Vague closings that say nothing ("I hope you found this helpful")

**What to include:**
- Honest acknowledgment of difficulty, tradeoffs, or limitations when they exist
- Specific examples — concrete over abstract whenever possible
- Links to primary sources (official docs, proposals, relevant prior art) where they add value

**Rhythm and voice:**
- Vary sentence length deliberately. Short declarative statements, then longer explanatory ones. Uniform sentence length produces flat prose.
- Vary paragraph length too. A one-sentence paragraph works for emphasis. A five-sentence paragraph works for explanation. Uniformly-sized paragraphs feel generated.
- Have opinions and state them directly. Brandon's posts take positions: "Concepts are more important to master than writing code is." Don't hedge into neutral territory.
- Acknowledge difficulty honestly. "Learning to write code is hard, time-consuming, and mentally exhausting" is more credible than a generic list of challenges.
- Avoid the clean-contrast trap. Not every paragraph needs a tidy thesis-antithesis structure. Sometimes the answer is messy or uncertain — saying so is more human than resolving it artificially.
- Be specific about experiences. "I spent days reading documentation, only for it to click the moment I actually wrote the code" beats "practice is important."

---

## AI Pattern Detection

These patterns are the most common signs of AI-generated prose. Check for them throughout drafting and revision.

### AI vocabulary watch list

The words and phrases below are strongly associated with AI output. They're not always wrong — "key" in a database context or "enhance" describing a specific API improvement are fine. The test: would a person say this in conversation, or does it only appear because you've read it in AI output a thousand times?

> additionally, align with, at its core, boasts, breathtaking, catalyst, commitment to, comprehensive, crucial, cultivating, cutting-edge, deeply rooted, delve, elevate, emphasizing, encompassing, enduring, enhance, evolving landscape, exemplifies, explore (as a call to action), focal point, fostering, fundamentally, furthermore, garner, groundbreaking, harness, highlight (as a verb), holistic, indelible mark, innovative, interplay, intricate / intricacies, it's worth noting, key (as a hollow intensifier), landscape (abstract), lasting, leverage, moreover, multifaceted, navigate (abstract), nestled, notably, nuanced (when meaning nothing specific), paramount, pivotal, plethora, profound, realm, renowned, reshaping, robust, seamless, serves as / stands as / functions as / marks / represents (replacing "is"), setting the stage, showcase, streamline, stunning, supercharge, tapestry (abstract), testament, transformative, underscore (as a verb), unique (when meaning "notable"), unlocking, valuable, vibrant, vital

### Structural patterns to avoid

1. **Rule-of-three forcing** — Don't pack ideas into groups of three for rhetorical effect. If there are two things, say two. If there are four, say four.
2. **Superficial -ing phrases** — Don't tack participial phrases onto sentences for fake depth ("highlighting the importance of...", "showcasing how..."). If the point matters, give it its own sentence.
3. **Synonym cycling** — If you mean the same thing, use the same word. Don't rotate through synonyms to avoid repetition ("the tool / the solution / the platform / the system").
4. **Negative parallelisms** — Avoid "It's not just X; it's Y" and "Not only X, but Y." State what it *is* directly.
5. **Filler phrases** — Cut wordy constructions to their core:

   | Instead of                   | Write                            |
   | ---------------------------- | -------------------------------- |
   | In order to                  | To                               |
   | Due to the fact that         | Because                          |
   | At this point in time        | Now                              |
   | In the event that            | If                               |
   | Has the ability to           | Can                              |
   | It is important to note that | *(delete — just state the thing)* |
   | Prior to                     | Before                           |
   | A wide variety of            | Many / various                   |

6. **Excessive hedging** — Don't stack qualifiers. "The policy may affect outcomes" not "It could potentially possibly be argued that the policy might have some effect."
7. **Persuasive authority tropes** — Don't use "The real question is", "At its core", "What really matters", "Fundamentally", "The heart of the matter." These pretend to cut through noise but just add ceremony to an ordinary point.
8. **Signposting and announcements** — Don't narrate what you're about to do. No "Let's dive in", "Let's explore", "Let's break this down", "Here's what you need to know", "Without further ado." Just start.
9. **Copula avoidance** — Prefer "is", "are", "has" over "serves as", "stands as", "functions as", "boasts", "features", "offers" when a simple copula is accurate.
10. **Passive voice** — Use active voice when the actor is known. "The compiler catches the error" not "The error is caught."

---

## Technical Writing Standards

**Code blocks:**
- Always include a language identifier (` ```js `, ` ```sh `, ` ```ts `, ` ```yaml `, etc.)
- Shell commands use `sh` or `bash`
- Use `diff` syntax for before/after code changes

**Links:**
- Use descriptive link text — not "click here" or bare URLs in prose
- External links go inline on first reference
- Official documentation links are preferred over third-party tutorials for reference material

**Tables:**
- Use for shortcut references, command summaries, comparison matrices, and side-by-side option analysis
- Always include a header row
- Keep cell content concise — one concept per cell

**Blockquotes:**
- Use for direct external quotes only
- Attribute quotes with "— Source" on the same line

**Notes and caveats:**
- Use `> **Note:**` blockquote pattern for important warnings, deprecation notices, or platform-specific caveats
- Place notes at the point in the post where they are relevant, not in a separate section

---

## Quality Checklist

Before considering a post complete, verify:

- [ ] Frontmatter is complete: `title`, `description`, `publishedAt`, `tags` all present and formatted correctly
- [ ] Title is descriptive and specific — not clickbait, not vague
- [ ] Description is one sentence, under 160 characters, describes content not value
- [ ] Tags are lowercase and hyphenated
- [ ] Opening frames the topic with context before diving into substance
- [ ] No section opens by repeating its heading
- [ ] Code examples build from simple to realistic; each block has a language identifier
- [ ] Bold is used sparingly — not on whole sentences or section summaries
- [ ] No emojis, no exclamation points used for enthusiasm
- [ ] No em dashes anywhere in the post
- [ ] Closing ties back to the broader principle and looks forward
- [ ] No hard call to action in the closing
- [ ] External links use descriptive anchor text
- [ ] No AI vocabulary watch-list words used without justification
- [ ] No rule-of-three forcing, synonym cycling, or -ing phrase tacking
- [ ] No filler phrases, hedging stacks, or persuasive authority tropes
- [ ] Sentence and paragraph length vary naturally — no uniform rhythm
- [ ] Self-audit: reread the draft and ask "What would make someone suspect this was AI-generated?" Fix any remaining tells.
- [ ] Post reads naturally aloud — if a sentence sounds awkward spoken, rewrite it

---

## When to Use

- Drafting a new blog post from a topic brief or idea
- Editing or revising an existing draft
- Writing any content destined for the blog as a `.mdx` file
- When the user says "write a blog post", "draft a post", or "help me write about X for my blog"

## When NOT to Use This Skill

- Confluence spike documents, how-to guides, or team documentation — those follow a different structure and voice (problem/solution/phases, more formal, team-oriented "we")
- README files or inline code documentation
- Technical proposal documents or architecture decision records
- Any writing that is not destined for `src/content/posts/` on this blog

