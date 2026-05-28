# Copy-Paste Install Prompt

Paste this into Codex, Claude Code, or another local coding agent:

```text
Install this skill: https://github.com/Chenwei-1999/agent-self-improvement
```

If the agent supports `skill-installer`, this shorter command is equivalent:

```text
$skill-installer install https://github.com/Chenwei-1999/agent-self-improvement
```

The repository contains `scripts/install_skill.py`, tests, and the target-path notes. A coding agent should be able to infer the clone/install/verify steps from the link alone.

Works with Codex, Claude Code, and other local coding agents. If the runtime has no native skill directory, keep the cloned repository available and follow `SKILL.md`; if it has a custom skill directory, install with `python3 scripts/install_skill.py --target custom --custom-dir <skill-dir> --force`. Map the `history-scout`, `docs-scout`, `main-synthesizer`, and `verifier` roles to that agent's closest equivalents.

Manual fallback:

```bash
git clone https://github.com/Chenwei-1999/agent-self-improvement.git
cd agent-self-improvement
python3 scripts/install_skill.py --target all --force
python3 -m unittest discover -s tests -v
```
