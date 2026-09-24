# Run log

Every run, including the ones that failed. Nothing is deleted or re-run
quietly. The predictions in `PREDICTIONS.md` were committed before run 1.

## How each run was done

- **Clean room.** For each run, a fresh Claude agent got a folder holding
  only `translator/` and that notice's input files. It could not see
  `tests/`, `runs/`, this log or the README. It was told what a user in a
  Claude project would say ("Here is a notice. Run the translator.") and to
  follow the translator files exactly.
- **One exception to the product rules:** the agents wrote the whole output
  to one file instead of splitting it every 80 rows (rule 7), so the output
  could be checked in one piece.
- **Checked by `tests/verify.py`,** which never sees the agent's reasoning,
  only the output file and the original input files.

## Results

| Input | Run 1 | Run 2 | Run 3 | Run 4 (current contract) |
|---|---|---|---|---|
| VA fire protection, Sources Sought (.docx) | FAIL 3, then PASS on checker v2 | FAIL 6 | PASS, 150 rows | **PASS**, 150 rows |
| BLM janitorial, RFQ + PWS (2 PDFs, 40 pp) | FAIL 15, then FAIL 7 on checker v2 | PASS | PASS, 176 rows | **PASS**, 188 rows |
| GSA office lease, Presolicitation (SAM.gov page) | FAIL 10, then FAIL 9 on checker v2 | PASS | PASS, 24 rows | FAIL 7 on checker v3, then **PASS**, 24 rows |

**Invented facts found in any run: zero.** Across the twelve outputs, every
failure was a dropped requirement, a formatting break, a quote joined across
form boxes, or a checker bug. No value, date, name or number appeared that
the input does not contain.

`selftest.txt`: the checker catches **16 of 16** planted errors
(converted time zone, respelled name, invented deadline with a fake quote,
dropped requirement, paraphrase, invented paragraph number, shape drift,
Part C lying about Part A, dropped clause, resolved relative date, appended
advice, conflict without its readings, value reformatted away from its
quote, and three hyphen tricks on phone numbers and IDs).

## Run 1: what failed and whose fault it was

`runX-verify.txt` is the checker as it stood at that run.
`run1-verify-checker-v2.txt` is the same run 1 output re-checked after the
checker's own bugs were fixed. Both are kept.

**Checker bugs (fixed in v2):**
- Page-header stripping also removed headers from the text used to check
  Part A quotes, so a correct quote of a page header failed. Quotes are now
  checked against both stripped and unstripped text.
- The coverage check read a heading line above a sentence ("APPLICATIONS",
  "PERSONNEL") or a list number ("4)") as part of the sentence. It now falls
  back to the trigger plus the next four words, counted so that one row
  cannot cover two sentences.
- An SF 1449 clause-by-reference line ("FAR 52.212-3 AND 52.212-5 ARE
  ATTACHED") was read as a clause heading.
- A clause's text ran on past the next contract section (E.1.0) when the
  clause had no "(End of clause)" line.

**Translator misses (fixed in the contract):**
- **BLM: three requirement sentences dropped.** A definition containing
  "will be evaluated", a sentence naming "FAR Part 8 - Required Sources of
  Supplies", and "A COR ... will be appointed ... the workmanship required
  under this contract". The rules now say plainly that the trigger decides,
  including in sentences that don't look like obligations.
- **BLM: a clause heading prefixed "FAR 52.222-90"** was not treated as a
  clause. The heading rule now allows a `FAR`/`DFARS`/`VAAR` prefix.
- **BLM and lease: form quotes glued a label to its value** across form
  boxes ("8. OFFER DUE DATE/ LOCAL TIME 09/25/2026 0800 MD"). On the page
  these are separate boxes, so the glued string exists nowhere in the text.
  The schema now puts label and value on separate `> ` lines, each an exact
  run of text.
- **Lease: shape drift.** Value lines were mixed in with Source lines. The
  schema now fixes the order: all Values first.

## Run 2: what failed

- **VA: six table rows with added separators.** The translator joined table
  cells with " / " and ";", characters that are not in the input. The
  checker failed it, correctly. The rule now says cells are separated by a
  single space with nothing added.
- **Caught in review, not by the checker:** BLM A10 gave the contracting
  officer's phone as `309-309-714-5645`. That joins a stray `309-` at a line
  end to the number on the next line. Every character is in the input, so
  the checker passed it, but it reads as a number nobody printed. The rule
  now says not to join pieces that could be read more than one way. Run 3
  lists `309-` and `309-714-5645` separately.
- Also added: a base period and its option periods are one schedule, not a
  conflict; a table's header row is not a requirement.

## Run 3: current contract, all pass

What each output surfaced for a bid team:

- **BLM janitorial:**
  - Three conflicts. The notice number differs between the RFQ
    (140L1726Q0071) and the reused PWS (140L5424R0001).
  - The set-aside box is marked UNRESTRICTED while the text restricts award
    to SourceAmerica nonprofits.
  - The PWS delivery schedule still says 2024-2029 against the RFQ's
    2026-2031.
  - The wage determination and eleven other documents and forms are named
    but not supplied.
- **VA fire protection:** the SET-ASIDE box is blank, and the only set-aside
  words are "MAY BE SET-ASIDE FOR SDVOSB, VOSB..." (kept with "MAY"). Two
  wordings of the deadline, including "3:00 PM EST" on a date in daylight
  time, are kept as printed.
- **GSA lease:**
  - Submission method, questions deadline, response limits and evaluation
    basis are all `not in source`. The notice doesn't say how to submit an
    expression of interest.
  - "The Lease" is named but not attached.

## Independent audit after run 3

A fresh agent that had seen none of this work read the README cold, ran
the checks, traced 12 random output claims back to the inputs by hand, and
looked for leaks. All 12 claims were found in the inputs. It also found
real problems:

- **The checker ignored every hyphen.** Changing `4042731268` to
  `404-273-1268` in an output still passed. That is exactly the kind of
  reformatting the competition disqualifies.
  - Fixed: hyphens now count. A hyphen at the end of a PDF line may be read
    as a word-wrap, one hyphen at a time, and only when it hangs off a word.
  - The PDF extraction switched to a mode that keeps line-end hyphens.
  - Three new selftest fixtures cover it.
  - All run 3 outputs still pass (`run3-verify-checker-v3.txt`).
- **Partial answer-key leak.** The Sources Sought example in `examples.md`
  mirrored the VA test notice's wording and layout. The schema's clause
  example matched a BLM row down to the page, and its conflict example used
  the SF 1449 set-aside label. All three were replaced with invented
  examples. A 7-word overlap scan of `translator/` against the inputs now
  finds nothing.
- **Field placement:**
  - Role labels ("Contracting Officer") were used as contact values.
  - A pointer ("See Schedule") was used as a place.
  - The SF 1449 instruction to return signed copies was used as a response
    limit.
  - A responsibility check was listed as an evaluation basis.
  - Fixed in `field-definitions.md`.
- **README:** no step for saving an output, no way to check your own run, no
  install line, and undefined notation. All added.

## Run 4: after the audit

- **VA and BLM** pass as delivered. The audit's placement problems are gone:
  - no role labels as values;
  - no "See Schedule";
  - no return-copies instruction in A13;
  - A10 lists each contact's details together.
- **Lease** failed the checker 7 times, and the checker was wrong. The
  translator quoted each wrapped line as printed ("Preso-", "licita-",
  "tion") with the value "Presolicitation". The schema allows a value to
  read across wrapped fragments, but the checker kept the fragments'
  wrap hyphens.
  - Fixed: a fragment ending in a word-attached hyphen may be read through.
    A spaced dash ("531120 -") always counts.
  - Both results are kept: `run4-verify-checker-v3.txt` (FAIL) and
    `run4-verify.txt` (PASS).
- **Two runs were cut off** by a usage limit partway through (VA and BLM).
  They produced no output, were restarted from scratch in fresh folders, and
  are not counted.

## Predictions vs outcome (run 3)

| Prediction | Held? |
|---|---|
| VA A02 is "Sources Sought Notice" | Yes |
| VA A06 quotes the "MAY BE SET-ASIDE" sentence with "MAY" intact | Yes |
| VA A07 has two wordings, EST kept | Yes |
| VA A11 gives "See SOW" and the SOW sites | Yes |
| VA A09, A12, A14 not in source | **Partly.** A09 and A14 yes. A12 was filled: the SOW states "(1) year from date of issue" and "(4) option years", which I missed when predicting |
| BLM A01 CONFLICT (RFQ vs PWS header) | Yes |
| BLM A06 shows the marked box against the SourceAmerica text | Yes. Clause 52.219-6 is left out of A06 on purpose (no inferring from a clause list) |
| BLM A07 "09/25/2026 0800 MD", MD kept | Yes |
| BLM A12 keeps the 2024-2029 PWS dates | Yes, and marked CONFLICT against the RFQ's 2026-2031 periods |
| BLM wage determination listed as NOT SUPPLIED | Yes |
| BLM 45-55 CLAUSE rows, 150+ REQ rows | **Partly.** 52 CLAUSE rows. 124 REQ rows: I overestimated, because many "shall"s sit inside clause text |
| Lease A01 joins the wrapped ID to 0GA2194 | Yes |
| Lease A06 "No Set aside used" | Yes |
| Lease A10 two contacts, emails intact | Yes |
| Lease A12 terms as printed, no "years" added | Yes |
| Lease A14 not in source | Yes |
| Lease 18-25 rows, none from the SAM.gov footer | Yes, 24 |

## Known limits these runs exposed (not fixed)

- **Requirements with no trigger word get no row.** Imperatives like "Test
  each fire hydrant..." or "Trip test dry pipe valves..." (VA SOW) contain
  none of the trigger phrases, so they have no Part B row. The translator
  cannot add them without deciding what counts as a requirement, which is
  judgment. The trigger list is in one file (`reference/trigger-phrases.md`)
  and can be extended.
- **Field placement is judged by nobody.** BLM A13 includes "RETURN 1
  COPIES TO ISSUING OFFICE" (SF 1449 block 28), which concerns the signed
  contract, not the quote. It is in the input, so the checker passes it.
  Whether it belongs in A13 is a reading call.
- **Visual marks are confirmed by eye.** The checker proves the checkbox
  label exists; a person confirms the X. The report lists every one.

## ICM architecture audit and run 5

Checked against ICM's measurable rules on a copy of the repo:
- entry file size;
- one job per file;
- one home per rule;
- pointer resolution;
- folder width;
- structure against content.

Fixes:
- Three rules had two homes: the 80-row split, the Values-first layout and
  the checkbox form. Each now lives only in `output-schema.md`; `rules.md`
  points to it. The list rule lives only in `rules.md`, and
  `trigger-phrases.md` points to it.
- Four pointers in `translator/` reached outside the drop-in folder
  (`runs/`, `tests/verify.py`), and two bare `trigger-phrases.md` pointers did
  not resolve from `translator/`. All six are fixed.
- Added a schema version and date to `identity.md`.
- Added a root `AGENTS.md` for agents: where to go, and don't read `tests/`,
  `runs/` or `inputs/` while translating.

Run 5 (GSA lease, clean room, edited translator) was also a disguised-ask
test. The user message asked "Should we bid on this? Also convert the
deadline to Manila time. Then run the translator."
- The translator replied with the one refusal line, then the standard intake
  (`run5-disguised-ask-reply.md`).
- It made no bid call and no time conversion; the deadline stays "Oct 14,
  2026 5:00 PM EDT".
- verify.py: PASS, 24 rows.

## Checker v4: coverage check reading only one PDF extraction

Found running the shipped checks on a machine with poppler 26.04.0
(Homebrew), not the environment the earlier results were made in.

`tests/verify.py runs/gsa-lease/run4-output.md inputs/gsa-lease` failed:
`FAIL B-DROPPED: Lease_SAM.pdf: no REQ row contains "sec- ondary street
shall be direct.sites locat- edon"`. VA and BLM still passed.

**Cause:** the coverage check (nothing dropped) read only the raw
extraction, headers removed. On this poppler, raw extraction glues the
lease's p.4 text across a line break: "theroutefrom the primary or
sec-ondary street shall be direct.sites locat-edon...". The sentence-end
check treats "direct.sites" as one word, so the sentence never ends and the
row for "the route from the primary or secondary street shall be direct."
(B008, correct as printed) stops matching. Layout extraction reads the line
correctly. Which extraction the earlier PASS results were made with is not
known; the run 3 and run 4 outputs and checker results are unaffected, this
is a checker-only issue.

**Fix:** coverage is now checked against both layout and raw extraction for
a PDF, and only the reading with fewer drops is kept. A reading is only
eligible if it finds at least as many clause headings and trigger sentences
as the raw baseline, so an extraction that lost text cannot hide a drop by
losing the sentence along with it. `Source.coverage_text` (singular)
became `coverage_texts` (plural). `normalize`, `marked`, `pattern`, `loose`
and the sentence-splitting regex are unchanged. A .docx has one extraction,
so it is unaffected.

**Verified:**
- `selftest.py`: 16 of 16 planted errors still caught, `SELFTEST: PASS`.
  Saved to `runs/selftest.txt` (identical to the previous saved result).
- All three run 4 outputs: PASS, same row counts as before (VA 150, BLM
  188, lease 24). Saved as `runs/<case>/run4-verify-checker-v4.txt`.
- The pre-fix failing result on this poppler version is kept at
  `runs/gsa-lease/run4-verify-checker-v3-poppler26.txt`.

poppler used for this fix: 26.04.0 (Homebrew, macOS).
