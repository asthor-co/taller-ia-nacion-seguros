# /implement

Execute an approved implementation plan. This is phase 5 of the workflow — only run after PLAN is approved. This phase typically runs in a **new conversation** to maximize available context.

## Input

$ARGUMENTS — path to the plan file (e.g. `apps/api/specs/plans/orders.md` or `packages/auth/specs/plans/rbac.md`), or a unit name + feature name to look up.

## Instructions

1. **Locate and read the plan file.** If a path was given, read it. If a unit + feature name was given, resolve the unit directory (check `apps/<name>/` and `packages/<name>/`) and look in `<unit-dir>/specs/plans/`. If no argument was given, list available plans across all units and ask which one to implement.
2. **Read all referenced specs** listed in the plan's References section.
2a. **Read the Acceptance Criteria table and locate its checks.** The plan carries an oracle-tagged Acceptance Criteria table; each machine-verifiable row has a `check_ref` pointing at a check that is **red today** (authored by an independent sub-agent in `/plan`). These checks are the definition of done — your job is to make them go green by implementing the feature. Read each check so you know exactly what behavior it asserts. **The checks are read-only for you**: you may not edit, weaken, delete, or skip a check, and you may not grade them yourself — an independent verify sub-agent (step 9) renders the authoritative verdict. If a check looks genuinely wrong (asserts something the plan/specs do not say), STOP and flag it to the user rather than editing it — bending the oracle to your implementation is exactly the failure mode this pipeline removes.
3. **The mockup is the constitution for UI work.** When a `.pen` mockup exists for a screen or component, it is the authoritative source for how the UI looks. Text specs describe behavior, states, and interactions; they do **not** describe visual design. You do not invent UI from text specs. You do not infer layout from JSON property dumps alone. You reproduce what is in the rendered mockup.

   This step is a hard gate: no UI code may be written before the following is done for every screen/component the plan touches.

   **3a. Screenshot first, before anything else.** For every frame you will implement (and every responsive / dark variant of it), call `mcp__pencil__get_screenshot` and **look at the image**. This is not optional, and it is not a fallback — it is the primary input. The rendered image shows:
   - What elements exist and where they sit relative to each other.
   - Whether an icon is inside or beside a container.
   - Whether buttons are side-by-side or stacked.
   - Whether a header/nav/bottom bar is present on this route.
   - Overall visual weight, density, and proportions.

   JSON from `batch_get` alone does not convey these things reliably. Reading JSON without rendering the frame is how components end up structurally wrong ("Agregar" text button instead of a `+` icon; icon outside the input instead of inside; buttons stacked instead of side-by-side). If you are about to write UI code and have not viewed the screenshot for that frame in this conversation, stop and call `get_screenshot`.

   **3b. Enumerate every frame you need.** Before implementation, list every frame id you will reference, grouped by component, and confirm you have a screenshot for each:
   - Mobile light + mobile dark (if dark variant exists).
   - Desktop light + desktop dark (if desktop variant exists).
   - Every sub-state that renders differently (e.g. cart expanded vs collapsed, empty vs populated, SOS vs regular, error banners).
   - Every frame referenced by the plan's "Mockup frames" column.

   Missing a variant means guessing that variant. Do not guess.

   **3c. JSON is the secondary reference for exact values only.** After screenshots establish structure, call `mcp__pencil__batch_get` with `readDepth: 3-4` and `resolveVariables: true` to extract the precise numbers: fill colors, text colors, font sizes/weights/families, padding, gap, corner radius, border color/thickness, shadows, icon names/sizes. Use these to set exact values in code — never to reconstruct structure you didn't see in the screenshot.

   **3d. Tokens first, mockup hex as fallback.** Before writing any color, read `packages/ui/src/styles/tokens.css` and `theme.css` to learn the **exact token names that exist** (e.g. `--color-text`, `--color-text-muted`, `--color-card`, `--color-primary-subtle`). Do not invent tokens like `--color-text-primary` or `--color-surface-secondary`; CSS silently falls back when a var is undefined, so the wrong token produces an invisible bug that manifests only in dark mode or theme switches. Rules:
   - If a mockup hex matches a token value exactly (light **and** dark, when applicable), use the token.
   - If a mockup hex does not map to any existing token (e.g. amber banner `#FEF6E0` / `#D97706` / `#92400E`), use the hex literal and **flag it at report time** as "missing semantic token — recommend adding X".
   - If a mockup value clashes with the existing token value (e.g. mockup dark text is `#E8EAED` but `--color-text` dark is `#F6F7F8`), **flag the discrepancy to the user** and ask whether to update the token or deviate locally. Never silently override a token with a hardcoded hex — that spreads drift across the app.

   **3e. Verify what you built.** After implementing a component, the user will test it in the browser. When they report a mismatch, re-screenshot the mockup frame in question and diff it against their screenshot before editing — do not patch based on the description alone. Treat their screenshot as ground truth for "what is" and the mockup screenshot as ground truth for "what should be."
4. **Read `CLAUDE.md`** (root and unit-level) for project conventions, stack, and testing requirements. Read `<unit-dir>/TECH.md` for the tech stack.
5. **Forward dependency check (hard stop).** Before writing or modifying any code:
   - Read the unit's `PRODUCT.md`. Grep for `(planned, see #N)` markers in Dependencies and any Open Questions referencing GitHub issues.
   - Re-grep the plan + every spec it references for `(planned, see #N)` markers.
   - For each forward dependency that the plan **depends on** (the plan references the planned endpoint, contract, event, or entity field), run `gh issue view <N> --json state,title` to confirm current status.
   - **If the issue is still open**: STOP. Do not begin implementation. Report each blocking issue with its priority and title. The user must explicitly choose:
     - **(a)** confirm the issue actually shipped now and update the plan + `PRODUCT.md` to remove the `(planned, see #N)` marker, or
     - **(b)** confirm we're stubbing the dependency and update the plan to record the stub location, assumed contract, and backfill issue number, or
     - **(c)** abort implementation and resolve the blocker first.
   - **If the issue is now closed**: stop and suggest updating `PRODUCT.md` and the plan to remove the `(planned, see #N)` marker before proceeding. Do not proceed against stale markers.
   - Do NOT begin code changes until every forward dependency the plan touches is either resolved, explicitly stubbed in the updated plan, or explicitly waived by the user.
6. **Execute the plan** following the Execution Order:
   - Implement each step in order.
   - Implement to satisfy the red acceptance checks — never edit them (see step 2a).
   - Write additional tests alongside the code where the plan's Test Plan calls for them (not after). These are yours; the acceptance checks are not.
   - Follow project conventions strictly (naming, patterns, error handling).
7. **Run the checks yourself as a private convergence signal — not as the verdict.** Boot the env (`scripts/test-env.sh`) and run the acceptance checks plus your own tests to see how close you are. This is for your own iteration only; it does **not** advance any criterion's status and is **not** the authoritative result. Keep implementing until you believe every check is green, but do not declare done — that is the verify sub-agent's call, not yours.
8. **Verify via a fresh sub-agent — the independent oracle.** Do **not** self-report green. Spawn a **fresh sub-agent** (separate context from this one) to render the authoritative verdict. Give it this task: "Read [`.claude/commands/v2/verify.md`](.claude/commands/v2/verify.md) and [`.claude/commands/v2/_oracles.md`](.claude/commands/v2/_oracles.md) and follow them, but bound to the **Acceptance Criteria table** in `<plan-path>` instead of a DoD contract — treat its rows as the criteria (`oracle`/`check_ref`/`status`/`evidence` are the contract fields). For each criterion with status `red`/`needs-human`, run its check against the booted env (`scripts/test-env.sh`); execute, do not judge by inspection — a criterion flips to `green` only on a passing machine verdict (or human approval for `humano`/untrusted `visual`, which route to `needs-human`). Boot whatever the harness can provide rather than skipping; report `could-not-run` only for a genuinely unbootable env. Write each row's `status` + `evidence` back into the plan's table in place, and return the per-criterion verdict table plus whether the feature is satisfied (all criteria `green`/`approved`). Do NOT fix failing criteria — record the failure; fixing is the implementer's next pass." If the human asks for a behavior change during this step, that is a **definition change** — update the plan's Acceptance Criteria (and specs) first, then re-author/re-run the affected check; never make an undocumented edit that bends a check.
9. **Report results** based on the verify sub-agent's verdict (not your own run):
   - What was implemented (files created/modified)
   - The verify sub-agent's per-criterion verdict table (id · oracle · verdict · status · evidence) and whether the feature is **satisfied**
   - For any criterion still `red`/`needs-human`: what failed, and your next iteration plan (loop back to step 6 — never edit the check to make it pass)
   - Any deviations from the plan (and why)
   - Any issues or follow-ups discovered

## Rules

- Follow the plan exactly. If something in the plan seems wrong, flag it and ask before deviating.
- **Never edit, weaken, delete, or skip an acceptance check, and never grade the criteria yourself.** The checks are read-only (step 2a); the authoritative verdict comes from the fresh verify sub-agent (step 8). Making a check pass by changing the check — instead of the code — is the exact failure mode this pipeline removes. A check you believe is genuinely wrong is a STOP-and-flag, not a self-fix.
- **Do NOT declare the feature done on your own run.** Your run (step 7) is a private signal; the verify sub-agent's verdict (step 8) is the result.
- Do NOT make changes beyond the plan's scope (no drive-by refactors, no extra features).
- Do NOT proceed to CLOSE automatically.
- Do NOT skip the forward dependency check (step 5). Open `(planned, see #N)` markers that the plan depends on are a hard stop — never silently mock or stub them mid-implementation.
- Do NOT implement any UI component without having viewed the mockup screenshot for its frame — and every relevant variant (mobile/desktop, light/dark, populated/empty, expanded/collapsed, SOS/regular, etc.) — in this conversation. If you are about to write JSX and have not called `mcp__pencil__get_screenshot` for the frame it maps to, STOP and take the screenshot first. JSON property dumps do not substitute for the rendered image.
- Do NOT invent CSS custom property names. Read the app's `tokens.css` and `theme.css` up front and only use tokens that exist there. If a mockup value doesn't map to an existing token, flag it — do not coin a new name and do not silently replace it with a hardcoded hex where a token is expected.
- Do NOT use Material Symbols or any icon font the app doesn't already load. Prefer Lucide icons (already in use). If a mockup references a Material Symbol, find the Lucide equivalent or flag it.
- If your own tests fail, fix them before reporting. If an **acceptance check** is `red` after the verify sub-agent runs, the feature is not done — iterate on the code (step 6) and re-verify; do not report complete.
- After reporting, remind the user that the next step is COMMIT (phase 6) — but only if every acceptance criterion is `green`/`approved`.
- End your response with: "Implementation complete and verified — all acceptance criteria green. Ready for your review. Next step: `/commit`." (If any criterion is still red or awaiting human sign-off, say so instead and state what remains.)
