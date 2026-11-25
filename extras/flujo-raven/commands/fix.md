# /fix

Quick fix for small, well-scoped changes that don't require spec updates. Use `/understand` instead for features that need new or modified specs.

## Input

$ARGUMENTS — a unit name (app or package) + description or GitHub issue number (e.g. "api login redirect bug" or "auth #18").

## Instructions

1. **Parse the arguments.** Extract the target unit name and the fix reference. If the unit name is missing or ambiguous, list available units in `apps/` and `packages/` and ask.
2. **Resolve the unit directory.** Check `apps/<name>/` and `packages/<name>/` to find the matching unit. If found in neither, stop and tell the user.
3. **If a GitHub issue is referenced**, read it with `gh issue view <number>`.
4. **Assess complexity.** If the change appears to require new or modified specs (new entities, new flows, UI spec changes, schema changes), tell the user: "This looks like it needs specs — want to switch to `/understand`?" and stop.
5. **Clarify ambiguities.** If anything is unclear, ask before proceeding.
6. **Read the relevant code** — identify the files that need to change.
7. **Propose the change:**
   - What you'll do (one paragraph)
   - Which files you'll modify
   - Any risks or side effects
8. **Wait for the user's confirmation** before writing any code.
9. **Implement the fix** following project conventions. Write or update tests as needed.
10. **Report results:**
    - What was changed (files modified)
    - Test results
    - Suggested commit message (include `fixes #N` if a GitHub issue exists)
11. **Wait for the user's review.** Then suggest: "Ready to commit? Run `/commit`."

## Rules

- Do NOT create specs, plan files, or changes files.
- Do NOT modify existing specs.
- If you discover the change is more complex than expected, stop and suggest switching to `/understand`.
- Follow project conventions strictly.
- One confirmation checkpoint (step 8) before coding — do not skip it.
- Keep it concise. This is meant to be fast.
