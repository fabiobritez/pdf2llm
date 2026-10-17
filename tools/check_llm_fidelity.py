"""Independent structural and token audit; no converter imports or mappings."""
import argparse
from collections import Counter, defaultdict
import html
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def tokens(text):
    # Preserve numeric sign semantics before stripping arbitrary TeX commands.
    text = html.unescape(text).replace('−', '-').replace('–', '-').replace(r'\pm', '±')
    text = re.sub(r'^\s*[-+*]\s+', '', text)
    text = re.sub(r'</?(?:sub|sup)\b[^>]*>|<br\s*/?>', ' ', text, flags=re.I)
    text = re.sub(r'</?[A-Za-z][^>]*>', '', text)
    text = re.sub(r'\\[A-Za-z]+', ' ', text)
    text = re.sub(r'[{}$*]', ' ', text)
    text = text.replace(r'\_', '_')
    # Group delimiters and the radical do not themselves contain numeric data.
    # Ignore them consistently on both sides so TeX-to-plain grouping changes
    # cannot attach/detach the sign of the first numeric token of a group.
    numeric_text = re.sub(r'[()√^]', ' ', text)
    numbers = Counter()
    for match in re.finditer(r'[+±-]?\s*(?:\d+(?:\.\d+)?|\.\d+)', numeric_text):
        numbers[re.sub(r'\s', '', match[0])] += 1
    words = set(re.findall(r'[^\W\d_]{2,}', text, re.UNICODE))
    return numbers, words


# Full standard paragraphs: unfamiliar/custom support text is retained.
STANDARD_SUPPORT = frozenset((
    "Design Support TI's Design Support Quickly find helpful E2E forums along with design support tools and contact information for technical support.",
    'ESD damage can range from subtle performance degradation to complete device failure. Precision integrated circuits may be more susceptible to damage because very small parametric changes could cause the device not to meet its published specifications.',
    'Linked content is provided "AS IS" by the respective contributors. They do not constitute TI specifications and do not necessarily reflect TI\'s views; see TI\'s Terms of Use.',
    'SLYZ022 — TI Glossary.',
    "TI E2E™ Online Community TI's Engineer-to-Engineer (E2E) Community. Created to foster collaboration among engineers. At e2e.ti.com, you can ask questions, share knowledge, explore ideas and help solve problems with fellow engineers.",
    "TI E2E™ support forums are an engineer's go-to source for fast, verified answers and design help — straight from the experts. Search existing answers or ask your own question to get the quick design help you need.",
    'TI Glossary This glossary lists and explains terms, acronyms, and definitions.',
    'The following links connect to TI community resources. Linked contents are provided "AS IS" by the respective contributors. They do not constitute TI specifications and do not necessarily reflect TI\'s views; see TI\'s Terms of Use.',
    'These devices have limited built-in ESD protection. The leads should be shorted together or the device placed in conductive foam during storage or handling to prevent electrostatic damage to the MOS gates.',
    'This glossary lists and explains terms, acronyms, and definitions.',
    'This integrated circuit can be damaged by ESD. Texas Instruments recommends that all integrated circuits be handled with appropriate precautions. Failure to observe proper handling and installation procedures can cause damage.',
    'To receive notification of documentation updates, navigate to the device product folder on ti.com. Click on Notifications to register and receive a weekly digest of any product information that has changed. For change details, review the revision history included in any revised document.',
    'To receive notification of documentation updates, navigate to the device product folder on ti.com. Click on Subscribe to updates to register and receive a weekly digest of any product information that has changed. For change details, review the revision history included in any revised document.',
    'To receive notification of documentation updates, navigate to the device product folder on ti.com. In the upper right corner, click on Alert me to register and receive a weekly digest of any product information that has changed. For change details, review the revision history included in any revised document.',
))
SUPPORT_TITLES = frozenset(('receiving notification of documentation updates',
    'support resources', 'community resources', 'trademarks',
    'electrostatic discharge caution', 'glossary'))


def vendor_plain(text):
    text = re.sub(r'!?\[([^\]]*)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'<[^>]+>', '', text)
    return ' '.join(html.unescape(text).replace('*', '').split())


def trademark_legal(text):
    ownership = (
        r'All (?:registered trademarks and trademarks|(?:other )?trademarks) are the property of their respective owners\.'
        r'|[^.\n]+ (?:is|are) (?:a |an )?(?:registered )?trademarks? of '
        r'(?:Texas Instruments|NXP Semiconductors|Maxim Integrated Products, Inc|'
        r'Linear Technology Corporation|Analog Devices(?:,? Inc)?)\.')
    return bool(re.fullmatch(
        r'(?:' + ownership + r')(?: (?:' + ownership + r'))*'
        r'(?: Protected by U\.S\. patents, including [\d, and]+\.)?', text, re.I))


def legal_paragraph(text):
    if '|' in text or re.search(r'!\[|```|~~~', text):
        return False
    return bool(re.match(
        r"(?:TI PROVIDES TECHNICAL AND RELIABILITY DATA\b|These resources are intended for skilled developers designing with TI products\."
        r"|These resources are subject to change without notice\. TI grants you permission"
        r"|TI['’]s products are provided subject to TI['’]s Terms of Sale"
        r"|TI objects to and rejects any additional or different terms you may propose\."
        r"|Mailing Address: Texas Instruments\b"
        r"|Information furnished by (?:Analog Devices|Linear Technology) is believed to be accurate"
        r"|(?:Maxim Integrated|Linear Technology) cannot assume responsibility for use of any circuitry)", text, re.I))


def vendor_source_lines(lines):
    """Independently exclude vendor spans, preserving source line locations.

    Headings remain evidence; generated omission placeholders are never source
    data. Paragraph boundaries keep package tables outside legal exclusions.
    """
    out = []
    i = 0
    fence = None
    while i < len(lines):
        number, line = lines[i]
        if line.lstrip().startswith(('```', '~~~')):
            marker = line.lstrip()[:3]
            fence = None if fence == marker else marker if fence is None else fence
            out.append(lines[i])
            i += 1
            continue
        if fence:
            out.append(lines[i])
            i += 1
            continue
        heading = re.match(r'^(#{1,6})\s+(.*)', line)
        title = re.sub(r'^\d+(?:\.\d+)*\s+', '', vendor_plain(heading[2])) if heading else ''
        if heading and title.lower() == 'important notice and disclaimer':
            end = i + 1
            while end < len(lines) and not re.match(r'^#{1,6}\s+', lines[end][1]):
                end += 1
            body = '\n'.join(s for _, s in lines[i + 1:end]
                             if not re.match(r'^\{\d+\}-{3,}', s))
            paras = [vendor_plain(p) for p in re.split(r'\n\s*\n', body) if p.strip()]
            if paras and any(p.upper().startswith('TI PROVIDES TECHNICAL') for p in paras) and all(
                    legal_paragraph(p) or re.fullmatch(
                        r'(?:Copyright © [\d, –—-]+,? Texas Instruments Incorporated\.?'
                        r'|Last updated \d{1,2}/\d{4})', p, re.I) for p in paras):
                out.append(lines[i])
                out.extend((n, s) for n, s in lines[i + 1:end] if re.match(r'^\{\d+\}-{3,}', s))
                i = end
                continue
        if heading and title.lower() in SUPPORT_TITLES:
            end = i + 1
            while end < len(lines):
                next_heading = re.match(r'^(#{1,6})\s+(.*)', lines[end][1])
                # Only the standard TI Glossary link may be a nested heading.
                if next_heading and not (len(next_heading[1]) > len(heading[1])
                        and vendor_plain(next_heading[2]) == 'TI Glossary'):
                    break
                end += 1
            body = '\n'.join(s for _, s in lines[i + 1:end]
                             if not re.match(r'^\{\d+\}-{3,}', s))
            paras = [vendor_plain(p) for p in re.split(r'\n\s*\n', body) if p.strip()]
            def standard(p):
                if title.lower() == 'trademarks':
                    return trademark_legal(p) and 'Protected by' not in p
                if p.startswith('####'):
                    p = p.lstrip('# ').strip()
                return (p in STANDARD_SUPPORT or p == 'TI Glossary'
                        or (title.lower() == 'electrostatic discharge caution'
                            and re.fullmatch(r'Electrostatic Discharge Caution (?:icon|symbol): [^\d]+', p)))
            if paras and all(standard(p) for p in paras):
                out.append(lines[i])
                out.extend((n, s) for n, s in lines[i + 1:end] if re.match(r'^\{\d+\}-{3,}', s))
                i = end
                continue
            out.extend(lines[i:end])
            i = end
            continue
        # These lines are repeated page furniture, with no placeholder needed.
        if re.fullmatch(r'Copyright © [\d, –—-]+,? Texas Instruments Incorporated\.?(?: Submit Document Feedback \d+)?', vendor_plain(line), re.I):
            i += 1
            continue
        # Paragraphs are bounded by structural content even without blank lines.
        end = i + 1
        if line.strip() and not heading and not re.match(r'^\s*(?:[|!`~]|\{\d+\})', line):
            while end < len(lines) and lines[end][1].strip() and not re.match(
                    r'^\s*(?:[#|!`~]|\{\d+\}|\*\*)', lines[end][1]):
                end += 1
            text = vendor_plain(' '.join(s for _, s in lines[i:end]))
            if legal_paragraph(text) or trademark_legal(text):
                i = end
                # Blank lines between legal paragraphs should not create placeholders.
                while i < len(lines) and not lines[i][1].strip():
                    i += 1
                continue
        out.append(lines[i])
        i += 1
    return out


def source_lines(text, dedupe=False):
    """Independent omission accounting, retaining original source line numbers."""
    lines = vendor_source_lines(list(enumerate(text.splitlines(), 1)))
    kept = []
    section = None
    revision = False
    i = 0
    previous = ''
    while i < len(lines):
        number, line = lines[i]
        heading = re.match(r'^(#{1,6})\s+(.*)', line)
        if heading and section and (len(heading[1]) <= section or (not revision and (re.search(r'revision history', heading[2], re.I) or re.match(r'^\{\d+\}-{3,}', previous)))) and not (revision and re.match(r'[* ]*\d{1,2}/\d{4}', heading[2])):
            section = None
        if section:
            if line.strip():
                previous = line
            i += 1
            continue
        if heading and re.search(r'\b(table of contents|revision history)\b', heading[2], re.I):
            section = len(heading[1])
            revision = bool(re.search('revision history', heading[2], re.I))
            if revision:
                kept.append((number, line))
            i += 1
            continue
        if re.match(r'^\{\d+\}-{3,}', line):
            i += 1
            continue
        if line.strip().startswith('|'):
            j = i
            while j < len(lines) and lines[j][1].strip().startswith('|'):
                j += 1
            dotted = [s for _, s in lines[i:j] if re.search(r'\.{3,}', s)]
            if len(dotted) >= 2 and all(re.search(r'\d\s*(?:</b>)?\s*\|', s) for s in dotted):
                i = j
                continue
        image = re.match(r'^!\[(.*)\]\(.*\)\s*$', line)
        if image:
            alt = image[1]
            icon = re.fullmatch(r'(Product Folder|Order Now|Technical Documents|Tools & Software|Support & Community)( icon)?', html.unescape(alt), re.I)
            j = i + 1
            while j < len(lines) and not lines[j][1].strip():
                j += 1
            end = j
            while end < len(lines) and lines[end][1].strip() and not re.match(r'^(?:#|\||!\[|\{\d+\}|\*\*)', lines[end][1]):
                end += 1
            paragraph = ' '.join(s for _, s in lines[j:end])
            a, b = ' '.join(alt.replace(r'\_', '_').split()), ' '.join(paragraph.replace(r'\_', '_').split())
            duplicate = bool(a and b and (a.startswith(b) or b.startswith(a)))
            if not icon:
                kept.append((number, paragraph if dedupe and duplicate and len(b) > len(a) else alt))
            if icon or dedupe:
                if duplicate:
                    i = end
                    continue
            i += 1
            continue
        # Ignore link destinations, never their visible text.
        line = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', line)
        kept.append((number, line))
        i += 1
    return kept


def tables(lines):
    result = []
    block = []
    def finish():
        if not block:
            return
        rows = []
        separator_at = None
        for number, line in block:
            row = [c.strip() for c in re.split(r'(?<!\\)\|', line.strip()[1:-1])]
            if all(re.fullmatch(r':?-+:?', c) for c in row):
                if separator_at is None:
                    separator_at = len(rows)
                continue
            rows.append((number, row))
        # Include subsequent multirow headers through the first numeric data row.
        header_end = separator_at or 1
        while header_end < len(rows) and not tokens(' '.join(rows[header_end][1]))[0]:
            header_end += 1
        if any(re.search(r'\b(?:MIN|TYP|MAX|NOM|VALUE|UNITS?)\b', re.sub(r'</?[A-Za-z][^>]*>', ' ', ' '.join(row)).replace('_', ' '), re.I)
               for _, row in rows[:max(1, header_end)]):
            result.append(rows)
    for number, line in lines:
        if line.strip().startswith('|') and line.strip().endswith('|'):
            block.append((number, line))
        else:
            finish()
            block = []
    finish()
    return result


def check(source, compact):
    original = source_lines(source)
    src_tables = tables(original)
    dst_tables = tables(list(enumerate(compact.splitlines(), 1)))
    failures = []
    rows_checked = cells_checked = 0
    if len(src_tables) != len(dst_tables):
        failures.append(f'Spec table count: source {len(src_tables)}, compact {len(dst_tables)}')
    for index, (src, dst) in enumerate(zip(src_tables, dst_tables), 1):
        width = max(len(r) for _, r in src)
        keep = [k for k in range(width) if any(k < len(r) and r[k].strip() for _, r in src)]
        if len(src) != len(dst):
            failures.append(f'Table {index}: row count {len(src)} != {len(dst)}')
        for (line, row), (_, target) in zip(src, dst):
            rows_checked += 1
            if len(target) != len(keep):
                failures.append(f'Table {index}, source line {line}: columns {len(target)} != {len(keep)}')
            if ''.join(row).count('●') != ''.join(target).count('●'):
                failures.append(f'Table {index}, source line {line}: ● count differs')
            for k, out in zip(keep, target):
                cell = row[k] if k < len(row) else ''
                if not cell.strip():
                    continue
                cells_checked += 1
                ns, ws = tokens(cell)
                nd, wd = tokens(out)
                if ns - nd or ws - wd:
                    failures.append(f'Table {index}, source line {line}, column {k + 1}: missing numbers {dict(ns - nd)}, words {sorted(ws - wd)}; {cell!r} -> {out!r}')
    # Remove generated metadata/page labels before whole-document accounting.
    dst_lines = [(n, s) for n, s in enumerate(compact.splitlines(), 1)
                 if not s.startswith('<!-- pdf2llm compact:') and not re.fullmatch(r'\[p\d+\]', s)]
    target_numbers = sum((tokens(s)[0] for _, s in dst_lines), Counter())
    def numeric_audit(lines):
        counts = Counter()
        locations = defaultdict(list)
        for number, line in lines:
            nums, _ = tokens(line)
            counts.update(nums)
            for tok in nums:
                locations[tok].append(number)
        missing = counts - target_numbers
        return {'source_count': counts.total(), 'compact_count': target_numbers.total(),
                'equal': counts == target_numbers, 'subset': not missing,
                'missing': {t: {'count': n, 'source_lines': locations[t]} for t, n in sorted(missing.items())},
                'extra': dict(target_numbers - counts)}
    return {'tables': len(src_tables), 'rows': rows_checked, 'cells': cells_checked,
            'failures': failures, 'numeric': numeric_audit(original),
            'deduplicated_numeric': numeric_audit(source_lines(source, dedupe=True))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('names', nargs='*')
    args = parser.parse_args()
    report = ['# LLM fidelity audit', '', 'PASS requires zero spec-table failures and whole-document numeric source subset True after permitted figure-description deduplication.', '',
              'Numeric tokens retain signs; − and – normalize to -. Word sets are case-sensitive. '
              'Spec tables are paired in document order; all non-separator rows, including headers, are checked cell by cell. '
              'Whole-document equality/subset is reported both before and after the permitted figure-description deduplication. '
              'Image filenames, links, generated legend and page markers are metadata, not document numeric data. '
              'Source accounting excludes TOC, revision history, recognized vendor legal/trademark spans, '
              'wholly standard TI support subsections and TI copyright furniture; retained headings are still audited.', '']
    failed = False
    checked = table_failures = numeric_passes = 0
    paths = sorted((ROOT / 'output').glob('*/*.md'))
    for path in paths:
        if path.name.endswith('.llm.md') or (args.names and path.parent.name not in args.names):
            continue
        target = path.with_name(path.parent.name + '.llm.md')
        if not target.exists():
            failed = True
            report.extend([f'## {path.parent.name}', '', 'FAIL: compact file missing.', ''])
            continue
        result = check(path.read_text(), target.read_text())
        checked += 1
        table_failures += len(result['failures'])
        numeric_passes += int(result['deduplicated_numeric']['subset'])
        failed |= bool(result['failures']) or not result['deduplicated_numeric']['subset']
        report.extend([f'## {path.parent.name}', '',
                       f"Spec tables: {result['tables']}; rows: {result['rows']}; nonempty cells checked: {result['cells']}; failures: {len(result['failures'])}.", ''])
        for failure in result['failures']:
            report.append('- ' + failure)
        for key, title in [('deduplicated_numeric', 'Whole document after permitted figure deduplication'), ('numeric', 'Before figure deduplication (diagnostic only)')]:
            audit = result[key]
            report.extend(['', f"{title}: source numeric tokens {audit['source_count']}, compact {audit['compact_count']}; equal: {audit['equal']}; source subset: {audit['subset']}.", ''])
            if key == 'numeric':
                continue  # One count line; repeated figure descriptions explain losses.
            for token, detail in audit['missing'].items():
                report.append(f"- Missing `{token}` ×{detail['count']}; source lines: {', '.join(map(str, detail['source_lines']))}.")
            if audit['extra']:
                report.append(f"- Extra numeric tokens: {audit['extra']}.")
        report.append('')
        print(f"{path.parent.name}: {result['tables']} tables, {result['rows']} rows, {result['cells']} cells, {len(result['failures'])} failures; dedup numeric subset={result['deduplicated_numeric']['subset']}")
    report[2:2] = [f"{'FAIL' if failed else 'PASS'}: {checked} datasheets checked; spec-table failures: {table_failures}; "
                   f"whole-document numeric source subset after permitted figure deduplication: True for {numeric_passes}/{checked}.", '']
    directory = ROOT / 'reports' / 'llm'
    directory.mkdir(parents=True, exist_ok=True)
    (directory / 'fidelity.md').write_text(re.sub(r'\n{3,}', '\n\n', '\n'.join(report)).rstrip() + '\n')
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
