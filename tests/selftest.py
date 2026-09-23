#!/usr/bin/env python3
"""Prove the gate can fail.

Takes a passing output, plants one known error per fixture, writes each
fixture to tests/fixtures/, runs verify.py on it, and checks that verify.py
FAILS with the expected failure code. Also checks the untouched base passes.

Usage:  python3 tests/selftest.py
Exit 0 only if the base passes and every planted error is caught.
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIX = ROOT / "tests" / "fixtures"
VERIFY = ROOT / "tests" / "verify.py"

BASES = {
    "gsa-lease": ROOT / "runs" / "gsa-lease" / "final-output.md",
    "blm-janitorial": ROOT / "runs" / "blm-janitorial" / "final-output.md",
}


def sub_once(text, old, new):
    if old not in text:
        raise SystemExit(f"selftest: base output no longer contains {old!r}; update the fixture")
    return text.replace(old, new, 1)


def drop_row(text, rid):
    lines = text.splitlines(keepends=True)
    out = [l for l in lines if not l.startswith(f"| {rid} |")]
    if len(out) == len(lines):
        raise SystemExit(f"selftest: no row {rid}")
    return "".join(out)


def row_cell(text, rid, col, new):
    lines = text.splitlines(keepends=True)
    for i, l in enumerate(lines):
        if l.startswith(f"| {rid} |"):
            cells = l.rstrip("\n").split("|")
            cells[col + 1] = f" {new} "
            lines[i] = "|".join(cells) + "\n"
            return "".join(lines)
    raise SystemExit(f"selftest: no row {rid}")


def field_body(text, fid, new_body):
    m = re.search(rf"(### {fid} [^\n]+\n)(.*?)(?=\n### |\n## )", text, re.S)
    if not m:
        raise SystemExit(f"selftest: no field {fid}")
    return text[:m.start(2)] + new_body + text[m.end(2):]


def first_row_id(text, kind):
    m = re.search(r"^\| (B\d{3}[a-z]?) \| " + kind + r" \|", text, re.M)
    return m.group(1)


# name: (base, expected failure code, mutation, what it simulates)
FIXTURES = {
    "01-converted-timezone": ("blm-janitorial", "QUOTE",
        lambda t: sub_once(sub_once(t, "Value: 09/25/2026 0800 MD\n", "Value: 09/25/2026 0800 MDT\n"),
                           "> 09/25/2026 0800 MD\n", "> 09/25/2026 0800 MDT\n"),
        "time zone 'MD' expanded to 'MDT' in both value and quote"),
    "02-value-not-in-quote": ("blm-janitorial", "A-VALUE",
        lambda t: sub_once(t, "Value: 09/25/2026 0800 MD\n", "Value: 09/25/2026 8:00 AM MT\n"),
        "value reformatted; quote left as printed"),
    "03-respelled-name": ("gsa-lease", "QUOTE",
        lambda t: t.replace("Melissa Hein", "Melissa Hine"),
        "contact name respelled everywhere it appears"),
    "04-filled-a-blank": ("gsa-lease", "QUOTE",
        lambda t: sub_once(field_body(t, "A09",
            "Value: 10/07/2026\nSource: F1 p.6\n> Questions due 10/07/2026\n"),
            "Fields not in source: A08, A09, A13, A14", "Fields not in source: A08, A13, A14"),
        "questions deadline invented, with a made-up quote to back it"),
    "05-dropped-requirement": ("gsa-lease", "B-DROPPED",
        lambda t: drop_row(t, "B005"),
        "one requirement row deleted"),
    "06-paraphrased-requirement": ("gsa-lease", "QUOTE",
        lambda t: row_cell(t, "B001", 4, "Space must be contiguous and on a single floor."),
        "requirement reworded instead of copied"),
    "07-invented-ref": ("gsa-lease", "B-REF",
        lambda t: row_cell(t, "B002", 3, "4.7.2"),
        "paragraph number created where the input prints none"),
    "08-shape-drift": ("gsa-lease", "SHAPE",
        lambda t: t.replace("### A02 Notice type", "### A02 Type of notice"),
        "field heading reworded"),
    "09-part-c-disagrees": ("gsa-lease", "C-LIST",
        lambda t: sub_once(t, "Fields not in source: A08, A09, A13, A14", "Fields not in source: A08, A13, A14"),
        "Part C summary omits a field Part A marked not in source"),
    "10-dropped-clause": ("blm-janitorial", "B-CLAUSE-DROPPED",
        lambda t: drop_row(t, first_row_id(t, "CLAUSE")),
        "one CLAUSE row deleted"),
    "11-resolved-relative-date": ("blm-janitorial", "A-VALUE",
        lambda t: sub_once(t, "Value: within seven calendar days of the issuance of the original solicitation\n",
                           "Value: 09/30/2026\n"),
        "'within seven calendar days of issuance' turned into a date"),
    "12-added-advice": ("blm-janitorial", "SHAPE",
        lambda t: t.rstrip("\n") + "\n\nRecommendation: bid. Low competition expected.\n",
        "a recommendation appended after Part C"),
    "13-conflict-missing-reads": ("blm-janitorial", "A-CONFLICT",
        lambda t: sub_once(t, "Reads: 140L5424R0001\n", ""),
        "a CONFLICT source with no Reads line"),
}


def run(path, folder):
    r = subprocess.run([sys.executable, str(VERIFY), str(path), str(folder)],
                       capture_output=True, text=True)
    return r.returncode, r.stdout


def main():
    FIX.mkdir(parents=True, exist_ok=True)
    ok = True
    for case, base in BASES.items():
        code, out = run(base, ROOT / "inputs" / case)
        status = "PASS" if code == 0 else "FAIL"
        print(f"base  {case:<16} verify={status}  (expected PASS)")
        ok &= code == 0
    for name, (case, want, mutate, what) in FIXTURES.items():
        text = mutate(BASES[case].read_text())
        path = FIX / f"{name}.md"
        path.write_text(text)
        code, out = run(path, ROOT / "inputs" / case)
        caught = code == 1 and f"FAIL {want}" in out
        first = next((l for l in out.splitlines() if l.startswith(f"FAIL {want}")), "")
        print(f"{'CAUGHT' if caught else 'MISSED'}  {name:<30} {what}")
        if first:
            print(f"        {first[:150]}")
        ok &= caught
    print("SELFTEST:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
