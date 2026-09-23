# Predictions (written before any run)

Committed before the translator saw any input, so the runs can prove or
disprove them. Each line is a claim about what a correct output contains.
The run logs in each folder say which held.

## va-fire-protection (36C24126Q0831.docx, VA, fire alarm maintenance)

- A02 is the notice's own words for a Sources Sought ("Sources Sought
  Notice"), not RFQ or RFI.
- A06: the SET-ASIDE row is blank. The only set-aside words are a future
  possibility ("MAY BE SET-ASIDE FOR SDVOSB, VOSB, SMALL BUSINESSES OR
  PROCURED THROUGH FULL AND OPEN COMPETITION"). Correct output quotes that
  with "MAY" intact. Writing "SDVOSB" as the set-aside is a failure.
- A07: two wordings of one deadline ("09-22-2026 3PM EASTERN TIME, NEW YORK,
  USA" and "Tuesday, September 22, 2026 at 3:00 PM EST"), two Value lines.
  EST stays EST even though September 22 is daylight time.
- A11: the table says "See SOW"; the SOW names the site. Two Value lines.
- A13: "shall not exceed 8 pages" and Word or PDF format.
- A09, A12, A14: most likely `not in source`.
- Part B: most rows come from the SOW (Attachment 2). No FAR clause headings.
- Risk: the SOW is long; a dropped "must" or "should" deep in it.

## blm-janitorial (Sol_140L1726Q0071.pdf + A04 PWS, BLM, janitorial)

- A01: CONFLICT. The RFQ prints 140L1726Q0071; every PWS page header prints
  140L5424R0001.
- A06: CONFLICT. Block 10 has UNRESTRICTED marked (visual). Block 20 text
  says set-aside to Source America non-profits under FAR 8.102. Clauses
  52.219-6 (Total Small Business Set-Aside) and 52.219-14 are incorporated.
  A correct output shows at least the box and the text.
- A07: "09/25/2026 0800 MD", with "MD" kept as printed.
- A12: the PWS delivery schedule prints 2024-2029 periods (Base Year
  04/1/2024 - 03/31/2025 ...). That is what the input says; it is not
  corrected to 2026.
- Part C: NOT SUPPLIED for Attachment 2 "B03 2015-5435 REV 32" (the RFQ
  lists it; it was not given).
- Part B: roughly 45-55 CLAUSE rows and 150+ REQ rows, most from the PWS.
- Risk: checkbox marks misread; the PWS section numbering gap (C.1.1 to
  C.1.3) "fixed"; long output truncated.

## gsa-lease (Lease_SAM.pdf, GSA, office lease, SAM.gov page printed)

- A02: "Presolicitation".
- A01: the Notice ID wraps across two lines on the page ("0GA219" / "4").
  Correct value is the joined ID as displayed.
- A07: two wordings ("Oct 14, 2026 5:00 PM EDT" and "Expressions of
  Interest Due: 10/14/2026").
- A06: "No Set aside used".
- A10: two contacts, primary and alternative. Emails broken by hyphenated
  line wraps must come out with no added or dropped characters.
- A12: "Full Term: 15" and "Firm Term: 10" as printed, with no "years"
  added to the Full/Firm terms (only "Option Term" prints "0 Years").
- A14: `not in source`.
- Part B: about 18-25 rows including the seven list items under
  "Expressions of Interest must include the following". No rows from the
  SAM.gov footer ("are required to protect it").
- Risk: the text extraction reads "office" as "o!ice"; a quote with "o!ice"
  or "office" must both pass the checker.
