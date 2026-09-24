# Trigger phrases, clause rule and exemptions (Part B)

This file decides what counts as a requirement. The translator uses it to
build Part B. The repo's checker reads the fenced blocks below directly, so
the translator and the checker work from one list.

## Trigger phrases

A sentence is a requirement if it contains any of these words or phrases,
in any capitalization. It gets its own row in Part B, word for word.

```triggers
shall
must
should
required
prohibited
will be evaluated
will not be considered
will not be accepted
will not be acceptable
```

- One row per sentence, even if the sentence has several triggers.
- Lists under a requirement sentence: see `../rules.md`, section 3, item 3.
- Definitions, headings and table labels are not requirements unless they
  contain a trigger.
- "Should" is on the list on purpose. Notices use it for real requirements
  ("the facility should not be located within a floodplain"). The translator does not decide which uses matter.

## Clause rule

Solicitations carry standard FAR and agency clauses: pages of fixed text
full of "shall" that is the same in every solicitation. Listing every
sentence would bury the requirements that are specific to this job.

A clause heading is a line that starts with a clause number (optionally
prefixed `FAR`, `DFARS` or `VAAR`) followed by its title:

```clause-heading
^\s*(?:FAR\s+|DFARS\s+|VAAR\s+)?(?:52|552|852|1452)\.\d{3}-\d{1,3}\s+(?:[-–]\s+)?(?!AND\b|ARE\b|IS\b|OR\b)[A-Z][A-Za-z]
```

- Every clause heading gets one `CLAUSE` row: the number and title exactly
  as printed.
- The text from a clause heading down to the next stop line (below), the
  next clause heading, or the end of the file is clause text. Its sentences
  do not get their own rows.
- A number mentioned inside a sentence ("in accordance with FAR 52.232-18.") is not
  a heading.
- Clause text still feeds Part A. The evaluation basis, for example, usually
  lives inside 52.212-2.

Stop lines: a numbered section marker (`3 - List of Documents`), a
`SECTION X` heading, an `(End of clause)` / `(End of provision)` /
`(End of Section X)` line, or the document's own outline number (`E.1.0`,
`H.6.1`). Text after a stop line is ordinary text again and its
requirements get rows.

```section-marker
^\s*\d{1,2} - [A-Z]
^\s*SECTION [A-Z]\b
^\s*\(End of (?:clause|provision|Section)
^\s*[A-Z]\.\d+(?:\.\d+)*\s
```

## Exemptions

Text that is not part of the notice: website navigation, banners and
footers captured when a SAM.gov page is saved as PDF. It gets no rows. Each
line below is `start marker => end marker`; `<EOF>` means end of file.

```exempt
Our Website => <EOF>
```
