# /commit

Create a local commit for the work produced in the current workflow. This is phase 6 of the workflow — run after IMPLEMENT is reviewed and approved by the user. For `/fix` workflows, run after the fix is reviewed.

This command creates a **local commit only**. It does not push, does not open a pull request, and does not interact with `gh`.

## Input

$ARGUMENTS — optional: additional context for the commit message.

## Instructions

1. **Check prerequisites.**
   - Confirm you're on a feature or fix branch (not main). If on main, stop and tell the user.
   - Run `git status` — if there is nothing staged or modified, stop and tell the user there is nothing to commit.
2. **Gather context.**
   - Determine the target unit from the branch name (e.g. `feat/api/42-orders` → `api`, `feat/auth/rbac` → `auth`).
   - Resolve the unit directory — check `apps/<name>/` and `packages/<name>/`.
   - Read the plan file if it exists (`<unit-dir>/specs/plans/<feature-name>.md`) — extract the overview, scope, and GitHub issue reference.
   - Run `git status` to see what's staged and unstaged.
   - Run `git diff --staged` and `git diff` to see the actual changes.
   - Run `git log -n 5 --oneline` to match the repository's commit message style.
3. **Draft the commit message.**
   - **Subject:** concise, under 70 chars, imperative mood (e.g. "Add orders endpoint", not "Added" or "Adding").
   - **Body** (optional, only if the change warrants explanation):
     ```
     <what changed and why, in 1-3 short paragraphs or bullets>

     Unit: <unit-dir>/
     Refs: <unit-dir>/specs/plans/<feature-name>.md (if applicable)
     Refs: #<issue-number> (if applicable)
     ```
   - Focus on the **why**, not a file-by-file recap of the diff.
4. **Show the draft message to the user** and wait for approval before committing.
5. **Stage and commit.**
   - Stage the relevant files by name (avoid `git add -A` / `git add .` so sensitive or unrelated files aren't swept in).
   - Create the commit with the approved message using a HEREDOC to preserve formatting.
6. **Report.** Show the new commit's short hash and subject, and confirm the working tree is clean (or note any intentionally-unstaged files).

## Rules

- Do NOT push the branch.
- Do NOT create a pull request.
- Do NOT run `/close` automatically.
- Do NOT modify code or specs — this command only commits what's already there.
- Do NOT use `git add -A` or `git add .` — stage files explicitly by path.
- Do NOT amend previous commits unless the user explicitly asks. Create a new commit instead.
- If pre-commit hooks fail, fix the underlying issue and create a new commit (do not use `--no-verify`).
- Keep the message concise but complete enough that a reviewer reading `git log` alone understands what changed and why.
