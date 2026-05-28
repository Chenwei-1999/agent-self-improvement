# Agent Adapters

This skill is role-based. Use the fastest reliable worker available for each role; do not hardcode one vendor or model.

## Roles

| Role | Responsibility | Must not do |
|------|----------------|-------------|
| `history-scout` | Read one shard of conversation cards and extract evidence-backed findings. | Edit config, synthesize final rules, or infer from memory alone. |
| `docs-scout` | Check docs, policy, installation conventions, and compatibility notes. | Decide durable behavior rules. |
| `main-synthesizer` | Merge shard findings, decide scope, write final report, and own config changes. | Waste context on bulk shard scanning when scouts are available. |
| `verifier` | Run tests, installer dry-runs, schema validation, and package checks. | Rewrite source unless explicitly assigned. |

## Runtime Mappings

| Runtime | `history-scout` | `docs-scout` | `main-synthesizer` | `verifier` |
|---------|-----------------|--------------|--------------------|------------|
| Codex | `code_scout` or `GPT-5.3-Codex-Spark` when available | `docs_researcher` or a mini model | current Codex main model | local shell, test worker, or CI |
| Claude Code | `code-scout` or fast Sonnet-class worker | Haiku-class docs researcher | Opus/Sonnet-class main session | `test-runner` or local shell |
| Cursor / Continue / Aider / OpenHands | separate lightweight coding session, read-only prompt, or batch task | lightweight docs/search session | main chat/session | local shell or CI task |
| No subagents | sequential shard prompts in the same session | same session, separate pass | same session after all shard notes | local shell |

## Standard Scout Prompt

```text
You are the history-scout for one shard of conversation cards.
Read only this shard. Return:
1. Finding
2. Evidence card ids or file references
3. Proposed operating rule
4. Scope: global, project, tool, or one-off
5. Confidence: high, medium, or low

Do not edit files. Do not write final rules. Do not infer from memory alone.
```

## Selection Rule

Choose the cheapest worker that can accurately read and classify the shard. Save the strongest model for synthesis, conflict resolution, risky writes, and final user-facing decisions.
