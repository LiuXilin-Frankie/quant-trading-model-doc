#!/usr/bin/env python3
"""Mechanical completeness check for a quant model document.

Reports only what can be decided without judgement. Everything this script
stays silent about still needs reading: whether a formula is correct, whether
a finite domain is complete, whether a stated fact is true.

Usage:
    python check_doc.py <document.md>

Exit codes:
    0  no blocking findings
    1  blocking findings
    2  the document could not be read
"""

from __future__ import annotations

import pathlib
import re
import sys
from typing import List, Tuple

SECTIONS = [
    "Document Topology",
    "Purpose",
    "Data Inputs",
    "Data Outputs",
    "Model Definition",
    "Calibration",
    "Prediction and Information Boundary",
    "Fallback Policy",
    "Validation Examples",
    "Operational Notes",
    "Non-goals",
]

HEADING = re.compile(r"^#{1,6}\s+(.*?)\s*$")
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
TABLE_SEP = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
PROPOSED_REASON = re.compile(r"PROPOSED\s*[—–-]\s*[^,\s][^,]*,\s*\S+")


def in_code_fence(lines: List[str]) -> List[bool]:
    """Mark lines inside fenced code blocks so they are not parsed as content."""
    flags, fenced = [], False
    for line in lines:
        if line.lstrip().startswith("```"):
            fenced = not fenced
            flags.append(True)
        else:
            flags.append(fenced)
    return flags


def missing_sections(lines: List[str], skip: List[bool]) -> List[str]:
    headings = [
        HEADING.match(line).group(1).lower()
        for line, s in zip(lines, skip)
        if not s and HEADING.match(line)
    ]
    blob = " | ".join(headings)
    return [name for name in SECTIONS if name.lower() not in blob]


def empty_sections(lines: List[str], skip: List[bool]) -> List[Tuple[int, str]]:
    """Find required sections with no body, including under nested headings."""
    headings = [
        (i, len(line) - len(line.lstrip("#")), HEADING.match(line).group(1))
        for i, (line, s) in enumerate(zip(lines, skip))
        if not s and HEADING.match(line)
    ]
    findings = []
    for position, (start, level, title) in enumerate(headings):
        if not any(name.lower() in title.lower() for name in SECTIONS):
            continue
        end = next(
            (i for i, depth, _ in headings[position + 1:] if depth <= level),
            len(lines),
        )
        if not any(
            line.strip()
            and not line.lstrip().startswith("```")
            and (skip[i] or not HEADING.match(line))
            for i, line in enumerate(lines[start + 1:end], start=start + 1)
        ):
            findings.append((start + 1, title))
    return findings


def empty_tables(lines: List[str], skip: List[bool]) -> List[Tuple[int, str]]:
    """A contract table carrying a header and separator but no data rows."""
    findings, i = [], 0
    while i < len(lines):
        if skip[i] or not TABLE_ROW.match(lines[i]):
            i += 1
            continue
        header = i
        if header + 1 >= len(lines) or not TABLE_SEP.match(lines[header + 1]):
            i += 1
            continue
        body = header + 2
        rows = 0
        while body < len(lines) and TABLE_ROW.match(lines[body]):
            rows += 1
            body += 1
        if rows == 0:
            findings.append((header + 1, lines[header].strip()))
        i = max(body, header + 2)
    return findings


def broken_links(
    lines: List[str], skip: List[bool], doc: pathlib.Path
) -> List[Tuple[int, str]]:
    findings = []
    for n, (line, s) in enumerate(zip(lines, skip), start=1):
        if s:
            continue
        for target in MD_LINK.findall(line):
            target = target.strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path = target.split("#", 1)[0]
            if path and not (doc.parent / path).exists():
                findings.append((n, target))
    return findings


def proposed_without_reason(lines: List[str], skip: List[bool]) -> List[Tuple[int, str]]:
    """Check each proposal within its own table cell or prose line."""
    findings = []
    for n, (line, s) in enumerate(zip(lines, skip), start=1):
        if s or "PROPOSED" not in line:
            continue
        cells = re.split(r"(?<!\\)\|", line) if TABLE_ROW.match(line) else [line]
        proposals = [
            entry
            for cell in cells
            for entry in re.split(r"(?=PROPOSED)", cell)
            if entry.startswith("PROPOSED")
        ]
        if any(not PROPOSED_REASON.match(entry) for entry in proposals):
            findings.append((n, line.strip()))
    return findings


def open_items(lines: List[str], skip: List[bool]) -> List[Tuple[int, str]]:
    return [
        (n, line.strip())
        for n, (line, s) in enumerate(zip(lines, skip), start=1)
        if not s and ("TBD" in line or "PROPOSED" in line)
    ]


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip())
        return 2

    doc = pathlib.Path(sys.argv[1])
    if not doc.is_file():
        print(f"cannot read {doc}")
        return 2

    lines = doc.read_text(encoding="utf-8").splitlines()
    skip = in_code_fence(lines)

    blocking: List[str] = []
    for name in missing_sections(lines, skip):
        blocking.append(f"missing section: {name}")
    for n, title in empty_sections(lines, skip):
        blocking.append(f"line {n}: section has no body — {title}")
    for n, header in empty_tables(lines, skip):
        blocking.append(f"line {n}: table has a header but no rows — {header}")
    for n, target in broken_links(lines, skip, doc):
        blocking.append(f"line {n}: link does not resolve — {target}")
    for n, text in proposed_without_reason(lines, skip):
        blocking.append(f"line {n}: PROPOSED without a reason — {text}")

    openers = open_items(lines, skip)

    print(f"{doc}\n")
    print(f"BLOCKING ({len(blocking)})")
    for item in blocking:
        print(f"  {item}")

    print(f"\nOPEN ({len(openers)}) — carry these into the approval request")
    for n, text in openers:
        print(f"  line {n}: {text}")

    print(
        "\nNot checked here: whether a finite domain is complete, whether a formula\n"
        "is right, whether a stated fact is true, or whether a fallback rule is\n"
        "reachable. Read for those."
    )
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
