#!/usr/bin/env python3
"""A strict, dependency-free parser for the YAML subset this package allows.

Two jobs, one implementation:

1. It lets ``ai-dlc validate`` run from a fresh clone with nothing installed.
   The package has no runtime dependencies, which matters for a tool whose whole
   purpose is being dropped into somebody else's repository.

2. It is the portability guard. Agent Skills frontmatter is read by Claude Code,
   Codex, Copilot, and a long tail of third-party loaders, not all of which use a
   real YAML implementation. Anything this parser rejects -- anchors, aliases,
   merge keys, block scalars, flow collections, tabs -- is banned from the
   frontmatter of every SKILL.md in this repo, because a naive reader elsewhere
   would get it wrong.

Supported: nested block mappings, block sequences, quoted and bare scalars,
comments, ``null``/``~``/empty, booleans, integers, floats.
"""

from __future__ import annotations

import re
from typing import Any, List, Optional, Tuple

__all__ = ["YamlLiteError", "parse", "split_frontmatter"]

_FRONTMATTER_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n?", re.DOTALL)
_INT_RE = re.compile(r"^[+-]?\d+$")
_FLOAT_RE = re.compile(r"^[+-]?(\d+\.\d*|\.\d+)([eE][+-]?\d+)?$")


class YamlLiteError(ValueError):
    """The document uses YAML this package deliberately refuses to support."""

    def __init__(self, message: str, line: int = 0) -> None:
        super().__init__(f"line {line}: {message}" if line else message)
        self.line = line


def split_frontmatter(text: str) -> Tuple[Optional[str], str]:
    """Split ``---`` delimited frontmatter from the body.

    Returns ``(None, text)`` when the document has no frontmatter.
    """
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return None, text
    return match.group(1), text[match.end():]


def _strip_comment(value: str) -> str:
    """Remove a trailing ``# comment``, respecting quotes."""
    out: List[str] = []
    quote: Optional[str] = None
    prev_space = True
    for ch in value:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            out.append(ch)
            prev_space = False
            continue
        if ch == "#" and prev_space:
            break
        out.append(ch)
        prev_space = ch in " \t"
    return "".join(out).strip()


def _scalar(raw: str, line: int) -> Any:
    value = _strip_comment(raw)
    if value == "":
        return None
    first = value[0]
    if first in "&*":
        raise YamlLiteError("anchors and aliases are not supported", line)
    if first in "|>":
        raise YamlLiteError("block scalars are not supported", line)
    if first in "{[":
        raise YamlLiteError("flow collections are not supported; use block style", line)
    if len(value) >= 2 and first in "\"'" and value[-1] == first:
        inner = value[1:-1]
        if first == '"':
            inner = inner.replace('\\"', '"').replace("\\n", "\n").replace("\\\\", "\\")
        else:
            inner = inner.replace("''", "'")
        return inner
    lowered = value.lower()
    if lowered in ("null", "~"):
        return None
    if lowered in ("true", "yes", "on"):
        return True
    if lowered in ("false", "no", "off"):
        return False
    if _INT_RE.match(value):
        return int(value)
    if _FLOAT_RE.match(value):
        return float(value)
    return value


def _split_key(content: str, line: int) -> Tuple[str, str]:
    """Split ``key: rest`` at the first unquoted colon-space (or trailing colon)."""
    quote: Optional[str] = None
    for i, ch in enumerate(content):
        if quote:
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            continue
        if ch == ":":
            rest = content[i + 1:]
            if rest == "" or rest[0] in " \t":
                key = content[:i].strip()
                if key.startswith("<<"):
                    raise YamlLiteError("merge keys are not supported", line)
                if len(key) >= 2 and key[0] in "\"'" and key[-1] == key[0]:
                    key = key[1:-1]
                if not key:
                    raise YamlLiteError("empty mapping key", line)
                return key, rest.strip()
    raise YamlLiteError(f"expected 'key: value', got {content!r}", line)


def _tokenize(text: str) -> List[Tuple[int, str, int]]:
    tokens: List[Tuple[int, str, int]] = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            raise YamlLiteError("tabs are not allowed for indentation", lineno)
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped in ("---", "..."):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        tokens.append((indent, stripped, lineno))
    return tokens


def _parse_block(tokens: List[Tuple[int, str, int]], pos: int, indent: int) -> Tuple[Any, int]:
    first_indent, first_content, first_line = tokens[pos]
    if first_content.startswith("- ") or first_content == "-":
        return _parse_sequence(tokens, pos, first_indent)
    return _parse_mapping(tokens, pos, first_indent)


def _parse_sequence(tokens: List[Tuple[int, str, int]], pos: int, indent: int) -> Tuple[List[Any], int]:
    items: List[Any] = []
    while pos < len(tokens):
        cur_indent, content, lineno = tokens[pos]
        if cur_indent < indent:
            break
        if cur_indent > indent:
            raise YamlLiteError("unexpected indentation in sequence", lineno)
        if not (content.startswith("- ") or content == "-"):
            break
        rest = content[1:].strip()
        pos += 1
        if rest == "":
            if pos < len(tokens) and tokens[pos][0] > indent:
                value, pos = _parse_block(tokens, pos, tokens[pos][0])
            else:
                value = None
        elif _looks_like_mapping(rest):
            # "- key: value" opens a mapping whose indent is the text column.
            child_indent = indent + (len(content) - len(content[1:].lstrip()))
            synthetic = [(child_indent, rest, lineno)]
            j = pos
            while j < len(tokens) and tokens[j][0] > indent:
                synthetic.append(tokens[j])
                j += 1
            value, consumed = _parse_mapping(synthetic, 0, child_indent)
            pos += consumed - 1
        else:
            value = _scalar(rest, lineno)
        items.append(value)
    return items, pos


def _looks_like_mapping(content: str) -> bool:
    try:
        _split_key(content, 0)
    except YamlLiteError:
        return False
    return True


def _parse_mapping(tokens: List[Tuple[int, str, int]], pos: int, indent: int) -> Tuple[dict, int]:
    mapping: dict = {}
    while pos < len(tokens):
        cur_indent, content, lineno = tokens[pos]
        if cur_indent < indent:
            break
        if cur_indent > indent:
            raise YamlLiteError("unexpected indentation in mapping", lineno)
        if content.startswith("- ") or content == "-":
            break
        key, rest = _split_key(content, lineno)
        if key in mapping:
            raise YamlLiteError(f"duplicate key {key!r}", lineno)
        pos += 1
        if rest == "":
            if pos < len(tokens) and tokens[pos][0] > indent:
                value, pos = _parse_block(tokens, pos, tokens[pos][0])
            elif pos < len(tokens) and tokens[pos][0] == indent and tokens[pos][1].startswith("- "):
                value, pos = _parse_sequence(tokens, pos, indent)
            else:
                value = None
        else:
            value = _scalar(rest, lineno)
        mapping[key] = value
    return mapping, pos


def parse(text: str) -> Any:
    """Parse a YAML document restricted to this package's supported subset."""
    tokens = _tokenize(text)
    if not tokens:
        return {}
    value, pos = _parse_block(tokens, 0, tokens[0][0])
    if pos != len(tokens):
        raise YamlLiteError("trailing content could not be parsed", tokens[pos][2])
    return value
