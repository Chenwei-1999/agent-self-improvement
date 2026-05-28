# Audit Method

This method is for extracting agent-improvement rules from real conversation history. It is intentionally evidence-first and subagent-friendly.

## Inputs

Useful inputs include:

- Codex rollout summaries, JSONL sessions, installed skill files, and local logs.
- Claude Code project conversations, installed skill files, and transcript exports.
- User-provided chat exports from other agents.
- Existing rule files, skill docs, and project-specific conventions.

Prefer original conversation data when available. Summaries are useful for routing, but they should not be the only source for durable rules.

Default to a full-history scan. Do not stop for an upfront scope question when
local defaults are available: scan Codex sessions, Claude projects, Gemini
history/log folders, and generic transcript exports first. Narrow the scan only
when the user named a project, time range, or source.

## Step 1: Build Compact Cards

Each card should be small enough for cheap agents to scan quickly. A good card contains:

- Stable id: source, session id, turn id, and timestamp when available.
- User request: compact paraphrase or short quote.
- Agent action: what the agent actually did.
- Correction signal: user correction, failure, blocked state, repeated friction, or successful pattern.
- Evidence: file path, command, job id, config path, or output snippet.
- Candidate lesson: one sentence.

Use `scripts/extract_conversation_cards.py` for local Codex, Claude, Gemini, and
generic histories. It writes Markdown shard files and a JSON manifest.

A rendered shard entry looks like this:

```markdown
## codex-e3e3d7229233

- source: codex
- role: tool
- type: function_call
- file: /home/user/.codex/sessions/2025-11-01-<uuid>/rollout.jsonl:2
- session: aaaaaaaa-bbbb-cccc-dddd-111122223333
- ts: 2025-11-01T12:00:10Z

[tool:shell] {"command": ["bash", "-lc", "ls /tmp"]}
```

`role: tool` carries Codex `function_call` / `function_call_output` /
`local_shell_call` events, so scout prompts can rely on the `role` field to
separate user/assistant text from agent actions. The `session` and `ts` lines
let scouts cluster cards from the same session and order them in time.

## Step 2: Shard for Agent Roles

Shard by source and approximate size. Prefer many small shards over one huge shard. The main agent should dispatch independent read-only jobs such as:

```text
Scan this shard of conversation cards. Extract repeated agent mistakes,
explicit user corrections, and durable behavior rules. Return:
1. Finding
2. Evidence card ids
3. Proposed rule
4. Scope: agent itself or report-only
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

Ask the user which proposed rules to install before writing any durable file.
Show the proposed rules, evidence references, recommended scope, and the
available destinations:

- report only: no install.
- Agent itself: patch this skill package or the current runtime's installed copy
  of it.

Install rules only into the agent itself by default. Treat project files, memory, and global config as out of scope unless the user explicitly requests those destinations.

This should normally be the only user interaction: gather history, synthesize
update recommendations, then request confirmation for the selected installs.

Warn before global or systemic changes. If a proposed write affects global
config, memory, reusable skills, or multiple projects, state the destination,
blast radius, and reason. Continue only with explicit user permission or when
the original user prompt already authorized that class of change.

When editing the skill, preserve existing rules and add the smallest clear patch.
For cross-tool parity, update the shared skill behavior rather than divergent
project or global instruction files.

## Step 5: Verify

Verification can be lightweight:

- Re-run installer dry-runs or runtime discovery checks.
- Ask a fresh subagent to use the skill on a small fixture.
- Check that generated rules include evidence references.
- Confirm installers target the expected directories.

Do not call the improvement done until the new behavior has at least one concrete verification path.
