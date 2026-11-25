# Oracle taxonomy (shared reference)

Canonical definition of the four **oracles** — the things that prove an acceptance criterion true. This file is the single source. The skills that touch oracles cite it instead of redefining: `/clarify` assigns the oracle, `/author-checks` writes the check for it, `/verify` runs the check, `/iterate` reads the verdict. If this taxonomy changes, it changes here once.

Each acceptance criterion in a DoD contract (`specs/dod/<issue>.md`) carries **exactly one** oracle. The oracle decides two things: how the criterion gets verified, and how much autonomy is safe around it.

| oracle | what it proves | how it is checked | author-checks produces | autonomy |
|---|---|---|---|---|
| `funcional` | pure logic / data correctness | unit or integration test (Vitest) | a failing (red) test asserting the criterion | machine — loop iterates alone |
| `comportamiento` | a multi-step flow end-to-end | E2E / integration against a running, seeded system | a failing E2E spec + any seed it needs | machine — loop iterates alone |
| `visual` | appearance vs. the mockup | render the screen, screenshot, diff against the `.pen` frame via a multimodal judge | the frame↔screen/state mapping + diff config | machine, noisier — gate behind human until the judge is trusted |
| `humano` | subjective judgment no machine can yet make (copy tone, UX feel) | a human looks at packaged evidence and decides | the evidence to surface (screenshot, output) | human-only — loop proposes, waits for approval |

**Seam criteria** (cross-unit behavior in a `parent` contract — see [`_contract.md`](_contract.md)) are always `comportamiento` with `env: full-stack`: the check boots every involved unit together and drives the behavior across the boundary. A single-unit `comportamiento` check boots only that unit plus its seeded deps.

## Choosing an oracle (for `/clarify`)

- Prefer the **most machine-verifiable** oracle a criterion admits. `humano` is the escape hatch, not a default — every `humano` criterion is a place the loop cannot run alone, so each one is a deliberate, flagged choice.
- A criterion that needs a running system (DB, API, multiple modules) is `comportamiento`, not `funcional` — the distinction is whether a unit test in isolation can prove it.
- `visual` criteria must name the **screen + state** (e.g. "invoice-email / empty"), because the check is a frame-specific diff. A criterion about *what data shows* is `funcional`/`comportamiento`; one about *how it looks* is `visual`.
- A **new or restyled screen always yields a `visual` criterion, authored at `/clarify`** — never deferred to the mockup phase (mockup *realizes* the frame the criterion names; the criterion itself is clarify's). This applies to appearance only: a change to *what a screen shows/says* stays `funcional`/`comportamiento`, with no visual criterion.
- One observable claim per criterion. If a statement needs two different oracles to prove, it is two criteria.
- A **no-regression / suite-health** criterion is **baseline-relative by nature**: its truth is "introduces no new failures vs. `base`", never "the whole suite is green". Phrase its `what` relative to the change in `/clarify` ("no new regressions introduced by #<issue>") and let `/author-checks` operationalize it as a baseline delta — a test already red on `base` is not this issue's regression.

## Status lifecycle (for `/verify` and `/iterate`)

`pending` → (after `/author-checks`) `red` → (after `/build` + `/verify`) `green`, or `needs-human` for `humano`/un-trusted-`visual` → `approved` once the human signs off. The contract is satisfied when every criterion is `green` or `approved`.
