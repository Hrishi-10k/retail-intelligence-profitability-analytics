# Retail Dataset: Initial Data Quality Report

## Dataset overview

- Rows: 541,909
- Columns: 8
- Exact duplicate rows: 5,268

## Missing values by column

| Column | Missing rows |
|---|---:|
| InvoiceNo | 0 |
| StockCode | 0 |
| Description | 1,454 |
| Quantity | 0 |
| InvoiceDate | 0 |
| UnitPrice | 0 |
| CustomerID | 135,080 |
| Country | 0 |

## Validation checks

- Invalid invoice dates: 0
- Rows with quantity <= 0: 10,624
- Rows with unit price <= 0: 2,517
- Invoices marked as cancellations: 9,288

## Sales-value diagnostic

- Non-missing line values: 541,909
- Sum of quantity × unit price across all rows: 9,747,747.93

## Interpretation and limitations

- These are initial diagnostics, not automatic deletion rules.
- Negative quantities and cancellation invoices need investigation.
- Missing customer IDs do not necessarily make a transaction unusable.
- Duplicate rows should be reviewed before removing them.
- Quantity × unit price is a line-value calculation, not profit.
- The original workbook has not been modified.

## Reproducibility

Run `python src/data_quality.py` from the project root.

Dataset: UCI Online Retail. See the official source and license in the project README.
