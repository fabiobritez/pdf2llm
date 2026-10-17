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
        if not all(upper for _, _, upper in group['words']) and not {'MIN', 'MAX'}.issubset(
                {name for name, _, _ in group['words']}):
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
                and re.fullmatch(r'(?i)(?:test|conditions?|comments?)(?:/(?:conditions?|comments?))*[:.]?', w[4])]
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


UNVERIFIED = []  # debug: rows counted as unverifiable, with the reason (reset by callers)
AMBIGUOUS = {'ambiguous': True}  # marker: several rows matched equally (with 'tied' candidates)


def is_ambiguous(found):
    return isinstance(found, dict) and found.get('ambiguous') is True


def row_tables(block, schemas, normalize):
    """Per md row: the PDF table it belongs to, from the row's own values.

    A row votes only when its full set of numeric values occurs in a band of
    exactly one table on the page; Abs Max and Recommended tables share labels
    such as "Input voltage", but rarely whole value sets. Rows without a vote
    take the table of their nearest voting neighbours when those agree, so a md
    block that merges two PDF tables is still split at the right place.
    """
    votes = []
    columns = None  # md indices of value columns, from the block's header row
    for _, raw in block:
        labels = [label(normalize(c)) for c in raw]
        if any(c in VALUES for c in labels):
            columns = [i for i, c in enumerate(labels) if c in VALUES]
            votes.append(None)
            continue
        cells = [raw[i] for i in columns if i < len(raw)] if columns else raw
        sigs = [sig for sig in (signature(c, normalize) for c in cells) if sig]
        hit = [h for h, cands in schemas
               if sigs and any(all(any(sig == signature(v, normalize) for v in c['cells'].values()) for sig in sigs)
                               for c in cands)]
        votes.append(hit[0] if len(hit) == 1 else None)
    result = []
    for k, vote in enumerate(votes):
        if vote is None:
            before = next((v for v in reversed(votes[:k]) if v is not None), None)
            after = next((v for v in votes[k+1:] if v is not None), None)
            vote = before if after is None or after is before else after if before is None else None
        result.append(vote)
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
        # numeric ranges such as "1.1V to 1.3V" identify a sub-row as well as words do
        if len(set(terms)) >= 2 and (any(len(t) >= 3 and t.isalpha() for t in terms) or sum(bool(re.search(r"\d", t)) for t in terms) >= 2) and not re.fullmatch(r'[\d.()+*/x+%\- A-Z]+', normalize(cell)):
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
    ys = [c['y'] for c in candidates]
    owner = {id(w): min(ys, key=lambda cy: abs((w[1] + w[3]) / 2 - cy)) for w, _ in left_words} if ys else {}
    scored = []
    for candidate in candidates:
        y = candidate['y']
        # A word belongs to the nearest band only: tightly packed rows (3-4 pt
        # apart) must not borrow a neighbour's condition, e.g. "+105°C".
        local = [t for w, ts in left_words if abs((w[1] + w[3]) / 2 - y) <= 5
                 and owner.get(id(w), y) == y for t in ts]
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
    if not scored:
        return None
    if adjacent or (len(scored) > 1 and scored[0][0] - scored[1][0] < .035):
        top = scored[0][0]
        return dict(AMBIGUOUS, tied=[c for sc, c in scored if top - sc < .035 or abs(c['y'] - scored[0][1]['y']) <= 20])
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
    if len(hits) > 1:
        return dict(AMBIGUOUS, tied=hits)
    if not hits:
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
    # out_of_scope: rows of tables without MIN/TYP/MAX/VALUE columns (registers,
    # pin lists, ordering info) or on pages with no such PDF header. They are not
    # spec values this check can verify, so they are not counted as unverifiable.
    issues, stats = [], Counter(verified_ok=0, mismatched=0, unverifiable=0, value_matched=0, out_of_scope=0)
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
        previous_band = None  # (schema, candidates, index) of the last matched md row in this block
        tables = row_tables(block, schemas, normalize) if len(schemas) > 1 else [None] * len(block)
        for (line, raw), preferred in zip(block, tables):
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
                stats['out_of_scope'] += 1
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
            def unverifiable(reason, line=line, page_no=page_no, cells=cells):
                stats['unverifiable'] += 1
                stats['unverifiable_' + reason] += 1
                UNVERIFIED.append(dict(page=page_no + 1, line=line, reason=reason, row=' | '.join(cells)[:200]))
            if not mappings and not schemas:
                stats['out_of_scope'] += 1
                continue
            if not mappings or max(mappings) >= len(cells):
                unverifiable('mapping')
                continue
            matches = []
            tied = []
            ambiguous = value_ambiguous = False
            for schema, candidates in schemas:
                if set(mappings.values()) != set(schema['columns']):
                    continue
                found = match_row(raw, schema, candidates, words, normalize)
                if is_ambiguous(found):
                    ambiguous = True
                    tied.append((schema, candidates, found['tied']))
                elif found:
                    matches.append((schema, found))
            # A clear prose hit in another table (e.g. Abs Max "Supply voltage")
            # must not win when the row's own table matched several rows.
            if ambiguous:
                matches = []
            if not matches:
                for schema, candidates in schemas:
                    if set(mappings.values()) != set(schema['columns']):
                        continue
                    found = match_by_values(raw, mappings, schema, candidates, words, normalize)
                    if is_ambiguous(found):
                        value_ambiguous = True
                        tied.append((schema, candidates, found['tied']))
                    elif found:
                        matches.append((schema, found))
                # the values recur in another table on the page: no unique row
                if value_ambiguous:
                    matches = []
                if len(matches) == 1:
                    stats['value_matched'] += 1
            if len(matches) > 1 and preferred is not None:
                # the same label in two tables (Abs Max vs Recommended)
                own = [m for m in matches if m[0] is preferred]
                if len(own) == 1:
                    matches = own
                    stats['table_matched'] += 1
            same_cells = False
            if len(matches) > 1 and len({tuple(sorted((k, normalize(v)) for k, v in f['cells'].items() if k != 'UNIT'))
                                          for _, f in matches}) == 1:
                # identical value rows in two tables (e.g. one per VBIAS): the
                # column check is the same whichever table it is
                matches = matches[:1]
                same_cells = True
                stats['table_matched'] += 1
            if len(matches) != 1 and tied and previous_band is not None:
                # Order constraint: consecutive md rows follow consecutive PDF
                # rows. Among equally good candidates take the band right after
                # the previous row's band, only if that band is one of the ties.
                schema0, candidates0, row_index = previous_band
                follow = [(sc, c) for sc, cands, ties in tied if sc is schema0
                          for c in ties if row_index + 1 < len(cands) and c is cands[row_index + 1]]
                follow = list({id(c): (sc, c) for sc, c in follow}.values())  # prose and value ties may repeat
                if len(follow) == 1:
                    matches = follow
                    stats['order_matched'] += 1
            if len(matches) != 1:
                previous_band = None
                same = [sc for sc, _ in schemas if set(mappings.values()) == set(sc['columns'])]
                unverifiable('no_schema' if not same else 'prose_ambiguous' if ambiguous
                             else 'value_ambiguous' if value_ambiguous
                             else 'multi_table' if matches else 'no_match')
                continue
            schema, found = matches[0]
            cands = next(c for sc, c in schemas if sc is schema)
            previous_band = None if same_cells else (schema, cands, next(i for i, c in enumerate(cands) if c is found))
            if any(len(signature(cells[i], normalize)) > len(signature(found['cells'].get(name, ''), normalize))
                   and len(signature(cells[i], normalize)) > 1 for i, name in mappings.items()):
                unverifiable('wrapped')
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
            row_lower = normalize(' '.join(raw)).lower()
            row_numbers = set(re.findall(r'\d+(?:\.\d+)?', normalize(' '.join(raw))))
            for name, counts in remaining.items():
                if any(count > 0 for count in counts.values()):
                    pdf_cell = found['cells'][name]
                    # Formula cells (e.g. "20 + 0.1CB") are often transcribed into
                    # another column as LaTeX; only flag them if their numbers are absent.
                    # A formula needs an operator between operands ("5 V" is not one) and
                    # every number must appear as a whole token, not a substring ("5" in "15").
                    op = r'[\w)]\s*[+•×*/–-]\s*[\w(]'
                    letters = re.findall(r'[A-Za-z]{2,}', pdf_cell)
                    # the formula may be split over two PDF columns ("20 + 0.1 ×" | "CB")
                    formula = re.search(r'[A-Za-z]', pdf_cell) and (re.search(op, pdf_cell) or (
                        letters and any(re.search(op, normalize(c)) and all(l in normalize(c) for l in letters) for c in raw)))
                    if formula and all((t.lstrip('+-–') in row_numbers) if re.search(r'\d', t) else (t.lower() in row_lower)
                                       for t in counts if counts[t] > 0):
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
