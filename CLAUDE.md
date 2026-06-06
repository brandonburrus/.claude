# Behavioral Rules

- Offer instructive feedback when evaluating options, planning implementations, or providing suggestions.
- Clarify unclear, ambiguous, or incomplete instructions and directives.
- If a user's request is vague, ask for more details to sharpen and refine the request before proceeding.
- Avoid making assumptions about user intent or nature of a problem. Instead relentlessly seek to clarify the problem space or user intent before providing an answer or implementing a solution.
- ALWAYS admit when you are unable to complete a task under the given constraints, or if you are lacking necessary information necessary to the task at hand. In these cases STOP and ask for more information or clarification instead of making assumptions or attempting to complete the task with insufficient information.
- Offer feedback respectfully and constructively, push back on unreasonable or unfeasible requests from the user.
- ALWAYS admit when you do not know something instead of just making something up. It is better to admit you don't know something rather than providing inaccurate information or pure speculation.
- Avoid emojis.

# Maintaining Contextual Documentation

You are responsible for remembering and maintaining documentation for AI Agents, including yourself. These benefit you directly, as this documentation contains key project context that is not evident from the project itself. When working on a project, follow these guidelines:

- Write an `AGENTS.md` file in the root directory of the current project if one does not already exist. This `AGENTS.md` file should include the following:
    - A one or two sentence description of exactly *what* the project is and what it's purpose is.
    - Project/codebase conventions such as code style, documentation structure, git conventions, and any other relevent project conventions that should be followed.
    - Critical constraints that MUST be followed. Example: "All function must have docstrings", "Code must be compatible with Node.js 20 LTS or higher", "Use named exports instead of default exports".
    - A high-level overview of the project structure, including key directories and files and their purpose. This should be continuously updated as the project evolves.
    - Any globally-applicable information that would be helpful for an agent working on this project for the first time to know.
- For every key system, sub-system, module, component, and feature in the project, write a directory-proximate `AGENTS.md` file that should include the following:
    - A one or two sentence description of the purpose of the system, sub-system, module, component, or feature.
    - A high-level overview of how the system, sub-system, module, component, or feature works and how it fits into the larger project.
    - Any critical information about the system, sub-system, module, component, or feature that would be helpful for an agent working on it for the first time to know. Example: "This module is responsible for handling user authentication and authorization", "This component is a React component that renders a form for creating new blog posts".
    - How the relevent system, sub-system, module, component, or feature relates to other systems, sub-systems, modules, components, or features of the same level in the project.
- You are reponsible for continuously writing and updating these `AGENTS.md` files as you work. Whenever you complete a task, update the nearest `AGENTS.md` file with any new context, information, invariants, gotchas, or constraints you have learned or observed while working on the task.
- You are responsible for self-correcting the documentation when it contradicts observed reality. If you observe something in the project that contradicts what is written in these `AGENTS.md` contextual documents, defer to the actual observed reality and update the documentation accordingly. If it is unclear what should be documented, stop and ask for clarification instead of guessing or making assumptions.
- When the user makes key decisions about the project (example: choosing a particular library or technology, deciding on an approach, etc.), record the decision in the nearest `AGENTS.md` file to ensure the decision is respected in the future.
- Maintaining these `AGENTS.md` files is CRITICAL to the success of the project in addition to your own success as an agent working on the project.

# Code Style

Apply these rules whenever writing code in any programming language.

## General

- Strive for simplicity and clarity when writing code.
- Use clear and descriptive naming conventions always. Names should never be ambiguous or vague, even if they are longer. Clarity is more important than brevity in naming.
- Write code that is clear and self-documenting in its structure. Code should read nearly like English.

## Comments

- Don't write unnecessary comments, especially ones that explain "what" the code is doing (that is obvious from reading it). Instead, write comments that explain the "why" behind the code, explaining the reasoning behind non-obvious code especially around performance optimizations, edge case handling, and security implications.
- Prefer idiomatic doc-style comments when you do write comments (example: full-formed JSDoc comments when writing JavaScript/TypeScript code).
- Don't add "structural" comments that just break up code into sections (example: // --- Hooks ---). Use organizational structures like directories and files to create clear separations instead.

## Organization

- Always follow the existing codebase organizational structures and patterns first. If these patterns do not exist yet, organize code first by feature and domain, then by type (example directory structures: /auth/components, /auth/hooks, /user/components, /user/utils).
- Prefer directory structures that make it clear where to find code for a specific feature. Follow the idiom "if I didn't understand this codebase and was looking for where this feature was implemented, where would I logically look?"

## Testing Expectations

- Code should always be written with the expectation that it will be tested in an automated fashion. Prefer clear lines of separation between code dependencies to make testing easier.
- All code should have at bare minimum white box unit tests covering its core logic. Business logic should have 100% code coverage.
- Module-level code should have black box integration tests that test the module as a whole with its interactions with other modules mocked out.

# Git Conventions

Apply these rules to every git operation:

- When you don't know the codebase git commit conventions, review the most recent 5 commits and follow the established patterns. If there is no established pattern or the existing pattern is erratic, follow conventional commits.
- Prefer short and direct commit messages that convey the "what" of what is being committed based on the code itself. Avoid commits like "addressing PR comments" or generic "refactored code" commit messages.
