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
| A02 Notice type | What kind of notice this is, in its own words | SF 1449 Block 14 (visual); SAM "Contract Opportunity Type"; opening sentence of the description ("This is a Request for Information") | Translate one type into another (Sources Sought is not an RFQ; Presolicitation is not a solicitation) |
| A03 Title | The name of the requirement | SAM page title; "SUBJECT" row; PWS/SOW title line | Write a descriptive title of your own |
| A04 Issuing office | Who issued it | SF 1449 Block 9; SAM Department/Sub-tier/Office; "CONTRACTING OFFICE ADDRESS" | Expand abbreviations or complete a truncated name (a block that prints "REGIONAL CONTRACTING OFF" stays as printed) |
| A05 NAICS code | NAICS code, and the size standard if printed next to it | SF 1449 Block 10; SAM Classification; "NAICS CODE" row | Add the NAICS title if the input does not print it |
| A06 Set-aside | Who may compete | SF 1449 Block 10 (visual); SAM "Set Aside"; description text; clauses such as 52.219-6 | Infer a set-aside from the NAICS code or from a clause list alone without quoting it. A future possibility ("may be set-aside") is quoted as written, with "may" intact |
| A07 Response due | Date, time and time zone responses are due | SF 1449 Block 8; SAM "Response Date"; submission instructions | Convert time zones, add a year, change EST to EDT (even when the date falls in daylight time), expand a truncated zone ("CT" stays "CT"), resolve "30 days after" into a date |
| A08 Submission method | How and where to submit | Instructions to offerors; "Submission Instructions"; description | Add a portal or address that is not stated |
| A09 Questions deadline | Last date for questions | Instructions; description | Treat the response due date as the questions deadline |
| A10 Point of contact | Name, email and phone of each government contact | SF 1449 Block 7; SAM Contact Information; "POINT OF CONTACT" row | Fix spelling or capitalization; add a phone number that is not printed; use a role label ("Contracting Officer") or a placeholder ("[To Be Determined]") as a value. One Source block per contact, and list the Value lines contact by contact in the same order as the Source blocks, so each phone stays with its person |
| A11 Place of performance | Where the work happens | SF 1449 schedule "DELIVER TO"; SAM "Place of Performance"; SOW/PWS description of work | Use a pointer ("See SOW", "See Schedule") as a value. Follow it: if the place it points to states the site, quote that; if not, `not in source` |
| A12 Period of performance | Contract length, base and option periods, lease term. Keep the printed label in the value when the value means nothing without it (`Option Term: 0 Years`) | Schedule; clause 52.217-9 fill-ins; SAM description ("Full Term", "Firm Term") | Add up periods into a total that is not printed. A base period and its option periods are one schedule: one `Value:` line each. Use CONFLICT only when two places give different dates or lengths for the same period |
| A13 Response limits | Limits on the response itself: page limits, file formats, number of copies to submit | Instructions to offerors; submission instructions; description | Carry a limit from one document to another; use award or contract-signing instructions (such as copies of the signed contract to return) |
| A14 Evaluation basis | How offers will be evaluated and the award made | 52.212-2 text and its addendum; evaluation section; description | Summarize; include responsibility checks or delivery-schedule clauses that are not the award basis. Quote the stated basis. If two places state award bases that cannot both apply (best value against lowest price), that is a CONFLICT. Market research notices often have none: then `not in source` |
