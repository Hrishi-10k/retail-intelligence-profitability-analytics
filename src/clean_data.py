
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data" / "raw" / "Online Retail.xlsx"
OUTPUT_DIR = ROOT / "data" / "processed"
REPORT_DIR = ROOT / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {RAW_FILE}"
        )

    print("Reading original dataset...")
    df = pd.read_excel(RAW_FILE)

    expected_columns = [
        "InvoiceNo",
        "StockCode",
        "Description",
        "Quantity",
        "InvoiceDate",
        "UnitPrice",
        "CustomerID",
        "Country",
    ]

    missing_columns = set(expected_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"Missing expected columns: {sorted(missing_columns)}"
        )

    # Capture exact duplicates before modifying any values.
    exact_duplicate_extra_count = int(df.duplicated().sum())
    exact_duplicate_group_rows = int(
        df.duplicated(keep=False).sum()
    )

    # Standardize column names.
    df.columns = [
        column.strip().lower().replace(" ", "_")
        for column in df.columns
    ]

    # Normalize text fields.
    for column in ["invoiceno", "stockcode", "description", "country"]:
        df[column] = df[column].astype("string").str.strip()

    # Convert fields to appropriate data types.
    df["invoicedate"] = pd.to_datetime(
        df["invoicedate"], errors="coerce"
    )
    df["quantity"] = pd.to_numeric(
        df["quantity"], errors="coerce"
    )
    df["unitprice"] = pd.to_numeric(
        df["unitprice"], errors="coerce"
    )
    df["customerid"] = pd.to_numeric(
        df["customerid"], errors="coerce"
    ).astype("Int64")

    # Create transparent quality flags; do not discard records.
    df["is_exact_duplicate"] = df.duplicated(keep=False)

    df["missing_customer_id"] = df["customerid"].isna()
    df["missing_description"] = (
        df["description"].isna()
        | df["description"].eq("")
    )

    df["invalid_invoice_date"] = df["invoicedate"].isna()
    df["invalid_quantity"] = df["quantity"].isna()
    df["invalid_unit_price"] = df["unitprice"].isna()

    df["is_cancellation"] = (
        df["invoiceno"].str.upper().str.startswith("C", na=False)
    )

    df["nonpositive_quantity"] = (
        df["quantity"].le(0).fillna(False)
    )
    df["nonpositive_unit_price"] = (
        df["unitprice"].le(0).fillna(False)
    )

    # This is a line-value calculation, not verified profit.
    df["line_value"] = df["quantity"] * df["unitprice"]

    # Keep every original row for now.
    output_file = OUTPUT_DIR / "retail_transactions_cleaned.csv"
    df.to_csv(output_file, index=False)

    # Create a summary of the transformed dataset.
    summary = [
        ("Rows in source dataset", len(df)),
        ("Rows in output dataset", len(df)),
        (
            "Exact duplicate occurrences beyond first copies",
            exact_duplicate_extra_count,
        ),
        (
            "Rows belonging to exact duplicate groups",
            exact_duplicate_group_rows,
        ),
        ("Rows missing CustomerID", int(df["missing_customer_id"].sum())),
        ("Rows missing Description", int(df["missing_description"].sum())),
        ("Invalid invoice dates", int(df["invalid_invoice_date"].sum())),
        ("Invalid quantities", int(df["invalid_quantity"].sum())),
        ("Invalid unit prices", int(df["invalid_unit_price"].sum())),
        ("Cancellation invoices", int(df["is_cancellation"].sum())),
        ("Rows with quantity <= 0", int(df["nonpositive_quantity"].sum())),
        (
            "Rows with unit price <= 0",
            int(df["nonpositive_unit_price"].sum()),
        ),
    ]

    summary_df = pd.DataFrame(summary, columns=["Metric", "Value"])
    summary_df.to_csv(
        OUTPUT_DIR / "cleaning_summary.csv", index=False
    )

    report_lines = [
        "# Retail Data Cleaning Report",
        "",
        "## Processing approach",
        "",
        "- Standardized column names and text fields.",
        "- Converted dates and numeric fields to appropriate types.",
        "- Added flags for data-quality issues.",
        "- Preserved all source rows; no records were deleted.",
        "- Calculated quantity × unit price as line_value.",
        "- line_value is not verified profit or accounting revenue.",
        "",
        "## Results",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]

    for metric, value in summary:
        report_lines.append(f"| {metric} | {value:,} |")

    report_lines.extend(
        [
            "",
            "## Limitations and decisions",
            "",
            "- Duplicate groups require business-rule review.",
            "- Cancellation and return treatment requires investigation.",
            "- Missing customer IDs limit customer-level analysis.",
            "- Nonpositive quantities and prices were retained and flagged.",
            "- No profit calculation was performed because product costs "
            "are not available in this dataset.",
            "",
            "## Output",
            "",
            "`data/processed/retail_transactions_cleaned.csv`",
            "",
            "All source records were preserved in this processing step.",
        ]
    )

    report_file = REPORT_DIR / "cleaning_report.md"
    report_file.write_text(
        "\n".join(report_lines) + "\n",
        encoding="utf-8",
    )

    print("\nCleaning pipeline completed successfully.")
    print(summary_df.to_string(index=False))
    print(f"\nProcessed data: {output_file}")
    print(f"Cleaning report: {report_file}")


if __name__ == "__main__":
    main()
