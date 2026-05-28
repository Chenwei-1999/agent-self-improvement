<p align="center">
  <img src="assets/banner.png" width="900" alt="Agent Self-Improvement banner">
</p>

<h1 align="center">Agent Self-Improvement</h1>

<p align="center">
  <b>Turn real conversation history into better agent behavior.</b>
</p>

<p align="center">
  <a href="https://developers.openai.com/codex/skills"><img src="https://img.shields.io/badge/Codex-Skill-111827?style=for-the-badge&logo=openai&logoColor=white" alt="Codex Skill"></a>
  <img src="https://img.shields.io/badge/Subagents-GPT--5.3--Codex--Spark-0f766e?style=for-the-badge" alt="GPT-5.3-Codex-Spark subagents">
  <img src="https://img.shields.io/badge/Install-Copy--Paste--Prompt-f59e0b?style=for-the-badge" alt="Copy-paste install">
  <img src="https://img.shields.io/badge/Tests-7%20Passing-2563eb?style=for-the-badge" alt="Tests passing">
</p>

Self-Improvement is a portable agent skill for turning real conversation history into better operating rules. It is designed for Codex, Claude Code, and generic agents that support filesystem-installed skills.

The core advantage is coverage: shard conversation history into compact cards, let fast `GPT-5.3-Codex-Spark` scout subagents scan many shards in parallel, then spend the main agent's stronger reasoning on synthesis, rules, and safe installation.

## Quick Start

Give this GitHub link to your coding agent:

```text
Install this skill: https://github.com/Chenwei-1999/agent-self-improvement
```

That's the intended install path. The repo includes the installer, tests, and compatibility notes, so a local coding agent can clone it, run the installer, verify it, and report where it landed.

If your agent supports `skill-installer`, the equivalent single command is:

```text
$skill-installer install https://github.com/Chenwei-1999/agent-self-improvement
```

## Why It Exists

Most agent "self-improvement" drifts into vibes or hand-picked examples. This package keeps it grounded:

- Uses actual Codex and Claude conversation history.
- Dispatches `GPT-5.3-Codex-Spark` code-scout subagents for fast, low-cost coverage across many shards.
- Preserves the main agent as the owner of final judgment and config writes.
- Produces scoped rules that can be installed into `AGENTS.md`, `CLAUDE.md`, memories, or a reusable skill.

## How It Works

```text
conversation history
  Codex sessions, Claude projects, exported transcripts
        |
        v
compact cards + shards
  card id, user correction, evidence, candidate lesson
        |
        v
GPT-5.3-Codex-Spark scout subagents
  shard A -> repeated failures
  shard B -> successful patterns
  shard C -> missing rules
        |
        v
main agent synthesis
  evidence ledger -> durable rules -> AGENTS.md / CLAUDE.md / skills
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
python3 scripts/install_skill.py --target agents --force
```

Targets:

- Codex: `~/.codex/skills/self-improvement`
- Claude: `~/.claude/skills/self-improvement`
- Generic agents: `~/.agents/skills/self-improvement`

`--force` replaces the existing installed directory. Run the dry-run command first when installing into global agent locations.

Generic agent support assumes the runtime discovers skills from `~/.agents/skills/...` or lets you point it at that folder. Codex and Claude targets follow their local skill-directory conventions.

</details>

## First Use

Create compact conversation cards:

```bash
python3 scripts/extract_conversation_cards.py --out conversation-audit/cards
```

By default this reads `~/.codex/sessions` and `~/.claude/projects`. Override them with `--codex-root` and `--claude-root` when using exported history or a different machine layout.

Extraction writes Markdown shard files plus `manifest.json`, which records roots, counts, and shard paths for later verification.

Then ask your main agent to dispatch subagents over the shard files:

```text
Use the self-improvement skill. Scan conversation-audit/cards with subagents,
find repeated user corrections and agent failures, then propose durable rules.
```

Expected outputs:

- Evidence ledger: where each finding came from.
- Rule candidates: global, project-specific, and tool-specific.
- Proposed installs: AGENTS.md, CLAUDE.md, memory note, or skill patch.
- Verification plan: how to test the new behavior before calling it done.

## What Good Looks Like

A good audit does not say "be more careful." It says:

- When a user asks for repo status, inspect live files and scheduler state before summarizing.
- When a long-running job is active, report concrete state, elapsed time, and next gate.
- When history is large, use subagents to scan shards and keep the main agent on synthesis.
- When rules should persist across tools, mirror them in Codex and Claude configuration instead of letting the tools diverge.

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
  references/operating-rules.md
  scripts/extract_conversation_cards.py
  scripts/install_skill.py
  tests/
```

## Design Notes

The skill intentionally separates high-volume scanning from high-stakes synthesis. Subagents can cheaply read and classify lots of history; the main agent still owns the final rules, user-facing explanation, and any writes to global config.

This keeps cost low without lowering quality.

The original generated hero image is kept at `assets/self-improvement-hero.png`; the README uses `assets/banner.png` because the strongest skill READMEs lead with a polished banner and keep process details readable in Markdown.
