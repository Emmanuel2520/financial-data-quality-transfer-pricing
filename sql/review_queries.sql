-- Run against output/review.sqlite. Counts use source rows, not distinct business IDs.
SELECT status, COUNT(*) AS row_count FROM assessments GROUP BY status;
SELECT code, severity, COUNT(*) AS findings FROM findings GROUP BY code, severity ORDER BY findings DESC;
-- Retrieve original evidence for each finding. Multiple findings per row are intentional.
SELECT f.row_number, f.code, f.explanation, r.*
FROM findings f JOIN raw_transactions r USING(row_number)
ORDER BY f.row_number, f.code;
-- Eligible rows only; duplicate and invalid rows are excluded from this summary.
SELECT r.seller, r.buyer, COUNT(*) AS assessed_rows,
 ROUND(SUM(CAST(r.revenue AS REAL)), 2) AS revenue_usd
FROM raw_transactions r JOIN assessments a USING(row_number)
WHERE a.status IN ('review', 'no_flags') GROUP BY r.seller, r.buyer;
