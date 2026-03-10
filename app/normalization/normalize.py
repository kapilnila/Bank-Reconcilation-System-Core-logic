import pandas as pd


def normalize_transactions(df: pd.DataFrame, source: str):

    df.columns = df.columns.str.lower()
    
    if "date" not in df.columns:
        df["date"] = pd.Timestamp.today()

    column_map = {
        "transaction date": "date",
        "amount": "amount",
        "description": "description",
        "reference": "reference"
    }

    df = df.rename(columns=column_map)

    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = df["amount"].astype(float)

    df["description"] = df["description"].fillna("").str.lower()

    df["source"] = source

    return df