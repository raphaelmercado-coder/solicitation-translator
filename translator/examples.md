# Examples

Three short worked cases showing the contract holding, then the failure
modes that break it. The inputs are illustrative excerpts written for this
file; they are not real notices.

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

## Example 2: market research with gaps and labeled values

**Input (F1 = `RFI_Grounds.pdf`, page 1, a notice page):**

> Type: Request for Information
> Set Aside: (blank)
> Background: The agency is conducting market research only. The Government
> intends to consider HUBZone firms if two or more capable sources respond.
> Primary Contact: Dana Whitlock, Contracting Officer, 555-010-4477
> Secondary Contact: Luis Ferro, luis.ferro@agency.gov
> Term: 5

**Output (excerpts):**

```
### A02 Notice type
Value: Request for Information
Source: F1 p.1
> Type:
> Request for Information

### A06 Set-aside
Value: The Government intends to consider HUBZone firms if two or more capable sources respond.
Source: F1 p.1
> The Government intends to consider HUBZone firms if two or more capable sources respond.

### A10 Point of contact
Value: Dana Whitlock
Value: 555-010-4477
Value: Luis Ferro
Value: luis.ferro@agency.gov
Source: F1 p.1
> Primary Contact: Dana Whitlock, Contracting Officer, 555-010-4477
Source: F1 p.1
> Secondary Contact: Luis Ferro, luis.ferro@agency.gov

### A12 Period of performance
Value: Term: 5
Source: F1 p.1
> Term: 5

### A14 Evaluation basis
Value: not in source
```

Why:
- The Set Aside box is blank, so it adds nothing. The text states an
  intention, so A06 quotes it whole, "intends" and "if" intact. It is not
  shortened to "HUBZone".
- A02 keeps the notice's own words; the notice is not relabeled as another
  type.
- A10 lists each contact's details in the order of its Source blocks. Role
  titles ("Contracting Officer") stay in the quote, not as values.
- A12's bare "5" means nothing without its label, so the value keeps the
  label and adds no unit.
- Market research states no evaluation basis, so A14 is `not in source`.

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
drops something that was. The repo's checker fails every one.

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
| Filled a blank | `Value: Full and open` for an empty Set Aside box | `not in source` |
| Pointer as a place | `Value: See Attachment 1` for place of performance | the place Attachment 1 gives, or `not in source` |
| Added advice | "Recommend bidding; low competition." | nothing; not in the schema |
