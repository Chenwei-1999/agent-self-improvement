---
name: self-improvement
description: Use when the user asks an agent to learn from agent conversation history, chat transcripts, rollout logs, or exported sessions; extract recurring corrections; improve operating rules; or update agent instructions.
---

# Self-Improvement Skill

Use this skill when the user asks to audit past chats, extract durable lessons,
improve the current agent itself, update this self-improvement skill, or compare
recurring failures across agent transcripts.

## Activation Contract

Use for:

- Auditing actual conversation history, transcripts, rollout summaries, or chat exports.
- Finding repeated user corrections, repeated failures, durable preferences, and useful success patterns.
- Proposing evidence-backed updates to the current agent's self-improvement
  behavior or this skill package.

Do not use for:

- One-off code review, ordinary debugging, or generic advice with no conversation-history evidence.
- Installing rules from memory alone when the user asked for a history audit.
- Proposing project instruction files, memory notes, or global config writes
  unless the user explicitly asked for that broader destination.
- Silently rewriting durable behavior. Show proposed updates unless the user explicitly asked for installation.

Before writing any durable rule, collect source evidence and identify whether it
belongs to the agent itself. Treat project-specific, global, and memory-like
findings as report-only unless the user explicitly expands the scope.

## Default Full-History Scan

Do not stop for an upfront scope question when normal defaults are usable.
Default to scan all discoverable agent conversation history: Codex sessions,
Claude projects, Gemini history/log exports, and generic transcript folders.
If the user named a narrower project, time range, or transcript folder, use that
constraint; otherwise gather first and ask later.

## Installation Decision Gate / Agent-Self Update Gate

Ask the user which rule candidates to install into the agent itself before
writing any durable rule. Present the evidence-backed candidates with
recommended scopes, then offer clear destinations:

- report only: summarize candidates and do not install.
- Agent itself: patch this skill package or the current agent's installed
  self-improvement behavior.

Only propose updates to the agent itself by default. Do not propose project instruction files, memory notes, or global config writes unless the user explicitly asks for that broader destination.

Only install the candidates the user selected. If the user asks for a default,
prefer the narrowest durable destination that will affect the next relevant
agent decision.

The default interaction model is a single user interaction after synthesis:
present the update recommendations, evidence, scopes, destinations, and warnings,
then request confirmation before writing durable rules. Do not ask preliminary
questions unless history access is blocked or the request is ambiguous in a way
that would make scanning unsafe.

### Global or Systemic Change Warning

Before changing global config, memory, reusable skills, or any rule that affects
multiple projects or future sessions, warn the user about the scope and wait
unless the user's prompt explicitly authorizes global or systemic changes. The
warning must name the destination and expected blast radius.

## Adapter Rule

Use roles, not one hardcoded model:

- `history-scout`: fastest read-only coding worker for shard scans.
- `docs-scout`: cheap docs/search worker for documentation and policy checks.
- `main-synthesizer`: strongest available main agent for evidence integration and durable rule decisions.
- `verifier`: local shell or CI worker for install dry-runs, runtime discovery, and package smoke checks.

For Codex this may map `history-scout` to `code_scout` / `GPT-5.3-Codex-Spark`. For Claude Code this may map to a `code-scout` or fast Sonnet-class worker, with Haiku-class agents for docs. For Gemini CLI, use Gemini skills plus separate read-only sessions, custom commands, or sequential shard passes when subagents are unavailable. For other coding agents, use the closest read-only workers or run shard prompts sequentially. See `references/agent-adapters.md`.

The central pattern is:

1. Turn conversation history into compact evidence cards.
2. Fan those cards out to cheap, read-only subagents.
3. Synthesize repeated corrections into durable operating rules.
4. Install only evidence-backed updates to the agent itself.

Do not rely on manual keyword search alone. The value of this skill is broad coverage: subagents scan many shards of actual dialogue, surface failures and user corrections, and the main agent owns the final judgment.

## Workflow

1. Gather default history.
   - Scan all discoverable local agent logs, exported transcripts, project notes, Codex sessions, Claude projects, Gemini exports, and user-provided folders.
   - Only narrow the source, time range, or project when the user explicitly requested that constraint.
   - Avoid an upfront clarification unless access is blocked or scanning would be unsafe.

2. Extract cards.
   - Prefer `scripts/extract_conversation_cards.py` for local histories and exported transcripts. It has native Codex and Claude readers plus a generic reader for Gemini, Cursor, Continue, Aider, OpenHands, and other transcript exports.
   - Keep cards compact: user request, assistant response summary, tool evidence, corrections, failures, and follow-up outcome.
   - Avoid exposing secrets. Redact API keys, tokens, credentials, and private paths if the output may leave the machine.

3. Dispatch subagents.
   - Use the adapter roles above; do not assume Codex-only model names.
   - Give each subagent one shard and one narrow rubric.
   - Ask for concrete evidence: session id, card id, short quote or paraphrase, observed failure, proposed rule.
   - Do not delegate final synthesis, risky writes, or decisions that require full conversation context.

4. Synthesize.
   - Cluster repeated corrections and failures.
   - Separate global rules from project-specific habits.
   - Prefer small rules that change behavior at the moment of decision.
   - Drop one-off preferences unless the user explicitly wants them preserved.

5. Install or report.
   - Ask the user which agent-self update candidates to install before writing files.
   - Warn and get permission before global or systemic installs unless already authorized.
   - For Codex, Claude, Gemini CLI, or generic agents, propose patches to this skill package or that runtime's installed copy of the skill.
   - Do not propose edits to `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, memory, or global config unless the user explicitly asks for those destinations.
   - For portable use, install this skill with `scripts/install_skill.py`.
   - Never silently rewrite global config. Show the rule set and make the write explicit unless the user already asked for installation.

## Useful Commands

Install from GitHub by giving this line to a local coding agent:

```text
Install this skill: https://github.com/Chenwei-1999/agent-self-improvement
```

For agents with a skill installer:

```text
$skill-installer install https://github.com/Chenwei-1999/agent-self-improvement
```

For Gemini CLI:

```bash
gemini skills install https://github.com/Chenwei-1999/agent-self-improvement
```

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
python3 scripts/install_skill.py --target gemini --force
python3 scripts/install_skill.py --target generic --force
python3 scripts/install_skill.py --target custom --custom-dir ~/.my-agent/skills/self-improvement --force
```

`--force` replaces the existing installed skill directory. Use `--dry-run` first when installing into global agent locations.

## References

- `references/audit-method.md`: detailed audit method and subagent prompt templates.
- `references/agent-adapters.md`: role mappings for Codex, Claude Code, Gemini CLI, and generic coding agents.
- `references/operating-rules.md`: rule taxonomy and examples from real Codex/Claude self-improvement audits.
