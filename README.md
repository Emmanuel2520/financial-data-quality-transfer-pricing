# Financial Data Quality & Tax Audit Risk Engine

Working portfolio prototype v0.1 — October 19, 2026.

For a tax professional transitioning into data engineering: generate synthetic intercompany service transactions, validate them using Python, store traceable evidence in SQLite, and explore an explainable review report.

## Quick start

Python 3.10+; standard library only. No paid services, dependencies, accounts, or API keys.
Extract the ZIP and open a terminal in this project folder:

```sh
python engine.py generate
python engine.py run
python -m unittest discover -s tests -v
```

Use `python3` or Windows `py` if that is your Python command. Open `output/report.html` in your browser. A generated dataset and report are included for immediate review.

## Files

- `engine.py`: generator, validator, SQLite loader, and report builder.
- `config.json`: configurable demonstration markup interval.
- `data/synthetic.csv`: 1,000 fictional service invoices with planted anomalies.
- `output/report.html`: offline searchable report.
- `output/assessed.csv`: one result per source row.
- `output/findings.csv`: explanations and source-row references.
- `output/review.sqlite`: raw records, assessments, and findings.
- `output/manifest.json`: input hash, config, counts, and run time.
- `sql/review_queries.sql`: sample analytical queries.
- `tests/test_engine.py`: regression tests.
- `docs/WALKTHROUGH.md`: practical learning and handoff guide.
- `docs/SCOPE_AND_RULES.md`: assumptions, dictionary, and next steps.

## Architecture and outcomes

CSV → raw SQLite records → Python validation and decimal calculations → assessments and findings → CSV/HTML outputs.

Raw text is preserved. Source row numbers distinguish duplicate business IDs. Invalid records are quarantined before numeric review. Reruns replace the output snapshot instead of appending duplicates. SHA-256 identifies input bytes; historical run storage is not implemented.

Default output: 990 rows with no flags, 2 for review, 7 quarantined, and 1 out of scope. Ten findings in total. These are planted demonstration scenarios, not predictive accuracy measurements.

## US context and limitations

The [IRS transfer pricing overview](https://www.irs.gov/businesses/international-businesses/transfer-pricing), consulted October 19, 2026, describes Section 482 and comparison with uncontrolled transactions. It provides background, not the project's numerical rules.

The 3%–15% cost-markup band is invented for educational use. It is NOT an IRS threshold, safe harbor, or validated arm's-length range. Flags request human review; they do not predict audits or establish noncompliance. No flags does not mean compliant. Missing agreement references are not a legal documentation assessment.

V1 covers USD cross-border services with a US party. It does not implement a legal transfer pricing method, comparable-company study, currency conversion, tax calculations, filings, loans, royalties, goods, or credit-note handling. All records and entities are synthetic.

## GitHub handoff

Suggested repository: `financial-data-quality-transfer-pricing`.
Suggested description: “Python/SQL pipeline for synthetic intercompany data validation and explainable review flags.”

Upload source, docs, synthetic data, and sample exports after reviewing them. The included `.gitignore` excludes caches, virtual environments, and generated SQLite databases. Recreate the database using `python engine.py run`. No repository has been published. No personal, payment, or real financial records are included.

This is the first working prototype for review. Client revisions and the live/recorded walkthrough remain. The financial data availability pipeline is the other project and is not part of this package.
