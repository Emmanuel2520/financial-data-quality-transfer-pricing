# Walkthrough

1. **Business story.** A fictional US service company invoices a UK affiliate. Financial records must be usable before anyone reviews pricing.
2. **Inspect `data/synthetic.csv`.** All values are invented. The fixed seed makes generation repeatable. The first ten rows contain a missing agreement, duplicate-ID pair, zero cost, invalid revenue, invalid date, high markup, unsupported currency, missing buyer, and negative cost.
3. **Run `python engine.py run`.** Inspect the manifest for input hash, rule settings, counts, and timestamp.
4. **Open `output/report.html`.** Search for `DUPLICATE` or `MARKUP`. Trace each finding to its source row. Multiple findings may apply to one row; dashboard totals count each row once.
5. **Explain cost markup.** Revenue 110 and cost 100 yield `(110-100)/100 = 10%`. This is not operating margin on revenue. Decimal arithmetic handles the check; thresholds are inclusive.
6. **Explore SQL.** Open the SQLite database in a local SQLite viewer or run the Python below. The sample SQL file includes row counts and evidence joins. Join by row number rather than duplicated invoice IDs.
7. **Correct one sample.** Copy the CSV to `data/corrected.csv`, fill the missing agreement reference, then run the alternate command below. Review count should fall by one. Preserve the original input.
8. **Run tests.** `python -m unittest discover -s tests -v`. Tests exercise duplicates, invalid/nonfinite numbers, invalid dates, boundaries, scope, empty input, schemas, repeatability, and source reconciliation.

```python
import sqlite3
with sqlite3.connect('output/review.sqlite') as db:
    for row in db.execute('SELECT status, COUNT(*) FROM assessments GROUP BY status'):
        print(row)
```

```sh
python engine.py run --input data/corrected.csv --output corrected-output
```

SQL example totals use REAL casts for exploratory summaries. Raw amounts remain text; these totals are not accounting-ledger arithmetic.

## Interview discussion

- Why preserve raw values instead of overwriting errors?
- Why quarantine duplicates before aggregating?
- How does the hash support reproducibility?
- Why does clean data not establish tax compliance?
- How would you add currencies, multiple sources, run history, and scheduling?

## Suggested client walkthrough

Business purpose (5 minutes); dataset (5); pipeline and SQL (10); evidence tracing (5); correction and rerun (5); questions (10). This written guide is delivered; a live or recorded session has not yet occurred.
