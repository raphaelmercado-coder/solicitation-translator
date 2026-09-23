# Field definitions (Part A)

What each field holds and where it usually sits. "Usually" is a place to look,
never permission to assume. If the item is not stated, the field is
`not in source`.

Common layouts:
- **SF 1449** (the standard federal form for commercial buys): numbered blocks
  on page 1, then continuation pages, clauses and provisions.
- **SAM.gov notice page** (saved or printed from the website): a metadata
  strip (Notice ID, type, dates), Classification, Description, Contact
  Information, Attachments/Links.
- **Notice template in Word** (common for VA): a GENERAL INFORMATION table,
  then DESCRIPTION, then attachments pasted in.

| Field | Holds | Usually found | Do not |
|---|---|---|---|
| A01 Notice number | The solicitation or notice number | SF 1449 Block 5; SAM "Notice ID"; "SOLICITATION NUMBER" row | Take a number from a page header of an attached document as the notice number without checking. If an attachment prints a different number, that is a CONFLICT |
| A02 Notice type | What kind of notice this is, in its own words | SF 1449 Block 14 (visual); SAM "Contract Opportunity Type"; opening sentence of DESCRIPTION ("This is a Sources Sought Notice") | Translate one type into another (Sources Sought is not an RFQ; Presolicitation is not a solicitation) |
| A03 Title | The name of the requirement | SAM page title; "SUBJECT" row; PWS/SOW title line | Write a descriptive title of your own |
| A04 Issuing office | Who issued it | SF 1449 Block 9; SAM Department/Sub-tier/Office; "CONTRACTING OFFICE ADDRESS" | Expand abbreviations or complete a truncated name (a block that prints "REGIONAL CONTRACTING OFF" stays as printed) |
| A05 NAICS code | NAICS code and size standard if printed | SF 1449 Block 10; SAM Classification; "NAICS CODE" row | Add the NAICS title if the input does not print it |
| A06 Set-aside | Who may compete | SF 1449 Block 10 (visual); SAM "Set Aside"; description text; clauses such as 52.219-6 | Infer a set-aside from the NAICS code or from a clause list alone without quoting it. A future possibility ("may be set-aside") is quoted as written, with "may" intact |
| A07 Response due | Date, time and time zone responses are due | SF 1449 Block 8; SAM "Response Date"; submission instructions | Convert time zones, add a year, change EST to EDT (even when the date falls in daylight time), expand a truncated zone ("CT" stays "CT"), resolve "30 days after" into a date |
| A08 Submission method | How and where to submit | Instructions to offerors; "Submission Instructions"; description | Add a portal or address that is not stated |
| A09 Questions deadline | Last date for questions | Instructions; description | Treat the response due date as the questions deadline |
| A10 Point of contact | Name, title, email, phone of the government contact(s) | SF 1449 Block 7; SAM Contact Information; "POINT OF CONTACT" row | Fix spelling, capitalization or line breaks inside an email or name; add a phone number that is not printed |
| A11 Place of performance | Where the work happens | SF 1449 schedule "DELIVER TO"; SAM "Place of Performance"; SOW/PWS description of work | Copy "See SOW" as if it were an address. If the table says "See SOW" and the SOW gives the site, give both as two Value lines |
| A12 Period of performance | Contract length, base and option periods, lease term | Schedule; clause 52.217-9 fill-ins; SAM description ("Full Term", "Firm Term") | Add up periods into a total that is not printed |
| A13 Response limits | Page limits, file formats, number of copies | Instructions; description | Carry a limit from one document to another |
| A14 Evaluation basis | How responses will be evaluated or selected | 52.212-2 text; evaluation section; description | Summarize. Quote the stated basis. A Sources Sought or Presolicitation often has none: then `not in source` |
