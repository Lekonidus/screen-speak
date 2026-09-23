#!/usr/bin/env python3
"""Prosody-aware OCR text prep for screen-speak.

Maps symbols to pauses, drops decorative junk, protects abbreviations,
and chunks long notes so Piper does not rush.
"""

from __future__ import annotations

import re
import sys

ABBREVS = (
    "Mr",
    "Mrs",
    "Ms",
    "Dr",
    "Prof",
    "Sr",
    "Jr",
    "e.g",
    "i.e",
    "etc",
    "vs",
    "cf",
)

# Placeholder that survives punctuation passes (not a period).
_AB = "\x00"

DECORATIVE = (
    "★☆✦✧❖✿❀❁❂❋❊❇❈❁"
    "●○◆◇■□▪▫•‣⁃∙"
    "※†‡‽⁇⁈⁉"
    "│┃┆┇┊┋─━┄┅┈┉"
    "╔╗╚╝╠╣╦╩╬═║"
    "┌┐└┘├┤┬┴┼"
    "█▄▀░▒▓■□▬▭▮▯"
    "☀☁☂☃☄★☆☎☏☑☒☜☞☢☣"
)

ARROW_CHARS = "→⇒⟶⟹»›"


def heading(line: str) -> bool:
    letters = [c for c in line if c.isalpha()]
    return (
        bool(letters)
        and len(letters) >= 3
        and len(line) < 60
        and sum(c.isupper() for c in letters) / len(letters) > 0.85
    )


def bracket_heading(line: str) -> bool:
    """Whole line is only [Title] or (Title)."""
    m = re.fullmatch(r"[\[(]\s*([^\]\)]+?)\s*[\])]", line.strip())
    return bool(m) and len(m.group(1).strip()) >= 2


def garbage_line(line: str) -> bool:
    """OCR mojibake bars: mostly l/I/1/|/\\ with little real text."""
    compact = re.sub(r"\s+", "", line)
    if len(compact) < 4:
        return False
    noise = sum(1 for c in compact if c in "lI1|/\\")
    # l/I often are OCR noise; only count other letters as "real"
    real_letters = sum(1 for c in compact if c.isalpha() and c not in "lI")
    if noise / len(compact) >= 0.6 and real_letters <= max(2, len(compact) // 5):
        return True
    return False


def _protect_abbrevs(s: str) -> str:
    for ab in sorted(ABBREVS, key=len, reverse=True):
        # Match "Mr." / "e.g." case-insensitive at word start-ish
        if "." in ab:
            # e.g. / i.e. — protect the whole dotted form
            pat = re.compile(re.escape(ab) + r"\.?", re.IGNORECASE)
            s = pat.sub(lambda m: m.group(0).rstrip(".").replace(".", _AB) + _AB, s)
        else:
            pat = re.compile(r"\b" + re.escape(ab) + r"\.", re.IGNORECASE)
            s = pat.sub(lambda m: m.group(0)[:-1] + _AB, s)
    return s


def _restore_abbrevs(s: str) -> str:
    return s.replace(_AB, ".")


def clean(s: str) -> str:
    s = _protect_abbrevs(s)

    # Ellipsis → sentence break
    s = s.replace("...", ".").replace("…", ".")

    # Quotes → short breath
    s = re.sub(r'[“”„‟"\']', ", ", s)

    # Slash → pause
    s = s.replace("/", ", ")

    # Unicode dashes always → pause
    s = re.sub(r"[—–−‒]", ", ", s)
    # ASCII hyphen not between word chars (keep well-known)
    s = re.sub(r"(?<!\w)-(?!\w)", ", ", s)
    s = re.sub(r"\s+-\s+", ", ", s)

    # Brackets / asides → , content,
    s = re.sub(r"\(([^)]+)\)", r", \1,", s)
    s = re.sub(r"\[([^\]]+)\]", r", \1,", s)

    # Decorative junk → delete (leave space if between letters)
    deco_class = re.escape(DECORATIVE)
    s = re.sub(rf"(?<=\w)[{deco_class}]+(?=\w)", " ", s)
    s = re.sub(rf"[{deco_class}]+", "", s)

    # Arrows / separators
    s = re.sub(rf"[{re.escape(ARROW_CHARS)}]", ", ", s)
    s = re.sub(r"(?<!\w)>(?!\w)", ", ", s)
    s = re.sub(r"\|+", ", ", s)
    s = re.sub(r" {2,}", ", ", s)

    s = _restore_abbrevs(s)

    # Normalize whitespace / punctuation spacing
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s+([,.;:!?])", r"\1", s)
    s = re.sub(r",\s*,+", ", ", s)
    s = re.sub(r"\s+", " ", s).strip(" ,")
    # Avoid ",." artifacts
    s = re.sub(r",\s*\.", ".", s)
    s = re.sub(r"\.\s*\.", ".", s)

    if s and s[-1] not in ".!?":
        s += "."
    return s


def flow(text: str, *, chunk_sentences: int | None = None) -> str:
    """Join OCR lines, clean, optionally chunk.

    If chunk_sentences is None, returns a single cleaned string (no newlines).
    If set (e.g. 3), returns newline-separated chunks of that many sentences.
    """
    parts: list[str] = []
    buf: list[str] = []

    def flush() -> None:
        if buf:
            parts.append(clean(" ".join(buf)))
            buf.clear()

    for raw in text.replace("\r", "").split("\n"):
        line = re.sub(r"[ \t]+", " ", raw).strip()
        if not line:
            flush()
            continue
        if garbage_line(line):
            continue
        letters = sum(c.isalpha() for c in line)
        if letters == 0 or (len(line) > 6 and letters / len(line) < 0.25):
            continue
        if bracket_heading(line):
            flush()
            inner = re.fullmatch(r"[\[(]\s*([^\]\)]+?)\s*[\])]", line).group(1)  # type: ignore[union-attr]
            parts.append(clean(inner.title()))
            continue
        if heading(line):
            flush()
            parts.append(clean(line.title()))
            continue
        buf.append(line)
    flush()

    joined = " ".join(p for p in parts if p)
    joined = re.sub(r"\s+", " ", joined).strip()
    if not joined:
        return ""

    if chunk_sentences is None:
        return joined
    return chunk(joined, chunk_sentences)


def split_sentences(text: str) -> list[str]:
    text = _protect_abbrevs(text)
    # Split after .!? when followed by space + capital or end
    pieces = re.split(r"(?<=[.!?])\s+", text.strip())
    out: list[str] = []
    for p in pieces:
        p = _restore_abbrevs(p.strip())
        if p:
            out.append(p)
    return out


def chunk(text: str, max_sentences: int = 3) -> str:
    """Group sentences into newline-separated chunks of max_sentences each."""
    sents = split_sentences(text)
    if not sents:
        return ""
    groups: list[str] = []
    for i in range(0, len(sents), max_sentences):
        groups.append(" ".join(sents[i : i + max_sentences]))
    return "\n".join(groups)


def prepare(text: str) -> str:
    """Full pipeline for speech: flow + chunk every 3 sentences."""
    return flow(text, chunk_sentences=3)


def self_check() -> None:
    sample = """HYGINUS: FABULAE
Try your hand at these excerpts. The grammar is
very simple and the stories are interesting... Though
they might give you nightmares.
"""
    out = flow(sample)
    assert "grammar is very simple" in out, out
    assert "interesting. Though" in out, out
    assert "Hyginus: Fabulae." in out, out
    assert "\n" not in out, out

    assert "well-known" in clean("A well-known hero."), clean("A well-known hero.")
    assert ", " in clean("wait — then go") or "," in clean("wait — then go"), clean(
        "wait — then go"
    )
    assert "—" not in clean("wait — then go"), clean("wait — then go")

    c = clean("She spoke (quietly) now.")
    assert "quietly" in c and "(" not in c and ")" not in c, c

    c = clean("Item ★ rare loot")
    assert "★" not in c and "rare" in c, c

    c = clean("A → B → C")
    assert "→" not in c and "A" in c and "B" in c, c
    assert re.search(r"A,\s*B", c), c

    # Abbreviations: Mr. should not become sentence break before Smith
    sents = split_sentences(clean("Mr. Smith went home."))
    assert len(sents) == 1, sents
    assert "Mr." in sents[0] or "Mr" in sents[0], sents

    assert flow("Left / right now.") == "Left, right now."
    assert "hello" in flow('He said "hello" now.'), flow('He said "hello" now.')

    # Bracket-only heading line
    bh = flow("[NOTE]\nSomething happened.")
    assert "Note" in bh or "NOTE" in bh.upper(), bh
    assert "Something happened" in bh, bh

    # Garbage line dropped
    g = flow("llll||||IIII\nReal sentence here.")
    assert "Real sentence" in g, g
    assert "llll" not in g, g

    # Chunking: 7 short sentences → multiple lines, ≤3 each
    seven = " ".join(f"Sentence number {i}." for i in range(1, 8))
    chunked = chunk(seven, 3)
    lines = [ln for ln in chunked.split("\n") if ln.strip()]
    assert len(lines) == 3, lines
    for ln in lines:
        assert len(split_sentences(ln)) <= 3, ln

    prepared = prepare(seven)
    assert "\n" in prepared, prepared

    print("ok")


def main() -> int:
    if "--check" in sys.argv:
        self_check()
        return 0
    text = sys.stdin.read()
    sys.stdout.write(prepare(text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
