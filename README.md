# Solicitation Translator

Turns a federal contracting notice into a **Solicitation Intake**: a fixed
three-part document a small contractor uses to decide whether to bid and to
build the response. Every value, quote and requirement is copied from the
notice, with the page it came from. If the notice doesn't say it, the output
says `not in source`.

**Who does this by hand today:** the owner or proposal coordinator at a
small government contractor. For each notice they read every page, copy the
deadline, contact and set-aside into a tracker, then copy every "shall" into
a compliance spreadsheet so nothing goes unanswered. That's hours per notice,
and one missed requirement can get a bid thrown out.

---

## Use it

1. Create a Claude project. Upload the six files in `translator/` to the
   project's knowledge: `identity.md`, `rules.md`, `examples.md`,
   `output-schema.md`, `field-definitions.md`, `trigger-phrases.md`. The
   file names matter; the folders don't.
2. Paste this into the project's custom instructions:
   `You are the Solicitation Translator. Read identity.md, then follow rules.md exactly.`
3. In a chat, attach the notice's files and say **"Run the translator."**

**What to feed it:** all the files of one notice, as **text-based PDF or
.docx**:
- the solicitation or notice document itself;
- its attachments (SOW/PWS, forms);
- for SAM.gov, the notice page: open it and use **Print → Save as PDF**,
  because the set-aside, NAICS and dates are often only on that page.

A SAM.gov link won't work: the page can't be opened from a chat, and it can
change after you run it. Save it as a PDF.

**What comes back:**

| Part | What it holds |
|---|---|
| **A. Intake sheet** | 14 fixed fields: notice number, type, title, issuing office, NAICS, set-aside, response due, submission method, questions deadline, point of contact, place of performance, period of performance, response limits, evaluation basis. Each is a verbatim value plus its source and quote, or `not in source`, or `CONFLICT` with both readings. |
| **B. Compliance matrix** | One row per requirement sentence (anything with shall / must / should / required / prohibited ...), word for word, with page, paragraph number and a blank `[HUMAN]` owner column. Standard FAR clauses get one row each, by number and title. |
| **C. Not mapped** | Documents the notice names that weren't in your files (attachments, wage determinations, forms), unreadable pages, and which fields came up empty or in conflict. |

Long notices: after 80 matrix rows it stops and asks you to reply
"continue". Join the replies into one file.

A real excerpt (BLM janitorial RFQ, `runs/blm-janitorial/run3-output.md`):

```
### A06 Set-aside
Value: CONFLICT
Source: F1 p.1 [visual]
Reads: UNRESTRICTED
Mark: marked
> 10. THIS ACQUISITION IS
> UNRESTRICTED OR
Source: F1 p.2
Reads: this requirement is set-aside specifically to Source America non-profits ...
> PURSUANT TO FAR 8.102 Mandatory source for services, this requirement is set-aside specifically to Source America non-profits ...
```

The form's box says anyone can compete; the text says only SourceAmerica
nonprofits can. The translator shows both and doesn't pick. For a bid/no-go
meeting, that's the most important line in the document.

---

## What it won't do

- **Judge.** It won't tell you whether to bid, which requirements matter,
  or who should own them. Ask it, and it says so in one line and produces
  the standard output.
- **Fix the notice.** Wrong time zones, typos, reused attachments with old
  dates and dangling phone fragments are all copied as printed.
- **Read scans.** An image-only page is listed in Part C as `UNREADABLE`.
- **Catch requirements with no trigger word.** "Test each fire hydrant ..."
  has no shall/must/should, so it gets no matrix row. The trigger list is in
  `trigger-phrases.md`; extend it if your agencies write this way.
- **Handle a full RFP in one pass.** It's built for RFQs, Sources Sought,
  Presolicitations and combined synopsis/solicitations, roughly up to 40-50
  pages. It was tested on 8, 40 and 41 pages.

---

## Check it

`tests/verify.py` checks an output against the contract and the original
files. It needs Python 3, `pdftotext` (poppler-utils) and `python-docx`.

```
python3 tests/verify.py runs/blm-janitorial/run3-output.md inputs/blm-janitorial
```

It fails the output when:
- the shape drifts;
- a value isn't inside its quote;
- a quote isn't in the input;
- a paragraph number isn't printed in the input;
- any trigger sentence or clause heading in the input has no row;
- Part C disagrees with Part A.

It lists every checkbox mark for you to confirm by eye. Its only
tolerances (whitespace, hyphens, curly quotes, one PDF font quirk) are
listed at the top of the file.

`tests/selftest.py` plants 13 known errors in passing outputs and confirms
the checker catches every one: converted time zone, respelled name,
invented deadline with a fake quote, dropped requirement, paraphrase, and
others. Results: `runs/selftest.txt`.

**What the checker cannot catch:** a value placed in the wrong field, a
conflict the translator never noticed, and whether a checkbox is really
marked. Those need a person.

---

## Proof

Three real notices from SAM.gov, public domain, not edited:

| Input | Type | Files | Result (run 3) |
|---|---|---|---|
| `inputs/va-fire-protection` | VA Sources Sought, fire alarm maintenance | 1 .docx, 41 pp | PASS: 150 rows, 2 fields not in source |
| `inputs/blm-janitorial` | BLM RFQ on SF 1449 + PWS | 2 PDFs, 40 pp | PASS: 176 rows, 3 conflicts found |
| `inputs/gsa-lease` | GSA lease Presolicitation, SAM.gov page | 1 PDF, 8 pp | PASS: 24 rows, 4 fields not in source |

- **Predictions:** written and committed before the first run
  (`runs/PREDICTIONS.md`).
- **Every run is kept, including the failures:** runs 1 and 2 failed, for
  reasons explained in `runs/RUN-LOG.md`.
- **Invented facts across all nine outputs: zero.**

---

## Repo map

```
translator/          the product: drop these six files into a Claude project
  identity.md        what it converts, from what, to what
  rules.md           how each part of the input maps to the output
  examples.md        three short worked cases and the failure modes
  reference/
    output-schema.md      the contract: exact shape of the output
    field-definitions.md  what each Part A field holds and where to look
    trigger-phrases.md    what counts as a requirement; clause rule
inputs/              three real notices, as downloaded
tests/               kept apart from translator/ so the translator never sees them
  verify.py          the checker
  selftest.py        plants errors, proves the checker fails
  extract.py         the text extraction verify.py uses
  fixtures/          the 13 planted-error outputs
runs/                every run's output and checker result, predictions, log
```

MIT licensed.
