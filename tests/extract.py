#!/usr/bin/env python3
"""Turn every input file into checkable source text for verify.py.

verify.py imports this. Run it directly to see what the checker sees:
  python3 tests/extract.py inputs/gsa-lease/Lease_SAM.pdf

PDFs get three extractions per page (pdftotext -layout, -raw and default),
because forms read correctly in one and multi-column web pages in another.
A quote passes if it matches any of them. A .docx has no pages; it is stored as page 0.

This script only extracts. It never cleans, fixes or rewords anything; the
tolerances live in verify.py's normalize() where a reader can see them.
Requires: poppler-utils (pdftotext), python-docx.
"""
import pathlib
import subprocess
import sys



def pdf_pages(path):
    layout = subprocess.run(["pdftotext", "-layout", str(path), "-"],
                            capture_output=True, text=True, check=True).stdout
    # -raw keeps content-stream order and, unlike the default mode, does not
    # silently drop hyphens at line ends (it keeps "531120 -" and "multi-").
    raw = subprocess.run(["pdftotext", "-raw", str(path), "-"],
                         capture_output=True, text=True, check=True).stdout
    # Default mode reads some form blocks in the cleanest order, but it drops
    # hyphens at line ends; verify.py only trusts it where the others agree
    # on hyphens (see verify.py, "plain").
    plain = subprocess.run(["pdftotext", str(path), "-"],
                           capture_output=True, text=True, check=True).stdout
    sets = [x.split("\f") for x in (layout, raw, plain)]
    n = max(len(x) for x in sets)
    pages = []
    for i in range(n):
        texts = [x[i] if i < len(x) else "" for x in sets]
        if any(t.strip() for t in texts):
            pages.append({"page": i + 1, "texts": texts})
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
    if len(sys.argv) != 2:
        print(__doc__); sys.exit(2)
    f = pathlib.Path(sys.argv[1])
    if f.suffix.lower() == ".pdf":
        for p in pdf_pages(f):
            print(f"===== page {p['page']} (layout) =====")
            print(p["texts"][0])
    else:
        print(docx_text(f))


if __name__ == "__main__":
    main()
