import pandas as pd
from app.utils.logger import log_failure, log_success


def normalize_transactions(df: pd.DataFrame, source: str):

    try:

        df.columns = df.columns.str.lower()

        column_map = {
            "transaction date": "date",
            "txn_date": "date",
            "posting date": "date",
            "amount": "amount",
            "description": "description",
            "reference": "reference"
        }

        df = df.rename(columns=column_map)

        # ---------- DATE ----------
        if "date" not in df.columns:
            df["date"] = pd.Timestamp.today()

        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        # ---------- AMOUNT ----------
        if "amount" not in df.columns:
            df["amount"] = 0

        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

        # ---------- DESCRIPTION ----------
        if "description" not in df.columns:
            df["description"] = ""

        df["description"] = df["description"].astype(str).str.lower()

        # ---------- REFERENCE ----------
        if "reference" not in df.columns:
            df["reference"] = df.index.astype(str)

        df["reference"] = df["reference"].astype(str)

        df["source"] = source

        log_success(f"Normalization completed for {source}")

        return df

    except Exception as e:

        log_failure(f"Normalization failed: {str(e)}")

        raise