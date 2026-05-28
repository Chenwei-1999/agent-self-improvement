#!/usr/bin/env python3
"""Extract compact conversation cards from local agent histories."""

from __future__ import print_function

import argparse
import datetime as _dt
import hashlib
import json
import os
from pathlib import Path


SECRET_MARKERS = ("sk-", "api_key", "apikey", "token", "password", "secret")


def read_jsonl(path):
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield line_number, json.loads(line)
            except Exception:
                continue


def compact(value, limit):
    if value is None:
        return ""
    if not isinstance(value, str):
        try:
            value = json.dumps(value, ensure_ascii=False, sort_keys=True)
        except Exception:
            value = str(value)
    value = " ".join(value.replace("\x00", " ").split())
    lowered = value.lower()
    if any(marker in lowered for marker in SECRET_MARKERS):
        value = "[redacted possible secret]"
    if len(value) > limit:
        return value[: limit - 3] + "..."
    return value


def stable_id(prefix, path, line_number):
    digest = hashlib.sha1(("{0}:{1}".format(path, line_number)).encode("utf-8")).hexdigest()
    return "{0}-{1}".format(prefix, digest[:12])


def extract_text_from_message(message):
    if isinstance(message, str):
        return message
    if isinstance(message, list):
        parts = []
        for item in message:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text") or item.get("content") or item.get("input")
                if text:
                    parts.append(str(text))
        return "\n".join(parts)
    if isinstance(message, dict):
        return message.get("text") or message.get("content") or message.get("input") or ""
    return ""


def card_from_codex(path, line_number, payload, max_chars):
    item_type = payload.get("type") or payload.get("event") or ""
    role = payload.get("role")
    text = ""

    if "message" in payload:
        msg = payload.get("message")
        if isinstance(msg, dict):
            role = role or msg.get("role")
            text = extract_text_from_message(msg.get("content") or msg.get("text"))
        else:
            text = extract_text_from_message(msg)
    elif "payload" in payload:
        inner = payload.get("payload")
        if isinstance(inner, dict):
            role = role or inner.get("role")
            text = extract_text_from_message(inner.get("content") or inner.get("message") or inner.get("text"))

    if not text and "content" in payload:
        text = extract_text_from_message(payload.get("content"))

    if not text:
        return None

    return {
        "id": stable_id("codex", path, line_number),
        "source": "codex",
        "path": str(path),
        "line": line_number,
        "type": compact(item_type, 80),
        "role": compact(role or "unknown", 40),
        "text": compact(text, max_chars),
    }


def card_from_claude(path, line_number, payload, max_chars):
    role = payload.get("role")
    item_type = payload.get("type") or payload.get("event") or ""
    text = ""

    if "message" in payload:
        message = payload.get("message")
        if isinstance(message, dict):
            role = role or message.get("role")
            text = extract_text_from_message(message.get("content") or message.get("text"))
        else:
            text = extract_text_from_message(message)

    if not text:
        text = extract_text_from_message(payload.get("content") or payload.get("text"))

    if not text:
        return None

    return {
        "id": stable_id("claude", path, line_number),
        "source": "claude",
        "path": str(path),
        "line": line_number,
        "type": compact(item_type, 80),
        "role": compact(role or "unknown", 40),
        "text": compact(text, max_chars),
    }


def card_from_generic_jsonl(path, line_number, payload, max_chars):
    role = payload.get("role") or payload.get("speaker") or payload.get("author")
    item_type = payload.get("type") or payload.get("event") or "message"
    text = ""
    for key in (
        "message",
        "messages",
        "content",
        "text",
        "prompt",
        "response",
        "output",
        "conversation",
        "transcript",
    ):
        if key in payload:
            text = extract_text_from_message(payload.get(key))
            if text:
                break
    if not text:
        return None
    return {
        "id": stable_id("generic", path, line_number),
        "source": "generic",
        "path": str(path),
        "line": line_number,
        "type": compact(item_type, 80),
        "role": compact(role or "unknown", 40),
        "text": compact(text, max_chars),
    }


def cards_from_text_file(path, max_chars):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    text = " ".join(text.replace("\x00", " ").split())
    if not text:
        return []
    chunk_size = max(max_chars, 500)
    cards = []
    for index, start in enumerate(range(0, len(text), chunk_size), 1):
        chunk = text[start:start + chunk_size]
        cards.append({
            "id": stable_id("generic", path, index),
            "source": "generic",
            "path": str(path),
            "line": index,
            "type": "text-export",
            "role": "unknown",
            "text": compact(chunk, max_chars),
        })
    return cards


def collect_cards(root, source, max_chars):
    root = Path(root).expanduser()
    if not root.exists():
        return []
    cards = []
    for path in sorted(root.rglob("*.jsonl")):
        for line_number, payload in read_jsonl(path):
            if source == "codex":
                card = card_from_codex(path, line_number, payload, max_chars)
            else:
                card = card_from_claude(path, line_number, payload, max_chars)
            if card:
                cards.append(card)
    return cards


def collect_generic_cards(root, max_chars, max_files=None, max_bytes=None):
    if not root:
        return []
    root = Path(root).expanduser()
    if not root.exists():
        return []
    cards = []
    files_seen = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if max_files is not None and files_seen >= max_files:
            break
        if max_bytes is not None:
            try:
                if path.stat().st_size > max_bytes:
                    continue
            except Exception:
                continue
        suffix = path.suffix.lower()
        if suffix == ".jsonl":
            files_seen += 1
            for line_number, payload in read_jsonl(path):
                card = card_from_generic_jsonl(path, line_number, payload, max_chars)
                if card:
                    cards.append(card)
        elif suffix in (".md", ".txt"):
            files_seen += 1
            cards.extend(cards_from_text_file(path, max_chars))
    return cards


def write_shards(cards, out_dir, source, shard_count):
    source_dir = out_dir / source
    source_dir.mkdir(parents=True, exist_ok=True)
    if shard_count < 1:
        shard_count = 1
    shards = [[] for _ in range(shard_count)]
    for index, card in enumerate(cards):
        shards[index % shard_count].append(card)

    paths = []
    for index, shard in enumerate(shards, 1):
        path = source_dir / "shard-{0:02d}.md".format(index)
        with path.open("w", encoding="utf-8") as handle:
            handle.write("# {0} shard {1:02d}\n\n".format(source.title(), index))
            for card in shard:
                handle.write("## {id}\n\n".format(**card))
                handle.write("- source: {source}\n".format(**card))
                handle.write("- role: {role}\n".format(**card))
                handle.write("- type: {type}\n".format(**card))
                handle.write("- file: {path}:{line}\n\n".format(**card))
                handle.write("{0}\n\n".format(card["text"]))
        paths.append(str(path))
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-root", default="~/.codex/sessions", help="Root containing Codex JSONL history.")
    parser.add_argument("--claude-root", default="~/.claude/projects", help="Root containing Claude JSONL history.")
    parser.add_argument("--generic-root", default=None, help="Optional root containing exported JSONL, Markdown, or text transcripts from any coding agent.")
    parser.add_argument("--out", default="conversation-audit/cards", help="Output directory for shard files.")
    parser.add_argument("--codex-shards", type=int, default=16, help="Number of Codex shard files.")
    parser.add_argument("--claude-shards", type=int, default=10, help="Number of Claude shard files.")
    parser.add_argument("--generic-shards", type=int, default=8, help="Number of generic transcript shard files.")
    parser.add_argument("--max-chars", type=int, default=700, help="Maximum text length per card.")
    parser.add_argument("--max-files", type=int, default=None, help="Maximum number of generic export files to scan.")
    parser.add_argument("--max-bytes", type=int, default=None, help="Skip generic export files larger than this many bytes.")
    args = parser.parse_args()

    out_dir = Path(args.out).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    codex_cards = collect_cards(args.codex_root, "codex", args.max_chars)
    claude_cards = collect_cards(args.claude_root, "claude", args.max_chars)
    generic_cards = collect_generic_cards(args.generic_root, args.max_chars, args.max_files, args.max_bytes)

    shard_paths = []
    shard_paths.extend(write_shards(codex_cards, out_dir, "codex", args.codex_shards))
    shard_paths.extend(write_shards(claude_cards, out_dir, "claude", args.claude_shards))
    if generic_cards:
        shard_paths.extend(write_shards(generic_cards, out_dir, "generic", args.generic_shards))

    manifest = {
        "created_at": _dt.datetime.utcnow().isoformat() + "Z",
        "codex_root": os.path.expanduser(args.codex_root),
        "claude_root": os.path.expanduser(args.claude_root),
        "generic_root": os.path.expanduser(args.generic_root) if args.generic_root else None,
        "codex_cards": len(codex_cards),
        "claude_cards": len(claude_cards),
        "generic_cards": len(generic_cards),
        "shards": shard_paths,
    }
    manifest_path = out_dir / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print("Wrote {0} Codex cards, {1} Claude cards, and {2} generic cards to {3}".format(
        len(codex_cards), len(claude_cards), len(generic_cards), out_dir
    ))
    print("Manifest: {0}".format(manifest_path))


if __name__ == "__main__":
    main()
