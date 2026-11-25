# DoD contract (shared schema reference)

Canonical schema for the Definition-of-Done contract — the artifact that carries state between every v2 phase. `/clarify` writes it; `/author-checks`, `/build`, `/verify`, `/iterate`, `/sync-specs` read and advance it. Defined once here; skills cite it instead of restating. Oracles are defined in [`_oracles.md`](_oracles.md).

**The contract is the verifiable annex, not the record of understanding.** What we're doing and *why* — the restatement, the grounding map, the decisions — lives in the per-issue **brief** ([`_brief.md`](_brief.md)). The contract links it via `brief:` and stays lean: scope, criteria, and verification state. The brief says WHY; the contract says WHAT-must-be-true and carries `status` / `check_ref` / `evidence`. They are kept consistent by the brief's live-update rule: any definition change updates the brief first, then reconciles the affected criteria here (which re-opens approval).

A contract has one of two **kinds**:

- `unit` — governs one workflow unit (app/package). Path: `apps/<unit>/specs/dod/<issue>.md` (or `packages/<unit>/...`). Every issue has at least one.
- `parent` — governs a multi-unit issue: the child DAG + the cross-unit **seam** criteria + the rollup rule. Path: `specs/dod/<issue>.md` (workspace root). Exists **only** for multi-unit issues; a single-unit issue has no parent.

The issue number is shared by all contracts of one issue. Filenames use the bare number (`267.md`).

## Unit contract

```markdown
---
issue: "#267"
kind: unit
unit: apps/api
parent: specs/dod/267.md      # omit for single-unit issues
brief: specs/dod/267.brief.md # the per-issue narrative (understanding/grounding/decisions)
summary: >
  One-line orientation for THIS unit's slice. The full intent lives in the brief.
scope_in: [ ... ]
scope_out: [ ... ]
durable_specs_touched: [ apps/api/docs/api.md, ... ]
spec_contradictions: []       # or each conflict + its agreed resolution
approved_by: ""               # GATE — empty blocks /author-checks and /build for this unit
approved_at: ""
---

## Acceptance criteria

- id: C1
  what: "<one observable claim>"
  oracle: funcional           # see _oracles.md
  check_ref: ""               # filled by /author-checks
  status: pending             # pending → red → green | needs-human → approved
  evidence: ""                # filled by /verify
```

## Parent contract

```markdown
---
issue: "#267"
kind: parent
title: "<short>"
brief: specs/dod/267.brief.md # the per-issue narrative (shared with the children)
summary: >
  One-line cross-unit orientation. Full intent + cross-unit decisions live in the brief.
units:                        # children + dependency edges = the DAG
  - unit: apps/api
    contract: apps/api/specs/dod/267.md
    depends_on: []
  - unit: apps/branch
    contract: apps/branch/specs/dod/267.md
    depends_on: [apps/api]    # branch consumes api's surface → api lands first
execution:                    # the DAG flattened into ordered waves
  - wave: 1
    parallel: [apps/api]      # units sharing a wave have no edge between them → run concurrently
  - wave: 2
    parallel: [apps/branch]
approved_by: ""               # GATE
approved_at: ""
---

## Seam criteria

Cross-unit behavior that belongs to no single unit. Verified after every unit in
the DAG is satisfied, against the full-stack environment (all involved units booted
together — see _oracles.md `comportamiento`).

- id: S1
  what: "The invoice status api sets on authorize is the status branch renders in Mis Facturas."
  oracle: comportamiento
  env: full-stack
  check_ref: ""
  status: pending
  evidence: ""

## Rollup

The issue is DONE when every unit contract is satisfied (all its criteria
green/approved) AND every seam criterion is green/approved.
```

## Execution / orchestration

The parent contract **is** the orchestration spec — passive data, not an agent.
Whoever walks it is the **orchestrator**: in the manual phase, the human; in the
autonomous phase, an orchestrator agent. There is no "parent agent" and no parent
`/build` — the parent only takes `/author-checks` (seam checks) and `/verify` (seam
verification). All `/mockup`, `/architect`, `/plan`, `/build` happen per unit.

Walk order:

1. For each wave in `execution`, in sequence:
   - run the per-unit pipeline (`/author-checks → /build → /verify ⇄ /iterate`) for
     every unit in the wave; units within a wave are independent and parallelizable.
   - do not start a wave until every unit contract in the prior wave is satisfied.
2. After the last wave: `/author-checks #<issue>` then `/verify #<issue>` on the
   **parent**, exercising the seam criteria against the full-stack env.
3. The issue is done per the Rollup rule.

## Status lifecycle

Per criterion: see _oracles.md. A contract is **satisfied** when all its criteria
are green or approved. The `approved_by` gate is independent of criterion status — it
gates whether the build phase may start at all.
