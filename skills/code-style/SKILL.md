---
name: code-style
description: ALWAYS use whenever writing code in **any** programming language.
---

# Code Style Rules

IMPORTANT: ALWAYS follow these rules when writing code

## General Code Style

- Strive for simplicity and clarity when writing code.
- Use clear and descriptive naming conventions always. Names should never be ambiguous or vague, even if they are longer. Clarity is more important than brevity in naming.
- Write code that is clear and self-documenting in its structure. 
- Code should read nearly like english in its structure.

## Comments

- Don't write unecessary comments, especially ones that explain "what" the code is doing (its obvious what the code is doing by reading it, it doesn't need a comment to explain it). Instead, write comments that explain the "why" behind the code, explaining the reasoning behind non-obvious code especially in scenarios around performance optimizations, edge case handling, and security implications.
- Prefer idiomatic doc-style comments when you do write comments (example: full-formed JSDoc comments when writing JavaScript/TypeScript code).
- Don't add "structural" comments that are just used to break up code into sections (example: // --- Hooks ---). Instead, use organizational structures like directories and files to create clear separations of code.

## Code Organization

- Always follow the existing codebase code organizational structures and patterns first. If these patterns do not exist yet, organize code first by feature and domain, then by type (example directory sturctures: /auth/components, /auth/hooks, /user/components, /user/utils, etc).
- Prefer directory structures that make it clear where to find code related to a specific feature. Follow the idiom of "if I don't understand this codebase and was looking where this feature was implemented, where would I logically look for it?" when organizing code.

## Testing Expectations

- Code should always be written with an expectation that it will be tested, and tested in an automated fashion. Prefer clear lines of separation between code dependencies to make testing easier.
- All code should have at bare minimum white box unit tests that cover the core logic of the code. Business logic should have 100% code coverage.
- Module-level code should have black box integration tests that test the module as a whole with its interactions with other modules mocked out.
