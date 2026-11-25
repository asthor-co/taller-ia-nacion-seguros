# /plan

Write the implementation plan for the current feature. This is phase 4 of the workflow — only run after SPEC (and DESIGN, if applicable) are approved.

## Input

$ARGUMENTS — optional: unit name and/or constraints or scope adjustments from the user.

## Instructions

1. **Resolve the unit directory** from conversation context or arguments. Check `apps/<name>/` and `packages/<name>/`.
2. **Read the changes file** — `<unit-dir>/specs/plans/<feature-name>.changes.md`. This lists all specs and mockups created or modified in the SPEC and DESIGN phases. Use this as your guide for what needs to be implemented.
3. **Read the referenced specs** listed in the changes file.
4. **Read the mockups via Pencil MCP tools.** If the feature has UI work:
   - Read the app's mockup files in `<unit-dir>/specs/ui/mockups/` using Pencil MCP tools (batch_get). Identify the specific screens/nodes relevant to this feature.
   - The "Components / UI" section of the plan must reference specific mockup elements so implementation has concrete visual targets.
5. **Read the project conventions** — root `CLAUDE.md`, `<unit-dir>/CLAUDE.md`, and `<unit-dir>/TECH.md` for stack, naming, patterns, and testing requirements.
6. **Forward dependency check.** Before drafting any plan content:
   - Read `<unit-dir>/PRODUCT.md`. Grep for `(planned, see #N)` markers in Dependencies and any Open Questions referencing GitHub issues.
   - Re-read each spec listed in the changes file and grep for `(planned, see #N)` markers there too.
   - Build a list of every forward dependency that the current feature **touches** (by name-matching the planned endpoint/contract against the feature's specs and the Changes you're about to plan).
   - For each touched forward dependency, run `gh issue view <N> --json state,title` to confirm current status.
   - **If the issue is now closed**: stop and suggest updating `PRODUCT.md` and the relevant spec to remove the `(planned, see #N)` marker. Do not silently proceed against stale markers.
   - **If the issue is still open**: list it with priority and ask the user explicitly which path to take:
     - **(a) stub it** in the plan with a TODO and a backfill issue,
     - **(b) defer this feature** until the issue ships,
     - **(c) pause planning** and resolve the issue first.
   - Do NOT silently plan against vapor endpoints. If a `critical`-priority forward dependency is touched and unresolved, the default action is to STOP and ask before drafting the plan.
7. **Write the implementation plan** with these sections:

### Plan Structure

```markdown
# Plan: <feature-name>

Unit: <unit-name>
Location: <unit-dir>/
GitHub Issue: #<number> (if applicable — omit this line if no issue)

## Overview
One paragraph: what this plan implements and which specs it's based on.

## References
- Flow spec: `<unit-dir>/specs/flows/<name>.md`
- UI spec: `<unit-dir>/specs/ui/<name>.md`
- Entity changes: `<unit-dir>/specs/entities/<name>.md` (if applicable)
- Design mockup: (if applicable)

## Changes

### Schema Changes
List any DB migrations, new tables, altered columns. Skip if none.

### Service Layer
Files to create or modify. For each:
- File path
- Functions to add/modify
- Key logic (one sentence per function)

### Server Actions / API
Files to create or modify. For each:
- File path
- Actions/endpoints to add
- Input validation

### Components / UI
Files to create or modify. For each:
- File path
- What it renders
- Key interactions

### Other Changes
Anything else: config, utilities, migrations, seed data.

## Acceptance Criteria

The binding, oracle-tagged definition of done for this feature — the target the independent checks (step 8) will assert and the verify sub-agent (in `/implement`) will grade against. Distinct from the Test Plan below, which is implementation guidance for yourself; this table is the contract.

Write 2–6 criteria. Each is **one observable claim** with **exactly one oracle** drawn from the v2 oracle taxonomy — read [`.claude/commands/v2/_oracles.md`](.claude/commands/v2/_oracles.md) and use those four oracles unchanged (`funcional`, `comportamiento`, `visual`, `humano`), including its "Choosing an oracle" guidance and `pending → red → green / needs-human → approved` status lifecycle. Prefer the most machine-verifiable oracle a criterion admits; `humano` is the escape hatch, not a default, and every `humano` criterion is a place the loop can't run alone — flag it as a deliberate choice. One observable claim per row; if a claim needs two oracles, it's two criteria.

| id | what (observable) | oracle | check_ref | status | evidence |
|---|---|---|---|---|---|
| ac1 | <the observable claim> | funcional\|comportamiento\|visual\|humano | _(filled by step 8)_ | pending | |

- For a `visual` criterion, name the **screen + state** in `what` (e.g. "invoice-list / empty"); the check is a frame-specific diff.
- For a `humano` criterion, `what` must say what evidence will be surfaced.
- **You propose criteria + oracles; the user owns the final call on both.** Present them and get an explicit yes before running step 8.

## Test Plan
What to test, organized by layer. Expected coverage target. (Implementation guidance — the Acceptance Criteria above is the binding contract.)

## Execution Order
Numbered list of implementation steps in dependency order.
```

8. **Author the acceptance checks via a fresh sub-agent — independence gate.** Once the user has approved the Acceptance Criteria, spawn a **fresh sub-agent** (a separate context, not this one) to turn each machine-verifiable criterion into an executable check that fails **today** (red) and will pass only when the criterion is met. This is the cross-check that v1 lacked: the agent that writes the checks must **not** be the agent that later satisfies them, and the checks must exist **before** the implementation — a check authored after the code tends to assert whatever the code happens to do.

   Give the sub-agent this task: "Read [`.claude/commands/v2/author-checks.md`](.claude/commands/v2/author-checks.md) and [`.claude/commands/v2/_oracles.md`](.claude/commands/v2/_oracles.md) and follow them, but bound to the **Acceptance Criteria table** in `<unit-dir>/specs/plans/<feature-name>.md` instead of a DoD contract — treat that table's rows as the criteria (its `oracle`/`check_ref`/`status` columns are the contract fields). The plan is already approved, so the approval gate is satisfied; read the plan + the referenced specs for intent. Honor the independence rule (derive every expected value from the plan/specs, never from any existing implementation), ground all plumbing — enum values, DB constraints, factory signatures, query return shapes — in the unit's real code and `TESTING.md`, then **typecheck the checks AND run them against the booted env** (`scripts/test-env.sh`) to confirm each is red **for the right reason** (the criterion is unmet, not a broken seed). Write the checks where the unit keeps its tests, fill each row's `check_ref`, and advance each row's `status` from `pending` to `red` (or `needs-human` for `humano` / untrusted `visual`). Do NOT write or modify implementation code; do NOT make any check pass."

   Wait for the sub-agent to report back, then confirm every machine-verifiable row has a `check_ref` and a `red`/`needs-human` status before handing off.

9. **Save the plan** to `<unit-dir>/specs/plans/<feature-name>.md` (the sub-agent updates the Acceptance Criteria table in place; you keep the rest current).
10. **Present a summary** of the plan — key decisions, scope, estimated complexity, and the acceptance-criteria/oracle table with check status. If any forward dependencies were stubbed, list them explicitly so they're visible at handoff to `/implement`.
11. **Emit a ready-to-paste implementation prompt (REQUIRED — this is the deliverable of `/plan`).** After the summary, output a fenced code block containing a self-contained prompt the user can copy into a fresh session to implement the plan. **Never skip this**, even if the plan is partial, the forward-dependency check paused you, or the acceptance-check sub-agent (step 8) failed or was aborted — in those cases still emit the prompt and note the caveat inside it. The whole point of `/plan` is to hand off implementation to a different session; a run that ends without this block is incomplete. It must:
    - Start with the `/implement` invocation for the unit.
    - Name the plan file path (`<unit-dir>/specs/plans/<feature-name>.md`) as the source of truth, plus the unit dir so the agent can resolve context.
    - Note that acceptance checks are already authored and red — they must be made green, not rewritten.
    - Call out any stubbed forward dependencies the implementer must respect.
    - Contain no conversational framing — only what belongs in the pasted prompt.

    Template:

    ```
    /implement <unit-name>

    Implement the approved plan at `<unit-dir>/specs/plans/<feature-name>.md`. That plan + the specs it references are the source of truth; read them first. Unit dir: `<unit-dir>/`.

    Acceptance checks are already authored and currently red — make them green, do not rewrite them.
    <If any: Respect these stubbed forward dependencies: #N (contract: ...).>
    ```

## Rules

- **Always end the run by emitting the ready-to-paste implementation prompt (step 11).** It is a required, unconditional deliverable — the reason `/plan` exists is to hand implementation to a fresh session. Emit it even when earlier steps were partial, paused, or aborted; never let a `/plan` run finish without it.
- The plan must be **self-contained**: a new conversation should be able to implement it by reading only this file, the specs it references, and the CLAUDE.md files.
- **Every criterion carries exactly one oracle from the v2 taxonomy** ([`.claude/commands/v2/_oracles.md`](.claude/commands/v2/_oracles.md)) — do not invent new oracle kinds. Prefer machine oracles over `humano`; flag any `humano` criterion as a conscious choice.
- **The acceptance checks are authored by a fresh sub-agent (step 8), never by you.** You may not write the checks in this context, and you may not write any implementation code. The whole point is that the check-author is not the implementer.
- Do NOT start coding or create any source files.
- Do NOT proceed to the next phase automatically.
- Do NOT skip the forward dependency check (step 6). A `critical`-priority unresolved dependency that the feature touches is a hard stop — ask the user before proceeding.
- When stubbing a forward dependency, the plan MUST include the stub location, the assumed contract, and the backfill issue number — do not leave silent TODOs in the code.
- List specific file paths, not vague descriptions.
- If the feature is large, suggest how to split into sub-plans.
- End your response with: "Plan saved to `<unit-dir>/specs/plans/<feature-name>.md`, acceptance checks authored and red. Ready to implement when you are — I recommend starting a new conversation for maximum context. Paste the prompt above to kick it off."
