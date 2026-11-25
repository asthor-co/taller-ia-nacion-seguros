# /spec

Write or update specs for the current feature. This is phase 2 of the workflow — only run after UNDERSTAND is complete and the user has given the go-ahead.

## Input

$ARGUMENTS — optional: unit name and/or clarifications. If the unit context is not clear from the current conversation, ask.

## Spec Types and Structures

### Entity Spec (`<unit-dir>/specs/entities/<name>.md`)

Use when: a new DB table is needed, or an existing table changes (for packages: new types, interfaces, or schemas).

Required sections:
- **Description** — one sentence, what this entity represents
- **Schema** — table name, all columns (name, type, nullable, default, constraints)
- **Relations** — foreign keys with cardinality (belongs_to, has_many, etc.)
- **Invariants** — state rules that must always hold (e.g. "once signed, no field may be updated")

### Flow Spec (`<unit-dir>/specs/flows/<name>.md`)

Use when: a user action, process, or background job needs to be defined (for packages: an integration pattern or internal logic flow).

Required sections:
- **Description** — what this flow accomplishes, in one sentence
- **Actors** — who triggers it, who is affected
- **Preconditions** — what must be true before the flow starts
- **Steps** — numbered sequence including happy path, branches, and error cases
- **Business Rules** — validation rules, rate limits, authorization requirements, edge case handling
- **Postconditions** — what is true after the flow completes successfully

### UI Spec (`<unit-dir>/specs/ui/<name>.md`)

Use when: a screen or visual component needs to be defined.

Required sections:
- **Description** — what the user sees and does on this screen
- **Layout** — shell/frame type, component hierarchy, responsive behavior (mobile-first)
- **States** — every visual state: loading, empty, error, success, partial, edge cases
- **Interactions** — what happens on tap/click/submit/swipe, navigation targets
- **Accessibility** — keyboard navigation, screen reader labels, focus management

## Instructions

1. **Resolve the unit directory** from conversation context or arguments. Check `apps/<name>/` and `packages/<name>/`.
2. Read existing specs in `<unit-dir>/specs/` to understand current state and conventions.
3. Determine which spec types are needed for this feature (may be one or more).
4. Write or update the relevant specs following the structures above exactly. Do NOT add issue references or tracking metadata to spec files — specs are permanent documents that outlive any single issue.
5. **Cross-reference against ALL existing specs.** Specifically check:
   - Entity conflicts: does the new/changed schema break existing relations or invariants?
   - Flow conflicts: does the new flow contradict preconditions or postconditions of existing flows?
   - UI conflicts: does the new screen reuse components in a way that conflicts with existing usage?
6. **Write a changes file** to `<unit-dir>/specs/plans/<feature-name>.changes.md` (create if it doesn't exist, append if it does). Record all files created or modified in this phase under a `## SPEC` section.
7. Present a summary:
   - Files created or updated (with paths)
   - Key decisions made
   - Conflicts or dependencies flagged (if any)

## Changes file format

```markdown
# Changes: <feature-name>
GitHub Issue: #<number> (if applicable)

## SPEC
- Created/Modified `<unit-dir>/specs/flows/<name>.md` — <what changed>
- Created/Modified `<unit-dir>/specs/entities/<name>.md` — <what changed>
- Created/Modified `<unit-dir>/specs/ui/<name>.md` — <what changed>
```

## Rules

- Follow existing spec conventions in the project — match the style of existing specs.
- Do NOT write implementation plans or code.
- Do NOT proceed to the next phase automatically.
- If you find conflicts, explain them clearly and suggest resolution options.
- End your response with: "Ready to proceed to DESIGN when you are, or let me know what to adjust."
