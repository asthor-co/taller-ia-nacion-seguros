# /verify (v2)

Run the oracles. For a contract whose checks were authored (`/author-checks`) and whose code was built (`/build`), execute each criterion's check, record the verdict and evidence, and advance its status. This is the objective gate the whole redesign exists for — the step that tells the loop, mechanically, whether the work is done. It is also where the **visual VLM-diff** lives, the oracle the codebase did not have before.

`/verify` runs checks; it does **not** fix them. Fixing failing criteria is `/iterate`.

Two layers, same convention. **Layer 1** is model-agnostic. **Layer 2** is the Claude Code binding. Oracles: [`_oracles.md`](_oracles.md). Contract schema: [`_contract.md`](_contract.md).

---

## Layer 1 — Portable contract (model-agnostic)

### Inputs

- The **target contract** — a `unit` contract, or a `parent` contract (its seam criteria). Its criteria carry `check_ref` (filled by `/author-checks`) and a current `status` (`red` / `needs-human`).
- The **built working tree** for the unit(s).
- The unit's **run commands and env needs** (`TESTING.md`).
- For `visual` criteria: the **render recipe** + `.pen` reference frame + diff config named by the `check_ref`.
- For a `parent` target: the **full-stack environment**, and the precondition that every child contract in the DAG is already satisfied.

### The principle: execute, don't judge by inspection

A criterion's status flips **only** on the verdict of running its check. Never mark a criterion `green` because you read the implementation and reasoned that it "should" pass — that reintroduces the model grading its own work, which is exactly what this pipeline removes. The machine verdict (or, for `humano`, the human's verdict) is the only thing that moves status.

### Procedure

1. **Load and scope.** Read the contract. Work list = criteria with status `red` or `needs-human`. For a `parent` target, first confirm every child contract is satisfied; if any is not, STOP and report which units are unfinished — seam checks against a half-built stack are meaningless.

2. **Per criterion, run its oracle:**

   - `funcional` → run the referenced test(s). Pass → `green`. Fail → stays `red`. Evidence = pass/fail + the failure excerpt.
   - `comportamiento` → boot the seeded system (the unit's env, or the full-stack env for a seam criterion) and run the referenced spec. Same verdict rule. Evidence = result + trace/logs on failure.
   - `visual` → render the target at its named state, screenshot it, obtain the `.pen` reference screenshot, and **diff the two with a multimodal judge** using the diff config. Diff **only the region the criterion is about** (the screen's own content/component per the check's selector) and judge by the criterion's **intent** — ignore differences in shared global chrome (sidebar, header, nav) that has its own provenance and its own criterion; never fail a screen's check for incidental chrome drift (e.g. a sidebar item added by another issue). **Always emit a verdict** — `match` or `mismatch` plus **enumerated concrete differences** (spacing, color, type, hierarchy, missing/extra elements), never a vague "looks off". The verdict is computed every time; what changes is whether it auto-advances:
     - **Judge trusted** → the verdict auto-advances: `match` → `green`, `mismatch` → `red`.
     - **Judge untrusted (default)** → **both** outcomes route to `needs-human` — never auto-`red` either, since an untrusted judge's "mismatch" is no more authoritative than its "match". The evidence packaged for the human MUST include the judge's would-be verdict (`match`/`mismatch`) and its enumerated diffs, so the human sees exactly what the model would have decided and only has to confirm or override.
     - Evidence = both screenshots + the structured diff + the would-be verdict.
   - `humano` → package the evidence the check specified, set `needs-human`, and surface it to the human. Approval → `approved`. Rejection → `red` with the human's note as evidence.

3. **Bring up the env, then be honest about what truly can't run.** First stand up whatever a check needs and the harness can provide — the `_test` Postgres + seed, the API, the test-auth frontend — via `scripts/test-env.sh`. A bootable env being down is a **step, not a skip**: boot it and run the check. Only when an environment **genuinely cannot exist yet** (a full-stack seam before its units are built, a render harness that doesn't exist) do you leave a check unrun: do **not** mark it `green`/`red`, set evidence to `could not run: <reason>`, and report it as a blocker. A skipped check is always reported — never silently passed over, and never used to dodge booting an env the harness can stand up.

4. **Write back.** Update each criterion's `status` and `evidence` in the contract in place.

5. **Report.** Emit a per-criterion verdict table (id · oracle · verdict · status · evidence) and a summary: counts of `green` / `red` / `needs-human` / `could-not-run`, and whether the contract is now **satisfied** (all criteria `green`/`approved`).

### Done / gate

- Every criterion was either run (status advanced + evidence recorded) or explicitly reported `could-not-run`.
- No criterion was silently skipped.
- The contract is updated in place.
- The report states satisfied vs not, and lists exactly what blocks satisfaction.

### Rules

- Do NOT fix failing criteria — record the failure and stop; `/iterate` fixes.
- If the human requests a change during verification, that is a **definition change**, not a verification — do NOT make an undocumented code edit. Apply the live-update rule ([`_brief.md`](_brief.md)): record the decision in the brief, widen `scope_in`, and add the criterion so the change becomes official (documented + scoped + verified). A code change with no decision, no scope, and no criterion is exactly the unexplained drift a later `/verify` (e.g. the seam) correctly flags.
- Do NOT mark a criterion `green` without a passing machine verdict (or human approval for `humano`).
- Do NOT let the visual judge auto-advance while it is untrusted — route BOTH match and mismatch to `needs-human`, each carrying the judge's would-be verdict so the human can confirm or override.
- Do NOT silently skip an unrunnable check — report it as `could-not-run`.
- Visual verdicts MUST enumerate concrete differences — `/iterate` needs actionable detail, not a feeling.
- When a human resolves a `needs-human` visual check, record whether they agreed with the judge's would-be verdict. That agree/override history is the evidence for eventually marking the judge **trusted** (auto-advance) — trust is earned from a track record, not assumed.

---

## Layer 2 — Harness binding (Claude Code specifics)

Not portable.

- **Locate the contract**: `unit` at `apps/<unit>/specs/dod/<issue>.md`, or `parent` at `specs/dod/<issue>.md`, resolved from `$ARGUMENTS` (`<unit> #<issue>` or `#<issue>` for the parent) or conversation context.
- **funcional / integration**: `pnpm --filter @raven/<unit> test -- <path>`. API integration needs the `_test` Postgres up — **boot it if it isn't** (`scripts/test-env.sh db`: Postgres + migrate + seed), then run. Only report `could-not-run` if it genuinely can't be stood up.
- **comportamiento (E2E)**: `pnpm --filter @raven/<unit> test:e2e <spec>`. Playwright auto-starts the dev server; API-backed flows also need the API + seed — **boot them** (`scripts/test-env.sh`). **Seam (full-stack)** needs every unit in the DAG booted together — the full-stack target. Report `could-not-run` only if that target doesn't exist yet (the known dependency on the bootable env).
- **visual render + diff**:
  - Render: capture the target with the screenshot primitive `node tools/visual/shot.mjs <url> <out.png> [selector] [w] [h]` (Playwright, retina). For an app screen, boot the frontend in test-auth mode against the seeded API (`VITE_TEST_AUTH=1`, `VITE_TEST_AUTH_USER=<seeded user with the needed role>`, `VITE_API_URL=<test API>`) and point the url at the route/state per the render recipe; for a component, point it at the unit's Storybook iframe; for non-route artifacts (emails, PDFs) render via the preview/fixture path named in the `check_ref`.
  - Reference: get the `.pen` frame screenshot via Pencil MCP (`get_screenshot` / `export_nodes`) — never Read/Grep the `.pen`.
  - Judge: Read both PNGs (this model is multimodal) and produce the structured diff per the diff config. This is the judge; no external service needed. Until you mark the judge trusted, a match routes to `needs-human` with both images attached.
- **humano evidence**: surface inline for now; route over the messaging integration (Telegram) in the autonomous phase. The portable procedure is unchanged by where it's surfaced.
- **Write back**: Edit the contract's `status` / `evidence` fields.

End your response with the verdict table and the satisfied/blocked summary, then: "Verify complete. Next: `/iterate` if anything is `red` or awaiting human sign-off; otherwise the contract is satisfied."
