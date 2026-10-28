from pathlib import Path

import pandas as pd

# Project paths
ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data" / "raw" / "Online Retail.xlsx"
REPORT_DIR = ROOT / "reports"
PROCESSED_DIR = ROOT / "data" / "processed"

REPORT_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def main():
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {RAW_FILE}\n"
            "Place Online Retail.xlsx inside data/raw/."
        )

    print("Loading the original retail dataset...")
    df = pd.read_excel(RAW_FILE)

    # Basic inspection
    row_count = len(df)
    column_count = len(df.columns)
    duplicate_count = int(df.duplicated().sum())
    missing = df.isna().sum()

    # Validate expected columns
    required = {
        "InvoiceNo",
        "StockCode",
        "Description",
        "Quantity",
        "InvoiceDate",
        "UnitPrice",
        "CustomerID",
        "Country",
    }

    missing_columns = required - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"Unexpected dataset structure. Missing columns: "
            f"{sorted(missing_columns)}"
        )

    # Parse dates without changing the original dataframe
    dates = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    invalid_dates = int(dates.isna().sum())

    # Identify potential business/data-quality issues
    quantity = pd.to_numeric(df["Quantity"], errors="coerce")
    price = pd.to_numeric(df["UnitPrice"], errors="coerce")

    nonpositive_quantity = int((quantity <= 0).sum())
    nonpositive_price = int((price <= 0).sum())

    invoice_text = df["InvoiceNo"].astype("string").str.strip()
    cancellations = int(invoice_text.str.upper().str.startswith("C", na=False).sum())

    # Sales value is quantity multiplied by unit price.
    # This is not profit because product costs are unavailable.
    line_value = quantity * price
    valid_line_value = line_value.dropna()

    summary = pd.DataFrame(
        [
            {"Metric": "Total rows", "Value": row_count},
            {"Metric": "Total columns", "Value": column_count},
            {"Metric": "Exact duplicate rows", "Value": duplicate_count},
            {
                "Metric": "Rows with missing CustomerID",
                "Value": int(df["CustomerID"].isna().sum()),
            },
            {
                "Metric": "Rows with missing Description",
                "Value": int(df["Description"].isna().sum()),
            },
            {"Metric": "Invalid invoice dates", "Value": invalid_dates},
            {
                "Metric": "Rows with quantity <= 0",
                "Value": nonpositive_quantity,
            },
            {
                "Metric": "Rows with unit price <= 0",
                "Value": nonpositive_price,
            },
            {
                "Metric": "Invoices marked as cancellations",
                "Value": cancellations,
            },
        ]
    )

    summary.to_csv(
        PROCESSED_DIR / "data_quality_summary.csv",
        index=False,
    )

    report = [
        "# Retail Dataset: Initial Data Quality Report",
        "",
        "## Dataset overview",
        "",
        f"- Rows: {row_count:,}",
        f"- Columns: {column_count}",
        f"- Exact duplicate rows: {duplicate_count:,}",
        "",
        "## Missing values by column",
        "",
        "| Column | Missing rows |",
        "|---|---:|",
    ]

    for column, count in missing.items():
        report.append(f"| {column} | {int(count):,} |")

    report.extend(
        [
            "",
            "## Validation checks",
            "",
            f"- Invalid invoice dates: {invalid_dates:,}",
            f"- Rows with quantity <= 0: {nonpositive_quantity:,}",
            f"- Rows with unit price <= 0: {nonpositive_price:,}",
            f"- Invoices marked as cancellations: {cancellations:,}",
            "",
            "## Sales-value diagnostic",
            "",
            f"- Non-missing line values: {len(valid_line_value):,}",
            (
                "- Sum of quantity × unit price across all rows: "
                f"{valid_line_value.sum():,.2f}"
            ),
            "",
            "## Interpretation and limitations",
            "",
            "- These are initial diagnostics, not automatic deletion rules.",
            "- Negative quantities and cancellation invoices need investigation.",
            "- Missing customer IDs do not necessarily make a transaction unusable.",
            "- Duplicate rows should be reviewed before removing them.",
            "- Quantity × unit price is a line-value calculation, not profit.",
            "- The original workbook has not been modified.",
            "",
            "## Reproducibility",
            "",
            "Run `python src/data_quality.py` from the project root.",
            "",
            "Dataset: UCI Online Retail. See the official source and license "
            "in the project README.",
        ]
    )

    report_path = REPORT_DIR / "data_quality_report.md"
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")

    print("\nData quality checks completed.")
    print(summary.to_string(index=False))
    print(f"\nReport saved to: {report_path}")
    print("Summary saved to: " f"{PROCESSED_DIR / 'data_quality_summary.csv'}")


if __name__ == "__main__":
    main()
