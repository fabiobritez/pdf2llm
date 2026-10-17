# LLM fidelity audit

PASS: 2 datasheets checked; spec-table failures: 0; whole-document numeric source subset after permitted figure deduplication: True for 2/2.

PASS requires zero spec-table failures and whole-document numeric source subset True after permitted figure-description deduplication.

Numeric tokens retain signs; − and – normalize to -. Word sets are case-sensitive. Spec tables are paired in document order; all non-separator rows, including headers, are checked cell by cell. Whole-document equality/subset is reported both before and after the permitted figure-description deduplication. Image filenames, links, generated legend and page markers are metadata, not document numeric data. Source accounting excludes TOC, revision history, recognized vendor legal/trademark spans, wholly standard TI support subsections and TI copyright furniture; retained headings are still audited.

## ad5711r-ad5710r

Spec tables: 10; rows: 212; nonempty cells checked: 731; failures: 0.

Whole document after permitted figure deduplication: source numeric tokens 4513, compact 4513; equal: True; source subset: True.

Before figure deduplication (diagnostic only): source numeric tokens 5777, compact 4513; equal: False; source subset: False.

## tps22990

Spec tables: 21; rows: 210; nonempty cells checked: 817; failures: 0.

Whole document after permitted figure deduplication: source numeric tokens 2205, compact 2206; equal: False; source subset: True.

- Extra numeric tokens: {'271': 1}.

Before figure deduplication (diagnostic only): source numeric tokens 2556, compact 2206; equal: False; source subset: False.
