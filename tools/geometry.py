"""Conservative, offline table-column verification using PDF word coordinates.

Only numeric-baseline rows with distinctive, uniquely matched prose are checked.
Headerless continuations inherit the page's PDF schema, aligned at the right.
Ambiguous matches, wrapped values and unsupported schemas remain unverifiable.
"""
from collections import Counter
from difflib import SequenceMatcher
from decimal import Decimal
import re

LABELS = {'MIN', 'TYP', 'NOM', 'MAX', 'VALUE', 'UNIT', 'UNITS'}
VALUES = LABELS - {'UNIT', 'UNITS'}


def label(text):
    text = text.upper().strip(' .:')
    return 'UNIT' if text == 'UNITS' else text


def prose(text, normalize):
    text = re.sub(r'<sup>.*?</sup>', '', text, flags=re.I)
    text = normalize(text).lower()
    text = re.sub(r'\(\d+\)', '', text)
    return re.findall(r'[a-z]+\d*|\d+(?:\.\d+)?', text)


def signature(text, normalize):
    """Keep signs (including ±) and supply expressions; ignore unit typography."""
    text = normalize(text)
    allowed = {'ohm', 'omega', 'degC', 'ppm', 'sqrt', 'Hz'}
    if any(len(t) > 2 and not t.isupper() and t not in allowed
           for t in re.findall(r'[A-Za-z]+', text)):
        return ()
    text = text.replace('%', '')
    # Numeric signatures deliberately exclude device selectors such as A1.
    result = []
    for token in re.findall(r'(?<![\w.])(?:\+-|[+-])?(?:\d+(?:\.\d+)?|\.\d+)', text):
        symmetric = token.startswith('+-')
        value = Decimal(token[2:] if symmetric else token)
        canonical = format(value.normalize(), 'f') if value else '0'
        result.append(('+-' if symmetric else '') + canonical)
    return tuple(result)


def headers(words, right):
    groups = []
    for word in sorted(words, key=lambda w: (w[1], w[0])):
        name = label(word[4])
        if name not in LABELS or not (word[4] == word[4].upper() or word[4] == word[4].capitalize()):
            continue
        y = (word[1] + word[3]) / 2
        group = next((g for g in groups if abs(g['y'] - y) <= 3), None)
        if group is None:
            group = dict(y=y, words=[])
            groups.append(group)
        group['words'].append((name, (word[0] + word[2]) / 2, word[4] == word[4].upper()))
    result = []
    for group in groups:
        if not all(upper for _, _, upper in group['words']) and len(group['words']) < 3:
            continue  # Title-case labels only count as a header in a full Min/Typ/Max row.
        cols = sorted(((n, x) for n, x, _ in group['words']), key=lambda item: item[1])
        if len(cols) < 2 or not any(n in VALUES for n, _ in cols):
            continue
        if len({n for n, _ in cols}) != len(cols):
            continue  # Two side-by-side tables need a more specific schema.
        centers = [x for _, x in cols]
        edges = [centers[0] - (centers[1] - centers[0]) / 2]
        edges += [(a + b) / 2 for a, b in zip(centers, centers[1:])]
        prose_right = None
        tail = [w for w in words if abs((w[1] + w[3]) / 2 - group['y']) <= 3 and w[0] > centers[-1] + 5
                and re.match(r'(?i)(test|conditions?|comments?)', w[4])]
        if tail:
            prose_right = min(w[0] for w in tail) - 4
        edges.append(prose_right or right)
        result.append(dict(y=group['y'], columns=[n for n, _ in cols], edges=edges, prose_right=prose_right))
    return sorted(result, key=lambda h: h['y'])


def is_prose(word, schema):
    """Parameter/condition text: left of the value columns, or right of them (ADI layout)."""
    x = (word[0] + word[2]) / 2
    return x < schema['edges'][0] or (schema.get('prose_right') is not None and x >= schema['prose_right'])


def column(x, header):
    return next((name for name, left, right in zip(header['columns'], header['edges'], header['edges'][1:])
                 if left <= x < right), None)


def bands(words, schema, bottom, normalize):
    """Use value baselines, not extraction block order, to assemble physical rows."""
    numeric = [w for w in words if schema['y'] + 4 < (w[1] + w[3]) / 2 < bottom
               and column((w[0] + w[2]) / 2, schema) in VALUES
               and signature(w[4], normalize)]
    ys = []
    for word in sorted(numeric, key=lambda w: (w[1] + w[3]) / 2):
        y = (word[1] + word[3]) / 2
        if not ys or y - ys[-1] > 4:
            ys.append(y)
    result = []
    for y in ys:
        local = [w for w in words if abs((w[1] + w[3]) / 2 - y) <= 4]
        cells = {}
        for name in schema['columns']:
            selected = [w for w in local if column((w[0] + w[2]) / 2, schema) == name]
            cells[name] = ' '.join(w[4] for w in sorted(selected, key=lambda w: w[0]))
        result.append(dict(y=y, cells=cells))
    return result


def match_row(cells, schema, candidates, words, normalize):
    """Fuzzy token recall on local prose, with weaker support from shared labels.

    A local condition can identify a row whose parameter spans multiple baselines.
    Nearby parameter support distinguishes e.g. A1 under Gain from A1 under RVRR.
    Numeric agreement never selects a row, so a corrupt value cannot steer it.
    """
    queries = []
    for cell in cells:
        terms = prose(cell, normalize)
        if len(set(terms)) >= 2 and any(len(t) >= 3 and t.isalpha() for t in terms) and not re.fullmatch(r'[\d.()+*/x+%\- A-Z]+', normalize(cell)):
            queries.append(terms)
    if not queries:
        return None
    left_words = [(w, prose(w[4], normalize)) for w in words if is_prose(w, schema)]
    physical = {}
    for word, terms in left_words:
        physical.setdefault(tuple(word[5:7]), []).append(word)
    lines = []
    for group in physical.values():
        group.sort(key=lambda w: w[0])
        lines.append((group[0][0], sum((w[1]+w[3])/2 for w in group)/len(group),
                      prose(' '.join(w[4] for w in group), normalize)))
    anchors = []
    for x, y, terms in lines:
        joined = list(terms)
        if joined == queries[0]:
            anchors.append(y)
        for _, yy, more in sorted((ln for ln in lines if abs(ln[0]-x)<2 and y+2<ln[1]<=y+20), key=lambda ln: ln[1]):
            joined += more
            if joined == queries[0]:
                anchors.append((y+yy)/2)
    selector = next((i for i, q in reversed(list(enumerate(queries))) if 'devices' in q), None)
    scored = []
    for candidate in candidates:
        y = candidate['y']
        local = [t for w, ts in left_words if abs((w[1] + w[3]) / 2 - y) <= 5 for t in ts]
        nearby = [t for w, ts in left_words if abs((w[1] + w[3]) / 2 - y) <= 30 for t in ts]
        scores = []
        for query in queries:
            def recall(target):
                return sum(any(a == b or (len(a) > 4 and SequenceMatcher(None, a, b).ratio() >= .88)
                               for b in target) for a in query) / len(query)
            scores.append((recall(local), recall(nearby), len(query)))
        primary = selector if selector is not None else len(queries)-1
        required_numbers = {t for t in queries[primary] if re.fullmatch(r'\d+(?:\.\d+)?', t)}
        if scores[primary][0] < .95 or not required_numbers.issubset(local):
            continue
        strong = [s for s in scores if s[0] >= .85]
        if not strong:
            continue
        # Full long conditions and unique parameter labels outrank generic prose.
        score = max(s[0] + min(s[2], 12) * .008 for s in strong)
        score += .24 * sum(s[1] for s in scores) / len(scores)
        if anchors:
            distance = min(abs(y-a) for a in anchors)
            score += .25 * max(0, 1-distance/40)
        scored.append((score, candidate))
    scored.sort(key=lambda item: (-item[0], item[1]['y']))
    # Repeated conditions on adjacent baselines often differ only by a
    # temperature bullet; a shared, vertically centered parameter cannot
    # distinguish them reliably. Do not let its position break that tie.
    adjacent = len(scored) > 1 and abs(scored[0][1]['y'] - scored[1][1]['y']) <= 20
    if not scored or adjacent or (len(scored) > 1 and scored[0][0] - scored[1][0] < .035):
        return None
    return scored[0][1]


def match_by_values(raw, mappings, schema, candidates, words, normalize):
    """Fallback row match on the numeric values themselves.

    Used only when prose matching fails. The md row's value tokens (from its
    MIN/TYP/MAX/VALUE/UNIT cells) must form a sub-multiset of exactly one PDF
    band's value tokens. With a single token we additionally require some
    prose overlap near that band, so a lone "5" cannot pick an arbitrary row.
    Column placement is never used to choose the band, so column errors stay
    detectable; a value that was transcribed wrongly simply yields no match.
    """
    tokens = Counter(t for i, name in mappings.items() if i < len(raw)
                     for t in signature(raw[i], normalize)
                     if name in VALUES or name == 'UNIT')
    if not tokens:
        return None
    hits = []
    for candidate in candidates:
        have = Counter(t for name, value in candidate['cells'].items() if name in VALUES
                       for t in signature(value, normalize))
        if all(have[t] >= c for t, c in tokens.items()):
            hits.append(candidate)
    if len(hits) != 1:
        return None
    if sum(tokens.values()) < 2:
        terms = [t for c in raw[:min(mappings)] for t in prose(c, normalize) if len(t) >= 3 and t.isalpha()]
        y = hits[0]['y']
        local = {t for w in words if abs((w[1] + w[3]) / 2 - y) <= 12
                 and is_prose(w, schema) for t in prose(w[4], normalize)}
        if not terms or sum(t in local for t in terms) / len(terms) < .5:
            return None
    return hits[0]


def check_tables(text, document, table_blocks, normalize):
    issues, stats = [], Counter(verified_ok=0, mismatched=0, unverifiable=0, value_matched=0)
    markers = [(text.count('\n', 0, m.start()) + 1, int(m[1]))
               for m in re.finditer(r'^\{(\d+)\}-{8,}\s*$', text, re.M)]
    cache = {}
    inherited = {}
    for block in table_blocks(text):
        if not block:
            continue
        page_no = next((p for line, p in reversed(markers) if line <= block[0][0]), 0)
        if page_no >= len(document):
            continue
        if page_no not in cache:
            page = document[page_no]
            words = page.get_text('words')
            schemas = headers(words, page.rect.width)
            cache[page_no] = (words, [(h, bands(words, h, schemas[i+1]['y'] if i+1 < len(schemas)
                                             else page.rect.height - 35, normalize)) for i, h in enumerate(schemas)])
        words, schemas = cache[page_no]
        md_columns = None
        first = [label(normalize(c)) for c in block[0][1]]
        unsupported_header = (any(first) and not any(c in LABELS for c in first)
                              and not any(signature(c, normalize) for c in block[0][1]))
        unsupported = unsupported_header or any('UNIT' in [label(normalize(c)) for c in row[1]]
                          and not any(label(normalize(c)) in VALUES for c in row[1]) for row in block)
        for line, raw in block:
            cells = [normalize(c) for c in raw]
            labels = [label(c) for c in cells]
            if any(c in VALUES for c in labels):
                md_columns = {i: c for i, c in enumerate(labels) if c in LABELS}
                inherited[page_no] = md_columns
                continue
            if not any(cells):
                continue
            # Keep prose misplaced in value cells as potential row anchors.
            if not any(signature(c, normalize) for c in cells):
                continue
            if unsupported:
                stats['unverifiable'] += 1
                continue
            mappings = md_columns
            if mappings is None:
                previous = inherited.get(page_no)
                if previous and max(previous) == len(cells) - 1:
                    mappings = previous
                elif len(schemas) == 1 and len(cells) >= len(schemas[0][0]['columns']) + 1:
                    names = schemas[0][0]['columns']
                    mappings = dict(zip(range(len(cells)-len(names), len(cells)), names))
                elif previous:
                    names = list(previous.values())
                    mappings = dict(zip(range(len(cells)-len(names), len(cells)), names))
            if not mappings or max(mappings) >= len(cells):
                stats['unverifiable'] += 1
                continue
            matches = []
            for schema, candidates in schemas:
                if set(mappings.values()) != set(schema['columns']):
                    continue
                found = match_row(raw, schema, candidates, words, normalize)
                if found:
                    matches.append((schema, found))
            if not matches:
                for schema, candidates in schemas:
                    if set(mappings.values()) != set(schema['columns']):
                        continue
                    found = match_by_values(raw, mappings, schema, candidates, words, normalize)
                    if found:
                        matches.append((schema, found))
                if len(matches) == 1:
                    stats['value_matched'] += 1
            if len(matches) != 1:
                stats['unverifiable'] += 1
                continue
            schema, found = matches[0]
            if any(len(signature(cells[i], normalize)) > len(signature(found['cells'].get(name, ''), normalize))
                   and len(signature(cells[i], normalize)) > 1 for i, name in mappings.items()):
                stats['unverifiable'] += 1
                continue
            start = len(issues)
            parameter = ' / '.join(c for c in cells[:min(mappings)] if c) or next((c for c in cells if c), '')

            def emit(kind, value, md_col, pdf_col):
                detail = f'{value}: Markdown {md_col}, PDF {pdf_col}'
                issues.append(dict(type=kind, page=page_no+1, line=line, md_line=line,
                                   parameter=parameter, value=value, md_column=md_col,
                                   pdf_column=pdf_col, confidence='high', detail=detail,
                                   row=' | '.join(cells)[:240]))

            pdf_values = {name: signature(value, normalize) for name, value in found['cells'].items() if name in VALUES}
            md_values = {i: signature(cells[i], normalize) for i in mappings}
            # A condition under MIN is a geometry error even if numeric values
            # happen to remain in their correct TYP/MAX columns.
            for i, name in mappings.items():
                terms = prose(raw[i], normalize)
                if name in VALUES and len(terms) >= 2 and not md_values[i] and not re.fullmatch(r'[A-Z\W]+', cells[i]):
                    local = ' '.join(w[4] for w in words if abs((w[1]+w[3])/2-found['y']) <= 9
                                     and is_prose(w, schema))
                    target = prose(local, normalize)
                    if all(t in target for t in terms):
                        emit('geometry column mismatch', cells[i], name, 'CONDITIONS')
                for token in md_values[i]:
                    actual = [n for n, values in pdf_values.items() if token in values]
                    if name not in actual and len(actual) == 1:
                        emit('geometry column mismatch', token, name, actual[0])
            # Match occurrences in their own column first, then allow moved
            # occurrences. Equal limits in two columns still need two cells.
            remaining = {name: Counter(values) for name, values in pdf_values.items()}
            displaced = []
            for i, values in md_values.items():
                for token in values:
                    own = remaining.get(mappings[i], Counter())
                    if own[token]:
                        own[token] -= 1
                    else:
                        displaced.append(token)
            for token in displaced:
                target = next((counts for counts in remaining.values() if counts[token]), None)
                if target is not None:
                    target[token] -= 1
            row_text = normalize(' '.join(raw))
            for name, counts in remaining.items():
                if any(count > 0 for count in counts.values()):
                    pdf_cell = found['cells'][name]
                    # Formula cells (e.g. "20 + 0.1CB") are often transcribed into
                    # another column as LaTeX; only flag them if their numbers are absent.
                    if re.search(r'[A-Za-z]', pdf_cell) and all(t.lstrip('+-') in row_text for t in counts if counts[t] > 0):
                        continue
                    emit('geometry missing value', pdf_cell, 'MISSING', name)
            # Blank units can be shared over many rows. Compare printed units
            # when both sides provide one; numeric-only unit cells are corrupt.
            for i, name in mappings.items():
                if name != 'UNIT' or not cells[i] or not found['cells'].get('UNIT'):
                    continue
                def unit_key(value):
                    value = normalize(value).replace('omega', 'ohm').replace('√', 'sqrt')
                    value = value.replace('%', '')
                    return re.sub(r'[\s{}\\]+', '', value)
                md_unit = unit_key(re.sub(r"^[\d.±+\-\s]+", "", cells[i]))
                pdf_unit = unit_key(found['cells']['UNIT'])
                if md_unit != pdf_unit:
                    if md_unit:
                        emit('geometry column mismatch', cells[i], 'UNIT', 'UNIT (' + pdf_unit + ')')
                    else:
                        emit('geometry missing value', found['cells']['UNIT'], 'MISSING', 'UNIT')
            stats['mismatched' if len(issues) > start else 'verified_ok'] += 1
    return issues, dict(stats)
