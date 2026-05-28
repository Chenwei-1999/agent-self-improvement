# Copy-Paste Install Prompt

Paste this into Codex, Claude Code, or another local coding agent:

```text
Install the Self-Improvement Skill from GitHub.

Repository: https://github.com/Chenwei-1999/agent-self-improvement.git

Steps:
1. Clone the repository into a temporary directory.
2. From the cloned repository, run:
   python3 scripts/install_skill.py --target all --force
3. Verify the package:
   python3 -m unittest discover -s tests -v
4. Report the installed paths:
   ~/.codex/skills/self-improvement
   ~/.claude/skills/self-improvement
   ~/.agents/skills/self-improvement

Do not edit unrelated global config. If a target runtime does not use one of
those skill directories, explain that compatibility note instead of guessing.
```

For a single runtime, replace `--target all` with `--target codex`, `--target claude`, or `--target agents`.

