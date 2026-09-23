# Output schema (v1)

This file is the contract. Every output has exactly this shape, in this order,
whatever the input looks like. `tests/verify.py` parses outputs against it, so
the markers below are literal: copy them exactly.

The output is one Markdown document with a header and three parts.

---

## Header

```
# Solicitation Intake

Schema: solicitation-translator v1
Input files:
- F1 = <exact file name>
- F2 = <exact file name>
```

- List every file you were given, one per line, in the order received.
- `F1`, `F2` ... are the only way the rest of the output refers to a file.
- File names are copied exactly, extension included.

---

## Part A: Intake sheet

```
## Part A: Intake sheet
```

Fourteen fields, always all fourteen, always in this order, always with these
exact headings (see `field-definitions.md` for what each one means):

```
### A01 Notice number
### A02 Notice type
### A03 Title
### A04 Issuing office
### A05 NAICS code
### A06 Set-aside
### A07 Response due
### A08 Submission method
### A09 Questions deadline
### A10 Point of contact
### A11 Place of performance
### A12 Period of performance
### A13 Response limits
### A14 Evaluation basis
```

Each field body is one of three forms.

### Form 1: filled

```
### A07 Response due
Value: 03/14/2027 1400 CT
Source: F1 p.1
> 8. OFFER DUE DATE/ LOCAL TIME 03/14/2027 1400 CT
```

- Layout is fixed: all `Value:` lines first, then the `Source:` blocks.
  Never put a `Value:` line after a `Source:` line.
- `Value:` is copied word for word from the input. It is never reworded,
  reformatted, expanded or corrected. It must appear inside one of the
  field's quotes.
- A field may have more than one `Value:` line (a name, an email and a phone
  for A10; the same due date worded two ways in two places for A07). Every
  `Value:` line must appear inside one of the field's quotes.
- `Source:` gives the file and where in it. For a PDF the locator is `p.N` or
  `p.N-M` (PDF page numbers, counted from 1, as a viewer shows them). For a
  .docx, the locator is the nearest heading or table label as printed, e.g.
  `Source: F1 DESCRIPTION`.
- `> ` lines are the quote: the input's own words, copied exactly, long enough
  to show the value in context.
- Each `> ` line is one fragment and must be an exact, unbroken run of the
  input's text. Continuous text goes on one `> ` line. On a form or a web
  page grid, where a label and its value sit in separate boxes, put the label
  on one `> ` line and the value on the next:

  ```
  Source: F1 p.1
  > 8. OFFER DUE DATE/ LOCAL TIME
  > 03/14/2027 1400 CT
  ```

  The value must sit inside a single fragment, or run across fragments in
  order when the page wraps it (a number broken over two lines).
- A field may have several `Source:` blocks, each followed by its own quote.

### Form 2: not in source

```
### A09 Questions deadline
Value: not in source
```

- Exactly that text. No `Source:` lines, no quote, no explanation, no guess.
- Use it when nothing in the input states the item. A form field that is
  printed but left blank also counts as not in source.

### Form 3: conflict

```
### A06 Set-aside
Value: CONFLICT
Source: F1 p.1 [visual]
Reads: UNRESTRICTED
Mark: marked
> 10. THIS ACQUISITION IS UNRESTRICTED OR SET ASIDE
Source: F1 p.3
Reads: 100% set-aside for small business
> This acquisition is a 100% set-aside for small business concerns.
```

- Use `CONFLICT` only when two places in the input state the item in ways
  that cannot both be true: different numbers, different dates, a checked
  box against contrary text. Two wordings of the same fact are not a conflict;
  list them as two `Value:` lines instead.
- Every `Source:` block under a conflict has a `Reads:` line: what that place
  says, word for word, and it must appear inside that block's quote.
- The translator never says which side is right.

### Visual marks

Some facts exist only as a mark on a form (an X in a checkbox). Text
extraction loses those marks, so a quote cannot prove them.

- Tag the source `[visual]`.
- Add `Mark: marked` or `Mark: not marked`.
- The quote is the printed label next to the box, word for word.
- `verify.py` checks the label and lists every visual mark for a person to
  confirm by eye.

---

## Part B: Compliance matrix

```
## Part B: Compliance matrix

| ID | Kind | Source | Ref | Requirement | Owner |
|---|---|---|---|---|---|
| B001 | REQ | F2 p.1 | C.2.1 | The Contractor shall mow all turf areas weekly between April 1 and October 31. | [HUMAN] |
| B002 | CLAUSE | F1 p.5 | - | 52.203-17 Contractor Employee Whistleblower Rights. (NOV 2023) | [HUMAN] |
```

- One row per requirement sentence, in the order they appear in the input,
  files in F-number order.
- `ID`: B001, B002 ... with no gaps. List items under a requirement that ends
  in a colon take the parent ID plus a letter: B014a, B014b ...
- `Kind`: `REQ` for a requirement sentence or list item. `CLAUSE` for a
  standard clause heading (see `trigger-phrases.md`, "Clause rule").
- `Source`: F-number and locator, same format as Part A.
- `Ref`: the input's own paragraph or item number exactly as printed
  (`C.2.1`, `3)`), or `-` if it has none. Never create a number.
- `Requirement`: the whole sentence, word for word. For a `CLAUSE` row, the
  clause number and title exactly as printed.
- `Owner`: always `[HUMAN]`. The team fills this in.
- Never put a pipe character `|` inside a cell. If the input has one, write
  `/` and note it in Part C.
- If the matrix passes 80 rows, stop after B080 and write the line
  `CONTINUED: reply "continue" for B081 onward.` On "continue", resume at the
  next ID with no repeated header. The finished output is the parts joined.

---

## Part C: Not mapped

```
## Part C: Not mapped

Fields not in source: A09, A12
Fields in conflict: A01, A06

| ID | Kind | Source | Quote |
|---|---|---|---|
| C01 | NOT SUPPLIED | F1 p.9 | Attachment 3 - Wage Determination |
| C02 | UNREADABLE | F3 p.4 | - |
```

- `Fields not in source:` lists every Part A field whose value is
  `not in source`, or `none`.
- `Fields in conflict:` lists every Part A field whose value is `CONFLICT`,
  or `none`.
- Table rows, in input order:
  - `NOT SUPPLIED`: a document the input names (attachment, amendment,
    wage determination, exhibit, lease form) that is not among the input
    files. The quote is the input's own words naming it.
  - `UNREADABLE`: a page or area that could not be read. Quote `-`.
  - `PIPE REPLACED`: a `|` in the input that was written as `/`.
- If there is nothing to list, write one row: `| C01 | NONE | - | - |`.

Nothing else follows Part C. No summary, no advice, no recommendation.
