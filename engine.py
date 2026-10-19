"""Offline educational pipeline: synthetic data -> SQLite -> review reports."""
import argparse
import csv
from collections import Counter
from datetime import date, timedelta, datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import html
import json
from pathlib import Path
import random
import sqlite3

ROOT = Path(__file__).resolve().parent
FIELDS = ['transaction_id', 'invoice_date', 'seller', 'buyer', 'seller_country', 'buyer_country', 'transaction_type', 'currency', 'revenue', 'cost', 'agreement_id']


def generate(path, count=1000, seed=42):
    if count < 10:
        raise ValueError('Use at least 10 rows to include demonstration scenarios.')
    rng = random.Random(seed)
    rows = []
    for i in range(count):
        cost = Decimal(rng.randint(10000, 500000)) / 100
        markup = Decimal(rng.randint(500, 1200)) / 10000
        rows.append(dict(zip(FIELDS, [f'TX-{i+1:06}', str(date(2025, 1, 1) + timedelta(days=i % 365)), 'Example US Services', 'Example UK Affiliate', 'US', 'GB', 'services', 'USD', str((cost * (1 + markup)).quantize(Decimal('.01'))), str(cost), 'AGR-DEMO-01'])))
    rows[0]['agreement_id'] = ''
    rows[1]['transaction_id'] = rows[2]['transaction_id']
    rows[3]['cost'] = '0'
    rows[4]['revenue'] = 'not-a-number'
    rows[5]['invoice_date'] = '2025-02-30'
    rows[6]['revenue'] = str(Decimal(rows[6]['cost']) * Decimal('1.8'))
    rows[7]['currency'] = 'EUR'
    rows[8]['buyer'] = ''
    rows[9]['cost'] = '-5'
    write_csv(path, rows, FIELDS)


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def amount(value):
    try:
        n = Decimal(value)
        return n if n.is_finite() else None
    except (InvalidOperation, ValueError, TypeError):
        return None


def evaluate(rows, config):
    ids = Counter(r['transaction_id'].strip() for r in rows if r['transaction_id'].strip())
    findings, assessed = [], []
    for row_number, row in enumerate(rows, 1):
        r = {k: v.strip() for k, v in row.items()}
        flags = []
        def flag(code, category, severity, explanation):
            flags.append({'row_number': row_number, 'transaction_id': r['transaction_id'], 'code': code, 'category': category, 'severity': severity, 'explanation': explanation})
        for field in FIELDS:
            if not r[field]:
                flag('MISSING_' + field.upper(), 'quality', 'high' if field != 'agreement_id' else 'medium', f'Missing {field}; obtain source evidence.')
        if r['transaction_id'] and ids[r['transaction_id']] > 1:
            flag('DUPLICATE_ID', 'quality', 'high', 'Transaction ID occurs more than once; reconcile before aggregation.')
        try:
            date.fromisoformat(r['invoice_date'])
        except ValueError:
            flag('INVALID_DATE', 'quality', 'high', 'Invoice date must be a valid YYYY-MM-DD date.')
        revenue, cost = amount(r['revenue']), amount(r['cost'])
        if revenue is None or cost is None:
            flag('INVALID_AMOUNT', 'quality', 'high', 'Revenue and cost must be finite numeric amounts.')
        elif revenue < 0 or cost <= 0:
            flag('INVALID_SIGN', 'quality', 'high', 'Demo accepts nonnegative revenue and positive cost; credit notes need separate treatment.')
        supported = r['currency'] == 'USD' and r['transaction_type'] == 'services' and 'US' in (r['seller_country'], r['buyer_country']) and r['seller_country'] != r['buyer_country']
        if not supported:
            flag('OUT_OF_SCOPE', 'scope', 'medium', 'Only cross-border US-related services denominated in USD are evaluated in v1.')
        valid = not any(f['category'] == 'quality' and f['severity'] == 'high' for f in flags)
        markup = None
        if valid and supported:
            markup = (revenue - cost) / cost
            if markup < Decimal(str(config['demo_markup_min'])) or markup > Decimal(str(config['demo_markup_max'])):
                flag('DEMO_MARKUP_EXCEPTION', 'review', 'medium', 'Cost markup outside invented demonstration band; investigate comparability. Not an IRS threshold or compliance finding.')
        status = 'quarantined' if not valid else 'out_of_scope' if not supported else 'review' if flags else 'no_flags'
        assessed.append({'row_number': row_number, 'transaction_id': r['transaction_id'], 'status': status, 'markup': str(markup) if markup is not None else '', 'flag_count': len(flags)})
        findings.extend(flags)
    return assessed, findings


def report(output, assessed, findings, manifest):
    counts = Counter(r['status'] for r in assessed)
    escaped = html.escape
    cards = ''.join(f'<article><strong>{counts[k]:,}</strong><span>{k.replace("_", " ")}</span></article>' for k in ['no_flags', 'review', 'quarantined', 'out_of_scope'])
    body = ''.join('<tr>' + ''.join(f'<td>{escaped(str(f[k]))}</td>' for k in ['row_number', 'transaction_id', 'code', 'severity', 'explanation']) + '</tr>' for f in findings)
    doc = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Financial Data Review</title><style>body{font:16px system-ui;margin:0;background:#f2f5fa;color:#142438}main{max-width:1150px;margin:auto;padding:40px 24px}header{background:#102a43;color:white;padding:28px;border-radius:16px}h1{font-size:32px;margin:10px 0}p{line-height:1.6}.eyebrow{letter-spacing:2px;color:#8fe1d6;font-size:12px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:16px;margin:25px 0}article{background:white;padding:24px;border-radius:12px;border:1px solid #dce4ec}strong{display:block;font-size:32px}span{text-transform:capitalize}table{width:100%;border-collapse:collapse;background:white}th,td{text-align:left;padding:14px;border-bottom:1px solid #dce4ec;font-size:14px}th{background:#dce8ee}input{font:inherit;padding:12px;width:90%;max-width:500px;margin:10px 0 20px}.scroll{overflow:auto}.note{background:#fff3d8;padding:16px;border-radius:10px}footer{font-size:13px;color:#526377;margin-top:24px}</style><main><header><div class="eyebrow">PORTFOLIO DEMONSTRATION / VERSION 0.1</div><h1>Financial Data Quality &amp; Tax Audit Risk Engine</h1><p>US transfer pricing context · Synthetic services transactions · Explainable review flags</p></header>'''
    doc += f'<section class="cards">{cards}</section><p class="note">Demonstration rules only. Flags prioritize human review; they do not predict audit probability or establish tax noncompliance. “No flags” does not establish compliance.</p><h2>Review queue</h2><label for="search">Filter findings</label><br><input id="search" placeholder="Search transaction ID, rule, or explanation"><div class="scroll"><table><thead><tr><th>Source row</th><th>Transaction</th><th>Rule</th><th>Severity</th><th>Explanation</th></tr></thead><tbody>{body}</tbody></table></div><footer>{len(assessed):,} source rows · {len(findings)} findings · Input SHA-256: {manifest["input_sha256"]}<br>Generated {manifest["generated_at"]}. Full exports: findings.csv and assessed.csv.</footer></main>'
    doc += '''<script>document.getElementById('search').addEventListener('input',e=>{const q=e.target.value.toLowerCase();document.querySelectorAll('tbody tr').forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(q));});</script></html>'''
    (output / 'report.html').write_text(doc, encoding='utf-8')


def run(source, output, config_path):
    config = json.loads(config_path.read_text())
    if amount(str(config['demo_markup_min'])) is None or amount(str(config['demo_markup_max'])) is None or Decimal(str(config['demo_markup_min'])) > Decimal(str(config['demo_markup_max'])):
        raise ValueError('Invalid demonstration markup band')
    with source.open(newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != FIELDS:
            raise ValueError('CSV columns and order must match: ' + ', '.join(FIELDS))
        rows = list(reader)
    if any(None in r or any(v is None for v in r.values()) for r in rows):
        raise ValueError('Malformed CSV row: column count differs from header')
    assessed, findings = evaluate(rows, config)
    output.mkdir(parents=True, exist_ok=True)
    # Keep source text immutable; row_number distinguishes duplicate business IDs.
    with sqlite3.connect(output / 'review.sqlite') as db:
        db.executescript('DROP TABLE IF EXISTS raw_transactions; DROP TABLE IF EXISTS assessments; DROP TABLE IF EXISTS findings;')
        db.execute('CREATE TABLE raw_transactions (row_number INTEGER PRIMARY KEY, ' + ', '.join(k + ' TEXT' for k in FIELDS) + ')')
        db.executemany('INSERT INTO raw_transactions VALUES (' + ','.join('?' for _ in range(len(FIELDS)+1)) + ')', [(i, *[r[k] for k in FIELDS]) for i,r in enumerate(rows,1)])
        db.execute('CREATE TABLE assessments (row_number INTEGER PRIMARY KEY, transaction_id TEXT, status TEXT, markup TEXT, flag_count INTEGER)')
        db.executemany('INSERT INTO assessments VALUES (?,?,?,?,?)', [tuple(r.values()) for r in assessed])
        db.execute('CREATE TABLE findings (row_number INTEGER, transaction_id TEXT, code TEXT, category TEXT, severity TEXT, explanation TEXT)')
        db.executemany('INSERT INTO findings VALUES (?,?,?,?,?,?)', [tuple(r.values()) for r in findings])
        db.execute('CREATE INDEX idx_findings_row ON findings(row_number)')
    manifest = {'version': '0.1.0', 'generated_at': datetime.now(timezone.utc).isoformat(), 'input_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'config': config, 'rows': len(rows), 'findings': len(findings), 'statuses': dict(Counter(r['status'] for r in assessed))}
    write_csv(output/'assessed.csv', assessed, ['row_number','transaction_id','status','markup','flag_count'])
    write_csv(output/'findings.csv', findings, ['row_number','transaction_id','code','category','severity','explanation'])
    (output/'manifest.json').write_text(json.dumps(manifest, indent=2))
    report(output, assessed, findings, manifest)
    print(json.dumps(manifest, indent=2))
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    g = sub.add_parser('generate'); g.add_argument('--rows', type=int, default=1000); g.add_argument('--seed', type=int, default=42); g.add_argument('--output', type=Path, default=ROOT/'data'/'synthetic.csv')
    r = sub.add_parser('run'); r.add_argument('--input', type=Path, default=ROOT/'data'/'synthetic.csv'); r.add_argument('--output', type=Path, default=ROOT/'output'); r.add_argument('--config', type=Path, default=ROOT/'config.json')
    args = parser.parse_args()
    try:
        if args.command == 'generate': generate(args.output, args.rows, args.seed)
        else: run(args.input, args.output, args.config)
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(1, f'Error: {exc}\n')

if __name__ == '__main__':
    main()
