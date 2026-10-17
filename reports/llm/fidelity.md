# LLM fidelity audit

PASS: 5 datasheets checked; spec-table failures: 0; whole-document numeric source subset after permitted figure deduplication: True for 5/5.

PASS requires zero spec-table failures and whole-document numeric source subset True after permitted figure-description deduplication.

Numeric tokens retain signs; − and – normalize to -. Word sets are case-sensitive. Spec tables are paired in document order; all non-separator rows, including headers, are checked cell by cell. Whole-document equality/subset is reported both before and after the permitted figure-description deduplication. Image filenames, links, generated legend and page markers are metadata, not document numeric data. Source accounting excludes TOC, revision history, recognized vendor legal/trademark spans, wholly standard TI support subsections and TI copyright furniture; retained headings are still audited.

## ad5711r-ad5710r

Spec tables: 10; rows: 212; nonempty cells checked: 731; failures: 0.

Whole document after permitted figure deduplication: source numeric tokens 4513, compact 4513; equal: True; source subset: True.

Before figure deduplication (diagnostic only): source numeric tokens 5777, compact 4513; equal: False; source subset: False.

## ltc2975

Spec tables: 32; rows: 470; nonempty cells checked: 3371; failures: 0.

Whole document after permitted figure deduplication: source numeric tokens 8519, compact 8519; equal: True; source subset: True.

Before figure deduplication (diagnostic only): source numeric tokens 8915, compact 8519; equal: False; source subset: False.

## ltc3313

Spec tables: 4; rows: 76; nonempty cells checked: 308; failures: 0.

Whole document after permitted figure deduplication: source numeric tokens 1781, compact 1781; equal: True; source subset: True.

Before figure deduplication (diagnostic only): source numeric tokens 1848, compact 1781; equal: False; source subset: False.

## ltc3315a

Spec tables: 6; rows: 72; nonempty cells checked: 309; failures: 0.

Whole document after permitted figure deduplication: source numeric tokens 2163, compact 2163; equal: True; source subset: True.

Before figure deduplication (diagnostic only): source numeric tokens 2353, compact 2163; equal: False; source subset: False.

## tps63802

Spec tables: 10; rows: 82; nonempty cells checked: 364; failures: 0.

Whole document after permitted figure deduplication: source numeric tokens 1980, compact 1981; equal: False; source subset: True.

- Extra numeric tokens: {'271': 1}.

Before figure deduplication (diagnostic only): source numeric tokens 2208, compact 1981; equal: False; source subset: False.
