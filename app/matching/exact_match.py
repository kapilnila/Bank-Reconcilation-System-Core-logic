import pandas as pd


def exact_match(bank_df: pd.DataFrame, yardi_df: pd.DataFrame):

    matches = bank_df.merge(
        yardi_df,
        on=["amount", "date", "reference"],
        how="inner",
        suffixes=("_bank", "_yardi")
    )

    return matches