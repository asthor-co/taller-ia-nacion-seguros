# Issue Brief (shared reference)

The **brief** is the single per-issue source of *intent* — what we're doing, why, and what it builds on. It is the narrative companion to the DoD contracts: the contracts say WHAT must be true and carry verification state; the brief says WHY and holds the understanding the contracts derive from.

One brief per issue (issue-level, even for multi-unit), at `specs/dod/<issue>.brief.md`. `/clarify` writes and owns it.

## Why it is separate from the DoD contract

Different lifecycle and audience:

- The **DoD contract** is mechanical and mutable — `author-checks` / `verify` / `iterate` rewrite `check_ref` / `status` / `evidence` constantly. Machine-read, machine-mutated.
- The **brief** is narrative and stable — it changes only when the issue's *definition* changes. Read by humans and by `design` / `plan` / `build` for intent.

Keeping them apart stops status churn from polluting the narrative and keeps the contract reliably machine-parseable. They are two semantically different things that happen to live side by side.

## Contents

```markdown
# Brief — #<issue> <title>

## Understanding
Self-contained restatement: what the whole issue delivers, for whom, and the shape of
the change. As many paragraphs as it takes. A future session must grasp the goal from
this alone — never the (transient, gitignored) intake, never the chat.

## Grounding
The load-bearing map of the EXISTING system the change builds on — promoted from the
intake so it survives: where the relevant code/specs live, what is reused, what exists
today, the present-tense facts that shaped the decisions. Not exhaustive — the pointers
a future /architect or /build would otherwise have to rediscover, plus the verified
feasibility facts (see /clarify grounding).

## Decisions
One entry per resolved blocker / non-obvious choice — the WHY behind the criteria.

- id: D1
  question: "<the blocker /clarify resolved>"
  decision: "<what was decided>"
  why: "<rationale>"
  rejected: "<alternatives + why not — omit if none>"

## DoD contracts (the verifiable annex)
- parent:     specs/dod/<issue>.md            # multi-unit only
- apps/api:   apps/api/specs/dod/<issue>.md
- apps/admin: apps/admin/specs/dod/<issue>.md
```

## The live-update rule (non-negotiable)

**Any change to the issue's definition — however minimal — updates the brief in the
same step, before proceeding.** A new decision, a reworded scope, a flipped assumption,
a dropped or added criterion: the brief is updated the *moment* it changes, never
deferred. The brief is the source of intent and the DoD criteria derive from it, so on
any change you update the brief **first**, then reconcile the affected criteria — which
re-opens approval (see [`_contract.md`](_contract.md)).

Making a change "official" touches **three** things, not just the decision — otherwise
it lands as unexplained drift a later `/verify` correctly flags:
1. **The brief** — a `## Decisions` entry (the what + why).
2. **`scope_in`** — if the change was outside scope, the contract's scope is widened to
   include it (or it stays out-of-scope drift).
3. **A criterion** — if the change introduces *behavior*, it gets its own acceptance
   criterion so `/verify` checks it. Code that no criterion covers is unverified drift,
   not a delivered change. Adjusting an existing criterion counts; new behavior needs a
   new one.

**This is mandatory — not a suggestion, not a question.** Once a definition change is
agreed with the human, the phase you are *currently in* updates the brief and reconciles
the affected criteria **in place**, before proceeding. You do not ask whether to update
it; you do not defer it; and you do **NOT** bounce to a separate `/clarify` invocation.
`/clarify` originates the brief, but **any phase** that agrees a change writes it — that
is what keeps the brief current continuously.

The only guardrail: never change the definition **unilaterally**. A phase surfaces the
change, gets the human's agreement, and *then* the update is obligatory. Re-approval is
simply that agreement to the delta — show what changed; you need not re-present the whole
contract for a small edit.

This freshness is **NOT** `/sync-specs`' job. `/sync-specs` runs once, post-verify, and
only **graduates** the *lasting* decisions from the brief into durable unit specs (so
they outlive the issue). It is not — and must never become — the mechanism that keeps
the brief in sync during the work. The brief is kept live by the rule above, in every
phase, at the instant of change.
