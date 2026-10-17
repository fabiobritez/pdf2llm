"""Deterministic, conservative Markdown compaction (standard library only)."""
import argparse
import html
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
PAGE = re.compile(r'^\{(\d+)\}-{3,}\s*$')
IMAGE = re.compile(r'^!\[(.*)\]\([^\n]*\)\s*$')
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


def section_filter(lines):
    """Keep (line number, text), omitting only explicitly unwanted sections."""
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
    text = re.sub(r'\*\*(Figure\s+\d+\b.*?)\*\*', r'\1', text)
    return re.sub(r'[^\S\n]{2,}', ' ', text).strip()


def inline(text, table=False):
    # Backtick spans are literal code, including their internal whitespace.
    parts = re.split(r'(`+[^`]*`+)', text)
    return ''.join(part if part.startswith('`') else ((' ' if part[:1].isspace() else '') + _inline_plain(part, table) + (' ' if part[-1:].isspace() else ''))
                   for part in parts).strip() if len(parts) > 1 else _inline_plain(text, table)


def compact(text, source='source.md'):
    if text.startswith('<!-- pdf2llm compact:'):
        return text  # Canonical output is a fixed point; never reinterpret literal text.
    lines = section_filter(list(enumerate(text.splitlines(), 1)))
    output = []
    i = 0
    in_code = False
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
                output.append('Figure (description only, not data): ' + inline(paragraph if duplicate and len(b) > len(a) else alt))
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
            output.append(inline(line))
        i += 1
    body = re.sub(r'\n{3,}', '\n\n', '\n'.join(output)).strip()
    legend = f'<!-- pdf2llm compact: {source}. [pN] = PDF page N. "Figure (description only, not data)" lines are AI image descriptions, not measured data. ● = spec applies over full temperature range (as printed). -->'
    return legend + '\n\n' + body + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all', action='store_true')
    parser.add_argument('names', nargs='*')
    args = parser.parse_args()
    if args.all and args.names:
        parser.error('Use --all or names, not both')
    for path in sources(args.names):
        target = path.with_name(path.parent.name + '.llm.md')
        target.write_text(compact(path.read_text(), str(path.relative_to(ROOT))), encoding='utf-8')
        print(target.relative_to(ROOT))


if __name__ == '__main__':
    main()
