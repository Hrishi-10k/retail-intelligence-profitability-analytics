from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text

ROOT = Path(__file__).resolve().parents[1]
CSV_FILE = ROOT / "data" / "processed" / "retail_transactions_cleaned.csv"

load_dotenv(ROOT / ".env")


def main():
    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"Cannot find {CSV_FILE}. " "Run python src/clean_data.py first."
        )

    required = [
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
    ]

    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise ValueError("Missing .env settings: " + ", ".join(missing))

    print("Reading cleaned CSV...")
    df = pd.read_csv(CSV_FILE)

    # Restore important data types after reading the CSV.
    df["invoicedate"] = pd.to_datetime(df["invoicedate"], errors="coerce")
    df["customerid"] = pd.to_numeric(df["customerid"], errors="coerce").astype("Int64")

    for column in ["quantity", "unitprice", "line_value"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    bool_columns = [
        "is_exact_duplicate",
        "missing_customer_id",
        "missing_description",
        "invalid_invoice_date",
        "invalid_quantity",
        "invalid_unit_price",
        "is_cancellation",
        "nonpositive_quantity",
        "nonpositive_unit_price",
    ]

    for column in bool_columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.lower()
            .map({"true": True, "false": False})
            .astype("boolean")
        )

    database_url = URL.create(
        "mysql+pymysql",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_NAME"],
        query={"charset": "utf8mb4"},
    )

    engine = create_engine(database_url)

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("MySQL connection successful.")

        expected_rows = len(df)
        print(f"Loading {expected_rows:,} rows...")

        # This replaces this project's table on each full reload.
        # It does not delete other tables in the database.
        df.to_sql(
            name="retail_transactions",
            con=engine,
            if_exists="replace",
            index=False,
            chunksize=2000,
            method=None,
        )

        with engine.connect() as connection:
            actual_rows = connection.execute(
                text("SELECT COUNT(*) FROM retail_transactions")
            ).scalar_one()

        print(f"CSV rows: {expected_rows:,}")
        print(f"MySQL rows: {actual_rows:,}")

        if actual_rows != expected_rows:
            raise RuntimeError("Row count validation failed.")

        print("Data load and validation successful.")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
