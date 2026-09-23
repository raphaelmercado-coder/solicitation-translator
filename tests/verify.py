#!/usr/bin/env python3
"""Check a translator output against its input files and the contract.

Usage:
  python3 tests/verify.py <output.md> <input folder>
  e.g. python3 tests/verify.py runs/blm-janitorial/output.md inputs/blm-janitorial

Exit code 0 = PASS, 1 = FAIL. Prints every failure, every warning, and every
visual mark a person must confirm by eye.

What it checks (the contract is translator/reference/output-schema.md):
  SHAPE     header, three parts, fourteen fields in order, table headers
  FILES     every input file is listed; no listed file is missing
  A-*       every Value sits inside its quote; every quote sits in the input;
            'not in source' carries no source; CONFLICT has 2+ sources, each
            with a Reads line inside its quote
  B-*       IDs in sequence; every row's text sits in the input; every Ref is
            printed in the input; every trigger-phrase sentence in the input
            (outside clause text and exempt spans) appears in a REQ row;
            every clause heading appears in a CLAUSE row
  C-*       the 'not in source' and 'conflict' lists match Part A; every
            quote sits in the input

Matching tolerances (the only ones; both sides get the same treatment):
  - Unicode compatibility forms folded (NFKC); curly quotes made straight;
    all dash characters made '-'
  - '!' between two letters read as 'ff' (some PDF fonts lose the ff
    ligature on extraction: 'o!ice' is 'office')
  - all whitespace, hyphens, bullet characters and the Markdown characters
    * _ ` \\ ignored
  - repeated page headers/footers and bare page numbers removed at page edges
    (quotes are also checked against the unstripped text)
  - a quote may be split into fragments, one per '> ' line; each fragment
    must match exactly and all must sit within 2,500 characters of each
    other on the cited pages (form labels and their values)
  - for a [visual] mark only, the label's words may be split across form
    lines; each word must be found near the others
  Case is NOT ignored. Spelling is NOT ignored. Word order is NOT ignored.
"""
import pathlib
import re
import sys
import unicodedata

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
REF = ROOT / "translator" / "reference" / "trigger-phrases.md"
sys.path.insert(0, str(HERE))
import extract  # noqa: E402

FIELDS = [
    "A01 Notice number", "A02 Notice type", "A03 Title", "A04 Issuing office",
    "A05 NAICS code", "A06 Set-aside", "A07 Response due",
    "A08 Submission method", "A09 Questions deadline", "A10 Point of contact",
    "A11 Place of performance", "A12 Period of performance",
    "A13 Response limits", "A14 Evaluation basis",
]
B_HEADER = "| ID | Kind | Source | Ref | Requirement | Owner |"
C_HEADER = "| ID | Kind | Source | Quote |"
C_KINDS = {"NOT SUPPLIED", "UNREADABLE", "PIPE REPLACED", "NONE"}


# ---------------------------------------------------------------- matching
def normalize(s):
    s = unicodedata.normalize("NFKC", s)
    s = s.translate(str.maketrans({
        "‘": "'", "’": "'", "“": '"', "”": '"',
        "–": "-", "—": "-", "−": "-", "‐": "-",
        "‑": "-", " ": " ",
    }))
    s = re.sub(r"(?<=[A-Za-z])!(?=[A-Za-z])", "ff", s)
    return re.sub(r"[\s\-*_`\\\u2022\u25aa\u25cf\uf0b7]+", "", s)


def read_blocks(kind):
    text = REF.read_text()
    m = re.search(r"```" + kind + r"\n(.*?)```", text, re.S)
    return [l.strip() for l in m.group(1).splitlines() if l.strip()] if m else []


def clean_pages(pages):
    """Drop repeated header/footer lines and bare page numbers at page edges."""
    if len(pages) < 3:
        return pages
    def edges(lines):
        idx = [i for i, l in enumerate(lines) if l.strip()]
        return set(idx[:3] + idx[-3:])
    counts = {}
    split = [p.splitlines() for p in pages]
    for lines in split:
        for i in edges(lines):
            k = re.sub(r"\d+", "#", " ".join(lines[i].split()))
            counts[k] = counts.get(k, 0) + 1
    out = []
    for lines in split:
        drop = set()
        for i in edges(lines):
            s = " ".join(lines[i].split())
            k = re.sub(r"\d+", "#", s)
            if re.fullmatch(r"\d{1,3}", s) or (counts.get(k, 0) >= 3 and len(s) < 90):
                drop.add(i)
        out.append("\n".join(l for i, l in enumerate(lines) if i not in drop))
    return out


class Source:
    """One input file: text per page, in several extraction variants.

    PDF variants: layout and plain extraction, each with and without page
    header/footer removal. A quote passes if it is found in any variant.
    """
    WINDOW = 2500   # max spread, in normalized characters, of one quote's fragments

    def __init__(self, path):
        self.name = path.name
        if path.suffix.lower() == ".pdf":
            self.kind = "pdf"
            pages = extract.pdf_pages(path)
            n = max(p["page"] for p in pages)
            self.variants = []
            for v in range(2):
                bypage = {p["page"]: p["texts"][v] for p in pages}
                seq = [bypage.get(i, "") for i in range(1, n + 1)]
                self.variants.append(clean_pages(seq))
            for v in range(2):
                bypage = {p["page"]: p["texts"][v] for p in pages}
                self.variants.append([bypage.get(i, "") for i in range(1, n + 1)])
        else:
            self.kind = "docx"
            self.variants = [[extract.docx_text(path)]]
        self.norm = [[normalize(p) for p in var] for var in self.variants]
        self.full = ["".join(var) for var in self.norm]

    def npages(self):
        return len(self.variants[0])

    def _ranges(self, pages):
        if self.kind != "pdf" or not pages:
            return [("ok", None)]
        a, b = pages
        return [("ok", (max(a, 1), min(b, self.npages()))),
                ("near", (max(a - 1, 1), min(b + 1, self.npages())))]

    @staticmethod
    def _together(hay, frags, window):
        """True if every fragment occurs in hay, all within `window` chars."""
        occ = []
        for f in frags:
            pos = [m.start() for m in re.finditer(re.escape(f), hay)]
            if not pos:
                return False
            occ.append((pos, len(f)))
        for p0 in occ[0][0]:
            if all(any(abs(p - p0) <= window for p in pos) for pos, _ in occ[1:]):
                return True
        return False

    def find(self, text, pages=None):
        """One contiguous run of text. 'ok', 'near', 'elsewhere' or 'missing'."""
        return self.find_frags([text], pages)

    def find_frags(self, frags, pages=None):
        """Each fragment must occur verbatim; all within WINDOW of each other."""
        fr = [normalize(f) for f in frags if normalize(f)]
        if not fr:
            return "missing"
        for status, rng in self._ranges(pages):
            for var in self.norm:
                hay = "".join(var) if rng is None else "".join(var[rng[0] - 1:rng[1]])
                if self._together(hay, fr, self.WINDOW):
                    return status
        if any(self._together(f, fr, self.WINDOW) for f in self.full):
            return "elsewhere"
        return "missing"

    def coverage_text(self):
        """Plain extraction for PDF (better reading order), headers removed."""
        var = self.variants[1] if self.kind == "pdf" else self.variants[0]
        return "\n".join(var)


# ---------------------------------------------------------------- parsing
class Report:
    def __init__(self):
        self.fails, self.warns, self.visual = [], [], []
    def fail(self, code, msg): self.fails.append(f"FAIL {code}: {msg}")
    def warn(self, code, msg): self.warns.append(f"WARN {code}: {msg}")


LOC = re.compile(r"^(F\d+)(?:\s+(.*?))?\s*(\[visual\])?\s*$")


def parse_loc(loc_text, files, rep, where):
    m = LOC.match(loc_text.strip())
    if not m or m.group(1) not in files:
        rep.fail("SOURCE", f"{where}: bad source '{loc_text}'")
        return None, None, False
    f = files[m.group(1)]
    pages = None
    rest = m.group(2) or ""
    pm = re.match(r"p\.(\d+)(?:-(\d+))?", rest)
    if f.kind == "pdf":
        if not pm:
            rep.fail("SOURCE", f"{where}: PDF source needs p.N, got '{loc_text}'")
        else:
            a = int(pm.group(1)); b = int(pm.group(2) or a)
            if not (1 <= a <= b <= f.npages()):
                rep.fail("SOURCE", f"{where}: page out of range '{loc_text}'")
            pages = (a, b)
    return f, pages, bool(m.group(3))


def check_quote(f, pages, frags, rep, where):
    if isinstance(frags, str):
        frags = [frags]
    r = f.find_frags(frags, pages)
    if r == "missing":
        shown = " / ".join(frags)
        rep.fail("QUOTE", f"{where}: not in {f.name}: \"{shown[:140]}\"")
        return False
    if r in ("near", "elsewhere"):
        rep.warn("LOCATOR", f"{where}: found in {f.name} but not on the cited page(s)")
    return True


def split_parts(text, rep):
    heads = ["## Part A: Intake sheet", "## Part B: Compliance matrix", "## Part C: Not mapped"]
    pos = [text.find(h) for h in heads]
    if -1 in pos or pos != sorted(pos):
        rep.fail("SHAPE", "Parts A, B, C missing or out of order (exact headings required)")
        return None
    return text[:pos[0]], text[pos[0]:pos[1]], text[pos[1]:pos[2]], text[pos[2]:]


def parse_header(head, folder, rep):
    if "# Solicitation Intake" not in head:
        rep.fail("SHAPE", "missing '# Solicitation Intake' title")
    if "Schema: solicitation-translator v1" not in head:
        rep.fail("SHAPE", "missing 'Schema: solicitation-translator v1'")
    files = {}
    for m in re.finditer(r"^- (F\d+) = (.+?)\s*$", head, re.M):
        p = folder / m.group(2)
        if not p.exists():
            rep.fail("FILES", f"{m.group(1)} = '{m.group(2)}' is not in {folder}")
            continue
        files[m.group(1)] = Source(p)
    listed = {f.name for f in files.values()}
    for p in sorted(folder.iterdir()):
        if p.suffix.lower() in (".pdf", ".docx") and p.name not in listed:
            rep.fail("FILES", f"input file '{p.name}' is not listed in the header")
    return files


def parse_part_a(block, files, rep):
    heads = re.findall(r"^### (A\d\d .+?)\s*$", block, re.M)
    if heads != FIELDS:
        rep.fail("SHAPE", f"Part A fields must be exactly {len(FIELDS)} in order; got {heads}")
    status = {}
    chunks = re.split(r"^### (A\d\d .+?)\s*$", block, flags=re.M)[1:]
    for name, body in zip(chunks[0::2], chunks[1::2]):
        fid = name[:3]
        lines = [l.rstrip() for l in body.strip().splitlines() if l.strip()]
        values = [l[len("Value:"):].strip() for l in lines if l.startswith("Value:")]
        if not values:
            rep.fail("A-VALUE", f"{fid}: no Value line"); continue
        # group into source blocks
        blocks, cur = [], None
        for l in lines:
            if l.startswith("Source:"):
                cur = {"loc": l[len("Source:"):].strip(), "quote": [], "reads": None, "mark": None}
                blocks.append(cur)
            elif cur and l.startswith(">"):
                cur["quote"].append(l[1:].strip())
            elif cur and l.startswith("Reads:"):
                cur["reads"] = l[len("Reads:"):].strip()
            elif cur and l.startswith("Mark:"):
                cur["mark"] = l[len("Mark:"):].strip()
            elif l.startswith("Value:"):
                if cur:
                    rep.fail("A-SHAPE", f"{fid}: Value line after a Source block")
            else:
                rep.fail("A-SHAPE", f"{fid}: unexpected line '{l[:80]}'")
        if values == ["not in source"]:
            status[fid] = "nis"
            if blocks:
                rep.fail("A-NIS", f"{fid}: 'not in source' must have no Source lines")
            continue
        if "not in source" in values or ("CONFLICT" in values and len(values) > 1):
            rep.fail("A-VALUE", f"{fid}: 'not in source'/'CONFLICT' must be the only Value")
            continue
        if not blocks:
            rep.fail("A-SOURCE", f"{fid}: filled field has no Source"); continue
        quotes = []
        for i, b in enumerate(blocks, 1):
            where = f"{fid} source {i}"
            f, pages, visual = parse_loc(b["loc"], files, rep, where)
            q = " ".join(b["quote"])
            if not q:
                rep.fail("A-QUOTE", f"{where}: no quote"); continue
            if f:
                if visual and f.find_frags(b["quote"], pages) == "missing":
                    # Form labels wrap across grid lines; for a visual mark
                    # accept the label's words, each found near the others.
                    words = " ".join(b["quote"]).split()
                    check_quote(f, pages, words, rep, where)
                else:
                    check_quote(f, pages, b["quote"], rep, where)
            if visual:
                if b["mark"] not in ("marked", "not marked"):
                    rep.fail("A-VISUAL", f"{where}: [visual] needs 'Mark: marked' or 'Mark: not marked'")
                rep.visual.append(f"{fid} {b['loc']}: \"{q[:80]}\" -> {b['mark']}")
            quotes.append("".join(normalize(x) for x in b["quote"]))
            if b["reads"] is not None and normalize(b["reads"]) not in quotes[-1]:
                rep.fail("A-READS", f"{where}: Reads '{b['reads'][:80]}' is not inside its quote")
        if values == ["CONFLICT"]:
            status[fid] = "conflict"
            if len(blocks) < 2:
                rep.fail("A-CONFLICT", f"{fid}: CONFLICT needs 2+ Source blocks")
            if any(b["reads"] is None for b in blocks):
                rep.fail("A-CONFLICT", f"{fid}: every Source under CONFLICT needs a Reads line")
            continue
        status[fid] = "filled"
        for v in values:
            if not any(normalize(v) in q for q in quotes):
                rep.fail("A-VALUE", f"{fid}: Value '{v[:80]}' is not inside any of its quotes")
    return status


def table_rows(block, header, rep, part):
    lines = [l.strip() for l in block.splitlines()]
    if header not in lines:
        rep.fail("SHAPE", f"Part {part} table header must be exactly: {header}")
        return []
    rows = []
    ncol = header.count("|") - 1
    for l in lines[lines.index(header) + 2:]:
        if not l or l.startswith("CONTINUED:"):
            continue
        if not l.startswith("|"):
            rep.fail("SHAPE", f"Part {part}: unexpected line '{l[:80]}'")
            continue
        cells = [c.strip() for c in l.strip("|").split("|")]
        if len(cells) != ncol:
            rep.fail("SHAPE", f"Part {part}: row has {len(cells)} cells, expected {ncol}: '{l[:80]}'")
            continue
        rows.append(cells)
    return rows


def clause_spans(text, head_re, sec_re):
    """Return (list of heading numbers, list of (start, end) char spans)."""
    lines = text.splitlines(keepends=True)
    offs, pos = [], 0
    for l in lines:
        offs.append(pos); pos += len(l)
    heads, starts, stops = [], [], []
    for i, l in enumerate(lines):
        if re.match(head_re, l):
            heads.append(re.search(r"(\d+\.\d{3}-\d+)", l).group(1))
            starts.append(offs[i])
        elif re.match(sec_re, l):
            stops.append(offs[i])
    spans = []
    marks = sorted([(s, "h") for s in starts] + [(s, "x") for s in stops])
    for j, (s, k) in enumerate(marks):
        if k != "h":
            continue
        end = marks[j + 1][0] if j + 1 < len(marks) else len(text)
        spans.append((s, end))
    return heads, spans


def exempt_spans(text, rules):
    spans = []
    for r in rules:
        a, b = [x.strip() for x in r.split("=>")]
        i = text.find(a)
        while i != -1:
            j = len(text) if b == "<EOF>" else text.find(b, i)
            j = len(text) if j == -1 else j
            spans.append((i, j))
            i = text.find(a, j)
    return spans


def trigger_windows(text, triggers, skip, line_is_paragraph=False):
    """For each trigger outside `skip`: (pos, window, right_key).

    window    = up to 3 words before + trigger + up to 4 words after, clipped
                to the sentence (and, for .docx, to the paragraph line).
    right_key = trigger + up to 4 words after.
    """
    pat = re.compile(r"\b(" + "|".join(re.escape(t) for t in triggers) + r")\b", re.I)
    stop = r"[.!?;:]\s|\n\s*\n" + (r"|\n" if line_is_paragraph else "")
    out = []
    for m in pat.finditer(text):
        if any(a <= m.start() < b for a, b in skip):
            continue
        left = re.split(stop, text[max(0, m.start() - 200):m.start()])[-1]
        right = re.split(r"[.!?;:](?:\s|$)|\n\s*\n" + (r"|\n" if line_is_paragraph else ""),
                         text[m.end():m.end() + 200])[0]
        lw, rw = left.split()[-3:], right.split()[:4]
        out.append((m.start(), " ".join(lw + [m.group(0)] + rw), " ".join([m.group(0)] + rw)))
    return out


def parse_part_b(block, files, rep):
    rows = table_rows(block, B_HEADER, rep, "B")
    triggers = read_blocks("triggers")
    head_re = read_blocks("clause-heading")[0]
    sec_re = "|".join("(?:%s)" % r for r in read_blocks("section-marker"))
    exempt = read_blocks("exempt")
    expect = 1
    req_by_file, clause_by_file = {}, {}
    for cells in rows:
        rid, kind, loc, ref, text, owner = cells
        m = re.fullmatch(r"B(\d{3})([a-z]?)", rid)
        if not m:
            rep.fail("B-ID", f"bad ID '{rid}'"); continue
        n, sub = int(m.group(1)), m.group(2)
        if sub:
            if n != expect - 1:
                rep.fail("B-ID", f"{rid}: list item does not follow its parent")
        else:
            if n != expect:
                rep.fail("B-ID", f"{rid}: expected B{expect:03d}")
            expect = n + 1
        if kind not in ("REQ", "CLAUSE"):
            rep.fail("B-KIND", f"{rid}: Kind must be REQ or CLAUSE, got '{kind}'")
        if owner != "[HUMAN]":
            rep.fail("B-OWNER", f"{rid}: Owner must be [HUMAN]")
        f, pages, _ = parse_loc(loc, files, rep, rid)
        if not f:
            continue
        check_quote(f, pages, text, rep, rid)
        if ref != "-" and f.find(ref) == "missing":
            rep.fail("B-REF", f"{rid}: Ref '{ref}' is not printed in {f.name}")
        if kind == "CLAUSE":
            cm = re.match(r"\s*(?:(?:FAR|DFARS|VAAR)\s+)?((?:52|552|852|1452)\.\d{3}-\d{1,3})\b", text)
            if not cm:
                rep.fail("B-CLAUSE", f"{rid}: CLAUSE row must start with the clause number")
            else:
                clause_by_file.setdefault(f.name, set()).add(cm.group(1))
        else:
            req_by_file.setdefault(f.name, []).append(normalize(text))
    # coverage: nothing dropped
    dropped = 0
    for f in files.values():
        text = f.coverage_text()
        heads, cspans = clause_spans(text, head_re, sec_re)
        skip = cspans + exempt_spans(text, exempt)
        have = set(clause_by_file.get(f.name, set()))
        for h in sorted(set(heads)):
            if h not in have:
                rep.fail("B-CLAUSE-DROPPED", f"clause {h} in {f.name} has no CLAUSE row")
        reqs = req_by_file.get(f.name, [])
        wins = trigger_windows(text, triggers, skip, f.kind == "docx")
        # Fallback for windows whose left words are a heading, list number or
        # page furniture the row rightly leaves out: the trigger and the four
        # words after it must appear in REQ rows at least as many times as
        # they appear in the input (so one row cannot cover two sentences).
        need, seen = {}, {}
        for _, _, rk in wins:
            k = normalize(rk); need[k] = need.get(k, 0) + 1
        for k in need:
            seen[k] = sum(r.count(k) for r in reqs)
        for pos, window, rk in wins:
            if any(normalize(window) in r for r in reqs):
                continue
            k = normalize(rk)
            if seen[k] >= need[k]:
                continue
            dropped += 1
            rep.fail("B-DROPPED", f"{f.name}: no REQ row contains \"{window}\"")
    return len(rows), dropped


def parse_part_c(block, files, status, rep):
    def listed(label):
        m = re.search(r"^" + label + r":\s*(.+)$", block, re.M)
        if not m:
            rep.fail("C-SHAPE", f"missing '{label}:' line"); return None
        v = m.group(1).strip()
        return set() if v == "none" else {x.strip() for x in v.split(",")}
    nis = listed("Fields not in source")
    con = listed("Fields in conflict")
    want_nis = {k for k, v in status.items() if v == "nis"}
    want_con = {k for k, v in status.items() if v == "conflict"}
    if nis is not None and nis != want_nis:
        rep.fail("C-LIST", f"'Fields not in source' says {sorted(nis)}, Part A has {sorted(want_nis)}")
    if con is not None and con != want_con:
        rep.fail("C-LIST", f"'Fields in conflict' says {sorted(con)}, Part A has {sorted(want_con)}")
    rows = table_rows(block, C_HEADER, rep, "C")
    for cells in rows:
        cid, kind, loc, quote = cells
        if kind not in C_KINDS:
            rep.fail("C-KIND", f"{cid}: unknown kind '{kind}'")
        if kind in ("NOT SUPPLIED", "PIPE REPLACED") and loc != "-":
            f, pages, _ = parse_loc(loc, files, rep, cid)
            if f:
                check_quote(f, pages, quote, rep, cid)
    return len(rows)


def main():
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(2)
    out = pathlib.Path(sys.argv[1]); folder = pathlib.Path(sys.argv[2])
    rep = Report()
    text = out.read_text()
    parts = split_parts(text, rep)
    nrows = ncrows = dropped = 0
    status = {}
    if parts:
        head, a, b, c = parts
        files = parse_header(head, folder, rep)
        if files:
            status = parse_part_a(a, files, rep)
            nrows, dropped = parse_part_b(b, files, rep)
            ncrows = parse_part_c(c, files, status, rep)
    filled = sum(1 for v in status.values() if v == "filled")
    print(f"verify.py  {out}  against  {folder}")
    print(f"Part A: {filled} filled, "
          f"{sum(1 for v in status.values() if v == 'nis')} not in source, "
          f"{sum(1 for v in status.values() if v == 'conflict')} conflict")
    print(f"Part B: {nrows} rows, {dropped} requirement(s) dropped")
    print(f"Part C: {ncrows} rows")
    for l in rep.fails: print(l)
    for l in rep.warns: print(l)
    if rep.visual:
        print("CHECK BY EYE (visual marks the text cannot prove):")
        for l in rep.visual: print("  " + l)
    print("RESULT:", "FAIL" if rep.fails else "PASS",
          f"({len(rep.fails)} failure(s), {len(rep.warns)} warning(s))")
    sys.exit(1 if rep.fails else 0)


if __name__ == "__main__":
    main()
