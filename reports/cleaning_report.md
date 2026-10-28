# Retail Data Cleaning Report

## Processing approach

- Standardized column names and text fields.
- Converted dates and numeric fields to appropriate types.
- Added flags for data-quality issues.
- Preserved all source rows; no records were deleted.
- Calculated quantity × unit price as line_value.
- line_value is not verified profit or accounting revenue.

## Results

| Metric | Value |
|---|---:|
| Rows in source dataset | 541,909 |
| Rows in output dataset | 541,909 |
| Exact duplicate occurrences beyond first copies | 5,268 |
| Rows belonging to exact duplicate groups | 10,147 |
| Rows missing CustomerID | 135,080 |
| Rows missing Description | 1,454 |
| Invalid invoice dates | 0 |
| Invalid quantities | 0 |
| Invalid unit prices | 0 |
| Cancellation invoices | 9,288 |
| Rows with quantity <= 0 | 10,624 |
| Rows with unit price <= 0 | 2,517 |

## Limitations and decisions

- Duplicate groups require business-rule review.
- Cancellation and return treatment requires investigation.
- Missing customer IDs limit customer-level analysis.
- Nonpositive quantities and prices were retained and flagged.
- No profit calculation was performed because product costs are not available in this dataset.

## Output

`data/processed/retail_transactions_cleaned.csv`

All source records were preserved in this processing step.
