import pandas as pd


def detect_missing_transactions(bank_df, yardi_df):

    merged = bank_df.merge(
        yardi_df,
        on=["amount", "date", "reference"],
        how="left",
        indicator=True
    )

    missing = merged[merged["_merge"] == "left_only"]

    return missing


def detect_duplicates(df):

    duplicates = df[df.duplicated(
        subset=["date", "amount", "reference"],
        keep=False
    )]

    return duplicates