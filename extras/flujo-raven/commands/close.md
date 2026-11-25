# /close

Close out a completed feature. This is the final phase of the workflow — run once the work is done.

## Input

$ARGUMENTS — optional: the unit name and feature name or plan file path.

## Instructions

1. **Identify the feature and unit** from arguments or the current conversation context.
2. **Resolve the unit directory.** Check `apps/<name>/` and `packages/<name>/`.
3. **Read the plan file** (`<unit-dir>/specs/plans/<feature-name>.md`) to check for a `GitHub Issue:` reference.
4. **Close the tracking item** (if applicable):
   - **GitHub Issue:** if the plan file references a GitHub issue, close it with `gh issue close <number>`.
   - If no issue applies, skip this step.
5. **Delete transient files** from `<unit-dir>/specs/plans/`:
   - `<unit-dir>/specs/plans/<feature-name>.md` (the plan)
   - `<unit-dir>/specs/plans/<feature-name>.changes.md` (the changes log)
   The specs and code are the permanent artifacts; plan and changes were transient handoff documents.
6. **Update the MVP roadmap** (if applicable). Check if `<unit-dir>/specs/plans/mvp-roadmap.md` exists AND the completed feature is listed in it. If both conditions are true, mark the feature's checkbox as done (`- [x]`). If this was the last unchecked feature, mention that the MVP is complete.
7. **Report** what was closed and cleaned up.

## Rules

- Do NOT delete specs — only the plan file and changes file.
- Do NOT delete `<unit-dir>/specs/plans/mvp-roadmap.md` — it is a permanent tracking document.
- Do NOT make any code changes.
- If `gh` CLI is not available or the issue close fails, tell the user to close it manually.
- Keep it brief.
