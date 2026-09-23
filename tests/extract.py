#!/usr/bin/env python3
"""Turn every input file into checkable source text for verify.py.

Usage:  python3 tests/extract.py            (all cases under inputs/)

Writes tests/source/<case>/<file name>.json:
  {"file": "...", "kind": "pdf"|"docx",
   "pages": [{"page": 1, "texts": ["<layout text>", "<raw text>"]}, ...]}

PDFs get two extractions per page (pdftotext -layout and plain), because
forms read correctly in one and multi-column web pages in the other. A quote
passes if it matches either. A .docx has no pages; it is stored as page 0.

This script only extracts. It never cleans, fixes or rewords anything; the
tolerances live in verify.py's normalize() where a reader can see them.
Requires: poppler-utils (pdftotext), python-docx.
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
INPUTS = ROOT / "inputs"
OUT = ROOT / "tests" / "source"


def pdf_pages(path):
    layout = subprocess.run(["pdftotext", "-layout", str(path), "-"],
                            capture_output=True, text=True, check=True).stdout
    raw = subprocess.run(["pdftotext", str(path), "-"],
                         capture_output=True, text=True, check=True).stdout
    lp, rp = layout.split("\f"), raw.split("\f")
    n = max(len(lp), len(rp))
    pages = []
    for i in range(n):
        a = lp[i] if i < len(lp) else ""
        b = rp[i] if i < len(rp) else ""
        if a.strip() or b.strip():
            pages.append({"page": i + 1, "texts": [a, b]})
    return pages


def docx_text(path):
    import docx
    from docx.oxml.ns import qn
    d = docx.Document(str(path))
    parts = []
    # Walk the body in document order so tables sit where they appear.
    for block in d.element.body.iterchildren():
        if block.tag == qn("w:p"):
            parts.append("".join(t.text or "" for t in block.iter(qn("w:t"))))
        elif block.tag == qn("w:tbl"):
            for row in block.iter(qn("w:tr")):
                seen = []
                for cell in row.iter(qn("w:tc")):
                    paras = ["".join(t.text or "" for t in p.iter(qn("w:t")))
                             for p in cell.iter(qn("w:p"))]
                    txt = "\n".join(p for p in paras)
                    if txt not in seen:          # merged cells repeat
                        seen.append(txt)
                parts.append("\n".join(seen))
    return "\n".join(parts)


def main():
    cases = [p for p in sorted(INPUTS.iterdir()) if p.is_dir()]
    for case in cases:
        dest = OUT / case.name
        dest.mkdir(parents=True, exist_ok=True)
        for f in sorted(case.iterdir()):
            if f.suffix.lower() == ".pdf":
                rec = {"file": f.name, "kind": "pdf", "pages": pdf_pages(f)}
            elif f.suffix.lower() == ".docx":
                t = docx_text(f)
                rec = {"file": f.name, "kind": "docx",
                       "pages": [{"page": 0, "texts": [t]}]}
            else:
                print(f"skip {f} (not .pdf or .docx)", file=sys.stderr)
                continue
            (dest / (f.name + ".json")).write_text(json.dumps(rec, indent=1))
            chars = sum(len(p["texts"][0]) for p in rec["pages"])
            print(f"{case.name}/{f.name}: {len(rec['pages'])} page(s), {chars} chars")


if __name__ == "__main__":
    main()
