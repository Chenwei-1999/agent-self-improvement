---
name: self-improvement
description: Use when an agent should improve its own operating rules by auditing Codex, Claude, or other conversation history with subagents and evidence-backed synthesis.
---

# Self-Improvement Skill

Use this skill when the user asks to audit past chats, extract durable lessons, improve agent behavior, update AGENTS.md or CLAUDE.md, or compare recurring failures across Codex, Claude, and other agent transcripts.

The central pattern is:

1. Turn conversation history into compact evidence cards.
2. Fan those cards out to cheap, read-only subagents.
3. Synthesize repeated corrections into durable operating rules.
4. Install only the rules that are evidence-backed and scoped.

Do not rely on manual keyword search alone. The value of this skill is broad coverage: subagents scan many shards of actual dialogue, surface failures and user corrections, and the main agent owns the final judgment.

## Workflow

1. Define scope.
   - Sources: Codex logs, Claude logs, exported transcripts, project notes, or a user-provided folder.
   - Time range: all history, recent history, or a specific project.
   - Output: report only, proposed rules, memory note, AGENTS.md patch, CLAUDE.md patch, or installer-ready skill update.

2. Extract cards.
   - Prefer `scripts/extract_conversation_cards.py` for Codex and Claude local histories.
   - Keep cards compact: user request, assistant response summary, tool evidence, corrections, failures, and follow-up outcome.
   - Avoid exposing secrets. Redact API keys, tokens, credentials, and private paths if the output may leave the machine.

3. Dispatch subagents.
   - Use cheap models for broad scanning: code-scout style agents for evidence gathering, docs-researcher style agents for docs and policy lookup.
   - Give each subagent one shard and one narrow rubric.
   - Ask for concrete evidence: session id, card id, short quote or paraphrase, observed failure, proposed rule.
   - Do not delegate final synthesis, risky writes, or decisions that require full conversation context.

4. Synthesize.
   - Cluster repeated corrections and failures.
   - Separate global rules from project-specific habits.
   - Prefer small rules that change behavior at the moment of decision.
   - Drop one-off preferences unless the user explicitly wants them preserved.

5. Install or report.
   - For Codex, propose edits to `AGENTS.md`, a memory update, or a skill package.
   - For Claude, propose mirror edits to `CLAUDE.md`.
   - For portable use, install this skill with `scripts/install_skill.py`.
   - Never silently rewrite global config. Show the rule set and make the write explicit unless the user already asked for installation.

## Useful Commands

Create conversation-card shards:

```bash
python3 scripts/extract_conversation_cards.py --out conversation-audit/cards
```

Preview installation targets:

```bash
python3 scripts/install_skill.py --target all --dry-run
```

Install for one agent family:

```bash
python3 scripts/install_skill.py --target codex --force
python3 scripts/install_skill.py --target claude --force
python3 scripts/install_skill.py --target agents --force
```

`--force` replaces the existing installed skill directory. Use `--dry-run` first when installing into global agent locations.

## References

- `references/audit-method.md`: detailed audit method and subagent prompt templates.
- `references/operating-rules.md`: rule taxonomy and examples from real Codex/Claude self-improvement audits.
