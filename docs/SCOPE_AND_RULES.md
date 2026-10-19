# Scope and rules

First deliverable: financial data quality and tax audit review prototype, US transfer pricing context, synthetic data. The client knows some SQL and is refreshing Python. Delivery was discussed for next week; exact date remains to be confirmed.

## Assumptions for client review

One CSV; US-to-UK intercompany service invoices; USD; positive cost; nonnegative revenue; no credit notes; configurable illustrative markup band; offline operation. No actual tax-return or banking data.

## Data dictionary

| Fields | Meaning |
|---|---|
| transaction_id | Business ID; duplicates flagged, not dropped |
| invoice_date | Valid YYYY-MM-DD date |
| seller, buyer | Fictional entity labels |
| seller_country, buyer_country | Country codes; a US party and different counterpart country required |
| transaction_type | services for supported scope |
| currency | USD for supported scope |
| revenue, cost | Finite decimal values, preserved as raw text |
| agreement_id | Fictional reference, not a verified document |

Columns and order must match the sample exactly. Bad column counts fail clearly. Empty input with correct headers is valid. Checks trim whitespace; raw values remain unchanged. A full country-code registry is not included.

## Rule outcomes

| Condition | Action |
|---|---|
| Missing value except agreement | High severity; quarantine |
| Missing agreement | Medium severity; review |
| Duplicate transaction ID | Quarantine all occurrences |
| Invalid date or nonfinite/nonnumeric amount | Quarantine |
| Negative revenue or zero/negative cost | Quarantine |
| Unsupported currency/type or domestic/non-US transaction | Out of scope |
| Eligible markup outside invented band | Review |

Status precedence: quarantined → out of scope → review → no flags. No audit-probability score is generated. A medium finding can coexist with a high finding; quarantine takes precedence.

## Client signoff steps

1. Confirm service scope and synthetic scenarios.
2. Review initial report and request the included revision round.
3. Confirm GitHub username/repository for authorized upload.
4. Complete the walkthrough and final review.

Scheduled ingestion, multiple sources, FX rates, actual comparable-company benchmarking, historical runs, and additional transaction categories require scope agreement. No background jobs are active. The other financial data availability project is separate.
