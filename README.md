# Solicitation Translator

Give it a federal contracting notice from SAM.gov. It gives back three things:
the 14 facts you need for a bid decision (deadline, set-aside, contact ...),
every requirement sentence word for word as a compliance checklist, and a
list of documents the notice names but you don't have. Every line quotes the
notice and gives the page. If the notice doesn't say it, the output says
`not in source`.

**Who does this by hand today:** the owner or proposal coordinator at a
small government contractor. For each notice they read every page, copy the
deadline, contact and set-aside into a tracker, then copy every "shall" into
a compliance spreadsheet so nothing goes unanswered. That's hours per notice,
and one missed requirement can get a bid thrown out.

---

## Use it (about 2 minutes)

1. **Make a Claude project** on claude.ai.
2. **Add the translator to the project's knowledge.** Only the
   [`translator/`](translator/) folder goes in; the rest of this repo holds
   test answers. Pick one way:
   - **From GitHub (easiest):** in the project's knowledge, click
     **+ → GitHub**, paste this repo's URL and select only the
     `translator` folder. Claude asks you to sign in to GitHub the first
     time. **Sync** picks up later updates.
   - **Upload by hand:** on GitHub, **Code → Download ZIP** and unzip it.
     Drag these seven files into the project's knowledge, and nothing else:
     `AGENTS.md`, `identity.md`, `rules.md`, `examples.md` from
     `translator/`, and `output-schema.md`, `field-definitions.md`,
     `trigger-phrases.md` from `translator/reference/`. Don't upload the
     ZIP itself.
3. **Paste this into the project's custom instructions:**
   ```
   You are the Solicitation Translator. Read identity.md, then follow rules.md exactly.
   ```
4. **Start a chat, attach the notice's files and say "Run the translator."**
   Use PDF or .docx files. A SAM.gov link won't work (see below).
5. **Save the reply as a `.md` file.** If it ends with
   `CONTINUED: reply "continue" ...`, send "continue" and paste each part
   into the same file in order. The `CONTINUED` lines can stay; the checker
   skips them.

Want to see a finished output first? Open
[`runs/blm-janitorial/run4-output.md`](runs/blm-janitorial/run4-output.md).

The runs in this repo were made with Claude Opus 5.5.

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

**How to read it:**
- **File numbers:** F1, F2 ... are your files, in the order you attached
  them, listed at the top.
- **Values and quotes:** each `Value:` is copied from the notice. The `> `
  lines under `Source:` are the notice's own words it came from. A PDF
  source gives the page (`p.3`); a .docx source gives the nearest heading,
  since Word files have no fixed pages.
- **Conflicts:** `CONFLICT` means two places disagree. Each gets a `Reads:`
  line with what it says, and the translator doesn't pick.
- **Checkboxes:** `[visual]` with `Mark: marked` means the fact is a
  checkbox, which only the page image shows.

A real excerpt (BLM janitorial RFQ, `runs/blm-janitorial/run4-output.md`):

```
### A06 Set-aside
Value: CONFLICT
Source: F1 p.1 [visual]
Reads: UNRESTRICTED OR
Mark: marked
> 10. THIS ACQUISITION IS
> UNRESTRICTED OR
Source: F1 p.2
Reads: PURSUANT TO FAR 8.102 Mandatory source for services, this requirement is set-aside specifically to Source America non-profits ...
> PURSUANT TO FAR 8.102 Mandatory source for services, this requirement is set-aside specifically to Source America non-profits ...
> No other participants are authorized for award.
Source: F1 p.6
Reads: Notice of Total Small Business Set-Aside.
> 52.219-6 Notice of Total Small Business Set-Aside. (NOV 2020) (Deviation JAN 2026)
```

The form's box says anyone can compete, the text says only SourceAmerica
nonprofits can, and a clause says small businesses only. The translator shows both and doesn't pick. For a bid/no-go
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
files. It needs Python 3, `pdftotext` and `python-docx`:

```
pip install python-docx
brew install poppler          # macOS;  on Linux: apt install poppler-utils
```

Check a shipped run:

```
python3 tests/verify.py runs/blm-janitorial/run4-output.md inputs/blm-janitorial
```

To check your own run, make a folder holding exactly the files you
attached, with the same names, and point the checker at it:

```
python3 tests/verify.py my-intake.md my-notice-folder/
```

It fails the output when:
- the shape drifts;
- a value isn't inside its quote;
- a quote isn't in the input;
- a paragraph number isn't printed in the input;
- any trigger sentence or clause heading in the input has no row;
- Part C disagrees with Part A.

It ends with a **CHECK BY EYE** list: every checkbox the output relies on.
Open the cited page and confirm the X is in the box named. Its only
tolerances are listed at the top of `verify.py`:
- whitespace;
- curly quotes;
- word-wrap hyphens at line ends;
- one PDF font quirk.

Every other character counts, hyphens included: `404-273-1268` does not
match `4042731268`.

`tests/selftest.py` plants 16 known errors in passing outputs and confirms
the checker catches every one. The planted errors include a converted time
zone, a respelled name, an invented deadline with a fake quote, a dropped
requirement, a paraphrase, and a reformatted phone number. Run it with
`python3 tests/selftest.py`; saved results are in `runs/selftest.txt`.

**What the checker cannot catch:** a value placed in the wrong field, a
conflict the translator never noticed, and whether a checkbox is really
marked. Those need a person.

---

## Proof

Three real notices from SAM.gov, public domain, not edited:

| Input | Type | Files | Result (run 4, current contract) |
|---|---|---|---|
| `inputs/va-fire-protection` | VA Sources Sought, fire alarm maintenance | 1 .docx, 41 pp | PASS: 150 rows, 2 fields not in source |
| `inputs/blm-janitorial` | BLM RFQ on SF 1449 + PWS | 2 PDFs, 40 pp | PASS: 188 rows, 3 conflicts found |
| `inputs/gsa-lease` | GSA lease Presolicitation, SAM.gov page | 1 PDF, 8 pp | PASS: 24 rows, 4 fields not in source |

- **Predictions:** written and committed before the first run
  (`runs/PREDICTIONS.md`).
- **Every run is kept, including the failures:** four runs per notice.
  Runs 1 and 2 failed, and an independent audit after run 3 found a hole
  in the checker. All of it is explained in `runs/RUN-LOG.md`.
- **Refusal on record:** run 5 asked "Should we bid on this? Also convert
  the deadline to Manila time." The translator declined both in one line
  and produced the standard intake, which passes the checker
  (`runs/gsa-lease/run5-disguised-ask-reply.md`).
- **Invented facts across all thirteen outputs: zero.** No value, date, name
  or number appeared that the notice doesn't print. One run joined two
  printed phone fragments into one number; the log covers it and the rule
  that now prevents it.

---

## Repo map

```
AGENTS.md            for an agent working in the repo: where to go, what not to read
translator/          the product: drop these seven files into a Claude project
  AGENTS.md          entry file: tells any agent to start at identity.md
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
  fixtures/          the 16 planted-error outputs
runs/                every run's output and checker result, predictions, log
```

MIT licensed.
