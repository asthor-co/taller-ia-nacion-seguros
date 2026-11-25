# /understand

Start the UNDERSTAND phase for a feature. This is always the first step — never skip it.

## Input

$ARGUMENTS — a unit name (app or package) + feature description or GitHub issue number (e.g. "api #42" or "ui button-variants"). The unit name identifies which workflow unit this work targets.

## Instructions

1. **Parse the arguments.** Extract the target unit name and the feature reference. If the unit name is missing or ambiguous, list available units in `apps/` and `packages/` and ask.
2. **Resolve the unit directory.** Check `apps/<name>/` and `packages/<name>/` to find the matching unit. If found in neither, stop and tell the user.
3. **If a GitHub issue is referenced**, read it with `gh issue view <number>`. Extract the title, description, labels, and any linked issues.
4. **Read all related existing specs** — search `<unit-dir>/specs/flows/`, `specs/ui/`, and `specs/entities/` for anything related to this feature.
5. **Summarize back to the user:**
   - What the feature is (in your own words, one paragraph)
   - What existing specs it touches (list files)
   - What existing code it likely affects (list key files/directories)
   - Open questions or ambiguities that need clarification
6. **Ask the user** to clarify anything ambiguous before proceeding.

> **Phase ownership — do not misroute decisions.** `/design` is **UI work only** (mockups, screens, states, interactions). It holds **zero** architecture, data-model, business-logic, or API decisions. Every non-UI open question you surface here belongs to `/spec` — the very next phase. When listing open questions, never write "defer to `/design`" or "we'll decide this during design" for anything that isn't purely visual. If a question is about entities, flows, invariants, endpoints, or behavior, it resolves in `/spec`.

## Rules

- Do NOT write any specs, code, or plans.
- Do NOT proceed to the next phase automatically.
- Keep the summary concise — bullet points, not essays.
- Do NOT defer any architecture, data-model, business-logic, or API question to `/design`. `/design` is UI-only. Route those to `/spec`.
- If no existing specs are related, say so explicitly.
- If the feature comes from a GitHub issue, note the issue number. This number must be included in all specs and plans generated for this feature.
- If the feature looks simple enough that it doesn't need spec changes, suggest: "This looks like a quick fix — want to switch to `/fix`?"
- End your response with: "Ready to proceed to SPEC when you are."
