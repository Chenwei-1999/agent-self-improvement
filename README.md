<p align="center">
  <img src="assets/banner.png" width="900" alt="Agent Self-Improvement banner">
</p>

<h1 align="center">Agent Self-Improvement</h1>

<p align="center">
  <b>Turn real conversation history into better agent behavior.</b>
</p>

<p align="center">
  <a href="https://developers.openai.com/codex/skills"><img src="https://img.shields.io/badge/Codex-Skill-111827?style=for-the-badge&logo=openai&logoColor=white" alt="Codex Skill"></a>
  <img src="https://img.shields.io/badge/Claude-Code-6b46c1?style=for-the-badge" alt="Claude Code compatible">
  <img src="https://img.shields.io/badge/Gemini-CLI-4285f4?style=for-the-badge" alt="Gemini CLI compatible">
  <img src="https://img.shields.io/badge/Scouts-Role--Based-0f766e?style=for-the-badge" alt="Role-based scout agents">
  <img src="https://img.shields.io/badge/Install-Copy--Paste--Prompt-f59e0b?style=for-the-badge" alt="Copy-paste install">
</p>

Self-Improvement is a portable agent skill for turning real conversation
history into better behavior for the agent itself. It is designed for
SKILL.md-compatible agents, including Gemini CLI, Codex, Claude Code, and
generic agents that support filesystem-installed skills.

The core advantage is coverage: shard conversation history into compact cards, let fast read-only scout subagents scan many shards in parallel, then spend the main agent's stronger reasoning on synthesis, rules, and safe installation.

## Quick Start

Give this GitHub link to your coding agent:

```text
Install this skill: https://github.com/Chenwei-1999/agent-self-improvement
```

That's the intended install path. The repo includes the skill, installer, and compatibility notes, so a local coding agent can clone it, run the installer, verify target discovery, and report where it landed.

If your agent supports `skill-installer`, the equivalent single command is:

```text
$skill-installer install https://github.com/Chenwei-1999/agent-self-improvement
```

For Gemini CLI, use Gemini's own skill installer instead of Codex:

```bash
gemini skills install https://github.com/Chenwei-1999/agent-self-improvement
```

## Why It Exists

Most agent "self-improvement" drifts into vibes or hand-picked examples. This package keeps it grounded:

- Uses actual agent conversation history, including Codex sessions, Claude projects, Gemini exports, and generic transcript folders.
- Dispatches role-based scout subagents for fast, low-cost coverage across many shards.
- Preserves the main agent as the owner of final judgment and config writes.
- Produces scoped updates for this skill or the current agent's installed
  self-improvement behavior.
- By default, scan all discoverable agent histories before asking the user for
  decisions.
- Before writing any rule, ask the user which candidates to install and whether
  they should update the agent itself or stay as report-only output.
- It only updates the agent itself by default, not project instruction files, memories, or global config.
- The only required user interaction is the final update proposal: review the
  recommendations, destinations, and warnings, then confirm what to install.
- Warn before global or systemic changes unless the user's prompt explicitly
  allows global config, memory, reusable-skill, or cross-project writes.

## Agent Adapters

The skill does not require one specific model. It uses roles and maps them to whatever your coding agent supports.

| Role | Job | Codex adapter | Claude Code adapter | Gemini CLI adapter | Generic coding agents |
|------|-----|---------------|---------------------|--------------------|-----------------------|
| `history-scout` | Scan conversation-card shards | `code_scout` / `GPT-5.3-Codex-Spark` | `code-scout` or a fast Sonnet-class subagent | Gemini skill plus separate read-only session or sequential shard pass | fastest read-only coding worker |
| `docs-scout` | Check docs, policy, install conventions | `docs_researcher` / mini model | Haiku-class docs researcher | Gemini docs/search session | cheap docs/search worker |
| `main-synthesizer` | Merge evidence and decide rules | current main agent | Opus/Sonnet-class main agent | primary Gemini CLI session | strongest available coding agent |
| `verifier` | Run install dry-runs, skill discovery, and smoke checks | local shell or CI | local shell or CI | `gemini skills list`, local shell, or CI | local shell / CI worker |

If a runtime has no subagents, run the same shard prompts sequentially. The quality goal is evidence coverage; the optimization is parallelism.

## How It Works

```text
conversation history
  Codex sessions, Claude projects, Gemini exports, generic transcripts
        |
        v
compact cards + shards
  card id, user correction, evidence, candidate lesson
        |
        v
history-scout subagents
  shard A -> repeated failures
  shard B -> successful patterns
  shard C -> missing rules
        |
        v
main agent synthesis
  evidence ledger -> agent-self updates -> installed skill package
```

The scouts do the wide scan. The main agent does the judgment.

<details>
<summary>Manual fallback</summary>

If you need to install without an agent:

```bash
git clone https://github.com/Chenwei-1999/agent-self-improvement.git
cd agent-self-improvement
python3 scripts/install_skill.py --target all --dry-run
python3 scripts/install_skill.py --target all --force
```

Install only one target:

```bash
python3 scripts/install_skill.py --target codex --force
python3 scripts/install_skill.py --target claude --force
python3 scripts/install_skill.py --target gemini --force
python3 scripts/install_skill.py --target generic --force
python3 scripts/install_skill.py --target custom --custom-dir ~/.my-agent/skills/self-improvement --force
```

Targets:

- Codex: `~/.codex/skills/self-improvement`
- Claude: `~/.claude/skills/self-improvement`
- Gemini CLI: `~/.gemini/skills/self-improvement`
- Generic local agents: `~/.agents/skills/self-improvement`
- Custom runtimes: any directory passed with `--custom-dir`

`--force` replaces the existing installed directory. Run the dry-run command first when installing into global agent locations.

Generic agent support assumes the runtime discovers skills from `~/.agents/skills/...` or lets you point it at that folder. For Cursor, Continue, Aider, OpenHands, or another runtime with its own convention, use `--target custom --custom-dir <skill-dir>`.

</details>

## First Use

Create compact conversation cards across local agent histories:

```bash
python3 scripts/extract_conversation_cards.py --out conversation-audit/cards
```

By default this reads Codex sessions, Claude projects, and safe conventional
generic history roots such as Gemini `history` and `tmp` folders when present.
Override Codex and Claude with `--codex-root` and `--claude-root` when using
exported history or a different machine layout.

For additional Gemini CLI or other coding-agent exports, pass one or more
generic roots:

```bash
python3 scripts/extract_conversation_cards.py \
  --generic-root /path/to/transcripts \
  --max-files 200 \
  --max-bytes 2000000 \
  --out conversation-audit/cards
```

Extraction writes Markdown shard files plus `manifest.json`, which records roots, counts, and shard paths for later verification.

Then ask your main agent to dispatch subagents over the shard files:

```text
Use the self-improvement skill. Scan conversation-audit/cards with subagents,
find repeated user corrections and agent failures, then propose durable rules.
```

Expected outputs:

- Evidence ledger: where each finding came from.
- Rule candidates: agent-self updates, plus out-of-scope observations when useful.
- Single user confirmation: which update recommendations to install, skip, or
  keep as report only.
- Global/systemic warning: scope and destination when a selected install affects
  multiple projects or future sessions.
- Proposed installs: patch this skill package or the current agent's installed
  self-improvement behavior.
- Verification plan: how to test the new behavior before calling it done.

## What You Get After Running It

Installing the skill only makes the workflow discoverable. The actual
self-improvement effect happens after you extract cards, audit them, and install
the resulting rules.

The normal output is:

- `conversation-audit/cards/...`: compact shard files for scout agents or
  sequential review.
- `manifest.json`: source roots, card counts, and shard paths.
- Evidence ledger: card ids, source files, and observed correction signals.
- Rule candidates: scoped to the agent itself by default; project, memory, and
  global findings are reported as out-of-scope unless explicitly requested.
- Install decision prompt: the single required user interaction, asking which
  candidates should be installed, skipped, or reported only.
- Scope warning: call out global or systemic changes before any write that
  affects future sessions or multiple projects.
- Install proposal: exact edits for this skill package or the current agent's
  installed copy of it.

## What Good Looks Like

A good audit does not say "be more careful." It says:

- When a user asks for repo status, inspect live files and scheduler state before summarizing.
- When a long-running job is active, report concrete state, elapsed time, and next gate.
- When history is large, use subagents to scan shards and keep the main agent on synthesis.
- When a lesson should persist, encode it in the shared skill behavior so Codex,
  Claude, Gemini, and generic agents can consume the same agent-self update.

## Package Layout

```text
self-improvement/
  INSTALL_PROMPT.md
  SKILL.md
  README.md
  agents/openai.yaml
  assets/banner.png
  assets/self-improvement-hero.png
  references/audit-method.md
  references/agent-adapters.md
  references/operating-rules.md
  scripts/extract_conversation_cards.py
  scripts/install_skill.py
```

## Design Notes

The skill intentionally separates high-volume scanning from high-stakes synthesis. Role-based scout agents can cheaply read and classify lots of history; the main agent still owns the final rules, user-facing explanation, and any writes to the installed skill.

This keeps cost low without lowering quality.

The original generated hero image is kept at `assets/self-improvement-hero.png`; the README uses `assets/banner.png` because the strongest skill READMEs lead with a polished banner and keep process details readable in Markdown.
