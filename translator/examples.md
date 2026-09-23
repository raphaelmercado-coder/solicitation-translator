# Examples

Three short worked cases showing the contract holding, then the failure
modes that break it. The inputs are illustrative excerpts written for this
file; they are not real notices. Real, full runs are in the repo's `runs/`
folder.

---

## Example 1: a filled field, a relative date, a list

**Input (F1 = `RFQ_12345A27Q0042.pdf`, page 2):**

> Quotes are due 03/14/2027 1400 CT. Submit quotes by email to
> jane.okafor@agency.gov. Work shall begin within 10 days after award.
> The quote must include the following:
> 1) Company name and UEI.
> 2) Unit price for each line item.

**Output (excerpts):**

```
### A07 Response due
Value: 03/14/2027 1400 CT
Source: F1 p.2
> Quotes are due 03/14/2027 1400 CT.

### A12 Period of performance
Value: not in source
```

```
| B001 | REQ | F1 p.2 | - | Work shall begin within 10 days after award. | [HUMAN] |
| B002 | REQ | F1 p.2 | - | The quote must include the following: | [HUMAN] |
| B002a | REQ | F1 p.2 | 1) | Company name and UEI. | [HUMAN] |
| B002b | REQ | F1 p.2 | 2) | Unit price for each line item. | [HUMAN] |
```

Why: the due date keeps "CT" as printed. "Within 10 days after award" is a
start rule, not a period of performance, so A12 is `not in source`, and the
sentence stays relative in Part B. The list items get rows though they
contain no trigger.

---

## Example 2: a Sources Sought with gaps

**Input (F1 = `SS_Notice.docx`):**

> SET-ASIDE: [blank]
> This is a Sources Sought Notice only. This is not a request for quotes.
> Responses shall not exceed 5 pages. Based on responses, this requirement
> may be set-aside for small business.

**Output (excerpts):**

```
### A02 Notice type
Value: Sources Sought Notice
Source: F1 DESCRIPTION
> This is a Sources Sought Notice only. This is not a request for quotes.

### A06 Set-aside
Value: this requirement may be set-aside for small business
Source: F1 DESCRIPTION
> Based on responses, this requirement may be set-aside for small business.

### A14 Evaluation basis
Value: not in source
```

Why: the SET-ASIDE box is blank, so it adds nothing, but the text states a
possibility. The value keeps "may". A02 is the notice's own words; it is not
turned into "RFI" or "RFQ". A Sources Sought has no evaluation basis here,
so A14 is `not in source`.

---

## Example 3: a conflict and a missing attachment

**Input:** F1 = `Solicitation.pdf` prints `SOLICITATION NUMBER 12345A27Q0042`
on page 1 and lists `Attachment 3 - Wage Determination` on page 9.
F2 = `Attachment_1_SOW.pdf` prints `12345A24R0007` in every page header.
No wage determination file was given.

**Output (excerpts):**

```
### A01 Notice number
Value: CONFLICT
Source: F1 p.1
Reads: 12345A27Q0042
> 5. SOLICITATION NUMBER 12345A27Q0042
Source: F2 p.1
Reads: 12345A24R0007
> 12345A24R0007 Grounds Maintenance Statement of Work
```

```
Fields not in source: A09, A13
Fields in conflict: A01

| ID | Kind | Source | Quote |
|---|---|---|---|
| C01 | NOT SUPPLIED | F1 p.9 | Attachment 3 - Wage Determination |
```

Why: the SOW's header number differs from the solicitation's. The output
shows both and does not decide which is right. The wage determination is
named but absent, so it goes in Part C.

---

## Failure modes

Each of these puts something in the output that was not in the input, or
drops something that was. Each one fails `verify.py`.

| Failure | Looks like | Correct |
|---|---|---|
| Converted time zone | `Value: 03/14/2027 3:00 PM ET` | `Value: 03/14/2027 1400 CT` |
| Resolved relative date | `Work begins 04/05/2027` | the sentence as written, in Part B |
| Corrected spelling | `Jane Okafor` when the input printed `Jane Okafar` | `Jane Okafar` |
| Inferred set-aside | `Value: Small business` from NAICS or clause 52.219-6 alone | quote the stated set-aside, or `not in source` |
| Picked a winner | `Value: 12345A27Q0042` when an attachment prints another number | `CONFLICT` with both |
| Paraphrased requirement | `Mow weekly in season.` | the full sentence, word for word |
| Dropped requirement | a "should" sentence left out as "advisory" | every trigger sentence gets a row |
| Invented numbering | `Ref: 3.1` when the input prints no number | `Ref: -` |
| Filled a blank | `Value: Full and open` for an empty SET-ASIDE box | `not in source` |
| Added advice | "Recommend bidding; low competition." | nothing; not in the schema |
