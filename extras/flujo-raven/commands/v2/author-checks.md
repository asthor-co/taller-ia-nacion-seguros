# /author-checks (v2)

Turn an **approved DoD contract** into the **oracles that will judge the build** — before any implementation exists. For each machine-verifiable criterion, write a check that fails today (red) and will pass only when the criterion is met. This skill exists so the agent that satisfies the checks is **not** the agent that wrote them: it is the structural answer to "the model can't grade its own homework."

Runs after `/clarify`, before `/build`. It is a hard ordering: a check authored *after* the code tends to assert whatever the code happens to do.

Two layers, same convention as the rest of v2. **Layer 1** is the model-agnostic task contract. **Layer 2** is the Claude Code binding. The four oracles are defined once in [`_oracles.md`](_oracles.md) — read it; do not restate it here.

---

## Layer 1 — Portable contract (model-agnostic)

### Inputs

- The **approved DoD contract** for the target — a `unit` contract at `apps/<unit>/specs/dod/<issue>.md`, or the `parent` contract at `specs/dod/<issue>.md` (its **seam** criteria). If `approved_by` is empty, STOP — not approved, no check may be authored yet. See [`_contract.md`](_contract.md) for the two kinds.
- The **brief** (linked from the contract's `brief:`) — read its `## Decisions` to know what each criterion actually means and why, so the checks assert the intended behavior, not a literal misreading of a terse `what`. In particular, a terse "the suite passes" / "no regressions" `what` means **no new regressions this change introduces** — never "the whole suite is green regardless of what was already red." Scope it accordingly (see the scope-to-change rule in step 2).
- The unit's **`TESTING.md`** — the source of test conventions: runner/commands, where each oracle's tests live, the fixture/seed entrypoints and isolation pattern, and the **baseline** reference data the environment already guarantees. Plus the unit's **durable specs**.
- For `visual` criteria, the unit's **`.pen` mockup** frames named by the contract.

### The independence rule (read first)

You derive every **expected value** from the contract and the durable specs — **never** from the feature's implementation. You may read surrounding code, but only to (a) match test conventions and (b) wire fixtures/imports. The moment you let existing code tell you what the answer *should* be, the oracle is worthless. For a fresh feature there is no implementation to look at; if any partial implementation of this issue exists, treat it as untrusted and ignore its outputs when deciding what to assert.

But the conventions and wiring you DO borrow must be **accurate** — read from the unit's real code and test exemplars (`TESTING.md`), never guessed. Enum values, DB constraints, factory signatures, and how this codebase consumes a query (e.g. `db.execute()` returns an array here, not `{rows}`) are **facts to read, not assume**. Asserting expected values from the contract is the rule; fabricating the plumbing around them — a guessed enum, a constraint-violating seed, a wrong return shape — is what produces checks that don't even compile and waste `/build`'s time.

### Procedure

1. **Load and gate.** Read the contract. If not approved, stop. Otherwise take its acceptance criteria as the work list.

2. **Per criterion, author by oracle** (see `_oracles.md` for what each proves):

   - `funcional` → write a **red unit/integration test** asserting the criterion. Expected values come from the contract/specs.
   - `comportamiento` → write a **red E2E/integration spec** that drives the flow end-to-end, **plus the per-case fixture it needs** — built with the unit's seed/fixture conventions from `TESTING.md`, on top of the documented baseline (do not recreate the org/branch/category the baseline already guarantees), isolated and torn down per the unit's pattern. Follow the unit's existing E2E harness shape.
   - `visual` → you do not write a passing renderer. You produce the **check spec**: the `.pen` frame identity, the target screen + state, the **render recipe** (how `/verify` reaches that screen at that state — route + state-forcing, or for non-route artifacts like emails/PDFs the unit's preview/fixture path), and the diff configuration (viewport, which element, tolerance). **Scope the diff to the criterion's own region** — set the selector to the screen's content/component, NOT the full page. Shared global chrome (sidebar, header, nav) is out of this check's scope: it has its own provenance and is verified by its own criterion when it changes, so a screen's visual check never depends on chrome staying frozen (a future sidebar item must not break it). Record it as data, not as an executable assertion.
   - `humano` → there is no executable check. Specify exactly **what evidence** `/verify` must package for the human (which screenshot, which output, which state) so the human can judge with minimal context.

   **Scope a check to the change, not the pre-existing world.** For a `funcional`/`comportamiento` criterion phrased as "no regression" / "the suite still passes", operationalize it as a **baseline delta** — assert the change introduces no NEW failures (the failing set stays ⊆ the pre-change baseline, restricted to the criterion's scope), or scope the check to the tests that exercise the issue's own surfaces. **Never** encode it as an absolute "whole suite green": a test already red on `base` is not this issue's regression, and gating on it makes the issue hostage to unrelated breakage it never caused. This is the `funcional`/`comportamiento` analogue of scoping a `visual` diff to its own region (the `visual` bullet above) — same principle, machine oracle instead of pixels. Two operationalizations, in order of preference:
     - **Default** = scope the check to the **diff-affected tests** and assert they are green — the lightest correct answer.
     - **Rigorous option** = snapshot the base failing set once and assert **no new failures** against it. Heavier: it must run the whole suite on `base` to establish the baseline, so note the cold-suite cost (cf. #57) and reach for it only when a diff-scoped selection can't express the criterion.

   **If the target is a `parent` contract**, its criteria are all **seam** criteria (`comportamiento`, `env: full-stack`). Author each as a full-stack E2E that boots every unit named in the parent's DAG together and drives the cross-unit behavior across the boundary. There is no per-unit convention to match — follow the full-stack harness. The parent has no `/build`; these checks go red→green purely as the child units land and the seam holds, so author them only once the units they cross actually exist (after their waves).

3. **Confirm red for the right reason — typecheck AND run.** A check that does not compile, crashes on setup, violates a DB constraint, or reads a query the wrong way is **red for the WRONG reason** — a broken oracle that wastes `/build`'s time, not a real one. Two gates, both mandatory:
   - **Typecheck the checks.** A check that doesn't compile is a defect — fix it before handoff. A bad enum value, a wrong type, a missing import surface here without running anything.
   - **Run them against the booted environment.** Stand the test env up — the harness provides it (`scripts/test-env.sh`) — and run each check, confirming it fails **because the criterion is unmet**, not because the seed/helper is malformed (the `_test` DB is up, the seed actually inserts within its constraints, helpers read the real return shapes). `provisional` is allowed **only** when the environment genuinely cannot exist yet — e.g. a full-stack seam check before its units are built — **never** as a shortcut to skip booting a DB the harness can stand up. If you couldn't run it, you didn't finish authoring it.

4. **Wire each check back to its criterion.** In the contract, for every criterion: fill `check_ref` (test file path, or the visual diff-spec location, or the evidence spec), and advance `status` from `pending` to `red` (machine oracles) or `needs-human` (`humano`, and `visual` until the judge is trusted). Leave `evidence` empty — that is `/verify`'s to fill.

### Output

- New **failing checks** committed to the working tree, following the unit's test conventions and located where that unit keeps its tests.
- The DoD contract updated: every criterion has a non-empty `check_ref` and an advanced `status`.

### Done / gate

- The contract was approved before any check was written.
- Every machine-verifiable criterion (`funcional`, `comportamiento`, `visual`) has a check and a `check_ref`.
- Every `humano` criterion has an evidence spec.
- No expected value was lifted from the feature's implementation.
- Checks are red (or provably-red-pending-environment), and red for the criterion — not for a test defect.

### Rules

- Do NOT write or modify implementation code. Only checks, fixtures/seed, and the contract.
- Do NOT read the feature's implementation to decide what to assert (the independence rule). Reading for conventions and wiring is fine.
- Do NOT make a check pass. Your output is red by design; turning it green is `/build`'s job.
- Do NOT invent a machine oracle for a `humano` criterion — surface evidence instead.
- Match existing test style exactly (naming, layout, fixtures). A new test that ignores the unit's conventions is a defect.
- Hand off only checks that **typecheck** and that you've **run red-for-the-right-reason** (or are genuinely-unbootable `provisional`). A check that doesn't compile, crashes on setup, or violates a constraint is a defect YOU fix here — never something `/build` discovers and routes back. Read facts (enum values, constraints, return shapes) from the code/exemplars; do not guess them.
- Do NOT proceed to `/build` automatically.

---

## Layer 2 — Harness binding (Claude Code specifics)

Not portable — names tools and layouts specific to this harness.

- **Locate the contract**: `specs/dod/<issue>.md` under the unit dir resolved from `$ARGUMENTS` or conversation context.
- **Test locations & conventions** (this monorepo):
  - `funcional` (Vitest): colocated `*.test.ts(x)` next to source, or the unit's `__tests__/`. Match what the unit already does.
  - `comportamiento` (API): integration tests under `apps/api/src/**/*.test.ts` run against the `_test` Postgres DB via the existing test setup/factories.
  - `comportamiento` (frontend flows): Playwright specs under `apps/<app>/e2e/*.spec.ts`, with seed/fixtures in the same dir (`seed.ts`, `fixtures.ts`, `constants.ts` — follow the fulfillment e2e harness as the reference shape).
  - `visual`: store the diff-spec next to the e2e specs or under the contract's sibling (your call, but be consistent); reference the `.pen` frame by id.
- **Read mockup frames (visual)**: `.pen` is encrypted — never Read/Grep. Use Pencil MCP to identify the frame and capture the reference screenshot the visual judge will diff against.
- **Typecheck + confirm red**: first `pnpm --filter @raven/<unit> typecheck` — a check that doesn't compile is a defect, fix it. Then run each check with `pnpm --filter @raven/<unit> test -- <path>`. For integration checks needing the `_test` DB, **boot it** (`scripts/test-env.sh db`) and run them — that is exactly what the harness is for; do NOT mark them provisional to avoid booting. Reserve `provisional` for the genuinely-unbootable (a full-stack seam before its units exist). Read each failure and confirm it's the criterion that's unmet, not a malformed seed/helper.
- **Update the contract**: Edit `specs/dod/<issue>.md` in place — `check_ref`, `status`. Leave `evidence` untouched.

End your response with a per-criterion table (id · oracle · check_ref · status), and: "Checks authored and red. Next: `/build`."
