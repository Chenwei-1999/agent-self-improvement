#!/usr/bin/env python3
"""Install the self-improvement skill for Codex, Claude, or generic agents."""

from __future__ import print_function

import argparse
import os
import shutil
from pathlib import Path


SKILL_NAME = "self-improvement"
TARGETS = {
    "codex": Path("~/.codex/skills") / SKILL_NAME,
    "claude": Path("~/.claude/skills") / SKILL_NAME,
    "agents": Path("~/.agents/skills") / SKILL_NAME,
}
EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", "tests", "conversation-audit"}


def source_root():
    return Path(__file__).resolve().parents[1]


def selected_targets(target):
    if target == "all":
        return TARGETS
    return {target: TARGETS[target]}


def ignore_patterns(directory, names):
    ignored = set()
    for name in names:
        if name in EXCLUDE_DIRS:
            ignored.add(name)
        if name.endswith(".pyc"):
            ignored.add(name)
    return ignored


def install_one(src, target_path, dry_run, force):
    target_path = target_path.expanduser()
    display = str(target_path).replace(os.path.expanduser("~"), "~", 1)
    if dry_run:
        print("would install {0} -> {1}".format(src, display))
        return

    if target_path.exists():
        if not force:
            raise SystemExit("{0} already exists; rerun with --force".format(display))
        print("replacing existing {0}".format(display))
        shutil.rmtree(str(target_path))

    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(str(src), str(target_path), ignore=ignore_patterns)
    print("installed {0}".format(display))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=["all", "codex", "claude", "agents"], default="all")
    parser.add_argument("--dry-run", action="store_true", help="Print target directories without copying.")
    parser.add_argument("--force", action="store_true", help="Replace an existing installed copy.")
    args = parser.parse_args()

    src = source_root()
    for _, target_path in selected_targets(args.target).items():
        install_one(src, target_path, args.dry_run, args.force)


if __name__ == "__main__":
    main()
