"""Deterministic, conservative Markdown compaction (standard library only)."""
import argparse
import html
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
PAGE = re.compile(r'^\{(\d+)\}-{3,}\s*$')
IMAGE = re.compile(r'^!\[(.*)\]\(([^\n]*)\)\s*$')
HEADING = re.compile(r'^(#{1,6})\s+(.*)')
ICONS = re.compile(r'^(Product Folder|Order Now|Technical Documents|Tools & Software|Support & Community)( icon)?$', re.I)
SEPARATOR = re.compile(r'^:?-+:?$')


def sources(names=None):
    paths = []
    for directory in sorted((ROOT / 'output').iterdir()):
        if not directory.is_dir() or (names and directory.name not in names):
            continue
        path = directory / ('markdown.md' if directory.name == 'tps6287b20' else directory.name + '.md')
        if path.exists():
            paths.append(path)
    if names and set(names) - {p.parent.name for p in paths}:
        raise ValueError('Unknown datasheet: ' + ', '.join(sorted(set(names) - {p.parent.name for p in paths})))
    return paths


def cells(line):
    return re.split(r'(?<!\\)\|', line.strip()[1:-1])


def is_separator(row):
    return bool(row) and all(SEPARATOR.fullmatch(c.strip()) for c in row)


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


def vendor_filter(lines, placeholders=True):
    """Omit recognized legal paragraphs and wholly standard support sections.

    Retain original line numbers and page boundaries. Never extend a legal
    paragraph across a heading, table, image or page marker.
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
                if placeholders:
                    out.append((number, f'({title} omitted: vendor boilerplate; see PDF.)'))
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
                if placeholders:
                    out.append((number, f'({title} omitted: vendor boilerplate; see PDF.)'))
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
            legal_title = ('IMPORTANT NOTICE AND DISCLAIMER' if text.lower().startswith(('ti provides', 'these resources', "ti's", 'ti’s', 'ti objects', 'mailing address:'))
                           else 'Legal Terms and Conditions')
            if legal_paragraph(text) or trademark_legal(text):
                if trademark_legal(text):
                    legal_title = 'Trademarks'
                # Adjacent legal paragraphs belong to one omitted span.
                if placeholders and not (out and out[-1][1] == f'({legal_title} omitted: vendor boilerplate; see PDF.)'):
                    out.append((number, f'({legal_title} omitted: vendor boilerplate; see PDF.)'))
                i = end
                # Blank lines between legal paragraphs should not create placeholders.
                while i < len(lines) and not lines[i][1].strip():
                    i += 1
                continue
        out.append(lines[i])
        i += 1
    return out


def section_filter(lines):
    """Keep (line number, text), omitting only explicitly unwanted sections."""
    lines = vendor_filter(lines)
    result = []
    section = None
    revision = False
    previous = ''
    for number, line in lines:
        heading = HEADING.match(line)
        if heading and section and (len(heading[1]) <= section or (not revision and (re.search(r'revision history', heading[2], re.I) or PAGE.match(previous)))) and not (revision and re.match(r'[* ]*\d{1,2}/\d{4}', heading[2])):
            section = None
        if section:
            if line.strip():
                previous = line
            # Page boundaries remain useful even within an omitted section.
            if PAGE.match(line):
                result.append((number, line))
            continue
        if heading and re.search(r'\b(table of contents|revision history)\b', heading[2], re.I):
            section = len(heading[1])
            revision = bool(re.search('revision history', heading[2], re.I))
            if re.search('revision history', heading[2], re.I):
                result.extend([(number, line), (number, '(Revision history omitted; see PDF.)')])
            continue
        result.append((number, line))
    # Standalone TOC tables: dotted leaders in several rows, with page references.
    out = []
    i = 0
    while i < len(result):
        j = i
        if result[i][1].strip().startswith('|'):
            while j < len(result) and result[j][1].strip().startswith('|'):
                j += 1
            block = result[i:j]
            dotted = [s for _, s in block if re.search(r'\.{3,}', s)]
            if len(dotted) >= 2 and all(re.search(r'\d\s*(?:</b>)?\s*\|', s) for s in dotted):
                i = j
                continue
        out.append(result[i])
        i += 1
    return out


SYMBOLS = {
    'circ': '°', 'mu': 'µ', 'Omega': 'Ω', 'pm': '±', 'leq': '≤', 'le': '≤',
    'geq': '≥', 'ge': '≥', 'neq': '≠', 'times': '×', 'cdot': '·',
    'approx': '≈', 'cong': '≅', 'equiv': '≡', 'sim': '~', 'infty': '∞',
    'quad': ' ', 'qquad': ' ', 'left': '', 'right': '', 'lvert': '|',
    'rvert': '|', 'parallel': '∥', 'dots': '…',
}
for _name in ('alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi '
              'omicron pi rho sigma tau upsilon phi chi psi omega').split():
    for _variant in (_name, _name.capitalize()):
        if _variant not in SYMBOLS:
            SYMBOLS[_variant] = unicodedata.lookup('GREEK ' + ('CAPITAL' if _variant[0].isupper() else 'SMALL') + ' LETTER ' + _name.upper().replace('LAMBDA', 'LAMDA'))
SYMBOLS.update({'varepsilon': 'ε', 'vartheta': 'ϑ', 'varphi': 'ϕ', 'varrho': 'ϱ', 'varsigma': 'ς', 'varpi': 'ϖ'})


def latex(text):
    """Small recursive TeX reader: retain all unknown command names and arguments."""
    def group(pos):
        while pos < len(text) and text[pos].isspace():
            pos += 1
        if pos < len(text) and text[pos] == '{':
            return parse(pos + 1, True)
        if pos < len(text) and text[pos] == '\\':
            return command(pos)
        return (text[pos:pos + 1], pos + 1)

    def command(pos):
        match = re.match(r'\\([A-Za-z]+|.)', text[pos:])
        if not match:
            return '\\', pos + 1
        name = match[1]
        pos += len(match[0])
        if name in ('text', 'mathrm', 'mathbf', 'textbf', 'mathit', 'operatorname'):
            return group(pos)
        if name == 'frac':
            a, pos = group(pos)
            b, pos = group(pos)
            def wrap(x):
                return x if re.fullmatch(r'[\w.]+', x) else '(' + x + ')'
            return wrap(a) + '/' + wrap(b), pos
        if name in ('sqrt', 'overline', 'bar'):
            value, pos = group(pos)
            return ('√(' + value + ')' if name == 'sqrt' else '/' + value), pos
        return SYMBOLS.get(name, name if name not in (',', ';', '!', ' ') else ' '), pos

    def parse(pos, grouped=False):
        out = []
        while pos < len(text):
            char = text[pos]
            if char == '}' and grouped:
                return ''.join(out), pos + 1
            if char == '\\':
                value, pos = command(pos)
                out.append(value)
            elif char in '_^':
                value, pos = group(pos + 1)
                out.append(('' if char == '^' and value == '°' else char) + value)
            elif char == '{':
                value, pos = parse(pos + 1, True)
                out.append(value)
            else:
                out.append(char)
                pos += 1
        return ''.join(out), pos
    return parse(0)[0]


def _inline_plain(text, table=False):
    text = html.unescape(text)
    while re.search(r'<sub\b[^>]*>', text, re.I):
        updated = re.sub(r'\s*<sub\b[^>]*>((?:(?!</?sub\b).)*)</sub>', lambda m: '_' + m[1], text, flags=re.I)
        if updated == text:
            break
        text = updated
    text = re.sub(r'<sup\b[^>]*>(.*?)</sup>', lambda m: m[1] if re.fullmatch(r'\(.*\)', m[1]) else '^' + m[1], text, flags=re.I)
    text = re.sub(r'<br\s*/?>', '; ' if table else '\n', text, flags=re.I)
    text = re.sub(r'</?(?:b|i|u|a|strong|em)\b[^>]*>', '', text, flags=re.I)
    text = re.sub(r'\[([^\]]*)\]\(#\)', r'\1', text)
    text = re.sub(r'\${1,2}(.*?)\${1,2}', lambda m: latex(m[1].strip()), text, flags=re.S)
    if re.search(r'\\[A-Za-z]+|[_^]\{', text):
        text = latex(text)
    # TeX commands also occur outside math delimiters. Do not parse ordinary ^/_
    # again: doing so would make flattened nested subscripts non-idempotent.
    text = re.sub(r'\\([_#%&()\[\]])', r'\1', text)
    text = re.sub(r'\.{3,}', '', text)
    # Paired prose emphasis only: underscores within identifiers stay literal.
    for _ in range(3):
        for marker in ('**', '__', '*', '_'):
            escaped = re.escape(marker)
            boundary = r'\w' if marker[0] == '_' else r'\*'
            text = re.sub(r'(?<![' + boundary + r'\\])' + escaped
                          + r'(?=\S)(.+?)(?<=\S)' + escaped
                          + r'(?![' + boundary + r'])', r'\1', text)
    # Extracted captions can split bold across lines or leave a lone closer.
    text = re.sub(r'(?<!\\)\*\*', '', text)
    text = re.sub(r'(?<!\S)[–−](?=\d)|(?<=[(=])[–−](?=\d)', '-', text)
    text = re.sub(r',[^\S\n]*;', ';', text)
    text = re.sub(r'[^\S\n]+([,;:)\]])', r'\1', text)
    text = re.sub(r'[^\S\n]+\.(?=\s|$)', '.', text)
    text = re.sub(r'([(\[])[^\S\n]+', r'\1', text)
    text = re.sub(r'([±Δ])[^\S\n]+(?=\S)', r'\1', text)
    text = re.sub(r'([µμ])[^\S\n]+(?=[^\W\d_])', r'\1', text)
    return re.sub(r'[^\S\n]{2,}', ' ', text).strip()


def inline(text, table=False):
    # Protect literal spans while allowing cleanup at their prose boundaries.
    spans = []
    sentinel = '\ue000'
    while sentinel in text:
        sentinel += '\ue000'
    def protect(match):
        spans.append(match[0])
        return sentinel + str(len(spans) - 1) + sentinel
    text = re.sub(r'(?<!`)(`+)(?!`)(.*?)\1(?!`)', protect, text)
    text = _inline_plain(text, table)
    return re.sub(re.escape(sentinel) + r'(\d+)' + re.escape(sentinel),
                  lambda m: spans[int(m[1])], text)


SUMMARY_BEGIN = '<!-- summary: begin. Cross-checked against this datasheet; not part of the verbatim text. -->'
SUMMARY_END = '<!-- summary: end -->'
INDEX_BEGIN = '<!-- section index: begin -->'
INDEX_END = '<!-- section index: end -->'


def section_index(body):
    """Top-level headings (# and ##) with the PDF page they start on."""
    page, entries = None, []
    for line in body.splitlines():
        marker = re.fullmatch(r'\[p(\d+)\]', line)
        if marker:
            page = marker[1]
            continue
        heading = re.match(r'^(#{1,2})\s+(.*\S)\s*$', line)
        if not heading:
            continue
        title = re.sub(r'\*+', '', heading[2]).strip()
        if re.search(r'\(continued\)\s*$', title, re.I) or (entries and entries[-1][0].lower() == title.lower()):
            continue
        entries.append((title, page))
    return [f'- {title}' + (f' [p{pg}]' if pg else '') for title, pg in entries]


def compact(text, source='source.md', summary=None):
    if text.startswith('<!-- pdf2llm compact:'):
        return text  # Canonical output is a fixed point; never reinterpret literal text.
    lines = section_filter(list(enumerate(text.splitlines(), 1)))
    output = []
    i = 0
    in_code = False
    list_indents = []
    while i < len(lines):
        line = lines[i][1]
        if line.lstrip().startswith(('```', '~~~')):
            in_code = not in_code
        if in_code or line.lstrip().startswith(('```', '~~~')):
            output.append(line.rstrip())
            i += 1
            continue
        page = PAGE.match(line)
        img = IMAGE.match(line.strip())
        if page:
            output.append('[p' + str(int(page[1]) + 1) + ']')
        elif img:
            alt = img[1]
            j = i + 1
            while j < len(lines) and not lines[j][1].strip():
                j += 1
            end = j
            while end < len(lines) and lines[end][1].strip() and not re.match(r'^(?:#|\||!\[|\{\d+\}|\*\*)', lines[end][1]):
                end += 1
            paragraph = ' '.join(s for _, s in lines[j:end])
            a, b = ' '.join(inline(alt).split()), ' '.join(inline(paragraph).split())
            duplicate = bool(a and b and (a.startswith(b) or b.startswith(a)))
            if not ICONS.fullmatch(html.unescape(alt)):
                # When the repeat is longer, keep it so prefix matching loses no data.
                text = inline(paragraph if duplicate and len(b) > len(a) else alt)
                if text.strip():
                    output.append(f'Figure {img[2].strip()} (description only, not data): ' + text)
                else:
                    output.append(f'Figure {img[2].strip()} (image only; no description)')
            if duplicate:
                i = end - 1
        elif line.strip().startswith('|') and line.strip().endswith('|'):
            rows = []
            while i < len(lines) and lines[i][1].strip().startswith('|') and lines[i][1].strip().endswith('|'):
                rows.append(cells(lines[i][1]))
                i += 1
            width = max(map(len, rows))
            rows = [(['-'] * width if is_separator(r) else r + [''] * (width - len(r))) for r in rows]
            keep = [k for k in range(width) if any(r[k].strip() for r in rows if not is_separator(r))]
            for row in rows:
                values = ['-' for _ in keep] if is_separator(row) else [re.sub(r'(?<!\\)\|', r'\\|', inline(row[k], True)) for k in keep]
                output.append('|' + '|'.join(values) + '|')
            continue
        else:
            item = re.match(r'^(\s*)([-+*]|\d+[.)])\s+(.*)$', line)
            if item:
                indent = len(item[1].expandtabs(4))
                while list_indents and indent < list_indents[-1]:
                    list_indents.pop()
                if not list_indents or indent > list_indents[-1]:
                    list_indents.append(indent)
                output.append('  ' * (len(list_indents) - 1) + item[2] + ' ' + inline(item[3]))
            else:
                if line.strip() and not line[:1].isspace():
                    list_indents.clear()
                output.append(inline(line))
        i += 1
    body = re.sub(r'\n{3,}', '\n\n', '\n'.join(output)).strip()
    legend = f'<!-- pdf2llm compact: {source}. [pN] = PDF page N, 1-based (the full .md marks that page {{N-1}}). "Figure (description only, not data)" lines are AI image descriptions (image file given), not measured data. A cross-checked summary and a section index come first; the datasheet text follows. ● = spec applies over full temperature range (as printed). -->'
    head = [legend, '']
    if summary and summary.strip():
        head += [SUMMARY_BEGIN, summary.strip(), SUMMARY_END, '']
    index = section_index(body)
    if index:
        head += [INDEX_BEGIN, '## Section index', '', *index, INDEX_END, '']
    return '\n'.join(head) + '\n' + body + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all', action='store_true')
    parser.add_argument('names', nargs='*')
    args = parser.parse_args()
    if args.all and args.names:
        parser.error('Use --all or names, not both')
    for path in sources(args.names):
        target = path.with_name(path.parent.name + '.llm.md')
        summary_path = ROOT / 'reports' / 'llm' / 'summaries' / (path.parent.name + '.md')
        summary = summary_path.read_text(encoding='utf-8') if summary_path.exists() else None
        target.write_text(compact(path.read_text(), str(path.relative_to(ROOT)), summary), encoding='utf-8')
        print(target.relative_to(ROOT))


if __name__ == '__main__':
    main()
