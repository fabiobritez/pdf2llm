# LLM fidelity audit

PASS: 5 datasheets checked; spec-table failures: 0; whole-document numeric source subset after permitted figure deduplication: True for 5/5.

PASS requires zero spec-table failures and whole-document numeric source subset True after permitted figure-description deduplication.

Numeric tokens retain signs; − and – normalize to -. Word sets are case-sensitive. Spec tables are paired in document order; all non-separator rows, including headers, are checked cell by cell. Whole-document equality/subset is reported both before and after the permitted figure-description deduplication. Image filenames, links, generated legend and page markers are metadata, not document numeric data. Source accounting excludes TOC, revision history, recognized vendor legal/trademark spans, wholly standard TI support subsections and TI copyright furniture; retained headings are still audited.

## ad5593r

Spec tables: 5; rows: 163; nonempty cells checked: 554; failures: 0.

Whole document after permitted figure deduplication: source numeric tokens 3853, compact 3853; equal: True; source subset: True.

Before figure deduplication (diagnostic only): source numeric tokens 4458, compact 3853; equal: False; source subset: False.

## ad5711r-ad5710r

Spec tables: 10; rows: 212; nonempty cells checked: 731; failures: 0.

Whole document after permitted figure deduplication: source numeric tokens 4513, compact 4513; equal: True; source subset: True.

Before figure deduplication (diagnostic only): source numeric tokens 5777, compact 4513; equal: False; source subset: False.

## lt1965fb

Spec tables: 2; rows: 65; nonempty cells checked: 292; failures: 0.

Whole document after permitted figure deduplication: source numeric tokens 3025, compact 3025; equal: True; source subset: True.

Before figure deduplication (diagnostic only): source numeric tokens 3201, compact 3025; equal: False; source subset: False.

## ltc2975

Spec tables: 32; rows: 470; nonempty cells checked: 3371; failures: 0.

Whole document after permitted figure deduplication: source numeric tokens 8519, compact 8519; equal: True; source subset: True.

Before figure deduplication (diagnostic only): source numeric tokens 8915, compact 8519; equal: False; source subset: False.

## max31730

Spec tables: 18; rows: 189; nonempty cells checked: 902; failures: 0.

Whole document after permitted figure deduplication: source numeric tokens 2952, compact 2953; equal: False; source subset: True.

- Extra numeric tokens: {'31730': 1}.

Before figure deduplication (diagnostic only): source numeric tokens 2970, compact 2953; equal: False; source subset: False.
