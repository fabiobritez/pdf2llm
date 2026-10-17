# LLM fidelity audit

PASS: 1 datasheets checked; spec-table failures: 0; whole-document numeric source subset after permitted figure deduplication: True for 1/1.

PASS requires zero spec-table failures and whole-document numeric source subset True after permitted figure-description deduplication.

Numeric tokens retain signs; − and – normalize to -. Word sets are case-sensitive. Spec tables are paired in document order; all non-separator rows, including headers, are checked cell by cell. Whole-document equality/subset is reported both before and after the permitted figure-description deduplication. Image filenames, links, generated legend and page markers are metadata, not document numeric data. Source accounting excludes TOC, revision history, recognized vendor legal/trademark spans, wholly standard TI support subsections and TI copyright furniture; retained headings are still audited.

## ad5593r

Spec tables: 5; rows: 163; nonempty cells checked: 554; failures: 0.

Whole document after permitted figure deduplication: source numeric tokens 3853, compact 3853; equal: True; source subset: True.

Before figure deduplication (diagnostic only): source numeric tokens 4458, compact 3853; equal: False; source subset: False.
