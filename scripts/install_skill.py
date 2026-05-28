#!/usr/bin/env python3
"""Install the self-improvement skill for local coding-agent runtimes."""

from __future__ import print_function

import argparse
import os
import shutil
from pathlib import Path


SKILL_NAME = "self-improvement"
TARGETS = {
    "codex": Path("~/.codex/skills") / SKILL_NAME,
    "claude": Path("~/.claude/skills") / SKILL_NAME,
    "gemini": Path("~/.gemini/skills") / SKILL_NAME,
    "agents": Path("~/.agents/skills") / SKILL_NAME,
}
ALIASES = {
    "agent": "agents",
    "gemini-cli": "gemini",
    "generic": "agents",
}
EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", "tests", "conversation-audit"}
DISCOVERY_HINTS = {
    "codex": "verify: `codex --help` includes skills, or ls ~/.codex/skills",
    "claude": "verify: `claude /skills` or check ~/.claude/settings.json skill loader",
    "gemini": "verify: `gemini skills list`",
    "agents": "verify: confirm your runtime scans ~/.agents/skills/",
}


def source_root():
    return Path(__file__).resolve().parents[1]


def selected_targets(target, custom_dir):
    target = ALIASES.get(target, target)
    if target == "all":
        return TARGETS
    if target == "custom":
        if not custom_dir:
            raise SystemExit("--target custom requires --custom-dir")
        return {"custom": Path(custom_dir)}
    return {target: TARGETS[target]}


def ignore_patterns(directory, names):
    ignored = set()
    for name in names:
        if name in EXCLUDE_DIRS:
            ignored.add(name)
        if name.endswith(".pyc"):
            ignored.add(name)
    return ignored


def target_exists(target_path):
    return target_path.exists() or target_path.is_symlink()


def remove_existing_target(target_path):
    if target_path.is_symlink() or target_path.is_file():
        target_path.unlink()
    else:
        shutil.rmtree(str(target_path))


def install_one(src, target_path, dry_run, force, hint=None):
    target_path = target_path.expanduser()
    display = str(target_path).replace(os.path.expanduser("~"), "~", 1)
    if dry_run:
        print("would install {0} -> {1}".format(src, display))
        if hint:
            print("  {0}".format(hint))
        return

    if target_exists(target_path):
        if not force:
            raise SystemExit("{0} already exists; rerun with --force".format(display))
        print("replacing existing {0}".format(display))
        remove_existing_target(target_path)

    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(str(src), str(target_path), ignore=ignore_patterns)
    print("installed {0}".format(display))
    if hint:
        print("  {0}".format(hint))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        choices=["all", "codex", "claude", "gemini", "gemini-cli", "agents", "agent", "generic", "custom"],
        default="all",
        help="Runtime target. 'generic' and 'agent' install to ~/.agents/skills; 'gemini-cli' is an alias for 'gemini'.",
    )
    parser.add_argument("--custom-dir", help="Install into an explicit skill directory for another runtime.")
    parser.add_argument("--dry-run", action="store_true", help="Print target directories without copying.")
    parser.add_argument("--force", action="store_true", help="Replace an existing installed copy.")
    args = parser.parse_args()

    src = source_root()
    for key, target_path in selected_targets(args.target, args.custom_dir).items():
        install_one(src, target_path, args.dry_run, args.force, DISCOVERY_HINTS.get(key))


if __name__ == "__main__":
    main()
