# Operating Rules

These are examples of durable rules that commonly emerge from conversation-history audits. Treat them as a taxonomy, not as automatic installs.

## Evidence First

Answer status questions from live evidence: files, logs, schedulers, configs, tests, or cited docs. Memory and summaries can route the search, but they should not replace current inspection when the fact may drift.

## Scope Binding

Keep rules tied to their scope:

- Global rules belong in user-level agent config.
- Project rules belong in that project's AGENTS.md or CLAUDE.md.
- Skill-specific behavior belongs in the skill.
- One-off task details belong in the report, not durable config.

## Subagents for Coverage

Use subagents for broad, cheap, read-only work:

- Conversation-card scanning.
- Codebase file discovery.
- Documentation lookup.
- Mechanical verification.

The main agent keeps ownership of synthesis, risky writes, config edits, and final user-facing decisions.

## Compute Discipline

For research and Slurm-heavy work, avoid heavy login-node computation. Submit jobs through the scheduler, monitor concrete state, and cancel stale, duplicated, dominated, or no-longer-useful runs when that is in scope.

## Status Discipline

For long-running tasks, report concrete state before interpretation:

- command or job id
- queue/runtime state
- latest artifact or log
- current gate
- next action

Avoid vague "still running" updates when better evidence is cheap to collect.

## Preflight and Verification

Before expensive work, check paths, configs, credentials, environment, storage, and scheduler constraints. After changes, run the narrowest meaningful tests and report exactly what passed or could not be run.

## Source-Grounded Writing

For papers, CVs, rebuttals, websites, and grant material, ground edits in actual source documents. Do not invent metrics, publications, reviewer claims, or experiment results.

## Sync Boundaries

When the user asks for push, sync, or install, finish with the real operation if permissions and credentials allow it. Report exact destination and verification evidence.

## Privacy and Secrets

Conversation audits may touch private paths, credentials, unpublished work, and personal data. Redact secrets before sharing outputs beyond the local machine. Never send private history to an external service unless the user explicitly approves that data flow.

## Resume Behavior

When continuing after interruption, recover current state from files, logs, tests, and scheduler output. Do not restart from stale assumptions.

