"""Write reproducible character and tiktoken counts for source/compact Markdown."""
import json
from pathlib import Path
import tiktoken

ROOT = Path(__file__).resolve().parents[1]
ENCODINGS = ('o200k_base', 'cl100k_base')


def saved(before, after):
    return round(100 * (before - after) / before, 2) if before else 0.0


def main():
    encoders = {name: tiktoken.get_encoding(name) for name in ENCODINGS}
    rows = []
    for directory in sorted((ROOT / 'output').iterdir()):
        if not directory.is_dir():
            continue
        source = directory / (directory.name + '.md')
        if not source.exists():
            continue
        target = directory / (directory.name + '.llm.md')
        before, after = source.read_text(), target.read_text()
        row = {'name': directory.name, 'source': str(source.relative_to(ROOT)),
               'compact': str(target.relative_to(ROOT)), 'chars': {'before': len(before), 'after': len(after)}}
        for name, encoder in encoders.items():
            row[name] = {'before': len(encoder.encode_ordinary(before)), 'after': len(encoder.encode_ordinary(after))}
        for metric in ('chars', *ENCODINGS):
            row[metric]['saved_percent'] = saved(row[metric]['before'], row[metric]['after'])
        rows.append(row)
    totals = {}
    for metric in ('chars', *ENCODINGS):
        before = sum(r[metric]['before'] for r in rows)
        after = sum(r[metric]['after'] for r in rows)
        totals[metric] = {'before': before, 'after': after, 'saved_percent': saved(before, after)}
    report = ['# LLM token counts', '', 'Counts include the complete files, including the compact legend. '
              'Characters are Unicode code points; tokens use tiktoken encode_ordinary. Savings are weighted by source size.', '',
              '|Datasheet|Chars before|Chars after|Saved|o200k_base before|After|Saved|cl100k_base before|After|Saved|',
              '|-|-:|-:|-:|-:|-:|-:|-:|-:|-:|']
    for row in rows + [{'name': 'TOTAL', **totals}]:
        values = [row['name']]
        for metric in ('chars', *ENCODINGS):
            values.extend([str(row[metric]['before']), str(row[metric]['after']), f"{row[metric]['saved_percent']:.2f}%"])
        report.append('|' + '|'.join(values) + '|')
    destination = ROOT / 'reports' / 'llm'
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'token_counts.json').write_text(json.dumps({'datasheets': rows, 'totals': totals}, indent=2, ensure_ascii=False) + '\n')
    (destination / 'token_counts.md').write_text('\n'.join(report) + '\n')
    print(json.dumps(totals, indent=2))


if __name__ == '__main__':
    main()
