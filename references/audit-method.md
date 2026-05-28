# Audit Method

This method is for extracting agent-improvement rules from real conversation history. It is intentionally evidence-first and subagent-friendly.

## Inputs

Useful inputs include:

- Codex rollout summaries, JSONL sessions, memories, AGENTS.md files, and local logs.
- Claude Code project conversations, CLAUDE.md files, and transcript exports.
- User-provided chat exports from other agents.
- Existing rule files, skill docs, and project-specific conventions.

Prefer original conversation data when available. Summaries are useful for routing, but they should not be the only source for durable rules.

## Step 1: Build Compact Cards

Each card should be small enough for cheap agents to scan quickly. A good card contains:

- Stable id: source, session id, turn id, and timestamp when available.
- User request: compact paraphrase or short quote.
- Agent action: what the agent actually did.
- Correction signal: user correction, failure, blocked state, repeated friction, or successful pattern.
- Evidence: file path, command, job id, config path, or output snippet.
- Candidate lesson: one sentence.

Use `scripts/extract_conversation_cards.py` for local Codex and Claude histories. It writes Markdown shard files and a JSON manifest.

## Step 2: Shard for Agent Roles

Shard by source and approximate size. Prefer many small shards over one huge shard. The main agent should dispatch independent read-only jobs such as:

```text
Scan this shard of conversation cards. Extract repeated agent mistakes,
explicit user corrections, and durable behavior rules. Return:
1. Finding
2. Evidence card ids
3. Proposed rule
4. Scope: global, project, tool, or one-off
5. Confidence: high, medium, low
```

Subagents should not write config files. They gather evidence and propose rules.

Use `references/agent-adapters.md` to map these roles onto Codex, Claude Code, or another coding agent. Codex may use `GPT-5.3-Codex-Spark`; Claude Code may use a Sonnet-class code scout; generic agents can run the same prompt in separate lightweight sessions or sequentially.

## Step 3: Synthesize

The main agent merges shard findings and removes noise.

Keep:

- Corrections repeated across multiple sessions.
- Rules that prevent expensive failures.
- Rules that change a concrete decision point.
- Preferences the user explicitly asked to persist.

Discard:

- One-off task details.
- Rules that only restate generic diligence.
- Advice that conflicts with higher-priority system or project instructions.
- Anything based on a single weak example unless the risk is high.

## Step 4: Install Carefully

Install rules at the narrowest durable location:

- Project behavior: project `AGENTS.md` or `CLAUDE.md`.
- Global agent behavior: user-level AGENTS/CLAUDE configuration.
- Reusable workflow: a skill package.
- Historical preference: memory note.

When editing shared config, preserve existing rules and add the smallest clear patch. For cross-tool parity, update both Codex and Claude instructions when the rule should affect both tools.

## Step 5: Verify

Verification can be lightweight:

- Re-run package tests.
- Ask a fresh subagent to use the skill on a small fixture.
- Check that generated rules include evidence references.
- Confirm installers target the expected directories.

Do not call the improvement done until the new behavior has at least one concrete verification path.
