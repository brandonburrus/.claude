---
name: open-pull-request
description: Use this skill when opening, creating, or submitting a pull request
  for the current branch. Use when the user says "open a PR", "create a pull
  request", "submit this for review", "put this up", "push this up and open a PR",
  or asks to get the branch ready for review. Do not use for reviewing an existing
  PR (use the review skill), merging or managing PRs, or committing without a PR.
---

## Purpose

Take the current branch from its working state to an opened pull request: commit what is pending, resolve the base branch, draft a title and body grounded in the actual diff, link the related issue, push, and create the PR with `gh`. Create immediately once the required data is resolved; ask only when something is genuinely ambiguous (base branch, template choice, multiple issue candidates). Report the PR URL when done.

## Workflow

Copy this checklist and track progress:

```text
PR Progress:
- [ ] 1. Pre-flight passed (auth, branch, existing PR)
- [ ] 2. Working tree committed
- [ ] 3. Base branch resolved
- [ ] 4. Diff read; issue reference resolved
- [ ] 5. Title and body drafted
- [ ] 6. Pushed and created; URL reported
```

### 1. Pre-flight

Stop and report instead of proceeding when any of these fails:

- `gh auth status` succeeds; if not, tell the user to run `gh auth login` (suggest they type `! gh auth login` so the interactive flow runs in-session)
- `git rev-parse --abbrev-ref HEAD` is a real branch: detached HEAD or the default branch means stop and have the user create a feature branch first; never open a PR from the default branch onto itself
- `gh pr view --json url,state 2>/dev/null`: if an open PR already exists for this branch, do not create a duplicate; report its URL and offer to update its title or body instead (`gh pr edit`)

### 2. Commit pending work

If `git status --porcelain` shows changes, commit them without asking:

- Stage everything first (`git add -A`), then scan the staged diff for secrets (`git diff --cached` against patterns like `password`, `secret`, `api_key`, `token`, private key headers). Staging before scanning matters: untracked files never appear in `git diff`, so scanning the unstaged diff silently misses a brand-new credentials file. On a hit, unstage, stop, and show the user the offending lines; a secret pushed to a remote is published even if force-removed later.
- Then commit with a message derived from the staged diff, following the repository's commit conventions (review recent commits per the global git rules). If the diff is too broad for one honest summary, use `chore: save branch changes for pull request`.

### 3. Resolve the base branch

Use the user-specified target if one was given. Otherwise:

1. Default branch: `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`, falling back to `git symbolic-ref refs/remotes/origin/HEAD`
2. Check where this branch forked from: if `git merge-base HEAD origin/<default>` sits on the default branch, target the default branch without asking
3. If the history suggests this branch forked from a different parent branch (stacked branches), ask which branch the PR should target, recommending the likely parent

### 4. Read the diff and resolve the issue reference

- `git log <base>..HEAD --oneline` and `git diff <base>...HEAD --stat` for shape, then read the substantive hunks of the full diff. Commit messages alone produce vague bodies; the diff is what the PR actually contains.
- Scan the branch name and commit messages for GitHub issue references (`#123`, `GH-123`, `owner/repo#123`):
  - Exactly one found and the work fixes it (fix/close language in commits, or the branch implements the issue): use `Closes #123`
  - Exactly one found but the relationship is partial: use `Refs #123`, because `Closes` auto-closes the issue on merge and a wrong auto-close loses tracking silently
  - Multiple found: ask which one this PR is for
  - None found: omit; do not ask

### 5. Draft title and body

**Title:** imperative mood, 72 characters maximum. Match the repository's established PR title pattern: check `gh pr list --state merged --limit 5 --json title` and follow what the repo does (conventional-commit style titles when the repo uses them, plain imperative otherwise).

**Body:** find the repo's PR template and fill it; check in order:

```text
.github/pull_request_template.md
.github/PULL_REQUEST_TEMPLATE/*.md   (multiple: list them and ask which)
docs/pull_request_template.md
pull_request_template.md
```

With no template, use:

```markdown
## Summary

- <what changed and why, 1-3 bullets at the feature or behavior level>

## Testing

<how the changes were verified>
```

Body rules:

- 1-3 bullets conveying the what and the why; the reviewer reads the diff for specifics, so never enumerate files or restate each commit
- Never invent details absent from the commits and diff, including test claims; if the changes were not tested, say so rather than decorating the Testing section
- Fill template sections minimally and honestly; leave inapplicable sections at their defaults instead of over-filling them
- The issue reference from step 4 goes in the body, not the title
- Keep it short; a wall of text will not be read

### 6. Push and create

- No upstream (`git rev-parse --abbrev-ref @{u}` fails): `git push -u origin HEAD`
- Upstream exists and `git rev-list --count @{u}..HEAD` is greater than 0: `git push`
- Never force-push, even when the remote rejects; report the rejection and stop

Then create and report the URL:

```shell
gh pr create --base <base> --title "<title>" --body "<body>"
```

Add `--draft` when the user asked for a draft or called the work in-progress. Print the returned PR URL.

## Guardrails

- Never force-push.
- Never merge, close, or delete anything; this skill only creates.
- Never open a PR from the default branch.
- Never create a second PR for a branch that already has an open one; update the existing PR instead.
- Do not add an approval gate before creation; the PR title and body are editable after the fact with `gh pr edit`, so ask up front only for genuinely missing data.

## Gotchas

- **Drafting from commit messages alone produces fiction.** Commit messages describe intent at commit time; the diff is the truth. Read it before writing a single body bullet.
- **`Closes #N` is an action, not a label.** It auto-closes the issue when the PR merges. Used on a partially-related issue, it silently kills live tracking; default to `Refs` unless the PR genuinely finishes the issue.
- **`gh pr create` fails when a PR already exists for the branch.** The pre-flight check exists because the error surfaces late, after pushing and drafting; check first and route to `gh pr edit`.
- **Stacked branches silently target the wrong base.** A PR for branch B forked from branch A diffs against the default branch as A+B's changes combined, doubling the review surface. The merge-base check in step 3 exists to catch this before the reviewer does.
- **The auto-commit is for the PR, not a license to bypass hygiene.** The secrets scan runs before every auto-commit because pushing publishes; once on the remote, a leaked credential must be rotated, not just removed.
