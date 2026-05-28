#!/usr/bin/env python3
"""Extract compact conversation cards from local agent histories."""

from __future__ import print_function

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
from pathlib import Path


SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_\-]{16,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"xox[abpr]-[A-Za-z0-9\-]{10,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"AIza[0-9A-Za-z_\-]{30,}"),
    re.compile(r"hf_[A-Za-z0-9]{30,}"),
    re.compile(r"glpat-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"Bearer\s+[A-Za-z0-9._~+/=\-]{20,}", re.IGNORECASE),
    re.compile(
        r"(?i)(?:api[_\-]?key|access[_\-]?token|secret[_\-]?key|client[_\-]?secret)"
        r"['\"]?\s*[:=]\s*['\"]?[A-Za-z0-9_\-./+]{16,}"
    ),
)
SESSION_ID_RE = re.compile(
    r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
    re.IGNORECASE,
)
CODEX_TOOL_TYPES = {
    "function_call",
    "function_call_output",
    "local_shell_call",
    "local_shell_call_output",
    "tool_use",
    "tool_result",
}
DEFAULT_GENERIC_ROOTS = (
    "~/.gemini/history",
    "~/.gemini/tmp",
    "~/.agents/history",
    "~/.agents/conversations",
)


def redact_secrets(text):
    for pattern in SECRET_PATTERNS:
        text = pattern.sub("[redacted]", text)
    return text


def session_id_from_path(path):
    p = Path(path)
    candidates = [p.stem, p.parent.name]
    for candidate in candidates:
        match = SESSION_ID_RE.search(candidate)
        if match:
            return match.group(1)
    return p.stem


def timestamp_from_payload(payload):
    if not isinstance(payload, dict):
        return ""
    for key in ("timestamp", "created_at", "time", "ts", "_ts"):
        value = payload.get(key)
        if value:
            return str(value)[:40]
    return ""


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


def read_json_records(path):
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            data = json.load(handle)
    except Exception:
        return

    if isinstance(data, list):
        for index, item in enumerate(data, 1):
            yield index, item
    else:
        yield 1, data


def default_generic_roots():
    roots = []
    for root in DEFAULT_GENERIC_ROOTS:
        path = Path(root).expanduser()
        if path.exists():
            roots.append(str(path))
    return roots


def compact(value, limit):
    if value is None:
        return ""
    if not isinstance(value, str):
        try:
            value = json.dumps(value, ensure_ascii=False, sort_keys=True)
        except Exception:
            value = str(value)
    value = " ".join(value.replace("\x00", " ").split())
    value = redact_secrets(value)
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


def tool_text_from_codex(payload):
    item_type = payload.get("type") or ""
    if item_type not in CODEX_TOOL_TYPES:
        return None
    name = payload.get("name") or payload.get("tool") or ""

    if item_type in ("function_call", "tool_use"):
        args = payload.get("arguments")
        if args is None:
            args = payload.get("input") or payload.get("action") or ""
        if not isinstance(args, str):
            try:
                args = json.dumps(args, ensure_ascii=False)
            except Exception:
                args = str(args)
        return "[tool:{0}] {1}".format(name or "call", args).strip()

    if item_type in ("function_call_output", "tool_result", "local_shell_call_output"):
        output = payload.get("output")
        if output is None:
            output = payload.get("content")
        return "[tool_output:{0}] {1}".format(
            name or item_type, extract_text_from_message(output)
        ).strip()

    if item_type == "local_shell_call":
        action = payload.get("action") or {}
        if isinstance(action, dict):
            command = action.get("command") or action
            if not isinstance(command, str):
                try:
                    command = json.dumps(command, ensure_ascii=False)
                except Exception:
                    command = str(command)
            return "[shell] {0}".format(command)
        return "[shell] {0}".format(action)

    return None


def card_from_codex(path, line_number, payload, max_chars):
    if not isinstance(payload, dict):
        return None
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
        text = tool_text_from_codex(payload) or ""
        if text and not role:
            role = "tool"

    if not text:
        return None

    return {
        "id": stable_id("codex", path, line_number),
        "source": "codex",
        "path": str(path),
        "line": line_number,
        "session_id": session_id_from_path(path),
        "timestamp": timestamp_from_payload(payload),
        "type": compact(item_type, 80),
        "role": compact(role or "unknown", 40),
        "text": compact(text, max_chars),
    }


def card_from_claude(path, line_number, payload, max_chars):
    if not isinstance(payload, dict):
        return None
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
        "session_id": session_id_from_path(path),
        "timestamp": timestamp_from_payload(payload),
        "type": compact(item_type, 80),
        "role": compact(role or "unknown", 40),
        "text": compact(text, max_chars),
    }


def card_from_generic_jsonl(path, line_number, payload, max_chars):
    if not isinstance(payload, dict):
        return None
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
        "session_id": session_id_from_path(path),
        "timestamp": timestamp_from_payload(payload),
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
    session_id = session_id_from_path(path)
    for index, start in enumerate(range(0, len(text), chunk_size), 1):
        chunk = text[start:start + chunk_size]
        cards.append({
            "id": stable_id("generic", path, index),
            "source": "generic",
            "path": str(path),
            "line": index,
            "session_id": session_id,
            "timestamp": "",
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
        elif suffix == ".json":
            files_seen += 1
            for line_number, payload in read_json_records(path):
                card = card_from_generic_jsonl(path, line_number, payload, max_chars)
                if card:
                    cards.append(card)
        elif suffix in (".md", ".txt"):
            files_seen += 1
            cards.extend(cards_from_text_file(path, max_chars))
    return cards


def collect_generic_roots(roots, max_chars, max_files=None, max_bytes=None):
    cards = []
    for root in roots:
        cards.extend(collect_generic_cards(root, max_chars, max_files, max_bytes))
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
                handle.write("- file: {path}:{line}\n".format(**card))
                if card.get("session_id"):
                    handle.write("- session: {0}\n".format(card["session_id"]))
                if card.get("timestamp"):
                    handle.write("- ts: {0}\n".format(card["timestamp"]))
                handle.write("\n")
                handle.write("{0}\n\n".format(card["text"]))
        paths.append(str(path))
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-root", default="~/.codex/sessions", help="Root containing Codex JSONL history.")
    parser.add_argument("--claude-root", default="~/.claude/projects", help="Root containing Claude JSONL history.")
    parser.add_argument(
        "--generic-root",
        action="append",
        default=None,
        help="Root containing exported JSON, JSONL, Markdown, or text transcripts from any coding agent. May be passed multiple times; when omitted, safe conventional roots are auto-discovered.",
    )
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
    generic_roots = args.generic_root or default_generic_roots()
    generic_cards = collect_generic_roots(generic_roots, args.max_chars, args.max_files, args.max_bytes)

    shard_paths = []
    shard_paths.extend(write_shards(codex_cards, out_dir, "codex", args.codex_shards))
    shard_paths.extend(write_shards(claude_cards, out_dir, "claude", args.claude_shards))
    if generic_cards:
        shard_paths.extend(write_shards(generic_cards, out_dir, "generic", args.generic_shards))

    try:
        now = _dt.datetime.now(_dt.UTC)
    except AttributeError:
        now = _dt.datetime.utcnow().replace(tzinfo=_dt.timezone.utc)
    manifest = {
        "created_at": now.isoformat().replace("+00:00", "Z"),
        "codex_root": os.path.expanduser(args.codex_root),
        "claude_root": os.path.expanduser(args.claude_root),
        "generic_root": os.path.expanduser(generic_roots[0]) if len(generic_roots) == 1 else None,
        "generic_roots": [os.path.expanduser(root) for root in generic_roots],
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
